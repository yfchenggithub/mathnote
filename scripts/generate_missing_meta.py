#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Generate/refresh meta.json for selected L2 conclusion folders.

Focus:
- Strict schema compatibility with search builder
- Conservative extraction from local tex only
- Cleaner summary/keywords/formulaTokens than the first pass
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

try:
    from pypinyin import lazy_pinyin
except Exception:  # pragma: no cover
    lazy_pinyin = None


PROJECT_ROOT = Path(__file__).resolve().parent.parent

TARGET_ROOTS = [
    "00_set",
    "01_function",
    "02_sequence",
    "03_conic",
    "04_vector",
    "05_geometry-solid",
    "06_probability-stat",
    "07_inequality",
    "08_trigonometry",
    "09_geometry-plane",
]

MODULE_MAP = {
    "00_set": "set",
    "01_function": "function",
    "02_sequence": "sequence",
    "03_conic": "conic",
    "04_vector": "vector",
    "05_geometry-solid": "geometry-solid",
    "06_probability-stat": "probability-stat",
    "07_inequality": "inequality",
    "08_trigonometry": "trigonometry",
    "09_geometry-plane": "geometry-plane",
}

CATEGORY_MAP = {
    "00_set": "集合",
    "01_function": "函数",
    "02_sequence": "数列",
    "03_conic": "解析几何",
    "04_vector": "向量",
    "05_geometry-solid": "立体几何",
    "06_probability-stat": "概率统计",
    "07_inequality": "不等式",
    "08_trigonometry": "三角函数",
    "09_geometry-plane": "解析几何",
}

KNOWLEDGE_NODE_MAP = {
    "00_set": "其他-未分类-待定",
    "01_function": "函数-性质-单调性",
    "02_sequence": "数列-求和技巧-错位相减",
    "03_conic": "解析几何-圆锥曲线-椭圆",
    "04_vector": "向量-应用-坐标表示",
    "05_geometry-solid": "立体几何-空间向量-坐标法",
    "06_probability-stat": "概率-古典概型-基本概率",
    "07_inequality": "不等式-经典不等式-均值不等式",
    "08_trigonometry": "三角函数-基本关系-同角恒等",
    "09_geometry-plane": "解析几何-综合-最值问题",
}

ALT_NODES_MAP = {
    "00_set": ["其他-未分类-待定", "代数-式的变形-恒等变形"],
    "01_function": ["函数-性质-单调性", "函数-综合-函数与不等式"],
    "04_vector": ["向量-数量积-几何意义", "向量-应用-平行与垂直"],
    "09_geometry-plane": ["解析几何-圆-位置关系", "解析几何-综合-最值问题"],
}

PREREQUISITES_MAP = {
    "00_set": ["集合的基本运算", "子集与补集定义"],
    "01_function": ["导数定义", "导数符号与函数变化"],
    "04_vector": ["向量加减与数乘", "向量数量积"],
    "09_geometry-plane": ["圆的标准方程", "点到圆的距离定义"],
}

INTENTS_MAP = {
    "00_set": ["化简", "证明", "计数", "判断关系"],
    "01_function": ["判定单调性", "求最值", "求零点", "证明性质"],
    "04_vector": ["向量计算", "坐标求点", "证明共线", "求几何量"],
    "09_geometry-plane": ["求最小距离", "求最大距离", "位置关系判断", "参数计算"],
}

PROBLEM_TYPES_MAP = {
    "00_set": ["集合化简", "集合证明"],
    "01_function": ["导数应用", "函数性质判定"],
    "04_vector": ["向量法证明", "几何计算"],
    "09_geometry-plane": ["距离最值", "解析几何计算"],
}

MODULE_HINT_KEYWORDS = {
    "00_set": ["子集", "补集", "交集", "并集", "容斥"],
    "01_function": ["导数", "单调性", "极值", "零点"],
    "04_vector": ["向量", "数量积", "共线", "重心", "垂心"],
    "09_geometry-plane": ["圆", "距离", "最值", "外点", "内点"],
}

TITLE_OVERRIDES = {
    "S001": "有限集合子集计数公式",
    "S003": "德摩根律",
    "S005": "两个集合的容斥原理",
    "S006": "集合包含关系等价判定",
    "S008": "命题否定形式转换",
    "S009": "四种命题关系",
    "S010": "充分必要条件判定",
    "F001": "导数判定单调性",
    "F002": "导数判定单调性",
    "F003": "导数判定单调性",
    "V001": "极化恒等式",
    "V002": "极化恒等式（三角形模型）",
    "V003": "矩形对角向量恒等式",
    "V004": "长方体向量平方和恒等式",
    "V005": "向量点积定值轨迹",
    "V006": "奔驰定理",
    "V007": "奔驰定理推论",
    "V008": "三角形重心向量结论",
    "V009": "三角形内心向量结论",
    "V010": "三角形旁心向量结论",
    "V011": "三角形外心向量结论",
    "V012": "等和线定理",
    "V013": "爪子定理（三点共线）",
    "V014": "点积边长公式",
    "V015": "哈密顿定理",
    "V016": "欧拉线四点共线定理",
    "V017": "九点圆定理",
    "V018": "垂心性质汇总",
    "V019": "三角形垂心向量结论",
    "P001": "圆外一点到圆的距离极值",
    "P002": "圆内一点到圆的距离极值",
    "P003": "圆上一点到圆的距离极值",
    "P004": "点到圆距离极值统一模型",
    "P005": "直线与圆的距离极值",
    "P006": "两圆之间的距离极值",
}

GENERIC_TITLE_WORDS = {
    "结论",
    "核心公式",
    "一句话总结",
    "几何意义",
    "命题类型",
    "原结论",
    "基准等式",
    "模长恒等性",
    "数量积等量性",
    "核心等式",
}

REFRESH_TARGETS = [
    "00_set/S001_Subset_Count",
    "00_set/S003_DeMorgan",
    "00_set/S005_InclusionExclusion",
    "00_set/S006_Inclusion",
    "00_set/S008_NegationForms",
    "00_set/S009_FourPropositions",
    "00_set/S010_Necessary_and_Sufficient_Conditions",
    "01_function/F001_monotonicity",
    "01_function/F002_extrema",
    "01_function/F003_zero-points",
    "04_vector/V001_Polarization_Identity",
    "04_vector/V002_Polarization_Identity_triangular",
    "04_vector/V003_Polarization_Identity_rectangle",
    "04_vector/V004_Polarization_Identity_rectangle_three_dimensional",
    "04_vector/V005_Polarization_Identity_vector_product",
    "04_vector/V006_Mercedes_Theorem",
    "04_vector/V007_Mercedes_Theorem_Corollary",
    "04_vector/V008_gravity_center",
    "04_vector/V009_Incenter",
    "04_vector/V010_Excenter",
    "04_vector/V011_Circumcenter",
    "04_vector/V012_Equal_Sum_Line",
    "04_vector/V013_Claw",
    "04_vector/V014_Dot_Product_Side_Formula",
    "04_vector/V015_Hamilton",
    "04_vector/V016_Euler_Line_Four_Points",
    "04_vector/V017_Nine_point_Circle",
    "04_vector/V018_Orthocenter_Properties",
    "04_vector/V019_Orthocenter",
    "09_geometry-plane/P001_distance-extreme-from-external-point",
    "09_geometry-plane/P002_distance-extreme-from-internal-point",
    "09_geometry-plane/P003_distance-extreme-from-point-on-circle",
    "09_geometry-plane/P004_distance-extreme-between-point-and-circle-unified",
    "09_geometry-plane/P005_distance-extreme-between-line-and-circle",
    "09_geometry-plane/P006_distance-extreme-between-two-circles",
]

FORMULA_COMMAND_HINTS = (
    "\\cap",
    "\\cup",
    "\\subset",
    "\\cdot",
    "\\vec",
    "\\frac",
    "\\sqrt",
    "\\sum",
    "\\sin",
    "\\cos",
    "\\tan",
    "\\le",
    "\\ge",
    "\\neq",
    "\\Rightarrow",
    "\\Leftrightarrow",
    "\\in",
    "\\notin",
)

VAR_STOP_WORDS = {
    "cap",
    "cup",
    "left",
    "right",
    "frac",
    "sqrt",
    "sum",
    "cdot",
    "sin",
    "cos",
    "tan",
    "min",
    "max",
    "text",
}


@dataclass(frozen=True)
class BlockTexts:
    statement: str
    explanation: str
    proof: str
    examples: str
    traps: str
    summary: str


def read_utf8(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def read_blocks(item_dir: Path) -> BlockTexts:
    return BlockTexts(
        statement=read_utf8(item_dir / "01_statement.tex"),
        explanation=read_utf8(item_dir / "02_explanation.tex"),
        proof=read_utf8(item_dir / "03_proof.tex"),
        examples=read_utf8(item_dir / "04_examples.tex"),
        traps=read_utf8(item_dir / "05_traps.tex"),
        summary=read_utf8(item_dir / "06_summary.tex"),
    )


def strip_comments(text: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", text)


def normalize_space(text: str) -> str:
    s = re.sub(r"\s+", " ", text).strip()
    s = re.sub(r"\s*([，。；：！？])\s*", r"\1", s)
    s = re.sub(r"\s*([,;:!?])\s*", r"\1 ", s)
    s = re.sub(r"\s{2,}", " ", s).strip()
    return s


def clean_sentence(text: str, max_len: int = 140) -> str:
    s = normalize_space(text)
    s = re.sub(r"^\d+[\.、)]\s*", "", s)
    s = s.strip(" .，,;；:：\"“”")
    if len(s) > max_len:
        s = s[:max_len].rstrip("，,;； ")
    return s


def latex_to_text(text: str) -> str:
    s = strip_comments(text)
    s = re.sub(r"\\input\{[^{}]*\}", " ", s)
    s = re.sub(r"\\begin\{[^{}]*\}", " ", s)
    s = re.sub(r"\\end\{[^{}]*\}", " ", s)

    for cmd in ("textbf", "emph", "paragraph", "textit", "underline"):
        s = re.sub(rf"\\{cmd}\{{([^{{}}]*)\}}", r" \1 ", s)

    s = re.sub(r"\\item\b", "。", s)

    # Remove remaining commands but keep their text content already extracted above.
    s = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^{}]*\})?", " ", s)
    s = s.replace("\\[", " ").replace("\\]", " ")
    s = s.replace("\\(", " ").replace("\\)", " ")
    s = s.replace("$", " ")
    s = s.replace("{", " ").replace("}", " ")
    s = s.replace("\\", " ")
    return normalize_space(s)


def first_sentence(text: str, max_len: int = 140) -> str:
    if not text:
        return ""
    chunks = re.split(r"[。！？!?；;\n\r]", text)
    for chunk in chunks:
        c = clean_sentence(chunk, max_len=max_len)
        if len(c) >= 6:
            return c
    return clean_sentence(text, max_len=max_len)


def clean_title(candidate: str) -> str:
    t = clean_sentence(candidate, max_len=80)
    t = re.sub(r"^[A-Z]\d{2,4}\s*", "", t)
    t = t.strip("：:。.,，;； ")
    if "（" in t and "）" in t and t.startswith("结论"):
        inner = t.split("（", 1)[1].rsplit("）", 1)[0].strip()
        if inner:
            t = inner
    if "(" in t and ")" in t and t.startswith("结论"):
        inner = t.split("(", 1)[1].rsplit(")", 1)[0].strip()
        if inner:
            t = inner
    if t.startswith("结论"):
        t = t[2:].strip("：:。.,，;； ")
    t = t.replace("结论", "").strip("：:。.,，;； ")
    if t in GENERIC_TITLE_WORDS or len(t) < 3:
        return ""
    return t


def extract_title(doc_id: str, item_dir: Path, blocks: BlockTexts) -> str:
    if doc_id in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[doc_id]

    for match in re.finditer(r"\\(?:paragraph|textbf)\{([^{}]{2,180})\}", blocks.statement):
        title = clean_title(match.group(1))
        if title:
            return title

    title = clean_title(first_sentence(latex_to_text(blocks.statement), max_len=80))
    if title:
        return title

    title = clean_title(first_sentence(latex_to_text(blocks.summary), max_len=80))
    if title:
        return title

    fallback = re.sub(r"^[A-Z]\d{3}_", "", item_dir.name).replace("_", " ").replace("-", " ")
    fallback = clean_sentence(fallback, max_len=80)
    return fallback or doc_id


def normalize_formula(raw: str) -> str:
    text = " ".join(raw.split()).strip().strip(".,;，；。")
    return text


def is_meaningful_formula(expr: str) -> bool:
    e = expr.strip()
    if len(e) < 3:
        return False
    if any(op in e for op in ("=", "<", ">", "+", "-", "*", "/", "^", "|")):
        return True
    return any(cmd in e for cmd in FORMULA_COMMAND_HINTS)


def is_noise_formula(expr: str) -> bool:
    # Variable list like "A, B, C" is not a formula.
    if re.fullmatch(r"[A-Za-z0-9_ ,，]+", expr.strip()):
        return True
    return False


def collect_formulas(texts: Iterable[str]) -> list[str]:
    patterns = [
        r"\\\[(.*?)\\\]",
        r"\$\$(.*?)\$\$",
        r"\$(.+?)\$",
        r"\\\((.*?)\\\)",
    ]
    candidates: list[str] = []
    for text in texts:
        src = strip_comments(text)
        for pattern in patterns:
            for match in re.finditer(pattern, src, flags=re.S):
                expr = normalize_formula(match.group(1))
                if not expr:
                    continue
                if is_noise_formula(expr):
                    continue
                if not is_meaningful_formula(expr):
                    continue
                candidates.append(expr)

    out: list[str] = []
    seen: set[str] = set()
    for expr in candidates:
        key = re.sub(r"\s+", "", expr)
        if key in seen:
            continue
        seen.add(key)
        out.append(expr)
    return out[:10]


def braces_balanced(text: str) -> bool:
    return text.count("{") == text.count("}")


def formula_tokens(formulas: list[str]) -> list[str]:
    tokens: list[str] = []
    for f in formulas:
        expr = normalize_formula(f)
        if is_meaningful_formula(expr):
            tokens.append(expr)
        if "=" in expr:
            left, right = expr.split("=", 1)
            left = normalize_formula(left)
            right = normalize_formula(right)
            if is_meaningful_formula(left):
                tokens.append(left)
            if is_meaningful_formula(right):
                tokens.append(right)
        for frac in re.findall(r"\\frac\{[^{}]+\}\{[^{}]+\}", expr):
            tokens.append(normalize_formula(frac))
        for abs_expr in re.findall(r"\|[^|]{2,60}\|", expr):
            tokens.append(normalize_formula(abs_expr))

    out: list[str] = []
    seen: set[str] = set()
    for t in tokens:
        t = normalize_formula(t)
        if len(t) < 2:
            continue
        if len(t) > 120:
            continue
        if not braces_balanced(t):
            continue
        if re.fullmatch(r"[()\[\]{}+\-*/=<>|\\\s]+", t):
            continue
        if t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out[:12]


def make_pinyin(text: str) -> tuple[str, str]:
    if lazy_pinyin is None:
        return "", ""
    chars = re.sub(r"[^\u4e00-\u9fff]", "", text)
    if not chars:
        return "", ""
    syllables = lazy_pinyin(chars)
    full = " ".join(syllables)
    abbr = "".join(s[0] for s in syllables if s)
    return full, abbr


def extract_sentences(text: str, min_len: int, limit: int, max_len: int = 120) -> list[str]:
    plain = latex_to_text(text)
    parts = re.split(r"[。！？!?；;\n\r]", plain)
    out: list[str] = []
    for part in parts:
        sentence = clean_sentence(part, max_len=max_len)
        if len(sentence) < min_len:
            continue
        if sentence.count("=") > 3 and len(sentence) > 80:
            continue
        out.append(sentence)
        if len(out) >= limit:
            break
    return out


def choose_summary(blocks: BlockTexts, title: str) -> str:
    summary = first_sentence(latex_to_text(blocks.summary), max_len=92)
    if len(summary) >= 8:
        return summary
    summary = first_sentence(latex_to_text(blocks.statement), max_len=92)
    if len(summary) >= 8:
        return summary
    return f"{title}的核心结论与使用要点。"


def build_aliases(title: str, folder_name: str, category: str) -> list[str]:
    candidates = [
        title,
        re.sub(r"^[A-Z]\d{3}_", "", folder_name).replace("_", " ").replace("-", " "),
        f"{title}结论",
        f"{category}常用结论",
    ]
    out: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        name = clean_sentence(item, max_len=40)
        if len(name) < 2:
            continue
        if name in seen:
            continue
        seen.add(name)
        out.append(name)
    return out[:5]


def build_keywords(root_name: str, title: str, aliases: list[str], formulas: list[str], statement: str) -> list[str]:
    raw: list[str] = []
    raw.extend([title] + aliases)
    raw.extend(MODULE_HINT_KEYWORDS.get(root_name, []))
    raw.extend(formulas[:4])

    plain = latex_to_text(statement)
    raw.extend(re.findall(r"[\u4e00-\u9fff]{2,8}", plain))

    out: list[str] = []
    seen: set[str] = set()
    for item in raw:
        token = clean_sentence(str(item), max_len=60)
        if len(token) < 2:
            continue
        if len(token) > 30 and not is_meaningful_formula(token):
            continue
        key = token.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(token)
        if len(out) >= 15:
            break
    # Ensure at least 8.
    if len(out) < 8:
        for fallback in MODULE_HINT_KEYWORDS.get(root_name, []):
            if fallback not in out:
                out.append(fallback)
            if len(out) >= 8:
                break
    return out


def build_variables(formulas: list[str]) -> dict[str, str]:
    vars_found: list[str] = []
    for formula in formulas:
        cleaned = re.sub(r"\\[a-zA-Z]+", " ", formula)
        for var in re.findall(r"\b[A-Za-z](?:_[A-Za-z0-9]+)?\b", cleaned):
            if var.lower() in VAR_STOP_WORDS:
                continue
            vars_found.append(var)
    out: dict[str, str] = {}
    for var in vars_found:
        if var in out:
            continue
        out[var] = "题设变量"
        if len(out) >= 10:
            break
    return out


def choose_condition(blocks: BlockTexts, formula_list: list[str]) -> str:
    candidates = extract_sentences(blocks.statement + "\n" + blocks.explanation, min_len=8, limit=8, max_len=120)
    for sent in candidates:
        if any(mark in sent for mark in ("设", "若", "当", "满足", "可导", ">", "<", "≥", "≤", "≠")):
            return sent
    if formula_list:
        return f"使用时需满足题设条件，并保证公式 {formula_list[0]} 中各量有定义。"
    return "使用时需满足题设条件与变量定义范围。"


def module_defaults(root_name: str) -> tuple[list[str], list[str], list[str]]:
    intents = INTENTS_MAP.get(root_name, ["求解", "证明", "化简", "应用"])
    problem_types = PROBLEM_TYPES_MAP.get(root_name, ["综合题"])
    prereq = PREREQUISITES_MAP.get(root_name, ["对应模块基础定义与公式"])
    return intents, problem_types, prereq


def discover_missing_dirs() -> list[Path]:
    missing: list[Path] = []
    for root_name in TARGET_ROOTS:
        root_dir = PROJECT_ROOT / root_name
        if not root_dir.is_dir():
            continue
        for sub in sorted(root_dir.iterdir()):
            if sub.is_dir() and not (sub / "meta.json").exists():
                missing.append(sub)
    return missing


def discover_targets() -> list[Path]:
    targets: list[Path] = []
    for rel in REFRESH_TARGETS:
        p = PROJECT_ROOT / rel
        if p.is_dir():
            targets.append(p)
    targets.extend(discover_missing_dirs())

    out: list[Path] = []
    seen: set[str] = set()
    for p in targets:
        key = str(p.resolve())
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    out.sort()
    return out


def build_meta(item_dir: Path) -> dict[str, object]:
    root_name = item_dir.parent.name
    module = MODULE_MAP[root_name]
    category = CATEGORY_MAP[root_name]
    knowledge_node = KNOWLEDGE_NODE_MAP[root_name]
    alt_nodes = ALT_NODES_MAP.get(root_name, [knowledge_node])

    code_match = re.match(r"^([A-Z]\d{3})", item_dir.name)
    doc_id = code_match.group(1) if code_match else item_dir.name

    blocks = read_blocks(item_dir)
    title = extract_title(doc_id, item_dir, blocks)
    summary = choose_summary(blocks, title)
    aliases = build_aliases(title, item_dir.name, category)

    formulas = collect_formulas(
        [blocks.statement, blocks.explanation, blocks.proof, blocks.examples, blocks.summary]
    )
    core_formula = ""
    for formula in formulas:
        if any(op in formula for op in ("=", "<", ">")):
            core_formula = formula
            break
    if not core_formula and formulas:
        core_formula = formulas[0]
    related_formulas = [f for f in formulas if f != core_formula][:3] if core_formula else formulas[:3]

    token_source = [core_formula] + related_formulas if core_formula else formulas
    formula_token_list = formula_tokens(token_source)
    if not formula_token_list and core_formula:
        formula_token_list = [core_formula]

    keywords = build_keywords(root_name, title, aliases, token_source, blocks.statement)

    derivation = extract_sentences(blocks.proof, min_len=10, limit=3, max_len=100)
    if not derivation:
        derivation = extract_sentences(blocks.explanation, min_len=10, limit=3, max_len=100)
    if not derivation:
        derivation = ["依据定义与题设条件进行等价变形，可得到核心结论。"]

    common_tricks = extract_sentences(blocks.traps, min_len=8, limit=4, max_len=95)
    if not common_tricks:
        common_tricks = [
            "先核对适用条件，再代入公式。",
            "注意符号方向与边界情况，避免等价变形失误。",
        ]

    scenarios = extract_sentences(blocks.examples, min_len=8, limit=3, max_len=90)
    if not scenarios:
        scenarios = [f"用于{category}模块常见题型的快速判断与计算。"]

    intents, problem_types, prerequisites = module_defaults(root_name)
    pinyin, pinyin_abbr = make_pinyin(title)

    statement_text = first_sentence(latex_to_text(blocks.statement), max_len=180)
    intuition_text = first_sentence(latex_to_text(blocks.explanation), max_len=100)
    if len(intuition_text) < 8:
        intuition_text = summary

    has_diagram = any(
        marker in (blocks.statement + blocks.explanation + blocks.proof + blocks.examples + blocks.summary).lower()
        for marker in ("tikz", "includegraphics", "geogebra")
    )

    difficulty = 3
    search_boost = round(min(1.0, 0.45 + difficulty * 0.08), 2)

    share_title = f"{title}：条件判断与题型速查"
    share_desc = "适合刷题前速查与课后复盘，聚焦适用条件和常见误区，做同类题时能减少符号与分类讨论错误。"

    meta = {
        "id": doc_id,
        "module": module,
        "core": {
            "title": title,
            "alias": aliases,
            "summary": summary,
            "difficulty": difficulty,
            "category": category,
            "tags": keywords[:6],
        },
        "search": {
            "keywords": keywords,
            "synonyms": aliases[1:] if len(aliases) > 1 else [title],
            "intents": intents,
            "query_templates": [
                title,
                f"{title}怎么用",
                f"{title}常见题型",
            ],
            "ocrKeywords": keywords[:10],
            "latex_patterns": token_source[:6],
            "formulaTokens": formula_token_list[:12],
            "pinyin": pinyin,
            "pinyinAbbr": pinyin_abbr,
        },
        "searchmeta": {
            "titleWeight": 10,
            "keywordWeight": 8,
            "synonymWeight": 6,
            "formulaWeight": 7,
        },
        "ranking": {
            "search_boost": search_boost,
            "hot_score": 62,
            "click_rate": 0,
            "success_rate": 0,
        },
        "math": {
            "core_formula": core_formula,
            "related_formulas": related_formulas,
            "variables": build_variables([core_formula] + related_formulas if core_formula else related_formulas),
            "conditions": choose_condition(blocks, [core_formula] + related_formulas if core_formula else related_formulas),
            "conclusions": [summary],
        },
        "content": {
            "statement": statement_text,
            "derivation": derivation[:3],
            "intuition": intuition_text,
            "common_tricks": common_tricks,
        },
        "usage": {
            "scenarios": scenarios,
            "problem_types": problem_types,
            "exam_frequency": 0.6,
            "exam_score": 5,
        },
        "interactive": {
            "has_diagram": has_diagram,
            "geogebra_id": "",
            "param_demo": {},
        },
        "assets": {
            "svg": f"{doc_id}.svg",
            "png": "",
            "webp": "",
            "video": "",
            "audio": "",
        },
        "shareConfig": {
            "title": share_title,
            "shareDesc": share_desc,
        },
        "relations": {
            "prerequisites": prerequisites,
            "related_ids": [],
            "similar": [f"{category}中的相近变形结论"],
        },
        "meta": {
            "version": 1,
            "source": "AI生成",
            "created_at": str(date.today()),
        },
        "isPro": 0,
        "remarks": "",
        "knowledgeNode": knowledge_node,
        "altNodes": alt_nodes,
    }
    return meta


def main() -> int:
    targets = discover_targets()
    for item_dir in targets:
        data = build_meta(item_dir)
        out_path = item_dir / "meta.json"
        out_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(f"generated={len(targets)}")
    for item_dir in targets:
        print(item_dir.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
