"""Command-line entry point for the Zhishu publisher."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

if __package__:
    from .source_discovery import ScanResult, scan_repository
    from .source_initialization import InitializationResult, initialize_sources
else:
    from source_discovery import ScanResult, scan_repository
    from source_initialization import InitializationResult, initialize_sources


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="publish.py")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("scan", help="discover and validate conclusion sources")
    subparsers.add_parser(
        "init-source",
        help="ensure images/ and pdfs/ exist for discovered sources",
    )
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


def format_initialization_result(result: InitializationResult) -> str:
    lines = ["Zhishu Source Directory Initialization", ""]
    for module in result.modules:
        lines.extend(
            (
                module.module_name,
                f"  Conclusions: {module.conclusion_count}",
                f"  Created images/: {module.created_images}",
                f"  Created pdfs/: {module.created_pdfs}",
                f"  Already initialized: {module.already_initialized}",
                "",
            )
        )

    if result.errors:
        lines.extend(("ERROR",))
        lines.extend(f"{error.path.as_posix()}: {error.message}" for error in result.errors)
        lines.append("")

    lines.extend(
        (
            "Summary",
            "",
            f"Modules: {len(result.modules)}",
            f"Conclusions: {result.conclusion_count}",
            f"Created images/: {result.created_images}",
            f"Created pdfs/: {result.created_pdfs}",
            f"Already initialized: {result.already_initialized}",
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
    if args.command == "init-source":
        scan_result = scan_repository(PROJECT_ROOT)
        initialization_result = initialize_sources(scan_result)
        print(format_initialization_result(initialization_result))
        return 1 if initialization_result.errors else 0
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
