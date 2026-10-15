"""Independent module envelopes over an immutable, validated Full v2 snapshot.

Schema 4 preserves the 17A-F candidate DTO/layout, but separates content identity
from source/release identity. See reports/TASK_17B_M_MODULE_CONTRACT.md.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
import unicodedata
import zipfile
import uuid
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any

from PIL import Image

if __package__:
    from . import content_package as full
else:
    import content_package as full

SCHEMA_VERSION = 4
FILES = {**full.JSON_FILES, full.SHARE_KEY: full.SHARE_FILE,
         "externalRelations": "external-relations.json"}
ID_FIELDS = {**full.ENTITY_ID_FIELDS, "externalRelations": "id"}
# Explicit 17A-F registry, checked against the actual chapter and parent chain.
MODULES = {
    "sets": ("zhishu.math.set", "math.set", "struct:集合", "集合"),
    "analytic-geometry": ("zhishu.math.analytic-geometry", "math.analytic-geometry",
                          "struct:解析几何", "解析几何"),
}
ROOT = "root-high-school-math"
BASE_CAPABILITIES = {"package-schema-v4", "persistent-content-uri-v1",
                     "shared-entity-ownership-v1"}
EXT_FIELDS = {"externalEndpointId", "targetPackageId", "resolutionPolicy"}
MANIFEST_FIELDS = {
    "schemaVersion", "packageId", "subjectId", "moduleId", "packageKind",
    "packageVersion", "rootNodeId", "moduleRootNodeId", "minAppContentApi",
    "requiredCapabilities", "dependencies", "sourcePackage", "files", "counts",
    "fileHashes", "entityHashes", "assetHashes", "shareAssetHashes", "resources",
    "packageHash", "contentVersion",
}
# Host validator limits, not an assertion about Android capacity.
MAX_FILES = 20000
MAX_FILE_BYTES = 512 * 1024 * 1024
MAX_TOTAL_BYTES = 2 * 1024 * 1024 * 1024
MAX_JSON_BYTES = 32 * 1024 * 1024
MAX_DEPTH = 16
SHA = re.compile(r"[0-9a-f]{64}\Z")
PACKAGE_ID = re.compile(r"[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*\Z")
DEVICE = re.compile(r"(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?\Z", re.I)
MIMES = {".webp": "image/webp", ".gif": "image/gif", ".png": "image/png",
         ".pdf": "application/pdf", ".mp4": "video/mp4"}


class ModuleError(ValueError):
    """Invalid input, unsafe path or inconsistent module data."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ModuleError(message)


def digest(value: Any) -> str:
    return hashlib.sha256(full._canonical_bytes(value)).hexdigest()


@contextmanager
def temporary_directory(parent: Path | None = None, prefix: str = "mathnote-module-"):
    # Python 3.14's Windows mkdir(0700), used by tempfile.mkdtemp, creates a
    # protected ACL that this workspace's sandbox token cannot reopen. Normal
    # mkdir inherits the parent's ACL; no ACL is edited or broadened here.
    parent = (parent or Path(tempfile.gettempdir())).resolve()
    _no_links(parent)
    root = parent / (prefix + uuid.uuid4().hex)
    root.mkdir(mode=0o777)
    try:
        yield root
    finally:
        if root.exists():
            require(root.resolve().parent == parent, "unsafe temporary cleanup")
            shutil.rmtree(root)


def replace_output(staged: Path, output: Path) -> None:
    backup = output.parent / ("." + output.name + ".old-" + uuid.uuid4().hex)
    require(staged.resolve().parent == output.parent.resolve(), "staging/output filesystem mismatch")
    require(backup.resolve().parent == output.parent.resolve(), "unsafe output backup")
    existed = output.exists()
    if existed:
        os.replace(output, backup)
    try:
        os.replace(staged, output)
    except BaseException:
        if existed:
            os.replace(backup, output)
        raise
    if existed:
        shutil.rmtree(backup)


def write_json(path: Path, value: Any) -> None:
    # Keep explicit null external package hints; canonical hashing still uses
    # the inherited Python clean(None) rule from 17A-F / Full v2.
    path.write_bytes((json.dumps(value, ensure_ascii=False, sort_keys=True,
                                 indent=2, allow_nan=False) + "\n").encode("utf-8"))


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _numbers_and_unicode(value: Any) -> None:
    if isinstance(value, str):
        value.encode("utf-8", errors="strict")
    elif type(value) is int:
        require(abs(value) <= 2**53 - 1, "integer exceeds JS safe range")
    elif isinstance(value, dict):
        for key, item in value.items():
            _numbers_and_unicode(key)
            _numbers_and_unicode(item)
    elif isinstance(value, list):
        for item in value:
            _numbers_and_unicode(item)


def read_json(path: Path) -> Any:
    require(path.stat().st_size <= MAX_JSON_BYTES, f"JSON size limit: {path.name}")
    def invalid(value: str) -> None:
        raise ModuleError(f"non-finite JSON number: {value}")
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_object,
                       parse_constant=invalid)
    _numbers_and_unicode(value)
    # Also catches float overflow such as 1e999.
    full._canonical_bytes(value)
    return value


def safe_name(name: str) -> str:
    require(isinstance(name, str) and bool(name), "empty/non-string path")
    require(not any(ord(c) < 32 or ord(c) == 127 or c in '\\:%?#<>"|*?' for c in name),
            f"unsafe path: {name!r}")
    parts = name.split("/")
    require(len(parts) <= MAX_DEPTH, f"path depth limit: {name}")
    require(all(p and p not in {".", ".."} and not p.endswith((" ", "."))
                and not DEVICE.fullmatch(p) for p in parts), f"unsafe path: {name}")
    return name


def _no_links(path: Path) -> None:
    for item in (path, *path.parents):
        require(not item.is_symlink() and not item.is_junction(), f"link path: {item}")


def inventory(root: Path) -> dict[str, Path]:
    _no_links(root)
    require(root.is_dir(), f"package directory missing: {root}")
    result: dict[str, Path] = {}
    aliases: set[str] = set()
    total = 0
    for path in root.rglob("*"):
        require(not path.is_symlink() and not path.is_junction(), f"link entry: {path}")
        name = safe_name(path.relative_to(root).as_posix())
        alias = unicodedata.normalize("NFC", name).casefold()
        require(alias not in aliases, f"path collision: {name}")
        aliases.add(alias)
        if path.is_dir():
            continue
        info = path.stat()
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, f"non-regular/link file: {name}")
        require(info.st_size <= MAX_FILE_BYTES, f"file size limit: {name}")
        result[name] = path
        total += info.st_size
        require(len(result) <= MAX_FILES and total <= MAX_TOTAL_BYTES, "package size/count limit")
    return result


def tree(nodes: list[dict[str, Any]], module_root: str | None = None) -> set[str]:
    by_id = {row["id"]: row for row in nodes}
    require(len(by_id) == len(nodes), "knowledgeNodes duplicate ID")
    roots = [row for row in nodes if row["type"] == "root"]
    require(len(roots) == 1 and roots[0]["id"] == ROOT and not roots[0].get("parentId"),
            "expected one original subject root")
    for row in nodes:
        require(row["type"] in {"root", "chapter", "section", "knowledge"}, "invalid node type")
        require(type(row["sortOrder"]) is int, "invalid node sortOrder")
        seen: set[str] = set()
        current = row
        while current["id"] != ROOT:
            require(current["id"] not in seen, f"tree cycle at {row['id']}")
            seen.add(current["id"])
            parent = current.get("parentId")
            require(parent in by_id, f"unknown parentId for {current['id']}: {parent}")
            current = by_id[parent]
            require(current["type"] != "knowledge", "knowledge node cannot be a parent")
    if module_root:
        require(module_root in by_id and by_id[module_root]["type"] == "chapter"
                and by_id[module_root].get("parentId") == ROOT, "module root is not a subject chapter")
        require({row["id"] for row in nodes if row["type"] == "chapter"} == {module_root},
                "other module chapter included")
    return {row["id"] for row in nodes if row["type"] == "knowledge"}


def load_full(root: Path) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]]]:
    """Call the unchanged Full validator before selecting any module records."""
    actual = inventory(root)
    manifest = read_json(root / "manifest.json")
    require(isinstance(manifest, dict) and type(manifest.get("schemaVersion")) is int
            and manifest["schemaVersion"] == 2, "input must be a Full v2 package")
    expected_files = {**full.JSON_FILES, full.SHARE_KEY: full.SHARE_FILE}
    require(manifest.get("files") == expected_files, "Full v2 files layout mismatch")
    data = {key: read_json(root / name) for key, name in expected_files.items()}
    issues = full.validate_package(root)
    require(not issues, "Full v2 validation failed: " + "; ".join(x.message for x in issues))
    tree(data["knowledgeNodes"])
    resources = {row["uri"] for row in data["knowledgeAssets"] + data["animationShares"]}
    require(set(actual) == {"manifest.json", *expected_files.values(), *resources},
            "Full v2 contains undeclared/missing files")
    return manifest, data


def select(data: dict[str, list[dict[str, Any]]], slug: str) -> dict[str, list[dict[str, Any]]]:
    require(slug in MODULES, f"unregistered module: {slug}")
    _, _, root_id, title = MODULES[slug]
    nodes = data["knowledgeNodes"]
    by_id = {row["id"]: row for row in nodes}
    require(root_id in by_id and by_id[root_id]["title"] == title
            and by_id[root_id]["type"] == "chapter" and by_id[root_id].get("parentId") == ROOT,
            f"registered chapter does not match actual tree: {root_id}")
    selected = {root_id}
    while True:
        more = {row["id"] for row in nodes if row.get("parentId") in selected}
        if more <= selected:
            break
        selected.update(more)
    selected.add(ROOT)
    knowledge = {row["id"] for row in nodes if row["id"] in selected and row["type"] == "knowledge"}
    result = {
        "knowledgeNodes": [row for row in nodes if row["id"] in selected],
        "knowledgeRelations": [],
        "externalRelations": [],
        "knowledgeAssets": [row for row in data["knowledgeAssets"] if row["knowledgeId"] in knowledge],
        "searchDocuments": [row for row in data["searchDocuments"] if row["knowledgeNodeId"] in knowledge],
        "animationShares": [row for row in data["animationShares"] if row["knowledgeId"] in knowledge],
    }
    for row in data["knowledgeRelations"]:
        endpoints = {row["sourceId"], row["targetId"]}
        local = endpoints & knowledge
        if len(local) == 2:
            result["knowledgeRelations"].append(row)
        elif len(local) == 1:
            result["externalRelations"].append({
                **row, "externalEndpointId": next(iter(endpoints - knowledge)),
                "targetPackageId": None, "resolutionPolicy": "resolve-when-installed",
            })
    result["externalRelations"].sort(key=lambda r: (r["sourceId"], r["type"], r["targetId"]))
    return result


def hashes(manifest: dict[str, Any]) -> tuple[str, str]:
    payload = {k: v for k, v in manifest.items() if k not in {"packageHash", "contentVersion"}}
    package_hash = digest(payload)
    # Release ordinal and full-source provenance do not describe local content.
    content = {k: v for k, v in payload.items() if k not in {"sourcePackage", "packageVersion"}}
    return package_hash, "sha256:" + digest(content)


def make_manifest(root: Path, data: dict[str, list[dict[str, Any]]], slug: str,
                  source_version: str, package_version: int) -> dict[str, Any]:
    require(type(package_version) is int and 0 < package_version <= 2**53 - 1, "invalid packageVersion")
    package_id, module_id, module_root, _ = MODULES[slug]
    resources: dict[str, Any] = {}
    asset_hashes: dict[str, str] = {}
    share_hashes: dict[str, str] = {}
    for group, id_field, target in (("knowledgeAssets", "id", asset_hashes),
                                     ("animationShares", "shareAssetId", share_hashes)):
        for row in data[group]:
            uri = safe_name(row["uri"])
            path = root / uri
            file_hash = full._sha256_file(path)
            target[row[id_field]] = file_hash
            require(uri not in resources, f"duplicate resource URI: {uri}")
            resources[uri] = {"assetId": row[id_field],
                              "kind": row["type"] if group == "knowledgeAssets" else "share-video",
                              "mimeType": MIMES.get(path.suffix.lower()),
                              "bytes": path.stat().st_size, "sha256": file_hash}
    capabilities = set(BASE_CAPABILITIES)
    if data["externalRelations"]:
        capabilities.add("external-related-v1")
    if data["animationShares"]:
        capabilities.add("animation-share-mp4-v1")
    counts = {key: len(rows) for key, rows in data.items()}
    counts.update(imageAssets=sum(r["type"] == "image" for r in data["knowledgeAssets"]),
                  pdfAssets=sum(r["type"] == "pdf" for r in data["knowledgeAssets"]),
                  videoAssets=len(data["animationShares"]))
    manifest = {
        "schemaVersion": SCHEMA_VERSION, "packageId": package_id, "subjectId": "math.high-school",
        "moduleId": module_id, "packageKind": "module", "packageVersion": package_version,
        "rootNodeId": ROOT, "moduleRootNodeId": module_root, "minAppContentApi": 1,
        "requiredCapabilities": sorted(capabilities), "dependencies": [],
        "sourcePackage": {"schemaVersion": 2, "contentVersion": source_version},
        "files": FILES, "counts": counts,
        "fileHashes": {key: full._sha256_file(root / name) for key, name in FILES.items()},
        "entityHashes": {key: {row[ID_FIELDS[key]]: digest(row) for row in rows}
                         for key, rows in data.items()},
        "assetHashes": asset_hashes, "shareAssetHashes": share_hashes, "resources": resources,
    }
    manifest["packageHash"], manifest["contentVersion"] = hashes(manifest)
    return manifest


def _validate_directory(root: Path, source: tuple[dict[str, Any], dict[str, Any]] | None = None) -> dict[str, Any]:
    actual = inventory(root)
    m = read_json(root / "manifest.json")
    require(isinstance(m, dict) and set(m) == MANIFEST_FIELDS, "Manifest missing/unknown fields")
    require(type(m["schemaVersion"]) is int and m["schemaVersion"] == SCHEMA_VERSION,
            "unsupported module schemaVersion (expected 4)")
    require(m["packageKind"] == "module" and m["subjectId"] == "math.high-school", "invalid package type/subject")
    slug = next((slug for slug, row in MODULES.items() if row[0] == m["packageId"]), None)
    require(slug is not None, "illegal/unregistered packageId")
    require(PACKAGE_ID.fullmatch(m["packageId"]) is not None and len(m["packageId"]) <= 128, "invalid packageId")
    reg = MODULES[slug]
    require((m["moduleId"], m["moduleRootNodeId"], m["rootNodeId"]) == (reg[1], reg[2], ROOT),
            "module identity/root mismatch")
    require(type(m["packageVersion"]) is int and 0 < m["packageVersion"] <= 2**53 - 1, "invalid packageVersion")
    require(type(m["minAppContentApi"]) is int and m["minAppContentApi"] == 1 and m["dependencies"] == [],
            "unsupported API/dependencies profile")
    require(m["files"] == FILES, "module files layout mismatch")
    require(isinstance(m["counts"], dict) and all(type(v) is int and 0 <= v <= 2**53 - 1
                                                for v in m["counts"].values()), "invalid counts integer")
    require(isinstance(m["resources"], dict), "resources must be an object")
    for uri, entry in m["resources"].items():
        safe_name(uri)
        require(isinstance(entry, dict) and type(entry.get("bytes")) is int
                and 0 < entry["bytes"] <= MAX_FILE_BYTES, "invalid resource bytes integer")
    src = m["sourcePackage"]
    require(isinstance(src, dict) and set(src) == {"schemaVersion", "contentVersion"}
            and type(src["schemaVersion"]) is int and src["schemaVersion"] == 2
            and isinstance(src["contentVersion"], str) and src["contentVersion"].startswith("sha256:")
            and SHA.fullmatch(src["contentVersion"][7:]) is not None, "invalid sourcePackage")
    data = {key: read_json(root / name) for key, name in FILES.items()}
    for key, rows in data.items():
        require(isinstance(rows, list) and all(isinstance(row, dict) for row in rows), f"{key}: expected object array")
        ids = [row.get(ID_FIELDS[key]) for row in rows]
        require(all(isinstance(x, str) and x for x in ids), f"{key}: missing/invalid entity ID")
        require(len(ids) == len(set(ids)), f"{key}: duplicate ID")
    shapes = full._validate_entity_shapes({k: v for k, v in data.items() if k != "externalRelations"}, FILES)
    require(not shapes, "; ".join(x.message for x in shapes))
    knowledge = tree(data["knowledgeNodes"], reg[2])
    require(next(row for row in data["knowledgeNodes"] if row["id"] == reg[2])["title"] == reg[3],
            "registered module title mismatch")
    require({r["knowledgeNodeId"] for r in data["searchDocuments"]} == knowledge, "SearchDocuments coverage mismatch")
    relation_ids: set[str] = set()
    for group in ("knowledgeRelations", "externalRelations"):
        for row in data[group]:
            a, b, kind = row.get("sourceId"), row.get("targetId"), row.get("type")
            require(isinstance(a, str) and isinstance(b, str) and a.isascii() and b.isascii()
                    and a < b and kind == "related" and row["id"] == f"{a}:related:{b}",
                    f"noncanonical related relation: {row['id']}")
            require(row["id"] not in relation_ids, "relation registered internally and externally")
            relation_ids.add(row["id"])
            missing = {a, b} - knowledge
            if group == "knowledgeRelations":
                require(not missing and not (EXT_FIELDS & row.keys()), f"internal relation unknown endpoint: {row['id']}")
            else:
                require(EXT_FIELDS <= row.keys() and len(missing) == 1
                        and row.get("externalEndpointId") == next(iter(missing))
                        and row.get("resolutionPolicy") == "resolve-when-installed"
                        and row.get("targetPackageId") in {None, *(r[0] for r in MODULES.values())},
                        f"invalid external relation: {row['id']}")
    resource_uris: set[str] = set()
    for row in data["knowledgeAssets"]:
        kind, uri = row["type"], safe_name(row["uri"])
        p = PurePosixPath(uri)
        require(kind in {"image", "pdf"} and row["knowledgeId"] in knowledge, "invalid asset owner/type")
        require(len(p.parts) == 4 and p.parts[:3] == ("resources", "images" if kind == "image" else "pdfs", row["knowledgeId"])
                and p.suffix in ({".png", ".webp", ".gif"} if kind == "image" else {".pdf"})
                and row["id"] == f"{row['knowledgeId']}:{kind}:{p.name}", f"invalid asset identity/URI: {row['id']}")
        require(uri not in resource_uris, f"duplicate resource URI: {uri}")
        resource_uris.add(uri)
    for row in data["animationShares"]:
        uri = safe_name(row["uri"])
        require(uri not in resource_uris, f"duplicate video URI: {uri}")
        resource_uris.add(uri)
    require(set(actual) == {"manifest.json", *FILES.values(), *resource_uris}, "missing/extra package files")
    issues, _, _ = full._validate_share_records(root, data["animationShares"], data["knowledgeAssets"], knowledge)
    require(not issues, "; ".join(x.message for x in issues))
    for row in data["knowledgeAssets"]:
        path = root / row["uri"]
        if row["type"] == "image":
            with Image.open(path) as img:
                require(img.format == {".webp": "WEBP", ".gif": "GIF", ".png": "PNG"}[path.suffix], "image MIME/format mismatch")
                img.verify()
        else:
            with path.open("rb") as stream:
                require(stream.read(5) == b"%PDF-", "PDF MIME/format mismatch")
    expected = make_manifest(root, data, slug, src["contentVersion"], m["packageVersion"])
    require(m == expected, "Manifest counts, capabilities, metadata or integrity hash mismatch")
    if source is not None:
        source_manifest, source_data = source
        require(src["contentVersion"] == source_manifest["contentVersion"], "sourcePackage version mismatch")
        projected = select(source_data, slug)
        for key in FILES:
            require(data[key] == projected[key], f"Full v2 consistency mismatch: {key} (IDs, records, order or relations)")
        for key in ("assetHashes", "shareAssetHashes"):
            require(all(source_manifest[key].get(k) == v for k, v in m[key].items()), f"Full v2 resource byte/hash mismatch: {key}")
    return m


def _extract(zip_path: Path, root: Path) -> None:
    _no_links(zip_path)
    with zipfile.ZipFile(zip_path) as archive:
        infos = archive.infolist()
        require(len(infos) <= MAX_FILES, "ZIP entry count limit")
        total = 0
        seen: set[str] = set()
        names: set[str] = set()
        for info in infos:
            name = safe_name(info.filename)
            require(not info.is_dir(), "ZIP directory entries unsupported; use regular files")
            alias = unicodedata.normalize("NFC", name).casefold()
            require(alias not in seen, f"duplicate/conflicting ZIP entry: {name}")
            seen.add(alias)
            names.add(name)
            mode = info.external_attr >> 16
            require(stat.S_IFMT(mode) in (0, stat.S_IFREG) and not info.flag_bits & 1,
                    f"ZIP link/non-regular/encrypted entry: {name}")
            require(info.compress_type in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}, "unsupported ZIP compression")
            total += info.file_size
            require(info.file_size <= MAX_FILE_BYTES and total <= MAX_TOTAL_BYTES, "ZIP size limit")
            require(not name.endswith(".json") or info.file_size <= MAX_JSON_BYTES, "ZIP JSON size limit")
        require(not any("/".join(name.split("/")[:i]) in names
                        for name in names for i in range(1, len(name.split("/")))), "ZIP file/directory conflict")
        for info in infos:
            target = root / info.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            require(target.resolve().is_relative_to(root.resolve()), "ZIP path escapes extraction root")
            written = 0
            with archive.open(info) as src, target.open("xb") as dst:
                for chunk in iter(lambda: src.read(1024 * 1024), b""):
                    written += len(chunk)
                    require(written <= info.file_size, "ZIP expanded size mismatch")
                    dst.write(chunk)
            require(written == info.file_size, "ZIP size mismatch")


def validate_module(path: Path, source_root: Path | None = None) -> tuple[str, ...]:
    """Validate a directory or ZIP alone; optional source adds exhaustive provenance checks."""
    try:
        source = load_full(source_root) if source_root is not None else None
        if path.is_dir():
            _validate_directory(path, source)
        else:
            with temporary_directory() as root:
                _extract(path, root)
                _validate_directory(root, source)
        return ()
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, RecursionError, Image.DecompressionBombError,
            zipfile.BadZipFile, RuntimeError) as exc:
        return (f"{type(exc).__name__}: {exc}",)


def write_zip(root: Path, destination: Path) -> None:
    files = inventory(root)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_STORED) as archive:
        for name in sorted(files, key=lambda n: n.encode("utf-8")):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_STORED
            with archive.open(info, "w") as target, files[name].open("rb") as source:
                shutil.copyfileobj(source, target)


def slice_modules(input_root: Path, output_root: Path, modules: list[str],
                  package_version: int = 1) -> list[dict[str, Any]]:
    _no_links(input_root)
    _no_links(output_root)
    input_root, output_root = input_root.resolve(), output_root.resolve()
    project = Path(__file__).resolve().parents[2]
    require(not output_root.is_relative_to(input_root) and not input_root.is_relative_to(output_root),
            "input/output directories must be isolated (no ancestor overlap)")
    require(not project.is_relative_to(output_root), "refusing project/root output")
    require(output_root != project / "build/zhishu-content-package", "refusing formal Full output")
    require(bool(modules) and len(modules) == len(set(modules)) and all(x in MODULES for x in modules),
            "modules must be unique registered slugs: sets,analytic-geometry")
    source = load_full(input_root)
    before = {name: full._sha256_file(path) for name, path in inventory(input_root).items()}
    output_root.parent.mkdir(parents=True, exist_ok=True)
    with temporary_directory(output_root.parent, f".{output_root.name}.tmp-") as staged:
        if output_root.exists():
            require(output_root.is_dir(), "output is not a directory")
            allowed = {*MODULES, *(slug + ".zip" for slug in MODULES)}
            require(all(p.name in allowed for p in output_root.iterdir()), "output contains unrelated files")
            inventory(output_root)
            shutil.copytree(output_root, staged, dirs_exist_ok=True)
        results = []
        for slug in modules:
            data = select(source[1], slug)
            root = staged / slug
            old = read_json(root / "manifest.json") if root.exists() else None
            if root.exists():
                require(root.resolve().is_relative_to(staged.resolve()), "unsafe staged removal")
                shutil.rmtree(root)
            root.mkdir()
            for key, name in FILES.items():
                write_json(root / name, data[key])
            for row in data["knowledgeAssets"] + data["animationShares"]:
                uri = safe_name(row["uri"])
                target = root / uri
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(input_root / uri, target)
            m = make_manifest(root, data, slug, source[0]["contentVersion"], package_version)
            if old:
                require(package_version >= old["packageVersion"], "packageVersion downgrade refused")
                require(package_version != old["packageVersion"] or m["packageHash"] == old["packageHash"],
                        "VERSION_REUSE: changed envelope requires a higher --package-version")
            write_json(root / "manifest.json", m)
            _validate_directory(root, source)
            archive = staged / (slug + ".zip")
            write_zip(root, archive)
            issues = validate_module(archive)
            require(not issues, "; ".join(issues))
            results.append({"module": slug, "path": str(output_root / archive.name),
                            "bytes": archive.stat().st_size, "sha256": full._sha256_file(archive),
                            "contentVersion": m["contentVersion"], "counts": m["counts"]})
        after = {name: full._sha256_file(path) for name, path in inventory(input_root).items()}
        require(after == before, "Full v2 input changed during slicing; output not committed")
        replace_output(staged, output_root)
        return results
