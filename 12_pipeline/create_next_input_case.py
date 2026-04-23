#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
每次需要找到下一个模块 ID 来创建新的输入案例时，运行此脚本。
人工找到下一个模块 ID 太麻烦了，脚本会自动扫描现有模块目录和已创建的案例目录，计算下一个可用的 ID，并创建对应的输入案例目录，同时复制 source.tex 作为模板。
source.tex 这个文件就是截图在deepseek或者gpt中获取的latex格式的内容
唯一一个需要手工操作的地方，因为deepseek不支持图片->latex的批量处理，所以只能一个一个截图获取source.tex文件，放在12_pipeline目录下。
Create next pipeline input case directory and copy source.tex.

Usage example:
    python 12_pipeline/create_next_input_case.py --print-mapping
    python 12_pipeline/create_next_input_case.py pm
    python 12_pipeline/create_next_input_case.py c
    python 12_pipeline/create_next_input_case.py conic
    python 12_pipeline/create_next_input_case.py 03
    python 12_pipeline/create_next_input_case.py 03_conic
    python 12_pipeline/create_next_input_case.py --module-dir d:/mathnote/03_conic
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

DEFAULT_MODULE_PREFIX_MAP: dict[str, str] = {
    "00_set": "S",
    "01_function": "F",
    "02_sequence": "L",
    "03_conic": "C",
    "04_vector": "V",
    "05_geometry-solid": "G",
    "06_probability-stat": "R",
    "07_inequality": "I",
    "08_trigonometry": "T",
    "09_geometry-plane": "P",
    "10_final": "O",
}

SINGLE_LETTER_PATTERN = re.compile(r"^[A-Za-z]$")
MODULE_DIR_PATTERN = re.compile(r"^\d{2}[_-].+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Find the next module <PREFIX><3-digit> ID, "
            "create 12_pipeline/input/<ID>, and copy 12_pipeline/source.tex."
        )
    )
    parser.add_argument(
        "module",
        nargs="?",
        help=(
            "Module selector (short form), e.g. conic / 03 / 03_conic. "
            "Equivalent to selecting module directory d:\\mathnote\\03_conic."
        ),
    )
    parser.add_argument(
        "--module-dir",
        type=Path,
        required=False,
        help="Module directory path, e.g. d:\\mathnote\\03_conic",
    )
    parser.add_argument(
        "--pipeline-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Pipeline directory path. Default: directory of this script.",
    )
    parser.add_argument(
        "--id-prefix",
        type=str,
        default=None,
        help="Optional manual prefix override (single letter).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions only, do not create/copy case files.",
    )
    parser.add_argument(
        "--print-mapping",
        action="store_true",
        help=(
            "Print current module mapping rules "
            "(module -> ID prefix -> supported selectors)."
        ),
    )
    return parser.parse_args()


def normalize_prefix(prefix: str) -> str:
    value = prefix.strip().upper()
    if not SINGLE_LETTER_PATTERN.fullmatch(value):
        raise ValueError(f"Invalid prefix: {prefix!r}. Expected one letter like C/F/I.")
    return value


def normalize_key(text: str) -> str:
    return re.sub(r"[-_\s]+", "-", text.strip().lower())


def list_module_dirs(
    project_root: Path,
    allowed_module_names: set[str] | None = None,
) -> list[Path]:
    return sorted(
        [
            p
            for p in project_root.iterdir()
            if p.is_dir()
            and MODULE_DIR_PATTERN.match(p.name)
            and (allowed_module_names is None or p.name in allowed_module_names)
        ],
        key=lambda p: p.name.lower(),
    )


def split_module_name(module_name: str) -> tuple[str | None, str]:
    match = re.match(r"^(\d{2})[_-](.+)$", module_name)
    if match:
        return match.group(1), match.group(2)
    return None, module_name


def print_current_mapping_rules(project_root: Path, prefix_map: dict[str, str]) -> None:
    module_dirs = list_module_dirs(project_root, set(prefix_map.keys()))
    if not module_dirs:
        print(f"No module directories found under: {project_root}")
        return

    prefix_to_modules: dict[str, list[str]] = {}
    for module_dir in module_dirs:
        prefix = prefix_map.get(module_dir.name, "").upper()
        if prefix:
            prefix_to_modules.setdefault(prefix, []).append(module_dir.name)

    print("Current module mapping rules:")
    print("Format: <module> -> prefix=<X>; selectors: ...")
    for module_dir in module_dirs:
        module_name = module_dir.name
        index, suffix = split_module_name(module_name)
        prefix = prefix_map.get(module_name, "").upper()

        selectors: list[str] = [module_name]
        if index:
            selectors.append(index)
        selectors.append(suffix)

        if prefix:
            if len(prefix_to_modules.get(prefix, [])) == 1:
                selectors.append(prefix.lower())
            else:
                selectors.append(f"{prefix.lower()}(conflict)")
        else:
            prefix = "?"

        print(f"- {module_name} -> prefix={prefix}; selectors: {', '.join(selectors)}")


def resolve_module_dir(
    pipeline_dir: Path,
    module_selector: str | None,
    module_dir_arg: Path | None,
    prefix_map: dict[str, str],
) -> Path:
    if module_selector and module_dir_arg:
        raise ValueError(
            "Please pass either positional module selector or --module-dir, not both."
        )

    if module_dir_arg:
        return module_dir_arg.expanduser().resolve()

    if not module_selector:
        raise ValueError(
            "Missing module selector. Use one of: conic / 03 / 03_conic "
            "(or pass --module-dir)."
        )

    project_root = pipeline_dir.parent
    module_dirs = list_module_dirs(project_root, set(prefix_map.keys()))
    if not module_dirs:
        raise ValueError(
            f"No mapped module directories found under: {project_root}. "
            "Check module_prefix_map.json."
        )

    token = module_selector.strip()
    if not token:
        raise ValueError("Module selector cannot be empty.")

    # 1) Exact module dir name, e.g. "03_conic"
    exact_hits = [p for p in module_dirs if p.name.lower() == token.lower()]
    if len(exact_hits) == 1:
        return exact_hits[0]

    # 2) Two-digit index, e.g. "03"
    if re.fullmatch(r"\d{2}", token):
        prefix_hits = [
            p for p in module_dirs if re.match(rf"^{re.escape(token)}[_-]", p.name)
        ]
        if len(prefix_hits) == 1:
            return prefix_hits[0]
        if len(prefix_hits) > 1:
            joined = ", ".join(p.name for p in prefix_hits)
            raise ValueError(f"Ambiguous module selector {token!r}: {joined}")

    # 3) Single-letter selector by configured module prefix, e.g. "c" -> "03_conic"
    if re.fullmatch(r"[A-Za-z]", token):
        letter = token.upper()
        letter_hits = [
            p
            for p in module_dirs
            if prefix_map.get(p.name, "").strip().upper() == letter
        ]
        if len(letter_hits) == 1:
            return letter_hits[0]
        if len(letter_hits) > 1:
            joined = ", ".join(p.name for p in letter_hits)
            raise ValueError(
                f"Ambiguous module selector {token!r} by prefix mapping: {joined}. "
                "Run with --print-mapping."
            )

    # 3) Alias by suffix, e.g. "conic" -> "03_conic"
    norm_token = normalize_key(token)
    alias_hits: list[Path] = []
    for p in module_dirs:
        matched = False
        if normalize_key(p.name) == norm_token:
            matched = True
        else:
            suffix_match = re.match(r"^\d{2}[_-](.+)$", p.name)
            if suffix_match and normalize_key(suffix_match.group(1)) == norm_token:
                matched = True
        if matched:
            alias_hits.append(p)

    if len(alias_hits) == 1:
        return alias_hits[0]
    if len(alias_hits) > 1:
        joined = ", ".join(p.name for p in alias_hits)
        raise ValueError(f"Ambiguous module selector {token!r}: {joined}")

    available = ", ".join(p.name for p in module_dirs)
    raise ValueError(
        f"Cannot resolve module selector {token!r}. "
        f"Available modules: {available}. Run with --print-mapping."
    )


def normalize_module_prefix_map(raw: Any) -> dict[str, str]:
    if not isinstance(raw, dict):
        raise ValueError("module_prefix_map.json must be a JSON object.")

    normalized: dict[str, str] = {}
    for key, value in raw.items():
        if not isinstance(key, str):
            raise ValueError("module_prefix_map.json keys must be strings.")
        if not isinstance(value, str):
            raise ValueError(
                f"Invalid prefix for key {key!r}: expected string, got {type(value).__name__}."
            )
        normalized[key] = normalize_prefix(value)

    return normalized


def load_or_create_prefix_map(config_path: Path) -> dict[str, str]:
    existing: dict[str, str] = {}
    should_write_back = False

    if config_path.exists():
        try:
            raw = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {config_path}: {exc}") from exc
        existing = normalize_module_prefix_map(raw)
    else:
        should_write_back = True

    merged = dict(existing)
    for module_name, prefix in DEFAULT_MODULE_PREFIX_MAP.items():
        normalized_prefix = normalize_prefix(prefix)
        if merged.get(module_name) != normalized_prefix:
            merged[module_name] = normalized_prefix
            should_write_back = True

    if should_write_back:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(
            json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return merged


def resolve_prefix(
    module_dir: Path, prefix_map: dict[str, str], id_prefix: str | None
) -> str:
    if id_prefix:
        return normalize_prefix(id_prefix)

    module_name = module_dir.name
    if module_name not in prefix_map:
        raise ValueError(
            f"Module {module_name!r} is not configured in module_prefix_map.json. "
            "Please add it or pass --id-prefix."
        )

    return normalize_prefix(prefix_map[module_name])


def find_max_serial(module_dir: Path, prefix: str) -> int:
    pattern = re.compile(rf"^{re.escape(prefix)}(\d{{3}})(?:_|$)", re.IGNORECASE)
    max_serial = 0
    for child in module_dir.iterdir():
        if not child.is_dir():
            continue
        match = pattern.match(child.name)
        if not match:
            continue
        serial = int(match.group(1))
        if serial > max_serial:
            max_serial = serial
    return max_serial


def compute_next_module_id(module_dir: Path, prefix: str) -> str:
    max_serial = find_max_serial(module_dir, prefix)
    next_serial = max_serial + 1 if max_serial > 0 else 1

    if next_serial <= 999:
        return f"{prefix}{next_serial:03d}"

    raise RuntimeError(
        f"No available module IDs for prefix {prefix!r} in range {prefix}001-{prefix}999."
    )


def run(args: argparse.Namespace) -> None:
    pipeline_dir = args.pipeline_dir.expanduser().resolve()

    if not pipeline_dir.exists() or not pipeline_dir.is_dir():
        raise FileNotFoundError(f"Pipeline directory does not exist: {pipeline_dir}")

    # Positional alias: "pm" == "--print-mapping"
    if args.module and args.module.strip().lower() == "pm":
        if args.module_dir:
            raise ValueError("Selector 'pm' cannot be used together with --module-dir.")
        args.print_mapping = True
        args.module = None

    source_tex = pipeline_dir / "source.tex"
    input_dir = pipeline_dir / "input"
    if not source_tex.exists() or not source_tex.is_file():
        raise FileNotFoundError(f"Missing source file: {source_tex}")
    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"Missing input directory: {input_dir}")

    prefix_map_path = pipeline_dir / "config" / "module_prefix_map.json"
    prefix_map = load_or_create_prefix_map(prefix_map_path)
    project_root = pipeline_dir.parent

    if args.print_mapping:
        print_current_mapping_rules(project_root, prefix_map)
        if not args.module and not args.module_dir:
            return

    module_dir = resolve_module_dir(
        pipeline_dir, args.module, args.module_dir, prefix_map
    )
    if not module_dir.exists() or not module_dir.is_dir():
        raise FileNotFoundError(f"Module directory does not exist: {module_dir}")

    prefix = resolve_prefix(module_dir, prefix_map, args.id_prefix)

    new_id = compute_next_module_id(module_dir, prefix)
    target_dir = input_dir / new_id
    target_source = target_dir / "source.tex"

    if target_dir.exists():
        if not target_dir.is_dir():
            raise FileExistsError(f"Target exists but is not a directory: {target_dir}")
        print(f"[INFO] Target already exists, removing: {target_dir}")
        if args.dry_run:
            print(f"would remove {target_dir}")
        else:
            shutil.rmtree(target_dir)
            print(f"[INFO] Removed existing directory: {target_dir}")

    if args.dry_run:
        print(f"would create {target_dir}")
        print(f"would copy {source_tex} -> {target_source}")
    else:
        target_dir.mkdir(parents=True, exist_ok=False)
        print(f"[INFO] Created directory: {target_dir}")
        shutil.copy2(source_tex, target_source)
        print(f"[INFO] Copied source: {source_tex} -> {target_source}")

    print(f"NEW_ID={new_id}")
    print(f"TARGET_DIR={target_dir}")


def main() -> int:
    args = parse_args()
    try:
        run(args)
    except Exception as exc:  # pragma: no cover - CLI error handling
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
