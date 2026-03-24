# ============================================
# build_core_index.py
# --------------------------------------------
# 功能：
# 1. 扫描 D:\mathnote 所有模块
# 2. 提取二级结论（tex + meta.json）
# 3. 构建内容数据
# 4. 输出 JS 模块（适配小程序 require）
#
# 设计动机：
# - 小程序不稳定支持 JSON require
# - JS module.exports 100%兼容
# - 构建阶段完成数据整合 → 运行时极快
#
# 作者：为“极致搜索体验”设计
# ============================================

import os
import json
import re
from pathlib import Path
import traceback
import sys
import io

# 强制设置标准输出为 UTF-8，解决 Windows 终端乱码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
# ==============================
# 配置区（你只需要改这里）
# ==============================

BASE_DIR = r"D:\mathnote"
OUTPUT_DIR = r"D:\mathnote\data\content"

# 选择要生成的模块（None = 全部）
TARGET_MODULES = [
    # "07-inequality",
    "03-vector",
    # "02-trigonometry"
]

# 需要生成 HTML 的字段（高度可扩展）
HTML_FIELDS = ["statement", "explanation", "proof", "examples", "traps", "summary_text"]


# ==============================
# 工具函数
# ==============================

import re


def clean_tex(text: str) -> str:
    """
    【功能】
    将 LaTeX 文本转换为“可读 + 可搜索”的纯文本。

    【设计目标】
    1. 保留数学结构（尤其是分式、绝对值、不等式）
    2. 去除排版噪音（环境、样式命令）
    3. 输出适合：
       - 小程序展示
       - 搜索索引构建

    【核心原则】
    👉 结构优先 > 清理命令
    👉 特殊结构（如 \\frac）必须优先处理，避免被通用规则破坏
    """

    if not text:
        return ""

    # =========================
    # 1. 移除注释（必须最先做）
    # =========================
    # 原因：
    # % 后面的内容在 LaTeX 中是注释，不应该参与任何解析
    text = re.sub(r"%.*", "", text)

    # =========================
    # 2. 去掉环境（结构壳）
    # =========================
    # 如：
    # \begin{enumerate} / \end{enumerate}
    # \begin{statementbox}
    #
    # 原因：
    # 这些只是排版容器，不影响语义
    text = re.sub(r"\\(begin|end)\{.*?\}", "", text)

    # =========================
    # 3. 处理列表项
    # =========================
    # \item → 可读列表符号
    #
    # 原因：
    # 保留“结构感”，提升用户阅读体验
    text = re.sub(r"\\item", "\n· ", text)

    # =========================
    # 4. 处理分式（最高优先级！！）
    # =========================
    # ⚠️ 这是整个系统最关键的一步
    #
    # 原因：
    # 如果先处理 \cmd{}，会把 \frac 拆坏
    #
    # 支持嵌套：
    # \frac{a}{\frac{b}{c}}
    #
    def replace_frac(s: str) -> str:
        pattern = r"\\frac\{((?:[^{}]|\{[^{}]*\})*)\}\{((?:[^{}]|\{[^{}]*\})*)\}"
        while re.search(pattern, s):
            s = re.sub(pattern, r"(\1) / (\2)", s)
        return s

    text = replace_frac(text)

    # =========================
    # 5. 处理根号（关键新增）
    # =========================
    # \sqrt{ab} → sqrt(ab)
    text = re.sub(r"\\sqrt\{((?:[^{}]|\{[^{}]*\})*)\}", r"sqrt(\1)", text)

    # =========================
    # 5. 处理绝对值（left/right）
    # =========================
    # \left| x \right| → | x |
    #
    # 原因：
    # 保留语义，但去掉 LaTeX 语法噪音
    text = re.sub(r"\\left\|", "|", text)
    text = re.sub(r"\\right\|", "|", text)

    # =========================
    # 6. 处理普通命令（排除 frac）
    # =========================
    # \textbf{xxx} → xxx
    # \sqrt{a} → a （这里只做基础处理）
    #
    # ⚠️ 排除 frac，避免重复破坏
    #
    def replace_cmd(s: str) -> str:
        pattern = r"\\(?!frac)[a-zA-Z]+\{(.*?)\}"
        while re.search(pattern, s):
            s = re.sub(pattern, r"\1", s)
        return s

    text = replace_cmd(text)

    # =========================
    # 7. 数学符号标准化
    # =========================
    # 原因：
    # 统一表达 → 提高搜索命中率
    symbol_map = {
        r"\\iff": " <=> ",
        r"\\implies": " => ",
        r"\\geqslant": " ≥ ",
        r"\\leqslant": " ≤ ",
        r"\\to": " → ",
        r"\\neq": " ≠ ",
        r"\\cdot": " · ",
        r"\\infty": " ∞ ",
        r"\\mathbb\{R\}": "R",
        r"\\mathbb\{N\}": "N",
        r"\\mathbb\{Z\}": "Z",
        r"\\in": " ∈ ",
    }

    for cmd, repl in symbol_map.items():
        text = re.sub(cmd, repl, text)

    # =========================
    # 8. 去掉数学环境符号 $
    # =========================
    text = text.replace("$", "")

    # =========================
    # 9. 清理剩余命令（无参数）
    # =========================
    # 如：
    # \alpha \quad \text
    #
    # 原因：
    # 已无语义价值
    text = re.sub(r"\\[a-zA-Z]+", " ", text)

    # =========================
    # 10. 去掉多余大括号
    # =========================
    text = text.replace("{", "").replace("}", "")

    # =========================
    # 11. 空白规范化（非常重要）
    # =========================
    # 目的：
    # - 防止搜索索引混乱
    # - 提升可读性
    lines = []
    for line in text.split("\n"):
        line = line.strip()
        if line:
            # 压缩多空格
            line = re.sub(r"\s+", " ", line)
            lines.append(line)

    return "\n".join(lines)


def clean_tex_v3(text):
    """
    将 LaTeX 转换为人可读的纯文本，保留逻辑结构，剔除排版指令。
    """
    if not text:
        return ""

    # 1. 移除 LaTeX 注释
    text = re.sub(r"%.*", "", text)

    # 2. 处理环境标记：直接移除 \begin{...} 和 \end{...}
    # 这会解决你提到的 \begin{statementbox} 和 \begin{enumerate}
    text = re.sub(r"\\(begin|end)\{.*?\}", "", text)

    # 3. 处理列表项：将 \item 替换为换行符和列表符号，增强可读性
    text = re.sub(r"\\item", "\n· ", text)

    # 4. 递归处理带大括号的命令：\cmd{内容} -> 内容
    # 使用循环处理嵌套情况，如 \textbf{\textit{重点}}
    while re.search(r"\\[a-zA-Z]+\{(.*?)\}", text):
        text = re.sub(r"\\[a-zA-Z]+\{(.*?)\}", r"\1", text)

    # 5. 常见数学符号转义（可选，为了让搜索和阅读更自然）
    symbol_map = {
        r"\\iff": " <=> ",
        r"\\implies": " => ",
        r"\\geqslant": "≥",
        r"\\leqslant": "≤",
        r"\\to": "→",
        r"\\neq": "≠",
        r"\\cdot": "·",
        r"\\infty": "∞",
    }
    for cmd, repl in symbol_map.items():
        text = re.sub(cmd, repl, text)

    # 6. 处理分式：\frac{a}{b} -> a/b
    # 使用非贪婪匹配，并循环处理嵌套分式
    while r"\frac" in text:
        # 这个正则匹配 \frac{内容1}{内容2}
        new_text = re.sub(
            r"\\frac\{((?:[^{}]|\{[^{}]*\})*)\}\{((?:[^{}]|\{[^{}]*\})*)\}",
            r"(\1)/(\2)",
            text,
        )
        if new_text == text:
            break  # 防止死循环
        text = new_text
    # 7. 移除数学符号边界符 $
    text = text.replace("$", "")

    # 8. 移除剩余的无参数命令（如 \alpha, \quad, \text）
    text = re.sub(r"\\[a-zA-Z]+", " ", text)

    # 9. 移除多余的大括号
    text = text.replace("{", "").replace("}", "")

    # 10. 清理空白字符：压缩多余空行，保留必要的换行
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)


def clean_tex_v2(text):
    """
    这个版本的函数会移除 textbf、color 等干扰搜索的格式命令，但会保留 sqrt、sin 等关键数学算式，方便你以后做公式搜索
    """
    if not text:
        return ""
    # 1. 去掉注释
    text = re.sub(r"%.*", "", text)
    # 2. 移除常见的纯排版命令，但保留其大括号内的内容
    # 例如 \textbf{重点} -> 重点
    formatting_cmds = [
        r"\\textbf",
        r"\\textit",
        r"\\color\{.*?\}",
        r"\\underline",
        r"\\emph",
    ]
    for cmd in formatting_cmds:
        text = re.sub(cmd + r"\{(.*?)\}", r"\1", text)
    # 3. 压缩空白字符
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_tex_v1(text):
    """
    清理 LaTeX 内容，适合搜索 & 展示
    """
    if not text:
        return ""

    # 去注释
    text = re.sub(r"%.*", "", text)

    # 去命令
    text = re.sub(r"\\[a-zA-Z]+\{.*?\}", "", text)

    # 去多余符号
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""


def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


import subprocess

# Node 渲染脚本路径（你之前已经有）
BASE_PATH = Path(__file__).resolve().parent
NODE_RENDER_SCRIPT = BASE_PATH / "latex_to_html.js"
# NODE_RENDER_SCRIPT = os.path.join("scripts", "latex_to_html.js")


def batch_render_latex(text_map: dict) -> dict:
    """
    ==========================================
    批量 LaTeX → HTML 渲染（核心优化）
    ==========================================

    参数：
        text_map: {id: latex_text}

    返回：
        {id: html}
    """

    if not text_map:
        return {}

    try:
        # 转成 list 结构传给 Node
        payload = [{"id": k, "text": v} for k, v in text_map.items()]

        result = subprocess.run(
            ["node", str(NODE_RENDER_SCRIPT)],
            input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        if result.stderr:
            print("Node stderr:", result.stderr.decode("utf-8"))

        return json.loads(result.stdout.decode("utf-8"))

    except Exception as e:
        print("批量渲染失败:", e)
        return {}


# ==============================
# 全局缓存（避免重复渲染）
# ==============================
RENDER_CACHE = {}


def render_latex_to_html(text: str) -> str:
    """
    ==========================================
    LaTeX → HTML 渲染函数（调用 KaTeX）
    ==========================================

    功能：
    - 调用 Node.js 脚本（latex_to_html.js）
    - 将 LaTeX 转换为 KaTeX HTML

    为什么这样设计：
    - Python 不适合直接跑 KaTeX
    - Node 是官方支持环境
    - 构建阶段完成 → 小程序零压力

    参数：
        text: 原始 LaTeX 字符串

    返回：
        HTML 字符串（可直接用于 mp-html）
    """

    if not text:
        return ""

    # ⭐ 缓存命中
    if text in RENDER_CACHE:
        return RENDER_CACHE[text]

    try:
        result = subprocess.run(
            ["node", NODE_RENDER_SCRIPT],
            input=text.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        html = result.stdout.decode("utf-8")

        # ⭐ 写入缓存
        RENDER_CACHE[text] = html
        return html

    except subprocess.CalledProcessError as e:
        print("❌ KaTeX 渲染失败：", e.stderr.decode())
        return text  # fallback，保证系统不崩


def smart_truncate(text, length=80):
    return text[:length] + ("..." if len(text) > length else "")


# ==============================
# 核心处理
# ==============================

TOTAL_COUNT = 0


def process_module(module_path):
    """
    处理单个模块（如 07-inequality）
    """
    module_name = os.path.basename(module_path)
    print(f"\n处理模块: {module_name}")

    result = {}
    # ==========================
    # 收集所有需要渲染的 LaTeX
    # ==========================
    all_items = []
    all_render_tasks = {}

    for item in os.listdir(module_path):
        item_path = os.path.join(module_path, item)

        if not os.path.isdir(item_path):
            continue

        try:
            # meta
            meta = read_json(os.path.join(item_path, "meta.json"))

            # 读取 6 个内容文件
            # ==========================
            # ✅ 正确读取方式（关键修改）
            # ==========================

            # 原始 LaTeX（绝对不能 clean，用于渲染）
            statement_latex = read_file(os.path.join(item_path, "01-statement.tex"))
            explanation_latex = read_file(os.path.join(item_path, "02-explanation.tex"))
            proof_latex = read_file(os.path.join(item_path, "03-proof.tex"))
            examples_latex = read_file(os.path.join(item_path, "04-examples.tex"))
            traps_latex = read_file(os.path.join(item_path, "05-traps.tex"))
            summary_latex = read_file(os.path.join(item_path, "06-summary.tex"))

            # 清洗版（用于搜索 / summary）
            statement_clean = clean_tex(statement_latex)
            # print(f"\nstatement_latex: {statement_latex}")
            # print(f"\nstatement_clean: {statement_clean}")
            explanation = clean_tex(explanation_latex)
            proof = clean_tex(proof_latex)
            examples = clean_tex(examples_latex)
            traps = clean_tex(traps_latex)
            summary_clean = clean_tex(summary_latex)

            item_id = meta.get("id", item)

            # ==========================
            # 构建基础数据（保留原始 LaTeX）
            # ==========================
            FIELD_MAP = {
                "statement": statement_latex,
                "explanation": explanation_latex,
                "proof": proof_latex,
                "examples": examples_latex,
                "traps": traps_latex,
                "summary_text": summary_latex,
            }

            item_data = {
                "id": item,
                "title": meta.get("title", item),
                "summary": smart_truncate(summary_clean),
                # 原始 LaTeX（用于复制 & 搜索）
                **FIELD_MAP,  # 自动展开
                # （可选）搜索优化字段（以后做搜索增强用）
                "statement_search": statement_clean,
            }

            # ==========================
            # ⭐ 新增：HTML 渲染层, HTML 渲染（用 latex 数据！）
            # ==========================
            for field, latex_text in FIELD_MAP.items():
                html_field = f"{field}_html"
                if latex_text.strip():
                    # latex_text 不为空
                    task_id = f"{item_id}::{field}"
                    all_render_tasks[task_id] = latex_text
                    # print(f"\ntask_id: {task_id}")
                    # print(f"\nlatex_text: {latex_text}")
                    # print(f"\nall_render_tasks: {all_render_tasks}")
                    item_data[html_field] = task_id
                else:
                    item_data[html_field] = ""
            all_items.append((item_id, item_data))

        except Exception as e:
            print(f"跳过 {item}: {e}")
            traceback.print_exc()

    # 一次性渲染
    render_results = batch_render_latex(all_render_tasks)

    # 回填结果
    for item_id, item_data in all_items:
        for field in FIELD_MAP.keys():
            html_field = f"{field}_html"
            task_id = item_data.get(html_field)
            print(f"\ntask_id: {task_id}")
            if task_id in render_results:
                html_render = render_results[task_id]
                item_data[html_field] = html_render
                print(f"\nhtml_render: {html_render}")
            else:
                item_data[html_field] = ""
        result[item_id] = item_data
    return module_name, result


def save_js(module_name, data):
    """
    输出 JS 文件
    """
    # 生成简单模块名（去数字前缀）
    simple_name = module_name.split("-", 1)[-1]

    output_path = os.path.join(OUTPUT_DIR, f"{simple_name}.js")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    js_content = "module.exports = " + json.dumps(data, ensure_ascii=False, indent=2)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"已生成: {output_path}")


# ==============================
# 主流程
# ==============================


def main():
    print("开始构建内容索引（JS版）")

    for module in os.listdir(BASE_DIR):
        module_path = os.path.join(BASE_DIR, module)

        if not os.path.isdir(module_path):
            continue

        # 模块过滤
        if TARGET_MODULES and module not in TARGET_MODULES:
            continue

        module_name, data = process_module(module_path)

        save_js(module_name, data)

    print("\n构建完成！")


if __name__ == "__main__":
    main()
