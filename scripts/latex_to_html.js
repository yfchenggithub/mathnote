/**
 * ==========================================
 * LaTeX → HTML 批量渲染引擎（生产级）
 * ==========================================
 *
 * ✅ 功能：
 * - 支持多种 LaTeX 语法（$ / $$ / \( \) / \[ \]）
 * - 批量处理（高性能）
 * - 容错（单条错误不影响整体）
 * - 输出纯净 JSON（适配 Python）
 *
 * ✅ 输入（stdin）：
 *   [
 *     { "id": "xxx", "text": "latex内容" }
 *   ]
 *
 * ✅ 输出（stdout）：
 *   {
 *     "xxx": "<span class='katex'>...</span>"
 *   }
 *
 * ==========================================
 */

const katex = require("katex");

const {
  splitStatementBlocks,
  splitProofBlocks,
  splitExampleBlocks,
} = require("./latex_block_splitter");

/**
 * ===============================
 * 主入口：读取 stdin
 * ===============================
 */
let input = "";

/**
 * 必须指定 utf8（否则中文会乱码）
 */
process.stdin.setEncoding("utf8");

process.stdin.on("data", (chunk) => {
  input += chunk;
});

process.stdin.on("end", () => {
  try {
    const list = JSON.parse(input);

    const result = Object.create(null);

    for (const item of list) {
      // item.id 的格式通常是 "item_id::field_name" (来自 python 的 task_id)
      const [id, field] = item.id.split("::");
      // --- 核心修改：判断是否需要拆分 ---
      if (field === "statement") {
        const blocks = splitStatementBlocks(item.text);
        result[item.id] = blocks.map((b) => renderLatexSafe(b)); // 渲染每一个小块
      } else if (field === "proof") {
        const blocks = splitProofBlocks(item.text);
        result[item.id] = blocks.map((b) => renderLatexSafe(b));
      } else if (field === "examples") {
        const blocks = splitExampleBlocks(item.text);
        result[item.id] = blocks.map((b) => renderLatexSafe(b));
      } else {
        // 普通字段，按原样渲染成单个字符串
        result[item.id] = renderLatexSafe(item.text);
      }
    }

    /**
     * ⚠️ 只能输出 JSON！
     * 不能有 console.log，否则 Python 会解析失败
     */
    process.stdout.write(JSON.stringify(result));
  } catch (err) {
    /**
     * ❗错误写 stderr，不污染 stdout
     */
    console.error("渲染失败:", err.message);
    process.stdout.write("{}");
  }
});

/**
 * ==========================================
 * 预处理：剥离指定 LaTeX 环境（精准版）
 * ==========================================
 *
 * 支持：
 *   - statementbox
 *   - trapbox
 *   - proofbox
 *
 * 行为：
 *   删除 \begin / \end 标签，只保留内容
 *
 * 示例：
 *   \begin{statementbox} 内容 \end{statementbox}
 *   → 内容
 */
function stripTargetEnvironments(text) {
  if (!text) return "";

  const ENV_LIST = [
    "statementbox",
    "trapbox",
    "proofbox",
    "explanationbox",
    "examplebox",
    "summarybox",
  ];

  for (const env of ENV_LIST) {
    const regex = new RegExp(
      `\\\\begin\\{${env}\\}([\\s\\S]*?)\\\\end\\{${env}\\}`,
      "g",
    );

    text = text.replace(regex, (_, content) => {
      return content.trim();
    });
  }

  return text;
}

function transformListEnvironments(text) {
  if (!text) return "";

  // 1. enumerate → <ol>
  text = text.replace(
    /\\begin\{enumerate\}([\s\S]*?)\\end\{enumerate\}/g,
    (_, content) => {
      const items = content
        .split(/\\item/)
        .map((s) => s.trim())
        .filter(Boolean)
        .map((item) => `<li>${item}</li>`)
        .join("");

      return `<ol>${items}</ol>`;
    },
  );

  // 2. itemize → <ul>
  text = text.replace(
    /\\begin\{itemize\}([\s\S]*?)\\end\{itemize\}/g,
    (_, content) => {
      const items = content
        .split(/\\item/)
        .map((s) => s.trim())
        .filter(Boolean)
        .map((item) => `<li>${item}</li>`)
        .join("");

      return `<ul>${items}</ul>`;
    },
  );

  return text;
}

function transformTextCommands(text) {
  if (!text) return "";

  // 加粗
  text = text.replace(/\\textbf\{([\s\S]*?)\}/g, "<strong>$1</strong>");

  // 斜体
  text = text.replace(/\\textit\{([\s\S]*?)\}/g, "<em>$1</em>");

  // 强调（等价斜体）
  text = text.replace(/\\emph\{([\s\S]*?)\}/g, "<em>$1</em>");

  // 下划线
  text = text.replace(/\\underline\{([\s\S]*?)\}/g, "<u>$1</u>");

  // text{}（普通文本容器）
  text = text.replace(/\\text\{([\s\S]*?)\}/g, "$1");

  return text;
}

/**
 * ==========================================
 * 核心：安全渲染入口（永不抛异常）
 * ==========================================
 */
function renderLatexSafe(text) {
  if (!text) return "";

  try {
    // ✅ 1. 先做预处理
    text = stripTargetEnvironments(text);

    // ✅ 2. 新增：处理列表
    text = transformListEnvironments(text);

    // ✅ 3. 新增：文本命令
    text = transformTextCommands(text);

    // ✅ 再做 KaTeX 渲染
    return renderLatex(text);
  } catch (err) {
    // 单条失败 → 原样返回
    return text;
  }
}

/**
 * ==========================================
 * 核心渲染逻辑（分阶段处理）
 * ==========================================
 *
 * 为什么要分阶段？
 * 👉 避免冲突，例如：
 *    $$ 内部再被 $ 误匹配
 *
 * 顺序：
 *   1. $$...$$（块级）
 *   2. \[...\]（块级）
 *   3. \(...\)（行内）
 *   4. $...$（行内）
 */
function renderLatex(text) {
  /**
   * ===============================
   * 1️⃣ 处理 $$...$$（块级公式）
   * ===============================
   */
  text = text.replace(/\$\$([\s\S]+?)\$\$/g, (_, formula) => {
    return renderFormula(formula, true);
  });

  /**
   * ===============================
   * 2️⃣ 处理 \[...\]（块级）
   * ===============================
   */
  text = text.replace(/\\\[([\s\S]+?)\\\]/g, (_, formula) => {
    return renderFormula(formula, true);
  });

  /**
   * ===============================
   * 3️⃣ 处理 \(...\)（行内）
   * ===============================
   */
  text = text.replace(/\\\(([\s\S]+?)\\\)/g, (_, formula) => {
    return renderFormula(formula, false);
  });

  /**
   * ===============================
   * 4️⃣ 处理 $...$（行内）
   *
   * ⚠️ 放最后，避免破坏 $$ 匹配
   * ===============================
   */
  text = text.replace(/\$([^\$]+?)\$/g, (_, formula) => {
    return renderFormula(formula, false);
  });

  return text;
}

/**
 * ==========================================
 * 渲染单个公式（统一入口）
 * ==========================================
 *
 * @param {string} formula LaTeX内容
 * @param {boolean} isBlock 是否块级
 */

const cache = new Map();
function renderFormula(formula, isBlock) {
  const key = (isBlock ? "B:" : "I:") + formula;

  if (cache.has(key)) {
    return cache.get(key);
  }

  const html = katex.renderToString(formula.trim(), {
    displayMode: isBlock,
    throwOnError: false,
    strict: "ignore",
    trust: true,
  });

  cache.set(key, html);

  return html;
}
