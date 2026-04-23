#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fix Chinese punctuation inside LaTeX math environments for selected conclusion IDs.

Usage:
    python scripts/fix_math_punctuation.py C019
    python scripts/fix_math_punctuation.py C019 C020 --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

TARGET_FILES = (
    "01_statement.tex",
    "02_explanation.tex",
    "03_proof.tex",
    "04_examples.tex",
    "05_traps.tex",
    "06_summary.tex",
)

MODULE_DIR_PATTERN = re.compile(r"^\d{2}[_-].+")
ID_PATTERN = re.compile(r"^[A-Za-z]\d{3}$")

MATH_ENV_NAMES = {
    "equation",
    "equation*",
    "align",
    "align*",
    "gather",
    "gather*",
    "multline",
    "multline*",
    "flalign",
    "flalign*",
    "eqnarray",
    "eqnarray*",
}

PUNCT_REPLACEMENTS = {
    "。": ".",
    "，": ",",
    "；": ";",
    "：": ":",
    "！": "!",
    "？": "?",
    "（": "(",
    "）": ")",
    "【": "[",
    "】": "]",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fix Chinese punctuation inside LaTeX math environments for "
            "01~06 lecture files under selected conclusion IDs."
        )
    )
    parser.add_argument(
        "ids",
        nargs="+",
        help="Conclusion IDs (e.g. C019, C020). Supports comma/space mixed input.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview only; do not write files.",
    )
    return parser.parse_args()


def split_csv_tokens(values: list[str]) -> list[str]:
    tokens: list[str] = []
    for raw in values:
        for token in raw.split(","):
            piece = token.strip()
            if piece:
                tokens.append(piece)
    return tokens


def normalize_ids(raw_ids: list[str]) -> list[str]:
    normalized: list[str] = []
    invalid: list[str] = []
    for value in split_csv_tokens(raw_ids):
        item_id = value.strip().upper()
        if not ID_PATTERN.fullmatch(item_id):
            invalid.append(value)
            continue
        normalized.append(item_id)

    if invalid:
        raise ValueError(
            "Invalid ID format: "
            + ", ".join(invalid)
            + " (expected format like C019)."
        )

    return list(dict.fromkeys(normalized))


def list_module_dirs(project_root: Path) -> list[Path]:
    return sorted(
        [
            path
            for path in project_root.iterdir()
            if path.is_dir() and MODULE_DIR_PATTERN.match(path.name)
        ],
        key=lambda p: p.name.lower(),
    )


def find_conclusion_dir(project_root: Path, item_id: str) -> Path:
    prefix = item_id.upper()
    candidates: list[Path] = []

    for module_dir in list_module_dirs(project_root):
        for child in module_dir.iterdir():
            if not child.is_dir():
                continue
            upper_name = child.name.upper()
            if upper_name == prefix or upper_name.startswith(f"{prefix}_"):
                candidates.append(child)

    if not candidates:
        raise FileNotFoundError(f"{item_id}: no matching conclusion directory found.")

    if len(candidates) > 1:
        refs = ", ".join(
            str(path.relative_to(project_root)).replace("\\", "/")
            for path in sorted(candidates, key=lambda p: str(p).lower())
        )
        raise ValueError(f"{item_id}: multiple conclusion directories found: {refs}")

    return candidates[0]


def read_utf8_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def is_escaped(text: str, index: int) -> bool:
    slash_count = 0
    pos = index - 1
    while pos >= 0 and text[pos] == "\\":
        slash_count += 1
        pos -= 1
    return (slash_count % 2) == 1


def pop_last(stack: list[str], token: str) -> bool:
    for idx in range(len(stack) - 1, -1, -1):
        if stack[idx] == token:
            del stack[idx]
            return True
    return False


def replace_math_punctuation(text: str) -> tuple[str, int, Counter[str]]:
    stack: list[str] = []
    output: list[str] = []
    counts: Counter[str] = Counter()

    i = 0
    n = len(text)
    while i < n:
        if text.startswith("\\begin{", i):
            end = text.find("}", i + len("\\begin{"))
            if end != -1:
                segment = text[i : end + 1]
                output.append(segment)
                env_name = text[i + len("\\begin{") : end].strip().lower()
                if env_name in MATH_ENV_NAMES:
                    stack.append(f"env:{env_name}")
                i = end + 1
                continue

        if text.startswith("\\end{", i):
            end = text.find("}", i + len("\\end{"))
            if end != -1:
                segment = text[i : end + 1]
                output.append(segment)
                env_name = text[i + len("\\end{") : end].strip().lower()
                if env_name in MATH_ENV_NAMES:
                    pop_last(stack, f"env:{env_name}")
                i = end + 1
                continue

        if text.startswith("\\(", i):
            output.append("\\(")
            stack.append("delim:\\(")
            i += 2
            continue

        if text.startswith("\\)", i):
            output.append("\\)")
            pop_last(stack, "delim:\\(")
            i += 2
            continue

        if text.startswith("\\[", i):
            output.append("\\[")
            stack.append("delim:\\[")
            i += 2
            continue

        if text.startswith("\\]", i):
            output.append("\\]")
            pop_last(stack, "delim:\\[")
            i += 2
            continue

        ch = text[i]

        if ch == "%" and not is_escaped(text, i):
            line_end = text.find("\n", i)
            if line_end == -1:
                output.append(text[i:])
                break
            output.append(text[i : line_end + 1])
            i = line_end + 1
            continue

        if text.startswith("$$", i) and not is_escaped(text, i):
            output.append("$$")
            if not pop_last(stack, "delim:$$"):
                stack.append("delim:$$")
            i += 2
            continue

        if ch == "$" and not is_escaped(text, i):
            output.append("$")
            if not pop_last(stack, "delim:$"):
                stack.append("delim:$")
            i += 1
            continue

        if stack and ch in PUNCT_REPLACEMENTS:
            output.append(PUNCT_REPLACEMENTS[ch])
            counts[ch] += 1
        else:
            output.append(ch)
        i += 1

    return "".join(output), sum(counts.values()), counts


def format_counts(counts: Counter[str]) -> str:
    if not counts:
        return ""

    def encode_char(ch: str) -> str:
        escaped = ch.encode("unicode_escape").decode("ascii")
        return escaped if escaped.startswith("\\u") else repr(ch)

    parts = [
        f"{encode_char(src)}->{encode_char(PUNCT_REPLACEMENTS[src])} x{counts[src]}"
        for src in sorted(counts)
    ]
    return ", ".join(parts)


def process_file(path: Path, dry_run: bool) -> tuple[str, int]:
    if not path.is_file():
        print(f"  [MISS] {path.name}: file not found")
        return "missing", 0

    original = read_utf8_text(path)
    updated, replaced_count, detail = replace_math_punctuation(original)

    if replaced_count == 0:
        print(f"  [OK]   {path.name}: no replacement needed")
        return "unchanged", 0

    detail_text = format_counts(detail)
    if dry_run:
        print(
            f"  [DRY]  {path.name}: would replace {replaced_count} "
            f"punctuation(s) ({detail_text})"
        )
        return "modified", replaced_count

    path.write_text(updated, encoding="utf-8", newline="\n")
    print(
        f"  [FIX]  {path.name}: replaced {replaced_count} "
        f"punctuation(s) ({detail_text})"
    )
    return "modified", replaced_count


def run(ids: list[str], dry_run: bool) -> int:
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent

    try:
        normalized_ids = normalize_ids(ids)
    except ValueError as exc:
        print(f"[error] {exc}")
        return 2

    print(f"[info] Project root: {project_root}")
    print(f"[info] IDs: {', '.join(normalized_ids)}")
    print(f"[info] Mode: {'dry-run' if dry_run else 'write'}")

    checked_total = 0
    existing_total = 0
    missing_total = 0
    modified_files = 0
    replaced_total = 0

    for item_id in normalized_ids:
        try:
            conclusion_dir = find_conclusion_dir(project_root, item_id)
        except (FileNotFoundError, ValueError) as exc:
            print(f"[error] {exc}")
            return 2

        rel_dir = str(conclusion_dir.relative_to(project_root)).replace("\\", "/")
        print(f"\n[{item_id}] target: {rel_dir}")

        for filename in TARGET_FILES:
            checked_total += 1
            file_path = conclusion_dir / filename
            status, count = process_file(file_path, dry_run)
            if status == "missing":
                missing_total += 1
                continue
            existing_total += 1
            if status == "modified":
                modified_files += 1
                replaced_total += count

    print("\n[summary]")
    print(f"  checked files: {checked_total}")
    print(f"  existing files: {existing_total}")
    print(f"  missing files: {missing_total}")
    print(f"  modified files: {modified_files}")
    print(f"  total replacements: {replaced_total}")

    return 0


def main() -> int:
    args = parse_args()
    return run(args.ids, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
