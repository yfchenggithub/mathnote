"""Deterministic Zhishu content packages, validation, and package diffs."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

if __package__:
    from .runtime_mapping import RuntimeMappingResult
    from .source_discovery import ScanResult
else:
    from runtime_mapping import RuntimeMappingResult
    from source_discovery import ScanResult


SCHEMA_VERSION = 1
JSON_FILES = {
    "knowledgeNodes": "knowledge-nodes.json",
    "knowledgeRelations": "knowledge-relations.json",
    "knowledgeAssets": "knowledge-assets.json",
    "searchDocuments": "search-documents.json",
}
ENTITY_ID_FIELDS = {
    "knowledgeNodes": "id",
    "knowledgeRelations": "id",
    "knowledgeAssets": "id",
    "searchDocuments": "knowledgeNodeId",
}
ENTITY_LABELS = {
    "knowledgeNodes": "KnowledgeNode",
    "knowledgeRelations": "KnowledgeRelation",
    "knowledgeAssets": "KnowledgeAsset",
    "searchDocuments": "SearchDocument",
}


@dataclass(frozen=True)
class PackageIssue:
    path: Path
    message: str


@dataclass(frozen=True)
class PackageBuildResult:
    output_dir: Path
    content_version: str
    package_hash: str
    package_size: int
    counts: Mapping[str, int]
    errors: tuple[PackageIssue, ...]
    warnings: tuple[PackageIssue, ...]


@dataclass(frozen=True)
class DiffEntry:
    entity_type: str
    operation: str
    entity_id: str


@dataclass(frozen=True)
class PackageDiff:
    entries: tuple[DiffEntry, ...]
    errors: tuple[PackageIssue, ...]

    def count(self, entity_type: str, operation: str) -> int:
        return sum(
            entry.entity_type == entity_type and entry.operation == operation
            for entry in self.entries
        )


def _json_value(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        value = asdict(value)
    if isinstance(value, dict):
        return {
            key: _json_value(item)
            for key, item in value.items()
            if item is not None
        }
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _json_value(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source_file:
        for chunk in iter(lambda: source_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, value: Any) -> None:
    text = json.dumps(
        _json_value(value),
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
        allow_nan=False,
    )
    path.write_bytes((text + "\n").encode("utf-8"))


def _runtime_entities(result: RuntimeMappingResult) -> dict[str, list[dict[str, Any]]]:
    return {
        "knowledgeNodes": [_json_value(item) for item in result.knowledge_nodes],
        "knowledgeRelations": [_json_value(item) for item in result.relations],
        "knowledgeAssets": [_json_value(item) for item in result.assets],
        "searchDocuments": [_json_value(item) for item in result.search_documents],
    }


def _entity_hashes(entities: Mapping[str, list[dict[str, Any]]]) -> dict[str, dict[str, str]]:
    hashes: dict[str, dict[str, str]] = {}
    for entity_group, records in entities.items():
        id_field = ENTITY_ID_FIELDS[entity_group]
        hashes[entity_group] = {
            str(record[id_field]): _sha256_bytes(_canonical_bytes(record))
            for record in records
        }
    return hashes


def _source_index(scan_result: ScanResult) -> dict[str, Path]:
    sources: dict[str, Path] = {}
    for module in scan_result.modules:
        for source in module.sources:
            data = json.loads(source.meta_json_path.read_text(encoding="utf-8"))
            source_id = data.get("id")
            if isinstance(source_id, str):
                sources[source_id] = source.conclusion_path
    return sources


def _resource_path(package_root: Path, uri: str) -> Path:
    logical_path = PurePosixPath(uri)
    if logical_path.is_absolute() or ".." in logical_path.parts:
        raise ValueError(f"asset URI is not a safe logical path: {uri}")
    return package_root.joinpath(*logical_path.parts)


def _copy_assets(
    package_root: Path,
    assets: Iterable[dict[str, Any]],
    source_index: Mapping[str, Path],
) -> dict[str, str]:
    asset_hashes: dict[str, str] = {}
    for asset in assets:
        asset_id = str(asset["id"])
        knowledge_id = str(asset["knowledgeId"])
        asset_type = str(asset["type"])
        uri = str(asset["uri"])
        source_root = source_index.get(knowledge_id)
        if source_root is None:
            raise ValueError(f"asset {asset_id} has no source directory")
        source_directory = "images" if asset_type == "image" else "pdfs"
        expected_prefix = PurePosixPath("resources", source_directory, knowledge_id)
        logical_path = PurePosixPath(uri)
        if logical_path.parent != expected_prefix:
            raise ValueError(f"asset {asset_id} URI does not match its identity: {uri}")
        source_path = source_root / source_directory / logical_path.name
        if not source_path.is_file():
            raise ValueError(f"asset source file is missing: {source_path}")
        destination = _resource_path(package_root, uri)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, destination)
        asset_hashes[asset_id] = _sha256_file(destination)
    return asset_hashes


def _package_hash(
    entity_hashes: Mapping[str, Mapping[str, str]],
    asset_hashes: Mapping[str, str],
) -> str:
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "entityHashes": entity_hashes,
        "assetHashes": asset_hashes,
    }
    return _sha256_bytes(_canonical_bytes(payload))


def _package_size(root: Path) -> int:
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def validate_package(package_root: Path) -> tuple[PackageIssue, ...]:
    errors: list[PackageIssue] = []
    manifest_path = package_root / "manifest.json"
    if not manifest_path.is_file():
        return (PackageIssue(Path("manifest.json"), "manifest file is missing"),)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return (PackageIssue(Path("manifest.json"), f"manifest is invalid JSON: {exc}"),)
    if not isinstance(manifest, dict):
        return (PackageIssue(Path("manifest.json"), "manifest root must be an object"),)

    entities: dict[str, list[dict[str, Any]]] = {}
    for group, default_name in JSON_FILES.items():
        relative_name = (manifest.get("files") or {}).get(group, default_name)
        path = package_root / relative_name
        if not path.is_file():
            errors.append(PackageIssue(Path(relative_name), "package JSON file is missing"))
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(PackageIssue(Path(relative_name), f"invalid JSON: {exc}"))
            continue
        if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
            errors.append(PackageIssue(Path(relative_name), "file must contain an array of objects"))
            continue
        entities[group] = value

    if len(entities) != len(JSON_FILES):
        return tuple(errors)

    entity_hashes = _entity_hashes(entities)
    manifest_entity_hashes = manifest.get("entityHashes")
    if manifest_entity_hashes != entity_hashes:
        errors.append(PackageIssue(Path("manifest.json"), "entity hashes do not match package JSON"))

    ids_by_group: dict[str, set[str]] = {}
    for group, records in entities.items():
        id_field = ENTITY_ID_FIELDS[group]
        ids = [str(record.get(id_field, "")) for record in records]
        ids_by_group[group] = set(ids)
        if len(ids) != len(set(ids)):
            errors.append(PackageIssue(Path(JSON_FILES[group]), "entity IDs are not unique"))

    nodes = entities["knowledgeNodes"]
    node_ids = ids_by_group["knowledgeNodes"]
    roots = [node for node in nodes if node.get("type") == "root"]
    if len(roots) != 1:
        errors.append(PackageIssue(Path(JSON_FILES["knowledgeNodes"]), f"expected one root node, found {len(roots)}"))
    for node in nodes:
        if node.get("type") != "root" and node.get("parentId") not in node_ids:
            errors.append(PackageIssue(Path(JSON_FILES["knowledgeNodes"]), f"node {node.get('id')} has unknown parentId"))

    for relation in entities["knowledgeRelations"]:
        if relation.get("sourceId") not in node_ids or relation.get("targetId") not in node_ids:
            errors.append(PackageIssue(Path(JSON_FILES["knowledgeRelations"]), f"relation {relation.get('id')} has an unknown endpoint"))

    expected_resources: set[str] = set()
    calculated_asset_hashes: dict[str, str] = {}
    for asset in entities["knowledgeAssets"]:
        asset_id = str(asset.get("id", ""))
        if asset.get("knowledgeId") not in node_ids:
            errors.append(PackageIssue(Path(JSON_FILES["knowledgeAssets"]), f"asset {asset_id} has unknown knowledgeId"))
        uri = asset.get("uri")
        if not isinstance(uri, str):
            errors.append(PackageIssue(Path(JSON_FILES["knowledgeAssets"]), f"asset {asset_id} has invalid URI"))
            continue
        try:
            resource_path = _resource_path(package_root, uri)
        except ValueError as exc:
            errors.append(PackageIssue(Path(JSON_FILES["knowledgeAssets"]), str(exc)))
            continue
        expected_resources.add(PurePosixPath(uri).as_posix())
        if not resource_path.is_file():
            errors.append(PackageIssue(Path(uri), f"asset resource is missing for {asset_id}"))
            continue
        calculated_asset_hashes[asset_id] = _sha256_file(resource_path)

    manifest_asset_hashes = manifest.get("assetHashes")
    if manifest_asset_hashes != calculated_asset_hashes:
        errors.append(PackageIssue(Path("manifest.json"), "asset hashes do not match resource contents"))

    resources_root = package_root / "resources"
    actual_resources = {
        path.relative_to(package_root).as_posix()
        for path in resources_root.rglob("*")
        if path.is_file()
    } if resources_root.is_dir() else set()
    if actual_resources != expected_resources:
        errors.append(PackageIssue(Path("resources"), "resource files do not exactly match KnowledgeAsset URIs"))

    for document in entities["searchDocuments"]:
        if document.get("knowledgeNodeId") not in node_ids:
            errors.append(PackageIssue(Path(JSON_FILES["searchDocuments"]), f"search document {document.get('knowledgeNodeId')} has unknown knowledgeNodeId"))

    expected_counts = {
        "knowledgeNodes": len(entities["knowledgeNodes"]),
        "knowledgeRelations": len(entities["knowledgeRelations"]),
        "knowledgeAssets": len(entities["knowledgeAssets"]),
        "searchDocuments": len(entities["searchDocuments"]),
        "imageAssets": sum(asset.get("type") == "image" for asset in entities["knowledgeAssets"]),
        "pdfAssets": sum(asset.get("type") == "pdf" for asset in entities["knowledgeAssets"]),
    }
    if manifest.get("counts") != expected_counts:
        errors.append(PackageIssue(Path("manifest.json"), "manifest counts do not match package data"))

    file_hashes = {
        group: _sha256_file(package_root / JSON_FILES[group])
        for group in JSON_FILES
    }
    if manifest.get("fileHashes") != file_hashes:
        errors.append(PackageIssue(Path("manifest.json"), "file hashes do not match package JSON files"))

    calculated_package_hash = _package_hash(entity_hashes, calculated_asset_hashes)
    if manifest.get("packageHash") != calculated_package_hash:
        errors.append(PackageIssue(Path("manifest.json"), "packageHash is invalid"))
    if manifest.get("contentVersion") != f"sha256:{calculated_package_hash}":
        errors.append(PackageIssue(Path("manifest.json"), "contentVersion is invalid"))
    if manifest.get("schemaVersion") != SCHEMA_VERSION:
        errors.append(PackageIssue(Path("manifest.json"), "schemaVersion is unsupported"))
    return tuple(errors)


def _safe_replace_directory(staged: Path, output_dir: Path) -> None:
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    if output_dir.exists() and not output_dir.is_dir():
        raise ValueError(f"package output exists and is not a directory: {output_dir}")
    backup: Path | None = None
    if output_dir.exists():
        backup = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.old-", dir=output_dir.parent))
        backup.rmdir()
        os.replace(output_dir, backup)
    try:
        os.replace(staged, output_dir)
    except BaseException:
        if backup is not None and backup.exists() and not output_dir.exists():
            os.replace(backup, output_dir)
        raise
    if backup is not None and backup.exists():
        shutil.rmtree(backup)


def build_package(
    scan_result: ScanResult,
    runtime_result: RuntimeMappingResult,
    output_dir: Path,
) -> PackageBuildResult:
    """Build and validate a complete package before replacing the output."""

    output_dir = output_dir.resolve()
    if output_dir == Path(output_dir.anchor):
        raise ValueError("refusing to use a filesystem root as package output")
    if runtime_result.errors:
        issues = tuple(
            PackageIssue(issue.path, f"runtime mapping failed: {issue.message}")
            for issue in runtime_result.errors
        )
        return PackageBuildResult(output_dir, "", "", 0, {}, issues, ())

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.tmp-", dir=output_dir.parent))
    try:
        entities = _runtime_entities(runtime_result)
        for group, file_name in JSON_FILES.items():
            _write_json(staged / file_name, entities[group])

        (staged / "resources" / "images").mkdir(parents=True)
        (staged / "resources" / "pdfs").mkdir(parents=True)
        source_index = _source_index(scan_result)
        asset_hashes = _copy_assets(staged, entities["knowledgeAssets"], source_index)
        entity_hashes = _entity_hashes(entities)
        package_hash = _package_hash(entity_hashes, asset_hashes)
        content_version = f"sha256:{package_hash}"
        counts = {
            "knowledgeNodes": len(entities["knowledgeNodes"]),
            "knowledgeRelations": len(entities["knowledgeRelations"]),
            "knowledgeAssets": len(entities["knowledgeAssets"]),
            "searchDocuments": len(entities["searchDocuments"]),
            "imageAssets": runtime_result.asset_count("image"),
            "pdfAssets": runtime_result.asset_count("pdf"),
        }
        file_hashes = {
            group: _sha256_file(staged / file_name)
            for group, file_name in JSON_FILES.items()
        }
        manifest = {
            "schemaVersion": SCHEMA_VERSION,
            "contentVersion": content_version,
            "counts": counts,
            "files": JSON_FILES,
            "fileHashes": file_hashes,
            "entityHashes": entity_hashes,
            "assetHashes": asset_hashes,
            "packageHash": package_hash,
        }
        _write_json(staged / "manifest.json", manifest)
        validation_errors = validate_package(staged)
        if validation_errors:
            return PackageBuildResult(
                output_dir, content_version, package_hash, 0, counts, validation_errors, ()
            )
        package_size = _package_size(staged)
        _safe_replace_directory(staged, output_dir)
        return PackageBuildResult(
            output_dir, content_version, package_hash, package_size, counts, (), ()
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return PackageBuildResult(
            output_dir,
            "",
            "",
            0,
            {},
            (PackageIssue(Path("package"), str(exc)),),
            (),
        )
    finally:
        if staged.exists():
            shutil.rmtree(staged)


def _load_manifest(package_dir: Path) -> tuple[dict[str, Any] | None, tuple[PackageIssue, ...]]:
    validation_errors = validate_package(package_dir)
    if validation_errors:
        return None, validation_errors
    manifest = json.loads((package_dir / "manifest.json").read_text(encoding="utf-8"))
    return manifest, ()


def diff_packages(previous_dir: Path, current_dir: Path) -> PackageDiff:
    previous, previous_errors = _load_manifest(previous_dir)
    current, current_errors = _load_manifest(current_dir)
    errors = tuple(
        [PackageIssue(Path("previous") / issue.path, issue.message) for issue in previous_errors]
        + [PackageIssue(Path("current") / issue.path, issue.message) for issue in current_errors]
    )
    if errors or previous is None or current is None:
        return PackageDiff((), errors)

    entries: list[DiffEntry] = []
    previous_hashes = previous["entityHashes"]
    current_hashes = current["entityHashes"]
    for group in JSON_FILES:
        previous_group = dict(previous_hashes[group])
        current_group = dict(current_hashes[group])
        if group == "knowledgeAssets":
            previous_assets = previous.get("assetHashes", {})
            current_assets = current.get("assetHashes", {})
            previous_group = {
                entity_id: _sha256_bytes(
                    _canonical_bytes((entity_hash, previous_assets.get(entity_id)))
                )
                for entity_id, entity_hash in previous_group.items()
            }
            current_group = {
                entity_id: _sha256_bytes(
                    _canonical_bytes((entity_hash, current_assets.get(entity_id)))
                )
                for entity_id, entity_hash in current_group.items()
            }

        previous_ids = set(previous_group)
        current_ids = set(current_group)
        label = ENTITY_LABELS[group]
        entries.extend(DiffEntry(label, "ADD", entity_id) for entity_id in sorted(current_ids - previous_ids))
        entries.extend(
            DiffEntry(label, "UPDATE", entity_id)
            for entity_id in sorted(previous_ids & current_ids)
            if previous_group[entity_id] != current_group[entity_id]
        )
        entries.extend(DiffEntry(label, "DELETE", entity_id) for entity_id in sorted(previous_ids - current_ids))
    return PackageDiff(tuple(entries), ())

