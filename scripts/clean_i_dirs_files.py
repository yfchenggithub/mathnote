#!/usr/bin/env python3
"""
Delete files under selected child directories (keep directory structure).

Default behavior:
- Module: 07-inequality
- Subdirectory match:
  1) CLI --pattern (highest priority)
  2) config.module_patterns[module_path] (if provided)
  3) inferred from module name, e.g. 01_function -> ^F\\d{2}
- Dry-run only (no delete) unless --apply is given

Examples:
1) Preview cleanup for 07-inequality (safe):
   python scripts/clean_i_dirs_files.py

2) Actually delete for 07-inequality:
   python scripts/clean_i_dirs_files.py --apply

3) Clean only specific subdirectories in one module:
   python scripts/clean_i_dirs_files.py --module 07-inequality \
       --subdir I01_Compound_Inequality_Transformation --subdir I02_Basic_Inequalities_and_Variations --apply

4) Use JSON config (module-specific patterns):
   python scripts/clean_i_dirs_files.py --config scripts/clean_i_dirs_files.example.json --apply
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


DEFAULT_PATTERN = r"^[A-Z]\d{2}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Delete files inside selected child directories (keep directories)."
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to JSON config file.",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path("."),
        help="Workspace base directory. Default: current directory.",
    )
    parser.add_argument(
        "--module",
        action="append",
        help="Module path (relative to base-dir). Can be repeated.",
    )
    parser.add_argument(
        "--subdir",
        action="append",
        help="Only clean these exact subdirectory names (applies to all --module). Can be repeated.",
    )
    parser.add_argument(
        "--exclude-subdir",
        action="append",
        help="Exclude these exact subdirectory names (applies to all --module). Can be repeated.",
    )
    parser.add_argument(
        "--pattern",
        default=None,
        help=(
            "Regex for target subdirectory names. "
            "If omitted: config.module_patterns > inferred module prefix rule."
        ),
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually delete files. Without this flag, script runs in dry-run mode.",
    )
    return parser.parse_args()


def is_within(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Config root must be a JSON object.")
    return data


def normalize_module_key(module_path: str) -> str:
    return module_path.replace("\\", "/").strip("/")


def infer_pattern_from_module(module_path: str) -> str:
    """
    Infer pattern from module basename.
    Example: 01_function -> ^F\\d{2}, 02_sequence -> ^S\\d{2}
    """
    base = Path(module_path).name
    if "-" in base:
        suffix = base.split("-", 1)[1]
        if suffix and suffix[0].isalpha():
            return rf"^{suffix[0].upper()}\d{{2}}"
    return DEFAULT_PATTERN


def build_module_pattern_map(config: dict[str, Any]) -> dict[str, str]:
    raw = config.get("module_patterns", {})
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("config.module_patterns must be an object (map).")

    out: dict[str, str] = {}
    for key, value in raw.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("config.module_patterns keys/values must be strings.")
        out[normalize_module_key(key)] = value
    return out


def resolve_pattern_for_module(
    module_path: str,
    cli_pattern: str | None,
    module_pattern_map: dict[str, str],
) -> str:
    if cli_pattern:
        return cli_pattern

    normalized = normalize_module_key(module_path)
    if normalized in module_pattern_map:
        return module_pattern_map[normalized]

    base = Path(module_path).name
    normalized_base = normalize_module_key(base)
    if normalized_base in module_pattern_map:
        return module_pattern_map[normalized_base]

    return infer_pattern_from_module(module_path)


def normalize_module_specs(
    args: argparse.Namespace,
    config: dict[str, Any],
) -> tuple[Path, list[dict[str, Any]], bool]:
    # Base directory precedence:
    # CLI --base-dir > config.base_dir > "."
    base_dir = args.base_dir
    if args.base_dir == Path(".") and "base_dir" in config:
        base_dir = Path(str(config["base_dir"]))
    base_dir = base_dir.resolve()

    dry_run = not args.apply
    if not args.apply and "dry_run" in config:
        dry_run = bool(config["dry_run"])

    module_pattern_map = build_module_pattern_map(config)

    # If CLI --module is provided, use CLI specs and ignore config.modules.
    if args.module:
        specs = []
        for module in args.module:
            specs.append(
                {
                    "path": module,
                    "pattern": resolve_pattern_for_module(
                        module_path=module,
                        cli_pattern=args.pattern,
                        module_pattern_map=module_pattern_map,
                    ),
                    "only_subdirs": args.subdir or [],
                    "exclude_subdirs": args.exclude_subdir or [],
                }
            )
        return base_dir, specs, dry_run

    # Else use config.modules if present.
    if "modules" in config:
        modules = config["modules"]
        if not isinstance(modules, list):
            raise ValueError("config.modules must be a list.")
        specs = []
        for item in modules:
            if not isinstance(item, dict):
                raise ValueError("Each module config must be an object.")
            if "path" not in item:
                raise ValueError("Each module config must contain 'path'.")
            specs.append(
                {
                    "path": str(item["path"]),
                    "pattern": str(
                        item.get(
                            "pattern",
                            resolve_pattern_for_module(
                                module_path=str(item["path"]),
                                cli_pattern=args.pattern,
                                module_pattern_map=module_pattern_map,
                            ),
                        )
                    ),
                    "only_subdirs": list(item.get("only_subdirs", [])),
                    "exclude_subdirs": list(item.get("exclude_subdirs", [])),
                }
            )
        return base_dir, specs, dry_run

    # Fallback default: current task's module.
    return (
        base_dir,
        [
            {
                "path": "07-inequality",
                "pattern": resolve_pattern_for_module(
                    module_path="07-inequality",
                    cli_pattern=args.pattern,
                    module_pattern_map=module_pattern_map,
                ),
                "only_subdirs": args.subdir or [],
                "exclude_subdirs": args.exclude_subdir or [],
            }
        ],
        dry_run,
    )


def select_target_dirs(base_dir: Path, spec: dict[str, Any]) -> list[Path]:
    module_dir = (base_dir / spec["path"]).resolve()
    if not module_dir.exists():
        raise FileNotFoundError(f"Module not found: {module_dir}")
    if not module_dir.is_dir():
        raise NotADirectoryError(f"Module is not a directory: {module_dir}")
    if not is_within(base_dir, module_dir):
        raise ValueError(f"Unsafe module path outside base-dir: {module_dir}")

    pattern = re.compile(spec.get("pattern") or DEFAULT_PATTERN)
    only_subdirs = set(spec.get("only_subdirs") or [])
    exclude_subdirs = set(spec.get("exclude_subdirs") or [])

    targets: list[Path] = []
    for child in module_dir.iterdir():
        if not child.is_dir():
            continue
        name = child.name
        if not pattern.match(name):
            continue
        if only_subdirs and name not in only_subdirs:
            continue
        if name in exclude_subdirs:
            continue
        targets.append(child)
    return sorted(targets)


def delete_files_under_dir(target_dir: Path, dry_run: bool) -> tuple[int, int]:
    deleted = 0
    failed = 0
    for path in target_dir.rglob("*"):
        if not path.is_file():
            continue
        try:
            if dry_run:
                print(f"[DRY-RUN] delete file: {path}")
            else:
                path.unlink()
                print(f"[DELETED] {path}")
            deleted += 1
        except OSError as exc:
            failed += 1
            print(f"[ERROR] cannot delete {path}: {exc}", file=sys.stderr)
    return deleted, failed


def main() -> int:
    args = parse_args()

    config: dict[str, Any] = {}
    if args.config:
        config = load_json(args.config.resolve())

    base_dir, module_specs, dry_run = normalize_module_specs(args, config)
    mode = "DRY-RUN" if dry_run else "APPLY"
    print(f"[MODE] {mode}")
    print(f"[BASE] {base_dir}")

    total_deleted = 0
    total_failed = 0
    total_target_dirs = 0

    for spec in module_specs:
        module_path = spec["path"]
        targets = select_target_dirs(base_dir, spec)
        print(f"\n[MODULE] {module_path}")
        print(f"[PATTERN] {spec['pattern']}")
        print(f"[TARGET DIR COUNT] {len(targets)}")
        for t in targets:
            print(f"  - {t}")

        for target_dir in targets:
            deleted, failed = delete_files_under_dir(target_dir, dry_run=dry_run)
            total_deleted += deleted
            total_failed += failed
            total_target_dirs += 1

    print("\n[SUMMARY]")
    print(f"target_dirs={total_target_dirs}")
    print(f"files_processed={total_deleted}")
    print(f"errors={total_failed}")
    if dry_run:
        print("No files were deleted. Add --apply to perform deletion.")

    return 1 if total_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
