#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mark JSON nodes with need-image flag based on latex length.

Rule:
- If a dict node has a string field `latex`
- And len(latex.strip()) > min_length
- Then add/update flag field (default: need_image = "true")

Examples:
    python scripts/mark_need_image_by_latex_length.py
    python scripts/mark_need_image_by_latex_length.py --dry-run
    python scripts/mark_need_image_by_latex_length.py --min-length 40
    python scripts/mark_need_image_by_latex_length.py --mode sync
    python scripts/mark_need_image_by_latex_length.py --flag-key need_imgae
"""

from __future__ import annotations

import argparse
import codecs
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path("data/content/canonical_content_v2.json")


@dataclass
class MarkStats:
    total_latex_nodes: int = 0
    matched_nodes: int = 0
    added_flags: int = 0
    already_flagged: int = 0
    removed_flags: int = 0


def parse_non_negative_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid int: {value!r}") from exc
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Add need-image flag for nodes whose latex length is above a threshold."
        )
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help=f"Input JSON path (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--output",
        default=None,
        help=(
            "Output JSON path. If omitted, overwrite input file."
        ),
    )
    parser.add_argument(
        "--min-length",
        type=parse_non_negative_int,
        default=30,
        help="Threshold for len(latex.strip()) (default: 30)",
    )
    parser.add_argument(
        "--flag-key",
        default="need_image",
        help="Flag key name to write (default: need_image)",
    )
    parser.add_argument(
        "--flag-value",
        default="true",
        help='Flag value to write (default: "true")',
    )
    parser.add_argument(
        "--mode",
        choices=("add", "sync"),
        default="add",
        help=(
            "add: only set flags on matched nodes; "
            "sync: also remove existing true flags on unmatched nodes"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview stats only; do not write output file.",
    )
    return parser.parse_args()


def read_json_with_style(path: Path) -> tuple[Any, bool, str]:
    raw = path.read_bytes()
    has_bom = raw.startswith(codecs.BOM_UTF8)
    newline = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8-sig")
    return json.loads(text), has_bom, newline


def is_true_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return False


def iter_dict_nodes(root: Any):
    stack = [root]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            yield node
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)


def apply_marking(
    root: Any,
    *,
    min_length: int,
    flag_key: str,
    flag_value: Any,
    mode: str,
) -> MarkStats:
    stats = MarkStats()
    for node in iter_dict_nodes(root):
        latex = node.get("latex")
        if not isinstance(latex, str):
            continue

        stats.total_latex_nodes += 1
        matched = len(latex.strip()) > min_length
        existing = node.get(flag_key)

        if matched:
            stats.matched_nodes += 1
            if is_true_flag(existing):
                stats.already_flagged += 1
            else:
                node[flag_key] = flag_value
                stats.added_flags += 1
            continue

        if mode == "sync" and is_true_flag(existing):
            del node[flag_key]
            stats.removed_flags += 1

    return stats


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
    output_text = dump_json_text(data, newline)
    payload = output_text.encode("utf-8")
    if has_bom:
        payload = codecs.BOM_UTF8 + payload
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve() if args.output else input_path

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    data, has_bom, newline = read_json_with_style(input_path)
    stats = apply_marking(
        data,
        min_length=int(args.min_length),
        flag_key=str(args.flag_key),
        flag_value=args.flag_value,
        mode=str(args.mode),
    )

    print(f"[mark_need_image] input      : {input_path}")
    print(f"[mark_need_image] output     : {output_path}")
    print(f"[mark_need_image] mode       : {args.mode}")
    print(f"[mark_need_image] min_length : {args.min_length}")
    print(f"[mark_need_image] flag       : {args.flag_key}={args.flag_value!r}")
    print(f"[mark_need_image] total_latex_nodes : {stats.total_latex_nodes}")
    print(f"[mark_need_image] matched_nodes     : {stats.matched_nodes}")
    print(f"[mark_need_image] added_flags       : {stats.added_flags}")
    print(f"[mark_need_image] already_flagged   : {stats.already_flagged}")
    print(f"[mark_need_image] removed_flags     : {stats.removed_flags}")

    if args.dry_run:
        print("[mark_need_image] dry-run: no file written.")
        return 0

    write_json_with_style(
        output_path,
        data,
        has_bom=has_bom,
        newline=newline,
    )
    print("[mark_need_image] done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
