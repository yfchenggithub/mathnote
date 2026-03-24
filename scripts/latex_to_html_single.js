/**
 * ==========================================
 * LaTeX → KaTeX HTML 渲染脚本
 * ==========================================
 *
 * 功能：
 * 1. 读取 stdin 输入的 LaTeX 文本
 * 2. 自动识别：
 *    - $...$ 行内公式
 *    - $$...$$ 块级公式
 * 3. 转换为 KaTeX HTML
 * 4. 输出 HTML 字符串（stdout）
 *
 * 设计原则：
 * - 无状态（方便 Python 调用）
 * - 高稳定（错误不抛出）
 * - 可扩展（后续支持更多语法）
 */

const katex = require("katex");

// 读取 stdin
let input = "";

process.stdin.on("data", (chunk) => {
  input += chunk.toString();
});

process.stdin.on("end", () => {
  const output = renderLatex(input);
  process.stdout.write(output);
});

/**
 * 主渲染函数
 */
function renderLatex(text) {
  if (!text) return "";

  try {
    // 1️⃣ 先处理块级公式 $$...$$
    text = text.replace(/\$\$([\s\S]+?)\$\$/g, (_, formula) => {
      return katex.renderToString(formula.trim(), {
        displayMode: true,
        throwOnError: false,
      });
    });

    // 2️⃣ 再处理行内公式 $...$
    text = text.replace(/\$([^\$]+?)\$/g, (_, formula) => {
      return katex.renderToString(formula.trim(), {
        displayMode: false,
        throwOnError: false,
      });
    });

    return text;
  } catch (err) {
    console.error("KaTeX render error:", err);
    return text; // 出错时返回原文（保证不崩）
  }
}
