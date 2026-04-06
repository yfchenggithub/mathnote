from build_detail_page_js import main as _detail_main


if __name__ == "__main__":
    raise SystemExit(_detail_main())

"""
===============================================================================
build_content_js.py
===============================================================================

作用
----
将模块目录中的 `01_statement.tex` 构建为可直接 `require` 的 JS 文件。

当前版本只保留一条最小、清晰、可维护的职责链：

1. 扫描目标模块目录
2. 读取每个结论目录下的 `meta.json`
3. 读取 `01_statement.tex`
4. 对 statement 执行 `clean_tex`
5. 调用 `save_js` 输出 `module.exports = {...}`

这个版本刻意移除了 HTML 渲染、批量 KaTeX、explanation/proof/examples/
summary 等无关流程。这样做的目标很明确：

- 更容易调试：问题只会出现在“扫描 / 读取 / 清洗 / 输出”四个环节
- 更容易扩展：以后如果要加字段，只需要增加字段配置，不需要重写主流程
- 更容易维护：函数职责单一，日志清晰，错误边界明确

输出约定
--------
每个结论目前只输出 3 个字段：

- `id`: 结论 ID，优先使用 `meta.json` 中的 `id`
- `title`: 结论标题，优先使用 `meta.json` 中的 `title`
- `statement`: 经过 `clean_tex` 清洗后的纯文本 statement

说明：
- 输出中的 `statement` 不再保留原始 LaTeX
- `save_js` 的输出方式保持不变，仍然生成 `module.exports = ...`

用法
----
1. 使用默认配置构建：

   py scripts/build_content_js.py

2. 只构建指定模块：

   py scripts/build_content_js.py --module 07_inequality

3. 只调试单个结论目录或结论 ID，并且不落盘：

   py scripts/build_content_js.py --module 07_inequality --item I001_Compound_Inequality_Transformation --debug --dry-run
   py scripts/build_content_js.py --module 07_inequality --item I001 --debug --dry-run

4. 严格模式：

   py scripts/build_content_js.py --strict

维护说明
--------
- 如果以后要新增字段，请优先修改 `CONTENT_FIELD_SPECS`
- 如果以后要调整 LaTeX 清洗策略，请优先修改 `clean_tex` 的分步骤函数
- 不建议再把所有正则逻辑堆回一个超长函数中

Last Updated: 2026-04-05
===============================================================================
"""

# Legacy implementation kept below for reference only.

import argparse
import json
import logging
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Sequence, Tuple


# =============================================================================
# 路径与默认配置
# =============================================================================

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# 这两个变量保留为全局字符串，是为了兼容既有的 save_js 写法。
BASE_DIR = str(PROJECT_ROOT)
OUTPUT_DIR = str(PROJECT_ROOT / "data" / "content")

# 默认仅构建当前主要模块；如果需要构建其他模块，可以通过命令行覆盖。
TARGET_MODULES = [
    "07_inequality",
]

META_FILENAME = "meta.json"
PRIMARY_STATEMENT_FILENAME = "01_statement.tex"


# =============================================================================
# 日志与错误类型
# =============================================================================

LOGGER = logging.getLogger("build_content_js")


class BuildError(RuntimeError):
    """表示脚本在构建阶段遇到的可解释业务错误。"""


# =============================================================================
# 数据结构
# =============================================================================


@dataclass(frozen=True)
class ContentFieldSpec:
    """
    描述一个“源文件 -> 输出字段”的映射关系。

    当前脚本只启用 statement 一个字段，但主流程已经按字段配置驱动，
    以后如果要扩展 proof / summary 等字段，只需要在这里追加定义即可。
    """

    output_name: str
    source_filename: str
    transform: Callable[[str], str]
    required: bool = True


@dataclass(frozen=True)
class BuildConfig:
    """集中保存命令行解析后的运行配置。"""

    project_root: Path
    output_dir: Path
    target_modules: Tuple[str, ...]
    target_items: Tuple[str, ...]
    dry_run: bool
    debug: bool
    strict: bool


@dataclass
class ModuleStats:
    """用于输出每个模块的构建统计，方便调试和排错。"""

    module_name: str
    scanned_items: int = 0
    built_items: int = 0
    filtered_items: int = 0
    skipped_items: int = 0


# =============================================================================
# 控制台 / 参数 / 日志
# =============================================================================


def configure_console_encoding() -> None:
    """
    在 Windows 终端中尽量强制 stdout / stderr 使用 UTF-8，减少中文乱码。

    这里使用“尽力而为”的策略：
    - 支持 reconfigure 时直接设置
    - 不支持时静默跳过，不影响脚本主逻辑
    """

    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None or not hasattr(stream, "reconfigure"):
            continue
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            # 终端编码设置失败时不阻塞业务逻辑。
            pass


def configure_logging(debug: bool) -> None:
    """
    初始化日志系统。

    debug=False:
        输出简洁的构建进度日志

    debug=True:
        输出更详细的目录、字段、清洗结果预览，便于单步排查问题
    """

    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""

    parser = argparse.ArgumentParser(
        description="Build JS content files from cleaned statement tex files."
    )
    parser.add_argument(
        "--base-dir",
        default=BASE_DIR,
        help="项目根目录。默认使用脚本所在仓库根目录。",
    )
    parser.add_argument(
        "--output-dir",
        default=OUTPUT_DIR,
        help="JS 输出目录。默认写入 data/content。",
    )
    parser.add_argument(
        "--module",
        dest="modules",
        action="append",
        help=("只处理指定模块目录，可重复传入。" "例如：--module 07_inequality"),
    )
    parser.add_argument(
        "--item",
        dest="items",
        action="append",
        help=(
            "只处理指定结论目录名或结论 ID，可重复传入。"
            "例如：--item I01 或 --item I001_Compound_Inequality_Transformation"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="执行完整扫描与清洗，但不写入最终 JS 文件。",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="输出更详细的调试日志。",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="遇到缺失文件、无效 JSON、重复 ID 等问题时立即报错退出。",
    )
    return parser.parse_args()


def build_config_from_args(args: argparse.Namespace) -> BuildConfig:
    """
    将 argparse 结果转成结构化配置对象。

    这样做的好处是：
    - 主流程不需要直接依赖 argparse 命名
    - 后续如果要增加配置来源（例如配置文件），改动范围更小
    """

    project_root = Path(args.base_dir).resolve()
    output_dir = Path(args.output_dir).resolve()

    # 优先使用命令行参数；如果用户没有传入，则退回文件内默认配置。
    target_modules = tuple(args.modules or TARGET_MODULES)
    target_items = tuple(args.items or ())

    return BuildConfig(
        project_root=project_root,
        output_dir=output_dir,
        target_modules=target_modules,
        target_items=target_items,
        dry_run=bool(args.dry_run),
        debug=bool(args.debug),
        strict=bool(args.strict),
    )


def apply_runtime_paths(config: BuildConfig) -> None:
    """
    将运行时路径同步到全局变量。

    这样既能保留 save_js 的原有实现，又能支持命令行覆盖路径。
    """

    global BASE_DIR, OUTPUT_DIR
    BASE_DIR = str(config.project_root)
    OUTPUT_DIR = str(config.output_dir)


# =============================================================================
# 文本读取与基础工具
# =============================================================================


def preview_text(text: str, limit: int = 80) -> str:
    """生成调试日志用的文本预览。"""

    compact = text.replace("\n", "\\n")
    return compact[:limit] + ("..." if len(compact) > limit else "")


def read_text_file(path: Path, *, strict: bool) -> str:
    """
    读取 UTF-8 文本文件。

    strict=True:
        读取失败时抛出异常，直接中断构建

    strict=False:
        读取失败时返回空字符串，并记录 warning 日志
    """

    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        if strict:
            raise BuildError(f"Failed to read text file: {path}") from exc
        LOGGER.warning("Failed to read text file: %s", path)
        return ""


def read_json_file(path: Path, *, strict: bool) -> Dict:
    """
    读取 JSON 文件并返回字典。

    与 read_text_file 一样，strict 控制错误处理策略。
    """

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as exc:
        if strict:
            raise BuildError(f"Failed to read JSON file: {path}") from exc
        LOGGER.warning("Failed to read JSON file: %s", path)
        return {}

    if not isinstance(data, dict):
        if strict:
            raise BuildError(f"JSON root must be an object: {path}")
        LOGGER.warning("JSON root is not an object: %s", path)
        return {}

    return data


# =============================================================================
# clean_tex 相关：按步骤拆分，方便单独调试与维护
# =============================================================================


# 说明：
# 这里不追求“完整 LaTeX 解析器”，而是追求“足够稳定的 statement 文本清洗”。
# 核心策略是：
# 1. 优先保留数学语义
# 2. 尽量移除排版噪音
# 3. 输出适合搜索与调试的纯文本

_NESTED_BRACE_CONTENT = r"(?:[^{}]|\{[^{}]*\})*"

_FRACTION_PATTERN = re.compile(
    rf"\\frac\{{({_NESTED_BRACE_CONTENT})\}}\{{({_NESTED_BRACE_CONTENT})\}}"
)
_SQRT_PATTERN = re.compile(rf"\\sqrt\{{({_NESTED_BRACE_CONTENT})\}}")
_WRAPPED_COMMAND_PATTERN = re.compile(
    rf"\\(?!frac\b)[a-zA-Z]+\{{({_NESTED_BRACE_CONTENT})\}}"
)
_TWO_ARGUMENT_COMMAND_PATTERN = re.compile(
    rf"\\(?!frac\b)[a-zA-Z]+\{{({_NESTED_BRACE_CONTENT})\}}\{{({_NESTED_BRACE_CONTENT})\}}"
)

_SYMBOL_REPLACEMENTS: Sequence[Tuple[str, str]] = (
    (r"\\iff", " <=> "),
    (r"\\implies", " => "),
    (r"\\Rightarrow", " => "),
    (r"\\geqslant", " >= "),
    (r"\\geq", " >= "),
    (r"\\leqslant", " <= "),
    (r"\\leq", " <= "),
    (r"\\neq", " != "),
    (r"\\to", " -> "),
    (r"\\cdot", " * "),
    (r"\\times", " * "),
    (r"\\infty", " infinity "),
    (r"\\in", " in "),
)


def _repeat_substitution(
    pattern: re.Pattern[str],
    replacer: Callable[[re.Match[str]], str],
    text: str,
) -> str:
    """
    重复执行替换，直到文本不再变化。

    这个辅助函数主要用于处理：
    - 可嵌套的 `\\frac{...}{...}`
    - 可嵌套的 `\\textbf{...}` / `\\mathbb{...}` 等包裹命令

    好处是逻辑稳定、调用点清晰，后续调试时也容易定位是哪一步出了问题。
    """

    previous = None
    current = text

    while previous != current:
        previous = current
        current = pattern.sub(replacer, current)

    return current


def strip_latex_comments(text: str) -> str:
    """
    移除 LaTeX 行内注释。

    使用 `(?<!\\)%` 的原因是：
    - `%` 在 LaTeX 中表示注释
    - 但 `\\%` 是“百分号字符本身”，不应被误删
    """

    return re.sub(r"(?<!\\)%.*$", "", text, flags=re.MULTILINE)


def strip_environment_markers(text: str) -> str:
    """
    移除 `\\begin{...}` / `\\end{...}` 这类纯容器命令。

    这些命令主要用于排版结构，对 statement 搜索文本没有直接价值。
    """

    return re.sub(r"\\(begin|end)\{[^{}]+\}", "", text)


def remove_standalone_option_lines(text: str) -> str:
    """
    移除环境命令留下来的独立可选参数行。

    典型场景：
    - `\\begin{description}[style=nextline, ...]`

    在去掉 `\\begin{description}` 后，会残留一整行：
    - `[style=nextline, ...]`

    这类信息只影响排版，不影响 statement 语义，直接删除即可。
    """

    return re.sub(r"^\s*\[[^\]]+\]\s*$", "", text, flags=re.MULTILINE)


def convert_list_items(text: str) -> str:
    """
    将 `\\item` 转成普通文本列表项。

    这里用换行加 `- `，是因为：
    - 输出更易读
    - 纯 ASCII，适合后续搜索与排查
    """

    return re.sub(r"\\item", "\n- ", text)


def unwrap_item_label_brackets(text: str) -> str:
    """
    将列表项标签中的外层方括号去掉。

    例如：
    - `[条件 1]` -> `条件 1`

    这样输出更接近普通笔记文本，而不是半清洗状态的 LaTeX 列表语法。
    """

    return re.sub(r"(^\s*-\s*)\[([^\]]+)\]", r"\1\2", text, flags=re.MULTILINE)


def replace_fractions(text: str) -> str:
    """
    将 `\\frac{a}{b}` 替换为 `(a) / (b)`。

    分式是最容易在“先删命令后清洗”流程里被破坏的结构，因此单独提前处理。
    """

    def replacer(match: re.Match[str]) -> str:
        numerator = match.group(1)
        denominator = match.group(2)
        return f"({numerator}) / ({denominator})"

    return _repeat_substitution(_FRACTION_PATTERN, replacer, text)


def replace_square_roots(text: str) -> str:
    """将 `\\sqrt{a}` 替换为 `sqrt(a)`。"""

    return _SQRT_PATTERN.sub(lambda match: f"sqrt({match.group(1)})", text)


def normalize_absolute_value_and_scalers(text: str) -> str:
    """
    处理 `\\left` / `\\right` 和绝对值边界符。

    这里的目标不是完整保留所有伸缩定界符，而是把最常见的阅读噪音先消掉。
    """

    text = text.replace(r"\left|", "|").replace(r"\right|", "|")
    text = text.replace(r"\left", "").replace(r"\right", "")
    return text


def unwrap_simple_commands(text: str) -> str:
    """
    将 `\\textbf{...}`、`\\mathbb{...}`、`\\mathrm{...}` 等“包裹型命令”去壳。

    例如：
    - `\\textbf{核心}` -> `核心`
    - `\\mathbb{R}` -> `R`

    注意：
    - 这里显式排除了 `\\frac`，因为分式必须由专门逻辑处理
    """

    return _repeat_substitution(
        _WRAPPED_COMMAND_PATTERN,
        lambda match: match.group(1),
        text,
    )


def unwrap_two_argument_commands(text: str) -> str:
    """
    处理 `\\textcolor{red}{正文}` 这类双参数命令。

    对当前构建目标来说，第一个参数通常是样式或辅助信息，
    第二个参数才是用户真正需要搜索/阅读的正文，因此保留第二个参数。
    """

    return _repeat_substitution(
        _TWO_ARGUMENT_COMMAND_PATTERN,
        lambda match: match.group(2),
        text,
    )


def replace_symbol_commands(text: str) -> str:
    """
    替换常见无参数数学命令。

    这里使用 ASCII 风格替换，是为了让输出更适合：
    - 纯文本搜索
    - 终端调试
    - JS 文件对比
    """

    for pattern, replacement in _SYMBOL_REPLACEMENTS:
        text = re.sub(pattern, replacement, text)
    return text


def remove_math_mode_markers(text: str) -> str:
    """
    移除数学环境边界符。

    包括：
    - `$...$`
    - `\\[ ... \\]`
    - `\\( ... \\)`
    """

    return (
        text.replace("$", "")
        .replace(r"\[", "\n")
        .replace(r"\]", "\n")
        .replace(r"\(", "")
        .replace(r"\)", "")
    )


def remove_remaining_commands(text: str) -> str:
    """
    清理前面步骤未覆盖到的 LaTeX 命令残留。

    例如：
    - `\\quad`
    - `\\alpha`
    - `\\sum`

    这里选择保守删除，因为本脚本的目标是生成可搜索纯文本，而不是精准排版。
    """

    return re.sub(r"\\[a-zA-Z]+(?:\[[^\]]*\])?", " ", text)


def remove_curly_braces(text: str) -> str:
    """删除清洗流程最后残留的大括号。"""

    return text.replace("{", "").replace("}", "")


def normalize_whitespace(text: str) -> str:
    """
    统一空白字符格式。

    规则：
    - 每一行内部压缩连续空白
    - 去掉首尾空白
    - 删除空行
    - 保留换行，方便后续定位和人工调试
    """

    normalized_lines: List[str] = []

    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if line:
            normalized_lines.append(line)

    return "\n".join(normalized_lines)


def clean_tex(text: str) -> str:
    """
    将 statement LaTeX 文本转换为“可读 + 可搜索 + 易调试”的纯文本。

    处理顺序非常重要，原则如下：
    1. 先去注释，避免干扰后续解析
    2. 先处理结构性强的分式 / 根式
    3. 再移除包裹命令与剩余命令
    4. 最后统一空白输出

    这个函数是整个脚本最值得单独调试的部分，因此它只做流程编排，
    具体细节尽量拆给独立步骤函数。
    """

    if not text:
        return ""

    cleaned = text
    cleaned = strip_latex_comments(cleaned)
    cleaned = strip_environment_markers(cleaned)
    cleaned = remove_standalone_option_lines(cleaned)
    cleaned = convert_list_items(cleaned)
    cleaned = unwrap_item_label_brackets(cleaned)
    cleaned = replace_fractions(cleaned)
    cleaned = replace_square_roots(cleaned)
    cleaned = normalize_absolute_value_and_scalers(cleaned)
    cleaned = unwrap_two_argument_commands(cleaned)
    cleaned = unwrap_simple_commands(cleaned)
    cleaned = replace_symbol_commands(cleaned)
    cleaned = remove_math_mode_markers(cleaned)
    cleaned = remove_remaining_commands(cleaned)
    cleaned = remove_curly_braces(cleaned)
    cleaned = normalize_whitespace(cleaned)
    return cleaned


# 当前仅收集 clean_tex 处理后的 statement。
CONTENT_FIELD_SPECS: Sequence[ContentFieldSpec] = (
    ContentFieldSpec(
        output_name="statement",
        source_filename=PRIMARY_STATEMENT_FILENAME,
        transform=clean_tex,
        required=True,
    ),
)


# =============================================================================
# 目录发现与过滤
# =============================================================================


def module_contains_content(module_dir: Path) -> bool:
    """
    判断一个一级目录是否看起来像内容模块。

    规则很保守：
    - 只要目录下存在子目录
    - 且某个子目录里带有 `meta.json` 或 `01_statement.tex`
    就认为它是内容模块
    """

    for child in module_dir.iterdir():
        if not child.is_dir():
            continue
        if (child / META_FILENAME).exists() or (
            child / PRIMARY_STATEMENT_FILENAME
        ).exists():
            return True
    return False


def discover_all_module_directories(project_root: Path) -> List[Path]:
    """
    自动发现所有可处理模块。

    当 TARGET_MODULES 为空时，这个函数可以作为兜底逻辑使用。
    """

    module_dirs: List[Path] = []

    for path in sorted(project_root.iterdir()):
        if not path.is_dir():
            continue
        if module_contains_content(path):
            module_dirs.append(path)

    return module_dirs


def resolve_target_module_directories(config: BuildConfig) -> List[Path]:
    """
    根据配置解析最终要处理的模块目录列表。

    处理策略：
    - 如果用户明确给了模块列表，就按列表解析
    - 如果模块列表为空，就自动发现
    """

    if config.target_modules:
        module_dirs: List[Path] = []
        missing_modules: List[str] = []

        for module_name in config.target_modules:
            module_dir = config.project_root / module_name
            if module_dir.is_dir():
                module_dirs.append(module_dir)
            else:
                missing_modules.append(module_name)

        if missing_modules:
            message = "Module directory not found: " + ", ".join(missing_modules)
            if config.strict:
                raise BuildError(message)
            LOGGER.warning(message)

        return module_dirs

    return discover_all_module_directories(config.project_root)


def iter_item_directories(module_dir: Path) -> Sequence[Path]:
    """返回模块下的一级结论目录，按名称排序，便于稳定输出与 diff。"""

    return sorted(path for path in module_dir.iterdir() if path.is_dir())


def resolve_item_identity(meta: Dict, item_dir: Path) -> Tuple[str, str]:
    """
    统一解析结论 ID 和标题。

    兜底规则：
    - `id` 缺失时使用目录名
    - `title` 缺失时使用目录名
    """

    item_id = str(meta.get("id") or item_dir.name)
    title = str(meta.get("title") or item_dir.name)
    return item_id, title


def matches_item_filter(
    item_dir: Path, item_id: str, target_items: Sequence[str]
) -> bool:
    """
    判断当前结论是否命中 `--item` 过滤条件。

    支持两种匹配方式：
    - 目录名匹配
    - meta 中的结论 ID 匹配
    """

    if not target_items:
        return True

    targets = set(target_items)
    return item_dir.name in targets or item_id in targets


# =============================================================================
# 核心构建逻辑
# =============================================================================


def build_item_record(
    item_dir: Path,
    item_id: str,
    title: str,
    config: BuildConfig,
) -> Dict[str, str]:
    """
    构建单个结论的输出记录。

    当前只收集清洗后的 statement，但实现已经是“字段配置驱动”的：
    - 以后新增字段时，这个函数无需重写
    - 只要扩展 CONTENT_FIELD_SPECS 即可
    """

    record: Dict[str, str] = {
        "id": item_id,
        "title": title,
    }

    for field_spec in CONTENT_FIELD_SPECS:
        source_path = item_dir / field_spec.source_filename
        raw_text = read_text_file(source_path, strict=config.strict)
        cleaned_text = field_spec.transform(raw_text)

        if field_spec.required and not cleaned_text:
            raise BuildError(
                f"Required field '{field_spec.output_name}' is empty after clean_tex: {source_path}"
            )

        record[field_spec.output_name] = cleaned_text

        LOGGER.debug(
            "Field built | item=%s | field=%s | preview=%s",
            item_id,
            field_spec.output_name,
            preview_text(cleaned_text),
        )

    return record


def process_module(
    module_dir: Path, config: BuildConfig
) -> Tuple[str, Dict[str, Dict[str, str]], ModuleStats]:
    """
    处理单个模块目录。

    返回：
    - module_name: 模块目录名
    - result: `{item_id: item_record}` 结构
    - stats: 构建统计信息
    """

    module_name = module_dir.name
    stats = ModuleStats(module_name=module_name)
    result: Dict[str, Dict[str, str]] = {}

    LOGGER.info("Processing module: %s", module_name)

    for item_dir in iter_item_directories(module_dir):
        stats.scanned_items += 1

        try:
            meta = read_json_file(item_dir / META_FILENAME, strict=config.strict)
            item_id, title = resolve_item_identity(meta, item_dir)

            if not matches_item_filter(item_dir, item_id, config.target_items):
                stats.filtered_items += 1
                LOGGER.debug(
                    "Filtered item | module=%s | item_dir=%s | item_id=%s",
                    module_name,
                    item_dir.name,
                    item_id,
                )
                continue

            if item_id in result:
                raise BuildError(
                    f"Duplicate item id '{item_id}' found in module '{module_name}'."
                )

            record = build_item_record(item_dir, item_id, title, config)
            result[item_id] = record
            stats.built_items += 1

        except Exception as exc:
            stats.skipped_items += 1

            if config.strict:
                raise

            LOGGER.warning("Skip item: %s (%s)", item_dir, exc)

    LOGGER.info(
        "Module summary | module=%s | scanned=%d | built=%d | filtered=%d | skipped=%d",
        module_name,
        stats.scanned_items,
        stats.built_items,
        stats.filtered_items,
        stats.skipped_items,
    )

    return module_name, result, stats


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

    print(f"已生成 {output_path}")


def run_build(config: BuildConfig) -> None:
    """
    执行完整构建流程。

    这里单独抽出来，便于以后：
    - 编写测试
    - 在 REPL / 调试器中直接调用
    - 后续扩展为其他入口
    """

    module_dirs = resolve_target_module_directories(config)

    if not module_dirs:
        message = "No module directories matched the current configuration."
        if config.strict:
            raise BuildError(message)
        LOGGER.warning(message)
        return

    total_modules = 0
    total_items = 0
    total_filtered = 0
    total_skipped = 0

    LOGGER.info("Start building JS content from cleaned statements")
    LOGGER.info("Project root: %s", config.project_root)
    LOGGER.info("Output dir: %s", config.output_dir)

    if config.target_modules:
        LOGGER.info("Target modules: %s", ", ".join(config.target_modules))
    else:
        LOGGER.info("Target modules: auto discover")

    if config.target_items:
        LOGGER.info("Target items: %s", ", ".join(config.target_items))

    for module_dir in module_dirs:
        module_name, data, stats = process_module(module_dir, config)
        total_modules += 1
        total_items += stats.built_items
        total_filtered += stats.filtered_items
        total_skipped += stats.skipped_items

        if config.dry_run:
            LOGGER.info(
                "[dry-run] Would generate module '%s' with %d item(s)",
                module_name,
                len(data),
            )
        else:
            save_js(module_name, data)

    LOGGER.info(
        "Build finished | modules=%d | items=%d | filtered=%d | skipped=%d",
        total_modules,
        total_items,
        total_filtered,
        total_skipped,
    )


def main() -> int:
    """脚本入口。返回进程退出码，便于终端直接判断成败。"""

    configure_console_encoding()
    args = parse_args()
    configure_logging(args.debug)

    config = build_config_from_args(args)
    apply_runtime_paths(config)

    try:
        run_build(config)
        return 0
    except BuildError as exc:
        LOGGER.error("%s", exc)
        return 1
    except Exception:
        LOGGER.exception("Unexpected build failure")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
