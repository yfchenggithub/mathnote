from __future__ import annotations

"""
===============================================================================
脚本名称: verify_detail_js_to_content_v2_integrity.py
===============================================================================

python verify_detail_js_to_content_v2_integrity.py \
  --source-js 07_inequality.js \
  --target-json canonical_content_v2.json \
  --migration-script migrate_detail_js_to_content_v2.py

python.exe .\scripts\verify_detail_js_to_content_v2_integrity.py --source-js .\data\content\07_inequality.js --target-json .\data\content\canonical_content_v2.json --migration-script .\scripts\migrate_detail_js_to_content_v2.py  

功能说明
--------
校验 legacy detail js（例如 `07_inequality.js`）迁移到
`canonical_content_v2.json` 后的数据完整性与映射正确性。

本脚本不是新的迁移器，也不是单纯的 schema 校验器；它的职责是：
1. 根据当前 `migrate_detail_js_to_content_v2.py` 的真实映射逻辑，重建“期望目标值”。
2. 将“期望目标值”与真实 `canonical_content_v2.json` 逐字段对照。
3. 输出机器可读 JSON 报告 + 人工可读 Markdown 报告。

适用场景
--------
1. 你已经完成 detail js -> canonical v2 的迁移。
2. 你需要确认迁移后有没有丢字段、落错路径、值被改坏。
3. 你需要一份可审计报告，便于人工排查具体记录与字段。

为什么不能只做简单 JSON diff
---------------------------
因为源文件与目标文件的组织形式天然不同：
- legacy: `module.exports = { [id]: DetailRecord }`
- canonical: `{ [id]: ConclusionRecordV2 }`

例如：
- `alias` -> `meta.aliases`
- `knowledgeNode` -> `identity.knowledge_node`
- `conditions` -> `content.conditions[*].content[*]`
- `sections(layout=text/theorem-list)` -> v2 block 结构
- `usage / interactive / related_formulas / display_version` -> `ext.extra`

因此，若直接做 JSON 深比较，几乎全部会误报。
正确做法必须是：
`源数据 -> 按当前迁移器规则得到期望目标结构 -> 与真实目标结构做语义级比较`

输入 / 输出
-----------
输入:
- `--source-js`: legacy detail js 文件
- `--target-json`: canonical_content_v2.json
- `--migration-script`: migrate_detail_js_to_content_v2.py

输出:
- `migration_integrity_report.json`
- `migration_integrity_report.md`

执行流程概述
------------
1. 动态加载当前迁移脚本，复用其解析能力与 `convert_record` 作为映射真值来源。
2. 读取 source js 与 target json。
3. 对每条源记录执行：
   - 记录级校验（id、缺失、多余）
   - 强校验字段对照
   - 规则型字段对照（variables / conditions / conclusions / sections / plain / assets / ext）
4. 汇总统计并写出 JSON/Markdown 报告。

设计原则
--------
1. 真实规则优先：以当前迁移器为准，不凭主观猜测。
2. 语义比较优先：避免结构变化导致误报。
3. 单条失败不阻断全量校验：必须给出完整扫描结果。
4. 工业级可读性：日志、报告、字段路径、原因都可定位。
===============================================================================
"""

import argparse
import importlib.util
import json
import logging
import re
import sys
import traceback
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger("verify_detail_js_to_content_v2_integrity")


# ==============================
# 配置与结果对象
# ==============================


@dataclass(frozen=True)
class BuildConfig:
    """运行配置。"""

    source_js: Path
    target_json: Path
    migration_script: Path
    report_json: Path
    report_md: Path
    strict: bool
    log_level: str


@dataclass
class FieldCheck:
    """单字段校验结果。

    说明:
    - `status` 取值: pass / warning / failed / skipped
    - `source_field` 用于标记 legacy 来源字段
    - `expected_path` 用于标记 canonical 预期路径
    """

    name: str
    source_field: str
    expected_path: str
    status: str
    severity: str
    reason: str
    source_value_preview: str | None = None
    expected_value_preview: str | None = None
    actual_value_preview: str | None = None


@dataclass
class RecordVerification:
    """单条记录的校验结果。"""

    source_key: str
    record_id: str | None
    status: str
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    migration_warnings: list[str] = field(default_factory=list)
    field_checks: list[FieldCheck] = field(default_factory=list)


@dataclass
class VerificationSummary:
    """全局汇总。"""

    total_source_records: int = 0
    total_target_records: int = 0
    matched_records: int = 0
    missing_in_target: int = 0
    extra_in_target: int = 0
    passed_records: int = 0
    warning_records: int = 0
    failed_records: int = 0
    field_warning_count: int = 0
    field_failed_count: int = 0
    uncovered_legacy_field_count: int = 0


# ==============================
# 基础工具
# ==============================


def configure_console_encoding() -> None:
    """尽力把控制台切到 UTF-8，避免 Windows 中文乱码。"""
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
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="校验 detail js -> canonical_content_v2.json 的迁移完整性",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "示例:\n"
            "  python verify_detail_js_to_content_v2_integrity.py "
            "--source-js 07_inequality.js "
            "--target-json canonical_content_v2.json "
            "--migration-script migrate_detail_js_to_content_v2.py\n"
        ),
    )
    parser.add_argument("--source-js", required=True, help="源 detail js 文件")
    parser.add_argument(
        "--target-json", required=True, help="目标 canonical_content_v2.json"
    )
    parser.add_argument(
        "--migration-script",
        required=True,
        help="迁移脚本 migrate_detail_js_to_content_v2.py",
    )
    parser.add_argument(
        "--report-json",
        default="data/content/migration_integrity_report.json",
        help="输出 JSON 报告路径",
    )
    parser.add_argument(
        "--report-md",
        default="data/content/migration_integrity_report.md",
        help="输出 Markdown 报告路径",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="存在 failed 记录时在终端显著提示，但仍不以 failed records 作为退出码",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="日志级别",
    )
    return parser.parse_args()


def build_config_from_args(args: argparse.Namespace) -> BuildConfig:
    """将 argparse 结果收敛为强类型配置对象。"""
    return BuildConfig(
        source_js=Path(args.source_js).resolve(),
        target_json=Path(args.target_json).resolve(),
        migration_script=Path(args.migration_script).resolve(),
        report_json=Path(args.report_json).resolve(),
        report_md=Path(args.report_md).resolve(),
        strict=bool(args.strict),
        log_level=str(args.log_level).upper(),
    )


def write_json(path: Path, data: Any) -> None:
    """写出 JSON 文件。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def preview(value: Any, limit: int = 220) -> str | None:
    """任意值转短预览文本，便于报告阅读。"""
    if value is None:
        return None
    try:
        text = (
            value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
        )
    except Exception:
        text = repr(value)
    compact = re.sub(r"\s+", " ", text).strip()
    return compact if len(compact) <= limit else compact[: limit - 3] + "..."


def normalize_text(value: Any) -> str | None:
    """轻量文本归一化。

    设计原因:
    - 忽略首尾空白与连续空白差异
    - 不做激进数学公式改写，避免把 latex 比较弄坏
    """
    if value is None:
        return None
    text = value if isinstance(value, str) else str(value)
    text = text.strip()
    if not text:
        return None
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_string_list(value: Any) -> list[str]:
    """统一转为字符串数组并做轻量清洗。"""
    if value is None:
        return []
    items = value if isinstance(value, list) else [value]
    result: list[str] = []
    for item in items:
        text = normalize_text(item)
        if text:
            result.append(text)
    return result


def normalize_nullable_text_map(value: dict[str, Any] | None) -> dict[str, str | None]:
    """将 plain 层等简单字典统一成 {key: normalized_text_or_none}。"""
    if not isinstance(value, dict):
        return {}
    return {k: normalize_text(v) for k, v in value.items()}


def dynamic_import_module(path: Path, module_name: str) -> Any:
    """动态导入脚本文件。

    为什么需要这个函数:
    - 校验器要以“当前迁移器实现”为真值来源
    - 因此必须在运行时动态加载用户指定的 migration script
    """
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"无法导入文件: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_source_js(
    config: BuildConfig, migrator: Any
) -> tuple[dict[str, Any], list[str]]:
    """加载源 js。

    设计原因:
    - 直接复用迁移器的解析逻辑，确保“解析结果”与正式迁移过程保持一致
    - 这样校验差异才更聚焦在“映射是否正确”，而非“解析器差异”
    """
    return migrator.load_source_map(config.source_js, disable_node_fallback=False)


def load_target_json(config: BuildConfig) -> dict[str, Any]:
    """加载目标 canonical json。"""
    if not config.target_json.exists():
        raise FileNotFoundError(f"目标文件不存在: {config.target_json}")
    data = json.loads(config.target_json.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("目标 JSON 顶层必须为对象")
    return data


# ==============================
# 映射规则摘要
# ==============================


def extract_mapping_rules_from_current_migrator(migrator: Any) -> dict[str, Any]:
    """输出当前迁移器对应的规则摘要。

    说明:
    - 这里的“抽取”是工程化摘要，不是 AST 级静态分析。
    - 规则内容与当前迁移器实现保持一致；若迁移器改动，需要同步更新本函数。
    """
    legacy_fields = sorted(getattr(migrator, "LEGACY_TOP_LEVEL_FIELDS", []))
    supported_blocks = sorted(getattr(migrator, "SUPPORTED_BLOCK_TYPES", []))

    return {
        "source_top_level_shape": "module.exports = { [id]: DetailRecord }",
        "target_top_level_shape": "{ [id]: ConclusionRecordV2 }",
        "record_level": {
            "record_id": "source.id 优先；若缺失则回退 source_key",
            "source_key_mismatch": "当 source_key != source.id 时，采用 source.id 作为最终记录 id，并记 warning",
            "slug": "由 slugify_record(record_id, title) 生成",
            "module_fallback": "source.module 优先；为空时回退 source_js 文件 stem",
        },
        "field_rules": {
            "id": "id",
            "schema_version": "固定 2",
            "type": "固定 conclusion",
            "status": "固定 published",
            "title": "meta.title",
            "module": "identity.module",
            "knowledgeNode": "identity.knowledge_node",
            "altNodes": "identity.alt_nodes（字符串按中英文逗号拆分，去重保序）",
            "alias": "meta.aliases（字符串按逗号/分号/换行拆分，或保留数组）",
            "difficulty": "meta.difficulty（解析为 0~10 整数，越界钳制，异常写 warning）",
            "category": "meta.category",
            "tags": "meta.tags",
            "core_summary": "meta.summary",
            "isPro": "meta.is_pro（宽松布尔转换）",
            "remarks": "meta.remarks",
            "core_formula": "content.primary_formula",
            "variables": "content.variables（{latex|name|symbol, description|desc|text, required} -> {name, latex, description, required}）",
            "conditions": "content.conditions[*]（统一包装为 cond_i + content[text]）",
            "conclusions": "content.conclusions[*]（统一包装为 conc_i + content[text]）",
            "sections": "content.sections（layout=text/theorem-list -> blocks）",
            "statement": "content.plain.statement",
            "explanation": "content.plain.explanation",
            "proof": "content.plain.proof",
            "examples": "content.plain.examples",
            "traps": "content.plain.traps",
            "summary": "content.plain.summary",
            "assets": "assets（识别 cover/svg/png/pdf/mp4，其余进入 assets.extra）",
            "shareConfig": "ext.share（title -> title, desc/shareDesc -> desc）",
            "relations": "ext.relations（prerequisites, related_ids, similar）",
            "usage.exam_frequency": "ext.exam.frequency",
            "usage.exam_score": "ext.exam.score",
            "usage": "ext.extra.usage（完整原值保留）",
            "interactive": "ext.extra.interactive",
            "related_formulas": "ext.extra.related_formulas",
            "display_version": "ext.extra.legacy_display_version",
            "unknown_legacy_fields": "ext.extra.unmapped_legacy_fields",
        },
        "sections_rules": {
            "layout=text": [
                "{text} -> paragraph(tokens=[text])",
                "{latex} -> math_block",
                "{segments:[...]} -> paragraph(tokens)",
                "{text, latex} -> paragraph(text + math_inline)，并写 warning",
                "未知形态 -> paragraph(降级文本)，并写 warning",
            ],
            "layout=theorem-list": [
                "items -> single theorem_group block",
                "{title, desc, latex} -> theorem item",
                '缺 latex 时尝试用 text，仍无则写 "\\text{N/A}" 并 warning',
            ],
            "block_type": {
                "summary": "summary",
                "trap/warning/易错/陷阱/注意": "warning_group",
                "theorem-list": "theorem_group",
                "others": "rich_text",
            },
        },
        "legacy_top_level_fields_known_by_migrator": legacy_fields,
        "supported_block_types_known_by_migrator": supported_blocks,
        "maintain_note": "若 migrate_detail_js_to_content_v2.py 更新了映射逻辑，本校验器也需要同步更新规则摘要与比较策略。",
    }


# ==============================
# 规范化表示（用于语义比较）
# ==============================


def tokens_to_semantic(tokens: Any) -> list[dict[str, Any]]:
    """将 token 列表归一化为便于比较的表示。"""
    if not isinstance(tokens, list):
        return []
    result: list[dict[str, Any]] = []
    for token in tokens:
        if not isinstance(token, dict):
            result.append({"type": "text", "text": normalize_text(token)})
            continue
        ttype = str(token.get("type", "")).strip()
        if ttype == "text":
            result.append({"type": "text", "text": normalize_text(token.get("text"))})
        elif ttype in {"math_inline", "math_display"}:
            result.append({"type": ttype, "latex": normalize_text(token.get("latex"))})
        elif ttype == "line_break":
            result.append({"type": "line_break"})
        else:
            result.append({"type": ttype or "unknown", "raw": preview(token)})
    return result


def content_list_to_texts(content_list: Any) -> list[str]:
    """从 conditions/conclusions 的 content 字段中抽取文本。

    当前迁移器对这两类字段统一写成 text token，因此这里保持轻量处理。
    """
    if not isinstance(content_list, list):
        return []
    output: list[str] = []
    for item in content_list:
        if isinstance(item, dict):
            if item.get("type") == "text":
                text = normalize_text(item.get("text"))
                if text:
                    output.append(text)
            else:
                raw = preview(item)
                if raw:
                    output.append(raw)
        else:
            text = normalize_text(item)
            if text:
                output.append(text)
    return output


def normalize_variable_entries(items: Any) -> list[dict[str, Any]]:
    """将 canonical variables 归一化。

    比较关注点:
    - latex
    - description
    - required
    - name（多数情况下与 latex 相同）
    """
    if not isinstance(items, list):
        return []
    result: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            result.append(
                {
                    "latex": normalize_text(item),
                    "description": None,
                    "required": True,
                    "name": normalize_text(item),
                }
            )
            continue
        result.append(
            {
                "name": normalize_text(item.get("name")),
                "latex": normalize_text(item.get("latex")),
                "description": normalize_text(item.get("description")),
                "required": bool(item.get("required", True)),
            }
        )
    return result


def normalize_conditions_or_conclusions(items: Any) -> list[dict[str, Any]]:
    """归一化 canonical conditions/conclusions。"""
    if not isinstance(items, list):
        return []
    result: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            result.append(
                {
                    "title": None,
                    "texts": [normalize_text(item)] if normalize_text(item) else [],
                }
            )
            continue
        result.append(
            {
                "title": normalize_text(item.get("title")),
                "texts": content_list_to_texts(item.get("content")),
                "required": item.get("required"),
                "scope": item.get("scope"),
            }
        )
    return result


def normalize_block(block: Any) -> dict[str, Any]:
    """归一化 canonical block。"""
    if not isinstance(block, dict):
        return {"type": "unknown", "raw": preview(block)}

    btype = str(block.get("type", "")).strip() or "unknown"
    if btype == "paragraph":
        return {"type": "paragraph", "tokens": tokens_to_semantic(block.get("tokens"))}
    if btype == "math_block":
        return {
            "type": "math_block",
            "latex": normalize_text(block.get("latex")),
            "align": block.get("align"),
        }
    if btype == "theorem_group":
        items = block.get("items") if isinstance(block.get("items"), list) else []
        normalized_items: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                normalized_items.append(
                    {
                        "title": None,
                        "desc_tokens": [],
                        "formula_latex": normalize_text(item),
                    }
                )
                continue
            normalized_items.append(
                {
                    "title": normalize_text(item.get("title")),
                    "desc_tokens": tokens_to_semantic(item.get("desc_tokens")),
                    "formula_latex": normalize_text(item.get("formula_latex")),
                }
            )
        return {"type": "theorem_group", "items": normalized_items}
    return {"type": btype, "raw": preview(block)}


def normalize_canonical_section(section: Any) -> dict[str, Any]:
    """归一化目标/期望 section，便于语义比较。"""
    if not isinstance(section, dict):
        return {
            "key": None,
            "title": None,
            "block_type": "unknown",
            "blocks": [{"type": "unknown", "raw": preview(section)}],
        }
    blocks = section.get("blocks") if isinstance(section.get("blocks"), list) else []
    return {
        "key": normalize_text(section.get("key")),
        "title": normalize_text(section.get("title")),
        "block_type": normalize_text(section.get("block_type")),
        "blocks": [normalize_block(block) for block in blocks],
    }


def normalize_legacy_section(section: Any) -> dict[str, Any]:
    """归一化 legacy section。

    说明:
    - 该函数主要用于把源 section 抽成稳定语义表示，便于报告展示。
    - 真正的期望 canonical 值仍以当前迁移器 `convert_record` 产出为准。
    """
    if not isinstance(section, dict):
        return {
            "key": None,
            "title": None,
            "layout": "text",
            "items": [
                {"kind": "raw", "value": normalize_text(section) or preview(section)}
            ],
        }

    key = normalize_text(section.get("key"))
    title = normalize_text(section.get("title"))
    layout = normalize_text(section.get("layout")) or "text"
    raw_items = (
        section.get("items")
        if isinstance(section.get("items"), list)
        else ([section.get("items")] if section.get("items") is not None else [])
    )

    items: list[dict[str, Any]] = []
    for item in raw_items:
        if isinstance(item, str):
            items.append({"kind": "text", "text": normalize_text(item)})
            continue
        if not isinstance(item, dict):
            items.append({"kind": "raw", "value": preview(item)})
            continue
        if isinstance(item.get("segments"), list):
            items.append(
                {
                    "kind": "segments",
                    "segments": tokens_to_semantic(item.get("segments")),
                }
            )
            continue
        text_val = normalize_text(item.get("text"))
        latex_val = normalize_text(item.get("latex"))
        if layout == "theorem-list":
            items.append(
                {
                    "kind": "theorem_item",
                    "title": normalize_text(item.get("title")),
                    "desc": normalize_text(item.get("desc")),
                    "latex": latex_val or normalize_text(item.get("formula_latex")),
                    "text": text_val,
                }
            )
            continue
        if text_val is not None and latex_val is None:
            items.append({"kind": "text", "text": text_val})
        elif latex_val is not None and text_val is None:
            items.append({"kind": "latex", "latex": latex_val})
        elif text_val is not None and latex_val is not None:
            items.append({"kind": "text+latex", "text": text_val, "latex": latex_val})
        else:
            items.append({"kind": "raw", "value": preview(item)})
    return {"key": key, "title": title, "layout": layout, "items": items}


# ==============================
# 对比函数
# ==============================


def get_by_path(data: dict[str, Any], path: str) -> Any:
    """从嵌套 dict 中按简单点路径读取值。

    支持示例:
    - meta.title
    - ext.share.desc
    不处理带 [idx] 的复杂路径；这类由专门函数处理。
    """
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def push_check(
    result: RecordVerification,
    *,
    name: str,
    source_field: str,
    expected_path: str,
    status: str,
    severity: str,
    reason: str,
    source_value: Any = None,
    expected_value: Any = None,
    actual_value: Any = None,
) -> None:
    """向单条记录结果追加一个字段检查结果。"""
    result.field_checks.append(
        FieldCheck(
            name=name,
            source_field=source_field,
            expected_path=expected_path,
            status=status,
            severity=severity,
            reason=reason,
            source_value_preview=preview(source_value),
            expected_value_preview=preview(expected_value),
            actual_value_preview=preview(actual_value),
        )
    )
    if status == "failed":
        result.errors.append(f"{name}: {reason}")
    elif status == "warning":
        result.warnings.append(f"{name}: {reason}")


def compare_scalar_field(
    result: RecordVerification,
    *,
    name: str,
    source_field: str,
    expected_path: str,
    source_value: Any,
    expected_record: dict[str, Any],
    actual_record: dict[str, Any],
) -> None:
    """比较简单标量或简单列表字段。"""
    expected_value = get_by_path(expected_record, expected_path)
    actual_value = get_by_path(actual_record, expected_path)

    # list[str] 与标量都统一走轻量比较
    if isinstance(expected_value, list) or isinstance(actual_value, list):
        left = normalize_string_list(expected_value)
        right = normalize_string_list(actual_value)
    else:
        left = normalize_text(expected_value)
        right = normalize_text(actual_value)

    if left == right:
        push_check(
            result,
            name=name,
            source_field=source_field,
            expected_path=expected_path,
            status="pass",
            severity="info",
            reason="字段一致",
            source_value=source_value,
            expected_value=expected_value,
            actual_value=actual_value,
        )
        return

    push_check(
        result,
        name=name,
        source_field=source_field,
        expected_path=expected_path,
        status="failed",
        severity="error",
        reason="字段值与当前迁移器推导的期望值不一致",
        source_value=source_value,
        expected_value=expected_value,
        actual_value=actual_value,
    )


def compare_variables(
    result: RecordVerification,
    source: dict[str, Any],
    expected_record: dict[str, Any],
    actual_record: dict[str, Any],
) -> None:
    """比较 variables 的映射结果。"""
    source_value = source.get("variables")
    expected_items = normalize_variable_entries(
        get_by_path(expected_record, "content.variables")
    )
    actual_items = normalize_variable_entries(
        get_by_path(actual_record, "content.variables")
    )

    if expected_items == actual_items:
        push_check(
            result,
            name="variables",
            source_field="variables",
            expected_path="content.variables",
            status="pass",
            severity="info",
            reason="variables 迁移一致",
            source_value=source_value,
            expected_value=expected_items,
            actual_value=actual_items,
        )
        return

    push_check(
        result,
        name="variables",
        source_field="variables",
        expected_path="content.variables",
        status="failed",
        severity="error",
        reason="variables 与当前迁移器规则不一致，可能存在变量丢失、description 占位缺失或 required 值异常",
        source_value=source_value,
        expected_value=expected_items,
        actual_value=actual_items,
    )


def compare_conditions(
    result: RecordVerification,
    source: dict[str, Any],
    expected_record: dict[str, Any],
    actual_record: dict[str, Any],
) -> None:
    """比较 conditions。"""
    source_value = source.get("conditions")
    expected_items = normalize_conditions_or_conclusions(
        get_by_path(expected_record, "content.conditions")
    )
    actual_items = normalize_conditions_or_conclusions(
        get_by_path(actual_record, "content.conditions")
    )

    if expected_items == actual_items:
        push_check(
            result,
            name="conditions",
            source_field="conditions",
            expected_path="content.conditions",
            status="pass",
            severity="info",
            reason="conditions 迁移一致",
            source_value=source_value,
            expected_value=expected_items,
            actual_value=actual_items,
        )
        return

    push_check(
        result,
        name="conditions",
        source_field="conditions",
        expected_path="content.conditions",
        status="failed",
        severity="error",
        reason="conditions 与期望值不一致，可能出现文本丢失、顺序变化或包装结构错误",
        source_value=source_value,
        expected_value=expected_items,
        actual_value=actual_items,
    )


def compare_conclusions(
    result: RecordVerification,
    source: dict[str, Any],
    expected_record: dict[str, Any],
    actual_record: dict[str, Any],
) -> None:
    """比较 conclusions。"""
    source_value = source.get("conclusions")
    expected_items = normalize_conditions_or_conclusions(
        get_by_path(expected_record, "content.conclusions")
    )
    actual_items = normalize_conditions_or_conclusions(
        get_by_path(actual_record, "content.conclusions")
    )

    if expected_items == actual_items:
        push_check(
            result,
            name="conclusions",
            source_field="conclusions",
            expected_path="content.conclusions",
            status="pass",
            severity="info",
            reason="conclusions 迁移一致",
            source_value=source_value,
            expected_value=expected_items,
            actual_value=actual_items,
        )
        return

    push_check(
        result,
        name="conclusions",
        source_field="conclusions",
        expected_path="content.conclusions",
        status="failed",
        severity="error",
        reason="conclusions 与期望值不一致，可能出现文本丢失、顺序变化或包装结构错误",
        source_value=source_value,
        expected_value=expected_items,
        actual_value=actual_items,
    )


def compare_sections(
    result: RecordVerification,
    source: dict[str, Any],
    expected_record: dict[str, Any],
    actual_record: dict[str, Any],
) -> None:
    """比较 sections 的语义表示。

    设计要点:
    - 不直接比较原始 JSON
    - 统一转为 semantic representation 后比对
    """
    source_sections = source.get("sections")
    if source_sections is None:
        source_semantic = []
    else:
        source_items = (
            source_sections if isinstance(source_sections, list) else [source_sections]
        )
        source_semantic = [normalize_legacy_section(sec) for sec in source_items]

    expected_sections = get_by_path(expected_record, "content.sections")
    actual_sections = get_by_path(actual_record, "content.sections")
    expected_semantic = [
        normalize_canonical_section(sec) for sec in expected_sections or []
    ]
    actual_semantic = [
        normalize_canonical_section(sec) for sec in actual_sections or []
    ]

    if expected_semantic == actual_semantic:
        push_check(
            result,
            name="sections",
            source_field="sections",
            expected_path="content.sections",
            status="pass",
            severity="info",
            reason="sections 语义一致",
            source_value=source_semantic,
            expected_value=expected_semantic,
            actual_value=actual_semantic,
        )
        return

    reason = "sections 与期望值不一致，可能出现 block_type、block 数量、paragraph tokens、math_block latex 或 theorem_group item 映射异常"
    push_check(
        result,
        name="sections",
        source_field="sections",
        expected_path="content.sections",
        status="failed",
        severity="error",
        reason=reason,
        source_value=source_semantic,
        expected_value=expected_semantic,
        actual_value=actual_semantic,
    )


def compare_plain_content(
    result: RecordVerification,
    source: dict[str, Any],
    expected_record: dict[str, Any],
    actual_record: dict[str, Any],
) -> None:
    """比较 plain 层六个文本字段。"""
    source_plain = {
        "statement": source.get("statement"),
        "explanation": source.get("explanation"),
        "proof": source.get("proof"),
        "examples": source.get("examples"),
        "traps": source.get("traps"),
        "summary": source.get("summary"),
    }
    expected_plain = normalize_nullable_text_map(
        get_by_path(expected_record, "content.plain")
    )
    actual_plain = normalize_nullable_text_map(
        get_by_path(actual_record, "content.plain")
    )

    if expected_plain == actual_plain:
        push_check(
            result,
            name="plain",
            source_field="statement/explanation/proof/examples/traps/summary",
            expected_path="content.plain",
            status="pass",
            severity="info",
            reason="plain 内容一致",
            source_value=source_plain,
            expected_value=expected_plain,
            actual_value=actual_plain,
        )
        return

    push_check(
        result,
        name="plain",
        source_field="statement/explanation/proof/examples/traps/summary",
        expected_path="content.plain",
        status="failed",
        severity="error",
        reason="plain 内容与期望值不一致，可能存在正文丢失或空串/null 处理错误",
        source_value=source_plain,
        expected_value=expected_plain,
        actual_value=actual_plain,
    )


def normalize_assets(value: Any) -> dict[str, Any]:
    """归一化 assets。"""
    if not isinstance(value, dict):
        return {}
    extra = value.get("extra") if isinstance(value.get("extra"), list) else []
    extra_norm = []
    for item in extra:
        if not isinstance(item, dict):
            extra_norm.append({"kind": None, "url": normalize_text(item), "meta": {}})
            continue
        meta = item.get("meta") if isinstance(item.get("meta"), dict) else {}
        extra_norm.append(
            {
                "kind": normalize_text(item.get("kind")),
                "url": normalize_text(item.get("url")),
                "meta": meta,
            }
        )
    return {
        "cover": normalize_text(value.get("cover")),
        "svg": normalize_text(value.get("svg")),
        "png": normalize_text(value.get("png")),
        "pdf": normalize_text(value.get("pdf")),
        "mp4": normalize_text(value.get("mp4")),
        "extra": extra_norm,
    }


def compare_assets(
    result: RecordVerification,
    source: dict[str, Any],
    expected_record: dict[str, Any],
    actual_record: dict[str, Any],
) -> None:
    """比较 assets。"""
    source_value = source.get("assets")
    expected_assets = normalize_assets(expected_record.get("assets"))
    actual_assets = normalize_assets(actual_record.get("assets"))

    if expected_assets == actual_assets:
        push_check(
            result,
            name="assets",
            source_field="assets",
            expected_path="assets",
            status="pass",
            severity="info",
            reason="assets 一致",
            source_value=source_value,
            expected_value=expected_assets,
            actual_value=actual_assets,
        )
        return

    push_check(
        result,
        name="assets",
        source_field="assets",
        expected_path="assets",
        status="failed",
        severity="error",
        reason="assets 与期望值不一致，可能出现已知资源字段丢失或未知资源未进入 assets.extra",
        source_value=source_value,
        expected_value=expected_assets,
        actual_value=actual_assets,
    )


def normalize_ext(value: Any) -> dict[str, Any]:
    """归一化 ext。"""
    if not isinstance(value, dict):
        return {}
    share = value.get("share") if isinstance(value.get("share"), dict) else {}
    relations = (
        value.get("relations") if isinstance(value.get("relations"), dict) else {}
    )
    exam = value.get("exam") if isinstance(value.get("exam"), dict) else {}
    extra = value.get("extra") if isinstance(value.get("extra"), dict) else {}
    return {
        "share": {
            "title": normalize_text(share.get("title")),
            "desc": normalize_text(share.get("desc")),
        },
        "relations": {
            "prerequisites": normalize_string_list(relations.get("prerequisites")),
            "related_ids": normalize_string_list(relations.get("related_ids")),
            "similar": normalize_text(relations.get("similar")),
        },
        "exam": {
            "frequency": exam.get("frequency"),
            "score": exam.get("score"),
        },
        "extra": extra,
    }


def compare_ext_fields(
    result: RecordVerification,
    source: dict[str, Any],
    expected_record: dict[str, Any],
    actual_record: dict[str, Any],
) -> None:
    """比较 share / relations / exam / extra。"""
    expected_ext = normalize_ext(expected_record.get("ext"))
    actual_ext = normalize_ext(actual_record.get("ext"))
    source_value = {
        "shareConfig": source.get("shareConfig"),
        "relations": source.get("relations"),
        "usage": source.get("usage"),
        "interactive": source.get("interactive"),
        "related_formulas": source.get("related_formulas"),
        "display_version": source.get("display_version"),
    }

    if expected_ext == actual_ext:
        push_check(
            result,
            name="ext",
            source_field="shareConfig/relations/usage/interactive/related_formulas/display_version",
            expected_path="ext",
            status="pass",
            severity="info",
            reason="ext 一致",
            source_value=source_value,
            expected_value=expected_ext,
            actual_value=actual_ext,
        )
        return

    push_check(
        result,
        name="ext",
        source_field="shareConfig/relations/usage/interactive/related_formulas/display_version",
        expected_path="ext",
        status="failed",
        severity="error",
        reason="ext 与期望值不一致，可能出现 share/relations/exam 或 ext.extra 备份字段缺失",
        source_value=source_value,
        expected_value=expected_ext,
        actual_value=actual_ext,
    )


# ==============================
# 单条记录校验
# ==============================


def derive_record_status(record_result: RecordVerification) -> str:
    """根据 errors/warnings 推导单条记录状态。"""
    if record_result.errors:
        return "failed"
    if record_result.warnings:
        return "warning"
    return "passed"


def verify_record_integrity(
    *,
    source_key: str,
    source: dict[str, Any],
    target_record: dict[str, Any] | None,
    migrator: Any,
    fallback_module: str,
) -> RecordVerification:
    """校验单条记录完整性。

    核心思想:
    - 调用当前迁移器 `convert_record` 得到期望目标结构
    - 再把真实目标值与期望目标值逐字段比对
    """
    source_id = source.get("id") if isinstance(source, dict) else None
    record_id = (
        source_id if isinstance(source_id, str) and source_id.strip() else source_key
    )
    result = RecordVerification(
        source_key=source_key, record_id=record_id, status="passed"
    )

    if not isinstance(source, dict):
        result.errors.append("源记录不是对象，无法校验")
        result.status = "failed"
        return result

    try:
        expected_record, migration_warnings = migrator.convert_record(
            source_key, source, fallback_module
        )
        result.migration_warnings.extend(migration_warnings)
    except Exception as exc:
        result.errors.append(f"调用迁移器 convert_record 失败: {exc}")
        result.status = "failed"
        return result

    if target_record is None:
        result.errors.append("目标文件中不存在该记录")
        result.status = "failed"
        return result

    if not isinstance(target_record, dict):
        result.errors.append("目标记录不是对象")
        result.status = "failed"
        return result

    # 记录级检查
    expected_id = expected_record.get("id")
    actual_id = target_record.get("id")
    if normalize_text(expected_id) != normalize_text(actual_id):
        result.errors.append("记录 id 与当前迁移器推导的期望值不一致")

    # 强校验字段
    compare_scalar_field(
        result,
        name="id",
        source_field="id",
        expected_path="id",
        source_value=source.get("id"),
        expected_record=expected_record,
        actual_record=target_record,
    )
    compare_scalar_field(
        result,
        name="title",
        source_field="title",
        expected_path="meta.title",
        source_value=source.get("title"),
        expected_record=expected_record,
        actual_record=target_record,
    )
    compare_scalar_field(
        result,
        name="module",
        source_field="module",
        expected_path="identity.module",
        source_value=source.get("module"),
        expected_record=expected_record,
        actual_record=target_record,
    )
    compare_scalar_field(
        result,
        name="alias",
        source_field="alias",
        expected_path="meta.aliases",
        source_value=source.get("alias"),
        expected_record=expected_record,
        actual_record=target_record,
    )
    compare_scalar_field(
        result,
        name="difficulty",
        source_field="difficulty",
        expected_path="meta.difficulty",
        source_value=source.get("difficulty"),
        expected_record=expected_record,
        actual_record=target_record,
    )
    compare_scalar_field(
        result,
        name="category",
        source_field="category",
        expected_path="meta.category",
        source_value=source.get("category"),
        expected_record=expected_record,
        actual_record=target_record,
    )
    compare_scalar_field(
        result,
        name="tags",
        source_field="tags",
        expected_path="meta.tags",
        source_value=source.get("tags"),
        expected_record=expected_record,
        actual_record=target_record,
    )
    compare_scalar_field(
        result,
        name="core_summary",
        source_field="core_summary",
        expected_path="meta.summary",
        source_value=source.get("core_summary"),
        expected_record=expected_record,
        actual_record=target_record,
    )
    compare_scalar_field(
        result,
        name="isPro",
        source_field="isPro",
        expected_path="meta.is_pro",
        source_value=source.get("isPro"),
        expected_record=expected_record,
        actual_record=target_record,
    )
    compare_scalar_field(
        result,
        name="remarks",
        source_field="remarks",
        expected_path="meta.remarks",
        source_value=source.get("remarks"),
        expected_record=expected_record,
        actual_record=target_record,
    )
    compare_scalar_field(
        result,
        name="knowledgeNode",
        source_field="knowledgeNode",
        expected_path="identity.knowledge_node",
        source_value=source.get("knowledgeNode"),
        expected_record=expected_record,
        actual_record=target_record,
    )
    compare_scalar_field(
        result,
        name="altNodes",
        source_field="altNodes",
        expected_path="identity.alt_nodes",
        source_value=source.get("altNodes"),
        expected_record=expected_record,
        actual_record=target_record,
    )
    compare_scalar_field(
        result,
        name="core_formula",
        source_field="core_formula",
        expected_path="content.primary_formula",
        source_value=source.get("core_formula"),
        expected_record=expected_record,
        actual_record=target_record,
    )

    # 规则型字段
    compare_variables(result, source, expected_record, target_record)
    compare_conditions(result, source, expected_record, target_record)
    compare_conclusions(result, source, expected_record, target_record)
    compare_sections(result, source, expected_record, target_record)
    compare_plain_content(result, source, expected_record, target_record)
    compare_assets(result, source, expected_record, target_record)
    compare_ext_fields(result, source, expected_record, target_record)

    # 对目标记录做最小基础结构检查（可帮助发现不是迁移错误而是落盘/手改损坏）
    try:
        basic_errors = migrator.validate_record_basic_shape(
            target_record, Path("<target_json>"), record_id
        )
    except Exception:
        basic_errors = []
    for err in basic_errors:
        result.warnings.append(f"basic_shape: {err}")

    result.status = derive_record_status(result)
    return result


# ==============================
# 报告生成
# ==============================


def summarize_results(
    *,
    source_map: dict[str, Any],
    target_map: dict[str, Any],
    per_record: dict[str, RecordVerification],
    extra_target_ids: list[str],
    mapping_rules: dict[str, Any],
) -> VerificationSummary:
    """汇总全局统计。"""
    summary = VerificationSummary(
        total_source_records=len(source_map),
        total_target_records=len(target_map),
        matched_records=len(per_record),
        extra_in_target=len(extra_target_ids),
        uncovered_legacy_field_count=len(
            mapping_rules.get("legacy_top_level_fields_known_by_migrator", [])
        ),
    )

    for record in per_record.values():
        if record.status == "passed":
            summary.passed_records += 1
        elif record.status == "warning":
            summary.warning_records += 1
        elif record.status == "failed":
            summary.failed_records += 1
        if any("目标文件中不存在该记录" in e for e in record.errors):
            summary.missing_in_target += 1

        for check in record.field_checks:
            if check.status == "warning":
                summary.field_warning_count += 1
            elif check.status == "failed":
                summary.field_failed_count += 1

    return summary


def build_report(
    *,
    config: BuildConfig,
    source_parse_warnings: list[str],
    mapping_rules: dict[str, Any],
    per_record: dict[str, RecordVerification],
    extra_target_ids: list[str],
    summary: VerificationSummary,
) -> dict[str, Any]:
    """组装最终 JSON 报告。"""
    return {
        "script": "verify_detail_js_to_content_v2_integrity.py",
        "inputs": {
            "source_js": str(config.source_js),
            "target_json": str(config.target_json),
            "migration_script": str(config.migration_script),
        },
        "summary": asdict(summary),
        "source_parse_warnings": source_parse_warnings,
        "mapping_rules": mapping_rules,
        "extra_target_ids": extra_target_ids,
        "per_record": {
            rid: {
                "source_key": rec.source_key,
                "record_id": rec.record_id,
                "status": rec.status,
                "migration_warnings": rec.migration_warnings,
                "warnings": rec.warnings,
                "errors": rec.errors,
                "field_checks": [asdict(fc) for fc in rec.field_checks],
            }
            for rid, rec in per_record.items()
        },
    }


def write_markdown_report(path: Path, report: dict[str, Any]) -> None:
    """输出 Markdown 可读报告。"""
    summary = report["summary"]
    mapping_rules = report["mapping_rules"]
    per_record = report["per_record"]

    failed_records = [
        item for item in per_record.values() if item["status"] == "failed"
    ]
    warning_records = [
        item for item in per_record.values() if item["status"] == "warning"
    ]

    lines: list[str] = []
    lines.append("# migration_integrity_report")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    for key, value in summary.items():
        lines.append(f"- **{key}**: {value}")
    lines.append("")

    lines.append("## Mapping Rules Summary")
    lines.append("")
    lines.append("### Record Level")
    for key, value in mapping_rules.get("record_level", {}).items():
        lines.append(f"- **{key}**: {value}")
    lines.append("")

    lines.append("### Field Rules")
    for key, value in mapping_rules.get("field_rules", {}).items():
        lines.append(f"- `{key}` -> `{value}`")
    lines.append("")

    lines.append("### Sections Rules")
    for key, value in mapping_rules.get("sections_rules", {}).items():
        lines.append(f"- **{key}**: `{value}`")
    lines.append("")

    lines.append("## Failed Records")
    lines.append("")
    if not failed_records:
        lines.append("无。")
    else:
        for item in failed_records:
            lines.append(f"### {item['record_id'] or item['source_key']}")
            lines.append(f"- source_key: `{item['source_key']}`")
            for err in item.get("errors", []):
                lines.append(f"- error: {err}")
            for check in item.get("field_checks", []):
                if check.get("status") != "failed":
                    continue
                lines.append(f"  - field: `{check['name']}`")
                lines.append(f"    - source_field: `{check['source_field']}`")
                lines.append(f"    - expected_path: `{check['expected_path']}`")
                lines.append(f"    - reason: {check['reason']}")
                if check.get("source_value_preview") is not None:
                    lines.append(
                        f"    - source_value: `{check['source_value_preview']}`"
                    )
                if check.get("expected_value_preview") is not None:
                    lines.append(
                        f"    - expected_value: `{check['expected_value_preview']}`"
                    )
                if check.get("actual_value_preview") is not None:
                    lines.append(
                        f"    - actual_value: `{check['actual_value_preview']}`"
                    )
            lines.append("")

    lines.append("## Warning Records")
    lines.append("")
    if not warning_records:
        lines.append("无。")
    else:
        for item in warning_records:
            lines.append(f"### {item['record_id'] or item['source_key']}")
            lines.append(f"- source_key: `{item['source_key']}`")
            for warn in item.get("warnings", []):
                lines.append(f"- warning: {warn}")
            lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


# ==============================
# 主流程
# ==============================


def main() -> int:
    """主入口。

    退出码策略:
    - 只有输入读取失败、脚本导入失败、整体流程异常时返回非 0
    - 存在 failed records 仍返回 0，因为这属于审计结果，不是运行时崩溃
    """
    configure_console_encoding()
    args = parse_args()
    config = build_config_from_args(args)
    configure_logging(config.log_level)

    try:
        migrator = dynamic_import_module(
            config.migration_script, "detail_migrator_dynamic"
        )
        mapping_rules = extract_mapping_rules_from_current_migrator(migrator)

        source_map, source_parse_warnings = load_source_js(config, migrator)
        target_map = load_target_json(config)

        fallback_module = (
            migrator.normalize_non_empty_string(config.source_js.stem)
            or "unknown_module"
        )

        per_record: dict[str, RecordVerification] = {}
        source_record_ids: list[str] = []
        for source_key, source_value in source_map.items():
            source_id = None
            if isinstance(source_value, dict):
                raw_id = source_value.get("id")
                source_id = (
                    raw_id if isinstance(raw_id, str) and raw_id.strip() else None
                )
            record_id = source_id or source_key
            source_record_ids.append(record_id)
            target_record = target_map.get(record_id)
            verification = verify_record_integrity(
                source_key=source_key,
                source=source_value,
                target_record=target_record,
                migrator=migrator,
                fallback_module=fallback_module,
            )
            per_record[record_id] = verification

        extra_target_ids = [
            rid for rid in target_map.keys() if rid not in set(source_record_ids)
        ]
        summary = summarize_results(
            source_map=source_map,
            target_map=target_map,
            per_record=per_record,
            extra_target_ids=extra_target_ids,
            mapping_rules=mapping_rules,
        )

        report = build_report(
            config=config,
            source_parse_warnings=source_parse_warnings,
            mapping_rules=mapping_rules,
            per_record=per_record,
            extra_target_ids=extra_target_ids,
            summary=summary,
        )
        write_json(config.report_json, report)
        write_markdown_report(config.report_md, report)

        LOGGER.info("校验完成")
        LOGGER.info("总记录数: %s", summary.total_source_records)
        LOGGER.info(
            "通过: %s | warning: %s | failed: %s",
            summary.passed_records,
            summary.warning_records,
            summary.failed_records,
        )
        LOGGER.info(
            "字段 warning: %s | 字段 failed: %s",
            summary.field_warning_count,
            summary.field_failed_count,
        )
        LOGGER.info("目标多余记录数: %s", summary.extra_in_target)
        LOGGER.info("JSON 报告: %s", config.report_json)
        LOGGER.info("Markdown 报告: %s", config.report_md)

        if config.strict and summary.failed_records > 0:
            LOGGER.warning(
                "strict 模式提示：检测到 failed records，请优先查看 migration_integrity_report.md"
            )

        return 0

    except Exception as exc:
        LOGGER.error("执行失败: %s", exc)
        LOGGER.debug("%s", traceback.format_exc())
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
