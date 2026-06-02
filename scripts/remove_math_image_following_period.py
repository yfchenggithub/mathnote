#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Remove punctuation tokens that immediately follow math_image tokens in inline token lists.

Current default rule:
- In a list field named `tokens`, `desc_tokens`, or `content`
- If one token is `{"type": "math_image", ...}`
- And the next token is `{"type": "text", "text": "\u3002"}`
- Then remove only that punctuation token.

This script is designed to be safe and debuggable:
- Dry-run by default (no file writes unless `--write` is provided)
- Preserve UTF-8 BOM and newline style from input
- Provide structured stats and optional debug logs

Examples:
    python scripts/remove_math_image_following_period.py
    python scripts/remove_math_image_following_period.py --write
    python scripts/remove_math_image_following_period.py --write --verbose
    python scripts/remove_math_image_following_period.py --target-text "。,." --write
"""

from __future__ import annotations

import argparse
import codecs
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path("data/content/canonical_content_v2.json")
DEFAULT_TOKEN_LIST_FIELDS = "tokens,desc_tokens,content"
LOGGER = logging.getLogger("remove_math_image_following_period")


@dataclass(frozen=True)
class CleanConfig:
    math_token_type: str
    text_token_type: str
    target_texts: frozenset[str]
    token_list_fields: frozenset[str]
    strip_text: bool


@dataclass
class CleanStats:
    token_lists_seen: int = 0
    token_lists_changed: int = 0
    math_image_tokens_seen: int = 0
    punctuation_candidates_seen: int = 0
    tokens_removed: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Remove text punctuation tokens that are immediately after math_image "
            "tokens in inline token lists."
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
            "Output JSON path. If omitted, output path is the input path. "
            "Only written when --write is provided."
        ),
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write changes to output file. Default behavior is dry-run preview.",
    )
    parser.add_argument(
        "--target-text",
        default="。",
        help=(
            "Comma-separated text values to remove when they immediately follow "
            'a math_image token (default: "。").'
        ),
    )
    parser.add_argument(
        "--strict-text",
        action="store_true",
        help=(
            "Use exact text matching. By default, token text is stripped before "
            "comparison."
        ),
    )
    parser.add_argument(
        "--paragraph-type",
        default="paragraph",
        help=(
            "Deprecated compatibility option. Token-list fields are cleaned "
            "regardless of parent node type."
        ),
    )
    parser.add_argument(
        "--token-list-fields",
        default=DEFAULT_TOKEN_LIST_FIELDS,
        help=(
            "Comma-separated list field names to clean "
            f'(default: "{DEFAULT_TOKEN_LIST_FIELDS}").'
        ),
    )
    parser.add_argument(
        "--math-token-type",
        default="math_image",
        help='Math token type value (default: "math_image").',
    )
    parser.add_argument(
        "--text-token-type",
        default="text",
        help='Text token type value (default: "text").',
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show info logs.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show detailed debug logs for each removed token.",
    )
    return parser.parse_args()


def configure_logging(*, verbose: bool, debug: bool) -> None:
    level = logging.WARNING
    if verbose:
        level = logging.INFO
    if debug:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
    )


def parse_comma_separated_values(raw: str, *, option_name: str) -> frozenset[str]:
    values = [part.strip() for part in raw.split(",")]
    filtered = [item for item in values if item]
    if not filtered:
        raise ValueError(f"{option_name} must contain at least one non-empty value")
    return frozenset(filtered)


def format_text_values(values: frozenset[str]) -> str:
    escaped = [item.encode("unicode_escape").decode("ascii") for item in sorted(values)]
    return ", ".join(f"'{item}'" for item in escaped)


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


def is_math_image_token(node: Any, *, math_token_type: str) -> bool:
    return isinstance(node, dict) and node.get("type") == math_token_type


def is_target_text_token(node: Any, *, config: CleanConfig) -> bool:
    if not isinstance(node, dict):
        return False
    if node.get("type") != config.text_token_type:
        return False

    text = node.get("text")
    if not isinstance(text, str):
        return False

    candidate = text if config.strip_text is False else text.strip()
    return candidate in config.target_texts


def format_json_path(parts: list[str | int]) -> str:
    output = "$"
    for part in parts:
        if isinstance(part, int):
            output += f"[{part}]"
        elif part.isidentifier():
            output += f".{part}"
        else:
            escaped = part.replace("\\", "\\\\").replace('"', '\\"')
            output += f'["{escaped}"]'
    return output


def clean_token_sequence(
    tokens: list[Any],
    *,
    path: list[str | int],
    config: CleanConfig,
    stats: CleanStats,
) -> int:
    changed = 0
    rebuilt: list[Any] = []
    idx = 0

    while idx < len(tokens):
        current = tokens[idx]

        if is_math_image_token(current, math_token_type=config.math_token_type):
            stats.math_image_tokens_seen += 1

            next_idx = idx + 1
            if next_idx < len(tokens):
                next_token = tokens[next_idx]
                if is_target_text_token(next_token, config=config):
                    stats.punctuation_candidates_seen += 1
                    stats.tokens_removed += 1
                    changed += 1
                    rebuilt.append(current)
                    LOGGER.debug(
                        "Removed token at %s after math_image (latex=%r).",
                        format_json_path(path + [next_idx]),
                        current.get("latex")
                        if isinstance(current, dict)
                        else None,
                    )
                    idx += 2
                    continue

        rebuilt.append(current)
        idx += 1

    if changed > 0:
        tokens[:] = rebuilt

    return changed


def traverse_and_clean(
    node: Any,
    *,
    path: list[str | int],
    config: CleanConfig,
    stats: CleanStats,
) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key in config.token_list_fields and isinstance(value, list):
                stats.token_lists_seen += 1
                removed = clean_token_sequence(
                    value,
                    path=path + [str(key)],
                    config=config,
                    stats=stats,
                )
                if removed > 0:
                    stats.token_lists_changed += 1
                    LOGGER.debug(
                        "Token list changed at %s, removed %d token(s).",
                        format_json_path(path + [str(key)]),
                        removed,
                    )

            traverse_and_clean(
                value,
                path=path + [str(key)],
                config=config,
                stats=stats,
            )
        return

    if isinstance(node, list):
        for index, item in enumerate(node):
            traverse_and_clean(
                item,
                path=path + [index],
                config=config,
                stats=stats,
            )


def build_config(args: argparse.Namespace) -> CleanConfig:
    target_texts = parse_comma_separated_values(
        str(args.target_text),
        option_name="--target-text",
    )
    token_list_fields = parse_comma_separated_values(
        str(args.token_list_fields),
        option_name="--token-list-fields",
    )
    return CleanConfig(
        math_token_type=str(args.math_token_type),
        text_token_type=str(args.text_token_type),
        target_texts=target_texts,
        token_list_fields=token_list_fields,
        strip_text=not bool(args.strict_text),
    )


def print_summary(
    *,
    input_path: Path,
    output_path: Path,
    write_enabled: bool,
    stats: CleanStats,
) -> None:
    mode = "WRITE" if write_enabled else "DRY-RUN"
    print(f"[{mode}] input:  {input_path}")
    print(f"[{mode}] output: {output_path}")
    print(f"[{mode}] token_lists_seen:           {stats.token_lists_seen}")
    print(f"[{mode}] token_lists_changed:        {stats.token_lists_changed}")
    print(f"[{mode}] math_image_tokens_seen:     {stats.math_image_tokens_seen}")
    print(
        f"[{mode}] punctuation_candidates_seen: "
        f"{stats.punctuation_candidates_seen}"
    )
    print(f"[{mode}] tokens_removed:             {stats.tokens_removed}")

    if stats.tokens_removed == 0:
        print(
            f"[{mode}] no matching `math_image` + punctuation token pairs found."
        )


def main() -> int:
    args = parse_args()
    configure_logging(verbose=bool(args.verbose), debug=bool(args.debug))

    if args.verbose and args.debug:
        LOGGER.info("Debug logging is enabled.")

    input_path = Path(str(args.input)).resolve()
    output_path = Path(str(args.output)).resolve() if args.output else input_path
    write_enabled = bool(args.write)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    config = build_config(args)
    LOGGER.info("Target text values: %s", format_text_values(config.target_texts))

    data, has_bom, newline = read_json_with_style(input_path)
    stats = CleanStats()
    traverse_and_clean(
        data,
        path=[],
        config=config,
        stats=stats,
    )

    print_summary(
        input_path=input_path,
        output_path=output_path,
        write_enabled=write_enabled,
        stats=stats,
    )

    if write_enabled:
        write_json_with_style(
            output_path,
            data,
            has_bom=has_bom,
            newline=newline,
        )
        LOGGER.info("Wrote cleaned JSON to: %s", output_path)
    else:
        LOGGER.info("Dry-run mode: no file changes were written.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
