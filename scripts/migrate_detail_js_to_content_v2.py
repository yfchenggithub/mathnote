from __future__ import annotations

"""
===============================================================================
脚本名称: migrate_detail_js_to_content_v2.py
===============================================================================

功能说明
--------
将历史详情页数据（`module.exports = { [id]: DetailRecord }`）迁移为
跨端统一协议 `canonical_content_v2.json`，并输出结构化迁移报告
`conversion_report.json`。

适用场景
--------
1. 既有微信小程序 detail 数据需要统一到 canonical content v2 协议。
2. 迁移过程需要“保守保真”：尽量不丢字段、不中断全量处理。
3. 迁移后需要可审计报告，便于内容工程团队排查与二次修复。

输入 / 输出
-----------
输入:
- detail js 文件（例如 `data/content/07_inequality.js`）
- 文件形态通常为 `module.exports = {...}`，并可能包含注释头

输出:
1. canonical_content_v2.json
   - 顶层对象映射: `{ "I001": ConclusionRecordV2, ... }`
2. conversion_report.json
   - `total_records / success_count / failed_count / warnings / per_record_status`

执行流程概述
------------
1. 读取并解析 JS 导出对象（优先 Python 解析，失败回退 Node require）。
2. 遍历源记录，逐条执行字段映射与标准化。
3. 在“转换完成后、写盘前”逐条调用 `ConclusionRecordV2` 校验。
4. 按策略处理异常（默认记录错误并继续；可切换严格模式）。
5. 写出 canonical 数据与报告。

校验机制说明（为什么要引入 ConclusionRecordV2）
-------------------------------------------
本脚本承担“迁移器”职责，最容易出现的问题是“字段看似迁移成功，
但结构不符合目标协议”。因此校验必须放在：

`原始数据 -> 标准结构（convert_record） -> Schema/Pydantic 校验 -> 落盘`

这样可以在不影响转换流程可读性的前提下，把协议一致性问题尽早暴露，
并定位到“文件 + 记录 + 字段 + 原因”，避免把脏数据写入下游系统。

异常处理策略
------------
默认策略: “记录错误并继续处理其它记录”
- 迁移任务通常是批量内容工程任务，局部脏数据不应阻断全量产出。
- 每条失败都写入 `conversion_report.json`，便于后续精修。

严格模式: `--strict-validation`
- 对校验失败记录标记为 failed，不写入 canonical 输出。
- 仍继续处理其它记录（非 fail-fast），保证全量扫描和完整报告。

依赖说明
--------
- Python 标准库: argparse/pathlib/logging/json/re/subprocess 等
- Pydantic v2: 用于优先校验 `ConclusionRecordV2`
- 可选 jsonschema: 当 Pydantic 模型不可用时作为次级校验
- 可选 Node.js: 当 Python 无法直接解析 JS 模块时用于回退解析

使用方式
--------
1) 基础迁移:
   python scripts/migrate_detail_js_to_content_v2.py \
     --input data/content/07_inequality.js

2) 严格校验（校验失败记录计入 failed）:
   python scripts/migrate_detail_js_to_content_v2.py \
     --input data/content/07_inequality.js --strict-validation

3) 跳过强校验，仅做基础结构检查:
   python scripts/migrate_detail_js_to_content_v2.py \
     --input data/content/07_inequality.js --skip-validation

关键设计原则
------------
1. 最小改动原则: 保留原主流程，不另起割裂的新流程。
2. 可调试原则: 日志与报告可定位到文件、记录、字段。
3. 可扩展原则: 校验器与策略可替换，便于后续接入更多 schema。
4. 最小风险迁移: 非核心字段不丢失，尽量落入 ext.extra / assets.extra。
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
    """运行配置。

    设计原因:
    - 把 CLI 参数收敛为单个对象，减少函数间参数扩散。
    - 后续扩展批处理/远端输入时，可直接扩展该配置而不改主流程签名。
    """

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
    """单条记录处理状态。"""

    source_key: str
    record_id: str | None
    status: str
    warnings: list[str] = field(default_factory=list)
    error: str | None = None


@dataclass
class ConversionReport:
    """全量迁移报告。

    说明:
    - `warnings` 用于保存全局级提示（解析回退、校验器回退等）。
    - `per_record_status` 保存逐条处理结果，便于精确定位。
    """

    total_records: int = 0
    success_count: int = 0
    failed_count: int = 0
    warnings: list[str] = field(default_factory=list)
    per_record_status: dict[str, dict[str, Any]] = field(default_factory=dict)

    def add(self, status: RecordStatus) -> None:
        """追加单条状态并维护计数。"""
        if status.status == "success":
            self.success_count += 1
        else:
            self.failed_count += 1
        self.per_record_status[status.source_key] = asdict(status)


@dataclass
class ValidationBundle:
    """校验器封装。

    字段说明:
    - mode: 当前使用的校验模式（pydantic_model/jsonschema/basic_xxx）。
    - startup_warnings: 构建校验器过程中的降级信息。
    - validate: 统一校验入口，返回“结构化错误文本列表”。
    """

    mode: str
    startup_warnings: list[str]
    validate: Callable[[dict[str, Any], Path, str | None], list[str]]


class ParseError(RuntimeError):
    """输入解析错误（JS -> Python dict）。"""


def configure_console_encoding() -> None:
    """尽力将控制台输出改为 UTF-8。

    设计原因:
    - Windows 控制台默认编码可能导致中文日志乱码。
    - 仅“尽力”处理，不因编码配置失败而中断迁移流程。
    """
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None or not hasattr(stream, "reconfigure"):
            continue
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


def configure_logging(level_name: str) -> None:
    """初始化日志系统。"""
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")


def parse_args() -> argparse.Namespace:
    """解析命令行参数。

    返回:
    - argparse.Namespace，后续由 `build_config_from_args` 转为强类型配置对象。

    设计原因:
    - 保持与历史脚本习惯一致（argparse + 明确选项）。
    - 为后续新增模式（例如 batch/fail-fast）保留扩展位。
    """
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
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="跳过模型/Schema 强校验，仅执行基础结构检查",
    )
    parser.add_argument(
        "--strict-validation",
        action="store_true",
        help="校验失败时，该条记录记为 failed（默认仅记 warning）",
    )
    parser.add_argument(
        "--disable-node-fallback",
        action="store_true",
        help="禁用 Node require 回退解析",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="日志级别",
    )
    return parser.parse_args()


def build_config_from_args(args: argparse.Namespace) -> BuildConfig:
    """将 argparse 输出转换为 BuildConfig。

    边界条件:
    - 未显式指定 output/report 时，默认输出到输入文件同目录。
    """
    input_path = Path(args.input).resolve()
    output_path = (
        Path(args.output).resolve()
        if args.output
        else input_path.parent / "canonical_content_v2.json"
    )
    report_path = (
        Path(args.report).resolve()
        if args.report
        else input_path.parent / "conversion_report.json"
    )

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
    """按 UTF-8 + pretty 格式写 JSON。

    调用时机:
    - 仅在主流程完成后调用，避免中间状态写盘污染。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_non_empty_string(value: Any) -> str | None:
    """转为非空字符串。

    返回:
    - 非空字符串 -> str
    - 空值/空串 -> None
    """
    if value is None:
        return None
    text = value.strip() if isinstance(value, str) else str(value).strip()
    return text or None


def normalize_nullable_string(value: Any) -> str | None:
    """空字符串归一化为 None。"""
    return normalize_non_empty_string(value)


def normalize_string_list(value: Any) -> list[str]:
    """将输入标准化为字符串数组（去空、去首尾空白）。"""
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
    """alias 标准化。

    规则:
    - list: 逐项清洗
    - str: 按中英文逗号/分号/换行切分
    - 其它: 转单元素数组后清洗
    """
    if isinstance(value, str):
        parts = re.split(r"[,，;\n]+", value.strip())
        return [p.strip() for p in parts if p and p.strip()]
    return normalize_string_list(value)


def normalize_alt_nodes(value: Any) -> list[str]:
    """altNodes 标准化（兼容字符串和数组）。

    规则:
    - 字符串按中英文逗号拆分
    - 去空白、去空串、去重保持顺序
    """
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
    """宽松布尔转换（兼容 0/1/true/false/yes/no）。"""
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
    """将 difficulty 规范到 0~10 整数区间。"""
    if value in (None, ""):
        return None
    try:
        number = int(float(value))
    except Exception:
        warnings.append(f"difficulty 无法解析: {value!r}，已置为 null")
        return None
    if number < 0:
        warnings.append(f"difficulty={number} < 0，已钳制为 0")
        return 0
    if number > 10:
        warnings.append(f"difficulty={number} > 10，已钳制为 10")
        return 10
    return number


def normalize_non_negative_number(
    value: Any,
    field_name: str,
    warnings: list[str],
) -> int | float | None:
    """将值转为非负数，失败返回 None 并写 warning。"""
    if value in (None, ""):
        return None
    try:
        number = float(value)
    except Exception:
        warnings.append(f"{field_name} 无法解析: {value!r}，已置为 null")
        return None
    if number < 0:
        warnings.append(f"{field_name}={number} < 0，已置为 null")
        return None
    return int(number) if number.is_integer() else number


def preview_text(value: Any, limit: int = 160) -> str:
    """把任意值转短文本预览，用于 warning 日志。"""
    try:
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    except Exception:
        text = repr(value)
    compact = re.sub(r"\s+", " ", text).strip()
    return compact if len(compact) <= limit else compact[: limit - 3] + "..."


def slugify_record(record_id: str, title: str | None) -> str:
    """用 `id + title` 生成稳定 slug。

    注意:
    - 目标是“稳定”而非“完美 SEO”。
    - 失败时回退为基于 id 的 slug。
    """
    raw = f"{record_id}-{title or ''}".strip().lower()
    normalized = unicodedata.normalize("NFKD", raw)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    if slug:
        return slug
    fallback = re.sub(r"[^a-z0-9]+", "-", record_id.lower()).strip("-")
    return fallback or "record"


def extract_balanced_brace_object(text: str, start: int) -> str:
    """从指定位置提取平衡花括号对象字面量。

    设计原因:
    - 源文件不是标准 JSON，而是 JS 导出；且可能夹带注释、字符串。
    - 需要一个容错扫描器，避免正则直接截断造成误解析。
    """
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
    """优先使用 Python 解析 module.exports。

    关键点:
    - 从后往前匹配 `module.exports=`，避免命中注释头示例。
    - 若文件本身就是 JSON，也支持直接 `json.loads`。
    """
    matches = list(re.finditer(r"module\.exports\s*=", js_text))
    if not matches:
        data = json.loads(js_text)
        if not isinstance(data, dict):
            raise ParseError("输入顶层不是对象")
        return data

    parse_errors: list[str] = []
    for match in reversed(matches):
        start = js_text.find("{", match.end())
        if start == -1:
            parse_errors.append("module.exports 后未找到 '{'")
            continue
        try:
            object_literal = extract_balanced_brace_object(js_text, start)
            data = json.loads(object_literal)
            if not isinstance(data, dict):
                parse_errors.append("module.exports 根对象不是对象")
                continue
            return data
        except Exception as exc:
            parse_errors.append(str(exc))

    message = parse_errors[0] if parse_errors else "unknown error"
    raise ParseError(f"Python 解析 module.exports 失败: {message}")


def parse_js_module_exports_via_node(input_path: Path) -> dict[str, Any]:
    """Node require 回退解析。

    何时使用:
    - Python 解析失败时。

    为什么保留:
    - 某些 JS 细节（例如更复杂对象字面量）由 Node 解析更稳妥。
    """
    node_script = (
        "const path=require('path');"
        "const p=process.argv[1];"
        "const d=require(path.resolve(p));"
        "process.stdout.write(JSON.stringify(d));"
    )
    result = subprocess.run(
        ["node", "-e", node_script, str(input_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise ParseError(f"Node 回退解析失败: {result.stderr.strip() or 'unknown'}")
    data = json.loads(result.stdout)
    if not isinstance(data, dict):
        raise ParseError("Node 解析结果根对象不是对象")
    return data


def load_source_map(input_path: Path, disable_node_fallback: bool) -> tuple[dict[str, Any], list[str]]:
    """加载输入文件并返回源记录映射。

    返回:
    - source_map: 源数据映射（id -> detail record）
    - warnings: 解析阶段 warning（例如触发回退解析）

    设计原因:
    - 把“加载 + 解析 + 回退策略”集中在一个函数，主流程更清晰。
    """
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
    """生成稳定 block id。

    设计原因:
    - block 需要稳定 id 便于前端追踪、测试对比和后续 diff。
    """
    key = unicodedata.normalize("NFKD", section_key or "section")
    key = key.encode("ascii", "ignore").decode("ascii").lower()
    key = re.sub(r"[^a-z0-9]+", "-", key).strip("-") or "section"
    return f"{key}-b{index}"


def convert_segments_to_tokens(segments: Any, warnings: list[str]) -> list[dict[str, Any]]:
    """legacy `segments` -> v2 token 列表。

    支持:
    - text -> text token
    - math/math_inline -> math_inline token
    - math_display -> math_display token

    边界策略:
    - 遇到未知结构不抛异常，降级为文本并写 warning。
    """
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
    return {
        "id": block_id,
        "type": "paragraph",
        "tokens": tokens or [text_token("（空段落）")],
    }


def build_math_block(block_id: str, latex: str) -> dict[str, Any]:
    """构造 math_block。"""
    return {
        "id": block_id,
        "type": "math_block",
        "latex": normalize_non_empty_string(latex) or r"\text{N/A}",
        "align": "center",
    }


def map_text_layout_items_to_blocks(
    section_key: str,
    items: Any,
    warnings: list[str],
) -> list[dict[str, Any]]:
    """layout=text 的 items -> blocks。

    规则对应:
    1) {text} -> paragraph
    2) {latex} -> math_block
    3) {segments:[...]} -> paragraph(tokens)
    4) 未知形态 -> warning + paragraph 降级
    """
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
            blocks.append(
                build_paragraph_block(
                    block_id,
                    convert_segments_to_tokens(item.get("segments"), warnings),
                )
            )
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


def map_theorem_list_to_block(
    section_key: str,
    items: Any,
    warnings: list[str],
) -> dict[str, Any]:
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
    layout_norm = (layout or "").strip().lower()
    key_norm = (key or "").strip().lower()

    if "summary" in key_norm or "总结" in title:
        return "summary"
    if (
        "trap" in key_norm
        or "warning" in key_norm
        or "易错" in title
        or "陷阱" in title
        or "注意" in title
    ):
        return "warning_group"
    if layout_norm == "theorem-list":
        return "theorem_group"
    if layout_norm == "text":
        return "rich_text"
    if "proof" in key_norm or "证明" in title:
        # TODO: 后续可升级 proof_steps 结构化解析
        return "rich_text"
    return "rich_text"


def map_sections(sections: Any, warnings: list[str]) -> list[dict[str, Any]]:
    """迁移 legacy sections -> content.sections。

    在流程中的位置:
    - 属于 convert_record 的核心步骤之一。

    边界处理:
    - sections 非数组: 自动包装并记录 warning
    - section/item 未知形态: 降级为 paragraph 文本，不中断迁移
    """
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
            blocks = [
                build_paragraph_block(
                    make_block_id(key, 1),
                    [text_token("原 section 为空，迁移占位")],
                )
            ]

        mapped.append(
            {
                "key": key,
                "title": title,
                "block_type": block_type,
                "blocks": blocks,
            }
        )

    return mapped


def normalize_variable_item(item: Any, idx: int, warnings: list[str]) -> dict[str, Any] | None:
    """单个 variable 映射为 VariableDef。

    规则:
    - {latex, description} -> {name, latex, description, required}
    - 缺失 description: 填充占位文案并记录 warning
    - 缺失 latex/name: 该条跳过
    """
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
    """variables 映射入口。"""
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
    """标准化 conditions/conclusions 输入为字符串数组。"""
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
    """conditions MVP 迁移。

    当前策略:
    - 不做复杂数学分词
    - 每条条件包装为 token 列表（text token）
    """
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
    """conclusions MVP 迁移。"""
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
    """plain 层迁移（空串统一转 null）。"""
    return {
        "statement": normalize_nullable_string(source.get("statement")),
        "explanation": normalize_nullable_string(source.get("explanation")),
        "proof": normalize_nullable_string(source.get("proof")),
        "examples": normalize_nullable_string(source.get("examples")),
        "traps": normalize_nullable_string(source.get("traps")),
        "summary": normalize_nullable_string(source.get("summary")),
    }


def map_assets(raw_assets: Any, warnings: list[str]) -> dict[str, Any]:
    """assets 迁移。

    规则:
    - 识别 cover/svg/png/pdf/mp4
    - 空串 -> null
    - 未知资源进入 assets.extra（kind/url/meta）
    """
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
    """收集暂未结构化字段到 ext.extra。

    设计原因:
    - 迁移第一阶段优先保真，避免信息丢失。
    - 后续可以逐步把 ext.extra 中高价值字段再结构化。
    """
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


def convert_record(
    source_key: str,
    source: dict[str, Any],
    fallback_module: str,
) -> tuple[dict[str, Any], list[str]]:
    """将单条 legacy 记录转换为 canonical v2 记录。

    在流程中的位置:
    - 解析完成后、校验前。

    返回:
    - record: 目标结构字典（尚未写盘）
    - warnings: 迁移阶段的非致命告警

    设计原因:
    - 转换与校验解耦：先得到标准候选数据，再用模型严格校验。
    - 便于单元测试：可单独测试该函数的字段映射行为。
    """
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

def stringify_location(loc: Any) -> str:
    """将 pydantic/jsonschema 的 loc/path 转换为可读字段路径。"""
    if loc is None:
        return "<root>"
    if isinstance(loc, (list, tuple)):
        return ".".join(str(part) for part in loc) if loc else "<root>"
    text = str(loc).strip()
    return text or "<root>"


def format_structured_error(
    *,
    source_file: Path,
    record_id: str | None,
    field_path: str,
    reason: str,
    validator: str,
) -> str:
    """统一校验错误文本格式。

    目标:
    - 人可读
    - 可 grep
    - 可直接定位 `文件 + 记录 + 字段 + 原因 + 校验器`
    """
    rid = record_id or "<unknown>"
    return (
        f"file={source_file} | record_id={rid} | field={field_path} | "
        f"reason={reason} | validator={validator}"
    )


def validate_record_basic_shape(
    record: dict[str, Any],
    source_file: Path,
    record_id: str | None,
) -> list[str]:
    """基础结构校验兜底。

    使用时机:
    - 未加载到 Pydantic 模型且 jsonschema 不可用时。

    说明:
    - 该校验不替代 ConclusionRecordV2，只做最小结构防线。
    """
    errors: list[str] = []

    def push(field: str, reason: str) -> None:
        errors.append(
            format_structured_error(
                source_file=source_file,
                record_id=record_id,
                field_path=field,
                reason=reason,
                validator="basic_shape",
            )
        )

    if not isinstance(record, dict):
        push("<root>", "record 不是对象")
        return errors

    for key in ("id", "identity", "meta", "content"):
        if key not in record:
            push(key, "缺少必需顶层字段")

    if not isinstance(record.get("id"), str) or not str(record.get("id", "")).strip():
        push("id", "必须为非空字符串")

    identity = record.get("identity")
    if not isinstance(identity, dict):
        push("identity", "必须为对象")
    else:
        module = identity.get("module")
        if not isinstance(module, str) or not module.strip():
            push("identity.module", "必须为非空字符串")

    meta = record.get("meta")
    if not isinstance(meta, dict):
        push("meta", "必须为对象")
    else:
        title = meta.get("title")
        if not isinstance(title, str) or not title.strip():
            push("meta.title", "必须为非空字符串")

    content = record.get("content")
    if not isinstance(content, dict):
        push("content", "必须为对象")
    else:
        if content.get("render_schema_version") != 2:
            push("content.render_schema_version", "必须为 2")
        for name in ("variables", "conditions", "conclusions", "sections"):
            if name in content and not isinstance(content.get(name), list):
                push(f"content.{name}", "必须为数组")

        sections = content.get("sections", [])
        if isinstance(sections, list):
            for idx, sec in enumerate(sections, start=1):
                sec_path = f"content.sections[{idx}]"
                if not isinstance(sec, dict):
                    push(sec_path, "必须为对象")
                    continue
                for name in ("key", "title", "block_type", "blocks"):
                    if name not in sec:
                        push(f"{sec_path}.{name}", "缺少字段")
                bt = sec.get("block_type")
                if bt not in SUPPORTED_BLOCK_TYPES:
                    push(f"{sec_path}.block_type", f"非法值: {bt!r}")
                blocks = sec.get("blocks")
                if not isinstance(blocks, list) or not blocks:
                    push(f"{sec_path}.blocks", "必须为非空数组")

    return errors


def load_conclusion_model(model_path: Path) -> Any:
    """动态加载 `ConclusionRecordV2` 模型。

    设计原因:
    - 不强依赖固定包路径，允许在脚本目录下直接加载 `content_v2.py`。
    - 保持迁移脚本与模型文件的松耦合。

    返回:
    - 可调用 `model_validate` 的模型类。
    """
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

    # 动态导入场景下，前向引用有时不会自动完成，主动 rebuild 提升稳定性。
    if hasattr(model_cls, "model_rebuild"):
        try:
            model_cls.model_rebuild(force=True, _types_namespace=module.__dict__)
        except TypeError:
            model_cls.model_rebuild(force=True)

    return model_cls


def build_validation_bundle(config: BuildConfig) -> ValidationBundle:
    """构建校验器（优先 ConclusionRecordV2）。

    优先级:
    1. `content_v2.py` 中 ConclusionRecordV2（推荐）
    2. jsonschema + schema 文件（可选）
    3. 基础结构校验（兜底）

    设计原因:
    - 尽量复用项目内“唯一真相模型”。
    - 在模型不可用时保证脚本仍可运行并给出降级提示。
    """
    startup_warnings: list[str] = []

    if config.skip_validation:
        startup_warnings.append("已开启 --skip-validation，仅执行基础结构检查")
        return ValidationBundle(
            mode="basic_only",
            startup_warnings=startup_warnings,
            validate=validate_record_basic_shape,
        )

    # 1) 优先 Pydantic 模型
    try:
        model_cls = load_conclusion_model(config.model_path)

        def validate_with_model(record: dict[str, Any], source_file: Path, record_id: str | None) -> list[str]:
            basic_errors = validate_record_basic_shape(record, source_file, record_id)
            if basic_errors:
                return basic_errors

            try:
                model_cls.model_validate(record)
                return []
            except Exception as exc:
                # 尽量提取结构化错误（loc + msg + type）
                if hasattr(exc, "errors") and callable(getattr(exc, "errors")):
                    parsed_errors: list[str] = []
                    for err in exc.errors():
                        loc = stringify_location(err.get("loc"))
                        msg = str(err.get("msg", "unknown validation error"))
                        typ = str(err.get("type", "unknown_type"))
                        parsed_errors.append(
                            format_structured_error(
                                source_file=source_file,
                                record_id=record_id,
                                field_path=loc,
                                reason=f"{msg} (type={typ})",
                                validator="pydantic.ConclusionRecordV2",
                            )
                        )
                    return parsed_errors or [
                        format_structured_error(
                            source_file=source_file,
                            record_id=record_id,
                            field_path="<root>",
                            reason=str(exc),
                            validator="pydantic.ConclusionRecordV2",
                        )
                    ]

                return [
                    format_structured_error(
                        source_file=source_file,
                        record_id=record_id,
                        field_path="<root>",
                        reason=str(exc),
                        validator="pydantic.ConclusionRecordV2",
                    )
                ]

        return ValidationBundle(
            mode="pydantic_model",
            startup_warnings=startup_warnings,
            validate=validate_with_model,
        )
    except Exception as exc:
        startup_warnings.append(f"Pydantic 校验器不可用: {exc}")

    # 2) JSON Schema 兜底
    if config.schema_path.exists():
        try:
            import jsonschema  # type: ignore

            schema = json.loads(config.schema_path.read_text(encoding="utf-8"))
            validator = jsonschema.Draft202012Validator(schema)

            def validate_with_schema(record: dict[str, Any], source_file: Path, record_id: str | None) -> list[str]:
                basic_errors = validate_record_basic_shape(record, source_file, record_id)
                if basic_errors:
                    return basic_errors

                errors = sorted(validator.iter_errors(record), key=lambda e: list(e.path))
                formatted: list[str] = []
                for err in errors:
                    loc = stringify_location(list(err.path))
                    formatted.append(
                        format_structured_error(
                            source_file=source_file,
                            record_id=record_id,
                            field_path=loc,
                            reason=err.message,
                            validator="jsonschema.Draft202012",
                        )
                    )
                return formatted

            return ValidationBundle(
                mode="jsonschema",
                startup_warnings=startup_warnings,
                validate=validate_with_schema,
            )
        except Exception as exc:
            startup_warnings.append(f"JSON Schema 校验器不可用: {exc}")
    else:
        startup_warnings.append(f"schema 文件不存在: {config.schema_path}")

    # 3) 基础结构兜底
    startup_warnings.append("已回退到基础结构校验")
    return ValidationBundle(
        mode="basic_fallback",
        startup_warnings=startup_warnings,
        validate=validate_record_basic_shape,
    )


def run_migration(config: BuildConfig) -> tuple[dict[str, Any], ConversionReport]:
    """迁移主流程。

    核心流程:
    1. 读取源数据
    2. 逐条转换（convert_record）
    3. 逐条校验（ConclusionRecordV2 / schema / basic）
    4. 聚合结果并返回

    为什么把校验放在“转换后、写盘前”:
    - 转换后数据最接近最终落盘形态。
    - 可以精准验证目标协议，不污染转换逻辑。
    - 失败可在写盘前拦截，避免输出不可用记录。
    """
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
            report.warnings.append(
                format_structured_error(
                    source_file=config.input_path,
                    record_id=None,
                    field_path="<root>",
                    reason=msg,
                    validator="precheck",
                )
            )
            continue

        try:
            # 第 1 阶段：字段转换（保留原主流程）
            record, record_warnings = convert_record(source_key, value, fallback_module)

            record_id = record.get("id")
            if not isinstance(record_id, str) or not record_id.strip():
                raise ValueError("迁移后 id 非法")
            if record_id in output_mapping:
                raise ValueError(f"迁移后 id 冲突: {record_id}")

            # 第 2 阶段：严格协议校验（新增核心能力）
            # 放在此处的原因：record 已是最终结构，可直接验证落盘质量。
            validation_errors = validator.validate(record, config.input_path, record_id)
            if validation_errors:
                if config.strict_validation:
                    # 严格模式：该条视为失败，不写入 output。
                    raise ValueError("；".join(validation_errors))
                # 非严格模式：记录 warning 并继续写入。
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
            rid = normalize_non_empty_string(value.get("id"))
            report.add(
                RecordStatus(
                    source_key=source_key,
                    record_id=rid,
                    status="failed",
                    error=error_text,
                )
            )
            report.warnings.append(
                format_structured_error(
                    source_file=config.input_path,
                    record_id=rid,
                    field_path="<root>",
                    reason=error_text,
                    validator="pipeline",
                )
            )
            LOGGER.error("记录失败 | key=%s | error=%s", source_key, error_text)

    # 计数兜底（防止后续修改影响计数一致性）
    report.success_count = sum(1 for s in report.per_record_status.values() if s.get("status") == "success")
    report.failed_count = sum(1 for s in report.per_record_status.values() if s.get("status") == "failed")

    return output_mapping, report


def main() -> int:
    """CLI 入口。

    流程:
    - 初始化编码与日志
    - 构建配置
    - 执行迁移并写出结果

    返回:
    - 0: 成功
    - 1: 失败
    """
    configure_console_encoding()
    args = parse_args()
    config = build_config_from_args(args)
    configure_logging(config.log_level)

    try:
        output_mapping, report = run_migration(config)
        write_json(config.output_path, output_mapping)
        write_json(config.report_path, asdict(report))

        LOGGER.info(
            "迁移完成: total=%d success=%d failed=%d",
            report.total_records,
            report.success_count,
            report.failed_count,
        )
        LOGGER.info("canonical: %s", config.output_path)
        LOGGER.info("report: %s", config.report_path)
        return 0
    except Exception as exc:
        LOGGER.error("迁移失败: %s", exc)
        LOGGER.debug("异常详情", exc_info=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
