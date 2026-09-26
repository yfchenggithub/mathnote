"""Safe, idempotent directory initialization for discovered sources."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

if __package__:
    from .source_discovery import ConclusionSource, ScanResult
else:
    from source_discovery import ConclusionSource, ScanResult


@dataclass(frozen=True)
class InitializationError:
    path: Path
    message: str


@dataclass(frozen=True)
class ModuleInitializationResult:
    module_name: str
    conclusion_count: int
    created_images: int
    created_pdfs: int
    already_initialized: int


@dataclass(frozen=True)
class InitializationResult:
    modules: tuple[ModuleInitializationResult, ...]
    errors: tuple[InitializationError, ...]

    @property
    def conclusion_count(self) -> int:
        return sum(module.conclusion_count for module in self.modules)

    @property
    def created_images(self) -> int:
        return sum(module.created_images for module in self.modules)

    @property
    def created_pdfs(self) -> int:
        return sum(module.created_pdfs for module in self.modules)

    @property
    def already_initialized(self) -> int:
        return sum(module.already_initialized for module in self.modules)


def _display_path(source: ConclusionSource, directory_name: str = "") -> Path:
    path = Path(source.module_name) / source.conclusion_dir_name
    return path / directory_name if directory_name else path


def _initialize_source(
    source: ConclusionSource,
) -> tuple[bool, bool, bool, tuple[InitializationError, ...]]:
    if not source.conclusion_path.is_dir():
        return False, False, False, (
            InitializationError(_display_path(source), "conclusion source directory is missing"),
        )

    targets = (
        ("images", source.conclusion_path / "images"),
        ("pdfs", source.conclusion_path / "pdfs"),
    )
    errors = tuple(
        InitializationError(
            _display_path(source, name),
            f"{name} exists but is not a directory",
        )
        for name, path in targets
        if path.exists() and not path.is_dir()
    )
    if errors:
        return False, False, False, errors

    existed = {name: path.is_dir() for name, path in targets}
    created: dict[str, bool] = {"images": False, "pdfs": False}
    creation_errors: list[InitializationError] = []
    for name, path in targets:
        if existed[name]:
            continue
        try:
            path.mkdir()
            created[name] = True
        except OSError as exc:
            creation_errors.append(
                InitializationError(
                    _display_path(source, name),
                    f"could not create directory: {exc}",
                )
            )

    return (
        created["images"],
        created["pdfs"],
        existed["images"] and existed["pdfs"],
        tuple(creation_errors),
    )


def initialize_sources(scan_result: ScanResult) -> InitializationResult:
    """Ensure images/ and pdfs/ exist for every discovered conclusion source."""

    if scan_result.errors:
        errors = tuple(
            InitializationError(error.path, f"discovery validation failed: {error.message}")
            for error in scan_result.errors
        )
        modules = tuple(
            ModuleInitializationResult(module.module_name, len(module.sources), 0, 0, 0)
            for module in scan_result.modules
        )
        return InitializationResult(modules, errors)

    module_results: list[ModuleInitializationResult] = []
    errors: list[InitializationError] = []
    for module in scan_result.modules:
        created_images = 0
        created_pdfs = 0
        already_initialized = 0
        for source in module.sources:
            source_images, source_pdfs, source_initialized, source_errors = _initialize_source(
                source
            )
            created_images += int(source_images)
            created_pdfs += int(source_pdfs)
            already_initialized += int(source_initialized)
            errors.extend(source_errors)

        module_results.append(
            ModuleInitializationResult(
                module_name=module.module_name,
                conclusion_count=len(module.sources),
                created_images=created_images,
                created_pdfs=created_pdfs,
                already_initialized=already_initialized,
            )
        )

    return InitializationResult(tuple(module_results), tuple(errors))
