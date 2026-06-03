#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
脚本名称: sync_backend_core_formula_assets.py

用途
----
把 `backend_search_index.json` 中 `docs[*].coreFormula` 的纯 LaTeX 字符串
同步升级为公式图片节点：

    "coreFormula": "\\frac{a+b}{2}"

变为：

    "coreFormula": {
      "latex": "\\frac{a+b}{2}",
      "type": "math_image",
      "asset": {
        "png": "/static/formulas/I006/xxxx@3x.png",
        "webp": "/static/formulas/I006/xxxx@3x.webp",
        "width_px": 403,
        "height_px": 137,
        "display_width_px": 134,
        "display_height_px": 46,
        "scale": 3
      }
    }

使用背景
--------
`backend_search_index.json` 是搜索索引，里面的 `coreFormula` 原本是搜索结果
展示用的轻量字符串；`canonical_content_v2.json` 是详情页数据，已经通过
`render_math_assets.mjs` 把公式渲染为 `math_image` 节点并生成 PNG/WebP 资产。

如果再把 backend JSON 送进渲染脚本重新生成图片，会带来两个问题：
1. backend 不是详情页 token 树，缺少 `math_block` / `math_inline` / `primary_formula`
   这类渲染脚本识别的结构。
2. 即使人为改造成可渲染结构，也可能生成第二套资产或和详情页图片信息漂移。

为什么这样做
------------
本脚本只做“资产同步”，不做“公式渲染”：
1. 以 `canonical_content_v2.json` 为图片资产真源。
2. 按结论 ID 与 LaTeX 内容精确匹配已经存在的 `math_image` 节点。
3. 把匹配到的 `latex/type/asset` 回填到 backend 的 `coreFormula`。
4. 保留 `termIndex`、`prefixIndex`、`suggestions` 等搜索索引结构不变。

这样可以保证搜索结果使用的公式图片与详情页完全一致，并避免重复渲染。

工作方式
--------
A. 读取 canonical JSON，递归扫描每个结论 ID 作用域下的 `math_image` 节点。
B. 建立索引：`结论ID + latex.strip()` -> `{latex, type, asset}`。
C. 读取 backend JSON，遍历 `docs` 中每条文档的 `coreFormula`。
D. 对非空 `coreFormula`：
   - 若是字符串，则用该字符串作为待匹配 LaTeX；
   - 若已经是对象，则用对象中的 `latex` 作为待匹配 LaTeX，便于重复执行同步；
   - 找到 canonical 图片资产后，写成 `{latex, type: "math_image", asset}`。
E. 空字符串保持不变，因为没有可展示图片。

默认安全策略
------------
- 默认是 DRY-RUN，不写 backend JSON。需要真正写入时显式加 `--write`。
- 默认只使用“同一 ID + 相同 latex.strip()”的精确匹配。
- 如果确实希望在 LaTeX 不完全相同时仍按 ID 使用 canonical 的 `primary_formula`，
  可加 `--allow-primary-fallback`，但建议先查看报告确认没有错配风险。
- 脚本会输出 JSON 报告，列出已转换、已同步、空公式、缺失匹配、格式异常等统计。

输入输出
--------
输入:
- `--backend-json`:
  默认 `data/search_engine/backend_search_index.json`
- `--canonical-json`:
  默认 `data/content/canonical_content_v2.json`

输出:
- backend JSON:
  默认原地覆盖 `--backend-json`，但只有加 `--write` 才会写入。
- 报告:
  默认 `reports/sync_backend_core_formula_assets_report.json`

用法示例
--------
1) 先演练，查看统计和报告，不修改文件：

   python scripts/sync_backend_core_formula_assets.py

2) 确认报告后原地写入 backend JSON：

   python scripts/sync_backend_core_formula_assets.py --write

3) 写到临时文件，便于人工 diff：

   python scripts/sync_backend_core_formula_assets.py \\
     --output data/search_engine/backend_search_index.with_core_formula_assets.json \\
     --write

4) 严格模式：如果非空 coreFormula 找不到对应图片资产，则返回非 0：

   python scripts/sync_backend_core_formula_assets.py --strict

5) 允许 ID 兜底：精确 LaTeX 匹配失败时，使用同 ID 的 primary_formula 图片：

   python scripts/sync_backend_core_formula_assets.py --allow-primary-fallback

建议运行顺序
------------
先完成详情页图片生成，再同步 backend：

    python scripts/build_backend_and_canonical.py --module 07_inequality
    python scripts/mark_need_image_by_latex_length.py --min-length 5
    node scripts/render_math_assets.mjs --in-place
    python scripts/remove_math_image_following_period.py --write
    python scripts/sync_backend_core_formula_assets.py --write

注意事项
--------
- 本脚本会改变 `docs[*].coreFormula` 的类型：从 string 变为 object。
  搜索结果展示代码需要支持这种新结构。
- 如果还要验证 `backend_search_index.json` 与 `search_bundle.js` 的原始抽取一致性，
  应先运行 `verify_backend_index_extraction.py`，再运行本脚本做展示字段升级。
"""

from __future__ import annotations

import argparse
import codecs
import copy
import json
import logging
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_BACKEND_JSON = Path("data/search_engine/backend_search_index.json")
DEFAULT_CANONICAL_JSON = Path("data/content/canonical_content_v2.json")
DEFAULT_REPORT = Path("reports/sync_backend_core_formula_assets_report.json")
MATH_IMAGE_TYPE = "math_image"

LOGGER = logging.getLogger("sync_backend_core_formula_assets")


@dataclass
class FormulaAssetNode:
    """canonical 中可同步到 backend 的公式图片节点。"""

    conclusion_id: str
    latex: str
    asset: dict[str, Any]
    path: str
    source: str


@dataclass
class SyncStats:
    """同步统计。"""

    backend_docs_seen: int = 0
    canonical_image_nodes_seen: int = 0
    canonical_primary_images_seen: int = 0
    core_formula_string_seen: int = 0
    core_formula_object_seen: int = 0
    empty_core_formula_skipped: int = 0
    converted: int = 0
    already_synced: int = 0
    refreshed_existing_object: int = 0
    missing_asset: int = 0
    malformed_core_formula: int = 0
    fallback_primary_used: int = 0


@dataclass
class SyncReport:
    """写入报告文件的结构。"""

    generated_at: str
    mode: str
    backend_json: str
    canonical_json: str
    output: str
    allow_primary_fallback: bool
    strict: bool
    stats: dict[str, int]
    items: list[dict[str, Any]] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Sync docs[*].coreFormula in backend_search_index.json from "
            "rendered math_image assets in canonical_content_v2.json."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/sync_backend_core_formula_assets.py\n"
            "  python scripts/sync_backend_core_formula_assets.py --write\n"
            "  python scripts/sync_backend_core_formula_assets.py --strict\n"
            "  python scripts/sync_backend_core_formula_assets.py "
            "--allow-primary-fallback --write\n"
        ),
    )
    parser.add_argument(
        "--backend-json",
        default=str(DEFAULT_BACKEND_JSON),
        help=f"backend JSON path (default: {DEFAULT_BACKEND_JSON})",
    )
    parser.add_argument(
        "--canonical-json",
        default=str(DEFAULT_CANONICAL_JSON),
        help=f"canonical JSON path (default: {DEFAULT_CANONICAL_JSON})",
    )
    parser.add_argument(
        "--output",
        default=None,
        help=(
            "Output backend JSON path. If omitted, output path is --backend-json. "
            "Only written when --write is set."
        ),
    )
    parser.add_argument(
        "--report",
        default=str(DEFAULT_REPORT),
        help=f"Report JSON path (default: {DEFAULT_REPORT})",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write backend JSON. Default is dry-run preview only.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Return non-zero when any non-empty coreFormula cannot be matched "
            "to a canonical math_image asset."
        ),
    )
    parser.add_argument(
        "--allow-primary-fallback",
        action="store_true",
        help=(
            "If exact latex match fails, use the same conclusion ID's "
            "canonical primary_formula image when available."
        ),
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="Logging level (default: INFO).",
    )
    return parser.parse_args()


def configure_logging(level_name: str) -> None:
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")


def read_json_with_style(path: Path) -> tuple[Any, bool, str]:
    raw = path.read_bytes()
    has_bom = raw.startswith(codecs.BOM_UTF8)
    newline = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8-sig")
    return json.loads(text), has_bom, newline


def dump_json_text(data: Any, newline: str) -> str:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if newline != "\n":
        text = text.replace("\n", newline)
    if not text.endswith(newline):
        text += newline
    return text


def write_json_with_style(
    path: Path,
    data: Any,
    *,
    has_bom: bool,
    newline: str,
) -> None:
    payload = dump_json_text(data, newline).encode("utf-8")
    if has_bom:
        payload = codecs.BOM_UTF8 + payload
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def save_report(path: Path, report: SyncReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(report), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def normalize_latex(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()


def normalize_type(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().lower()


def format_json_path(parts: list[str | int]) -> str:
    output = "$"
    for part in parts:
        if isinstance(part, int):
            output += f"[{part}]"
            continue
        if part.isidentifier():
            output += f".{part}"
            continue
        escaped = part.replace("\\", "\\\\").replace('"', '\\"')
        output += f'["{escaped}"]'
    return output


def is_math_image_node(node: Any) -> bool:
    if not isinstance(node, dict):
        return False
    if normalize_type(node.get("type")) != MATH_IMAGE_TYPE:
        return False
    if not isinstance(node.get("latex"), str):
        return False
    return isinstance(node.get("asset"), dict)


def build_formula_node(node: dict[str, Any], *, path: str, source: str) -> FormulaAssetNode:
    return FormulaAssetNode(
        conclusion_id="",
        latex=node["latex"],
        asset=copy.deepcopy(node["asset"]),
        path=path,
        source=source,
    )


def collect_canonical_formula_assets(
    canonical: Any,
    *,
    stats: SyncStats,
) -> tuple[dict[str, dict[str, FormulaAssetNode]], dict[str, FormulaAssetNode]]:
    by_id_and_latex: dict[str, dict[str, FormulaAssetNode]] = {}
    primary_by_id: dict[str, FormulaAssetNode] = {}

    def add_node(conclusion_id: str, node: dict[str, Any], path: str, source: str) -> None:
        normalized = normalize_latex(node.get("latex"))
        if not normalized:
            return

        formula = build_formula_node(node, path=path, source=source)
        formula.conclusion_id = conclusion_id

        by_latex = by_id_and_latex.setdefault(conclusion_id, {})
        by_latex.setdefault(normalized, formula)

        stats.canonical_image_nodes_seen += 1
        if source == "primary_formula":
            stats.canonical_primary_images_seen += 1
            primary_by_id.setdefault(conclusion_id, formula)

    def walk(node: Any, path: list[str | int], context_id: str | None) -> None:
        if isinstance(node, list):
            for index, item in enumerate(node):
                walk(item, path + [index], context_id)
            return

        if not isinstance(node, dict):
            return

        next_context_id = context_id
        node_id = node.get("id")
        if isinstance(node_id, str) and node_id.strip():
            next_context_id = node_id.strip()

        if next_context_id and is_math_image_node(node):
            add_node(
                next_context_id,
                node,
                format_json_path(path),
                "math_image",
            )

        primary_formula = node.get("primary_formula")
        if next_context_id and is_math_image_node(primary_formula):
            add_node(
                next_context_id,
                primary_formula,
                format_json_path(path + ["primary_formula"]),
                "primary_formula",
            )

        for key, value in node.items():
            if key == "primary_formula":
                continue
            walk(value, path + [str(key)], next_context_id)

    walk(canonical, [], None)
    return by_id_and_latex, primary_by_id


def get_core_formula_latex(value: Any) -> tuple[str, str]:
    if isinstance(value, str):
        return value, "string"
    if isinstance(value, dict) and isinstance(value.get("latex"), str):
        return value["latex"], "object"
    return "", "malformed"


def make_backend_core_formula(formula: FormulaAssetNode) -> dict[str, Any]:
    return {
        "latex": formula.latex,
        "type": MATH_IMAGE_TYPE,
        "asset": copy.deepcopy(formula.asset),
    }


def sync_backend_core_formulas(
    backend: Any,
    by_id_and_latex: dict[str, dict[str, FormulaAssetNode]],
    primary_by_id: dict[str, FormulaAssetNode],
    *,
    allow_primary_fallback: bool,
    stats: SyncStats,
) -> list[dict[str, Any]]:
    if not isinstance(backend, dict):
        raise TypeError("backend JSON root must be an object")

    docs = backend.get("docs")
    if not isinstance(docs, dict):
        raise TypeError("backend JSON must contain object field: docs")

    report_items: list[dict[str, Any]] = []
    stats.backend_docs_seen = len(docs)

    for doc_id in sorted(docs):
        doc = docs[doc_id]
        if not isinstance(doc, dict):
            stats.malformed_core_formula += 1
            report_items.append(
                {
                    "doc_id": doc_id,
                    "status": "malformed_doc",
                    "message": "docs entry is not an object",
                }
            )
            continue

        raw_value = doc.get("coreFormula", "")
        latex, value_kind = get_core_formula_latex(raw_value)
        normalized = normalize_latex(latex)

        if value_kind == "string":
            stats.core_formula_string_seen += 1
        elif value_kind == "object":
            stats.core_formula_object_seen += 1
        else:
            stats.malformed_core_formula += 1
            report_items.append(
                {
                    "doc_id": doc_id,
                    "status": "malformed_core_formula",
                    "message": "coreFormula must be a string or an object with latex",
                    "value_type": type(raw_value).__name__,
                }
            )
            continue

        if not normalized:
            stats.empty_core_formula_skipped += 1
            report_items.append(
                {
                    "doc_id": doc_id,
                    "status": "empty_skipped",
                    "message": "empty coreFormula is kept unchanged",
                }
            )
            continue

        formula = by_id_and_latex.get(doc_id, {}).get(normalized)
        match_kind = "exact_latex"

        if formula is None and allow_primary_fallback:
            formula = primary_by_id.get(doc_id)
            if formula is not None:
                match_kind = "primary_formula_fallback"
                stats.fallback_primary_used += 1

        if formula is None:
            stats.missing_asset += 1
            report_items.append(
                {
                    "doc_id": doc_id,
                    "status": "missing_asset",
                    "latex": latex,
                    "message": (
                        "no canonical math_image asset found for same doc ID "
                        "and latex.strip()"
                    ),
                }
            )
            continue

        new_value = make_backend_core_formula(formula)
        if raw_value == new_value:
            stats.already_synced += 1
            status = "already_synced"
        else:
            doc["coreFormula"] = new_value
            if value_kind == "object":
                stats.refreshed_existing_object += 1
                status = "refreshed_existing_object"
            else:
                stats.converted += 1
                status = "converted"

        item: dict[str, Any] = {
            "doc_id": doc_id,
            "status": status,
            "match": match_kind,
            "canonical_path": formula.path,
            "canonical_source": formula.source,
            "latex": formula.latex,
            "asset": formula.asset,
        }
        if match_kind == "primary_formula_fallback":
            item["backend_latex"] = latex
        report_items.append(item)

    return report_items


def print_summary(
    *,
    mode: str,
    backend_path: Path,
    canonical_path: Path,
    output_path: Path,
    report_path: Path,
    stats: SyncStats,
) -> None:
    print(f"[{mode}] backend   : {backend_path}")
    print(f"[{mode}] canonical : {canonical_path}")
    print(f"[{mode}] output    : {output_path}")
    print(f"[{mode}] report    : {report_path}")
    print(f"[{mode}] backend_docs_seen          : {stats.backend_docs_seen}")
    print(
        f"[{mode}] canonical_image_nodes_seen : "
        f"{stats.canonical_image_nodes_seen}"
    )
    print(
        f"[{mode}] canonical_primary_images   : "
        f"{stats.canonical_primary_images_seen}"
    )
    print(f"[{mode}] core_formula_string_seen   : {stats.core_formula_string_seen}")
    print(f"[{mode}] core_formula_object_seen   : {stats.core_formula_object_seen}")
    print(f"[{mode}] converted                  : {stats.converted}")
    print(f"[{mode}] already_synced             : {stats.already_synced}")
    print(
        f"[{mode}] refreshed_existing_object  : "
        f"{stats.refreshed_existing_object}"
    )
    print(
        f"[{mode}] empty_core_formula_skipped : "
        f"{stats.empty_core_formula_skipped}"
    )
    print(f"[{mode}] missing_asset              : {stats.missing_asset}")
    print(f"[{mode}] malformed_core_formula     : {stats.malformed_core_formula}")
    print(f"[{mode}] fallback_primary_used      : {stats.fallback_primary_used}")


def main() -> int:
    args = parse_args()
    configure_logging(str(args.log_level))

    backend_path = Path(str(args.backend_json)).resolve()
    canonical_path = Path(str(args.canonical_json)).resolve()
    output_path = Path(str(args.output)).resolve() if args.output else backend_path
    report_path = Path(str(args.report)).resolve()
    mode = "WRITE" if args.write else "DRY-RUN"

    if not backend_path.exists():
        raise FileNotFoundError(f"backend JSON not found: {backend_path}")
    if not canonical_path.exists():
        raise FileNotFoundError(f"canonical JSON not found: {canonical_path}")

    backend, has_bom, newline = read_json_with_style(backend_path)
    canonical, _, _ = read_json_with_style(canonical_path)

    stats = SyncStats()
    by_id_and_latex, primary_by_id = collect_canonical_formula_assets(
        canonical,
        stats=stats,
    )
    items = sync_backend_core_formulas(
        backend,
        by_id_and_latex,
        primary_by_id,
        allow_primary_fallback=bool(args.allow_primary_fallback),
        stats=stats,
    )

    report = SyncReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        mode=mode,
        backend_json=str(backend_path),
        canonical_json=str(canonical_path),
        output=str(output_path),
        allow_primary_fallback=bool(args.allow_primary_fallback),
        strict=bool(args.strict),
        stats=asdict(stats),
        items=items,
    )
    save_report(report_path, report)

    if args.write:
        write_json_with_style(output_path, backend, has_bom=has_bom, newline=newline)
        LOGGER.info("Wrote synced backend JSON: %s", output_path)
    else:
        LOGGER.info("Dry-run mode: backend JSON was not written.")

    print_summary(
        mode=mode,
        backend_path=backend_path,
        canonical_path=canonical_path,
        output_path=output_path,
        report_path=report_path,
        stats=stats,
    )

    if args.strict and (stats.missing_asset > 0 or stats.malformed_core_formula > 0):
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - CLI guard
        LOGGER.error("%s", exc)
        raise SystemExit(2)
