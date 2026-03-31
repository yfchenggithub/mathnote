#!/usr/bin/env python3
"""
Create scaffold files inside selected child directories (keep directories).

Default behavior:
- Module: 07-inequality
- Subdirectory match:
  1) CLI --pattern (highest priority)
  2) config.module_patterns[module_path] (if provided)
  3) inferred from module name, e.g. 01-function -> ^F\\d{2}
- Dry-run only (no write) unless --apply is given
- Existing files are kept unless --overwrite is given

Examples:
1) Preview create for one module:
   python scripts/create_prefixed_dirs_files.py --module 07-inequality

2) Actually create files:
   python scripts/create_prefixed_dirs_files.py --module 07-inequality --apply

3) Create for selected subdirectories:
   python scripts/create_prefixed_dirs_files.py --module 07-inequality \
       --subdir I01_Compound_Inequality_Transformation --subdir I02_Basic_Inequalities_and_Variations --apply

4) Use JSON config:
   python scripts/create_prefixed_dirs_files.py --config scripts/create_prefixed_dirs_files.example.json --apply
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


DEFAULT_PATTERN = r"^[A-Z]\d{2}"
DEFAULT_FILE_NAMES = [
    "01_statement.tex",
    "02_explanation.tex",
    "03_proof.tex",
    "04_examples.tex",
    "05_traps.tex",
    "06_summary.tex",
    "main.tex",
    "meta.json",
    "source.tex",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create files inside selected child directories."
    )
    parser.add_argument("--config", type=Path, help="Path to JSON config file.")
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
        help="Only process these exact subdirectory names. Can be repeated.",
    )
    parser.add_argument(
        "--exclude-subdir",
        action="append",
        help="Exclude these exact subdirectory names. Can be repeated.",
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
        "--file",
        action="append",
        help="File name (or relative path) to create in each target subdirectory. Can be repeated.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files. Without this, existing files are kept.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually create files. Without this flag, script runs in dry-run mode.",
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


def normalize_file_list(raw: Any) -> list[str]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ValueError("File list must be an array.")

    out: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            raise ValueError("Each file name must be a string.")
        name = item.strip()
        if not name:
            continue
        out.append(name)
    return out


def normalize_module_specs(
    args: argparse.Namespace,
    config: dict[str, Any],
) -> tuple[Path, list[dict[str, Any]], bool]:
    base_dir = args.base_dir
    if args.base_dir == Path(".") and "base_dir" in config:
        base_dir = Path(str(config["base_dir"]))
    base_dir = base_dir.resolve()

    dry_run = not args.apply
    if not args.apply and "dry_run" in config:
        dry_run = bool(config["dry_run"])

    module_pattern_map = build_module_pattern_map(config)
    config_default_files = normalize_file_list(config.get("default_files")) or list(
        DEFAULT_FILE_NAMES
    )
    cli_files = args.file or []

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
                    "files": cli_files or config_default_files,
                }
            )
        return base_dir, specs, dry_run

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

            module_path = str(item["path"])
            item_files = normalize_file_list(item.get("files"))
            specs.append(
                {
                    "path": module_path,
                    "pattern": str(
                        item.get(
                            "pattern",
                            resolve_pattern_for_module(
                                module_path=module_path,
                                cli_pattern=args.pattern,
                                module_pattern_map=module_pattern_map,
                            ),
                        )
                    ),
                    "only_subdirs": list(item.get("only_subdirs", [])),
                    "exclude_subdirs": list(item.get("exclude_subdirs", [])),
                    "files": cli_files or item_files or config_default_files,
                }
            )
        return base_dir, specs, dry_run

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
                "files": cli_files or config_default_files,
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


def create_files_under_dir(
    target_dir: Path,
    file_names: list[str],
    dry_run: bool,
    overwrite: bool,
) -> tuple[int, int, int]:
    created = 0
    skipped_existing = 0
    failed = 0

    for rel_name in file_names:
        candidate = target_dir / rel_name
        resolved = candidate.resolve()
        if not is_within(target_dir.resolve(), resolved):
            failed += 1
            print(
                f"[ERROR] unsafe file path (outside target dir): {candidate}",
                file=sys.stderr,
            )
            continue

        if resolved.exists():
            if resolved.is_dir():
                failed += 1
                print(f"[ERROR] target path is a directory: {resolved}", file=sys.stderr)
                continue
            if not overwrite:
                skipped_existing += 1
                print(f"[SKIP] exists: {resolved}")
                continue
            if dry_run:
                print(f"[DRY-RUN] overwrite file: {resolved}")
            else:
                resolved.parent.mkdir(parents=True, exist_ok=True)
                resolved.write_text("", encoding="utf-8")
                print(f"[OVERWRITTEN] {resolved}")
            created += 1
            continue

        if dry_run:
            print(f"[DRY-RUN] create file: {resolved}")
        else:
            resolved.parent.mkdir(parents=True, exist_ok=True)
            resolved.write_text("", encoding="utf-8")
            print(f"[CREATED] {resolved}")
        created += 1

    return created, skipped_existing, failed


def main() -> int:
    args = parse_args()

    config: dict[str, Any] = {}
    if args.config:
        config = load_json(args.config.resolve())

    base_dir, module_specs, dry_run = normalize_module_specs(args, config)
    mode = "DRY-RUN" if dry_run else "APPLY"
    print(f"[MODE] {mode}")
    print(f"[BASE] {base_dir}")
    print(f"[OVERWRITE] {args.overwrite}")

    total_dirs = 0
    total_created = 0
    total_skipped = 0
    total_failed = 0

    for spec in module_specs:
        module_path = spec["path"]
        targets = select_target_dirs(base_dir, spec)
        files = spec.get("files") or list(DEFAULT_FILE_NAMES)

        print(f"\n[MODULE] {module_path}")
        print(f"[PATTERN] {spec['pattern']}")
        print(f"[FILES PER DIR] {len(files)}")
        for name in files:
            print(f"  - {name}")
        print(f"[TARGET DIR COUNT] {len(targets)}")
        for t in targets:
            print(f"  - {t}")

        for target_dir in targets:
            created, skipped_existing, failed = create_files_under_dir(
                target_dir=target_dir,
                file_names=files,
                dry_run=dry_run,
                overwrite=args.overwrite,
            )
            total_created += created
            total_skipped += skipped_existing
            total_failed += failed
            total_dirs += 1

    print("\n[SUMMARY]")
    print(f"target_dirs={total_dirs}")
    print(f"created_or_overwritten={total_created}")
    print(f"skipped_existing={total_skipped}")
    print(f"errors={total_failed}")
    if dry_run:
        print("No files were created. Add --apply to perform creation.")

    return 1 if total_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

