#!/usr/bin/env python
r"""Find or fix over-escaped LaTeX command prefixes in meta.json files.

The target bug is JSON text like "\\\\mathrm", which parses to runtime LaTeX
"\\mathrm" and is interpreted as a line break plus plain text. A normal LaTeX
command should be written as "\\mathrm" in JSON, which parses to "\mathrm".
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


LATEX_FIELD_NAMES = {
    "core_formula",
    "related_formulas",
    "latex_patterns",
    "formulaTokens",
}

OVER_ESCAPED_COMMAND_RE = re.compile(r"\\\\(?=[A-Za-z])")


@dataclass
class Change:
    path: str
    before: str
    after: str


def normalize_latex_command_escapes(value: str) -> str:
    """Collapse repeated command-prefix slashes, preserving LaTeX line breaks.

    This only changes two runtime backslashes immediately followed by a letter.
    Example:
      "\\\\mathrm{C}" -> "\\mathrm{C}"

    It does not change real line breaks such as "\\\\ " or "\\\\\n".
    """

    previous = None
    normalized = value
    while previous != normalized:
        previous = normalized
        normalized = OVER_ESCAPED_COMMAND_RE.sub(r"\\", normalized)
    return normalized


def walk_latex_value(value: Any, path: str, changes: list[Change]) -> Any:
    if isinstance(value, str):
        normalized = normalize_latex_command_escapes(value)
        if normalized != value:
            changes.append(Change(path=path, before=value, after=normalized))
        return normalized

    if isinstance(value, list):
        return [
            walk_latex_value(item, f"{path}[{index}]", changes)
            for index, item in enumerate(value)
        ]

    if isinstance(value, dict):
        return {
            key: walk_latex_value(item, f"{path}.{key}", changes)
            for key, item in value.items()
        }

    return value


def walk_json(value: Any, path: str, changes: list[Change]) -> Any:
    if isinstance(value, list):
        return [
            walk_json(item, f"{path}[{index}]", changes)
            for index, item in enumerate(value)
        ]

    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            item_path = f"{path}.{key}"
            if key in LATEX_FIELD_NAMES:
                normalized[key] = walk_latex_value(item, item_path, changes)
            else:
                normalized[key] = walk_json(item, item_path, changes)
        return normalized

    return value


def iter_meta_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted(root.rglob("meta.json"))


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def save_json(path: Path, data: Any) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Dry-run or fix over-escaped LaTeX command prefixes in meta.json files."
        )
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Project root, a directory containing meta.json files, or one meta.json file.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write fixes. Without this flag, only report planned changes.",
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        default=80,
        help="Maximum individual changes to print.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files = iter_meta_files(root)
    changed_files = 0
    total_changes = 0
    printed = 0

    for meta_path in files:
        try:
            data = load_json(meta_path)
        except ValueError as exc:
            print(f"[skip] {exc}")
            continue

        changes: list[Change] = []
        normalized = walk_json(data, "$", changes)
        if not changes:
            continue

        changed_files += 1
        total_changes += len(changes)
        display_path = meta_path.relative_to(Path.cwd()) if meta_path.is_relative_to(Path.cwd()) else meta_path
        print(f"[fix-meta-latex] {display_path}: {len(changes)} change(s)")
        for change in changes:
            if printed >= args.max_examples:
                continue
            print(f"  {change.path}")
            print(f"    before: {json.dumps(change.before, ensure_ascii=False)}")
            print(f"    after:  {json.dumps(change.after, ensure_ascii=False)}")
            printed += 1

        if args.write:
            save_json(meta_path, normalized)

    if total_changes > printed:
        print(f"[fix-meta-latex] ... {total_changes - printed} more change(s) omitted")

    mode = "written" if args.write else "dry-run"
    print(
        f"[fix-meta-latex] {mode}: {changed_files} file(s), "
        f"{total_changes} change(s)"
    )
    if not args.write and total_changes:
        print("[fix-meta-latex] rerun with --write to apply these fixes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
