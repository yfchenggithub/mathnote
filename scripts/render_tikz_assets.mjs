#!/usr/bin/env node

import crypto from "node:crypto";
import { spawn } from "node:child_process";
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import sharp from "sharp";

const DEFAULT_INPUT = path.join("data", "content", "canonical_content_v2.json");
const DEFAULT_OUTPUT = path.join(
  "data",
  "content",
  "canonical_content_v2.with_tikz_assets.json",
);
const DEFAULT_OUT_DIR = path.join("public", "static", "tikz");
const DEFAULT_REPORT = path.join("reports", "render_tikz_assets_report.json");
const DEFAULT_ASSET_BASE = "/static/tikz";
const DEFAULT_SCALE = 3;
const CONCLUSION_ID_RE = /^[A-Z]\d{3}$/;
const TIKZ_PATH_RE =
  /assets[\\/]tikz[\\/][^\s"'<>]+?\.(?:tikz\.tex|tex|tikz)/g;
const VSPACE_AND_CAPTION_RE =
  /^\s*(?:(\d+(?:\.\d+)?em)\s*)?(?:\r?\n|\s)*((?:\u56fe|\u5716)\s*[:\uff1a][\s\S]*)$/;
const CAPTION_PREFIX_RE = /^(?:\u56fe|\u5716)\s*[:\uff1a]\s*/;

function printUsage() {
  console.log(`Usage:
  node scripts/render_tikz_assets.mjs [options]

Options:
  --input <path>        Input JSON path (default: ${DEFAULT_INPUT})
  --output <path>       Output JSON path (default: ${DEFAULT_OUTPUT})
  --in-place            Overwrite input JSON directly
  --out-dir <path>      TikZ PNG asset directory (default: ${DEFAULT_OUT_DIR})
  --asset-base <path>   Asset base path (default: ${DEFAULT_ASSET_BASE})
  --scale <number>      Output scale factor (default: ${DEFAULT_SCALE})
  --force [bool]        Force re-render existing PNG files (default: false)
  --dry-run [bool]      Scan only, do not generate files (default: false)
  --limit <number>      Max unique TikZ sources to process (default: unlimited)
  --help                Show this message
`);
}

function parseBoolean(rawValue, flagName) {
  if (typeof rawValue !== "string") {
    throw new Error(`Missing boolean value for ${flagName}.`);
  }
  const lowered = rawValue.trim().toLowerCase();
  if (["true", "1", "yes", "y"].includes(lowered)) return true;
  if (["false", "0", "no", "n"].includes(lowered)) return false;
  throw new Error(`Invalid boolean value for ${flagName}: ${rawValue}`);
}

function parsePositiveInt(rawValue, flagName) {
  const value = Number(rawValue);
  if (!Number.isInteger(value) || value <= 0) {
    throw new Error(`${flagName} must be a positive integer, got: ${rawValue}`);
  }
  return value;
}

function normalizeAssetBase(assetBase) {
  let normalized = String(assetBase || "").trim().replace(/\\/g, "/");
  if (!normalized) throw new Error("--asset-base must not be empty.");
  if (/^https?:\/\//i.test(normalized)) {
    throw new Error("--asset-base must be a relative path, not a full URL.");
  }
  if (!normalized.startsWith("/")) normalized = `/${normalized}`;
  normalized = normalized.replace(/\/+$/g, "");
  if (!normalized) throw new Error("--asset-base must not be empty.");
  return normalized;
}

function parseArgs(argv) {
  const options = {
    input: DEFAULT_INPUT,
    output: DEFAULT_OUTPUT,
    outputFromArg: false,
    inPlace: false,
    outDir: DEFAULT_OUT_DIR,
    assetBase: DEFAULT_ASSET_BASE,
    scale: DEFAULT_SCALE,
    force: false,
    dryRun: false,
    limit: null,
    help: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === "--help" || arg === "-h") {
      options.help = true;
      continue;
    }

    if (
      arg === "--input" ||
      arg === "--output" ||
      arg === "--out-dir" ||
      arg === "--asset-base" ||
      arg === "--public-base" ||
      arg === "--scale" ||
      arg === "--limit"
    ) {
      const value = argv[index + 1];
      if (!value || value.startsWith("--")) {
        throw new Error(`Missing value for ${arg}.`);
      }
      if (arg === "--input") options.input = value;
      if (arg === "--output") {
        options.output = value;
        options.outputFromArg = true;
      }
      if (arg === "--out-dir") options.outDir = value;
      if (arg === "--asset-base" || arg === "--public-base") {
        options.assetBase = value;
      }
      if (arg === "--scale") options.scale = parsePositiveInt(value, "--scale");
      if (arg === "--limit") options.limit = parsePositiveInt(value, "--limit");
      index += 1;
      continue;
    }

    if (arg === "--force" || arg === "--dry-run") {
      const nextValue = argv[index + 1];
      const hasValue = Boolean(nextValue && !nextValue.startsWith("--"));
      const parsed = hasValue ? parseBoolean(nextValue, arg) : true;
      if (arg === "--force") options.force = parsed;
      if (arg === "--dry-run") options.dryRun = parsed;
      if (hasValue) index += 1;
      continue;
    }

    if (arg === "--in-place") {
      options.inPlace = true;
      continue;
    }

    throw new Error(`Unknown argument: ${arg}`);
  }

  const inputAbs = path.resolve(options.input);
  const outputFromOptionAbs = path.resolve(options.output);
  let outputAbs = outputFromOptionAbs;

  if (options.inPlace) {
    if (options.outputFromArg && outputFromOptionAbs !== inputAbs) {
      throw new Error(
        "--in-place is set, but --output points to a different file.",
      );
    }
    outputAbs = inputAbs;
  } else if (outputFromOptionAbs === inputAbs) {
    throw new Error(
      "Output path equals input path. Use --in-place to overwrite input explicitly.",
    );
  }

  return {
    ...options,
    inputAbs,
    outputAbs,
    outDirAbs: path.resolve(options.outDir),
    reportAbs: path.resolve(DEFAULT_REPORT),
    assetBase: normalizeAssetBase(options.assetBase),
  };
}

async function loadJson(jsonPath) {
  try {
    return JSON.parse(await fs.readFile(jsonPath, "utf8"));
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`Failed to load JSON file: ${jsonPath}\n${message}`);
  }
}

async function saveJson(jsonPath, data) {
  await fs.mkdir(path.dirname(jsonPath), { recursive: true });
  await fs.writeFile(jsonPath, `${JSON.stringify(data, null, 2)}\n`, "utf8");
}

function normalizeSourcePath(source) {
  return String(source || "")
    .trim()
    .replace(/\\/g, "/")
    .replace(/^\.\//, "");
}

function isConclusionId(value) {
  return typeof value === "string" && CONCLUSION_ID_RE.test(value);
}

function sourceConclusionId(source) {
  const filename = path.posix.basename(normalizeSourcePath(source));
  const matched = filename.match(/^([A-Z]\d{3})(?:[_-]|$)/i);
  return matched ? matched[1].toUpperCase() : null;
}

function safeStem(source) {
  const basename = path.posix.basename(normalizeSourcePath(source));
  return basename
    .replace(/\.(?:tikz\.tex|tex|tikz)$/i, "")
    .replace(/[^A-Za-z0-9_.-]+/g, "_");
}

function joinAssetPath(assetBase, ...segments) {
  const normalizedBase = assetBase.replace(/\/+$/g, "");
  const normalizedSegments = segments.map((segment) =>
    String(segment || "").replace(/^\/+|\/+$/g, ""),
  );
  return [normalizedBase, ...normalizedSegments]
    .join("/")
    .replace(/\/{2,}/g, "/");
}

function toDisplayPath(absPath) {
  const relative = path.relative(process.cwd(), absPath);
  if (!relative || relative.startsWith("..")) return absPath;
  return relative.split(path.sep).join("/");
}

function hashTikz(source, content) {
  return crypto
    .createHash("sha1")
    .update(`${normalizeSourcePath(source)}\0${content}`)
    .digest("hex")
    .slice(0, 12);
}

async function fileExists(targetPath) {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
}

async function readImageSize(pngPath) {
  const metadata = await sharp(pngPath).metadata();
  if (!metadata.width || !metadata.height) {
    throw new Error(`Could not read width/height from ${pngPath}`);
  }
  return {
    widthPx: metadata.width,
    heightPx: metadata.height,
  };
}

function runProcess(command, args, cwd) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd,
      shell: false,
      windowsHide: true,
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) {
        resolve({ stdout, stderr });
        return;
      }
      const tail = `${stdout}\n${stderr}`.split(/\r?\n/).slice(-80).join("\n");
      reject(
        new Error(
          `${command} ${args.join(" ")} failed with exit code ${code}\n${tail}`,
        ),
      );
    });
  });
}

function buildStandaloneTex(sourceContent) {
  const hasRealDocumentClass = sourceContent
    .split(/\r?\n/)
    .some((line) => {
      const trimmed = line.trimStart();
      return trimmed && !trimmed.startsWith("%") && /\\documentclass\b/.test(trimmed);
    });

  if (hasRealDocumentClass) {
    return sourceContent;
  }

  return String.raw`\documentclass[tikz,border=6pt]{standalone}
\usepackage{fontspec}
\usepackage{xeCJK}
\IfFontExistsTF{SimSun}{\setCJKmainfont{SimSun}}{%
  \IfFontExistsTF{Noto Serif CJK SC}{\setCJKmainfont{Noto Serif CJK SC}}{}%
}
\usepackage{amsmath,amssymb,mathtools}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usetikzlibrary{arrows,arrows.meta,intersections,calc,quotes,angles,decorations.pathreplacing,decorations.markings,positioning,patterns,shapes.geometric,shapes.misc,fit,matrix}
\begin{document}
` + sourceContent + String.raw`
\end{document}
`;
}

async function renderTikzToPng({
  source,
  conclusionId,
  outDirAbs,
  assetBase,
  scale,
  force,
}) {
  const normalizedSource = normalizeSourcePath(source);
  if (!normalizedSource.startsWith("assets/tikz/")) {
    throw new Error(`Unsupported TikZ source path: ${source}`);
  }

  const sourceAbs = path.resolve(normalizedSource);
  const sourceContent = await fs.readFile(sourceAbs, "utf8");
  const hash = hashTikz(normalizedSource, sourceContent);
  const stem = safeStem(normalizedSource);
  const outputDir = path.join(outDirAbs, conclusionId);
  const pngFilename = `${stem}.${hash}@${scale}x.png`;
  const pngPath = path.join(outputDir, pngFilename);
  await fs.mkdir(outputDir, { recursive: true });

  if (!force && (await fileExists(pngPath))) {
    const { widthPx, heightPx } = await readImageSize(pngPath);
    return {
      status: "reused",
      hash,
      pngPath,
      pngUrl: joinAssetPath(assetBase, conclusionId, pngFilename),
      widthPx,
      heightPx,
    };
  }

  const tmpRoot = path.resolve(".tmp", "render_tikz_assets");
  await fs.mkdir(tmpRoot, { recursive: true });
  const buildDir = await fs.mkdtemp(
    path.join(tmpRoot, `${conclusionId}_${stem}_${hash}_`),
  );

  try {
    const mainTex = path.join(buildDir, "main.tex");
    const mainPdf = path.join(buildDir, "main.pdf");
    const mainSvg = path.join(buildDir, "main.svg");
    await fs.writeFile(mainTex, buildStandaloneTex(sourceContent), "utf8");

    await runProcess(
      "xelatex",
      ["-interaction=nonstopmode", "-halt-on-error", "-file-line-error", "main.tex"],
      buildDir,
    );

    if (!(await fileExists(mainPdf))) {
      throw new Error(`LaTeX finished but PDF was not generated: ${mainPdf}`);
    }

    await runProcess(
      "dvisvgm",
      [
        "--pdf",
        "main.pdf",
        "--page=1",
        "-o",
        "main.svg",
        "--no-fonts",
        "--exact",
        "--bbox=min",
      ],
      buildDir,
    );

    if (!(await fileExists(mainSvg))) {
      throw new Error(`dvisvgm finished but SVG was not generated: ${mainSvg}`);
    }

    const pngInfo = await sharp(mainSvg, {
      density: Math.max(72, Math.round(72 * scale)),
    })
      .png({
        compressionLevel: 9,
        adaptiveFiltering: true,
        palette: false,
      })
      .toFile(pngPath);

    if (!pngInfo.width || !pngInfo.height) {
      throw new Error(`Failed to get image size for ${pngPath}`);
    }

    return {
      status: "rendered",
      hash,
      pngPath,
      pngUrl: joinAssetPath(assetBase, conclusionId, pngFilename),
      widthPx: pngInfo.width,
      heightPx: pngInfo.height,
    };
  } finally {
    try {
      await fs.rm(buildDir, { recursive: true, force: true });
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      console.warn(`[render_tikz_assets] warning: could not remove ${buildDir}: ${message}`);
    }
  }
}

function buildAsset(result, scale) {
  return {
    src: result.pngUrl,
    width_px: result.widthPx,
    height_px: result.heightPx,
    display_width_px: Math.max(1, Math.round(result.widthPx / scale)),
    display_height_px: Math.max(1, Math.round(result.heightPx / scale)),
  };
}

function splitTextToSegments(text) {
  const segments = [];
  TIKZ_PATH_RE.lastIndex = 0;
  let lastIndex = 0;
  let match;
  while ((match = TIKZ_PATH_RE.exec(text)) !== null) {
    const before = text.slice(lastIndex, match.index).replace(/\s+$/g, "");
    if (before) segments.push({ kind: "text", text: before });
    segments.push({
      kind: "image",
      source: normalizeSourcePath(match[0]),
    });
    lastIndex = TIKZ_PATH_RE.lastIndex;
  }
  const after = text.slice(lastIndex);
  if (after) segments.push({ kind: "text", text: after });
  return segments;
}

function paragraphSegments(tokens) {
  const segments = [];
  for (const token of tokens) {
    if (token && token.type === "text" && typeof token.text === "string") {
      segments.push(...splitTextToSegments(token.text));
      continue;
    }
    segments.push({ kind: "token", token });
  }
  return segments;
}

function referencesInTokens(tokens) {
  const references = [];
  for (const segment of paragraphSegments(tokens)) {
    if (segment.kind === "image") references.push(segment.source);
  }
  return references;
}

function collectReferences(content) {
  const references = [];
  if (!content || typeof content !== "object") return references;

  for (const [recordKey, record] of Object.entries(content)) {
    if (!record || typeof record !== "object") continue;
    const recordId = isConclusionId(record.id) ? record.id : recordKey;
    const sections = record.content?.sections;
    if (!Array.isArray(sections)) continue;

    for (const [sectionIndex, section] of sections.entries()) {
      const blocks = section?.blocks;
      if (!Array.isArray(blocks)) continue;
      for (const [blockIndex, block] of blocks.entries()) {
        if (
          !block ||
          block.type !== "paragraph" ||
          !Array.isArray(block.tokens)
        ) {
          continue;
        }
        for (const source of referencesInTokens(block.tokens)) {
          const inferredId = isConclusionId(recordId)
            ? recordId
            : sourceConclusionId(source);
          references.push({
            source,
            conclusionId: inferredId,
            path: `${recordKey}.content.sections[${sectionIndex}].blocks[${blockIndex}]`,
          });
        }
      }
    }
  }
  return references;
}

function resultKey(conclusionId, source) {
  return `${conclusionId || ""}::${normalizeSourcePath(source)}`;
}

function segmentToCaptionText(segment) {
  if (segment.kind === "text") return segment.text;
  if (segment.kind !== "token" || !segment.token) return "";
  if (segment.token.type === "text") return segment.token.text || "";
  if (segment.token.type === "math_inline") return segment.token.latex || "";
  if (segment.token.type === "math_display") return segment.token.latex || "";
  if (segment.token.type === "ref") return segment.token.text || segment.token.target_id || "";
  if (segment.token.type === "line_break") return "\n";
  return "";
}

function splitAtFirstNewline(text) {
  const normalized = String(text || "").replace(/\r\n/g, "\n");
  const index = normalized.indexOf("\n");
  if (index < 0) {
    return { head: normalized, tail: "" };
  }
  return {
    head: normalized.slice(0, index),
    tail: normalized.slice(index + 1),
  };
}

function consumeCaption(segments, startIndex) {
  if (startIndex >= segments.length) {
    return { nextIndex: startIndex, caption: "", alt: "", vspace: "", remainingSegments: [] };
  }
  const first = segments[startIndex];
  if (first.kind !== "text") {
    return { nextIndex: startIndex, caption: "", alt: "", vspace: "", remainingSegments: [] };
  }

  const matched = first.text.match(VSPACE_AND_CAPTION_RE);
  if (!matched) {
    return { nextIndex: startIndex, caption: "", alt: "", vspace: "", remainingSegments: [] };
  }

  const captionParts = [];
  const firstSplit = splitAtFirstNewline(matched[2].trimStart());
  captionParts.push(firstSplit.head);
  if (firstSplit.tail) {
    const caption = captionParts.join("").trim();
    const alt = caption.replace(CAPTION_PREFIX_RE, "").trim();
    return {
      nextIndex: startIndex + 1,
      caption,
      alt,
      vspace: matched[1] || "",
      remainingSegments: [{ kind: "text", text: firstSplit.tail }],
    };
  }

  for (let index = startIndex + 1; index < segments.length; index += 1) {
    if (segments[index].kind === "text") {
      const split = splitAtFirstNewline(segments[index].text);
      captionParts.push(split.head);
      if (split.tail) {
        const caption = captionParts.join("").trim();
        const alt = caption.replace(CAPTION_PREFIX_RE, "").trim();
        return {
          nextIndex: index + 1,
          caption,
          alt,
          vspace: matched[1] || "",
          remainingSegments: [{ kind: "text", text: split.tail }],
        };
      }
      continue;
    }
    captionParts.push(segmentToCaptionText(segments[index]));
  }

  const caption = captionParts.join("").trim();
  const alt = caption.replace(CAPTION_PREFIX_RE, "").trim();
  return {
    nextIndex: segments.length,
    caption,
    alt,
    vspace: matched[1] || "",
    remainingSegments: [],
  };
}

function appendText(tokens, text, { trimLeading = false } = {}) {
  const nextText = (trimLeading ? text.replace(/^\s+/g, "") : text).replace(
    /\r\n/g,
    "\n",
  );
  if (!nextText) return;
  const previous = tokens[tokens.length - 1];
  if (previous && previous.type === "text") {
    previous.text += nextText;
    return;
  }
  tokens.push({ type: "text", text: nextText });
}

function appendSegmentToken(tokens, segment, trimLeadingText) {
  if (segment.kind === "text") {
    appendText(tokens, segment.text, { trimLeading: trimLeadingText });
    return;
  }
  if (segment.kind === "token") {
    tokens.push(structuredClone(segment.token));
  }
}

function hasRenderableTokens(tokens) {
  return tokens.some((token) => {
    if (!token || typeof token !== "object") return false;
    if (token.type === "text") return typeof token.text === "string" && token.text.length > 0;
    return true;
  });
}

function transformParagraphBlock(block, resultMap, scale) {
  const references = referencesInTokens(block.tokens || []);
  if (references.length === 0) return [block];

  for (const source of references) {
    const conclusionId = sourceConclusionId(source);
    const directKey = resultKey(conclusionId, source);
    const found = resultMap.get(directKey);
    if (!found || found.ok !== true || !found.asset) {
      return [block];
    }
  }

  const segments = paragraphSegments(block.tokens || []);
  const outputBlocks = [];
  const currentTokens = [];
  let imageCount = 0;
  let paragraphCount = 0;
  let trimLeadingText = false;

  function flushParagraph() {
    if (!hasRenderableTokens(currentTokens)) return;
    const paragraphId =
      paragraphCount === 0
        ? block.id
        : `${block.id || "paragraph"}-after-img${imageCount}`;
    outputBlocks.push({
      ...block,
      id: paragraphId,
      tokens: currentTokens.splice(0, currentTokens.length),
    });
    paragraphCount += 1;
  }

  for (let index = 0; index < segments.length; index += 1) {
    const segment = segments[index];
    if (segment.kind !== "image") {
      appendSegmentToken(currentTokens, segment, trimLeadingText);
      trimLeadingText = false;
      continue;
    }

    flushParagraph();
    imageCount += 1;
    const conclusionId = sourceConclusionId(segment.source);
    const renderResult = resultMap.get(resultKey(conclusionId, segment.source));
    const captionResult = consumeCaption(segments, index + 1);
    if (captionResult.remainingSegments.length > 0) {
      segments.splice(captionResult.nextIndex, 0, ...captionResult.remainingSegments);
    }
    index = captionResult.nextIndex - 1;

    outputBlocks.push({
      id: `${block.id || "paragraph"}-img${imageCount}`,
      type: "image_block",
      src: renderResult.asset.src,
      width_px: renderResult.asset.width_px,
      height_px: renderResult.asset.height_px,
      display_width_px: renderResult.asset.display_width_px,
      display_height_px: renderResult.asset.display_height_px,
      alt: captionResult.alt,
      caption: captionResult.caption,
      source: segment.source,
      ...(captionResult.vspace ? { vspace: captionResult.vspace } : {}),
      scale,
    });
    trimLeadingText = true;
  }

  flushParagraph();
  return outputBlocks.length > 0 ? outputBlocks : [block];
}

function applyRenderedTikz(content, resultMap, scale) {
  let replaced = 0;
  if (!content || typeof content !== "object") return replaced;

  for (const record of Object.values(content)) {
    const sections = record?.content?.sections;
    if (!Array.isArray(sections)) continue;
    for (const section of sections) {
      const blocks = section?.blocks;
      if (!Array.isArray(blocks)) continue;
      const nextBlocks = [];
      for (const block of blocks) {
        if (
          block &&
          block.type === "paragraph" &&
          Array.isArray(block.tokens)
        ) {
          const transformed = transformParagraphBlock(block, resultMap, scale);
          if (transformed.length !== 1 || transformed[0] !== block) {
            replaced += transformed.filter((item) => item.type === "image_block").length;
          }
          nextBlocks.push(...transformed);
          continue;
        }
        nextBlocks.push(block);
      }
      section.blocks = nextBlocks;
    }
  }
  return replaced;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    printUsage();
    return;
  }

  console.log(`[render_tikz_assets] input: ${toDisplayPath(options.inputAbs)}`);
  const content = await loadJson(options.inputAbs);
  const references = collectReferences(content);
  const dedup = new Map();

  for (const reference of references) {
    const conclusionId = reference.conclusionId || sourceConclusionId(reference.source);
    const key = resultKey(conclusionId, reference.source);
    if (!dedup.has(key)) {
      dedup.set(key, {
        source: reference.source,
        conclusionId,
        occurrences: [],
      });
    }
    dedup.get(key).occurrences.push(reference.path);
  }

  let items = Array.from(dedup.values());
  const totalEligibleUnique = items.length;
  const skippedByLimit =
    options.limit && options.limit < items.length ? items.length - options.limit : 0;
  if (options.limit) items = items.slice(0, options.limit);

  const resultMap = new Map();
  const reportItems = [];
  let rendered = 0;
  let reused = 0;
  let failed = 0;
  let dryRunCount = 0;

  for (let index = 0; index < items.length; index += 1) {
    const item = items[index];
    const progress = `${index + 1}/${items.length}`;
    try {
      if (!isConclusionId(item.conclusionId)) {
        throw new Error(`Cannot resolve conclusion ID for ${item.source}`);
      }

      if (options.dryRun) {
        dryRunCount += 1;
        const dryResult = {
          ok: true,
          status: "dry_run",
          asset: null,
        };
        resultMap.set(resultKey(item.conclusionId, item.source), dryResult);
        reportItems.push({
          conclusionId: item.conclusionId,
          source: item.source,
          status: "dry_run",
          png: null,
          width_px: null,
          height_px: null,
          occurrences: item.occurrences,
          error: null,
        });
        console.log(`[render_tikz_assets] ${progress} ${item.source} -> dry_run`);
        continue;
      }

      const renderResult = await renderTikzToPng({
        source: item.source,
        conclusionId: item.conclusionId,
        outDirAbs: options.outDirAbs,
        assetBase: options.assetBase,
        scale: options.scale,
        force: options.force,
      });
      const asset = buildAsset(renderResult, options.scale);
      resultMap.set(resultKey(item.conclusionId, item.source), {
        ok: true,
        status: renderResult.status,
        asset,
      });
      if (renderResult.status === "rendered") rendered += 1;
      if (renderResult.status === "reused") reused += 1;

      reportItems.push({
        conclusionId: item.conclusionId,
        source: item.source,
        hash: renderResult.hash,
        status: renderResult.status,
        png: renderResult.pngUrl,
        width_px: renderResult.widthPx,
        height_px: renderResult.heightPx,
        occurrences: item.occurrences,
        error: null,
      });
      console.log(
        `[render_tikz_assets] ${progress} ${item.source} -> ${renderResult.status}`,
      );
    } catch (error) {
      failed += 1;
      const message = error instanceof Error ? error.message : String(error);
      resultMap.set(resultKey(item.conclusionId, item.source), {
        ok: false,
        status: "failed",
        error: message,
      });
      reportItems.push({
        conclusionId: item.conclusionId,
        source: item.source,
        status: "failed",
        png: null,
        width_px: null,
        height_px: null,
        occurrences: item.occurrences,
        error: message,
      });
      console.error(
        `[render_tikz_assets] ${progress} ${item.source} -> failed: ${message}`,
      );
    }
  }

  let replaced = 0;
  if (!options.dryRun) {
    replaced = applyRenderedTikz(content, resultMap, options.scale);
    await saveJson(options.outputAbs, content);
  } else {
    console.log("[render_tikz_assets] dry-run: skip writing output json");
  }

  const report = {
    input: toDisplayPath(options.inputAbs),
    output: toDisplayPath(options.outputAbs),
    outDir: toDisplayPath(options.outDirAbs),
    assetBase: options.assetBase,
    scale: options.scale,
    totalReferences: references.length,
    totalEligibleUnique,
    rendered,
    reused,
    failed,
    skipped: skippedByLimit,
    dryRun: options.dryRun,
    dryRunCount,
    replaced,
    items: reportItems,
  };
  await saveJson(options.reportAbs, report);

  console.log(`[render_tikz_assets] rendered: ${rendered}`);
  console.log(`[render_tikz_assets] reused: ${reused}`);
  console.log(`[render_tikz_assets] failed: ${failed}`);
  console.log(`[render_tikz_assets] replaced image blocks: ${replaced}`);
  console.log(
    `[render_tikz_assets] output json: ${toDisplayPath(options.outputAbs)}`,
  );
  console.log(
    `[render_tikz_assets] report: ${toDisplayPath(options.reportAbs)}`,
  );
}

main().catch((error) => {
  console.error("[render_tikz_assets] failed");
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
