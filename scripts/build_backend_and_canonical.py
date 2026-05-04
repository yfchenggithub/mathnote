from __future__ import annotations

"""
统一构建 backend_search_index.json 与 canonical_content_v2.json。

设计目标
--------
1. 默认全量构建（不传 --module）。
2. 复用现有脚本，不复制核心业务逻辑。
3. 输出清晰阶段日志与结构化构建报告。
4. 支持 dry-run：不写最终 backend/canonical 目标文件。
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
META_FILENAME = "meta.json"

DEFAULT_BACKEND_OUTPUT = Path("data/search_engine/backend_search_index.json")
DEFAULT_CANONICAL_OUTPUT = Path("data/content/canonical_content_v2.json")
DEFAULT_REPORT_OUTPUT = Path("reports/build_backend_and_canonical_report.json")
DEFAULT_DETAIL_OUTPUT_DIR = Path("data/content")

IGNORED_TOP_LEVEL_DIRS = {
    ".git",
    ".github",
    ".vscode",
    "__pycache__",
    "assets",
    "data",
    "misc",
    "node_modules",
    "scripts",
    "search_engine",
    "templates",
    "reports",
}

LOGGER = logging.getLogger("build_backend_and_canonical")


class OrchestrationError(RuntimeError):
    """表示编排过程中的可解释错误。"""


@dataclass(frozen=True)
class BuildConfig:
    """脚本运行配置。"""

    base_dir: Path
    target_modules: tuple[str, ...]
    dry_run: bool
    strict: bool
    keep_temp: bool
    log_level: str
    output_backend: Path
    output_canonical: Path
    output_report: Path


@dataclass
class StageResult:
    """记录单个阶段的执行结果。"""

    name: str
    command: list[str]
    return_code: int
    duration_sec: float
    status: str
    stdout_tail: str = ""
    stderr_tail: str = ""
    note: str = ""


def configure_logging(level_name: str) -> None:
    """初始化日志。"""

    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""

    parser = argparse.ArgumentParser(
        description="同时构建 backend_search_index.json 与 canonical_content_v2.json",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/build_backend_and_canonical.py\n"
            "  python scripts/build_backend_and_canonical.py --dry-run --log-level DEBUG\n"
            "  python scripts/build_backend_and_canonical.py --module 07_inequality\n"
        ),
    )
    parser.add_argument(
        "--base-dir",
        default=str(PROJECT_ROOT),
        help="项目根目录。默认脚本所在仓库根目录。",
    )
    parser.add_argument(
        "--module",
        dest="modules",
        action="append",
        help="仅构建指定模块（可重复）。默认全量自动发现。",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="执行流程与统计，但不写最终 backend/canonical 输出文件。",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="严格模式：模块缺失等问题视为失败，并对子脚本开启 strict 选项。",
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="保留本次构建的临时目录（默认自动清理）。",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="日志级别，默认 INFO。",
    )
    parser.add_argument(
        "--output-backend",
        default=str(DEFAULT_BACKEND_OUTPUT),
        help=f"backend JSON 输出路径，默认: {DEFAULT_BACKEND_OUTPUT}",
    )
    parser.add_argument(
        "--output-canonical",
        default=str(DEFAULT_CANONICAL_OUTPUT),
        help=f"canonical JSON 输出路径，默认: {DEFAULT_CANONICAL_OUTPUT}",
    )
    parser.add_argument(
        "--report",
        default=str(DEFAULT_REPORT_OUTPUT),
        help=f"构建报告输出路径，默认: {DEFAULT_REPORT_OUTPUT}",
    )
    return parser.parse_args()


def resolve_path(base_dir: Path, value: str) -> Path:
    """把参数路径解析为绝对路径。"""

    path = Path(value)
    if path.is_absolute():
        return path.resolve()
    return (base_dir / path).resolve()


def build_config(args: argparse.Namespace) -> BuildConfig:
    """把 argparse 结果转换成强类型配置。"""

    base_dir = Path(args.base_dir).resolve()
    return BuildConfig(
        base_dir=base_dir,
        target_modules=tuple(args.modules or ()),
        dry_run=bool(args.dry_run),
        strict=bool(args.strict),
        keep_temp=bool(args.keep_temp),
        log_level=str(args.log_level).upper(),
        output_backend=resolve_path(base_dir, str(args.output_backend)),
        output_canonical=resolve_path(base_dir, str(args.output_canonical)),
        output_report=resolve_path(base_dir, str(args.report)),
    )


def module_contains_content(module_dir: Path) -> bool:
    """判断一个顶层目录是否像内容模块。"""

    try:
        for child in module_dir.iterdir():
            if not child.is_dir():
                continue
            if (child / META_FILENAME).exists() or (child / "01_statement.tex").exists():
                return True
    except OSError:
        return False
    return False


def discover_modules(base_dir: Path) -> list[str]:
    """自动发现可构建模块。"""

    modules: list[str] = []
    for path in sorted(base_dir.iterdir()):
        if not path.is_dir():
            continue
        if path.name in IGNORED_TOP_LEVEL_DIRS:
            continue
        if module_contains_content(path):
            modules.append(path.name)
    return modules


def resolve_target_modules(config: BuildConfig) -> list[str]:
    """解析最终模块列表。"""

    if not config.target_modules:
        discovered = discover_modules(config.base_dir)
        if not discovered:
            raise OrchestrationError("未发现可构建模块。")
        return discovered

    resolved: list[str] = []
    missing: list[str] = []
    for module_name in config.target_modules:
        module_dir = config.base_dir / module_name
        if module_dir.is_dir():
            resolved.append(module_name)
        else:
            missing.append(module_name)

    if missing:
        message = f"模块目录不存在: {', '.join(missing)}"
        if config.strict:
            raise OrchestrationError(message)
        LOGGER.warning(message)

    if not resolved:
        raise OrchestrationError("指定模块全部无效，无法继续。")
    return resolved


def tail_text(text: str, max_lines: int = 60) -> str:
    """保留输出末尾，避免报告过大。"""

    if not text:
        return ""
    lines = text.splitlines()
    return "\n".join(lines[-max_lines:])


def run_command(
    stage_name: str,
    command: list[str],
    workdir: Path,
    stage_results: list[StageResult],
) -> None:
    """执行子命令并记录阶段结果。"""

    LOGGER.info("Stage | %s", stage_name)
    LOGGER.debug("Command | %s", " ".join(command))
    started = time.perf_counter()
    result = subprocess.run(
        command,
        cwd=str(workdir),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    duration = time.perf_counter() - started
    stdout_tail = tail_text(result.stdout)
    stderr_tail = tail_text(result.stderr)
    ok = result.returncode == 0
    stage_results.append(
        StageResult(
            name=stage_name,
            command=command,
            return_code=result.returncode,
            duration_sec=duration,
            status="ok" if ok else "failed",
            stdout_tail=stdout_tail,
            stderr_tail=stderr_tail,
        )
    )

    if ok:
        LOGGER.info("Stage done | %s | %.2fs", stage_name, duration)
        if stdout_tail and LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.debug("Stage stdout tail | %s\n%s", stage_name, stdout_tail)
        return

    LOGGER.error("Stage failed | %s | exit=%d", stage_name, result.returncode)
    if stderr_tail:
        LOGGER.error("stderr tail:\n%s", stderr_tail)
    raise OrchestrationError(f"{stage_name} 失败（exit={result.returncode}）")


def read_json_file(path: Path) -> Any:
    """读取 JSON 文件。"""

    return json.loads(path.read_text(encoding="utf-8"))


def write_json_file(path: Path, payload: Any) -> None:
    """写 JSON 文件（UTF-8 + pretty）。"""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def create_workspace_temp_dir(base_dir: Path) -> Path:
    """在仓库内创建对子进程可见的临时目录。"""

    tmp_base = (base_dir / ".tmp").resolve()
    tmp_base.mkdir(parents=True, exist_ok=True)
    seed = int(time.time() * 1000)
    candidate = tmp_base / f"build_backend_and_canonical_{seed}_{os.getpid()}"
    index = 0
    while candidate.exists():
        index += 1
        candidate = tmp_base / (
            f"build_backend_and_canonical_{seed}_{os.getpid()}_{index}"
        )
    candidate.mkdir(parents=True, exist_ok=False)
    return candidate


def orchestrate(config: BuildConfig) -> dict[str, Any]:
    """执行完整构建流程并返回报告对象。"""

    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    started_perf = time.perf_counter()
    stage_results: list[StageResult] = []

    modules = resolve_target_modules(config)
    LOGGER.info("Target modules | %s", ", ".join(modules))

    tmp_root = create_workspace_temp_dir(config.base_dir)
    LOGGER.info("Temp root | %s", tmp_root)

    search_bundle_tmp = tmp_root / "search_bundle.js"
    search_audit_tmp = tmp_root / "search_audit.json"
    backend_tmp = tmp_root / "backend_search_index.json"
    backend_verify_report_tmp = tmp_root / "backend_index_verify_report.json"
    detail_output_dir = (
        tmp_root / "detail_data"
        if config.dry_run
        else (config.base_dir / DEFAULT_DETAIL_OUTPUT_DIR)
    )
    canonical_module_dir = tmp_root / "canonical_modules"
    canonical_report_dir = tmp_root / "conversion_reports"
    canonical_merged_tmp = tmp_root / "canonical_content_v2.json"

    try:
        # A1: build_search_bundle_js.py
        cmd_a1 = [
            sys.executable,
            str((SCRIPT_DIR / "build_search_bundle_js.py").resolve()),
            "--output-file",
            str(search_bundle_tmp),
            "--audit-report",
            str(search_audit_tmp),
        ]
        for module_name in modules:
            cmd_a1.extend(["--module", module_name])
        # 启用高级召回字段（仅扩展 termIndex，不放大低质量 prefix 候选）。
        cmd_a1.extend(
            [
                "--enable-knowledge-node-terms",
                "--enable-query-template-terms",
                "--enable-formula-token-terms",
                "--enable-formula-terms",
                "--enable-usage-terms",
            ]
        )
        if config.strict:
            cmd_a1.append("--strict")
        run_command("A1 build_search_bundle_js", cmd_a1, config.base_dir, stage_results)

        # A2: extract_backend_index_from_search_bundle.py
        cmd_a2 = [
            sys.executable,
            str((SCRIPT_DIR / "extract_backend_index_from_search_bundle.py").resolve()),
            "--input",
            str(search_bundle_tmp),
            "--output",
            str(backend_tmp),
            "--pretty",
        ]
        run_command(
            "A2 extract_backend_index_from_search_bundle",
            cmd_a2,
            config.base_dir,
            stage_results,
        )

        # A3: verify_backend_index_extraction.py
        cmd_a3 = [
            sys.executable,
            str((SCRIPT_DIR / "verify_backend_index_extraction.py").resolve()),
            "--bundle-js",
            str(search_bundle_tmp),
            "--backend-json",
            str(backend_tmp),
            "--report",
            str(backend_verify_report_tmp),
        ]
        run_command(
            "A3 verify_backend_index_extraction",
            cmd_a3,
            config.base_dir,
            stage_results,
        )

        # B1: build_detail_page_js.py
        cmd_b1 = [
            sys.executable,
            str((SCRIPT_DIR / "build_detail_page_js.py").resolve()),
            "--output-dir",
            str(detail_output_dir),
        ]
        for module_name in modules:
            cmd_b1.extend(["--module", module_name])
        if config.strict:
            cmd_b1.append("--strict")
        run_command("B1 build_detail_page_js", cmd_b1, config.base_dir, stage_results)

        # B2: migrate_detail_js_to_content_v2.py (per module)
        canonical_module_dir.mkdir(parents=True, exist_ok=True)
        canonical_report_dir.mkdir(parents=True, exist_ok=True)

        merged: dict[str, Any] = {}
        duplicate_ids: list[dict[str, str]] = []
        module_record_counts: dict[str, int] = {}
        migrated_modules: list[str] = []

        for module_name in modules:
            detail_js_path = detail_output_dir / f"{module_name}.js"
            if not detail_js_path.exists():
                message = f"detail js 不存在，跳过模块: {module_name} ({detail_js_path})"
                if config.strict:
                    raise OrchestrationError(message)
                LOGGER.warning(message)
                continue

            module_output = canonical_module_dir / f"{module_name}.canonical_content_v2.json"
            module_report = canonical_report_dir / f"{module_name}.conversion_report.json"
            cmd_b2 = [
                sys.executable,
                str((SCRIPT_DIR / "migrate_detail_js_to_content_v2.py").resolve()),
                "--input",
                str(detail_js_path),
                "--output",
                str(module_output),
                "--report",
                str(module_report),
            ]
            if config.strict:
                cmd_b2.append("--strict-validation")
            run_command(
                f"B2 migrate_detail_js_to_content_v2 [{module_name}]",
                cmd_b2,
                config.base_dir,
                stage_results,
            )

            payload = read_json_file(module_output)
            if not isinstance(payload, dict):
                raise OrchestrationError(
                    f"模块迁移结果顶层不是对象: {module_output}"
                )

            migrated_modules.append(module_name)
            module_record_counts[module_name] = len(payload)
            for record_id, record in payload.items():
                if record_id in merged:
                    existing = merged[record_id]
                    first_module = (
                        str(existing.get("_source_module", ""))
                        if isinstance(existing, dict)
                        else ""
                    )
                    duplicate_ids.append(
                        {
                            "id": str(record_id),
                            "first_module": first_module,
                            "second_module": module_name,
                        }
                    )
                    continue
                # 为了排查冲突，临时保存来源模块；落最终文件前再去掉。
                if isinstance(record, dict):
                    candidate = dict(record)
                    candidate["_source_module"] = module_name
                    merged[record_id] = candidate
                else:
                    merged[record_id] = record

        if not migrated_modules:
            raise OrchestrationError("没有任何模块成功迁移 canonical 内容。")

        if duplicate_ids:
            preview = ", ".join(item["id"] for item in duplicate_ids[:10])
            raise OrchestrationError(
                f"canonical 合并发现重复 id（示例）: {preview}"
            )

        # 删除临时来源字段
        for record in merged.values():
            if isinstance(record, dict):
                record.pop("_source_module", None)

        write_json_file(canonical_merged_tmp, merged)

        if not config.dry_run:
            config.output_backend.parent.mkdir(parents=True, exist_ok=True)
            config.output_canonical.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backend_tmp, config.output_backend)
            shutil.copy2(canonical_merged_tmp, config.output_canonical)
            LOGGER.info("Output backend | %s", config.output_backend)
            LOGGER.info("Output canonical | %s", config.output_canonical)
        else:
            LOGGER.info("[dry-run] Skip final write | backend=%s", config.output_backend)
            LOGGER.info(
                "[dry-run] Skip final write | canonical=%s", config.output_canonical
            )

        backend_payload = read_json_file(backend_tmp)
        backend_docs = (
            len(backend_payload.get("docs", {}))
            if isinstance(backend_payload, dict)
            else 0
        )

        report = {
            "script": "build_backend_and_canonical.py",
            "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "startedAt": started_at,
            "durationSec": round(time.perf_counter() - started_perf, 3),
            "status": "success",
            "options": {
                "dryRun": config.dry_run,
                "strict": config.strict,
                "keepTemp": config.keep_temp,
                "logLevel": config.log_level,
                "targetModules": modules,
            },
            "paths": {
                "tempRoot": str(tmp_root),
                "backendOutput": str(config.output_backend),
                "canonicalOutput": str(config.output_canonical),
                "backendVerifyReport": str(backend_verify_report_tmp),
                "detailOutputDir": str(detail_output_dir),
            },
            "summary": {
                "modulesRequested": len(modules),
                "modulesMigrated": len(migrated_modules),
                "moduleRecordCounts": module_record_counts,
                "canonicalRecords": len(merged),
                "backendDocs": backend_docs,
            },
            "stages": [asdict(stage) for stage in stage_results],
        }
        return report
    finally:
        if config.keep_temp:
            LOGGER.info("Keep temp root | %s", tmp_root)
        else:
            shutil.rmtree(tmp_root, ignore_errors=True)
            LOGGER.debug("Temp cleaned | %s", tmp_root)


def write_report_safe(path: Path, payload: dict[str, Any]) -> None:
    """尽量写报告，失败只记录日志。"""

    try:
        write_json_file(path, payload)
        LOGGER.info("Build report | %s", path)
    except Exception as exc:  # pragma: no cover - 报告写失败不应覆盖主错误
        LOGGER.error("写构建报告失败: %s", exc)


def main() -> int:
    """CLI 入口。"""

    args = parse_args()
    config = build_config(args)
    configure_logging(config.log_level)

    LOGGER.info("Base dir | %s", config.base_dir)
    LOGGER.info("Mode | dry_run=%s strict=%s", config.dry_run, config.strict)

    try:
        report = orchestrate(config)
        write_report_safe(config.output_report, report)
        LOGGER.info("Build finished successfully.")
        return 0
    except Exception as exc:
        LOGGER.error("Build failed: %s", exc)
        failure_report = {
            "script": "build_backend_and_canonical.py",
            "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "failed",
            "error": str(exc),
            "options": {
                "dryRun": config.dry_run,
                "strict": config.strict,
                "keepTemp": config.keep_temp,
                "logLevel": config.log_level,
                "targetModules": list(config.target_modules),
            },
            "paths": {
                "backendOutput": str(config.output_backend),
                "canonicalOutput": str(config.output_canonical),
            },
        }
        write_report_safe(config.output_report, failure_report)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
