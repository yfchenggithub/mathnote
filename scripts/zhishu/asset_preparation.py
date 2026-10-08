"""Prepare deterministic runtime images without modifying source PNGs or GIFs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
from typing import Any, Sequence

if __package__:
    from .source_discovery import ScanResult, scan_repository
else:
    from source_discovery import ScanResult, scan_repository


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = PROJECT_ROOT / "build" / "zhishu-runtime-assets"
WORKER_PATH = Path(__file__).with_name("prepare_knowledge_images.mjs")
IMAGE_CONTRACT = {
    "format": "webp",
    "quality": 85,
    "maxWidth": 1440,
    "preserveAspectRatio": True,
    "upscale": False,
}


class RuntimeAssetPreparationError(RuntimeError):
    """Raised when runtime images cannot be prepared or validated."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_jobs(scan_result: ScanResult, project_root: Path) -> list[dict[str, str]]:
    jobs: list[dict[str, str]] = []
    ids: set[str] = set()
    for module in scan_result.modules:
        for source in module.sources:
            try:
                record = json.loads(source.meta_json_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise RuntimeAssetPreparationError(
                    f"cannot read {source.meta_json_path}: {exc}"
                ) from exc
            knowledge_id = record.get("id") if isinstance(record, dict) else None
            if not isinstance(knowledge_id, str) or not knowledge_id:
                raise RuntimeAssetPreparationError(
                    f"{source.meta_json_path} must contain a non-empty id"
                )
            if knowledge_id in ids:
                raise RuntimeAssetPreparationError(f"duplicate knowledge id: {knowledge_id}")
            ids.add(knowledge_id)
            source_directory = source.conclusion_path / "images"
            jobs.append(
                {
                    "knowledgeId": knowledge_id,
                    "sourceDirectory": str(source_directory.resolve()),
                    "displayDirectory": source_directory.relative_to(project_root).as_posix(),
                }
            )
    return jobs


def prepare_runtime_images(
    scan_result: ScanResult,
    output_dir: Path = DEFAULT_OUTPUT,
    *,
    project_root: Path = PROJECT_ROOT,
    worker_path: Path = WORKER_PATH,
) -> dict[str, Any]:
    """Fully rebuild the runtime image mirror and return its stable manifest."""

    if scan_result.errors:
        raise RuntimeAssetPreparationError("source discovery failed; runtime images were not prepared")
    output_dir = output_dir.resolve()
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    jobs = {"sources": _source_jobs(scan_result, project_root.resolve())}
    staged_output = Path(
        tempfile.mkdtemp(
            prefix=f".{output_dir.name}.tmp-",
            dir=output_dir.parent,
        )
    )
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".json",
        prefix="zhishu-runtime-image-jobs-",
        dir=output_dir.parent,
        delete=False,
    ) as job_file:
        json.dump(jobs, job_file, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        jobs_path = Path(job_file.name)
    try:
        completed = subprocess.run(
            ["node", str(worker_path), "--jobs", str(jobs_path), "--output", str(staged_output)],
            cwd=project_root,
            text=True,
            capture_output=True,
            check=False,
        )
    finally:
        jobs_path.unlink(missing_ok=True)
    if completed.returncode != 0:
        shutil.rmtree(staged_output, ignore_errors=True)
        message = completed.stderr.strip() or completed.stdout.strip() or "unknown error"
        raise RuntimeAssetPreparationError(f"runtime image worker failed: {message}")
    backup = output_dir.parent / f".{output_dir.name}.old"
    shutil.rmtree(backup, ignore_errors=True)
    try:
        if output_dir.exists():
            output_dir.replace(backup)
        shutil.copytree(staged_output, output_dir)
    except BaseException:
        if output_dir.exists():
            shutil.rmtree(output_dir, ignore_errors=True)
        if backup.exists():
            backup.replace(output_dir)
        raise
    finally:
        shutil.rmtree(staged_output, ignore_errors=True)
    shutil.rmtree(backup, ignore_errors=True)
    manifest_path = output_dir / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeAssetPreparationError(f"cannot read prepared image manifest: {exc}") from exc
    return manifest


def verify_prepared_runtime_images(
    scan_result: ScanResult,
    output_dir: Path = DEFAULT_OUTPUT,
    *,
    project_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Prove the staging mirror matches current source bytes and the contract."""

    if scan_result.errors:
        raise RuntimeAssetPreparationError("source discovery failed; prepared images cannot be verified")
    output_dir = output_dir.resolve()
    manifest_path = output_dir / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeAssetPreparationError(f"cannot read prepared image manifest: {exc}") from exc
    if manifest.get("schemaVersion") != 1 or manifest.get("contract") != IMAGE_CONTRACT:
        raise RuntimeAssetPreparationError("prepared image manifest uses a stale contract")
    sharp_package = PROJECT_ROOT / "node_modules/sharp/package.json"
    try:
        sharp_version = json.loads(sharp_package.read_text(encoding="utf-8"))["version"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeAssetPreparationError(f"cannot determine Sharp version: {exc}") from exc
    if manifest.get("tool") != {"name": "sharp", "version": sharp_version}:
        raise RuntimeAssetPreparationError("prepared image manifest uses a stale tool version")

    expected: dict[str, tuple[Path, str]] = {}
    for job in _source_jobs(scan_result, project_root.resolve()):
        source_directory = Path(job["sourceDirectory"])
        if not source_directory.is_dir():
            raise RuntimeAssetPreparationError(
                f"source image directory does not exist: {job['displayDirectory']}"
            )
        for source_path in sorted(source_directory.iterdir(), key=lambda path: path.name):
            if source_path.name == ".gitkeep":
                continue
            suffix = source_path.suffix.lower()
            if not source_path.is_file() or suffix not in {".png", ".gif"}:
                raise RuntimeAssetPreparationError(
                    f"unsupported source image entry: {job['displayDirectory']}/{source_path.name}"
                )
            logical_source = f"{job['displayDirectory']}/{source_path.name}"
            expected[logical_source] = (
                source_path,
                f"images/{job['knowledgeId']}/{source_path.stem}{'.webp' if suffix == '.png' else '.gif'}",
            )

    assets = manifest.get("assets")
    if not isinstance(assets, list):
        raise RuntimeAssetPreparationError("prepared image manifest assets must be an array")
    actual_sources: set[str] = set()
    expected_outputs: set[str] = set()
    for asset in assets:
        if not isinstance(asset, dict) or not isinstance(asset.get("source"), str):
            raise RuntimeAssetPreparationError("prepared image manifest contains an invalid asset")
        logical_source = asset["source"]
        source = expected.get(logical_source)
        if source is None or logical_source in actual_sources:
            raise RuntimeAssetPreparationError("prepared image manifest source coverage is stale")
        source_path, expected_output = source
        if asset.get("output") != expected_output:
            raise RuntimeAssetPreparationError(f"prepared image output mapping is stale: {logical_source}")
        if asset.get("sourceSha256") != _sha256_file(source_path):
            raise RuntimeAssetPreparationError(f"prepared image source hash is stale: {logical_source}")
        output_path = output_dir.joinpath(*expected_output.split("/"))
        if not output_path.is_file() or asset.get("outputSha256") != _sha256_file(output_path):
            raise RuntimeAssetPreparationError(f"prepared image output hash is stale: {expected_output}")
        if source_path.suffix.lower() == ".gif" and _sha256_file(source_path) != _sha256_file(output_path):
            raise RuntimeAssetPreparationError(f"prepared GIF is not byte-identical: {expected_output}")
        actual_sources.add(logical_source)
        expected_outputs.add(expected_output)
    if actual_sources != set(expected):
        raise RuntimeAssetPreparationError("prepared image manifest source coverage is stale")
    actual_outputs = {
        path.relative_to(output_dir).as_posix()
        for path in (output_dir / "images").rglob("*")
        if path.is_file()
    } if (output_dir / "images").is_dir() else set()
    if actual_outputs != expected_outputs:
        raise RuntimeAssetPreparationError("prepared image directory contains missing or orphan files")
    return manifest


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    scan_result = scan_repository(PROJECT_ROOT)
    try:
        manifest = prepare_runtime_images(scan_result, args.output)
    except (RuntimeAssetPreparationError, OSError) as exc:
        print(f"Runtime image preparation failed: {exc}", file=sys.stderr)
        return 1
    total_bytes = sum(asset["bytes"] for asset in manifest["assets"])
    print(f"Prepared runtime images: {len(manifest['assets'])}")
    print(f"Prepared bytes: {total_bytes}")
    print(f"Tool: {manifest['tool']['name']} {manifest['tool']['version']}")
    print(f"Output: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
