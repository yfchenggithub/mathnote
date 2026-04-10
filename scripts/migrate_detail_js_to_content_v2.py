from __future__ import annotations

"""
===============================================================================
migrate_detail_js_to_content_v2.py
===============================================================================

用途
----
将 `module.exports = { [id]: DetailRecord }` 形式的详情数据迁移为
`canonical_content_v2.json`（顶层仍为 id -> record 映射），并输出
`conversion_report.json`。

设计说明
--------
1. 最小风险迁移：优先保留原始信息，避免激进重写。
2. 工程可维护：argparse + pathlib + logging + 清晰分层。
3. 容错：单条失败不影响全量，失败写入报告。
4. 可扩展：为未来 conditions/conclusions 分词与 proof_steps 细化预留 TODO。

输入
----
- detail js 文件（例如 data/content/07_inequality.js）

输出
----
- canonical_content_v2.json
- conversion_report.json
===============================================================================
"""

import argparse
import importlib.util
import json
import logging
import re
import subprocess
import sys
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

LOGGER = logging.getLogger("migrate_detail_js_to_content_v2")
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_SCHEMA_PATH = SCRIPT_DIR / "conclusion_record_v2.schema.json"
DEFAULT_MODEL_PATH = SCRIPT_DIR / "content_v2.py"

SUPPORTED_BLOCK_TYPES = {
    "rich_text",
    "math_block",
    "theorem_group",
    "proof_steps",
    "example_group",
    "summary",
    "warning_group",
}

LEGACY_TOP_LEVEL_FIELDS = {
    "id",
    "title",
    "module",
    "alias",
    "difficulty",
    "category",
    "tags",
    "core_summary",
    "core_formula",
    "related_formulas",
    "variables",
    "conditions",
    "conclusions",
    "usage",
    "interactive",
    "assets",
    "shareConfig",
    "relations",
    "isPro",
    "remarks",
    "knowledgeNode",
    "altNodes",
    "statement",
    "explanation",
    "proof",
    "examples",
    "traps",
    "summary",
    "display_version",
    "sections",
}


@dataclass(frozen=True)
class BuildConfig:
    """运行配置。"""

    input_path: Path
    output_path: Path
    report_path: Path
    schema_path: Path
    model_path: Path
    log_level: str
    skip_validation: bool
    strict_validation: bool
    disable_node_fallback: bool


@dataclass
class RecordStatus:
    """单条记录状态。"""

    source_key: str
    record_id: str | None
    status: str
    warnings: list[str] = field(default_factory=list)
    error: str | None = None


@dataclass
class ConversionReport:
    """迁移报告。"""

    total_records: int = 0
    success_count: int = 0
    failed_count: int = 0
    warnings: list[str] = field(default_factory=list)
    per_record_status: dict[str, dict[str, Any]] = field(default_factory=dict)

    def add(self, status: RecordStatus) -> None:
        if status.status == "success":
            self.success_count += 1
        else:
            self.failed_count += 1
        self.per_record_status[status.source_key] = asdict(status)


@dataclass
class ValidationBundle:
    """校验器封装。"""

    mode: str
    startup_warnings: list[str]
    validate: Callable[[dict[str, Any]], list[str]]


class ParseError(RuntimeError):
    """解析错误。"""


def configure_console_encoding() -> None:
    """尽力将 Windows 控制台设置为 UTF-8。"""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None or not hasattr(stream, "reconfigure"):
            continue
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


def configure_logging(level_name: str) -> None:
    """初始化日志。"""
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="迁移 detail js 到 canonical_content_v2.json，并输出 conversion_report.json",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "示例:\n"
            "  python scripts/migrate_detail_js_to_content_v2.py --input data/content/07_inequality.js\n"
            "  python scripts/migrate_detail_js_to_content_v2.py --input data/content/07_inequality.js --strict-validation --log-level DEBUG"
        ),
    )
    parser.add_argument("--input", required=True, help="输入 detail js 文件")
    parser.add_argument("--output", default=None, help="输出 canonical_content_v2.json 路径")
    parser.add_argument("--report", default=None, help="输出 conversion_report.json 路径")
    parser.add_argument("--schema-path", default=str(DEFAULT_SCHEMA_PATH), help="JSON Schema 路径")
    parser.add_argument("--model-path", default=str(DEFAULT_MODEL_PATH), help="content_v2.py 路径")
    parser.add_argument("--skip-validation", action="store_true", help="跳过模型/Schema 强校验，仅做基础结构检查")
    parser.add_argument("--strict-validation", action="store_true", help="校验失败时将该条记为 failed")
    parser.add_argument("--disable-node-fallback", action="store_true", help="禁用 Node require 回退解析")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="日志级别")
    return parser.parse_args()


def build_config_from_args(args: argparse.Namespace) -> BuildConfig:
    """构建强类型配置。"""
    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve() if args.output else input_path.parent / "canonical_content_v2.json"
    report_path = Path(args.report).resolve() if args.report else input_path.parent / "conversion_report.json"

    return BuildConfig(
        input_path=input_path,
        output_path=output_path,
        report_path=report_path,
        schema_path=Path(args.schema_path).resolve(),
        model_path=Path(args.model_path).resolve(),
        log_level=args.log_level,
        skip_validation=bool(args.skip_validation),
        strict_validation=bool(args.strict_validation),
        disable_node_fallback=bool(args.disable_node_fallback),
    )


def write_json(path: Path, data: Any) -> None:
    """写 JSON 文件。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_non_empty_string(value: Any) -> str | None:
    """转非空字符串，空值返回 None。"""
    if value is None:
        return None
    text = value.strip() if isinstance(value, str) else str(value).strip()
    return text or None


def normalize_nullable_string(value: Any) -> str | None:
    """空串转 None。"""
    return normalize_non_empty_string(value)


def normalize_string_list(value: Any) -> list[str]:
    """标准化为字符串数组。"""
    if value is None:
        return []
    items = value if isinstance(value, list) else [value]
    result: list[str] = []
    for item in items:
        text = normalize_non_empty_string(item)
        if text:
            result.append(text)
    return result


def normalize_aliases(value: Any) -> list[str]:
    """alias 标准化。"""
    if isinstance(value, str):
        parts = re.split(r"[,，;\n]+", value.strip())
        return [p.strip() for p in parts if p and p.strip()]
    return normalize_string_list(value)


def normalize_alt_nodes(value: Any) -> list[str]:
    """altNodes 标准化（支持字符串按中英文逗号拆分）。"""
    if isinstance(value, str):
        parts = re.split(r"[,，]", value)
        cleaned = [p.strip() for p in parts if p and p.strip()]
    elif isinstance(value, list):
        cleaned = [str(v).strip() for v in value if str(v).strip()]
    else:
        one = normalize_non_empty_string(value)
        cleaned = [one] if one else []

    deduped: list[str] = []
    seen: set[str] = set()
    for item in cleaned:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def normalize_bool(value: Any, default: bool = False) -> bool:
    """宽松布尔转换。"""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"1", "true", "yes", "y", "on"}:
            return True
        if text in {"0", "false", "no", "n", "off", ""}:
            return False
    return bool(value)


def normalize_difficulty(value: Any, warnings: list[str]) -> int | None:
    """难度标准化到 0~10。"""
    if value in (None, ""):
        return None
    try:
        number = int(float(value))
    except Exception:
        warnings.append(f"difficulty 无法解析: {value!r}，置为 null")
        return None
    if number < 0:
        warnings.append(f"difficulty={number} < 0，钳制为 0")
        return 0
    if number > 10:
        warnings.append(f"difficulty={number} > 10，钳制为 10")
        return 10
    return number


def normalize_non_negative_number(value: Any, field_name: str, warnings: list[str]) -> int | float | None:
    """非负数标准化。"""
    if value in (None, ""):
        return None
    try:
        number = float(value)
    except Exception:
        warnings.append(f"{field_name} 无法解析: {value!r}，置为 null")
        return None
    if number < 0:
        warnings.append(f"{field_name}={number} < 0，置为 null")
        return None
    return int(number) if number.is_integer() else number


def preview_text(value: Any, limit: int = 160) -> str:
    """短文本预览（用于 warning）。"""
    try:
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    except Exception:
        text = repr(value)
    compact = re.sub(r"\s+", " ", text).strip()
    return compact if len(compact) <= limit else compact[: limit - 3] + "..."


def slugify_record(record_id: str, title: str | None) -> str:
    """按 id+title 生成稳定 slug。"""
    raw = f"{record_id}-{title or ''}".strip().lower()
    normalized = unicodedata.normalize("NFKD", raw)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    if slug:
        return slug
    fallback = re.sub(r"[^a-z0-9]+", "-", record_id.lower()).strip("-")
    return fallback or "record"


def extract_balanced_brace_object(text: str, start: int) -> str:
    """从 start 位置提取平衡花括号对象。"""
    if start < 0 or start >= len(text) or text[start] != "{":
        raise ParseError("对象起始位置非法")

    depth = 0
    i = start
    in_string: str | None = None
    escaped = False
    in_single_comment = False
    in_multi_comment = False

    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""

        if in_single_comment:
            if ch == "\n":
                in_single_comment = False
            i += 1
            continue

        if in_multi_comment:
            if ch == "*" and nxt == "/":
                in_multi_comment = False
                i += 2
                continue
            i += 1
            continue

        if in_string is not None:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == in_string:
                in_string = None
            i += 1
            continue

        if ch in {"'", '"', "`"}:
            in_string = ch
            i += 1
            continue

        if ch == "/" and nxt == "/":
            in_single_comment = True
            i += 2
            continue

        if ch == "/" and nxt == "*":
            in_multi_comment = True
            i += 2
            continue

        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]

        i += 1

    raise ParseError("未找到匹配的右花括号")


def parse_js_module_exports_via_python(js_text: str) -> dict[str, Any]:
    """Python ?? module.exports?"""
    matches = list(re.finditer(r"module\.exports\s*=", js_text))
    if not matches:
        data = json.loads(js_text)
        if not isinstance(data, dict):
            raise ParseError("????????")
        return data

    parse_errors: list[str] = []
    # ???????????????????????????????
    for match in reversed(matches):
        start = js_text.find("{", match.end())
        if start == -1:
            parse_errors.append("module.exports ???? '{'")
            continue
        try:
            object_literal = extract_balanced_brace_object(js_text, start)
            data = json.loads(object_literal)
            if not isinstance(data, dict):
                parse_errors.append("module.exports ???????")
                continue
            return data
        except Exception as exc:
            parse_errors.append(str(exc))

    message = parse_errors[0] if parse_errors else "unknown error"
    raise ParseError(f"Python ?? module.exports ??: {message}")

def parse_js_module_exports_via_node(input_path: Path) -> dict[str, Any]:
    """Node require 回退解析。"""
    node_script = (
        "const path=require('path');"
        "const p=process.argv[1];"
        "const d=require(path.resolve(p));"
        "process.stdout.write(JSON.stringify(d));"
    )
    result = subprocess.run(["node", "-e", node_script, str(input_path)], capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        raise ParseError(f"Node 回退解析失败: {result.stderr.strip() or 'unknown'}")
    data = json.loads(result.stdout)
    if not isinstance(data, dict):
        raise ParseError("Node 解析结果根对象不是对象")
    return data


def load_source_map(input_path: Path, disable_node_fallback: bool) -> tuple[dict[str, Any], list[str]]:
    """加载输入并返回源映射。"""
    if not input_path.exists():
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    warnings: list[str] = []
    js_text = input_path.read_text(encoding="utf-8")

    try:
        return parse_js_module_exports_via_python(js_text), warnings
    except Exception as exc:
        warnings.append(f"Python 解析失败: {exc}")
        if disable_node_fallback:
            raise

    source_map = parse_js_module_exports_via_node(input_path)
    warnings.append("已使用 Node 回退解析")
    return source_map, warnings

def text_token(text: str) -> dict[str, Any]:
    """构造 text token。"""
    return {"type": "text", "text": normalize_non_empty_string(text) or "（空文本）"}


def make_block_id(section_key: str, index: int) -> str:
    """生成稳定 block id。"""
    key = unicodedata.normalize("NFKD", section_key or "section")
    key = key.encode("ascii", "ignore").decode("ascii").lower()
    key = re.sub(r"[^a-z0-9]+", "-", key).strip("-") or "section"
    return f"{key}-b{index}"


def convert_segments_to_tokens(segments: Any, warnings: list[str]) -> list[dict[str, Any]]:
    """legacy segments -> v2 tokens。"""
    if not isinstance(segments, list):
        return [text_token(preview_text(segments))]

    tokens: list[dict[str, Any]] = []
    for seg in segments:
        if isinstance(seg, str):
            if seg.strip():
                tokens.append(text_token(seg))
            continue

        if not isinstance(seg, dict):
            warnings.append(f"segments 含非对象元素，已降级: {preview_text(seg)}")
            tokens.append(text_token(preview_text(seg)))
            continue

        stype = str(seg.get("type", "")).strip().lower()
        if stype == "text":
            text = normalize_non_empty_string(seg.get("text"))
            if text:
                tokens.append(text_token(text))
            continue

        if stype in {"math", "math_inline"}:
            latex = normalize_non_empty_string(seg.get("latex"))
            if latex:
                tokens.append({"type": "math_inline", "latex": latex})
            else:
                warnings.append("segment.math 缺失 latex，已跳过")
            continue

        if stype == "math_display":
            latex = normalize_non_empty_string(seg.get("latex"))
            if latex:
                tokens.append({"type": "math_display", "latex": latex})
            else:
                warnings.append("segment.math_display 缺失 latex，已跳过")
            continue

        if stype == "line_break":
            tokens.append({"type": "line_break"})
            continue

        warnings.append(f"未知 segment.type={stype!r}，已降级")
        tokens.append(text_token(preview_text(seg)))

    return tokens or [text_token("（空段落）")]


def build_paragraph_block(block_id: str, tokens: list[dict[str, Any]]) -> dict[str, Any]:
    """构造 paragraph block。"""
    return {"id": block_id, "type": "paragraph", "tokens": tokens or [text_token("（空段落）")]}


def build_math_block(block_id: str, latex: str) -> dict[str, Any]:
    """构造 math_block。"""
    return {
        "id": block_id,
        "type": "math_block",
        "latex": normalize_non_empty_string(latex) or r"\text{N/A}",
        "align": "center",
    }


def map_text_layout_items_to_blocks(section_key: str, items: Any, warnings: list[str]) -> list[dict[str, Any]]:
    """layout=text 的 items -> blocks。"""
    if items is None:
        return []
    source_items = items if isinstance(items, list) else [items]

    blocks: list[dict[str, Any]] = []
    for idx, item in enumerate(source_items, start=1):
        block_id = make_block_id(section_key, idx)

        if isinstance(item, str):
            blocks.append(build_paragraph_block(block_id, [text_token(item)]))
            continue

        if not isinstance(item, dict):
            warnings.append(f"{section_key}: item 非对象，降级为文本")
            blocks.append(build_paragraph_block(block_id, [text_token(preview_text(item))]))
            continue

        has_segments = isinstance(item.get("segments"), list)
        text_val = normalize_non_empty_string(item.get("text"))
        latex_val = normalize_non_empty_string(item.get("latex"))

        if has_segments:
            tokens = convert_segments_to_tokens(item.get("segments"), warnings)
            blocks.append(build_paragraph_block(block_id, tokens))
            continue

        if text_val and not latex_val:
            blocks.append(build_paragraph_block(block_id, [text_token(text_val)]))
            continue

        if latex_val and not text_val:
            blocks.append(build_math_block(block_id, latex_val))
            continue

        if text_val and latex_val:
            warnings.append(f"{section_key}: 同时含 text+latex，降级为 paragraph")
            blocks.append(
                build_paragraph_block(
                    block_id,
                    [text_token(text_val), {"type": "math_inline", "latex": latex_val}],
                )
            )
            continue

        warnings.append(f"{section_key}: 未知 item 形态，降级为文本")
        blocks.append(build_paragraph_block(block_id, [text_token(preview_text(item))]))

    return blocks


def map_theorem_list_to_block(section_key: str, items: Any, warnings: list[str]) -> dict[str, Any]:
    """layout=theorem-list -> theorem_group block。"""
    source_items = items if isinstance(items, list) else ([items] if items is not None else [])
    theorem_items: list[dict[str, Any]] = []

    for idx, item in enumerate(source_items, start=1):
        if isinstance(item, str):
            theorem_items.append({"title": f"结论{idx}", "desc_tokens": None, "formula_latex": item})
            continue

        if not isinstance(item, dict):
            warnings.append(f"{section_key}: theorem item 非对象，已降级")
            theorem_items.append(
                {
                    "title": f"结论{idx}",
                    "desc_tokens": [text_token(preview_text(item))],
                    "formula_latex": r"\text{N/A}",
                }
            )
            continue

        title = normalize_non_empty_string(item.get("title")) or f"结论{idx}"
        desc = normalize_non_empty_string(item.get("desc"))
        formula = normalize_non_empty_string(item.get("latex")) or normalize_non_empty_string(item.get("formula_latex"))
        if not formula:
            formula = normalize_non_empty_string(item.get("text")) or r"\text{N/A}"
            warnings.append(f"{section_key}: theorem item 缺失 latex，已降级")

        theorem_items.append(
            {
                "title": title,
                "desc_tokens": [text_token(desc)] if desc else None,
                "formula_latex": formula,
            }
        )

    if not theorem_items:
        theorem_items.append(
            {
                "title": "结论1",
                "desc_tokens": [text_token("原 theorem-list 为空，迁移占位")],
                "formula_latex": r"\text{N/A}",
            }
        )

    return {"id": make_block_id(section_key, 1), "type": "theorem_group", "items": theorem_items}


def map_section_block_type(layout: str, key: str, title: str) -> str:
    """section.block_type 映射规则。"""
    ln = (layout or "").strip().lower()
    kn = (key or "").strip().lower()

    if "summary" in kn or "总结" in title:
        return "summary"
    if "trap" in kn or "warning" in kn or "易错" in title or "陷阱" in title or "注意" in title:
        return "warning_group"
    if ln == "theorem-list":
        return "theorem_group"
    if ln == "text":
        return "rich_text"
    if "proof" in kn or "证明" in title:
        # TODO: 后续可升级为 proof_steps 解析
        return "rich_text"
    return "rich_text"


def map_sections(sections: Any, warnings: list[str]) -> list[dict[str, Any]]:
    """sections 迁移。"""
    if sections is None:
        return []
    source_sections = sections if isinstance(sections, list) else [sections]
    if not isinstance(sections, list):
        warnings.append("sections 非数组，已自动包装")

    mapped: list[dict[str, Any]] = []
    for idx, sec in enumerate(source_sections, start=1):
        if not isinstance(sec, dict):
            warnings.append(f"section#{idx} 非对象，已降级")
            sec = {
                "key": f"section_{idx}",
                "title": f"Section {idx}",
                "layout": "text",
                "items": [sec],
            }

        key = normalize_non_empty_string(sec.get("key")) or f"section_{idx}"
        title = normalize_non_empty_string(sec.get("title")) or key
        layout = normalize_non_empty_string(sec.get("layout")) or "text"
        items = sec.get("items")

        block_type = map_section_block_type(layout, key, title)
        if block_type not in SUPPORTED_BLOCK_TYPES:
            warnings.append(f"{key}: block_type={block_type!r} 非法，回退 rich_text")
            block_type = "rich_text"

        if layout.strip().lower() == "theorem-list":
            blocks = [map_theorem_list_to_block(key, items, warnings)]
        else:
            blocks = map_text_layout_items_to_blocks(key, items, warnings)

        if not blocks:
            warnings.append(f"{key}: blocks 为空，写入占位 paragraph")
            blocks = [build_paragraph_block(make_block_id(key, 1), [text_token("原 section 为空，迁移占位")])]

        mapped.append({"key": key, "title": title, "block_type": block_type, "blocks": blocks})

    return mapped


def normalize_variable_item(item: Any, idx: int, warnings: list[str]) -> dict[str, Any] | None:
    """单个 variable 映射。"""
    if isinstance(item, dict):
        latex = (
            normalize_non_empty_string(item.get("latex"))
            or normalize_non_empty_string(item.get("name"))
            or normalize_non_empty_string(item.get("symbol"))
        )
        desc = (
            normalize_non_empty_string(item.get("description"))
            or normalize_non_empty_string(item.get("desc"))
            or normalize_non_empty_string(item.get("text"))
        )
        required = normalize_bool(item.get("required"), default=True)
    else:
        latex = normalize_non_empty_string(item)
        desc = None
        required = True

    if not latex:
        warnings.append(f"variables[{idx}] 缺失 latex/name，已跳过")
        return None

    if not desc:
        desc = "（迁移阶段未提供变量说明）"
        warnings.append(f"variables[{idx}] 缺失 description，已填充占位")

    return {
        "name": latex,
        "latex": latex,
        "description": desc,
        "required": required,
    }


def map_variables(raw_variables: Any, warnings: list[str]) -> list[dict[str, Any]]:
    """variables 映射。"""
    if raw_variables is None:
        return []
    source_items = raw_variables if isinstance(raw_variables, list) else [raw_variables]
    result: list[dict[str, Any]] = []
    for idx, item in enumerate(source_items, start=1):
        mapped = normalize_variable_item(item, idx, warnings)
        if mapped:
            result.append(mapped)
    return result


def normalize_condition_or_conclusion_source(value: Any) -> list[str]:
    """conditions/conclusions 源值标准化为字符串列表。"""
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, list):
        output: list[str] = []
        for item in value:
            text = normalize_non_empty_string(item)
            if text:
                output.append(text)
            elif isinstance(item, dict):
                output.append(preview_text(item))
        return output
    if isinstance(value, dict):
        return [preview_text(value)]
    text = normalize_non_empty_string(value)
    return [text] if text else []


def map_conditions(raw_conditions: Any) -> list[dict[str, Any]]:
    """conditions MVP 迁移：文本包装为 token 列表。"""
    texts = normalize_condition_or_conclusion_source(raw_conditions)
    return [
        {
            "id": f"cond_{idx}",
            "title": f"条件{idx}",
            "content": [text_token(text)],
            "required": True,
            "scope": None,
        }
        for idx, text in enumerate(texts, start=1)
    ]


def map_conclusions(raw_conclusions: Any) -> list[dict[str, Any]]:
    """conclusions MVP 迁移：文本包装为 token 列表。"""
    texts = normalize_condition_or_conclusion_source(raw_conclusions)
    return [
        {
            "id": f"conc_{idx}",
            "title": f"结论{idx}",
            "content": [text_token(text)],
        }
        for idx, text in enumerate(texts, start=1)
    ]


def map_plain_content(source: dict[str, Any]) -> dict[str, Any]:
    """plain 层迁移，空串转 null。"""
    return {
        "statement": normalize_nullable_string(source.get("statement")),
        "explanation": normalize_nullable_string(source.get("explanation")),
        "proof": normalize_nullable_string(source.get("proof")),
        "examples": normalize_nullable_string(source.get("examples")),
        "traps": normalize_nullable_string(source.get("traps")),
        "summary": normalize_nullable_string(source.get("summary")),
    }


def map_assets(raw_assets: Any, warnings: list[str]) -> dict[str, Any]:
    """assets 迁移，未知资源放到 assets.extra。"""
    if raw_assets is None:
        raw_assets = {}
    if not isinstance(raw_assets, dict):
        warnings.append("assets 非对象，已降级")
        raw_assets = {"legacy_assets_raw": raw_assets}

    known = {"cover", "svg", "png", "pdf", "mp4"}
    extra_assets: list[dict[str, Any]] = []

    for key, value in raw_assets.items():
        if key in known or value in (None, ""):
            continue

        if isinstance(value, str):
            extra_assets.append({"kind": key, "url": value, "meta": {}})
            continue

        if isinstance(value, list):
            for idx, item in enumerate(value, start=1):
                url = normalize_non_empty_string(item) or preview_text(item)
                extra_assets.append({"kind": f"{key}_{idx}", "url": url, "meta": {}})
            continue

        if isinstance(value, dict):
            url = normalize_non_empty_string(value.get("url")) or preview_text(value)
            meta = value.get("meta") if isinstance(value.get("meta"), dict) else {}
            extra_assets.append({"kind": key, "url": url, "meta": meta})
            continue

        extra_assets.append({"kind": key, "url": preview_text(value), "meta": {}})

    return {
        "cover": normalize_nullable_string(raw_assets.get("cover")),
        "svg": normalize_nullable_string(raw_assets.get("svg")),
        "png": normalize_nullable_string(raw_assets.get("png")),
        "pdf": normalize_nullable_string(raw_assets.get("pdf")),
        "mp4": normalize_nullable_string(raw_assets.get("mp4")),
        "extra": extra_assets,
    }


def map_share(raw_share_config: Any) -> dict[str, Any]:
    """shareConfig -> ext.share。"""
    if not isinstance(raw_share_config, dict):
        raw_share_config = {}
    return {
        "title": normalize_nullable_string(raw_share_config.get("title")),
        "desc": normalize_nullable_string(raw_share_config.get("desc") or raw_share_config.get("shareDesc")),
    }


def map_relations(raw_relations: Any) -> dict[str, Any]:
    """relations -> ext.relations。"""
    if not isinstance(raw_relations, dict):
        raw_relations = {}
    return {
        "prerequisites": normalize_string_list(raw_relations.get("prerequisites")),
        "related_ids": normalize_string_list(raw_relations.get("related_ids")),
        "similar": normalize_nullable_string(raw_relations.get("similar")),
    }


def map_exam(raw_usage: Any, warnings: list[str]) -> dict[str, Any]:
    """usage.exam_frequency/exam_score -> ext.exam。"""
    if not isinstance(raw_usage, dict):
        raw_usage = {}
    return {
        "frequency": normalize_non_negative_number(raw_usage.get("exam_frequency"), "usage.exam_frequency", warnings),
        "score": normalize_non_negative_number(raw_usage.get("exam_score"), "usage.exam_score", warnings),
    }


def collect_ext_extra(source: dict[str, Any]) -> dict[str, Any]:
    """收集暂未结构化字段，保证不丢失。"""
    ext_extra: dict[str, Any] = {}
    if "usage" in source:
        ext_extra["usage"] = source.get("usage")
    if "interactive" in source:
        ext_extra["interactive"] = source.get("interactive")
    if "related_formulas" in source:
        ext_extra["related_formulas"] = source.get("related_formulas")
    if "display_version" in source:
        ext_extra["legacy_display_version"] = source.get("display_version")

    unmapped = {k: v for k, v in source.items() if k not in LEGACY_TOP_LEVEL_FIELDS}
    if unmapped:
        ext_extra["unmapped_legacy_fields"] = unmapped

    return ext_extra


def convert_record(source_key: str, source: dict[str, Any], fallback_module: str) -> tuple[dict[str, Any], list[str]]:
    """单条记录迁移。"""
    warnings: list[str] = []

    source_id = normalize_non_empty_string(source.get("id"))
    record_id = source_id or source_key
    if source_id and source_id != source_key:
        warnings.append(f"source_key={source_key} 与 record.id={source_id} 不一致，已采用 record.id")

    title = normalize_non_empty_string(source.get("title")) or record_id
    module = normalize_non_empty_string(source.get("module")) or fallback_module

    identity = {
        "slug": slugify_record(record_id, title),
        "module": module,
        "knowledge_node": normalize_nullable_string(source.get("knowledgeNode")),
        "alt_nodes": normalize_alt_nodes(source.get("altNodes")),
    }

    meta = {
        "title": title,
        "aliases": normalize_aliases(source.get("alias")),
        "difficulty": normalize_difficulty(source.get("difficulty"), warnings),
        "category": normalize_nullable_string(source.get("category")),
        "tags": normalize_string_list(source.get("tags")),
        "summary": normalize_nullable_string(source.get("core_summary")),
        "is_pro": normalize_bool(source.get("isPro"), default=False),
        "remarks": normalize_nullable_string(source.get("remarks")),
    }

    content = {
        "render_schema_version": 2,
        "primary_formula": normalize_nullable_string(source.get("core_formula")),
        "variables": map_variables(source.get("variables"), warnings),
        "conditions": map_conditions(source.get("conditions")),
        "conclusions": map_conclusions(source.get("conclusions")),
        "sections": map_sections(source.get("sections"), warnings),
        "plain": map_plain_content(source),
    }

    ext = {
        "share": map_share(source.get("shareConfig")),
        "relations": map_relations(source.get("relations")),
        "exam": map_exam(source.get("usage"), warnings),
        "extra": collect_ext_extra(source),
    }

    record = {
        "id": record_id,
        "schema_version": 2,
        "type": "conclusion",
        "status": "published",
        "identity": identity,
        "meta": meta,
        "content": content,
        "assets": map_assets(source.get("assets"), warnings),
        "ext": ext,
    }
    return record, warnings

def validate_record_basic_shape(record: dict[str, Any]) -> list[str]:
    """基础结构校验（无模型时兜底）。"""
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["record 不是对象"]

    for key in ("id", "identity", "meta", "content"):
        if key not in record:
            errors.append(f"缺少顶层字段: {key}")

    if not isinstance(record.get("id"), str) or not str(record.get("id", "")).strip():
        errors.append("id 必须为非空字符串")

    identity = record.get("identity")
    if not isinstance(identity, dict):
        errors.append("identity 必须为对象")
    else:
        module = identity.get("module")
        if not isinstance(module, str) or not module.strip():
            errors.append("identity.module 必须为非空字符串")

    meta = record.get("meta")
    if not isinstance(meta, dict):
        errors.append("meta 必须为对象")
    else:
        title = meta.get("title")
        if not isinstance(title, str) or not title.strip():
            errors.append("meta.title 必须为非空字符串")

    content = record.get("content")
    if not isinstance(content, dict):
        errors.append("content 必须为对象")
    else:
        if content.get("render_schema_version") != 2:
            errors.append("content.render_schema_version 必须为 2")
        for name in ("variables", "conditions", "conclusions", "sections"):
            if name in content and not isinstance(content.get(name), list):
                errors.append(f"content.{name} 必须为数组")

        sections = content.get("sections", [])
        if isinstance(sections, list):
            for idx, sec in enumerate(sections, start=1):
                if not isinstance(sec, dict):
                    errors.append(f"content.sections[{idx}] 必须为对象")
                    continue
                for name in ("key", "title", "block_type", "blocks"):
                    if name not in sec:
                        errors.append(f"content.sections[{idx}] 缺少 {name}")
                bt = sec.get("block_type")
                if bt not in SUPPORTED_BLOCK_TYPES:
                    errors.append(f"content.sections[{idx}].block_type 非法: {bt!r}")
                blocks = sec.get("blocks")
                if not isinstance(blocks, list) or not blocks:
                    errors.append(f"content.sections[{idx}].blocks 必须为非空数组")

    return errors


def load_conclusion_model(model_path: Path) -> Any:
    """动态加载 content_v2.py 中的 ConclusionRecordV2。"""
    if not model_path.exists():
        raise FileNotFoundError(f"模型文件不存在: {model_path}")

    spec = importlib.util.spec_from_file_location("content_v2_dynamic", model_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"无法导入模型文件: {model_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    model_cls = getattr(module, "ConclusionRecordV2", None)
    if model_cls is None:
        raise AttributeError(f"{model_path} 中未找到 ConclusionRecordV2")
    if not hasattr(model_cls, "model_validate"):
        raise TypeError("ConclusionRecordV2 不是 Pydantic v2 模型")
    # 某些动态导入场景下前向引用不会自动完成，主动 rebuild 一次可避免
    # “class-not-fully-defined” 类错误。
    if hasattr(model_cls, "model_rebuild"):
        try:
            model_cls.model_rebuild(force=True, _types_namespace=module.__dict__)
        except TypeError:
            model_cls.model_rebuild(force=True)
    return model_cls


def build_validation_bundle(config: BuildConfig) -> ValidationBundle:
    """构建校验器：Pydantic -> JSON Schema -> basic。"""
    startup_warnings: list[str] = []

    if config.skip_validation:
        startup_warnings.append("已开启 --skip-validation，仅执行基础结构检查")
        return ValidationBundle("basic_only", startup_warnings, validate_record_basic_shape)

    # 1) 优先 Pydantic 模型
    try:
        model_cls = load_conclusion_model(config.model_path)

        def validate_with_model(record: dict[str, Any]) -> list[str]:
            basic_errors = validate_record_basic_shape(record)
            if basic_errors:
                return basic_errors
            try:
                model_cls.model_validate(record)
                return []
            except Exception as exc:
                return [f"Pydantic 校验失败: {exc}"]

        return ValidationBundle("pydantic_model", startup_warnings, validate_with_model)
    except Exception as exc:
        startup_warnings.append(f"Pydantic 校验器不可用: {exc}")

    # 2) JSON Schema 兜底
    if config.schema_path.exists():
        try:
            import jsonschema  # type: ignore

            schema = json.loads(config.schema_path.read_text(encoding="utf-8"))
            validator = jsonschema.Draft202012Validator(schema)

            def validate_with_schema(record: dict[str, Any]) -> list[str]:
                basic_errors = validate_record_basic_shape(record)
                if basic_errors:
                    return basic_errors
                errs = sorted(validator.iter_errors(record), key=lambda e: list(e.path))
                return [f"JSON Schema: {'/'.join(map(str, err.path))} -> {err.message}" for err in errs]

            return ValidationBundle("jsonschema", startup_warnings, validate_with_schema)
        except Exception as exc:
            startup_warnings.append(f"JSON Schema 校验器不可用: {exc}")
    else:
        startup_warnings.append(f"schema 文件不存在: {config.schema_path}")

    startup_warnings.append("已回退到基础结构校验")
    return ValidationBundle("basic_fallback", startup_warnings, validate_record_basic_shape)


def run_migration(config: BuildConfig) -> tuple[dict[str, Any], ConversionReport]:
    """执行迁移主流程。"""
    LOGGER.info("输入: %s", config.input_path)
    LOGGER.info("输出: %s", config.output_path)
    LOGGER.info("报告: %s", config.report_path)

    source_map, parse_warnings = load_source_map(config.input_path, config.disable_node_fallback)
    if not isinstance(source_map, dict):
        raise ParseError("输入顶层不是对象映射")

    validator = build_validation_bundle(config)
    fallback_module = normalize_non_empty_string(config.input_path.stem) or "unknown_module"

    report = ConversionReport(
        total_records=len(source_map),
        warnings=parse_warnings + validator.startup_warnings,
    )

    LOGGER.info("校验模式: %s", validator.mode)
    LOGGER.info("记录总数: %d", report.total_records)

    output_mapping: dict[str, Any] = {}

    for idx, (source_key, value) in enumerate(source_map.items(), start=1):
        LOGGER.debug("处理记录 %d/%d: %s", idx, report.total_records, source_key)

        if not isinstance(value, dict):
            msg = "源记录不是对象"
            report.add(RecordStatus(source_key=source_key, record_id=None, status="failed", error=msg))
            report.warnings.append(f"[{source_key}] {msg}")
            continue

        try:
            record, record_warnings = convert_record(source_key, value, fallback_module)
            record_id = record.get("id")
            if not isinstance(record_id, str) or not record_id.strip():
                raise ValueError("迁移后 id 非法")
            if record_id in output_mapping:
                raise ValueError(f"迁移后 id 冲突: {record_id}")

            validation_errors = validator.validate(record)
            if validation_errors:
                if config.strict_validation:
                    raise ValueError("；".join(validation_errors))
                record_warnings.extend([f"[校验警告] {e}" for e in validation_errors])

            output_mapping[record_id] = record
            report.add(
                RecordStatus(
                    source_key=source_key,
                    record_id=record_id,
                    status="success",
                    warnings=record_warnings,
                )
            )
        except Exception as exc:
            error_text = f"{type(exc).__name__}: {exc}"
            report.add(
                RecordStatus(
                    source_key=source_key,
                    record_id=normalize_non_empty_string(value.get("id")),
                    status="failed",
                    error=error_text,
                )
            )
            report.warnings.append(f"[{source_key}] 迁移失败: {error_text}")
            LOGGER.error("记录失败 | key=%s | error=%s", source_key, error_text)

    # 计数兜底
    report.success_count = sum(1 for s in report.per_record_status.values() if s.get("status") == "success")
    report.failed_count = sum(1 for s in report.per_record_status.values() if s.get("status") == "failed")

    return output_mapping, report


def main() -> int:
    """CLI 入口。"""
    configure_console_encoding()
    args = parse_args()
    config = build_config_from_args(args)
    configure_logging(config.log_level)

    try:
        output_mapping, report = run_migration(config)
        write_json(config.output_path, output_mapping)
        write_json(config.report_path, asdict(report))

        LOGGER.info("迁移完成: total=%d success=%d failed=%d", report.total_records, report.success_count, report.failed_count)
        LOGGER.info("canonical: %s", config.output_path)
        LOGGER.info("report: %s", config.report_path)
        return 0
    except Exception as exc:
        LOGGER.error("迁移失败: %s", exc)
        LOGGER.debug("异常详情", exc_info=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
