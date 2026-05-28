#!/usr/bin/env node

/**
 * ============================================================
 * 基于 canonical_content_v2.json 的公式图片化清洗脚本（第一阶段）
 * ============================================================
 *
 * 一、这个脚本解决什么问题
 * ------------------------------------------------------------
 * 在内容库里，公式节点原本是 `type: "math_block"`。其中一部分公式在小程序端
 * 渲染效果不理想，后续需要走“公式图片化”流程。但第一阶段不直接生成图片，
 * 只做离线内容清洗，把人工确认过的节点标记为 `math_image_pending`。
 *
 * 二、为什么要这么做（核心设计原因）
 * ------------------------------------------------------------
 * 1) 自动规则（例如 \sqrt / \dfrac / aligned）容易误伤，无法替代人工 UX 判断。
 * 2) 先做“人工确认 + 内容标记”可以把决策与渲染解耦，降低风险。
 * 3) 分阶段推进：先稳定数据结构，再交给后续图片生成模块补 asset。
 *
 * 三、严格门槛（必须同时满足）
 * ------------------------------------------------------------
 * 1) node.type === "math_block"
 * 2) node.need_image === "true"        // 严格布尔 1 / false 都不算
 * 3) node.latex 为非空字符串
 *
 * 只有满足以上 3 条，才转换为 `math_image_pending`。
 *
 * 四、规则系统在本阶段的角色
 * ------------------------------------------------------------
 * 规则仅用于“记录与统计”，不是决策门槛：
 * - 记录节点的 matchedRules，便于审计与调试
 * - 统计 ruleHits，便于后续优化推荐策略
 * - 即使 matchedRules 为空，只要 need_image === true 仍会转换
 *
 * 五、转换后会补充的字段
 * ------------------------------------------------------------
 * - type: "math_image_pending"
 * - imageKey: 由 latex 归一化后做 sha1 截断得到（formula_xxx）
 * - imageName: 默认等于 imageKey
 * - matchedRules: 命中的规则名数组
 * - asset: null
 *
 * 说明：原字段（id、align、style、className、note 等）会尽量保留。
 *
 * 六、使用方法（中文示例）
 * ------------------------------------------------------------
 * 1) 常规输出到新文件（推荐）
 *    node tools/formula_image_pipeline/scan_math_blocks.mjs \
 *      --input data/content/canonical_content_v2.json \
 *      --output data/content/canonical_content_v2.pending.json \
 *      --rules tools/formula_image_pipeline/formula_image_rules.example.json
 *
 * 2) 仅统计，不写文件
 *    node tools/formula_image_pipeline/scan_math_blocks.mjs \
 *      --input data/content/canonical_content_v2.json \
 *      --dry-run
 *
 * 3) 原地覆盖（需显式确认）
 *    node tools/formula_image_pipeline/scan_math_blocks.mjs \
 *      --input data/content/canonical_content_v2.json \
 *      --in-place
 *
 * 七、怎么干的（实现思路）
 * ------------------------------------------------------------
 * 1) 读取 input JSON 和 rules JSON
 * 2) 对任意对象/数组做通用递归遍历（不依赖固定字段名）
 * 3) 统计 math_block 总数、人工标记数、转换数、空 latex 告警数等
 * 4) 命中节点生成 imageKey/imageName 并改成 math_image_pending
 * 5) 输出 summary / ruleHits / 样例，支持 dry-run 与 in-place
 *
 * 八、边界与安全策略
 * ------------------------------------------------------------
 * - 默认不覆盖 input，避免误操作
 * - `--output` 与 `--in-place` 冲突时会报错退出
 * - 关键错误（文件不存在、JSON 解析失败、regex 非法、写入失败）非 0 退出
 * - need_image=true 但 latex 为空仅告警，不中断整批处理
 */

import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";

const DEFAULT_RULES_PATH = path.join(
  "tools",
  "formula_image_pipeline",
  "formula_image_rules.example.json"
);
const SAMPLE_LIMIT = 8;

function printUsage() {
  console.log(`Usage:
  node tools/formula_image_pipeline/scan_math_blocks.mjs --input <path> [options]

Options:
  --output <path>   Output JSON path (default: <input>.pending.json)
  --rules <path>    Rule config JSON path (default: ${DEFAULT_RULES_PATH})
  --dry-run         Print summary only, do not write output file
  --in-place        Overwrite input file (explicit opt-in only)
  --help            Show this message
`);
}

function parseArgs(argv) {
  const options = {
    input: "",
    output: "",
    rules: DEFAULT_RULES_PATH,
    dryRun: false,
    inPlace: false,
    help: false,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];

    if (arg === "--help" || arg === "-h") {
      options.help = true;
      continue;
    }

    if (arg === "--dry-run") {
      options.dryRun = true;
      continue;
    }

    if (arg === "--in-place") {
      options.inPlace = true;
      continue;
    }

    const needsValue = arg === "--input" || arg === "--output" || arg === "--rules";
    if (needsValue) {
      const value = argv[i + 1];
      if (!value || value.startsWith("--")) {
        throw new Error(`Missing value for ${arg}.`);
      }
      if (arg === "--input") options.input = value;
      if (arg === "--output") options.output = value;
      if (arg === "--rules") options.rules = value;
      i += 1;
      continue;
    }

    throw new Error(`Unknown argument: ${arg}`);
  }

  return options;
}

function defaultOutputPath(inputPath) {
  if (inputPath.toLowerCase().endsWith(".json")) {
    return `${inputPath.slice(0, -5)}.pending.json`;
  }
  return `${inputPath}.pending.json`;
}

function isNonEmptyString(value) {
  return typeof value === "string" && value.trim().length > 0;
}

function normalizeLatexForHash(latex) {
  return latex.trim().replace(/\s+/g, " ");
}

function formulaHash(latex) {
  return crypto
    .createHash("sha1")
    .update(normalizeLatexForHash(latex))
    .digest("hex")
    .slice(0, 12);
}

function buildImageKey(latex) {
  return `formula_${formulaHash(latex)}`;
}

function isManuallyMarkedForImage(node) {
  return node?.type === "math_block" && node?.need_image === "true";
}

function buildNodePath(parentPath, key) {
  if (typeof key === "number") {
    return `${parentPath}[${key}]`;
  }
  if (parentPath === "$") {
    return `${parentPath}.${key}`;
  }
  return `${parentPath}.${key}`;
}

function normalizeForPreview(latex, maxLength = 120) {
  const compact = latex.trim().replace(/\s+/g, " ");
  if (compact.length <= maxLength) return compact;
  return `${compact.slice(0, maxLength - 3)}...`;
}

function toDisplayPath(absPath) {
  const rel = path.relative(process.cwd(), absPath);
  if (!rel || rel.startsWith("..")) {
    return absPath;
  }
  return rel.split(path.sep).join("/");
}

async function readJsonFile(jsonPath, label) {
  let raw = "";
  try {
    raw = await fs.readFile(jsonPath, "utf8");
  } catch (error) {
    if (error && error.code === "ENOENT") {
      throw new Error(`${label} not found: ${jsonPath}`);
    }
    throw new Error(`${label} read failed: ${jsonPath}\n${error.message}`);
  }

  try {
    return JSON.parse(raw);
  } catch (error) {
    throw new Error(`${label} JSON parse failed: ${jsonPath}\n${error.message}`);
  }
}

function compileRules(ruleConfig) {
  const matchers = Array.isArray(ruleConfig?.matchers) ? ruleConfig.matchers : [];
  const compiledRules = [];
  const ruleHits = {};

  for (let index = 0; index < matchers.length; index += 1) {
    const matcher = matchers[index];
    if (!matcher || matcher.enabled !== true) continue;

    const name = typeof matcher.name === "string" && matcher.name.trim()
      ? matcher.name.trim()
      : `matcher_${index}`;
    const type = matcher.type;
    const pattern = matcher.pattern;

    if (!isNonEmptyString(pattern)) {
      throw new Error(`Enabled matcher "${name}" has empty pattern.`);
    }

    if (type === "includes") {
      compiledRules.push({
        name,
        test: (latex) => latex.includes(pattern),
      });
      ruleHits[name] = 0;
      continue;
    }

    if (type === "regex") {
      try {
        const regex = new RegExp(pattern);
        compiledRules.push({
          name,
          test: (latex) => regex.test(latex),
        });
        ruleHits[name] = 0;
      } catch (error) {
        throw new Error(
          `Invalid regex in matcher "${name}": ${pattern}\n${error.message}`
        );
      }
      continue;
    }

    throw new Error(`Unsupported matcher type for "${name}": ${String(type)}`);
  }

  return { compiledRules, ruleHits };
}

function collectMatchedRules(latex, compiledRules) {
  const matches = [];
  for (const rule of compiledRules) {
    if (rule.test(latex)) {
      matches.push(rule.name);
    }
  }
  return matches;
}

function transformTree(root, compiledRulesResult) {
  const stats = {
    totalNodesScanned: 0,
    mathBlockCount: 0,
    manualNeedImageCount: 0,
    convertedPendingCount: 0,
    skippedMathBlockWithoutNeedImage: 0,
    emptyLatexNeedImageCount: 0,
    uniqueImageKeyCount: 0,
  };
  const warnings = [];
  const samples = [];
  const uniqueImageKeys = new Set();
  const ruleHits = { ...compiledRulesResult.ruleHits };

  function visit(node, nodePath) {
    stats.totalNodesScanned += 1;

    if (Array.isArray(node)) {
      return node.map((item, index) => visit(item, buildNodePath(nodePath, index)));
    }

    if (!node || typeof node !== "object") {
      return node;
    }

    if (node.type === "math_block") {
      stats.mathBlockCount += 1;

      if (!isManuallyMarkedForImage(node)) {
        stats.skippedMathBlockWithoutNeedImage += 1;
        return node;
      }

      stats.manualNeedImageCount += 1;

      if (!isNonEmptyString(node.latex)) {
        stats.emptyLatexNeedImageCount += 1;
        warnings.push(
          `need_image=true but latex is empty at ${nodePath}; skipped conversion`
        );
        return node;
      }

      const latex = node.latex;
      const matchedRules = collectMatchedRules(
        latex,
        compiledRulesResult.compiledRules
      );
      for (const ruleName of matchedRules) {
        ruleHits[ruleName] = (ruleHits[ruleName] || 0) + 1;
      }

      const imageKey = buildImageKey(latex);
      uniqueImageKeys.add(imageKey);
      stats.convertedPendingCount += 1;

      if (samples.length < SAMPLE_LIMIT) {
        samples.push({
          path: nodePath,
          imageKey,
          matchedRules,
          latexPreview: normalizeForPreview(latex),
        });
      }

      return {
        ...node,
        type: "math_image_pending",
        imageKey,
        imageName: imageKey,
        matchedRules,
        asset: null,
      };
    }

    const next = {};
    for (const [key, value] of Object.entries(node)) {
      next[key] = visit(value, buildNodePath(nodePath, key));
    }
    return next;
  }

  const transformed = visit(root, "$");
  stats.uniqueImageKeyCount = uniqueImageKeys.size;

  return { transformed, stats, warnings, samples, ruleHits };
}

async function writeJsonFile(targetPath, data) {
  try {
    await fs.mkdir(path.dirname(targetPath), { recursive: true });
    await fs.writeFile(targetPath, `${JSON.stringify(data, null, 2)}\n`, "utf8");
  } catch (error) {
    throw new Error(`Output write failed: ${targetPath}\n${error.message}`);
  }
}

async function main() {
  const options = parseArgs(process.argv.slice(2));

  if (options.help) {
    printUsage();
    return;
  }

  if (!options.input) {
    throw new Error("Missing required --input argument.");
  }

  const inputAbsPath = path.resolve(options.input);
  const rulesAbsPath = path.resolve(options.rules);
  const outputFromArg = options.output ? path.resolve(options.output) : "";

  if (options.inPlace && outputFromArg && outputFromArg !== inputAbsPath) {
    throw new Error(
      "--output and --in-place are both set but point to different files. " +
        "Use only --in-place, or set --output exactly equal to --input."
    );
  }

  const outputAbsPath = options.inPlace
    ? inputAbsPath
    : outputFromArg || path.resolve(defaultOutputPath(options.input));

  if (!options.inPlace && outputAbsPath === inputAbsPath) {
    throw new Error(
      "Output path equals input path. Use --in-place to overwrite input explicitly."
    );
  }

  const inputJson = await readJsonFile(inputAbsPath, "Input file");
  const rulesJson = await readJsonFile(rulesAbsPath, "Rules file");
  const compiledRulesResult = compileRules(rulesJson);

  if (rulesJson?.decisionPolicy?.rulesAreDecisionGate === true) {
    console.warn(
      "[scan_math_blocks] rulesAreDecisionGate=true is currently ignored in this phase."
    );
  }

  const { transformed, stats, warnings, samples, ruleHits } = transformTree(
    inputJson,
    compiledRulesResult
  );

  if (!options.dryRun) {
    await writeJsonFile(outputAbsPath, transformed);
  }

  const summary = {
    ...stats,
    outputJsonPath: toDisplayPath(outputAbsPath),
    dryRun: options.dryRun,
  };

  if (options.inPlace) {
    console.log(`[scan_math_blocks] in-place mode enabled: ${toDisplayPath(inputAbsPath)}`);
  }

  console.log("Summary:");
  console.log(JSON.stringify(summary, null, 2));
  console.log("Rule Hits:");
  console.log(JSON.stringify({ ruleHits }, null, 2));

  if (warnings.length > 0) {
    console.log(`Warnings (${warnings.length}):`);
    for (const warning of warnings) {
      console.log(`- ${warning}`);
    }
  }

  if (samples.length > 0) {
    console.log("Manual need_image=true samples:");
    console.log(JSON.stringify(samples, null, 2));
  } else {
    console.log("Manual need_image=true samples: []");
  }
}

main().catch((error) => {
  console.error("[scan_math_blocks] failed");
  console.error(error.message);
  process.exitCode = 1;
});
