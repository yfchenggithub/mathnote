#!/usr/bin/env python3
"""
Batch-create sequential pipeline input directories such as I009, I010, I011.

Design goals
------------
1. Safe by default:
   - Dry-run by default; add ``--apply`` to actually write.
   - Refuses to write outside the configured base directory.
   - Refuses unsafe file paths such as ``..\\secret.txt``.
2. Config-driven:
   - Root directory, prefix, width, default start/count, and files come from JSON.
   - CLI positional arguments can override the configured start/count.
3. Easy to debug:
   - Clear logging, verbose mode, execution summary.
   - Each file can control its own overwrite policy.
4. Easy to extend:
   - File specs support empty files, inline content, or template files.
   - Supports placeholder rendering without conflicting with LaTeX braces.

Placeholder syntax
------------------
Use ``[[name]]`` inside ``content`` or template files. Supported placeholders:
- ``[[id]]``: full directory id, for example ``I009``
- ``[[dir_name]]``: same as ``[[id]]``
- ``[[number]]``: integer value, for example ``9``
- ``[[number_padded]]``: zero-padded number, for example ``009``
- ``[[batch_index]]``: zero-based index inside the current batch
- ``[[batch_ordinal]]``: one-based index inside the current batch

Examples
--------
1. Preview create I009 ~ I011 using default/example config:
   python scripts/create_pipeline_input_dirs.py 9 3

2. Actually create them:
   python scripts/create_pipeline_input_dirs.py 9 3 --apply

3. Use a custom config:
   python scripts/create_pipeline_input_dirs.py --config scripts/create_pipeline_input_dirs.example.json 9 3 --apply

4. Only inspect the resolved plan:
   python scripts/create_pipeline_input_dirs.py 9 3 --verbose
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_BASE_DIR = SCRIPT_PATH.parents[1]
DEFAULT_CONFIG_PATH = SCRIPT_PATH.with_name("create_pipeline_input_dirs.example.json")
DEFAULT_TARGET_ROOT = Path("12_pipeline/input")
DEFAULT_PREFIX = "I"
DEFAULT_NUMBER_WIDTH = 3
DEFAULT_DIRECTORY_EXISTS_POLICY = "reuse"
DEFAULT_FILE_EXISTS_POLICY = "skip"
VALID_EXISTS_POLICIES = {"skip", "overwrite", "error"}
VALID_DIRECTORY_EXISTS_POLICIES = {"reuse", "skip", "error"}

logger = logging.getLogger("create_pipeline_input_dirs")


@dataclass(slots=True)
class FileSpec:
    """Single file creation rule under every generated directory."""

    path: str
    content: str | None
    template_path: Path | None
    encoding: str
    exists_policy: str


@dataclass(slots=True)
class AppConfig:
    """Resolved runtime configuration after merging defaults, JSON, and CLI."""

    base_dir: Path
    config_dir: Path
    target_root: Path
    prefix: str
    number_width: int
    start: int
    count: int
    dry_run: bool
    directory_exists_policy: str
    default_file_exists_policy: str
    file_specs: list[FileSpec]


@dataclass(slots=True)
class RunStats:
    """Execution counters used for the final summary."""

    target_dirs: int = 0
    created_dirs: int = 0
    reused_dirs: int = 0
    skipped_dirs: int = 0
    created_files: int = 0
    overwritten_files: int = 0
    skipped_files: int = 0
    errors: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create sequential Ixxx-style directories and scaffold files."
    )
    parser.add_argument(
        "start",
        nargs="?",
        type=int,
        help="Starting number. Example: 9 -> I009.",
    )
    parser.add_argument(
        "count",
        nargs="?",
        type=int,
        help="How many directories to create. Example: 3 -> I009~I011.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help=(
            "Path to JSON config file. "
            f"Default: {DEFAULT_CONFIG_PATH.relative_to(DEFAULT_BASE_DIR)}"
        ),
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=None,
        help="Workspace base directory. Default: repository root.",
    )
    parser.add_argument(
        "--target-root",
        type=Path,
        default=None,
        help="Target root directory relative to base-dir. Example: 12_pipeline/input",
    )
    parser.add_argument(
        "--prefix",
        default=None,
        help="Directory prefix. Example: I",
    )
    parser.add_argument(
        "--number-width",
        type=int,
        default=None,
        help="Zero-padding width. Example: 3 -> I009",
    )
    parser.add_argument(
        "--directory-exists-policy",
        choices=sorted(VALID_DIRECTORY_EXISTS_POLICIES),
        default=None,
        help="How to handle an existing target directory: reuse, skip, or error.",
    )
    parser.add_argument(
        "--overwrite-files",
        action="store_true",
        help="Force all files to use overwrite mode, regardless of config.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually create directories/files. Without this flag, the script stays in dry-run mode.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show resolved configuration and per-file planning details.",
    )
    return parser.parse_args()


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(message)s")


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("Config root must be a JSON object.")
    return data


def is_within(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def resolve_path(value: str | Path, *, anchor: Path) -> Path:
    raw = Path(value)
    if raw.is_absolute():
        return raw.resolve()
    return (anchor / raw).resolve()


def validate_non_negative(name: str, value: int) -> int:
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got {value}.")
    return value


def validate_positive(name: str, value: int) -> int:
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value}.")
    return value


def validate_policy(name: str, value: str, allowed: set[str]) -> str:
    if value not in allowed:
        choices = ", ".join(sorted(allowed))
        raise ValueError(f"{name} must be one of: {choices}. Got: {value}")
    return value


def render_placeholders(raw_text: str, variables: dict[str, str]) -> str:
    """
    Replace placeholders like [[id]] without touching LaTeX braces.

    We intentionally do not use str.format() because LaTeX content often contains
    many single braces, which would make templates hard to write and debug.
    """
    rendered = raw_text
    for key, value in variables.items():
        rendered = rendered.replace(f"[[{key}]]", value)
    return rendered


def load_template_text(template_path: Path, encoding: str) -> str:
    with template_path.open("r", encoding=encoding) as file:
        return file.read()


def normalize_file_specs(
    raw_files: Any,
    *,
    config_dir: Path,
    default_exists_policy: str,
    force_overwrite: bool,
) -> list[FileSpec]:
    if raw_files is None:
        raw_files = [{"path": "source.tex", "content": ""}]

    if not isinstance(raw_files, list):
        raise ValueError("config.files must be a list.")

    file_specs: list[FileSpec] = []
    for index, item in enumerate(raw_files):
        if isinstance(item, str):
            path = item.strip()
            if not path:
                raise ValueError(f"config.files[{index}] cannot be an empty string.")
            exists_policy = "overwrite" if force_overwrite else default_exists_policy
            file_specs.append(
                FileSpec(
                    path=path,
                    content="",
                    template_path=None,
                    encoding="utf-8",
                    exists_policy=exists_policy,
                )
            )
            continue

        if not isinstance(item, dict):
            raise ValueError(
                f"config.files[{index}] must be a string or an object, got {type(item).__name__}."
            )

        if "path" not in item:
            raise ValueError(f"config.files[{index}] must contain 'path'.")

        path = str(item["path"]).strip()
        if not path:
            raise ValueError(f"config.files[{index}].path cannot be empty.")

        content = item.get("content")
        template_path_raw = item.get("template_path")
        if content is not None and template_path_raw is not None:
            raise ValueError(
                f"config.files[{index}] cannot contain both 'content' and 'template_path'."
            )

        encoding = str(item.get("encoding", "utf-8"))
        exists_policy = str(item.get("exists_policy", default_exists_policy))
        if force_overwrite:
            exists_policy = "overwrite"
        validate_policy(
            name=f"config.files[{index}].exists_policy",
            value=exists_policy,
            allowed=VALID_EXISTS_POLICIES,
        )

        template_path: Path | None = None
        if template_path_raw is not None:
            template_path = resolve_path(str(template_path_raw), anchor=config_dir)
            if not template_path.exists():
                raise FileNotFoundError(f"Template file not found: {template_path}")
            if not template_path.is_file():
                raise ValueError(f"Template path is not a file: {template_path}")

        if content is not None and not isinstance(content, str):
            raise ValueError(f"config.files[{index}].content must be a string.")

        file_specs.append(
            FileSpec(
                path=path,
                content=content,
                template_path=template_path,
                encoding=encoding,
                exists_policy=exists_policy,
            )
        )

    return file_specs


def resolve_runtime_config(args: argparse.Namespace) -> AppConfig:
    config_path = (args.config or DEFAULT_CONFIG_PATH).resolve()
    config_data: dict[str, Any] = {}
    config_dir = DEFAULT_BASE_DIR

    if config_path.exists():
        config_data = load_json_object(config_path)
        config_dir = config_path.parent.resolve()
    elif args.config is not None:
        raise FileNotFoundError(f"Config file not found: {config_path}")

    base_dir_raw = args.base_dir
    if base_dir_raw is None:
        base_dir_raw = config_data.get("base_dir", DEFAULT_BASE_DIR)
    base_dir = resolve_path(base_dir_raw, anchor=config_dir).resolve()
    if not base_dir.exists():
        raise FileNotFoundError(f"Base directory not found: {base_dir}")
    if not base_dir.is_dir():
        raise NotADirectoryError(f"Base directory is not a directory: {base_dir}")

    target_root_raw = args.target_root
    if target_root_raw is None:
        target_root_raw = config_data.get("target_root", DEFAULT_TARGET_ROOT)
    target_root = resolve_path(target_root_raw, anchor=base_dir)
    if not is_within(base_dir, target_root):
        raise ValueError(
            f"Unsafe target_root outside base_dir.\nbase_dir={base_dir}\ntarget_root={target_root}"
        )

    prefix = str(args.prefix if args.prefix is not None else config_data.get("prefix", DEFAULT_PREFIX)).strip()
    if not prefix:
        raise ValueError("prefix cannot be empty.")

    number_width = int(
        args.number_width
        if args.number_width is not None
        else config_data.get("number_width", DEFAULT_NUMBER_WIDTH)
    )
    validate_positive("number_width", number_width)

    start_raw = args.start if args.start is not None else config_data.get("start")
    count_raw = args.count if args.count is not None else config_data.get("count")
    if start_raw is None:
        raise ValueError("Missing start. Provide CLI positional argument or config.start.")
    if count_raw is None:
        raise ValueError("Missing count. Provide CLI positional argument or config.count.")

    start = validate_non_negative("start", int(start_raw))
    count = validate_positive("count", int(count_raw))

    # Safety-first rule:
    # - Without --apply, always stay in dry-run mode.
    # - Config can document intent, but it cannot silently disable dry-run.
    dry_run = not args.apply

    directory_exists_policy = str(
        args.directory_exists_policy
        if args.directory_exists_policy is not None
        else config_data.get(
            "directory_exists_policy", DEFAULT_DIRECTORY_EXISTS_POLICY
        )
    )
    validate_policy(
        name="directory_exists_policy",
        value=directory_exists_policy,
        allowed=VALID_DIRECTORY_EXISTS_POLICIES,
    )

    default_file_exists_policy = str(
        config_data.get("default_file_exists_policy", DEFAULT_FILE_EXISTS_POLICY)
    )
    if args.overwrite_files:
        default_file_exists_policy = "overwrite"
    validate_policy(
        name="default_file_exists_policy",
        value=default_file_exists_policy,
        allowed=VALID_EXISTS_POLICIES,
    )

    file_specs = normalize_file_specs(
        raw_files=config_data.get("files"),
        config_dir=config_dir,
        default_exists_policy=default_file_exists_policy,
        force_overwrite=args.overwrite_files,
    )

    return AppConfig(
        base_dir=base_dir,
        config_dir=config_dir,
        target_root=target_root,
        prefix=prefix,
        number_width=number_width,
        start=start,
        count=count,
        dry_run=dry_run,
        directory_exists_policy=directory_exists_policy,
        default_file_exists_policy=default_file_exists_policy,
        file_specs=file_specs,
    )


def build_dir_name(prefix: str, number: int, width: int) -> str:
    return f"{prefix}{number:0{width}d}"


def build_template_variables(
    *,
    dir_name: str,
    number: int,
    width: int,
    batch_index: int,
) -> dict[str, str]:
    return {
        "id": dir_name,
        "dir_name": dir_name,
        "number": str(number),
        "number_padded": f"{number:0{width}d}",
        "batch_index": str(batch_index),
        "batch_ordinal": str(batch_index + 1),
    }


def resolve_relative_file_path(target_dir: Path, relative_path: str) -> Path:
    file_path = (target_dir / relative_path).resolve()
    if not is_within(target_dir, file_path):
        raise ValueError(
            f"Unsafe file path outside target directory: {relative_path} -> {file_path}"
        )
    return file_path


def create_or_plan_file(
    *,
    target_dir: Path,
    file_spec: FileSpec,
    variables: dict[str, str],
    dry_run: bool,
    stats: RunStats,
) -> None:
    rendered_relative_path = render_placeholders(file_spec.path, variables)
    destination = resolve_relative_file_path(target_dir, rendered_relative_path)

    if file_spec.content is not None:
        body = render_placeholders(file_spec.content, variables)
    elif file_spec.template_path is not None:
        template_text = load_template_text(file_spec.template_path, file_spec.encoding)
        body = render_placeholders(template_text, variables)
    else:
        body = ""

    exists = destination.exists()
    action = "create"
    if exists:
        if destination.is_dir():
            raise IsADirectoryError(f"Target path is a directory: {destination}")
        if file_spec.exists_policy == "skip":
            stats.skipped_files += 1
            logger.info("[SKIP] file exists: %s", destination)
            return
        if file_spec.exists_policy == "error":
            raise FileExistsError(f"File already exists: {destination}")
        action = "overwrite"

    if dry_run:
        logger.info("[DRY-RUN] %s file: %s", action, destination)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "          encoding=%s, exists_policy=%s, content_length=%s",
                file_spec.encoding,
                file_spec.exists_policy,
                len(body),
            )
        if action == "overwrite":
            stats.overwritten_files += 1
        else:
            stats.created_files += 1
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(body, encoding=file_spec.encoding)
    if action == "overwrite":
        stats.overwritten_files += 1
        logger.info("[OVERWRITE] %s", destination)
    else:
        stats.created_files += 1
        logger.info("[CREATE] %s", destination)


def create_or_plan_directory(
    *,
    app_config: AppConfig,
    dir_name: str,
    number: int,
    batch_index: int,
    stats: RunStats,
) -> None:
    target_dir = (app_config.target_root / dir_name).resolve()
    if not is_within(app_config.base_dir, target_dir):
        raise ValueError(f"Unsafe target directory outside base_dir: {target_dir}")

    stats.target_dirs += 1
    directory_exists = target_dir.exists()

    if directory_exists:
        if not target_dir.is_dir():
            raise NotADirectoryError(f"Target exists but is not a directory: {target_dir}")
        if app_config.directory_exists_policy == "skip":
            stats.skipped_dirs += 1
            logger.info("[SKIP] directory exists: %s", target_dir)
            return
        if app_config.directory_exists_policy == "error":
            raise FileExistsError(f"Directory already exists: {target_dir}")
        stats.reused_dirs += 1
        logger.info("[REUSE] %s", target_dir)
    else:
        if app_config.dry_run:
            logger.info("[DRY-RUN] create directory: %s", target_dir)
        else:
            target_dir.mkdir(parents=True, exist_ok=True)
            logger.info("[CREATE] %s", target_dir)
        stats.created_dirs += 1

    variables = build_template_variables(
        dir_name=dir_name,
        number=number,
        width=app_config.number_width,
        batch_index=batch_index,
    )

    for file_spec in app_config.file_specs:
        try:
            create_or_plan_file(
                target_dir=target_dir,
                file_spec=file_spec,
                variables=variables,
                dry_run=app_config.dry_run,
                stats=stats,
            )
        except Exception as exc:
            stats.errors += 1
            logger.error("[ERROR] file failed in %s: %s", target_dir, exc)


def log_resolved_config(app_config: AppConfig) -> None:
    mode = "DRY-RUN" if app_config.dry_run else "APPLY"
    logger.info("[MODE] %s", mode)
    logger.info("[BASE_DIR] %s", app_config.base_dir)
    logger.info("[CONFIG_DIR] %s", app_config.config_dir)
    logger.info("[TARGET_ROOT] %s", app_config.target_root)
    logger.info("[RANGE] start=%s count=%s", app_config.start, app_config.count)
    logger.info(
        "[NAMING] prefix=%s width=%s directory_exists_policy=%s",
        app_config.prefix,
        app_config.number_width,
        app_config.directory_exists_policy,
    )
    logger.info(
        "[FILES] count=%s default_file_exists_policy=%s",
        len(app_config.file_specs),
        app_config.default_file_exists_policy,
    )
    if logger.isEnabledFor(logging.DEBUG):
        for item in app_config.file_specs:
            logger.debug(
                "  - path=%s exists_policy=%s template=%s",
                item.path,
                item.exists_policy,
                item.template_path,
            )


def main() -> int:
    args = parse_args()
    configure_logging(args.verbose)

    try:
        app_config = resolve_runtime_config(args)
        log_resolved_config(app_config)

        if not app_config.target_root.exists():
            if app_config.dry_run:
                logger.info("[DRY-RUN] create target root: %s", app_config.target_root)
            else:
                app_config.target_root.mkdir(parents=True, exist_ok=True)
                logger.info("[CREATE] target root: %s", app_config.target_root)

        stats = RunStats()
        logger.info("")
        for batch_index in range(app_config.count):
            number = app_config.start + batch_index
            dir_name = build_dir_name(
                prefix=app_config.prefix,
                number=number,
                width=app_config.number_width,
            )
            try:
                create_or_plan_directory(
                    app_config=app_config,
                    dir_name=dir_name,
                    number=number,
                    batch_index=batch_index,
                    stats=stats,
                )
            except Exception as exc:
                stats.errors += 1
                logger.error("[ERROR] directory failed for %s: %s", dir_name, exc)

        logger.info("")
        logger.info("[SUMMARY]")
        logger.info("target_dirs=%s", stats.target_dirs)
        logger.info("created_dirs=%s", stats.created_dirs)
        logger.info("reused_dirs=%s", stats.reused_dirs)
        logger.info("skipped_dirs=%s", stats.skipped_dirs)
        logger.info("created_files=%s", stats.created_files)
        logger.info("overwritten_files=%s", stats.overwritten_files)
        logger.info("skipped_files=%s", stats.skipped_files)
        logger.info("errors=%s", stats.errors)
        if app_config.dry_run:
            logger.info("No filesystem changes were made. Add --apply to write files.")
        return 0
    except Exception as exc:  # pragma: no cover - CLI script friendly error path
        logger.error("[ERROR] %s", exc)
        if args.verbose:
            raise
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
