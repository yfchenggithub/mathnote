"""Command-line entry point for the Zhishu publisher."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

if __package__:
    from .source_discovery import ScanResult, scan_repository
else:
    from source_discovery import ScanResult, scan_repository


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="publish.py")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("scan", help="discover and validate conclusion sources")
    return parser


def format_scan_result(result: ScanResult) -> str:
    lines = ["Zhishu Source Discovery", ""]
    for module in result.modules:
        lines.append(f"{module.module_name:<24}{len(module.sources)}")

    if result.errors:
        lines.extend(("", "ERROR"))
        lines.extend(f"{error.path.as_posix()}: {error.message}" for error in result.errors)

    lines.extend(
        (
            "",
            f"Modules: {len(result.modules)}",
            f"Conclusions: {result.conclusion_count}",
            f"Errors: {len(result.errors)}",
        )
    )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "scan":
        result = scan_repository(PROJECT_ROOT)
        print(format_scan_result(result))
        return 1 if result.errors else 0
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())

