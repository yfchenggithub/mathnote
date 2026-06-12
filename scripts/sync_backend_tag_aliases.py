#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ensure doc IDs are present in backend_search_index.json tags.

This is a small patching tool for already-built backend indexes. It scans
existing docs and ensures every conclusion has its own ID in docs[docId].tags,
then updates the exact posting index needed for search.

Example:
    python scripts/sync_backend_tag_aliases.py

Existing tags/postings are skipped, so it can be rerun after incremental
publish jobs. Explicit DOC_ID:TAG pairs are still accepted for rare aliases.
"""

from __future__ import annotations

import argparse
import codecs
import copy
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DEFAULT_BACKEND_INDEX = PROJECT_ROOT / "data" / "search_engine" / "backend_search_index.json"

TAG_FIELD_NAME = "tag"
TAG_FIELD_WEIGHT = 44
TAG_PREFIX_RATIO = 0.70

WHITESPACE_RE = re.compile(r"\s+")
PAIR_SPLIT_RE = re.compile(r"[,:;]\s*(?=[A-Za-z0-9_-]+\s*[:=])")
ID_TAG_RE = re.compile(r"^[A-Za-z]\d{3}$")


@dataclass
class JsonStyle:
    has_bom: bool = False
    newline: str = "\n"


@dataclass(frozen=True)
class AliasPair:
    doc_id: str
    tag: str


def iso_now() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def read_json_with_style(path: Path) -> tuple[Any, JsonStyle]:
    raw = path.read_bytes()
    style = JsonStyle(
        has_bom=raw.startswith(codecs.BOM_UTF8),
        newline="\r\n" if b"\r\n" in raw else "\n",
    )
    return json.loads(raw.decode("utf-8-sig")), style


def dumps_json(payload: Any, style: JsonStyle) -> bytes:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if style.newline != "\n":
        text = text.replace("\n", style.newline)
    if not text.endswith(style.newline):
        text += style.newline
    data = text.encode("utf-8")
    return codecs.BOM_UTF8 + data if style.has_bom else data


def write_json(path: Path, payload: Any, style: JsonStyle) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(dumps_json(payload, style))


def normalize_display(text: str) -> str:
    return WHITESPACE_RE.sub(" ", unicodedata.normalize("NFKC", text)).strip()


def normalize_text(text: str) -> str:
    text = normalize_display(text).lower()
    return text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")


def normalize_compact(text: str) -> str:
    return WHITESPACE_RE.sub("", text)


def dedupe(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        text = normalize_display(str(item))
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def parse_pair(text: str) -> AliasPair:
    raw = text.strip()
    if not raw:
        raise ValueError("empty alias pair")
    if ":" in raw:
        left, right = raw.split(":", 1)
    elif "=" in raw:
        left, right = raw.split("=", 1)
    else:
        raise ValueError(f"alias pair must be DOC_ID:TAG or DOC_ID=TAG: {text}")
    doc_id = normalize_display(left).upper()
    tag = normalize_display(right)
    if not doc_id or not tag:
        raise ValueError(f"alias pair has empty side: {text}")
    return AliasPair(doc_id=doc_id, tag=tag)


def parse_pairs(values: list[str]) -> list[AliasPair]:
    pairs: list[AliasPair] = []
    for value in values:
        parts = [part for part in PAIR_SPLIT_RE.split(value) if part.strip()]
        for part in parts or [value]:
            pairs.append(parse_pair(part))
    return dedupe_pairs(pairs)


def dedupe_pairs(pairs: Iterable[AliasPair]) -> list[AliasPair]:
    seen: set[tuple[str, str]] = set()
    result: list[AliasPair] = []
    for pair in pairs:
        key = (pair.doc_id, pair.tag)
        if key in seen:
            continue
        seen.add(key)
        result.append(pair)
    return result


def load_mapping(path: Path) -> list[AliasPair]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    pairs: list[AliasPair] = []
    if isinstance(payload, dict):
        for doc_id, tags in payload.items():
            if isinstance(tags, str):
                tags = [tags]
            if not isinstance(tags, list):
                raise ValueError(f"mapping value must be string or list: {doc_id}")
            for tag in tags:
                pairs.append(AliasPair(normalize_display(str(doc_id)).upper(), normalize_display(str(tag))))
    elif isinstance(payload, list):
        for row in payload:
            if isinstance(row, dict):
                doc_id = row.get("doc_id", row.get("docId", row.get("id")))
                tag = row.get("tag", row.get("alias"))
                pairs.append(AliasPair(normalize_display(str(doc_id)).upper(), normalize_display(str(tag))))
            elif isinstance(row, str):
                pairs.append(parse_pair(row))
            else:
                raise ValueError("mapping list items must be objects or pair strings")
    else:
        raise ValueError("mapping JSON must be an object or a list")
    return dedupe_pairs(pair for pair in pairs if pair.doc_id and pair.tag)


def doc_rank(docs: dict[str, Any], doc_id: str) -> int:
    doc = docs.get(doc_id)
    if not isinstance(doc, dict):
        return 0
    try:
        return int(doc.get("rank") or 0)
    except (TypeError, ValueError):
        return 0


def posting_doc_id(row: Any) -> str:
    if isinstance(row, list) and row:
        return str(row[0])
    return ""


def posting_score(row: Any) -> int:
    if isinstance(row, list) and len(row) > 1:
        try:
            return int(row[1])
        except (TypeError, ValueError):
            return 0
    return 0


def posting_mask(row: Any) -> int:
    if isinstance(row, list) and len(row) > 2:
        try:
            return int(row[2])
        except (TypeError, ValueError):
            return 0
    return 0


def sort_postings(rows: list[Any], docs: dict[str, Any], limit: int | None = None) -> list[Any]:
    filtered = [row for row in rows if isinstance(row, list) and len(row) >= 3]
    filtered.sort(
        key=lambda row: (
            -posting_score(row),
            -doc_rank(docs, posting_doc_id(row)),
            posting_doc_id(row),
        )
    )
    return filtered[:limit] if limit is not None else filtered


def upsert_posting(
    index: dict[str, Any],
    term: str,
    doc_id: str,
    score: int,
    field_mask: int,
    docs: dict[str, Any],
    *,
    limit: int | None = None,
) -> str:
    rows = index.setdefault(term, [])
    if not isinstance(rows, list):
        rows = []
        index[term] = rows

    for row in rows:
        if posting_doc_id(row) != doc_id:
            continue
        current_mask = posting_mask(row)
        if current_mask & field_mask:
            index[term] = sort_postings(rows, docs, limit=limit)
            return "already_present"
        row[1] = posting_score(row) + score
        row[2] = current_mask | field_mask
        index[term] = sort_postings(rows, docs, limit=limit)
        return "field_mask_added"

    rows.append([doc_id, score, field_mask])
    index[term] = sort_postings(rows, docs, limit=limit)
    return "posting_added"


def remove_posting_field(
    index: dict[str, Any],
    term: str,
    doc_id: str,
    score: int,
    field_mask: int,
    docs: dict[str, Any],
    *,
    limit: int | None = None,
) -> str:
    rows = index.get(term)
    if not isinstance(rows, list):
        return "already_absent"

    for row in list(rows):
        if posting_doc_id(row) != doc_id:
            continue
        current_mask = posting_mask(row)
        if not (current_mask & field_mask):
            return "already_absent"
        new_mask = current_mask & ~field_mask
        if new_mask:
            row[1] = max(0, posting_score(row) - score)
            row[2] = new_mask
            if posting_score(row) <= 0:
                rows.remove(row)
        else:
            rows.remove(row)
        if rows:
            index[term] = sort_postings(rows, docs, limit=limit)
        else:
            index.pop(term, None)
        return "removed"

    return "already_absent"


def latin_prefix_terms(term: str) -> list[str]:
    compact = normalize_compact(term)
    if len(compact) < 2:
        return []
    max_len = min(len(compact), 16)
    return [compact[:size] for size in range(2, max_len + 1)]


def ensure_doc_tag(doc: dict[str, Any], tag: str) -> str:
    raw_tags = doc.get("tags")
    if not isinstance(raw_tags, list):
        raw_tags = []
        doc["tags"] = raw_tags
    tags = dedupe(str(item) for item in raw_tags)
    if tags != raw_tags:
        doc["tags"] = tags
    if tag in tags:
        return "already_present"
    tags.append(tag)
    doc["tags"] = tags
    return "tag_added"


def apply_aliases(payload: dict[str, Any], pairs: list[AliasPair]) -> tuple[dict[str, Any], bool]:
    docs = payload.get("docs")
    term_index = payload.get("termIndex")
    prefix_index = payload.get("prefixIndex")
    field_mask_legend = payload.get("fieldMaskLegend")
    if not isinstance(docs, dict):
        raise ValueError("backend index must contain object field: docs")
    posting_indexes_available = isinstance(term_index, dict) and isinstance(prefix_index, dict)
    if (term_index is None) != (prefix_index is None):
        raise ValueError("backend index must either contain both termIndex/prefixIndex or neither")
    if term_index is not None and not posting_indexes_available:
        raise ValueError("backend termIndex/prefixIndex fields must be objects when present")
    if posting_indexes_available:
        if not isinstance(field_mask_legend, dict) or TAG_FIELD_NAME not in field_mask_legend:
            raise ValueError("fieldMaskLegend.tag is required when posting indexes are present")
        tag_mask = int(field_mask_legend[TAG_FIELD_NAME])
    else:
        tag_mask = 0
    prefix_limit = 32
    build_options = payload.get("buildOptions")
    if isinstance(build_options, dict):
        try:
            prefix_limit = int(build_options.get("prefixDocLimit") or prefix_limit)
        except (TypeError, ValueError):
            prefix_limit = 32
        if not posting_indexes_available:
            build_options.pop("prefixDocLimit", None)

    items: list[dict[str, Any]] = []
    changed = False
    exact_score = TAG_FIELD_WEIGHT
    prefix_score = max(1, int(round(TAG_FIELD_WEIGHT * TAG_PREFIX_RATIO)))

    for pair in pairs:
        doc = docs.get(pair.doc_id)
        if not isinstance(doc, dict):
            items.append(
                {
                    "doc_id": pair.doc_id,
                    "tag": pair.tag,
                    "status": "missing_doc_skipped",
                }
            )
            continue

        tag_status = ensure_doc_tag(doc, pair.tag)
        term = normalize_text(pair.tag)
        exact_status = "posting_indexes_absent"
        removed_prefix_statuses = {}
        if posting_indexes_available:
            exact_status = upsert_posting(
                term_index,
                term,
                pair.doc_id,
                exact_score,
                tag_mask,
                docs,
            )
            if pair.tag.upper() == pair.doc_id and ID_TAG_RE.fullmatch(pair.tag):
                removed_prefix_statuses = {
                    prefix: remove_posting_field(
                        prefix_index,
                        prefix,
                        pair.doc_id,
                        prefix_score,
                        tag_mask,
                        docs,
                        limit=prefix_limit,
                    )
                    for prefix in latin_prefix_terms(term)
                }

        item_changed = (
            tag_status != "already_present"
            or exact_status != "already_present"
            or any(status != "already_absent" for status in removed_prefix_statuses.values())
        )
        changed = changed or item_changed
        items.append(
            {
                "doc_id": pair.doc_id,
                "tag": pair.tag,
                "term": term,
                "status": "changed" if item_changed else "already_synced",
                "tag_status": tag_status,
                "term_index": exact_status,
                "prefix_index_cleanup": removed_prefix_statuses,
            }
        )

    stats = payload.setdefault("stats", {})
    if isinstance(stats, dict):
        if posting_indexes_available:
            stats["terms"] = len(term_index)
            stats["prefixes"] = len(prefix_index)
        else:
            stats.pop("terms", None)
            stats.pop("prefixes", None)

    return {"items": items, "changed": changed}, changed


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Idempotently add searchable doc-id tags to backend_search_index.json."
    )
    parser.add_argument(
        "pairs",
        nargs="*",
        help="Alias pairs such as C002:G003. Multiple pairs may be comma-separated.",
    )
    parser.add_argument(
        "--mapping-json",
        type=Path,
        help="Optional JSON mapping: {\"C002\": [\"G003\"]} or [{\"doc_id\": \"C002\", \"tag\": \"G003\"}].",
    )
    parser.add_argument(
        "--all-doc-id-tags",
        action="store_true",
        help="Ensure every existing doc is tagged with its own ID. This is the default when no pairs/mapping are given.",
    )
    parser.add_argument(
        "--backend-json",
        type=Path,
        default=DEFAULT_BACKEND_INDEX,
        help=f"Backend index path. Default: {DEFAULT_BACKEND_INDEX}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path. Defaults to overwriting --backend-json unless --dry-run is set.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not write changes.")
    parser.add_argument("--report", type=Path, help="Optional JSON report path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    pairs = parse_pairs(args.pairs)
    if args.mapping_json:
        pairs.extend(load_mapping(args.mapping_json))

    backend_path = args.backend_json.resolve()
    payload, style = read_json_with_style(backend_path)
    if not isinstance(payload, dict):
        raise ValueError(f"backend JSON root must be an object: {backend_path}")

    docs = payload.get("docs")
    if not pairs and not args.mapping_json:
        args.all_doc_id_tags = True

    if args.all_doc_id_tags:
        if not isinstance(docs, dict):
            raise ValueError("backend index must contain object field: docs")
        pairs.extend(AliasPair(str(doc_id), str(doc_id)) for doc_id in docs.keys())
    pairs = dedupe_pairs(pairs)
    if not pairs:
        parser.error("no docs found; provide at least one pair, --mapping-json, or --all-doc-id-tags")

    original = copy.deepcopy(payload)
    report, changed = apply_aliases(payload, pairs)
    material_changed = payload != original
    if material_changed:
        payload["generatedAt"] = iso_now()

    output_path = (args.output or backend_path).resolve()
    if not args.dry_run and material_changed:
        write_json(output_path, payload, style)
    if args.report:
        report_payload = {
            "generated_at": iso_now(),
            "backend_json": str(backend_path),
            "output": str(output_path),
            "dry_run": bool(args.dry_run),
            "material_changed": material_changed,
            **report,
        }
        write_json(args.report.resolve(), report_payload, JsonStyle())

    changed_items = [item for item in report["items"] if item["status"] == "changed"]
    missing_items = [item for item in report["items"] if item["status"] == "missing_doc_skipped"]
    print(
        "sync_backend_tag_aliases: "
        f"pairs={len(pairs)} changed={len(changed_items)} "
        f"missing={len(missing_items)} wrote={bool(not args.dry_run and material_changed)}"
    )
    for item in report["items"]:
        print(f"- {item['doc_id']} <- {item['tag']}: {item['status']}")
    return 0 if changed or not missing_items else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
