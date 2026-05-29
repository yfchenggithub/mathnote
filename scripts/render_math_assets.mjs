#!/usr/bin/env node

/**
 * ============================================================
 * 公式图片渲染脚本（渲染层 / 第 2 步）
 * ============================================================
 *
 * 一、这个脚本做什么
 * ------------------------------------------------------------
 * 从内容 JSON 中递归查找并处理以下节点：
 *   1) type === "math_block"
 *   2) need_image === "true"
 *   3) latex 为非空字符串
 *
 * 对命中节点执行：
 *   - LaTeX -> SVG（MathJax）
 *   - SVG -> PNG/WebP（sharp）
 *   - 回写节点：type 改为 "math_image"，并写入 asset 信息
 *
 * 二、为什么要有这个脚本
 * ------------------------------------------------------------
 * 第一阶段（标记层）已决定“哪些公式需要图片化”，本脚本只负责渲染执行。
 * 这样做可以把“是否需要图片”的判断与“图片生产”解耦，降低误改风险并便于追踪。
 *
 * 三、怎么做（核心流程）
 * ------------------------------------------------------------
 *   1) 读取输入 JSON
 *   2) 递归扫描节点并筛选待渲染目标
 *   3) 用 sha1(latex.trim()) 前 16 位生成稳定 hash
 *   4) 相同 hash 只渲染一次（去重复用）
 *   5) 若目标文件已存在且 force=false，则复用并读取 metadata
 *   6) 成功渲染后回写 asset，失败则保留原 math_block
 *   7) 输出新 JSON + 渲染报告
 *
 * 四、严格边界
 * ------------------------------------------------------------
 *   - 不处理 math_inline
 *   - 不自动新增 need_image
 *   - 不做复杂规则判断
 *   - 只改 type 与 asset，保留节点其他字段
 *   - 单个公式失败不影响全局流程
 *
 * 五、输出物
 * ------------------------------------------------------------
 *   - 图片目录：--out-dir（默认值见常量）
 *   - 内容 JSON：--output（默认值见常量）
 *   - 报告文件：reports/render_math_assets_report.json
 *
 * 六、使用方式（示例）
 * ------------------------------------------------------------
 *   node scripts/render_math_assets.mjs
 *   node scripts/render_math_assets.mjs --dry-run true
 *   node scripts/render_math_assets.mjs --force true
 *   node scripts/render_math_assets.mjs --in-place
 *   node scripts/render_math_assets.mjs --limit 50
 *
 * 七、技术约束
 * ------------------------------------------------------------
 *   - 使用 MathJax + sharp 渲染链路
 *   - 不使用 Playwright / Chromium / 浏览器截图
 */

import MathJax from "mathjax";
import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import sharp from "sharp";

const DEFAULT_INPUT = path.join("data", "content", "canonical_content_v2.json");
const DEFAULT_OUTPUT = path.join(
  "data",
  "content",
  "canonical_content_v2.with_formula_assets.json",
);
const DEFAULT_OUT_DIR = path.join("public", "static", "formulas");
const DEFAULT_REPORT = path.join("reports", "render_math_assets_report.json");
const DEFAULT_ASSET_BASE = "/static/formulas";
const DEFAULT_SCALE = 3;
const DEFAULT_PADDING_DISPLAY_PX = 4;
const CONCLUSION_ID_RE = /^[A-Z]\d{3}$/;

function printUsage() {
  console.log(`Usage:
  node scripts/render_math_assets.mjs [options]

Options:
  --input <path>        Input JSON path (default: ${DEFAULT_INPUT})
  --output <path>       Output JSON path (default: ${DEFAULT_OUTPUT})
  --in-place            Overwrite input JSON directly
  --out-dir <path>      Formula asset directory (default: ${DEFAULT_OUT_DIR})
  --asset-base <path>   Asset base path (default: ${DEFAULT_ASSET_BASE})
  --public-base <path>  Alias of --asset-base (backward compatibility)
  --scale <number>      Output scale factor (default: ${DEFAULT_SCALE})
  --force [bool]        Force re-render existing files (default: false)
  --dry-run [bool]      Scan only, do not generate files (default: false)
  --limit <number>      Max formulas to process (default: unlimited)
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
  if (!normalized) {
    throw new Error("--asset-base must not be empty.");
  }
  if (/^https?:\/\//i.test(normalized)) {
    throw new Error(
      "--asset-base must be a relative path (e.g. /static/formulas), not a full URL.",
    );
  }
  if (!normalized.startsWith("/")) {
    normalized = `/${normalized}`;
  }
  normalized = normalized.replace(/\/+$/g, "");
  if (!normalized) {
    throw new Error("--asset-base must not be empty.");
  }
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
        "--in-place is set, but --output points to a different file. " +
          "Remove --output or make it exactly equal to --input.",
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
  let raw = "";
  try {
    raw = await fs.readFile(jsonPath, "utf8");
  } catch (error) {
    if (error?.code === "ENOENT") {
      throw new Error(`Input JSON not found: ${jsonPath}`);
    }
    throw new Error(`Failed to read JSON file: ${jsonPath}\n${error.message}`);
  }

  try {
    return JSON.parse(raw);
  } catch (error) {
    throw new Error(`Failed to parse JSON file: ${jsonPath}\n${error.message}`);
  }
}

async function saveJson(jsonPath, data) {
  await fs.mkdir(path.dirname(jsonPath), { recursive: true });
  await fs.writeFile(jsonPath, `${JSON.stringify(data, null, 2)}\n`, "utf8");
}

function isConclusionId(value) {
  return typeof value === "string" && CONCLUSION_ID_RE.test(value);
}

function walkJson(node, visitor, nodePath = "$", context = { conclusionId: null }) {
  if (Array.isArray(node)) {
    for (let index = 0; index < node.length; index += 1) {
      walkJson(node[index], visitor, `${nodePath}[${index}]`, context);
    }
    return;
  }

  if (!node || typeof node !== "object") {
    return;
  }

  const nextContext = { ...context };
  if (isConclusionId(node.id)) {
    nextContext.conclusionId = node.id;
  }

  visitor(node, nodePath, nextContext);

  for (const [key, value] of Object.entries(node)) {
    walkJson(value, visitor, `${nodePath}.${key}`, nextContext);
  }
}

function normalizeLatex(latex) {
  if (typeof latex !== "string") return "";
  return latex.trim();
}

function isNeedImageEnabled(value) {
  if (value === true) return true;
  if (typeof value === "string") {
    return value.trim().toLowerCase() === "true";
  }
  return false;
}

function isContentRenderSchemaV2Node(node) {
  if (!node || typeof node !== "object") return false;
  if (node.render_schema_version !== 2) return false;
  return Object.prototype.hasOwnProperty.call(node, "primary_formula");
}

function shouldRenderNode(node) {
  if (!node || typeof node !== "object") return false;
  if (node.type !== "math_block") return false;
  if (!isNeedImageEnabled(node.need_image)) return false;
  return normalizeLatex(node.latex).length > 0;
}

function inspectPrimaryFormula(node) {
  if (!isContentRenderSchemaV2Node(node)) return null;

  const primaryFormula = node.primary_formula;
  if (!primaryFormula || typeof primaryFormula !== "object") return null;
  if (Array.isArray(primaryFormula)) return null;

  return {
    marked: isNeedImageEnabled(primaryFormula.need_image),
    latex: normalizeLatex(primaryFormula.latex),
  };
}

function shouldRenderPrimaryFormula(node) {
  const inspected = inspectPrimaryFormula(node);
  if (!inspected || !inspected.marked) return false;
  return inspected.latex.length > 0;
}

function hashLatex(latex) {
  return crypto
    .createHash("sha1")
    .update(normalizeLatex(latex))
    .digest("hex")
    .slice(0, 16);
}

async function initMathJax() {
  await MathJax.init({
    loader: {
      load: ["input/tex", "output/svg"],
    },
    svg: {
      fontCache: "none",
    },
  });
  return MathJax;
}

async function latexToSvg(mathJaxInstance, latex) {
  const containerNode = await mathJaxInstance.tex2svgPromise(latex, {
    display: true,
  });
  const adaptor = mathJaxInstance.startup.adaptor;
  const svgNode = adaptor.tags(containerNode, "svg")[0];

  if (!svgNode) {
    throw new Error("MathJax returned no SVG node.");
  }

  return adaptor.serializeXML(svgNode);
}

function scaleSuffix(scale) {
  return `${scale}x`;
}

function joinAssetPath(assetBase, ...segments) {
  const normalizedBase = assetBase.replace(/\/+$/g, "");
  const normalizedSegments = segments.map((segment) =>
    String(segment || "").replace(/^\/+|\/+$/g, ""),
  );
  const joined = [normalizedBase, ...normalizedSegments].join("/");
  return joined.replace(/\/{2,}/g, "/");
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

async function svgToImages({
  svg,
  outDirAbs,
  conclusionId,
  hash,
  scale,
  force,
}) {
  const outConclusionDirAbs = path.join(outDirAbs, conclusionId);
  await fs.mkdir(outConclusionDirAbs, { recursive: true });

  const suffix = scaleSuffix(scale);
  const pngFilename = `${hash}@${suffix}.png`;
  const webpFilename = `${hash}@${suffix}.webp`;
  const pngPath = path.join(outConclusionDirAbs, pngFilename);
  const webpPath = path.join(outConclusionDirAbs, webpFilename);
  const pngExists = await fileExists(pngPath);
  const webpExists = await fileExists(webpPath);

  if (!force && pngExists && webpExists) {
    const { widthPx, heightPx } = await readImageSize(pngPath);
    return {
      status: "reused",
      pngPath,
      webpPath,
      pngFilename,
      webpFilename,
      widthPx,
      heightPx,
    };
  }

  const paddingPx = Math.max(1, Math.round(DEFAULT_PADDING_DISPLAY_PX * scale));
  const density = Math.max(72, Math.round(72 * scale));

  const rasterPngBuffer = await sharp(Buffer.from(svg), {
    density,
  })
    .png()
    .toBuffer();

  const withPaddingPngBuffer = await sharp(rasterPngBuffer)
    .extend({
      top: paddingPx,
      bottom: paddingPx,
      left: paddingPx,
      right: paddingPx,
      background: { r: 0, g: 0, b: 0, alpha: 0 },
    })
    .png()
    .toBuffer();

  const pngInfo = await sharp(withPaddingPngBuffer)
    .png({
      compressionLevel: 9,
      adaptiveFiltering: true,
      palette: false,
    })
    .toFile(pngPath);

  await sharp(withPaddingPngBuffer)
    .webp({
      lossless: true,
      quality: 100,
      alphaQuality: 100,
    })
    .toFile(webpPath);

  if (!pngInfo.width || !pngInfo.height) {
    throw new Error(`Failed to get image size for ${pngPath}`);
  }

  return {
    status: "rendered",
    pngPath,
    webpPath,
    pngFilename,
    webpFilename,
    widthPx: pngInfo.width,
    heightPx: pngInfo.height,
  };
}

function buildAsset({
  assetBase,
  conclusionId,
  pngFilename,
  webpFilename,
  widthPx,
  heightPx,
  scale,
}) {
  return {
    png: joinAssetPath(assetBase, conclusionId, pngFilename),
    webp: joinAssetPath(assetBase, conclusionId, webpFilename),
    width_px: widthPx,
    height_px: heightPx,
    display_width_px: Math.round(widthPx / scale),
    display_height_px: Math.round(heightPx / scale),
    scale,
  };
}

async function renderOneFormula({
  mathJaxInstance,
  latex,
  conclusionId,
  hash,
  outDirAbs,
  assetBase,
  scale,
  force,
  dryRun,
}) {
  if (dryRun) {
    return {
      ok: true,
      status: "dry_run",
      hash,
      latex,
      conclusionId,
      asset: null,
      widthPx: null,
      heightPx: null,
      pngUrl: joinAssetPath(
        assetBase,
        conclusionId,
        `${hash}@${scaleSuffix(scale)}.png`,
      ),
      webpUrl: joinAssetPath(
        assetBase,
        conclusionId,
        `${hash}@${scaleSuffix(scale)}.webp`,
      ),
    };
  }

  const svg = await latexToSvg(mathJaxInstance, latex);
  const imageResult = await svgToImages({
    svg,
    outDirAbs,
    conclusionId,
    hash,
    scale,
    force,
  });

  const asset = buildAsset({
    assetBase,
    conclusionId,
    pngFilename: imageResult.pngFilename,
    webpFilename: imageResult.webpFilename,
    widthPx: imageResult.widthPx,
    heightPx: imageResult.heightPx,
    scale,
  });

  return {
    ok: true,
    status: imageResult.status,
    hash,
    latex,
    conclusionId,
    asset,
    widthPx: imageResult.widthPx,
    heightPx: imageResult.heightPx,
    pngUrl: asset.png,
    webpUrl: asset.webp,
  };
}

function toDisplayPath(absPath) {
  const relative = path.relative(process.cwd(), absPath);
  if (!relative || relative.startsWith("..")) return absPath;
  return relative.split(path.sep).join("/");
}

async function main() {
  const options = parseArgs(process.argv.slice(2));

  if (options.help) {
    printUsage();
    return;
  }

  if (options.inPlace) {
    console.log(
      `[render_math_assets] in-place mode: ${toDisplayPath(options.inputAbs)}`,
    );
  }

  console.log(`[render_math_assets] input: ${toDisplayPath(options.inputAbs)}`);
  const content = await loadJson(options.inputAbs);

  const candidates = [];
  let totalNeedImageMathBlock = 0;
  let emptyLatexMarkedMathBlock = 0;
  let totalNeedImagePrimaryFormula = 0;
  let emptyLatexMarkedPrimaryFormula = 0;

  walkJson(content, (node, nodePath, context) => {
    if (!node || typeof node !== "object") return;
    if (node.type === "math_block" && isNeedImageEnabled(node.need_image)) {
      totalNeedImageMathBlock += 1;
      if (normalizeLatex(node.latex).length === 0) {
        emptyLatexMarkedMathBlock += 1;
      }
    }

    const primaryFormulaInspected = inspectPrimaryFormula(node);
    if (primaryFormulaInspected && primaryFormulaInspected.marked) {
      totalNeedImagePrimaryFormula += 1;
      if (primaryFormulaInspected.latex.length === 0) {
        emptyLatexMarkedPrimaryFormula += 1;
      }
    }

    if (shouldRenderNode(node)) {
      candidates.push({
        sourceType: "math_block",
        node,
        path: nodePath,
        latex: normalizeLatex(node.latex),
        conclusionId: context.conclusionId,
      });
    }

    if (shouldRenderPrimaryFormula(node)) {
      const inspected = inspectPrimaryFormula(node);
      candidates.push({
        sourceType: "primary_formula",
        contentNode: node,
        path: `${nodePath}.primary_formula`,
        latex: inspected ? inspected.latex : "",
        conclusionId: context.conclusionId,
      });
    }
  });

  console.log(
    `[render_math_assets] scanned marked math_block count: ${totalNeedImageMathBlock}`,
  );
  console.log(
    `[render_math_assets] scanned marked primary_formula count: ${totalNeedImagePrimaryFormula}`,
  );
  if (emptyLatexMarkedMathBlock > 0) {
    console.log(
      `[render_math_assets] warning: ${emptyLatexMarkedMathBlock} marked math_block nodes have empty latex and were skipped`,
    );
  }
  if (emptyLatexMarkedPrimaryFormula > 0) {
    console.log(
      `[render_math_assets] warning: ${emptyLatexMarkedPrimaryFormula} marked primary_formula nodes have empty latex and were skipped`,
    );
  }

  const dedupMap = new Map();
  for (const candidate of candidates) {
    if (!isConclusionId(candidate.conclusionId)) {
      const unresolvedKey = `__UNRESOLVED__::${candidate.path}`;
      dedupMap.set(unresolvedKey, {
        hash: null,
        key: unresolvedKey,
        latex: candidate.latex,
        conclusionId: null,
        occurrences: [candidate],
      });
      continue;
    }

    const formulaHash = hashLatex(candidate.latex);
    const dedupKey = `${candidate.conclusionId}::${formulaHash}`;
    if (!dedupMap.has(dedupKey)) {
      dedupMap.set(dedupKey, {
        hash: formulaHash,
        key: dedupKey,
        latex: candidate.latex,
        conclusionId: candidate.conclusionId,
        occurrences: [],
      });
    }
    dedupMap.get(dedupKey).occurrences.push(candidate);
  }

  let formulas = Array.from(dedupMap.values());
  const totalEligibleUnique = formulas.length;
  const skippedByLimit =
    options.limit && options.limit < formulas.length
      ? formulas.length - options.limit
      : 0;
  if (options.limit) {
    formulas = formulas.slice(0, options.limit);
  }

  const formulaResultMap = new Map();
  const reportItems = [];
  let rendered = 0;
  let reused = 0;
  let failed = 0;
  let dryRunCount = 0;

  let mathJaxInstance = null;
  if (!options.dryRun && formulas.length > 0) {
    mathJaxInstance = await initMathJax();
  }

  for (let index = 0; index < formulas.length; index += 1) {
    const formula = formulas[index];
    const progress = `${index + 1}/${formulas.length}`;
    const sourceTypes = Array.from(
      new Set(formula.occurrences.map((occurrence) => occurrence.sourceType)),
    );

    try {
      if (!isConclusionId(formula.conclusionId)) {
        throw new Error(
          `Cannot resolve conclusion ID for formula at ${formula.occurrences[0]?.path || "unknown path"}`,
        );
      }

      const result = await renderOneFormula({
        mathJaxInstance,
        latex: formula.latex,
        conclusionId: formula.conclusionId,
        hash: formula.hash,
        outDirAbs: options.outDirAbs,
        assetBase: options.assetBase,
        scale: options.scale,
        force: options.force,
        dryRun: options.dryRun,
      });
      formulaResultMap.set(formula.key, result);

      if (result.status === "rendered") rendered += 1;
      if (result.status === "reused") reused += 1;
      if (result.status === "dry_run") dryRunCount += 1;

      reportItems.push({
        conclusionId: formula.conclusionId,
        hash: formula.hash,
        latex: formula.latex,
        source_types: sourceTypes,
        status: result.status,
        png: result.pngUrl,
        webp: result.webpUrl,
        width_px: result.widthPx,
        height_px: result.heightPx,
        error: null,
      });

      console.log(
        `[render_math_assets] ${progress} ${formula.hash} -> ${result.status}`,
      );
    } catch (error) {
      failed += 1;
      const message = error instanceof Error ? error.message : String(error);
      formulaResultMap.set(formula.key, {
        ok: false,
        status: "failed",
        error: message,
      });

      reportItems.push({
        conclusionId: formula.conclusionId,
        hash: formula.hash,
        latex: formula.latex,
        source_types: sourceTypes,
        status: "failed",
        png: null,
        webp: null,
        width_px: null,
        height_px: null,
        error: message,
      });

      console.error(
        `[render_math_assets] ${progress} ${formula.hash} -> failed: ${message}`,
      );
    }
  }

  if (!options.dryRun) {
    for (const formula of formulas) {
      const formulaResult = formulaResultMap.get(formula.key);
      if (!formulaResult || formulaResult.ok !== true || !formulaResult.asset) {
        continue;
      }

      for (const occurrence of formula.occurrences) {
        if (occurrence.sourceType === "math_block" && occurrence.node) {
          const originalNode = occurrence.node;
          originalNode.type = "math_image";
          originalNode.asset = formulaResult.asset;
          continue;
        }

        if (
          occurrence.sourceType === "primary_formula" &&
          occurrence.contentNode &&
          typeof occurrence.contentNode === "object"
        ) {
          const primaryFormula = occurrence.contentNode.primary_formula;
          if (
            !primaryFormula ||
            typeof primaryFormula !== "object" ||
            Array.isArray(primaryFormula)
          ) {
            continue;
          }
          primaryFormula.type = "math_image";
          primaryFormula.asset = formulaResult.asset;
          continue;
        }
      }
    }
  }

  if (!options.dryRun) {
    await saveJson(options.outputAbs, content);
  } else {
    console.log("[render_math_assets] dry-run: skip writing output json");
  }

  const report = {
    input: toDisplayPath(options.inputAbs),
    output: toDisplayPath(options.outputAbs),
    outDir: toDisplayPath(options.outDirAbs),
    assetBase: options.assetBase,
    scale: options.scale,
    totalMarked: totalNeedImageMathBlock,
    totalMarkedMathBlock: totalNeedImageMathBlock,
    totalMarkedPrimaryFormula: totalNeedImagePrimaryFormula,
    totalMarkedAllSources:
      totalNeedImageMathBlock + totalNeedImagePrimaryFormula,
    emptyLatexMarkedMathBlock,
    emptyLatexMarkedPrimaryFormula,
    emptyLatexMarkedAllSources:
      emptyLatexMarkedMathBlock + emptyLatexMarkedPrimaryFormula,
    totalEligibleUnique,
    rendered,
    reused,
    failed,
    skipped: skippedByLimit,
    dryRun: options.dryRun,
    dryRunCount,
    items: reportItems,
  };

  await saveJson(options.reportAbs, report);

  console.log(`[render_math_assets] rendered: ${rendered}`);
  console.log(`[render_math_assets] reused: ${reused}`);
  console.log(`[render_math_assets] failed: ${failed}`);
  console.log(
    `[render_math_assets] output json: ${toDisplayPath(options.outputAbs)}`,
  );
  console.log(
    `[render_math_assets] report: ${toDisplayPath(options.reportAbs)}`,
  );
}

main().catch((error) => {
  console.error("[render_math_assets] failed");
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
