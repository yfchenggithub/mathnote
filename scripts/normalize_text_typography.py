#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Normalize Chinese-style typography in text files (extensible rule engine).

This script is designed for repository-wide cleanup of punctuation/style
characters that often cause model instability or formatting noise.

Core design goals
-----------------
1. Single responsibility:
   Only does text typography normalization.
2. Extensible:
   Rules are grouped into profiles and can be extended with `--extra-map`.
3. Safe by default:
   - supports dry-run
   - skips binary files
   - preserves BOM and original newline characters
4. Easy to use:
   Run without targets to scan common text files in the whole repo.

Default behavior
----------------
If no target is provided, the script scans common text files under repo root
(excluding typical cache/dependency directories), and applies profiles:
  - quotes
  - punctuation

Built-in profiles
-----------------
- quotes:
  Chinese/full-width/curly quotes -> ASCII quotes
- punctuation:
  Common Chinese punctuation -> ASCII punctuation
- spaces:
  Full-width space -> normal ASCII space

Usage
-----
1) Preview repo-wide changes:
   python scripts/normalize_text_typography.py --dry-run

2) Apply repo-wide changes:
   python scripts/normalize_text_typography.py

3) Restrict to paths/globs:
   python scripts/normalize_text_typography.py 12_pipeline/prompts "*.md" --dry-run

4) Choose profiles:
   python scripts/normalize_text_typography.py --profiles quotes spaces --dry-run

5) Add custom mapping:
   python scripts/normalize_text_typography.py --extra-map "《=\"" --extra-map "》=\""

6) Show active rules only:
   python scripts/normalize_text_typography.py --show-rules

Exit code
---------
0: success
2: invalid arguments / no files found
3: runtime file read/write error
"""

from __future__ import annotations

import argparse
import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


# Text-like file extensions for repo-wide scanning.
DEFAULT_TEXT_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".tex",
    ".latex",
    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".pt",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".css",
    ".scss",
    ".less",
    ".vue",
    ".xml",
    ".sql",
    ".sh",
    ".bat",
    ".ps1",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".java",
    ".go",
    ".rs",
}

DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    ".idea",
    ".vscode",
}

PROFILE_RULES: dict[str, dict[str, str]] = {
    "quotes": {
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "＂": '"',
        "＇": "'",
        "「": '"',
        "」": '"',
        "『": '"',
        "』": '"',
    },
    "punctuation": {
        "，": ",",
        "。": ".",
        "；": ";",
        "：": ":",
        "！": "!",
        "？": "?",
        "（": "(",
        "）": ")",
        "【": "[",
        "】": "]",
        "｛": "{",
        "｝": "}",
        "、": ",",
    },
    "spaces": {
        "　": " ",
    },
}

DEFAULT_PROFILES = ("quotes", "punctuation")


@dataclass(slots=True)
class ReadResult:
    text: str
    has_bom: bool


@dataclass(slots=True)
class FileResult:
    path: Path
    modified: bool
    changed_chars: int
    changed_pairs: Counter[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize Chinese-style typography in repository text files."
    )
    parser.add_argument(
        "targets",
        nargs="*",
        help=(
            "Optional files/directories/glob patterns. "
            "If omitted, scan repo root using text extensions."
        ),
    )
    parser.add_argument(
        "--profiles",
        nargs="+",
        default=list(DEFAULT_PROFILES),
        help=(
            "Rule profiles to apply. "
            f"Available: {', '.join(sorted(PROFILE_RULES))}. "
            f"Default: {', '.join(DEFAULT_PROFILES)}."
        ),
    )
    parser.add_argument(
        "--extra-map",
        action="append",
        default=[],
        metavar="SRC=DST",
        help=(
            "Add custom one-character mapping, repeatable. "
            "Supports literal chars or unicode forms like U+201C=\\\"."
        ),
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=sorted(DEFAULT_TEXT_EXTENSIONS),
        help=(
            "Text extensions used when scanning directories recursively. "
            "Default is a broad text extension set."
        ),
    )
    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help=(
            "Exclude directory name during recursive scanning (repeatable). "
            "Default includes .git, __pycache__, node_modules, etc."
        ),
    )
    parser.add_argument(
        "--max-kb",
        type=int,
        default=1024,
        help="Skip files larger than this size in KB when scanning directories.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview only; do not write files.",
    )
    parser.add_argument(
        "--show-rules",
        action="store_true",
        help="Print active mapping rules and exit.",
    )
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def normalize_extensions(raw: list[str]) -> set[str]:
    result: set[str] = set()
    for item in raw:
        token = item.strip().lower()
        if not token:
            continue
        if not token.startswith("."):
            token = f".{token}"
        result.add(token)
    return result


def normalize_profiles(raw_profiles: list[str]) -> list[str]:
    invalid = [name for name in raw_profiles if name not in PROFILE_RULES]
    if invalid:
        raise ValueError(
            f"Invalid profile(s): {', '.join(invalid)}. "
            f"Available: {', '.join(sorted(PROFILE_RULES))}"
        )
    return list(dict.fromkeys(raw_profiles))


def decode_token(token: str) -> str:
    text = token.strip()
    if text.startswith("U+") and len(text) > 2:
        return chr(int(text[2:], 16))
    if text.startswith("\\u") or text.startswith("\\U") or text.startswith("\\x"):
        return bytes(text, "utf-8").decode("unicode_escape")
    return text


def parse_extra_map(raw_items: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for item in raw_items:
        if "=" not in item:
            raise ValueError(f"Invalid --extra-map value: {item!r} (expected SRC=DST)")
        raw_src, raw_dst = item.split("=", 1)
        src = decode_token(raw_src)
        dst = decode_token(raw_dst)
        if len(src) != 1:
            raise ValueError(
                f"Invalid SRC in --extra-map {item!r}: SRC must be exactly one character."
            )
        mapping[src] = dst
    return mapping


def build_replacements(profiles: list[str], extra_map: dict[str, str]) -> dict[str, str]:
    merged: dict[str, str] = {}
    for profile in profiles:
        for src, dst in PROFILE_RULES[profile].items():
            prev = merged.get(src)
            if prev is not None and prev != dst:
                raise ValueError(
                    f"Rule conflict for {src!r}: {prev!r} vs {dst!r} (profile={profile})"
                )
            merged[src] = dst

    for src, dst in extra_map.items():
        merged[src] = dst
    return merged


def list_repo_files(
    root: Path,
    extensions: set[str],
    excluded_dirs: set[str],
    max_bytes: int,
) -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in excluded_dirs]
        base = Path(dirpath)
        for filename in filenames:
            path = base / filename
            if path.suffix.lower() not in extensions:
                continue
            try:
                if path.stat().st_size > max_bytes:
                    continue
            except OSError:
                continue
            files.append(path)
    return sorted(files)


def list_dir_files(
    directory: Path,
    extensions: set[str],
    excluded_dirs: set[str],
    max_bytes: int,
) -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(directory):
        dirnames[:] = [d for d in dirnames if d not in excluded_dirs]
        base = Path(dirpath)
        for filename in filenames:
            path = base / filename
            if path.suffix.lower() not in extensions:
                continue
            try:
                if path.stat().st_size > max_bytes:
                    continue
            except OSError:
                continue
            files.append(path)
    return sorted(files)


def expand_targets(
    root: Path,
    raw_targets: list[str],
    extensions: set[str],
    excluded_dirs: set[str],
    max_bytes: int,
) -> list[Path]:
    if not raw_targets:
        return list_repo_files(root, extensions, excluded_dirs, max_bytes)

    files: set[Path] = set()

    for token in raw_targets:
        token_path = Path(token)

        if token_path.is_absolute():
            if token_path.is_file():
                files.add(token_path.resolve())
                continue
            if token_path.is_dir():
                files.update(
                    list_dir_files(token_path, extensions, excluded_dirs, max_bytes)
                )
                continue
            else:
                # Absolute glob pattern
                parent = token_path.parent
                if parent.exists():
                    for p in parent.glob(token_path.name):
                        if p.is_file():
                            try:
                                if p.stat().st_size <= max_bytes:
                                    files.add(p.resolve())
                            except OSError:
                                continue
                continue
        else:
            candidate = root / token
            if candidate.is_file():
                files.add(candidate.resolve())
                continue
            if candidate.is_dir():
                files.update(
                    list_dir_files(candidate, extensions, excluded_dirs, max_bytes)
                )
                continue
            else:
                # Relative glob pattern
                for p in root.glob(token):
                    if p.is_file():
                        try:
                            if p.stat().st_size <= max_bytes:
                                files.add(p.resolve())
                        except OSError:
                            continue

    return sorted(files)


def read_text(path: Path) -> ReadResult:
    raw = path.read_bytes()
    if b"\x00" in raw[:4096]:
        raise ValueError("binary-like file (contains NUL bytes)")
    has_bom = raw.startswith(b"\xef\xbb\xbf")

    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            text = raw.decode(encoding)
            return ReadResult(text=text, has_bom=has_bom)
        except UnicodeDecodeError:
            continue

    raise UnicodeDecodeError(
        "utf-8",
        b"",
        0,
        1,
        "unsupported text encoding (tried utf-8-sig/utf-8/gb18030)",
    )


def apply_replacements(text: str, mapping: dict[str, str]) -> tuple[str, Counter[str]]:
    changed = Counter()
    out_chars: list[str] = []

    for ch in text:
        new_ch = mapping.get(ch, ch)
        out_chars.append(new_ch)
        if new_ch != ch:
            changed[f"{ch}->{new_ch}"] += 1

    return "".join(out_chars), changed


def process_file(path: Path, mapping: dict[str, str], dry_run: bool) -> FileResult:
    read_result = read_text(path)
    updated, changes = apply_replacements(read_result.text, mapping)
    changed_chars = sum(changes.values())

    if changed_chars == 0:
        return FileResult(
            path=path,
            modified=False,
            changed_chars=0,
            changed_pairs=changes,
        )

    if not dry_run:
        out_encoding = "utf-8-sig" if read_result.has_bom else "utf-8"
        path.write_bytes(updated.encode(out_encoding))

    return FileResult(
        path=path,
        modified=True,
        changed_chars=changed_chars,
        changed_pairs=changes,
    )


def format_rule(src: str, dst: str) -> str:
    return f"{src!r} -> {dst!r}"


def print_rules(mapping: dict[str, str]) -> None:
    print("[rules]")
    for src in sorted(mapping):
        print(f"  {format_rule(src, mapping[src])}")
    print(f"  total: {len(mapping)}")


def run(args: argparse.Namespace) -> int:
    root = repo_root()

    try:
        profiles = normalize_profiles(args.profiles)
        extra_map = parse_extra_map(args.extra_map)
        mapping = build_replacements(profiles, extra_map)
    except ValueError as exc:
        print(f"[error] {exc}")
        return 2

    if args.show_rules:
        print_rules(mapping)
        return 0

    try:
        extensions = normalize_extensions(args.extensions)
        excluded_dirs = set(DEFAULT_EXCLUDED_DIRS)
        excluded_dirs.update(x.strip() for x in args.exclude_dir if x.strip())
        max_bytes = max(1, int(args.max_kb)) * 1024
    except Exception as exc:  # noqa: BLE001
        print(f"[error] invalid scan options: {exc}")
        return 2

    files = expand_targets(
        root=root,
        raw_targets=args.targets,
        extensions=extensions,
        excluded_dirs=excluded_dirs,
        max_bytes=max_bytes,
    )

    if not files:
        print("[error] no eligible files found.")
        print(f"[hint] root={root}")
        return 2

    print(f"[info] root: {root}")
    print(f"[info] mode: {'dry-run' if args.dry_run else 'write'}")
    print(f"[info] profiles: {', '.join(profiles)}")
    print(f"[info] files: {len(files)}")

    changed_files = 0
    changed_chars_total = 0
    pair_counter: Counter[str] = Counter()

    for file_path in files:
        try:
            result = process_file(file_path, mapping, dry_run=args.dry_run)
        except Exception as exc:  # noqa: BLE001
            print(f"[error] {file_path}: {exc}")
            return 3

        try:
            rel = file_path.relative_to(root)
        except ValueError:
            rel = file_path

        if not result.modified:
            continue

        changed_files += 1
        changed_chars_total += result.changed_chars
        pair_counter.update(result.changed_pairs)
        tag = "DRY" if args.dry_run else "FIX"
        details = ", ".join(
            f"{pair} x{count}" for pair, count in sorted(result.changed_pairs.items())
        )
        print(f"[{tag}] {rel}: {result.changed_chars} change(s)" + (f" ({details})" if details else ""))

    print("\n[summary]")
    print(f"  scanned files: {len(files)}")
    print(f"  changed files: {changed_files}")
    print(f"  total changes: {changed_chars_total}")
    if pair_counter:
        details = ", ".join(
            f"{pair} x{count}" for pair, count in sorted(pair_counter.items())
        )
        print(f"  replacements: {details}")

    return 0


def main() -> int:
    args = parse_args()
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
