/**
 * ==========================================
 * LaTeX 结构拆块引擎（小程序专用 · 生产级）
 * ==========================================
 *
 * 🎯 核心目标：
 * 将复杂 LaTeX（statement / proof / examples）
 * 拆分成“小块 HTML”，避免：
 *
 * ❌ 小程序 setData 超限
 * ❌ mp-html 渲染失败
 * ❌ KaTeX DOM 爆炸
 *
 * ------------------------------------------
 * ✅ 支持结构：
 * - statementbox（按 enumerate 拆）
 * - proofbox（按 enumerate 拆）
 * - examplebox（按“例题”拆）
 *
 * ------------------------------------------
 * ✅ 输出结构：
 *
 * {
 *   statement_blocks: [],
 *   proof_blocks: [],
 *   example_blocks: []
 * }
 *
 * ------------------------------------------
 * ✅ 设计原则：
 * - 不破坏 LaTeX 公式（$...$）
 * - 不破坏 KaTeX 渲染
 * - 拆分粒度可控
 * - 高容错（即使格式不规范也能跑）
 *
 * ==========================================
 */

/**
 * ==========================================
 * 工具函数：提取 LaTeX 环境内容
 * ==========================================
 */
function extractEnvironment(text, envName) {
  if (!text) return "";
  const regex = new RegExp(
    `\\\\begin\\{${envName}\\}([\\s\\S]*?)\\\\end\\{${envName}\\}`,
    "i",
  );
  const match = text.match(regex);
  return match ? match[1].trim() : "";
}

/**
 * 通用列表提取：支持 enumerate 和 itemize
 */
function extractListContent(text) {
  if (!text) return null;
  // 匹配最外层的列表环境
  const listMatch = text.match(
    /\\begin\{(?:enumerate|itemize)\}([\s\S]*?)\\end\{(?:enumerate|itemize)\}/i,
  );
  return listMatch ? listMatch[1].trim() : null;
}

/**
 * ==========================================
 * 工具函数：按 \item 安全拆分（核心）
 * ==========================================
 *
 * ⚠️ 不能简单 split("\\item")
 * 否则会破坏公式
 */
function splitLatexItems(content) {
  if (!content) return [];
  // 匹配 \item 后接空白字符、换行、或直接开始的内容（如 \item$x$）
  // 使用 split 后，第一项通常是 \begin 后的空字符串，需要过滤
  return content
    .split(/\\item(?:\s+|$|(?=\$))/g)
    .map((s) => s.trim())
    .filter(Boolean);
}

/**
 * ==========================================
 * 工具函数：包装 HTML（统一风格）
 * ==========================================
 */
function wrapBlock(tag, content) {
  return `<${tag}>${content}</${tag}>`;
}

/**
 * ==========================================
 * ① 拆 Statement（核心结论）
 * ==========================================
 *
 * 🎯 拆分策略：
 * - 提取 statementbox
 * - 查找 enumerate
 * - 按 \item 拆分
 *
 * 输出：
 *   ["<li>...</li>", ...]
 */
function splitStatementBlocks(latex) {
  const content = extractEnvironment(latex, "statementbox") || latex;
  const listContent = extractListContent(content);

  if (!listContent) return [wrapBlock("div", content)];

  return splitLatexItems(listContent).map((item) => wrapBlock("li", item));
}

/**
 * ==========================================
 * ② 拆 Proof（证明过程）
 * ==========================================
 *
 * 🎯 拆分策略：
 * - 提取 proofbox
 * - 按 enumerate → 每一步
 *
 * 输出：
 *   ["步骤1 HTML", "步骤2 HTML"]
 */
function splitProofBlocks(latex) {
  const content = extractEnvironment(latex, "proofbox") || latex;
  const listContent = extractListContent(content);

  if (!listContent) return [wrapBlock("div", content)];

  // 证明过程通常每一步是一个 div，方便小程序控制间距
  return splitLatexItems(listContent).map((item) => wrapBlock("div", item));
}

/**
 * ==========================================
 * ③ 拆 Examples（例题）
 * ==========================================
 *
 * 🎯 拆分策略（重点）：
 * 按 “\textbf{例题 X：}” 拆分
 *
 * 优势：
 * - 不依赖 enumerate
 * - 适配你当前内容结构
 *
 * 输出：
 *   ["例题1 HTML", "例题2 HTML"]
 */
function splitExampleBlocks(latex) {
  const content = extractEnvironment(latex, "examplebox") || latex;

  // 更加宽容的正则：支持 例题1、例题 1、冒号中英文、有无空格
  const separator = /\\textbf\{例题\s*\d+\s*[：:]\s*\}/g;

  const titles = content.match(separator) || [];
  const parts = content.split(separator).filter((p) => p.trim().length > 0);

  if (titles.length === 0) return [wrapBlock("div", content)];

  return parts.map((part, i) => {
    const title = titles[i] || `<strong>例题 ${i + 1}：</strong>`;
    return wrapBlock("div", `${title}<br/>${part.trim()}`);
  });
}

/**
 * ==========================================
 * 导出接口（统一入口）
 * ==========================================
 */
module.exports = {
  splitStatementBlocks,
  splitProofBlocks,
  splitExampleBlocks,
};
