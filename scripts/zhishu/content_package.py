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
    from .share_videos import ShareVideoError, load_share_videos, verify_mp4
    from .source_discovery import ScanResult
else:
    from runtime_mapping import RuntimeMappingResult
    from share_videos import ShareVideoError, load_share_videos, verify_mp4
    from source_discovery import ScanResult


SCHEMA_VERSION = 1
VIDEO_SCHEMA_VERSION = 2
SHARE_FILE = "animation-shares.json"
SHARE_KEY = "animationShares"
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
    SHARE_KEY: "displayAssetId",
}
ENTITY_LABELS = {
    "knowledgeNodes": "KnowledgeNode",
    "knowledgeRelations": "KnowledgeRelation",
    "knowledgeAssets": "KnowledgeAsset",
    "searchDocuments": "SearchDocument",
    SHARE_KEY: "AnimationShare",
}
MANIFEST_REQUIRED_FIELDS = (
    "schemaVersion",
    "contentVersion",
    "packageHash",
    "counts",
    "files",
)
ENTITY_REQUIRED_FIELDS = {
    "knowledgeNodes": ("id", "title", "sortOrder", "type"),
    "knowledgeRelations": ("id", "sourceId", "targetId", "type"),
    "knowledgeAssets": ("id", "knowledgeId", "type", "uri", "sortOrder"),
    "searchDocuments": ("knowledgeNodeId", "title"),
    SHARE_KEY: ("displayAssetId", "displayAssetUri", "shareAssetId", "knowledgeId", "uri", "mimeType", "bytes", "sha256"),
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
    if not uri or "\\" in uri or logical_path.is_absolute() or ".." in logical_path.parts:
        raise ValueError(f"asset URI is not a safe logical path: {uri}")
    return package_root.joinpath(*logical_path.parts)


def _package_file_path(package_root: Path, relative_name: str) -> Path:
    logical_path = PurePosixPath(relative_name)
    if (
        not relative_name
        or "\\" in relative_name
        or logical_path.is_absolute()
        or ".." in logical_path.parts
    ):
        raise ValueError(f"package file is not a safe logical path: {relative_name}")
    return package_root.joinpath(*logical_path.parts)


def _is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_entity_shapes(
    entities: Mapping[str, list[dict[str, Any]]],
    runtime_files: Mapping[str, str],
) -> list[PackageIssue]:
    errors: list[PackageIssue] = []
    string_fields = {
        "knowledgeNodes": ("id", "title", "type"),
        "knowledgeRelations": ("id", "sourceId", "targetId", "type"),
        "knowledgeAssets": ("id", "knowledgeId", "type", "uri"),
        "searchDocuments": ("knowledgeNodeId", "title"),
        SHARE_KEY: ("displayAssetId", "displayAssetUri", "shareAssetId", "knowledgeId", "uri", "mimeType", "sha256"),
    }
    integer_fields = {
        "knowledgeNodes": ("sortOrder",),
        "knowledgeAssets": ("sortOrder",),
        SHARE_KEY: ("bytes",),
    }
    for group, records in entities.items():
        issue_path = Path(runtime_files[group])
        for index, record in enumerate(records):
            for field in ENTITY_REQUIRED_FIELDS[group]:
                if field not in record:
                    errors.append(
                        PackageIssue(
                            issue_path,
                            f"entity {index} missing required field: {field}",
                        )
                    )
            for field in string_fields[group]:
                if field in record and (
                    not isinstance(record[field], str) or not record[field]
                ):
                    errors.append(
                        PackageIssue(
                            issue_path,
                            f"entity {index} field {field} must be a non-empty string",
                        )
                    )
            for field in integer_fields.get(group, ()):
                if field in record and not _is_integer(record[field]):
                    errors.append(
                        PackageIssue(
                            issue_path,
                            f"entity {index} field {field} must be an integer",
                        )
                    )
            if group == "knowledgeNodes" and "parentId" in record:
                parent_id = record["parentId"]
                if parent_id is not None and (
                    not isinstance(parent_id, str) or not parent_id
                ):
                    errors.append(
                        PackageIssue(
                            issue_path,
                            f"entity {index} field parentId must be null or a non-empty string",
                        )
                    )
    return errors


def _copy_assets(
    package_root: Path,
    assets: Iterable[dict[str, Any]],
    source_index: Mapping[str, Path],
    prepared_assets_root: Path,
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
        source_path = (
            prepared_assets_root / "images" / knowledge_id / logical_path.name
            if asset_type == "image"
            else source_root / source_directory / logical_path.name
        )
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
    *,
    schema_version: int = SCHEMA_VERSION,
    share_asset_hashes: Mapping[str, str] | None = None,
) -> str:
    payload = {
        "schemaVersion": schema_version,
        "entityHashes": entity_hashes,
        "assetHashes": asset_hashes,
    }
    if schema_version == VIDEO_SCHEMA_VERSION:
        payload["shareAssetHashes"] = share_asset_hashes
    return _sha256_bytes(_canonical_bytes(payload))


def _package_size(root: Path) -> int:
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def _validate_share_records(
    package_root: Path, shares: list[dict[str, Any]],
    display_assets: list[dict[str, Any]], node_ids: set[str],
) -> tuple[list[PackageIssue], dict[str, str], set[str]]:
    issues: list[PackageIssue] = []
    hashes: dict[str, str] = {}
    resources: set[str] = set()
    displays = {asset["id"]: asset for asset in display_assets}
    seen_display: set[str] = set()
    for share in shares:
        display_id = share["displayAssetId"]
        share_id = share["shareAssetId"]
        knowledge_id = share["knowledgeId"]
        uri = share["uri"]
        display = displays.get(display_id)
        if display_id in seen_display:
            issues.append(PackageIssue(Path(SHARE_FILE), f"duplicate GIF association: {display_id}"))
        seen_display.add(display_id)
        if (
            display is None or display.get("type") != "image"
            or display.get("knowledgeId") != knowledge_id
            or display.get("uri") != share["displayAssetUri"]
            or not str(share["displayAssetUri"]).lower().endswith(".gif")
        ):
            issues.append(PackageIssue(Path(SHARE_FILE), f"invalid GIF reference: {display_id}"))
        if knowledge_id not in node_ids:
            issues.append(PackageIssue(Path(SHARE_FILE), f"unknown knowledge ID: {knowledge_id}"))
        logical = PurePosixPath(uri)
        if (
            "\\" in uri or logical.is_absolute() or ".." in logical.parts
            or len(logical.parts) != 4 or logical.parts[:3] != ("resources", "videos", knowledge_id)
            or logical.suffix.lower() != ".mp4"
            or share_id != f"{knowledge_id}:share-video:{logical.name}"
            or share["mimeType"] != "video/mp4"
        ):
            issues.append(PackageIssue(Path(SHARE_FILE), f"invalid MP4 identity or type: {share_id}"))
            continue
        if uri in resources or share_id in hashes:
            issues.append(PackageIssue(Path(SHARE_FILE), f"duplicate MP4 association: {share_id}"))
        resources.add(uri)
        path = _resource_path(package_root, uri)
        if not path.is_file():
            issues.append(PackageIssue(Path(uri), f"share video resource is missing: {share_id}"))
            continue
        actual_hash = _sha256_file(path)
        hashes[share_id] = actual_hash
        if (
            share["bytes"] <= 0 or path.stat().st_size != share["bytes"]
            or share["sha256"] != actual_hash
        ):
            issues.append(PackageIssue(Path(uri), f"share video size or hash mismatch: {share_id}"))
        try:
            verify_mp4(path)
        except ShareVideoError as exc:
            issues.append(PackageIssue(Path(uri), str(exc)))
    return issues, hashes, resources


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
    schema_version = manifest.get("schemaVersion")
    video_schema = schema_version == VIDEO_SCHEMA_VERSION
    if schema_version not in (SCHEMA_VERSION, VIDEO_SCHEMA_VERSION):
        errors.append(PackageIssue(Path("manifest.json"), "schemaVersion is unsupported"))
    expected_runtime_files = dict(JSON_FILES)
    if video_schema:
        expected_runtime_files[SHARE_KEY] = SHARE_FILE

    for field in MANIFEST_REQUIRED_FIELDS:
        if field not in manifest:
            errors.append(
                PackageIssue(Path("manifest.json"), f"missing required field: {field}")
            )

    if "schemaVersion" in manifest and not _is_integer(manifest["schemaVersion"]):
        errors.append(PackageIssue(Path("manifest.json"), "schemaVersion must be an integer"))
    for field in ("contentVersion", "packageHash"):
        if field in manifest and not isinstance(manifest[field], str):
            errors.append(PackageIssue(Path("manifest.json"), f"{field} must be a string"))
    for field in ("counts", "files"):
        if field in manifest and not isinstance(manifest[field], dict):
            errors.append(PackageIssue(Path("manifest.json"), f"{field} must be an object"))

    counts = manifest.get("counts")
    if isinstance(counts, dict):
        for count_name in (*expected_runtime_files, "imageAssets", "pdfAssets", *(("videoAssets",) if video_schema else ())):
            if count_name not in counts:
                errors.append(
                    PackageIssue(Path("manifest.json"), f"counts missing required field: {count_name}")
                )
            elif not _is_integer(counts[count_name]):
                errors.append(
                    PackageIssue(Path("manifest.json"), f"counts.{count_name} must be an integer")
                )

    files = manifest.get("files")
    runtime_files: dict[str, str] = {}
    if isinstance(files, dict):
        for group in expected_runtime_files:
            relative_name = files.get(group)
            if not isinstance(relative_name, str) or not relative_name:
                errors.append(
                    PackageIssue(Path("manifest.json"), f"files.{group} must be a non-empty string path")
                )
                continue
            try:
                _package_file_path(package_root, relative_name)
            except ValueError as exc:
                errors.append(PackageIssue(Path("manifest.json"), str(exc)))
                continue
            runtime_files[group] = relative_name
        if video_schema and runtime_files.get(SHARE_KEY) != SHARE_FILE:
            errors.append(PackageIssue(Path("manifest.json"), f"files.{SHARE_KEY} must reference {SHARE_FILE}"))

    for field in ("fileHashes", "entityHashes", "assetHashes"):
        if field not in manifest:
            errors.append(PackageIssue(Path("manifest.json"), f"missing required field: {field}"))
        elif not isinstance(manifest[field], dict):
            errors.append(PackageIssue(Path("manifest.json"), f"{field} must be an object"))
    if video_schema and not isinstance(manifest.get("shareAssetHashes"), dict):
        errors.append(PackageIssue(Path("manifest.json"), "shareAssetHashes must be an object"))

    if len(runtime_files) != len(expected_runtime_files):
        return tuple(errors)

    entities: dict[str, list[dict[str, Any]]] = {}
    for group, relative_name in runtime_files.items():
        path = _package_file_path(package_root, relative_name)
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

    if len(entities) != len(expected_runtime_files):
        return tuple(errors)

    errors.extend(_validate_entity_shapes(entities, runtime_files))
    if errors:
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
            errors.append(PackageIssue(Path(runtime_files[group]), "entity IDs are not unique"))

    nodes = entities["knowledgeNodes"]
    node_ids = ids_by_group["knowledgeNodes"]
    roots = [node for node in nodes if node.get("type") == "root"]
    if len(roots) != 1:
        errors.append(PackageIssue(Path(runtime_files["knowledgeNodes"]), f"expected one root node, found {len(roots)}"))
    for node in nodes:
        if node.get("type") != "root" and node.get("parentId") not in node_ids:
            errors.append(PackageIssue(Path(runtime_files["knowledgeNodes"]), f"node {node.get('id')} has unknown parentId"))

    related_pairs: set[tuple[str, str]] = set()
    for relation in entities["knowledgeRelations"]:
        if relation.get("sourceId") not in node_ids or relation.get("targetId") not in node_ids:
            errors.append(PackageIssue(Path(runtime_files["knowledgeRelations"]), f"relation {relation.get('id')} has an unknown endpoint"))
        if relation.get("sourceId") == relation.get("targetId"):
            errors.append(PackageIssue(Path(runtime_files["knowledgeRelations"]), f"self relation is not allowed: {relation.get('id')}"))
        if relation.get("type") == "related":
            source_id = str(relation["sourceId"])
            target_id = str(relation["targetId"])
            pair = (min(source_id, target_id), max(source_id, target_id))
            if pair in related_pairs:
                errors.append(
                    PackageIssue(
                        Path(runtime_files["knowledgeRelations"]),
                        "duplicate symmetric related relation: "
                        f"{pair[0]} <-> {pair[1]}",
                    )
                )
            related_pairs.add(pair)

    expected_resources: set[str] = set()
    calculated_asset_hashes: dict[str, str] = {}
    for asset in entities["knowledgeAssets"]:
        asset_id = str(asset.get("id", ""))
        if asset.get("knowledgeId") not in node_ids:
            errors.append(PackageIssue(Path(runtime_files["knowledgeAssets"]), f"asset {asset_id} has unknown knowledgeId"))
        uri = asset.get("uri")
        if not isinstance(uri, str):
            errors.append(PackageIssue(Path(runtime_files["knowledgeAssets"]), f"asset {asset_id} has invalid URI"))
            continue
        try:
            resource_path = _resource_path(package_root, uri)
        except ValueError as exc:
            errors.append(PackageIssue(Path(runtime_files["knowledgeAssets"]), str(exc)))
            continue
        expected_resources.add(PurePosixPath(uri).as_posix())
        if not resource_path.is_file():
            errors.append(PackageIssue(Path(uri), f"asset resource is missing for {asset_id}"))
            continue
        calculated_asset_hashes[asset_id] = _sha256_file(resource_path)

    manifest_asset_hashes = manifest.get("assetHashes")
    if manifest_asset_hashes != calculated_asset_hashes:
        errors.append(PackageIssue(Path("manifest.json"), "asset hashes do not match resource contents"))

    share_hashes: dict[str, str] = {}
    if video_schema:
        for asset in entities["knowledgeAssets"]:
            asset_type = asset["type"]
            asset_uri = PurePosixPath(asset["uri"])
            expected_directory = "images" if asset_type == "image" else "pdfs"
            valid_suffix = asset_uri.suffix.lower() in ({".webp", ".gif"} if asset_type == "image" else {".pdf"})
            if (
                asset_type not in {"image", "pdf"} or "\\" in asset["uri"]
                or asset_uri.is_absolute() or ".." in asset_uri.parts
                or len(asset_uri.parts) != 4
                or asset_uri.parts[:3] != ("resources", expected_directory, asset["knowledgeId"])
                or not valid_suffix
            ):
                errors.append(PackageIssue(Path(runtime_files["knowledgeAssets"]), f"invalid v2 display asset type or URI: {asset['id']}"))
        share_issues, share_hashes, video_resources = _validate_share_records(
            package_root, entities[SHARE_KEY], entities["knowledgeAssets"], node_ids
        )
        errors.extend(share_issues)
        expected_resources.update(video_resources)
        if manifest.get("shareAssetHashes") != share_hashes:
            errors.append(PackageIssue(Path("manifest.json"), "share asset hashes do not match resource contents"))

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
            errors.append(PackageIssue(Path(runtime_files["searchDocuments"]), f"search document {document.get('knowledgeNodeId')} has unknown knowledgeNodeId"))

    expected_counts = {
        "knowledgeNodes": len(entities["knowledgeNodes"]),
        "knowledgeRelations": len(entities["knowledgeRelations"]),
        "knowledgeAssets": len(entities["knowledgeAssets"]),
        "searchDocuments": len(entities["searchDocuments"]),
        "imageAssets": sum(asset.get("type") == "image" for asset in entities["knowledgeAssets"]),
        "pdfAssets": sum(asset.get("type") == "pdf" for asset in entities["knowledgeAssets"]),
    }
    if video_schema:
        expected_counts[SHARE_KEY] = len(entities[SHARE_KEY])
        expected_counts["videoAssets"] = len(entities[SHARE_KEY])
    if counts != expected_counts:
        errors.append(PackageIssue(Path("manifest.json"), "manifest counts do not match package data"))

    file_hashes = {
        group: _sha256_file(_package_file_path(package_root, runtime_files[group]))
        for group in runtime_files
    }
    if manifest.get("fileHashes") != file_hashes:
        errors.append(PackageIssue(Path("manifest.json"), "file hashes do not match package JSON files"))

    calculated_package_hash = _package_hash(
        entity_hashes, calculated_asset_hashes,
        schema_version=schema_version if video_schema else SCHEMA_VERSION,
        share_asset_hashes=share_hashes if video_schema else None,
    )
    if manifest.get("packageHash") != calculated_package_hash:
        errors.append(PackageIssue(Path("manifest.json"), "packageHash mismatch"))
    if manifest.get("contentVersion") != f"sha256:{calculated_package_hash}":
        errors.append(PackageIssue(Path("manifest.json"), "contentVersion is invalid"))
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


def _removed_published_videos(output_dir: Path, shares: tuple[Any, ...]) -> tuple[str, ...]:
    """Reject accidental deletion of videos already present in a v2 output."""

    manifest_path = output_dir / "manifest.json"
    if not manifest_path.is_file():
        return ()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schemaVersion") != VIDEO_SCHEMA_VERSION:
        return ()
    previous_issues = validate_package(output_dir)
    if previous_issues:
        raise ValueError(f"existing v2 package is invalid: {previous_issues[0].message}")
    previous = json.loads((output_dir / SHARE_FILE).read_text(encoding="utf-8"))
    previous_ids = {row["shareAssetId"] for row in previous}
    current_ids = {share.record["shareAssetId"] for share in shares}
    return tuple(sorted(previous_ids - current_ids))


def build_package(
    scan_result: ScanResult,
    runtime_result: RuntimeMappingResult,
    output_dir: Path,
    prepared_assets_root: Path,
    *,
    schema_version: int = VIDEO_SCHEMA_VERSION,
    allow_video_removal: bool = False,
) -> PackageBuildResult:
    """Build and validate a complete package before replacing the output."""

    output_dir = output_dir.resolve()
    if output_dir == Path(output_dir.anchor):
        raise ValueError("refusing to use a filesystem root as package output")
    if schema_version not in (SCHEMA_VERSION, VIDEO_SCHEMA_VERSION):
        raise ValueError(f"unsupported package schema version: {schema_version}")
    if (
        schema_version == SCHEMA_VERSION
        and output_dir == Path(__file__).resolve().parents[2] / "build/zhishu-content-package"
    ):
        raise ValueError("legacy v1 package requires an isolated output directory")
    runtime_warnings = tuple(
        PackageIssue(issue.path, issue.message) for issue in runtime_result.warnings
    )
    if runtime_result.errors:
        issues = tuple(
            PackageIssue(issue.path, f"runtime mapping failed: {issue.message}")
            for issue in runtime_result.errors
        )
        return PackageBuildResult(output_dir, "", "", 0, {}, issues, runtime_warnings)

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.tmp-", dir=output_dir.parent))
    try:
        entities = _runtime_entities(runtime_result)
        shares = load_share_videos(scan_result, runtime_result) if schema_version == VIDEO_SCHEMA_VERSION else ()
        files = dict(JSON_FILES)
        if schema_version == VIDEO_SCHEMA_VERSION:
            entities[SHARE_KEY] = [share.record for share in shares]
            files[SHARE_KEY] = SHARE_FILE
        for group, file_name in JSON_FILES.items():
            _write_json(staged / file_name, entities[group])
        if schema_version == VIDEO_SCHEMA_VERSION:
            _write_json(staged / SHARE_FILE, entities[SHARE_KEY])

        (staged / "resources" / "images").mkdir(parents=True)
        (staged / "resources" / "pdfs").mkdir(parents=True)
        source_index = _source_index(scan_result)
        asset_hashes = _copy_assets(
            staged,
            entities["knowledgeAssets"],
            source_index,
            prepared_assets_root.resolve(),
        )
        share_hashes: dict[str, str] = {}
        for share in shares:
            destination = _resource_path(staged, share.record["uri"])
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(share.source_path, destination)
            share_hashes[share.record["shareAssetId"]] = _sha256_file(destination)
        entity_hashes = _entity_hashes(entities)
        package_hash = _package_hash(
            entity_hashes, asset_hashes, schema_version=schema_version,
            share_asset_hashes=share_hashes if schema_version == VIDEO_SCHEMA_VERSION else None,
        )
        content_version = f"sha256:{package_hash}"
        counts = {
            "knowledgeNodes": len(entities["knowledgeNodes"]),
            "knowledgeRelations": len(entities["knowledgeRelations"]),
            "knowledgeAssets": len(entities["knowledgeAssets"]),
            "searchDocuments": len(entities["searchDocuments"]),
            "imageAssets": runtime_result.asset_count("image"),
            "pdfAssets": runtime_result.asset_count("pdf"),
        }
        if schema_version == VIDEO_SCHEMA_VERSION:
            counts[SHARE_KEY] = len(shares)
            counts["videoAssets"] = len(shares)
        file_hashes = {
            group: _sha256_file(staged / file_name)
            for group, file_name in files.items()
        }
        manifest = {
            "schemaVersion": schema_version,
            "contentVersion": content_version,
            "counts": counts,
            "files": files,
            "fileHashes": file_hashes,
            "entityHashes": entity_hashes,
            "assetHashes": asset_hashes,
            "packageHash": package_hash,
        }
        if schema_version == VIDEO_SCHEMA_VERSION:
            manifest["shareAssetHashes"] = share_hashes
        _write_json(staged / "manifest.json", manifest)
        validation_errors = validate_package(staged)
        if validation_errors:
            return PackageBuildResult(
                output_dir,
                content_version,
                package_hash,
                0,
                counts,
                validation_errors,
                runtime_warnings,
            )
        if schema_version == VIDEO_SCHEMA_VERSION and not allow_video_removal:
            removed = _removed_published_videos(output_dir, shares)
            if removed:
                raise ValueError(
                    "previously published video removed without --allow-video-removal: "
                    + ", ".join(removed)
                )
        package_size = _package_size(staged)
        _safe_replace_directory(staged, output_dir)
        return PackageBuildResult(
            output_dir,
            content_version,
            package_hash,
            package_size,
            counts,
            (),
            runtime_warnings,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return PackageBuildResult(
            output_dir,
            "",
            "",
            0,
            {},
            (PackageIssue(Path("package"), str(exc)),),
            runtime_warnings,
        )
    finally:
        if staged.exists():
            shutil.rmtree(staged, ignore_errors=True)


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
    previous_shares = dict(previous_hashes.get(SHARE_KEY, {}))
    current_shares = dict(current_hashes.get(SHARE_KEY, {}))
    previous_share_assets = previous.get("shareAssetHashes", {})
    current_share_assets = current.get("shareAssetHashes", {})
    for entity_id in sorted(set(current_shares) - set(previous_shares)):
        entries.append(DiffEntry("AnimationShare", "ADD", entity_id))
    for entity_id in sorted(set(previous_shares) - set(current_shares)):
        entries.append(DiffEntry("AnimationShare", "DELETE", entity_id))
    for entity_id in sorted(set(previous_shares) & set(current_shares)):
        if (
            previous_shares[entity_id], previous_share_assets.get(entity_id)
        ) != (
            current_shares[entity_id], current_share_assets.get(entity_id)
        ):
            entries.append(DiffEntry("AnimationShare", "UPDATE", entity_id))
    return PackageDiff(tuple(entries), ())
