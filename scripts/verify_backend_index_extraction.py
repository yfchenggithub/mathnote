#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本名称: verify_backend_index_extraction.py

用途:
- 校验 `backend_search_index.json` 是否与 `search_bundle.js` 中的原始
  `searchBundle` 数据严格一致（结构、类型、值、数组顺序）。

校验思路:
1. 复用 `extract_backend_index_from_search_bundle.py` 的解析函数：
   `read_text_file`、`extract_search_bundle_object_literal`、
   `load_bundle_to_python_obj`。
2. source / backend 都解析为 Python 对象后，执行深度结构化比较。
3. 额外做统计一致性复核（actual vs stats）与 canonical SHA256 指纹比较。

输入输出:
- 输入:
  - `--bundle-js`（默认 `data/search_engine/search_bundle.js`）
  - `--backend-json`（默认 `data/search_engine/backend_search_index.json`）
- 输出:
  - 控制台日志（分步骤）
  - 可选 JSON 报告（`--report`）

退出码:
- 0: 完全一致
- 1: 发现不一致
- 2: 输入文件错误 / 解析失败 / 脚本异常

示例:
- python scripts/verify_backend_index_extraction.py
- python scripts/verify_backend_index_extraction.py --report reports/backend_index_verify_report.json
- python scripts/verify_backend_index_extraction.py --no-ignore-meta --log-level DEBUG
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from extract_backend_index_from_search_bundle import (  # noqa: E402
    ExtractionError,
    JsLiteralParseError,
    extract_search_bundle_object_literal,
    load_bundle_to_python_obj,
    read_text_file,
)

LOGGER = logging.getLogger("verify_backend_index_extraction")

DEFAULT_BUNDLE_JS = Path("data/search_engine/search_bundle.js")
DEFAULT_BACKEND_JSON = Path("data/search_engine/backend_search_index.json")

EXIT_OK = 0
EXIT_MISMATCH = 1
EXIT_ERROR = 2

ALLOWED_BACKEND_EXTRA_KEYS = {"meta", "_extractor_meta"}
TOP_LEVEL_CORE_FIELDS = (
    "version",
    "generatedAt",
    "stats",
    "buildOptions",
    "fieldMaskLegend",
    "docs",
    "termIndex",
    "prefixIndex",
    "suggestions",
)
BASIC_FIELDS = ("version", "generatedAt", "stats", "buildOptions", "fieldMaskLegend")
DOC_FOCUS_FIELDS = (
    "id",
    "module",
    "moduleDir",
    "title",
    "summary",
    "category",
    "tags",
    "coreFormula",
    "rank",
    "difficulty",
    "searchBoost",
    "hotScore",
    "examFrequency",
    "examScore",
)

_MISSING = object()


class VerificationInputError(RuntimeError):
    """输入文件不可用（不存在/不可读）时抛出。"""


class VerificationParseError(RuntimeError):
    """内容解析失败（JS/JSON）时抛出。"""


@dataclass
class DiffCollector:
    """差异收集器。

    做什么:
    - 记录差异总数；
    - 仅保留前 N 条差异样本，避免报告过大。
    """

    max_samples: int
    mismatch_count: int = 0
    mismatch_samples: list[dict[str, Any]] = field(default_factory=list)

    def add(
        self,
        category: str,
        path: str,
        message: str,
        source_value: Any = _MISSING,
        backend_value: Any = _MISSING,
    ) -> None:
        """追加一条差异。"""

        self.mismatch_count += 1
        if len(self.mismatch_samples) >= self.max_samples:
            return
        sample: dict[str, Any] = {
            "type": category,
            "path": path,
            "message": message,
        }
        if source_value is not _MISSING:
            sample["source"] = preview_value(source_value)
        if backend_value is not _MISSING:
            sample["backend"] = preview_value(backend_value)
        self.mismatch_samples.append(sample)


def preview_value(value: Any, max_len: int = 300) -> str:
    """把任意值转成适合日志/报告的短字符串。"""

    try:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    except TypeError:
        text = repr(value)
    if len(text) <= max_len:
        return text
    return f"{text[:max_len]} ... <truncated {len(text) - max_len} chars>"


def load_source_bundle(bundle_path: Path, encoding: str = "utf-8") -> dict[str, Any]:
    """读取并解析 source `search_bundle.js`。

    做什么:
    - 复用抽取脚本中的读取/对象抽取/JS 对象解析能力。

    为什么这样做:
    - 抽取与校验共用同一解析语义，避免双解析器差异。
    """

    if not bundle_path.is_file():
        raise VerificationInputError(f"source bundle 文件不存在或不是文件: {bundle_path}")

    try:
        js_text = read_text_file(bundle_path, encoding=encoding)
    except (FileNotFoundError, UnicodeDecodeError, OSError) as exc:
        raise VerificationInputError(f"读取 source bundle 失败: {bundle_path} ({exc})") from exc

    try:
        object_literal = extract_search_bundle_object_literal(js_text, "searchBundle")
        payload = load_bundle_to_python_obj(object_literal)
    except (ExtractionError, JsLiteralParseError, TypeError, ValueError) as exc:
        raise VerificationParseError(f"解析 source bundle 失败: {bundle_path} ({exc})") from exc

    if not isinstance(payload, dict):
        raise VerificationParseError(
            f"source searchBundle 顶层必须是对象，实际类型={type(payload).__name__}"
        )
    return payload


def load_backend_json(backend_path: Path, encoding: str = "utf-8") -> dict[str, Any]:
    """读取并解析 backend JSON。"""

    if not backend_path.is_file():
        raise VerificationInputError(f"backend JSON 文件不存在或不是文件: {backend_path}")

    try:
        text = read_text_file(backend_path, encoding=encoding)
    except (FileNotFoundError, UnicodeDecodeError, OSError) as exc:
        raise VerificationInputError(f"读取 backend JSON 失败: {backend_path} ({exc})") from exc

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise VerificationParseError(
            f"backend JSON 解析失败: {backend_path} (line={exc.lineno}, col={exc.colno}, {exc.msg})"
        ) from exc

    if not isinstance(payload, dict):
        raise VerificationParseError(
            f"backend JSON 顶层必须是对象，实际类型={type(payload).__name__}"
        )
    return payload


def normalize_payload_for_hash(payload: dict[str, Any], ignore_meta: bool) -> dict[str, Any]:
    """用于 hash 前的规范化：按需剔除顶层 `meta/_extractor_meta`。"""

    if not ignore_meta:
        return dict(payload)
    return {
        key: value
        for key, value in payload.items()
        if key not in ALLOWED_BACKEND_EXTRA_KEYS
    }


def canonical_sha256(payload: dict[str, Any], ignore_meta: bool) -> tuple[str, str]:
    """对规范化对象做 canonical JSON 序列化并计算 SHA256。"""

    normalized = normalize_payload_for_hash(payload, ignore_meta=ignore_meta)
    canonical_json = json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    return canonical_json, digest


def compare_strict_value(path: str, source: Any, backend: Any, diffs: DiffCollector) -> None:
    """严格比较两个对象。

    做什么:
    - dict: 比较 key 集合 + 递归比较值
    - list: 比较长度 + 严格顺序比较元素
    - 标量: 类型和值都必须一致

    策略:
    - 使用“严格对象一致”语义，`2` 与 `2.0` 判为不一致。
    """

    if type(source) is not type(backend):
        diffs.add(
            "type_mismatch",
            path,
            "类型不一致（严格策略，2 != 2.0）",
            type(source).__name__,
            type(backend).__name__,
        )
        return

    if isinstance(source, dict):
        source_keys = set(source.keys())
        backend_keys = set(backend.keys())
        for key in sorted(source_keys - backend_keys):
            diffs.add("missing_key", f"{path}.{key}", "backend 缺少字段", source_value=source[key])
        for key in sorted(backend_keys - source_keys):
            diffs.add(
                "extra_key",
                f"{path}.{key}",
                "backend 多出字段",
                backend_value=backend[key],
            )
        for key in sorted(source_keys & backend_keys):
            compare_strict_value(f"{path}.{key}", source[key], backend[key], diffs)
        return

    if isinstance(source, list):
        if len(source) != len(backend):
            diffs.add(
                "length_mismatch",
                path,
                "列表长度不一致（顺序敏感）",
                len(source),
                len(backend),
            )
        for idx in range(min(len(source), len(backend))):
            compare_strict_value(f"{path}[{idx}]", source[idx], backend[idx], diffs)
        return

    if source != backend:
        diffs.add("value_mismatch", path, "值不一致", source, backend)


def _encode_typed_value(value: Any) -> Any:
    """将值编码为“带类型信息”的结构，用于严格序列对齐。

    说明:
    - Python `==` 会把 `2 == 2.0` 视为 True，但本脚本要求严格类型一致。
    - 该编码用于生成稳定 token，确保 `int` 与 `float` 可区分。
    """

    if value is None:
        return {"t": "none"}
    if isinstance(value, bool):
        return {"t": "bool", "v": value}
    if isinstance(value, int):
        return {"t": "int", "v": value}
    if isinstance(value, float):
        return {"t": "float", "v": value}
    if isinstance(value, str):
        return {"t": "str", "v": value}
    if isinstance(value, list):
        return {"t": "list", "v": [_encode_typed_value(item) for item in value]}
    if isinstance(value, dict):
        return {
            "t": "dict",
            "v": {key: _encode_typed_value(value[key]) for key in sorted(value.keys())},
        }
    return {"t": type(value).__name__, "v": repr(value)}


def _strict_token(value: Any) -> str:
    """把任意值转成稳定 token（包含类型语义）。"""

    return json.dumps(
        _encode_typed_value(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _report_aligned_list_differences(
    *,
    source_list: list[Any],
    backend_list: list[Any],
    root_path: str,
    category_prefix: str,
    item_label: str,
    diffs: DiffCollector,
) -> None:
    """对列表做序列对齐差异报告，避免“删一条导致后续全错位”。

    做什么:
    - 使用 SequenceMatcher 基于严格 token 对齐；
    - 优先产出 `missing/extra`；
    - replace 段落报告为“变更项”，并补足多余 missing/extra。
    """

    source_tokens = [_strict_token(item) for item in source_list]
    backend_tokens = [_strict_token(item) for item in backend_list]
    matcher = difflib.SequenceMatcher(a=source_tokens, b=backend_tokens, autojunk=False)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue

        if tag == "delete":
            for i in range(i1, i2):
                diffs.add(
                    f"{category_prefix}_missing_item",
                    f"{root_path}[{i}]",
                    f"backend 缺少 1 条 {item_label}",
                    source_value=source_list[i],
                )
            continue

        if tag == "insert":
            for j in range(j1, j2):
                diffs.add(
                    f"{category_prefix}_extra_item",
                    f"{root_path}[{j}]",
                    f"backend 多出 1 条 {item_label}",
                    backend_value=backend_list[j],
                )
            continue

        # replace: 两边区间都有内容，按最短区间配对报告变更，再补充多余项
        overlap = min(i2 - i1, j2 - j1)
        for offset in range(overlap):
            si = i1 + offset
            bj = j1 + offset
            diffs.add(
                f"{category_prefix}_item_changed",
                f"{root_path}[{si}]",
                f"{item_label} 内容变更（序列对齐后）",
                source_value=source_list[si],
                backend_value=backend_list[bj],
            )

        for si in range(i1 + overlap, i2):
            diffs.add(
                f"{category_prefix}_missing_item",
                f"{root_path}[{si}]",
                f"backend 缺少 1 条 {item_label}",
                source_value=source_list[si],
            )
        for bj in range(j1 + overlap, j2):
            diffs.add(
                f"{category_prefix}_extra_item",
                f"{root_path}[{bj}]",
                f"backend 多出 1 条 {item_label}",
                backend_value=backend_list[bj],
            )


def compare_top_level_structure(
    source_payload: dict[str, Any],
    backend_payload: dict[str, Any],
    ignore_meta: bool,
    diffs: DiffCollector,
) -> None:
    """顶层结构校验。

    做什么:
    - 比较顶层 key 集合；
    - 默认允许 backend 顶层多出 `meta/_extractor_meta`。
    """

    source_keys = set(source_payload.keys())
    backend_keys = set(backend_payload.keys())

    effective_backend_keys = set(backend_keys)
    if ignore_meta:
        effective_backend_keys -= ALLOWED_BACKEND_EXTRA_KEYS

    for key in sorted(source_keys - effective_backend_keys):
        diffs.add("top_level_missing", f"$.{key}", "backend 缺少顶层字段")
    for key in sorted(effective_backend_keys - source_keys):
        diffs.add("top_level_extra", f"$.{key}", "backend 多出非白名单顶层字段")

    for key in TOP_LEVEL_CORE_FIELDS:
        if key not in source_payload:
            diffs.add("source_core_missing", f"$.{key}", "source 缺少核心字段")
        if key not in backend_payload:
            diffs.add("backend_core_missing", f"$.{key}", "backend 缺少核心字段")


def compare_basic_fields(
    source_payload: dict[str, Any],
    backend_payload: dict[str, Any],
    diffs: DiffCollector,
) -> None:
    """基础字段逐项校验。"""

    for key in BASIC_FIELDS:
        if key in source_payload and key in backend_payload:
            compare_strict_value(f"$.{key}", source_payload[key], backend_payload[key], diffs)


def compare_docs(source_docs: Any, backend_docs: Any, diffs: DiffCollector) -> None:
    """`docs` 深度校验。"""

    root = "$.docs"
    if not isinstance(source_docs, dict) or not isinstance(backend_docs, dict):
        diffs.add(
            "docs_type_mismatch",
            root,
            "docs 必须是对象",
            type(source_docs).__name__,
            type(backend_docs).__name__,
        )
        return

    source_ids = set(source_docs.keys())
    backend_ids = set(backend_docs.keys())
    for doc_id in sorted(source_ids - backend_ids):
        diffs.add("docs_missing_doc", f"{root}.{doc_id}", "backend 缺少 doc")
    for doc_id in sorted(backend_ids - source_ids):
        diffs.add("docs_extra_doc", f"{root}.{doc_id}", "backend 多出 doc")

    focus_set = set(DOC_FOCUS_FIELDS)
    for doc_id in sorted(source_ids & backend_ids):
        source_doc = source_docs[doc_id]
        backend_doc = backend_docs[doc_id]
        doc_path = f"{root}.{doc_id}"

        if not isinstance(source_doc, dict) or not isinstance(backend_doc, dict):
            diffs.add(
                "doc_type_mismatch",
                doc_path,
                "doc 必须是对象",
                type(source_doc).__name__,
                type(backend_doc).__name__,
            )
            continue

        source_fields = set(source_doc.keys())
        backend_fields = set(backend_doc.keys())
        for field_name in sorted(source_fields - backend_fields):
            diffs.add(
                "doc_field_missing",
                f"{doc_path}.{field_name}",
                "backend doc 缺少字段",
                source_value=source_doc[field_name],
            )
        for field_name in sorted(backend_fields - source_fields):
            diffs.add(
                "doc_field_extra",
                f"{doc_path}.{field_name}",
                "backend doc 多出字段",
                backend_value=backend_doc[field_name],
            )

        # 先比重点字段，再比其余字段，差异样本更利于排障。
        for field_name in DOC_FOCUS_FIELDS:
            if field_name in source_doc and field_name in backend_doc:
                compare_strict_value(
                    f"{doc_path}.{field_name}",
                    source_doc[field_name],
                    backend_doc[field_name],
                    diffs,
                )
        for field_name in sorted((source_fields & backend_fields) - focus_set):
            compare_strict_value(
                f"{doc_path}.{field_name}",
                source_doc[field_name],
                backend_doc[field_name],
                diffs,
            )


def compare_postings_index(
    index_name: str,
    source_index: Any,
    backend_index: Any,
    diffs: DiffCollector,
) -> None:
    """`termIndex` / `prefixIndex` 深度校验。"""

    root = f"$.{index_name}"
    if not isinstance(source_index, dict) or not isinstance(backend_index, dict):
        diffs.add(
            f"{index_name}_type_mismatch",
            root,
            f"{index_name} 必须是对象",
            type(source_index).__name__,
            type(backend_index).__name__,
        )
        return

    source_keys = set(source_index.keys())
    backend_keys = set(backend_index.keys())
    for term in sorted(source_keys - backend_keys):
        diffs.add(
            f"{index_name}_missing_term",
            f'{root}[{json.dumps(term, ensure_ascii=False)}]',
            "backend 缺少 key",
        )
    for term in sorted(backend_keys - source_keys):
        diffs.add(
            f"{index_name}_extra_term",
            f'{root}[{json.dumps(term, ensure_ascii=False)}]',
            "backend 多出 key",
        )

    labels = ("docId", "score", "fieldMask")
    for term in sorted(source_keys & backend_keys):
        source_postings = source_index[term]
        backend_postings = backend_index[term]
        term_path = f'{root}[{json.dumps(term, ensure_ascii=False)}]'

        if not isinstance(source_postings, list) or not isinstance(backend_postings, list):
            diffs.add(
                f"{index_name}_posting_list_type_mismatch",
                term_path,
                "posting 列表必须是数组",
                type(source_postings).__name__,
                type(backend_postings).__name__,
            )
            continue

        if len(source_postings) != len(backend_postings):
            # 关键修复: 长度不一致时采用序列对齐，避免后续全量错位误报。
            _report_aligned_list_differences(
                source_list=source_postings,
                backend_list=backend_postings,
                root_path=term_path,
                category_prefix=f"{index_name}_posting",
                item_label="posting 记录",
                diffs=diffs,
            )
            continue

        for idx in range(len(source_postings)):
            source_posting = source_postings[idx]
            backend_posting = backend_postings[idx]
            posting_path = f"{term_path}[{idx}]"

            if not isinstance(source_posting, list) or not isinstance(backend_posting, list):
                diffs.add(
                    f"{index_name}_posting_item_type_mismatch",
                    posting_path,
                    "posting 项必须是数组",
                    type(source_posting).__name__,
                    type(backend_posting).__name__,
                )
                continue

            if len(source_posting) != 3:
                diffs.add(
                    f"{index_name}_source_posting_shape_error",
                    posting_path,
                    "source posting 不是 [docId, score, fieldMask]",
                    source_value=source_posting,
                )
            if len(backend_posting) != 3:
                diffs.add(
                    f"{index_name}_backend_posting_shape_error",
                    posting_path,
                    "backend posting 不是 [docId, score, fieldMask]",
                    backend_value=backend_posting,
                )
            if len(source_posting) != len(backend_posting):
                diffs.add(
                    f"{index_name}_posting_item_length_mismatch",
                    posting_path,
                    "posting 项长度不一致",
                    len(source_posting),
                    len(backend_posting),
                )

            compare_len = min(len(source_posting), len(backend_posting), 3)
            for pos in range(compare_len):
                compare_strict_value(
                    f"{posting_path}.{labels[pos]}",
                    source_posting[pos],
                    backend_posting[pos],
                    diffs,
                )


def compare_suggestions(source_suggestions: Any, backend_suggestions: Any, diffs: DiffCollector) -> None:
    """`suggestions` 深度校验。"""

    root = "$.suggestions"
    if not isinstance(source_suggestions, list) or not isinstance(backend_suggestions, list):
        diffs.add(
            "suggestions_type_mismatch",
            root,
            "suggestions 必须是数组",
            type(source_suggestions).__name__,
            type(backend_suggestions).__name__,
        )
        return

    if len(source_suggestions) != len(backend_suggestions):
        _report_aligned_list_differences(
            source_list=source_suggestions,
            backend_list=backend_suggestions,
            root_path=root,
            category_prefix="suggestions",
            item_label="suggestion 记录",
            diffs=diffs,
        )
        return

    labels = ("displayText", "docId", "score")
    for idx in range(len(source_suggestions)):
        source_item = source_suggestions[idx]
        backend_item = backend_suggestions[idx]
        item_path = f"{root}[{idx}]"

        if not isinstance(source_item, list) or not isinstance(backend_item, list):
            diffs.add(
                "suggestions_item_type_mismatch",
                item_path,
                "suggestion 项必须是数组",
                type(source_item).__name__,
                type(backend_item).__name__,
            )
            continue

        if len(source_item) != 3:
            diffs.add(
                "suggestions_source_shape_error",
                item_path,
                "source suggestion 不是 [displayText, docId, score]",
                source_value=source_item,
            )
        if len(backend_item) != 3:
            diffs.add(
                "suggestions_backend_shape_error",
                item_path,
                "backend suggestion 不是 [displayText, docId, score]",
                backend_value=backend_item,
            )
        if len(source_item) != len(backend_item):
            diffs.add(
                "suggestions_item_length_mismatch",
                item_path,
                "suggestion 项长度不一致",
                len(source_item),
                len(backend_item),
            )

        compare_len = min(len(source_item), len(backend_item), 3)
        for pos in range(compare_len):
            compare_strict_value(
                f"{item_path}.{labels[pos]}",
                source_item[pos],
                backend_item[pos],
                diffs,
            )


def summarize_counts(payload: dict[str, Any]) -> dict[str, Any]:
    """汇总 actual 数量与 stats 声明值。"""

    actual = {
        "documents": len(payload["docs"]) if isinstance(payload.get("docs"), dict) else None,
        "terms": len(payload["termIndex"]) if isinstance(payload.get("termIndex"), dict) else None,
        "prefixes": len(payload["prefixIndex"]) if isinstance(payload.get("prefixIndex"), dict) else None,
        "suggestions": (
            len(payload["suggestions"]) if isinstance(payload.get("suggestions"), list) else None
        ),
    }

    declared = {"documents": None, "terms": None, "prefixes": None, "suggestions": None}
    stats_obj = payload.get("stats")
    if isinstance(stats_obj, dict):
        declared["documents"] = stats_obj.get("documents")
        declared["terms"] = stats_obj.get("terms")
        declared["prefixes"] = stats_obj.get("prefixes")
        declared["suggestions"] = stats_obj.get("suggestions")

    return {"actual": actual, "declared": declared}


def validate_stats_consistency(side: str, payload: dict[str, Any], diffs: DiffCollector) -> dict[str, Any]:
    """统计一致性复核（actual vs stats）。"""

    summary = summarize_counts(payload)
    actual = summary["actual"]
    declared = summary["declared"]
    consistent: dict[str, bool | None] = {}

    for metric in ("documents", "terms", "prefixes", "suggestions"):
        actual_value = actual.get(metric)
        declared_value = declared.get(metric)
        state: bool | None = None

        if actual_value is None:
            diffs.add(
                "stats_actual_invalid",
                f"$.{side}.actual.{metric}",
                f"{side} 的 `{metric}` 实际计数不可计算（字段类型异常）",
            )

        if not isinstance(declared_value, int):
            diffs.add(
                "stats_declared_type_error",
                f"$.{side}.stats.{metric}",
                f"{side} 的 `stats.{metric}` 不是 int",
                source_value=declared_value if side == "source" else _MISSING,
                backend_value=declared_value if side == "backend" else _MISSING,
            )
        elif isinstance(actual_value, int):
            state = declared_value == actual_value
            if not state:
                diffs.add(
                    "stats_value_mismatch",
                    f"$.{side}.stats.{metric}",
                    f"{side} 的 `stats.{metric}` 与实际数量不一致",
                    declared_value,
                    actual_value,
                )

        consistent[metric] = state

    summary["consistent"] = consistent
    return summary


def write_report_file(report_path: Path, report: dict[str, Any]) -> None:
    """写出 JSON 报告。"""

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)
        file.write("\n")


def build_report(
    passed: bool,
    bundle_path: Path,
    backend_path: Path,
    source_hash: str | None,
    backend_hash: str | None,
    source_stats: dict[str, Any] | None,
    backend_stats: dict[str, Any] | None,
    diffs: DiffCollector,
    ignore_meta: bool,
) -> dict[str, Any]:
    """构建结构化报告。"""

    summary = (
        "校验通过：source 与 backend 核心 payload 完全一致。"
        if passed
        else "校验失败：发现 source 与 backend 不一致。"
    )
    return {
        "passed": passed,
        "summary": summary,
        "source_bundle_path": str(bundle_path),
        "backend_json_path": str(backend_path),
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ignore_meta": ignore_meta,
        "source_hash": source_hash,
        "backend_hash": backend_hash,
        "stats": {"source": source_stats, "backend": backend_stats},
        "mismatch_count": diffs.mismatch_count,
        "mismatch_samples": diffs.mismatch_samples,
        "mismatch_samples_truncated": diffs.mismatch_count > len(diffs.mismatch_samples),
        "max_diff_samples": diffs.max_samples,
    }


def verify_payloads(
    source_payload: dict[str, Any],
    backend_payload: dict[str, Any],
    bundle_path: Path,
    backend_path: Path,
    ignore_meta: bool,
    max_diff_samples: int,
) -> dict[str, Any]:
    """执行完整校验流程。"""

    diffs = DiffCollector(max_samples=max_diff_samples)

    LOGGER.info("步骤 1/8: 顶层结构校验")
    compare_top_level_structure(source_payload, backend_payload, ignore_meta, diffs)

    LOGGER.info("步骤 2/8: 基础字段校验")
    compare_basic_fields(source_payload, backend_payload, diffs)

    LOGGER.info("步骤 3/8: docs 深度校验")
    compare_docs(source_payload.get("docs"), backend_payload.get("docs"), diffs)

    LOGGER.info("步骤 4/8: termIndex 深度校验")
    compare_postings_index("termIndex", source_payload.get("termIndex"), backend_payload.get("termIndex"), diffs)

    LOGGER.info("步骤 5/8: prefixIndex 深度校验")
    compare_postings_index("prefixIndex", source_payload.get("prefixIndex"), backend_payload.get("prefixIndex"), diffs)

    LOGGER.info("步骤 6/8: suggestions 深度校验")
    compare_suggestions(source_payload.get("suggestions"), backend_payload.get("suggestions"), diffs)

    LOGGER.info("步骤 7/8: 统计一致性复核")
    source_stats = validate_stats_consistency("source", source_payload, diffs)
    backend_stats = validate_stats_consistency("backend", backend_payload, diffs)

    LOGGER.info("步骤 8/8: 指纹校验")
    _, source_hash = canonical_sha256(source_payload, ignore_meta=ignore_meta)
    _, backend_hash = canonical_sha256(backend_payload, ignore_meta=ignore_meta)
    if source_hash != backend_hash and diffs.mismatch_count == 0:
        diffs.add(
            "hash_mismatch",
            "$.payload_sha256",
            "规范化 payload SHA256 不一致",
            source_hash,
            backend_hash,
        )

    return build_report(
        passed=diffs.mismatch_count == 0,
        bundle_path=bundle_path,
        backend_path=backend_path,
        source_hash=source_hash,
        backend_hash=backend_hash,
        source_stats=source_stats,
        backend_stats=backend_stats,
        diffs=diffs,
        ignore_meta=ignore_meta,
    )


def positive_int(value: str) -> int:
    """argparse 参数类型：正整数。"""

    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("必须是正整数")
    return parsed


def build_arg_parser() -> argparse.ArgumentParser:
    """构建 CLI 参数解析器。"""

    parser = argparse.ArgumentParser(
        description="验证 backend_search_index.json 是否与 search_bundle.js 中的 searchBundle 严格一致。"
    )
    parser.add_argument(
        "--bundle-js",
        type=Path,
        default=DEFAULT_BUNDLE_JS,
        help=f"source bundle 路径，默认: {DEFAULT_BUNDLE_JS}",
    )
    parser.add_argument(
        "--backend-json",
        type=Path,
        default=DEFAULT_BACKEND_JSON,
        help=f"backend JSON 路径，默认: {DEFAULT_BACKEND_JSON}",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="可选 JSON 报告路径，例如: reports/backend_index_verify_report.json",
    )
    parser.add_argument(
        "--max-diff-samples",
        type=positive_int,
        default=50,
        help="最多保留前 N 条差异样本，默认 50",
    )
    parser.add_argument(
        "--ignore-meta",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="是否忽略 backend 顶层 `meta/_extractor_meta` 差异（默认开启）",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="日志级别，默认 INFO",
    )
    return parser


def log_mismatch_samples(report: dict[str, Any]) -> None:
    """输出差异样本到控制台日志。"""

    for idx, sample in enumerate(report.get("mismatch_samples", []), start=1):
        parts = [
            f"[差异 {idx}]",
            f"type={sample.get('type')}",
            f"path={sample.get('path')}",
            f"message={sample.get('message')}",
        ]
        if "source" in sample:
            parts.append(f"source={sample['source']}")
        if "backend" in sample:
            parts.append(f"backend={sample['backend']}")
        LOGGER.error(" | ".join(parts))


def write_error_report_if_needed(
    report_path: Path | None,
    bundle_path: Path,
    backend_path: Path,
    summary: str,
    ignore_meta: bool,
) -> None:
    """在输入/解析错误时写最小化报告（可选）。"""

    if report_path is None:
        return
    write_report_file(
        report_path,
        {
            "passed": False,
            "summary": summary,
            "source_bundle_path": str(bundle_path),
            "backend_json_path": str(backend_path),
            "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "ignore_meta": ignore_meta,
            "source_hash": None,
            "backend_hash": None,
            "stats": None,
            "mismatch_count": 0,
            "mismatch_samples": [],
            "error": True,
        },
    )


def main(argv: list[str] | None = None) -> int:
    """CLI 主入口。"""

    parser = build_arg_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    try:
        LOGGER.info("开始校验 backend 索引抽取一致性")
        LOGGER.info("source bundle: %s", args.bundle_js)
        LOGGER.info("backend json : %s", args.backend_json)
        LOGGER.info("ignore meta  : %s", args.ignore_meta)

        source_payload = load_source_bundle(args.bundle_js)
        backend_payload = load_backend_json(args.backend_json)

        report = verify_payloads(
            source_payload=source_payload,
            backend_payload=backend_payload,
            bundle_path=args.bundle_js,
            backend_path=args.backend_json,
            ignore_meta=args.ignore_meta,
            max_diff_samples=args.max_diff_samples,
        )

        LOGGER.info(
            "统计摘要 | source actual=%s | backend actual=%s",
            preview_value(report["stats"]["source"]["actual"]),
            preview_value(report["stats"]["backend"]["actual"]),
        )
        LOGGER.info(
            "指纹摘要 | source=%s | backend=%s",
            report.get("source_hash"),
            report.get("backend_hash"),
        )

        if args.report is not None:
            write_report_file(args.report, report)
            LOGGER.info("已写出 JSON 报告: %s", args.report)

        if report.get("passed"):
            LOGGER.info("校验通过：未发现不一致。")
            return EXIT_OK

        LOGGER.error(
            "校验失败：共发现 %d 处不一致（展示前 %d 条）。",
            report.get("mismatch_count", 0),
            len(report.get("mismatch_samples", [])),
        )
        log_mismatch_samples(report)
        return EXIT_MISMATCH

    except VerificationInputError as exc:
        LOGGER.error("输入文件错误: %s", exc)
        write_error_report_if_needed(
            report_path=args.report,
            bundle_path=args.bundle_js,
            backend_path=args.backend_json,
            summary=f"输入文件错误: {exc}",
            ignore_meta=args.ignore_meta,
        )
        return EXIT_ERROR
    except VerificationParseError as exc:
        LOGGER.error("解析失败: %s", exc)
        write_error_report_if_needed(
            report_path=args.report,
            bundle_path=args.bundle_js,
            backend_path=args.backend_json,
            summary=f"解析失败: {exc}",
            ignore_meta=args.ignore_meta,
        )
        return EXIT_ERROR
    except Exception as exc:
        LOGGER.exception("脚本异常: %s", exc)
        write_error_report_if_needed(
            report_path=args.report,
            bundle_path=args.bundle_js,
            backend_path=args.backend_json,
            summary=f"脚本异常: {exc}",
            ignore_meta=args.ignore_meta,
        )
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
