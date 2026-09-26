"""Read-only discovery of conclusion sources in the fixed module set."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


MODULE_NAMES: tuple[str, ...] = (
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
    "10_junior_basics",
)


@dataclass(frozen=True)
class ConclusionSource:
    module_name: str
    conclusion_dir_name: str
    conclusion_path: Path
    meta_json_path: Path


@dataclass(frozen=True)
class ValidationError:
    path: Path
    message: str


@dataclass(frozen=True)
class ModuleScanResult:
    module_name: str
    sources: tuple[ConclusionSource, ...]


@dataclass(frozen=True)
class ScanResult:
    modules: tuple[ModuleScanResult, ...]
    errors: tuple[ValidationError, ...]

    @property
    def conclusion_count(self) -> int:
        return sum(len(module.sources) for module in self.modules)


def _validate_meta(source: ConclusionSource) -> ValidationError | None:
    meta_path = source.meta_json_path
    display_path = Path(source.module_name) / source.conclusion_dir_name / "meta.json"

    if not meta_path.exists():
        return ValidationError(display_path, "missing meta.json")
    if not meta_path.is_file():
        return ValidationError(display_path, "meta.json is not a regular file")

    try:
        with meta_path.open("r", encoding="utf-8") as meta_file:
            json.load(meta_file)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return ValidationError(display_path, f"invalid JSON: {exc}")
    return None


def scan_repository(project_root: Path) -> ScanResult:
    """Discover direct child directories in the fixed module whitelist."""

    modules: list[ModuleScanResult] = []
    errors: list[ValidationError] = []

    for module_name in MODULE_NAMES:
        module_path = project_root / module_name
        if not module_path.is_dir():
            modules.append(ModuleScanResult(module_name, ()))
            errors.append(ValidationError(Path(module_name), "module directory is missing"))
            continue

        child_directories = sorted(
            (child for child in module_path.iterdir() if child.is_dir()),
            key=lambda child: child.name,
        )
        sources = tuple(
            ConclusionSource(
                module_name=module_name,
                conclusion_dir_name=child.name,
                conclusion_path=child,
                meta_json_path=child / "meta.json",
            )
            for child in child_directories
        )
        modules.append(ModuleScanResult(module_name, sources))

        for source in sources:
            validation_error = _validate_meta(source)
            if validation_error is not None:
                errors.append(validation_error)

    return ScanResult(tuple(modules), tuple(errors))

