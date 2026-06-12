#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Incrementally publish one or more conclusion IDs.

This script is intentionally an orchestrator:
- existing build scripts still own search/detail/canonical/PDF generation;
- this script owns temporary workspace layout, post-processing order,
  incremental JSON merging, local backend data sync, and optional remote actions.

Typical dry run:
    python scripts/incremental_publish.py R005 --dry-run

Typical local publish:
    python scripts/incremental_publish.py R005

Typical publish with formula upload, remote git pull, and service restart:
    python scripts/incremental_publish.py R005 --deploy

Important data-flow notes:
1. `build/conclusion_pdf_map.json` is never used as the full baseline.
   The full baseline is always:
       D:\\mathnode_backend\\app\\data\\conclusion_pdf_map.json
2. Formula/TikZ images are rendered from the single-ID canonical delta, then only
   the current ID image directories are uploaded to the remote static directories.
   Formula image directories are copied to public/static/formulas/<ID> before
   the temporary workspace is deleted so local assets remain available.
3. Remote JSON/PDF updates are expected to arrive through backend git pull.
4. After files are synced into the local backend data directory, those exact
   files are committed and pushed from the backend repo unless disabled.
"""

from __future__ import annotations

import argparse
import codecs
import copy
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

DEFAULT_BACKEND_REPO = Path(r"D:\mathnode_backend")
DEFAULT_BACKEND_DATA_DIR = DEFAULT_BACKEND_REPO / "app" / "data"
DEFAULT_REMOTE_HOST = "146.56.223.203"
DEFAULT_REMOTE_USER = "yfcheng"
REMOTE_PASSWORD_ENV = "MATHNOTE_REMOTE_PASSWORD"
REMOTE_ASKPASS_PASSWORD_ENV = "MATHNOTE_REMOTE_ASKPASS_PASSWORD"
DEFAULT_REMOTE_FORMULA_DIR = "/var/www/ok-shuxue/static/formulas"
DEFAULT_REMOTE_TIKZ_DIR = "/var/www/ok-shuxue/static/tikz"
DEFAULT_REMOTE_FORMULA_OWNER = "www-data"
DEFAULT_REMOTE_FORMULA_GROUP = "www-data"
DEFAULT_REMOTE_BACKEND_ROOT = "/root/math_search_backend"
DEFAULT_RESTART_COMMAND = (
    "systemctl restart math-search.service && "
    "systemctl status math-search.service --no-pager"
)

DEFAULT_CANONICAL_PATH = PROJECT_ROOT / "data" / "content" / "canonical_content_v2.json"
DEFAULT_BACKEND_INDEX_PATH = (
    PROJECT_ROOT / "data" / "search_engine" / "backend_search_index.json"
)
DEFAULT_PDF_MAP_PATH = PROJECT_ROOT / "build" / "conclusion_pdf_map.json"
DEFAULT_PDF_OUTPUT_DIR = PROJECT_ROOT / "build" / "conclusion_pdfs"
DEFAULT_LOCAL_FORMULA_DIR = PROJECT_ROOT / "public" / "static" / "formulas"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports" / "incremental_publish_report.json"
RENDER_MATH_ASSETS_REPORT = PROJECT_ROOT / "reports" / "render_math_assets_report.json"
RENDER_TIKZ_ASSETS_REPORT = PROJECT_ROOT / "reports" / "render_tikz_assets_report.json"
MODULE_PREFIX_MAP = PROJECT_ROOT / "12_pipeline" / "config" / "module_prefix_map.json"

ID_PATTERN = re.compile(r"^[A-Za-z]\d{3}$")
MODULE_DIR_PATTERN = re.compile(r"^\d{2}[_-].+")

SEARCH_EXTRA_FLAGS = (
    "--enable-knowledge-node-terms",
    "--enable-query-template-terms",
    "--enable-formula-token-terms",
    "--enable-formula-terms",
    "--enable-usage-terms",
)

LOGGER = logging.getLogger("incremental_publish")


class PublishError(RuntimeError):
    """Readable error for an expected publish failure."""


@dataclass
class StageResult:
    name: str
    command: list[str]
    cwd: str
    return_code: int
    duration_sec: float
    status: str
    stdout_tail: str = ""
    stderr_tail: str = ""


@dataclass
class JsonStyle:
    has_bom: bool = False
    newline: str = "\n"


@dataclass
class PublishConfig:
    ids: tuple[str, ...]
    dry_run: bool
    strict: bool
    keep_temp: bool
    log_level: str
    canonical_path: Path
    backend_index_path: Path
    pdf_map_path: Path
    pdf_output_dir: Path
    backend_repo: Path
    backend_data_dir: Path
    sync_backend_data: bool
    pull_backend_repo: bool
    backend_git_publish: bool
    backend_git_push: bool
    backend_commit_message: str
    project_git_publish: bool
    project_git_push: bool
    project_commit_message: str
    formula_min_length: int
    asset_base: str
    remote_host: str
    remote_user: str
    remote_password: str
    remote_formula_dir: str
    remote_tikz_dir: str
    remote_formula_owner: str
    remote_formula_group: str
    remote_backend_root: str
    deploy: bool
    upload_formulas: bool
    remote_pull: bool
    restart: bool
    restart_command: str
    allow_primary_fallback: bool
    report_path: Path


@dataclass
class PublishPaths:
    tmp_root: Path
    search_bundle: Path
    search_audit: Path
    backend_delta: Path
    backend_delta_final: Path
    backend_verify_report: Path
    detail_dir: Path
    canonical_module_dir: Path
    canonical_report_dir: Path
    canonical_raw: Path
    canonical_marked: Path
    canonical_tikz_rendered: Path
    canonical_rendered: Path
    canonical_final: Path
    formula_dir: Path
    formula_out_dir: Path
    formula_render_report: Path
    tikz_out_dir: Path
    tikz_render_report: Path
    punctuation_report: Path
    core_formula_sync_report: Path
    merged_canonical: Path
    merged_backend_index: Path
    pdf_dir: Path
    pdf_map_delta: Path
    merged_pdf_map: Path
    tmp_report: Path


@dataclass
class PublishReport:
    generated_at: str
    ids: list[str]
    dry_run: bool
    tmp_root: str
    stages: list[dict[str, Any]] = field(default_factory=list)
    outputs: dict[str, Any] = field(default_factory=dict)
    counts: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


def configure_logging(level_name: str) -> None:
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")


def split_csv_tokens(values: Sequence[str]) -> list[str]:
    tokens: list[str] = []
    for raw in values:
        for token in str(raw).split(","):
            piece = token.strip()
            if piece:
                tokens.append(piece)
    return tokens


def normalize_ids(raw_values: Sequence[str]) -> tuple[str, ...]:
    normalized: list[str] = []
    invalid: list[str] = []
    for value in split_csv_tokens(raw_values):
        item_id = value.upper()
        if not ID_PATTERN.fullmatch(item_id):
            invalid.append(value)
            continue
        if item_id not in normalized:
            normalized.append(item_id)

    if invalid:
        raise PublishError(
            "Invalid conclusion ID(s): "
            + ", ".join(invalid)
            + ". Expected values like R005."
        )
    if not normalized:
        raise PublishError("At least one conclusion ID is required.")
    return tuple(normalized)


def read_windows_persisted_env(name: str) -> str:
    if os.name != "nt":
        return ""
    try:
        import winreg
    except ImportError:
        return ""

    registry_locations = (
        (winreg.HKEY_CURRENT_USER, r"Environment"),
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
        ),
    )
    for root, subkey in registry_locations:
        try:
            with winreg.OpenKey(root, subkey) as key:
                value, value_type = winreg.QueryValueEx(key, name)
        except OSError:
            continue
        text = str(value)
        if value_type == winreg.REG_EXPAND_SZ:
            text = winreg.ExpandEnvironmentStrings(text)
        if text:
            return text
    return ""


def read_remote_password_from_environment() -> str:
    return os.environ.get(REMOTE_PASSWORD_ENV, "") or read_windows_persisted_env(
        REMOTE_PASSWORD_ENV
    )


def remote_actions_requested(args: argparse.Namespace) -> bool:
    return bool(
        not args.dry_run
        and (args.deploy or args.upload_formulas or args.remote_pull or args.restart)
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Incrementally publish selected conclusion IDs.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/incremental_publish.py R005 --dry-run\n"
            "  python scripts/incremental_publish.py R005\n"
            "  python scripts/incremental_publish.py R005 --deploy\n"
        ),
    )
    parser.add_argument("ids", nargs="+", help="Conclusion IDs, e.g. R005 or R005,R006.")
    parser.add_argument("--dry-run", action="store_true", help="Build temp artifacts and reports only.")
    parser.add_argument("--strict", action="store_true", help="Pass strict flags and fail on formula sync misses.")
    parser.add_argument("--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING", "ERROR"))
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temp workspace after the run. Default: delete it.",
    )
    parser.add_argument("--cleanup-temp", action="store_true", help=argparse.SUPPRESS)

    parser.add_argument("--canonical-path", default=str(DEFAULT_CANONICAL_PATH))
    parser.add_argument("--backend-index-path", default=str(DEFAULT_BACKEND_INDEX_PATH))
    parser.add_argument("--pdf-map-path", default=str(DEFAULT_PDF_MAP_PATH))
    parser.add_argument("--pdf-output-dir", default=str(DEFAULT_PDF_OUTPUT_DIR))

    parser.add_argument("--backend-repo", default=str(DEFAULT_BACKEND_REPO))
    parser.add_argument("--backend-data-dir", default=str(DEFAULT_BACKEND_DATA_DIR))
    parser.add_argument(
        "--skip-backend-sync",
        action="store_true",
        help="Do not copy merged JSON/PDF files into the local backend data directory.",
    )
    parser.add_argument(
        "--pull-backend-repo",
        action="store_true",
        help="Run git pull --ff-only in the local backend repo before syncing data.",
    )
    parser.add_argument(
        "--skip-backend-git-publish",
        action="store_true",
        help="Do not commit/push the local backend repo after syncing data files.",
    )
    parser.add_argument(
        "--skip-backend-push",
        action="store_true",
        help="Commit the local backend repo but do not push.",
    )
    parser.add_argument(
        "--backend-commit-message",
        default="",
        help="Commit message for backend data publish. Default: Incremental publish <ids>.",
    )
    parser.add_argument(
        "--skip-project-git-publish",
        action="store_true",
        help="Do not commit local project JSON artifacts after a successful publish.",
    )
    parser.add_argument(
        "--project-git-push",
        action="store_true",
        help="Push the local project repo after committing publish artifacts.",
    )
    parser.add_argument(
        "--project-commit-message",
        default="",
        help="Commit message for local project artifacts. Default: Incremental publish <ids> project artifacts.",
    )

    parser.add_argument("--formula-min-length", type=int, default=5)
    parser.add_argument("--asset-base", default="/static/formulas")
    parser.add_argument(
        "--allow-primary-fallback",
        action="store_true",
        help="Pass --allow-primary-fallback to sync_backend_core_formula_assets.py.",
    )

    parser.add_argument("--remote-host", default=DEFAULT_REMOTE_HOST)
    parser.add_argument("--remote-user", default=DEFAULT_REMOTE_USER)
    parser.add_argument(
        "--remote-password",
        default=None,
        help=(
            f"Deprecated; ignored. Remote SSH/sudo password is read from "
            f"${REMOTE_PASSWORD_ENV} only."
        ),
    )
    parser.add_argument("--remote-formula-dir", default=DEFAULT_REMOTE_FORMULA_DIR)
    parser.add_argument("--remote-tikz-dir", default=DEFAULT_REMOTE_TIKZ_DIR)
    parser.add_argument("--remote-formula-owner", default=DEFAULT_REMOTE_FORMULA_OWNER)
    parser.add_argument("--remote-formula-group", default=DEFAULT_REMOTE_FORMULA_GROUP)
    parser.add_argument("--remote-backend-root", default=DEFAULT_REMOTE_BACKEND_ROOT)
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Upload formula/TikZ image directories, run remote git pull, and restart the service.",
    )
    parser.add_argument(
        "--upload-formulas",
        action="store_true",
        help="Only upload formula/TikZ image directories to the remote static directories.",
    )
    parser.add_argument(
        "--remote-pull",
        action="store_true",
        help="Run git pull --ff-only in the remote backend repo.",
    )
    parser.add_argument("--restart", action="store_true", help="Run remote restart command.")
    parser.add_argument("--restart-command", default=DEFAULT_RESTART_COMMAND)
    parser.add_argument("--report", default=str(DEFAULT_REPORT_PATH))
    return parser.parse_args()


def build_config(args: argparse.Namespace) -> PublishConfig:
    ids = normalize_ids(args.ids)
    if args.formula_min_length < 0:
        raise PublishError("--formula-min-length must be >= 0.")
    remote_formula_dir = str(args.remote_formula_dir).strip().rstrip("/")
    remote_tikz_dir = str(args.remote_tikz_dir).strip().rstrip("/")
    if not remote_formula_dir:
        raise PublishError("--remote-formula-dir must not be empty.")
    if not remote_tikz_dir:
        raise PublishError("--remote-tikz-dir must not be empty.")
    if not str(args.remote_formula_owner).strip():
        raise PublishError("--remote-formula-owner must not be empty.")
    if not str(args.remote_formula_group).strip():
        raise PublishError("--remote-formula-group must not be empty.")

    deploy = bool(args.deploy)
    remote_password = read_remote_password_from_environment()
    if "\r" in remote_password or "\n" in remote_password:
        raise PublishError(f"${REMOTE_PASSWORD_ENV} must be a single-line value.")
    if remote_actions_requested(args) and not remote_password:
        raise PublishError(
            f"Remote publish requires ${REMOTE_PASSWORD_ENV}. Interactive password "
            "entry is disabled; set the current process environment variable or the "
            "Windows User/System environment variable before running."
        )
    return PublishConfig(
        ids=ids,
        dry_run=bool(args.dry_run),
        strict=bool(args.strict),
        keep_temp=bool(args.keep_temp),
        log_level=str(args.log_level),
        canonical_path=Path(args.canonical_path).resolve(),
        backend_index_path=Path(args.backend_index_path).resolve(),
        pdf_map_path=Path(args.pdf_map_path).resolve(),
        pdf_output_dir=Path(args.pdf_output_dir).resolve(),
        backend_repo=Path(args.backend_repo).resolve(),
        backend_data_dir=Path(args.backend_data_dir).resolve(),
        sync_backend_data=not bool(args.skip_backend_sync),
        pull_backend_repo=bool(args.pull_backend_repo),
        backend_git_publish=not bool(args.skip_backend_git_publish),
        backend_git_push=not bool(args.skip_backend_push),
        backend_commit_message=(
            str(args.backend_commit_message).strip()
            or f"Incremental publish {', '.join(ids)}"
        ),
        project_git_publish=not bool(args.skip_project_git_publish),
        project_git_push=bool(args.project_git_push),
        project_commit_message=(
            str(args.project_commit_message).strip()
            or f"Incremental publish {', '.join(ids)} project artifacts"
        ),
        formula_min_length=int(args.formula_min_length),
        asset_base=str(args.asset_base),
        remote_host=str(args.remote_host),
        remote_user=str(args.remote_user),
        remote_password=remote_password,
        remote_formula_dir=remote_formula_dir,
        remote_tikz_dir=remote_tikz_dir,
        remote_formula_owner=str(args.remote_formula_owner).strip(),
        remote_formula_group=str(args.remote_formula_group).strip(),
        remote_backend_root=str(args.remote_backend_root),
        deploy=deploy,
        upload_formulas=deploy or bool(args.upload_formulas),
        remote_pull=deploy or bool(args.remote_pull) or bool(args.restart),
        restart=deploy or bool(args.restart),
        restart_command=str(args.restart_command),
        allow_primary_fallback=bool(args.allow_primary_fallback),
        report_path=Path(args.report).resolve(),
    )


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def create_paths(config: PublishConfig) -> PublishPaths:
    tmp_root = PROJECT_ROOT / ".tmp" / f"incremental_publish_{now_stamp()}_{os.getpid()}"
    return PublishPaths(
        tmp_root=tmp_root,
        search_bundle=tmp_root / "search_bundle.delta.js",
        search_audit=tmp_root / "search_audit.delta.json",
        backend_delta=tmp_root / "backend_search_index.delta.json",
        backend_delta_final=tmp_root / "backend_search_index.delta.final.json",
        backend_verify_report=tmp_root / "backend_index_verify.delta.json",
        detail_dir=tmp_root / "detail_data",
        canonical_module_dir=tmp_root / "canonical_modules",
        canonical_report_dir=tmp_root / "conversion_reports",
        canonical_raw=tmp_root / "canonical_content_v2.delta.json",
        canonical_marked=tmp_root / "canonical_content_v2.delta.marked.json",
        canonical_tikz_rendered=tmp_root / "canonical_content_v2.delta.tikz_rendered.json",
        canonical_rendered=tmp_root / "canonical_content_v2.delta.rendered.json",
        canonical_final=tmp_root / "canonical_content_v2.delta.final.json",
        formula_dir=tmp_root / "formulas",
        formula_out_dir=tmp_root / "formulas",
        formula_render_report=tmp_root / "render_math_assets_report.json",
        tikz_out_dir=tmp_root / "tikz",
        tikz_render_report=tmp_root / "render_tikz_assets_report.json",
        punctuation_report=tmp_root / "remove_math_image_following_period_report.json",
        core_formula_sync_report=tmp_root / "sync_backend_core_formula_assets_report.json",
        merged_canonical=tmp_root / "canonical_content_v2.merged.json",
        merged_backend_index=tmp_root / "backend_search_index.merged.json",
        pdf_dir=(tmp_root / "pdfs" if config.dry_run else config.pdf_output_dir),
        pdf_map_delta=tmp_root / "conclusion_pdf_map.delta.json",
        merged_pdf_map=tmp_root / "conclusion_pdf_map.merged.json",
        tmp_report=tmp_root / "incremental_publish_report.json",
    )


def derive_tikz_asset_base(asset_base: str) -> str:
    normalized = str(asset_base).strip().rstrip("/")
    if normalized.endswith("/formulas"):
        return normalized[: -len("/formulas")] + "/tikz"
    return normalized + "/tikz"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def tail_text(text: str, max_lines: int = 80) -> str:
    if not text:
        return ""
    lines = text.splitlines()
    return "\n".join(lines[-max_lines:])


def run_command(
    name: str,
    command: list[str],
    *,
    cwd: Path = PROJECT_ROOT,
    stages: list[StageResult],
    interactive: bool = False,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[Any]:
    LOGGER.info("Stage start | %s", name)
    LOGGER.debug("Command | %s", " ".join(command))
    started = time.perf_counter()

    command_env = None
    if env:
        command_env = os.environ.copy()
        command_env.update(env)

    try:
        if interactive:
            if input_text is not None:
                proc = subprocess.run(
                    command,
                    cwd=str(cwd),
                    input=input_text,
                    text=True,
                    env=command_env,
                    check=False,
                )
            else:
                proc = subprocess.run(
                    command,
                    cwd=str(cwd),
                    stdin=subprocess.DEVNULL,
                    env=command_env,
                    check=False,
                )
            stdout_tail = ""
            stderr_tail = ""
        else:
            proc = subprocess.run(
                command,
                cwd=str(cwd),
                input=input_text,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=command_env,
                check=False,
            )
            stdout_tail = tail_text(proc.stdout)
            stderr_tail = tail_text(proc.stderr)
    except FileNotFoundError as exc:
        if command and command[0] == "sshpass":
            raise PublishError(
                "Command not found: sshpass. Remote password automation requires "
                "sshpass or the SSH_ASKPASS fallback; interactive password entry is disabled."
            ) from exc
        raise PublishError(f"Command not found: {command[0]}") from exc

    duration = time.perf_counter() - started
    status = "ok" if proc.returncode == 0 else "failed"
    stages.append(
        StageResult(
            name=name,
            command=command,
            cwd=str(cwd),
            return_code=proc.returncode,
            duration_sec=duration,
            status=status,
            stdout_tail=stdout_tail,
            stderr_tail=stderr_tail,
        )
    )

    if proc.returncode == 0:
        LOGGER.info("Stage done | %s | %.2fs", name, duration)
        if stdout_tail and LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.debug("stdout tail | %s\n%s", name, stdout_tail)
        return proc

    if stderr_tail:
        LOGGER.error("stderr tail | %s\n%s", name, stderr_tail)
    raise PublishError(f"Stage failed: {name} (exit={proc.returncode})")


def read_json_with_style(path: Path) -> tuple[Any, JsonStyle]:
    raw = path.read_bytes()
    has_bom = raw.startswith(codecs.BOM_UTF8)
    newline = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8-sig")
    return json.loads(text), JsonStyle(has_bom=has_bom, newline=newline)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def dumps_json(data: Any, style: JsonStyle | None = None) -> bytes:
    style = style or JsonStyle()
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if style.newline != "\n":
        text = text.replace("\n", style.newline)
    if not text.endswith(style.newline):
        text += style.newline
    payload = text.encode("utf-8")
    if style.has_bom:
        payload = codecs.BOM_UTF8 + payload
    return payload


def write_json_atomic(path: Path, data: Any, style: JsonStyle | None = None) -> None:
    ensure_parent(path)
    # The caller backs up official files before writing. Direct writes are used
    # here because this Windows workspace can allow file writes while denying
    # replace/rename/unlink operations for temporary files.
    path.write_bytes(dumps_json(data, style))


def write_json_plain(path: Path, data: Any) -> None:
    write_json_atomic(path, data, JsonStyle())


def backup_file(path: Path) -> Path | None:
    if not path.exists():
        return None
    backup = path.with_name(f"{path.name}.bak_{now_stamp()}")
    shutil.copy2(path, backup)
    LOGGER.info("Backup written | %s -> %s", path, backup)
    return backup


def load_module_prefix_map() -> dict[str, str]:
    raw = read_json(MODULE_PREFIX_MAP)
    if not isinstance(raw, dict):
        raise PublishError(f"Invalid module prefix map: {MODULE_PREFIX_MAP}")
    result: dict[str, str] = {}
    for module, prefix in raw.items():
        module_name = str(module).strip()
        prefix_text = str(prefix).strip().upper()
        if module_name and prefix_text:
            result[prefix_text[0]] = module_name
    return result


def infer_modules(ids: Iterable[str]) -> list[str]:
    prefix_to_module = load_module_prefix_map()
    modules: list[str] = []
    missing: list[str] = []
    for item_id in ids:
        prefix = item_id[0].upper()
        module = prefix_to_module.get(prefix)
        if not module:
            missing.append(prefix)
            continue
        if module not in modules:
            modules.append(module)
    if missing:
        raise PublishError(
            "Missing module prefix mapping for: " + ", ".join(sorted(set(missing)))
        )
    return modules


def find_conclusion_dir(item_id: str) -> Path:
    candidates: list[Path] = []
    prefix = item_id.upper()
    for module_dir in sorted(PROJECT_ROOT.iterdir()):
        if not module_dir.is_dir() or not MODULE_DIR_PATTERN.match(module_dir.name):
            continue
        for child in module_dir.iterdir():
            if not child.is_dir():
                continue
            upper_name = child.name.upper()
            if upper_name == prefix or upper_name.startswith(f"{prefix}_"):
                if (child / "main.tex").is_file():
                    candidates.append(child)

    if not candidates:
        raise PublishError(f"{item_id}: no conclusion directory with main.tex found.")
    if len(candidates) > 1:
        refs = ", ".join(str(path.relative_to(PROJECT_ROOT)) for path in candidates)
        raise PublishError(f"{item_id}: multiple conclusion directories found: {refs}")
    return candidates[0]


def expected_pdf_name(item_id: str) -> str:
    return f"{find_conclusion_dir(item_id).name}.pdf"


def validate_input_files(config: PublishConfig) -> None:
    required = [
        config.canonical_path,
        config.backend_index_path,
        config.backend_data_dir / "conclusion_pdf_map.json",
        SCRIPT_DIR / "build_search_bundle_js.py",
        SCRIPT_DIR / "extract_backend_index_from_search_bundle.py",
        SCRIPT_DIR / "verify_backend_index_extraction.py",
        SCRIPT_DIR / "build_detail_page_js.py",
        SCRIPT_DIR / "migrate_detail_js_to_content_v2.py",
        SCRIPT_DIR / "mark_need_image_by_latex_length.py",
        SCRIPT_DIR / "render_tikz_assets.mjs",
        SCRIPT_DIR / "render_math_assets.mjs",
        SCRIPT_DIR / "remove_math_image_following_period.py",
        SCRIPT_DIR / "sync_backend_core_formula_assets.py",
        SCRIPT_DIR / "build_conclusion_pdfs.py",
    ]
    missing = [path for path in required if not path.exists()]
    if missing:
        raise PublishError(
            "Required file(s) missing:\n"
            + "\n".join(f"  - {path}" for path in missing)
        )


def build_search_delta(
    config: PublishConfig,
    paths: PublishPaths,
    modules: Sequence[str],
    stages: list[StageResult],
) -> None:
    command = [
        sys.executable,
        str(SCRIPT_DIR / "build_search_bundle_js.py"),
        "--output-file",
        str(paths.search_bundle),
        "--audit-report",
        str(paths.search_audit),
    ]
    for module in modules:
        command.extend(["--module", module])
    for item_id in config.ids:
        command.extend(["--item", item_id])
    command.extend(SEARCH_EXTRA_FLAGS)
    if config.strict:
        command.append("--strict")
    run_command("build_search_bundle_js delta", command, stages=stages)

    run_command(
        "extract_backend_index_from_search_bundle delta",
        [
            sys.executable,
            str(SCRIPT_DIR / "extract_backend_index_from_search_bundle.py"),
            "--input",
            str(paths.search_bundle),
            "--output",
            str(paths.backend_delta),
            "--pretty",
        ],
        stages=stages,
    )
    run_command(
        "verify_backend_index_extraction delta",
        [
            sys.executable,
            str(SCRIPT_DIR / "verify_backend_index_extraction.py"),
            "--bundle-js",
            str(paths.search_bundle),
            "--backend-json",
            str(paths.backend_delta),
            "--report",
            str(paths.backend_verify_report),
        ],
        stages=stages,
    )


def build_canonical_delta(
    config: PublishConfig,
    paths: PublishPaths,
    modules: Sequence[str],
    stages: list[StageResult],
) -> None:
    command = [
        sys.executable,
        str(SCRIPT_DIR / "build_detail_page_js.py"),
        "--output-dir",
        str(paths.detail_dir),
    ]
    for module in modules:
        command.extend(["--module", module])
    for item_id in config.ids:
        command.extend(["--item", item_id])
    if config.strict:
        command.append("--strict")
    run_command("build_detail_page_js delta", command, stages=stages)

    paths.canonical_module_dir.mkdir(parents=True, exist_ok=True)
    paths.canonical_report_dir.mkdir(parents=True, exist_ok=True)

    merged: dict[str, Any] = {}
    for module in modules:
        detail_js = paths.detail_dir / f"{module}.js"
        if not detail_js.exists():
            LOGGER.debug("No detail JS for module %s at %s", module, detail_js)
            continue
        module_output = paths.canonical_module_dir / f"{module}.canonical_content_v2.json"
        module_report = paths.canonical_report_dir / f"{module}.conversion_report.json"
        command = [
            sys.executable,
            str(SCRIPT_DIR / "migrate_detail_js_to_content_v2.py"),
            "--input",
            str(detail_js),
            "--output",
            str(module_output),
            "--report",
            str(module_report),
        ]
        if config.strict:
            command.append("--strict-validation")
        run_command(f"migrate_detail_js_to_content_v2 delta [{module}]", command, stages=stages)

        payload = read_json(module_output)
        if not isinstance(payload, dict):
            raise PublishError(f"Canonical module output is not an object: {module_output}")
        for record_id, record in payload.items():
            if record_id in merged:
                raise PublishError(f"Duplicate ID in canonical delta: {record_id}")
            merged[record_id] = record

    missing = [item_id for item_id in config.ids if item_id not in merged]
    if missing:
        raise PublishError("Canonical delta missing ID(s): " + ", ".join(missing))
    trimmed = {item_id: merged[item_id] for item_id in config.ids}
    write_json_plain(paths.canonical_raw, trimmed)
    LOGGER.info("Canonical raw delta written | %s | records=%d", paths.canonical_raw, len(trimmed))


def postprocess_canonical_delta(
    config: PublishConfig,
    paths: PublishPaths,
    stages: list[StageResult],
) -> None:
    run_command(
        "mark_need_image_by_latex_length delta",
        [
            sys.executable,
            str(SCRIPT_DIR / "mark_need_image_by_latex_length.py"),
            "--input",
            str(paths.canonical_raw),
            "--output",
            str(paths.canonical_marked),
            "--min-length",
            str(config.formula_min_length),
        ],
        stages=stages,
    )
    tikz_report_snapshot = (
        RENDER_TIKZ_ASSETS_REPORT.read_bytes()
        if RENDER_TIKZ_ASSETS_REPORT.exists()
        else None
    )
    try:
        run_command(
            "render_tikz_assets delta",
            [
                "node",
                str(SCRIPT_DIR / "render_tikz_assets.mjs"),
                "--input",
                str(paths.canonical_marked),
                "--output",
                str(paths.canonical_tikz_rendered),
                "--out-dir",
                str(paths.tikz_out_dir),
                "--asset-base",
                derive_tikz_asset_base(config.asset_base),
            ],
            stages=stages,
        )
        if RENDER_TIKZ_ASSETS_REPORT.exists():
            ensure_parent(paths.tikz_render_report)
            shutil.copy2(RENDER_TIKZ_ASSETS_REPORT, paths.tikz_render_report)
    finally:
        if tikz_report_snapshot is not None:
            ensure_parent(RENDER_TIKZ_ASSETS_REPORT)
            RENDER_TIKZ_ASSETS_REPORT.write_bytes(tikz_report_snapshot)
        elif RENDER_TIKZ_ASSETS_REPORT.exists():
            try:
                RENDER_TIKZ_ASSETS_REPORT.unlink()
            except OSError:
                LOGGER.warning(
                    "Could not remove generated TikZ render report: %s",
                    RENDER_TIKZ_ASSETS_REPORT,
                )
    render_report_snapshot = (
        RENDER_MATH_ASSETS_REPORT.read_bytes()
        if RENDER_MATH_ASSETS_REPORT.exists()
        else None
    )
    try:
        run_command(
            "render_math_assets delta",
            [
                "node",
                str(SCRIPT_DIR / "render_math_assets.mjs"),
                "--input",
                str(paths.canonical_tikz_rendered),
                "--output",
                str(paths.canonical_rendered),
                "--out-dir",
                str(paths.formula_out_dir),
                "--asset-base",
                config.asset_base,
            ],
            stages=stages,
        )
        if RENDER_MATH_ASSETS_REPORT.exists():
            ensure_parent(paths.formula_render_report)
            shutil.copy2(RENDER_MATH_ASSETS_REPORT, paths.formula_render_report)
    finally:
        if render_report_snapshot is not None:
            ensure_parent(RENDER_MATH_ASSETS_REPORT)
            RENDER_MATH_ASSETS_REPORT.write_bytes(render_report_snapshot)
        elif RENDER_MATH_ASSETS_REPORT.exists():
            try:
                RENDER_MATH_ASSETS_REPORT.unlink()
            except OSError:
                LOGGER.warning(
                    "Could not remove generated render report: %s",
                    RENDER_MATH_ASSETS_REPORT,
                )
    run_command(
        "remove_math_image_following_period delta",
        [
            sys.executable,
            str(SCRIPT_DIR / "remove_math_image_following_period.py"),
            "--input",
            str(paths.canonical_rendered),
            "--output",
            str(paths.canonical_final),
            "--write",
        ],
        stages=stages,
    )


def sync_backend_core_formula_delta(
    config: PublishConfig,
    paths: PublishPaths,
    stages: list[StageResult],
) -> None:
    command = [
        sys.executable,
        str(SCRIPT_DIR / "sync_backend_core_formula_assets.py"),
        "--backend-json",
        str(paths.backend_delta),
        "--canonical-json",
        str(paths.canonical_final),
        "--output",
        str(paths.backend_delta_final),
        "--report",
        str(paths.core_formula_sync_report),
        "--write",
    ]
    if config.strict:
        command.append("--strict")
    if config.allow_primary_fallback:
        command.append("--allow-primary-fallback")
    run_command("sync_backend_core_formula_assets delta", command, stages=stages)


def normalize_suggestion_key(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).strip().lower()
    return re.sub(r"\s+", " ", text)


def doc_rank(docs: dict[str, Any], doc_id: str) -> int:
    doc = docs.get(doc_id)
    if not isinstance(doc, dict):
        return 0
    try:
        return int(doc.get("rank") or 0)
    except (TypeError, ValueError):
        return 0


def posting_doc_id(posting: Any) -> str:
    if isinstance(posting, list) and posting:
        return str(posting[0])
    return ""


def posting_score(posting: Any) -> int:
    if isinstance(posting, list) and len(posting) > 1:
        try:
            return int(posting[1])
        except (TypeError, ValueError):
            return 0
    return 0


def sort_postings(
    postings: list[Any],
    docs: dict[str, Any],
    *,
    limit: int | None = None,
) -> list[Any]:
    filtered = [row for row in postings if isinstance(row, list) and len(row) >= 3]
    filtered.sort(
        key=lambda row: (
            -posting_score(row),
            -doc_rank(docs, posting_doc_id(row)),
            posting_doc_id(row),
        )
    )
    return filtered[:limit] if limit is not None else filtered


def merge_posting_index(
    base_index: Any,
    delta_index: Any,
    docs: dict[str, Any],
    target_ids: set[str],
    *,
    limit: int | None = None,
) -> dict[str, Any]:
    if not isinstance(base_index, dict):
        raise PublishError("Base posting index must be an object.")
    if not isinstance(delta_index, dict):
        raise PublishError("Delta posting index must be an object.")

    merged: dict[str, list[Any]] = {}
    for term, postings in base_index.items():
        if not isinstance(postings, list):
            continue
        kept = [row for row in postings if posting_doc_id(row) not in target_ids]
        if kept:
            merged[str(term)] = kept

    for term, postings in delta_index.items():
        if not isinstance(postings, list):
            continue
        target_postings = [
            row for row in postings if posting_doc_id(row) in target_ids
        ]
        if target_postings:
            merged.setdefault(str(term), []).extend(target_postings)

    return {
        term: sort_postings(rows, docs, limit=limit)
        for term, rows in sorted(merged.items())
        if rows
    }


def suggestion_score(row: Any) -> int:
    if isinstance(row, list) and len(row) > 2:
        try:
            return int(row[2])
        except (TypeError, ValueError):
            return 0
    return 0


def suggestion_doc_id(row: Any) -> str:
    if isinstance(row, list) and len(row) > 1:
        return str(row[1])
    return ""


def merge_suggestions(
    base_suggestions: Any,
    delta_suggestions: Any,
    target_ids: set[str],
    *,
    limit: int,
) -> list[Any]:
    if not isinstance(base_suggestions, list):
        raise PublishError("Base suggestions must be a list.")
    if not isinstance(delta_suggestions, list):
        raise PublishError("Delta suggestions must be a list.")

    by_key: dict[str, Any] = {}

    def add(row: Any) -> None:
        if not isinstance(row, list) or len(row) < 3:
            return
        key = normalize_suggestion_key(row[0])
        if not key:
            return
        current = by_key.get(key)
        if current is None or suggestion_score(row) > suggestion_score(current):
            by_key[key] = row

    for row in base_suggestions:
        if suggestion_doc_id(row) not in target_ids:
            add(row)
    for row in delta_suggestions:
        if suggestion_doc_id(row) in target_ids:
            add(row)

    rows = list(by_key.values())
    rows.sort(
        key=lambda row: (
            -suggestion_score(row),
            str(row[0]) if len(row) > 0 else "",
            suggestion_doc_id(row),
        )
    )
    return rows[:limit]


def get_positive_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def without_top_generated_at(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    cloned = dict(payload)
    cloned.pop("generatedAt", None)
    return cloned


def merge_canonical(config: PublishConfig, paths: PublishPaths) -> dict[str, Any]:
    base, style = read_json_with_style(config.canonical_path)
    delta = read_json(paths.canonical_final)
    if not isinstance(base, dict) or not isinstance(delta, dict):
        raise PublishError("Canonical base and delta must both be objects.")

    before_count = len(base)
    for item_id in config.ids:
        if item_id not in delta:
            raise PublishError(f"Canonical final delta missing ID: {item_id}")
        base[item_id] = delta[item_id]
    after_count = len(base)

    write_json_plain(paths.merged_canonical, base)
    if not config.dry_run:
        backup_file(config.canonical_path)
        write_json_atomic(config.canonical_path, base, style)

    return {"before": before_count, "after": after_count, "path": str(config.canonical_path)}


def merge_backend_index(config: PublishConfig, paths: PublishPaths) -> dict[str, Any]:
    base, style = read_json_with_style(config.backend_index_path)
    delta = read_json(paths.backend_delta_final)
    if not isinstance(base, dict) or not isinstance(delta, dict):
        raise PublishError("Backend base and delta must both be objects.")
    original_base = copy.deepcopy(base)

    if base.get("fieldMaskLegend") != delta.get("fieldMaskLegend"):
        raise PublishError("fieldMaskLegend mismatch between base and delta backend indexes.")

    docs = base.get("docs")
    delta_docs = delta.get("docs")
    if not isinstance(docs, dict) or not isinstance(delta_docs, dict):
        raise PublishError("Backend indexes must contain object field: docs.")

    target_ids = set(config.ids)
    before_docs = len(docs)
    for item_id in config.ids:
        if item_id not in delta_docs:
            raise PublishError(f"Backend delta missing docs.{item_id}")
        docs[item_id] = delta_docs[item_id]

    build_options = base.get("buildOptions") if isinstance(base.get("buildOptions"), dict) else {}
    suggestion_limit = get_positive_int(build_options.get("suggestionLimit"), 500)
    if isinstance(build_options, dict):
        build_options.pop("prefixDocLimit", None)

    base.pop("termIndex", None)
    base.pop("prefixIndex", None)
    base["suggestions"] = merge_suggestions(
        base.get("suggestions"),
        delta.get("suggestions"),
        target_ids,
        limit=suggestion_limit,
    )

    stats = base.setdefault("stats", {})
    if isinstance(stats, dict):
        stats["documents"] = len(docs)
        stats.pop("terms", None)
        stats.pop("prefixes", None)
        stats["suggestions"] = len(base["suggestions"])

    material_changed = without_top_generated_at(base) != without_top_generated_at(original_base)
    if material_changed:
        base["generatedAt"] = iso_now()
    elif "generatedAt" in original_base:
        base["generatedAt"] = original_base["generatedAt"]
    else:
        base.pop("generatedAt", None)

    write_json_plain(paths.merged_backend_index, base)
    if not config.dry_run:
        backup_file(config.backend_index_path)
        write_json_atomic(config.backend_index_path, base, style)

    return {
        "docs_before": before_docs,
        "docs_after": len(docs),
        "suggestions_after": len(base["suggestions"]),
        "material_changed": material_changed,
        "generated_at_updated": material_changed,
        "path": str(config.backend_index_path),
    }


def build_pdfs(
    config: PublishConfig,
    paths: PublishPaths,
    stages: list[StageResult],
) -> dict[str, str]:
    if config.dry_run:
        command = [
            sys.executable,
            str(SCRIPT_DIR / "build_conclusion_pdfs.py"),
            *config.ids,
            "--dry-run",
        ]
        run_command("build_conclusion_pdfs delta dry-run", command, stages=stages)
        return {item_id: expected_pdf_name(item_id) for item_id in config.ids}

    command = [
        sys.executable,
        str(SCRIPT_DIR / "build_conclusion_pdfs.py"),
        *config.ids,
        "--output-dir",
        str(paths.pdf_dir),
        "--map-json",
        str(paths.pdf_map_delta),
        "--overwrite",
    ]
    run_command("build_conclusion_pdfs delta", command, stages=stages)
    payload = read_json(paths.pdf_map_delta)
    if not isinstance(payload, dict):
        raise PublishError("PDF map delta must be an object.")
    missing = [item_id for item_id in config.ids if item_id not in payload]
    if missing:
        raise PublishError("PDF map delta missing ID(s): " + ", ".join(missing))
    return {item_id: str(payload[item_id]) for item_id in config.ids}


def merge_pdf_map(
    config: PublishConfig,
    paths: PublishPaths,
    pdf_delta: dict[str, str],
) -> dict[str, Any]:
    baseline_path = config.backend_data_dir / "conclusion_pdf_map.json"
    base, _style = read_json_with_style(baseline_path)
    if not isinstance(base, dict):
        raise PublishError(f"Backend PDF map baseline is not an object: {baseline_path}")

    before = len(base)
    for item_id, pdf_name in pdf_delta.items():
        base[item_id] = pdf_name

    write_json_plain(paths.merged_pdf_map, base)
    if not config.dry_run:
        backup_file(config.pdf_map_path)
        write_json_atomic(config.pdf_map_path, base, JsonStyle())

    return {
        "baseline": str(baseline_path),
        "path": str(config.pdf_map_path),
        "before": before,
        "after": len(base),
    }


def copy_backend_data_file(src: Path, dst: Path) -> None:
    if not src.exists():
        raise PublishError(f"Source file does not exist: {src}")
    ensure_parent(dst)
    shutil.copy2(src, dst)
    LOGGER.info("Copied | %s -> %s", src, dst)


def sync_backend_data(
    config: PublishConfig,
    pdf_delta: dict[str, str],
    stages: list[StageResult],
) -> dict[str, Any]:
    if config.pull_backend_repo:
        run_command(
            "local backend git pull --ff-only",
            ["git", "-C", str(config.backend_repo), "pull", "--ff-only"],
            stages=stages,
        )

    if config.dry_run or not config.sync_backend_data:
        return {"skipped": True, "reason": "dry-run or --skip-backend-sync"}

    copied_files: list[str] = []
    core_targets = [
        (config.canonical_path, config.backend_data_dir / "canonical_content_v2.json"),
        (config.backend_index_path, config.backend_data_dir / "backend_search_index.json"),
        (config.pdf_map_path, config.backend_data_dir / "conclusion_pdf_map.json"),
    ]
    for src, dst in core_targets:
        copy_backend_data_file(src, dst)
        copied_files.append(str(dst))

    pdf_dest_dir = config.backend_data_dir / "pdfs"
    pdf_dest_dir.mkdir(parents=True, exist_ok=True)
    copied_pdfs: list[str] = []
    for pdf_name in pdf_delta.values():
        src = config.pdf_output_dir / pdf_name
        dst = pdf_dest_dir / pdf_name
        copy_backend_data_file(src, dst)
        copied_pdfs.append(str(dst))
        copied_files.append(str(dst))

    return {
        "skipped": False,
        "backend_data_dir": str(config.backend_data_dir),
        "files": copied_files,
        "pdfs": copied_pdfs,
    }


def git_relative_path(repo: Path, path: Path) -> str:
    repo_resolved = repo.resolve()
    path_resolved = path.resolve()
    try:
        common = os.path.commonpath([str(repo_resolved), str(path_resolved)])
    except ValueError as exc:
        raise PublishError(f"Path is not on the backend repo drive: {path}") from exc

    if os.path.normcase(common) != os.path.normcase(str(repo_resolved)):
        raise PublishError(f"Path is outside backend repo: {path}")
    return Path(os.path.relpath(path_resolved, repo_resolved)).as_posix()


def publish_backend_git(
    config: PublishConfig,
    backend_sync_result: dict[str, Any],
    stages: list[StageResult],
) -> dict[str, Any]:
    if config.dry_run or not config.backend_git_publish:
        return {"skipped": True, "reason": "dry-run or backend git publish disabled"}
    if backend_sync_result.get("skipped"):
        return {
            "skipped": True,
            "reason": "backend data sync skipped",
        }

    raw_files = backend_sync_result.get("files") or []
    if not isinstance(raw_files, list) or not raw_files:
        return {"skipped": True, "reason": "no backend files were synced"}

    rel_files = [git_relative_path(config.backend_repo, Path(item)) for item in raw_files]
    status = run_command(
        "local backend git status targeted files",
        ["git", "-C", str(config.backend_repo), "status", "--porcelain", "--", *rel_files],
        stages=stages,
    )
    if not status.stdout.strip():
        return {
            "skipped": True,
            "reason": "no git changes in synced backend files",
            "files": rel_files,
        }

    run_command(
        "local backend git add synced files",
        ["git", "-C", str(config.backend_repo), "add", "--", *rel_files],
        stages=stages,
    )
    staged = run_command(
        "local backend git staged targeted files",
        ["git", "-C", str(config.backend_repo), "diff", "--cached", "--name-only", "--", *rel_files],
        stages=stages,
    )
    staged_files = [line.strip() for line in staged.stdout.splitlines() if line.strip()]
    if not staged_files:
        return {
            "skipped": True,
            "reason": "no staged changes in synced backend files",
            "files": rel_files,
        }

    run_command(
        "local backend git commit synced files",
        [
            "git",
            "-C",
            str(config.backend_repo),
            "commit",
            "-m",
            config.backend_commit_message,
            "--",
            *rel_files,
        ],
        stages=stages,
    )

    pushed = False
    if config.backend_git_push:
        run_command(
            "local backend git push",
            ["git", "-C", str(config.backend_repo), "push"],
            stages=stages,
        )
        pushed = True

    return {
        "skipped": False,
        "backend_repo": str(config.backend_repo),
        "commit_message": config.backend_commit_message,
        "files": staged_files,
        "pushed": pushed,
    }


def project_json_artifact_paths(config: PublishConfig) -> list[Path]:
    return [
        config.canonical_path,
        config.backend_index_path,
        config.report_path,
    ]


def project_backup_source_paths(config: PublishConfig) -> list[Path]:
    return [
        config.canonical_path,
        config.backend_index_path,
        config.pdf_map_path,
        config.report_path,
    ]


def path_is_within(root: Path, path: Path) -> bool:
    root_resolved = root.resolve()
    path_resolved = path.resolve()
    try:
        common = os.path.commonpath([str(root_resolved), str(path_resolved)])
    except ValueError:
        return False
    return os.path.normcase(common) == os.path.normcase(str(root_resolved))


def cleanup_project_backup_files(config: PublishConfig) -> list[str]:
    deleted: list[str] = []
    for source_path in project_backup_source_paths(config):
        if not path_is_within(PROJECT_ROOT, source_path):
            continue
        for backup_path in sorted(source_path.parent.glob(f"{source_path.name}.bak_*")):
            if not path_is_within(PROJECT_ROOT, backup_path):
                raise PublishError(f"Refusing to delete backup outside project root: {backup_path}")
            if backup_path.is_file():
                backup_path.unlink()
                deleted.append(str(backup_path))
                LOGGER.info("Project backup removed | %s", backup_path)
    return deleted


def publish_project_git(
    config: PublishConfig,
    stages: list[StageResult],
) -> dict[str, Any]:
    if config.dry_run or not config.project_git_publish:
        return {"skipped": True, "reason": "dry-run or project git publish disabled"}

    rel_files = [git_relative_path(PROJECT_ROOT, path) for path in project_json_artifact_paths(config)]
    status = run_command(
        "local project git status publish artifacts",
        ["git", "-C", str(PROJECT_ROOT), "status", "--porcelain", "--", *rel_files],
        stages=stages,
    )
    if not status.stdout.strip():
        return {
            "skipped": True,
            "reason": "no git changes in project publish artifacts",
            "files": rel_files,
        }

    run_command(
        "local project git add publish artifacts",
        ["git", "-C", str(PROJECT_ROOT), "add", "--", *rel_files],
        stages=stages,
    )
    staged = run_command(
        "local project git staged publish artifacts",
        ["git", "-C", str(PROJECT_ROOT), "diff", "--cached", "--name-only", "--", *rel_files],
        stages=stages,
    )
    staged_files = [line.strip() for line in staged.stdout.splitlines() if line.strip()]
    if not staged_files:
        return {
            "skipped": True,
            "reason": "no staged project publish artifact changes",
            "files": rel_files,
        }

    run_command(
        "local project git commit publish artifacts",
        [
            "git",
            "-C",
            str(PROJECT_ROOT),
            "commit",
            "-m",
            config.project_commit_message,
            "--",
            *rel_files,
        ],
        stages=stages,
    )

    pushed = False
    if config.project_git_push:
        run_command(
            "local project git push",
            ["git", "-C", str(PROJECT_ROOT), "push"],
            stages=stages,
        )
        pushed = True

    return {
        "skipped": False,
        "files": staged_files,
        "commit_message": config.project_commit_message,
        "pushed": pushed,
    }


def remote_ref(config: PublishConfig) -> str:
    return f"{config.remote_user}@{config.remote_host}"


def remote_askpass_path(paths: PublishPaths) -> Path:
    suffix = ".cmd" if os.name == "nt" else ".sh"
    return paths.tmp_root / f"ssh_askpass{suffix}"


def ensure_remote_askpass_script(config: PublishConfig, paths: PublishPaths) -> Path:
    path = remote_askpass_path(paths)
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        path.write_text(
            "@echo off\r\n"
            f"echo(%{REMOTE_ASKPASS_PASSWORD_ENV}%\r\n",
            encoding="utf-8",
        )
    else:
        path.write_text(
            "#!/bin/sh\n"
            f"printf '%s\\n' {shell_quote(config.remote_password)}\n",
            encoding="utf-8",
        )
        path.chmod(0o700)
    return path


def remote_auth_prefix(config: PublishConfig) -> list[str]:
    if not config.remote_password or shutil.which("sshpass") is None:
        return []
    return ["sshpass", "-e"]


def remote_auth_env(config: PublishConfig, paths: PublishPaths) -> dict[str, str] | None:
    if not config.remote_password:
        return None
    if shutil.which("sshpass") is not None:
        return {"SSHPASS": config.remote_password}
    askpass_path = ensure_remote_askpass_script(config, paths)
    return {
        "SSH_ASKPASS": str(askpass_path),
        "SSH_ASKPASS_REQUIRE": "force",
        "DISPLAY": "none",
        REMOTE_ASKPASS_PASSWORD_ENV: config.remote_password,
    }


def remote_sudo_input(config: PublishConfig) -> str | None:
    if not config.remote_password:
        return None
    # Windows OpenSSH can consume the first piped line for SSH auth when
    # askpass is unavailable; sudo then reads the next line.
    return config.remote_password + "\n" + config.remote_password + "\n"


def remote_ssh_options(config: PublishConfig) -> list[str]:
    return [
        "-o",
        f"BatchMode={'no' if config.remote_password else 'yes'}",
        "-o",
        "NumberOfPasswordPrompts=1",
        "-o",
        "StrictHostKeyChecking=accept-new",
    ]


def remote_ssh_command(config: PublishConfig, *args: str) -> list[str]:
    return [
        *remote_auth_prefix(config),
        "ssh",
        *remote_ssh_options(config),
        *args,
    ]


def remote_scp_command(config: PublishConfig, *args: str) -> list[str]:
    return [
        *remote_auth_prefix(config),
        "scp",
        *remote_ssh_options(config),
        *args,
    ]


def project_relative_posix_path(path: Path) -> str:
    root = PROJECT_ROOT.resolve()
    resolved = path.resolve()
    try:
        common = os.path.commonpath([str(root), str(resolved)])
    except ValueError as exc:
        raise PublishError(f"Path is not on the project drive: {path}") from exc

    if os.path.normcase(common) != os.path.normcase(str(root)):
        raise PublishError(f"Path is outside project root: {path}")
    return Path(os.path.relpath(resolved, root)).as_posix()


def remote_formula_owner_group(config: PublishConfig) -> str:
    owner = config.remote_formula_owner.strip()
    group = config.remote_formula_group.strip()
    if not owner or not group:
        raise PublishError("Remote formula owner/group must not be empty.")
    return f"{owner}:{group}"


def upload_formula_dirs(
    config: PublishConfig,
    paths: PublishPaths,
    stages: list[StageResult],
) -> dict[str, Any]:
    if config.dry_run or not config.upload_formulas:
        return {"skipped": True, "reason": "dry-run or upload not requested"}

    uploaded: list[str] = []
    tikz_uploaded: list[str] = []
    target = remote_ref(config)
    remote_stage_root = f"/tmp/{paths.tmp_root.name}/formulas"
    remote_tikz_stage_root = f"/tmp/{paths.tmp_root.name}/tikz"
    remote_tikz_dir = config.remote_tikz_dir
    owner_group = remote_formula_owner_group(config)
    run_command(
        "remote prepare formula upload staging",
        remote_ssh_command(
            config,
            target,
            (
                f"rm -rf -- {shell_quote(remote_stage_root)} {shell_quote(remote_tikz_stage_root)} "
                f"&& mkdir -p -- {shell_quote(remote_stage_root)} {shell_quote(remote_tikz_stage_root)}"
            ),
        ),
        stages=stages,
        interactive=True,
        env=remote_auth_env(config, paths),
    )

    for item_id in config.ids:
        local_dir = paths.formula_out_dir / item_id
        if not local_dir.is_dir():
            raise PublishError(f"Formula directory not found for {item_id}: {local_dir}")
        # Windows drive-letter paths such as D:/... can be misread by scp as
        # host:path remote specs, so upload from a project-relative source.
        local_source = project_relative_posix_path(local_dir)
        remote_item_dir = f"{config.remote_formula_dir}/{item_id}"
        remote_staged_item_dir = f"{remote_stage_root}/{item_id}"
        run_command(
            f"upload formula dir to staging [{item_id}]",
            remote_scp_command(
                config,
                "-r",
                local_source,
                f"{target}:{remote_stage_root}/",
            ),
            cwd=PROJECT_ROOT,
            stages=stages,
            interactive=True,
            env=remote_auth_env(config, paths),
        )
        install_steps = [
            f"[ -d {shell_quote(remote_staged_item_dir)} ]",
            f"mkdir -p -- {shell_quote(config.remote_formula_dir)}",
            f"rm -rf -- {shell_quote(remote_item_dir)}",
            f"cp -a -- {shell_quote(remote_staged_item_dir)} {shell_quote(config.remote_formula_dir + '/')}",
            f"chown -- {shell_quote(owner_group)} {shell_quote(config.remote_formula_dir)}",
            f"chown -R -- {shell_quote(owner_group)} {shell_quote(remote_item_dir)}",
        ]
        run_command(
            f"remote install formula dir [{item_id}]",
            remote_ssh_command(
                config,
                "-tt",
                target,
                sudo_login_shell(
                    " && ".join(install_steps),
                    password_stdin=bool(config.remote_password),
                ),
            ),
            stages=stages,
            interactive=True,
            env=remote_auth_env(config, paths),
            input_text=remote_sudo_input(config),
        )
        uploaded.append(remote_item_dir)

    for item_id in config.ids:
        local_dir = paths.tikz_out_dir / item_id
        if not local_dir.is_dir():
            continue
        local_source = project_relative_posix_path(local_dir)
        remote_item_dir = f"{remote_tikz_dir}/{item_id}"
        remote_staged_item_dir = f"{remote_tikz_stage_root}/{item_id}"
        run_command(
            f"upload TikZ dir to staging [{item_id}]",
            remote_scp_command(
                config,
                "-r",
                local_source,
                f"{target}:{remote_tikz_stage_root}/",
            ),
            cwd=PROJECT_ROOT,
            stages=stages,
            interactive=True,
            env=remote_auth_env(config, paths),
        )
        install_steps = [
            f"[ -d {shell_quote(remote_staged_item_dir)} ]",
            f"mkdir -p -- {shell_quote(remote_tikz_dir)}",
            f"rm -rf -- {shell_quote(remote_item_dir)}",
            f"cp -a -- {shell_quote(remote_staged_item_dir)} {shell_quote(remote_tikz_dir + '/')}",
            f"chown -- {shell_quote(owner_group)} {shell_quote(remote_tikz_dir)}",
            f"chown -R -- {shell_quote(owner_group)} {shell_quote(remote_item_dir)}",
        ]
        run_command(
            f"remote install TikZ dir [{item_id}]",
            remote_ssh_command(
                config,
                "-tt",
                target,
                sudo_login_shell(
                    " && ".join(install_steps),
                    password_stdin=bool(config.remote_password),
                ),
            ),
            stages=stages,
            interactive=True,
            env=remote_auth_env(config, paths),
            input_text=remote_sudo_input(config),
        )
        tikz_uploaded.append(remote_item_dir)

    run_command(
        "remote cleanup formula upload staging",
        remote_ssh_command(
            config,
            target,
            f"rm -rf -- {shell_quote(remote_stage_root)} {shell_quote(remote_tikz_stage_root)}",
        ),
        stages=stages,
        interactive=True,
        env=remote_auth_env(config, paths),
    )
    return {
        "skipped": False,
        "uploaded": uploaded,
        "tikz_uploaded": tikz_uploaded,
        "staging": remote_stage_root,
        "tikz_staging": remote_tikz_stage_root,
        "remote_formula_dir": config.remote_formula_dir,
        "remote_tikz_dir": remote_tikz_dir,
        "owner_group": owner_group,
    }


def shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def sudo_login_shell(command: str, *, password_stdin: bool = False) -> str:
    sudo_command = "sudo -S -p '' -i bash -lc" if password_stdin else "sudo -i bash -lc"
    return f"{sudo_command} {shell_quote(command)}"


def remote_pull_and_restart(
    config: PublishConfig,
    paths: PublishPaths,
    stages: list[StageResult],
) -> dict[str, Any]:
    if config.dry_run or not config.remote_pull:
        return {"skipped": True, "reason": "dry-run or remote pull not requested"}

    target = remote_ref(config)
    root_steps = [
        f"cd {shell_quote(config.remote_backend_root)}",
        "git pull --ff-only",
    ]
    if config.restart:
        root_steps.append(config.restart_command)
    root_command = " && ".join(root_steps)

    run_command(
        "remote backend git pull/restart as root",
        remote_ssh_command(
            config,
            "-tt",
            target,
            sudo_login_shell(root_command, password_stdin=bool(config.remote_password)),
        ),
        stages=stages,
        interactive=True,
        env=remote_auth_env(config, paths),
        input_text=remote_sudo_input(config),
    )
    return {
        "skipped": False,
        "remote_backend_root": config.remote_backend_root,
        "restart": config.restart,
        "sudo_login_shell": True,
    }


def write_report(report: PublishReport, config: PublishConfig, paths: PublishPaths) -> None:
    payload = asdict(report)
    paths.tmp_root.mkdir(parents=True, exist_ok=True)
    write_json_plain(paths.tmp_report, payload)
    ensure_parent(config.report_path)
    write_json_plain(config.report_path, payload)
    LOGGER.info("Report written | %s", config.report_path)


def backup_local_formula_dirs(config: PublishConfig, paths: PublishPaths) -> list[str]:
    if config.dry_run:
        LOGGER.info("Local formula backup skipped for dry run.")
        return []

    backed_up: list[str] = []
    for item_id in config.ids:
        source_dir = paths.formula_out_dir / item_id
        if not source_dir.is_dir():
            continue
        target_dir = DEFAULT_LOCAL_FORMULA_DIR / item_id
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
        backed_up.append(str(target_dir))
        LOGGER.info("Local formula assets backed up | %s -> %s", source_dir, target_dir)
    return backed_up


def cleanup_temp(paths: PublishPaths, config: PublishConfig) -> None:
    backup_local_formula_dirs(config, paths)
    if config.keep_temp:
        LOGGER.info("Temp workspace kept | %s", paths.tmp_root)
        return
    shutil.rmtree(paths.tmp_root, ignore_errors=True)
    LOGGER.info("Temp workspace removed | %s", paths.tmp_root)


def orchestrate(config: PublishConfig) -> PublishReport:
    validate_input_files(config)
    paths = create_paths(config)
    paths.tmp_root.mkdir(parents=True, exist_ok=False)
    stages: list[StageResult] = []
    report = PublishReport(
        generated_at=iso_now(),
        ids=list(config.ids),
        dry_run=config.dry_run,
        tmp_root=str(paths.tmp_root),
    )

    try:
        modules = infer_modules(config.ids)
        report.outputs["modules"] = modules
        LOGGER.info("Publish target | ids=%s | modules=%s", ", ".join(config.ids), ", ".join(modules))
        LOGGER.info("Temp root | %s", paths.tmp_root)

        build_search_delta(config, paths, modules, stages)
        build_canonical_delta(config, paths, modules, stages)
        postprocess_canonical_delta(config, paths, stages)
        sync_backend_core_formula_delta(config, paths, stages)

        canonical_counts = merge_canonical(config, paths)
        backend_counts = merge_backend_index(config, paths)
        pdf_delta = build_pdfs(config, paths, stages)
        pdf_map_counts = merge_pdf_map(config, paths, pdf_delta)
        backend_sync_result = sync_backend_data(config, pdf_delta, stages)
        backend_git_result = publish_backend_git(config, backend_sync_result, stages)
        formula_upload_result = upload_formula_dirs(config, paths, stages)
        remote_result = remote_pull_and_restart(config, paths, stages)
        project_backup_cleanup_result = cleanup_project_backup_files(config)

        report.stages = [asdict(item) for item in stages]
        report.counts["canonical"] = canonical_counts
        report.counts["backend_index"] = backend_counts
        report.counts["pdf_map"] = pdf_map_counts
        report.outputs.update(
            {
                "canonical_delta_final": str(paths.canonical_final),
                "backend_delta_final": str(paths.backend_delta_final),
                "merged_canonical_candidate": str(paths.merged_canonical),
                "merged_backend_candidate": str(paths.merged_backend_index),
                "merged_pdf_map_candidate": str(paths.merged_pdf_map),
                "formula_dirs": [str(paths.formula_out_dir / item_id) for item_id in config.ids],
                "tikz_dirs": [str(paths.tikz_out_dir / item_id) for item_id in config.ids],
                "pdf_delta": pdf_delta,
                "backend_sync": backend_sync_result,
                "backend_git": backend_git_result,
                "formula_upload": formula_upload_result,
                "remote": remote_result,
                "project_backup_cleanup": project_backup_cleanup_result,
            }
        )
        write_report(report, config, paths)
        publish_project_git(config, stages)
        return report
    finally:
        cleanup_temp(paths, config)


def main() -> int:
    args = parse_args()
    config = build_config(args)
    configure_logging(config.log_level)
    try:
        report = orchestrate(config)
        if config.dry_run:
            LOGGER.info("Dry run complete. No official files were overwritten.")
        else:
            LOGGER.info("Incremental publish complete | ids=%s", ", ".join(report.ids))
        return 0
    except PublishError as exc:
        LOGGER.error("%s", exc)
        return 1
    except KeyboardInterrupt:
        LOGGER.error("Interrupted by user.")
        return 130
    except Exception:
        LOGGER.exception("Unexpected incremental publish failure")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
