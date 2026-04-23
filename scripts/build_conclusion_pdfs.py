#!/usr/bin/env python
"""
Build one PDF per conclusion directory and emit an ID->PDF-name JSON map.

Examples:
  python scripts/build_conclusion_pdfs.py --dry-run
  python scripts/build_conclusion_pdfs.py S001 I001
  python scripts/build_conclusion_pdfs.py --modules 00_set 07_inequality --ids S001 I001
  python scripts/build_conclusion_pdfs.py --modules 00_set --conclusions S001_Subset_Count --pdf-name-mode id
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_MODULES = [
    "00_set",
    "01_function",
    "02_sequence",
    "03_conic",
    "04_vector",
    "05_geometry-solid",
    "06_probability-stat",
    "07_inequality",
    "08_trigonometry",
    "09_geometry-plane",
]

DEFAULT_OUTPUT_DIR = Path("build/conclusion_pdfs")
DEFAULT_MAP_JSON = Path("build/conclusion_pdf_map.json")
MODULE_PREFIX_MAP_JSON = Path("12_pipeline/config/module_prefix_map.json")
ID_PATTERN = re.compile(r"^([A-Za-z]\d{3})")


@dataclass(frozen=True)
class ConclusionItem:
    module: str
    folder_name: str
    folder_path: Path
    conclusion_id: str

    @property
    def main_tex(self) -> Path:
        return self.folder_path / "main.tex"

    def relative_main_tex(self, repo_root: Path) -> str:
        return self.main_tex.relative_to(repo_root).as_posix()


@dataclass
class BuildResult:
    item: ConclusionItem
    pdf_name: str
    status: str  # success | failed | skipped
    message: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compile selected second-level conclusion directories into standalone PDFs "
            "and write an ID->PDF-name JSON mapping."
        )
    )
    parser.add_argument(
        "--modules",
        nargs="*",
        default=None,
        help=(
            "Modules to include (default: all 00_set~09_geometry-plane). "
            "Supports comma and/or space separated values."
        ),
    )
    parser.add_argument(
        "--ids",
        nargs="*",
        default=None,
        help="Conclusion IDs to include (e.g. I001 S001). Supports comma and/or space separation.",
    )
    parser.add_argument(
        "positional_ids",
        nargs="*",
        help=(
            "Shorthand IDs, equivalent to --ids (e.g. I001 S001). "
            "If --modules is omitted, modules are auto-derived from "
            "12_pipeline/config/module_prefix_map.json."
        ),
    )
    parser.add_argument(
        "--conclusions",
        nargs="*",
        default=None,
        help=(
            "Conclusion folder names to include (e.g. S001_Subset_Count). "
            "Supports comma and/or space separation."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory for PDFs (default: {DEFAULT_OUTPUT_DIR.as_posix()}).",
    )
    parser.add_argument(
        "--map-json",
        default=str(DEFAULT_MAP_JSON),
        help=f"Output JSON path for ID->PDF mapping (default: {DEFAULT_MAP_JSON.as_posix()}).",
    )
    parser.add_argument(
        "--pdf-name-mode",
        choices=("id", "folder"),
        default="folder",
        help='PDF naming: "id" -> I001.pdf, "folder" -> I001_topic_name.pdf (default: folder).',
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output PDF files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List planned tasks only. No compile, no output writes.",
    )
    return parser.parse_args()


def split_csv_tokens(values: list[str] | None) -> list[str]:
    if not values:
        return []
    tokens: list[str] = []
    for raw in values:
        for token in raw.split(","):
            piece = token.strip()
            if piece:
                tokens.append(piece)
    return tokens


def dedupe_keep_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            deduped.append(value)
    return deduped


def normalize_modules(raw_modules: list[str] | None) -> list[str]:
    if raw_modules is None:
        return list(DEFAULT_MODULES)

    candidates = split_csv_tokens(raw_modules)
    if not candidates:
        return list(DEFAULT_MODULES)

    normalized = dedupe_keep_order(candidates)
    unknown = [module for module in normalized if module not in DEFAULT_MODULES]
    if unknown:
        allowed = ", ".join(DEFAULT_MODULES)
        bad = ", ".join(unknown)
        raise ValueError(f"Unknown modules: {bad}. Allowed modules: {allowed}")
    return normalized


def normalize_ids(raw_ids: list[str] | None) -> list[str]:
    ids = [token.upper() for token in split_csv_tokens(raw_ids)]
    ids = dedupe_keep_order(ids)
    invalid = [value for value in ids if not re.fullmatch(r"[A-Za-z]\d{3}", value)]
    if invalid:
        bad = ", ".join(invalid)
        raise ValueError(f"Invalid --ids values: {bad}. Expected format like I001.")
    return ids


def normalize_conclusions(raw_conclusions: list[str] | None) -> list[str]:
    return dedupe_keep_order(split_csv_tokens(raw_conclusions))


def load_module_prefix_map(repo_root: Path) -> dict[str, str]:
    map_path = repo_root / MODULE_PREFIX_MAP_JSON
    if not map_path.is_file():
        raise FileNotFoundError(f"Module-prefix map not found: {map_path}")

    try:
        raw = json.loads(map_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {map_path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValueError(f"Invalid map structure in {map_path}: expected JSON object.")

    cleaned: dict[str, str] = {}
    for module, prefix in raw.items():
        if not isinstance(module, str) or not module.strip():
            raise ValueError(f"Invalid module key in {map_path}: {module!r}")
        if not isinstance(prefix, str):
            raise ValueError(f"Invalid prefix type for module {module!r}: {type(prefix).__name__}")

        normalized_prefix = prefix.strip().upper()
        if not re.fullmatch(r"[A-Z]", normalized_prefix):
            raise ValueError(
                f"Invalid prefix for module {module!r}: {prefix!r}. Expected one letter."
            )
        cleaned[module.strip()] = normalized_prefix

    return cleaned


def build_prefix_to_module_map(module_prefix_map: dict[str, str]) -> dict[str, str]:
    prefix_to_module: dict[str, str] = {}
    conflicts: dict[str, list[str]] = {}

    for module, prefix in module_prefix_map.items():
        existing = prefix_to_module.get(prefix)
        if existing is None:
            prefix_to_module[prefix] = module
            continue

        conflicts.setdefault(prefix, [existing]).append(module)

    if conflicts:
        lines = [
            "Duplicate prefix mappings detected in module_prefix_map.json "
            "(cannot auto-resolve IDs):"
        ]
        for prefix, modules in sorted(conflicts.items()):
            lines.append(f"  - {prefix}: {', '.join(sorted(set(modules)))}")
        raise ValueError("\n".join(lines))

    return prefix_to_module


def resolve_modules(
    raw_modules: list[str] | None,
    ids: list[str],
    repo_root: Path,
) -> tuple[list[str], str]:
    if raw_modules is not None:
        return normalize_modules(raw_modules), "explicit (--modules)"

    if not ids:
        return list(DEFAULT_MODULES), "default (all)"

    module_prefix_map = load_module_prefix_map(repo_root)
    prefix_to_module = build_prefix_to_module_map(module_prefix_map)

    prefixes = dedupe_keep_order(item[0].upper() for item in ids)
    missing = [prefix for prefix in prefixes if prefix not in prefix_to_module]
    if missing:
        raise ValueError(
            "Missing module mapping for ID prefix(es): "
            f"{', '.join(missing)}. Please update {MODULE_PREFIX_MAP_JSON.as_posix()}."
        )

    modules = dedupe_keep_order(prefix_to_module[prefix] for prefix in prefixes)
    return modules, f"derived from ID prefix map ({MODULE_PREFIX_MAP_JSON.as_posix()})"


def discover_conclusions(repo_root: Path, modules: list[str]) -> list[ConclusionItem]:
    items: list[ConclusionItem] = []
    for module in modules:
        module_dir = repo_root / module
        if not module_dir.is_dir():
            raise FileNotFoundError(f"Module directory does not exist: {module_dir}")

        for child in sorted(module_dir.iterdir()):
            if not child.is_dir():
                continue
            main_tex = child / "main.tex"
            if not main_tex.is_file():
                continue

            match = ID_PATTERN.match(child.name)
            if not match:
                continue

            conclusion_id = match.group(1).upper()
            items.append(
                ConclusionItem(
                    module=module,
                    folder_name=child.name,
                    folder_path=child,
                    conclusion_id=conclusion_id,
                )
            )
    return items


def filter_items(
    items: list[ConclusionItem], ids: list[str], conclusions: list[str]
) -> list[ConclusionItem]:
    id_set = set(ids)
    conclusion_set = set(conclusions)

    filtered: list[ConclusionItem] = []
    for item in items:
        if id_set and item.conclusion_id not in id_set:
            continue
        if conclusion_set and item.folder_name not in conclusion_set:
            continue
        filtered.append(item)
    return filtered


def warn_unmatched_filters(
    selected_items: list[ConclusionItem], ids: list[str], conclusions: list[str]
) -> None:
    selected_ids = {item.conclusion_id for item in selected_items}
    selected_folders = {item.folder_name for item in selected_items}

    missing_ids = [item_id for item_id in ids if item_id not in selected_ids]
    missing_folders = [name for name in conclusions if name not in selected_folders]

    if missing_ids:
        print(f"[warn] Requested IDs not matched after filtering: {', '.join(missing_ids)}")
    if missing_folders:
        print(
            "[warn] Requested conclusion folders not matched after filtering: "
            f"{', '.join(missing_folders)}"
        )


def ensure_unique_ids(items: list[ConclusionItem]) -> None:
    index: dict[str, list[ConclusionItem]] = {}
    for item in items:
        index.setdefault(item.conclusion_id, []).append(item)

    conflicts = {k: v for k, v in index.items() if len(v) > 1}
    if not conflicts:
        return

    lines = ["Duplicate conclusion IDs detected. Mapping JSON requires unique ID keys:"]
    for conclusion_id, group in sorted(conflicts.items()):
        refs = ", ".join(
            f"{entry.module}/{entry.folder_name}" for entry in sorted(group, key=lambda i: i.folder_name)
        )
        lines.append(f"  - {conclusion_id}: {refs}")
    raise ValueError("\n".join(lines))


def build_pdf_name(item: ConclusionItem, mode: str) -> str:
    if mode == "id":
        return f"{item.conclusion_id}.pdf"
    return f"{item.folder_name}.pdf"


def ensure_unique_pdf_names(items: list[ConclusionItem], mode: str) -> None:
    name_map: dict[str, list[ConclusionItem]] = {}
    for item in items:
        name = build_pdf_name(item, mode)
        name_map.setdefault(name, []).append(item)

    conflicts = {k: v for k, v in name_map.items() if len(v) > 1}
    if not conflicts:
        return

    lines = ["Duplicate output PDF names detected for current selection:"]
    for pdf_name, group in sorted(conflicts.items()):
        refs = ", ".join(f"{entry.module}/{entry.folder_name}" for entry in group)
        lines.append(f"  - {pdf_name}: {refs}")
    raise ValueError("\n".join(lines))


def build_wrapper_tex(rel_main_tex: str) -> str:
    # Keep this wrapper aligned with the requested structure.
    return (
        "\\documentclass[12pt]{article}\n"
        "\n"
        "\\input{preamble}\n"
        "\\input{settings}\n"
        "\\graphicspath{{assets/figures/}{./}}\n"
        "\n"
        "\\begin{document}\n"
        f"\\input{{{rel_main_tex}}}\n"
        "\\end{document}\n"
    )


def truncate_tail(text: str, max_lines: int = 25) -> str:
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text.strip()
    return "\n".join(lines[-max_lines:]).strip()


def compile_one(
    repo_root: Path,
    output_dir: Path,
    item: ConclusionItem,
    pdf_name_mode: str,
    overwrite: bool,
) -> BuildResult:
    pdf_name = build_pdf_name(item, pdf_name_mode)
    target_pdf = output_dir / pdf_name
    if target_pdf.exists() and not overwrite:
        return BuildResult(
            item=item,
            pdf_name=pdf_name,
            status="skipped",
            message="target already exists (use --overwrite to rebuild)",
        )

    wrapper_stem = f"_tmp_conclusion_{item.conclusion_id}_{uuid.uuid4().hex}"
    wrapper_path = repo_root / f"{wrapper_stem}.tex"
    wrapper_text = build_wrapper_tex(item.relative_main_tex(repo_root))

    try:
        wrapper_path.write_text(wrapper_text, encoding="utf-8", newline="\n")
        with tempfile.TemporaryDirectory(prefix="latexmk_", dir=str(output_dir)) as temp_build_dir:
            cmd = [
                "latexmk",
                "-xelatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={temp_build_dir}",
                str(wrapper_path),
            ]
            try:
                proc = subprocess.run(
                    cmd,
                    cwd=str(repo_root),
                    capture_output=True,
                    text=True,
                    errors="replace",
                    check=False,
                )
            except FileNotFoundError:
                return BuildResult(
                    item=item,
                    pdf_name=pdf_name,
                    status="failed",
                    message="latexmk not found in PATH.",
                )

            if proc.returncode != 0:
                merged = (proc.stdout or "") + "\n" + (proc.stderr or "")
                excerpt = truncate_tail(merged)
                return BuildResult(
                    item=item,
                    pdf_name=pdf_name,
                    status="failed",
                    message=f"latexmk failed.\n{excerpt}",
                )

            built_pdf = Path(temp_build_dir) / f"{wrapper_stem}.pdf"
            if not built_pdf.is_file():
                return BuildResult(
                    item=item,
                    pdf_name=pdf_name,
                    status="failed",
                    message=f"Compiled PDF not found: {built_pdf}",
                )

            shutil.copy2(built_pdf, target_pdf)
            return BuildResult(item=item, pdf_name=pdf_name, status="success")
    finally:
        try:
            wrapper_path.unlink(missing_ok=True)
        except Exception:
            pass


def write_json(path: Path, payload: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered_payload = {key: payload[key] for key in sorted(payload)}
    path.write_text(
        json.dumps(ordered_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent

    try:
        raw_ids = split_csv_tokens(args.ids) + split_csv_tokens(args.positional_ids)
        ids = normalize_ids(raw_ids)
        conclusions = normalize_conclusions(args.conclusions)
        modules, module_source = resolve_modules(args.modules, ids, repo_root)
    except (ValueError, FileNotFoundError) as exc:
        print(f"[error] {exc}")
        return 2

    discovered = discover_conclusions(repo_root, modules)
    selected = filter_items(discovered, ids, conclusions)
    warn_unmatched_filters(selected, ids, conclusions)

    if not selected:
        print("[error] No conclusions matched the given filters.")
        return 2

    try:
        ensure_unique_ids(selected)
        ensure_unique_pdf_names(selected, args.pdf_name_mode)
    except ValueError as exc:
        print(f"[error] {exc}")
        return 2

    output_dir = (repo_root / Path(args.output_dir)).resolve()
    map_json_path = (repo_root / Path(args.map_json)).resolve()

    print(f"[info] Repo root: {repo_root}")
    print(f"[info] Modules ({module_source}): {', '.join(modules)}")
    print(f"[info] Selected conclusions: {len(selected)}")
    print(f"[info] PDF output dir: {output_dir}")
    print(f"[info] Map JSON path: {map_json_path}")
    print(f"[info] PDF naming mode: {args.pdf_name_mode}")

    if args.dry_run:
        print("[dry-run] Planned tasks:")
        for item in selected:
            pdf_name = build_pdf_name(item, args.pdf_name_mode)
            print(f"  - {item.conclusion_id}: {item.module}/{item.folder_name} -> {pdf_name}")
        print("[dry-run] No files written.")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    map_json_path.parent.mkdir(parents=True, exist_ok=True)

    mapping: dict[str, str] = {}
    results: list[BuildResult] = []
    total = len(selected)

    for index, item in enumerate(selected, start=1):
        pdf_name = build_pdf_name(item, args.pdf_name_mode)
        print(f"[build] ({index}/{total}) {item.module}/{item.folder_name} -> {pdf_name}")
        result = compile_one(
            repo_root=repo_root,
            output_dir=output_dir,
            item=item,
            pdf_name_mode=args.pdf_name_mode,
            overwrite=args.overwrite,
        )
        results.append(result)

        if result.status in {"success", "skipped"}:
            mapping[item.conclusion_id] = result.pdf_name
            if result.status == "success":
                print("        status: success")
            else:
                print(f"        status: skipped ({result.message})")
        else:
            print("        status: failed")
            if result.message:
                print("        details:")
                for line in result.message.splitlines():
                    print(f"          {line}")

    write_json(map_json_path, mapping)

    success_count = sum(1 for result in results if result.status == "success")
    skipped_count = sum(1 for result in results if result.status == "skipped")
    failed = [result for result in results if result.status == "failed"]

    print("[summary]")
    print(f"  success: {success_count}")
    print(f"  skipped: {skipped_count}")
    print(f"  failed : {len(failed)}")
    print(f"  map json written: {map_json_path}")

    if failed:
        print("[summary] Failed items:")
        for result in failed:
            print(f"  - {result.item.conclusion_id} ({result.item.module}/{result.item.folder_name})")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
