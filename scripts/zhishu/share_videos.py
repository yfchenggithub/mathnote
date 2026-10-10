"""Validate explicit UID video companions without altering display assets."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import subprocess
from typing import Any

if __package__:
    from .runtime_mapping import RuntimeMappingResult
    from .source_discovery import ScanResult
else:
    from runtime_mapping import RuntimeMappingResult
    from source_discovery import ScanResult


class ShareVideoError(ValueError):
    """A selected share-video source is missing or inconsistent."""


@dataclass(frozen=True)
class ShareVideo:
    record: dict[str, Any]
    source_path: Path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def _relative_source(value: Any, directory: str, suffix: str) -> Path:
    if not isinstance(value, str) or "\\" in value:
        raise ShareVideoError(f"invalid {directory} source path")
    logical = PurePosixPath(value)
    if (
        logical.is_absolute() or ".." in logical.parts or len(logical.parts) != 2
        or logical.parts[0] != directory or logical.suffix.lower() != suffix
    ):
        raise ShareVideoError(f"invalid {directory} source path: {value}")
    return Path(*logical.parts)


def verify_mp4(path: Path) -> None:
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=format_name,duration:stream=codec_name,codec_type,pix_fmt,width,height",
             "-of", "json", str(path)],
            text=True, capture_output=True, check=True,
        )
        media = json.loads(probe.stdout)
        streams = media["streams"]
        if (
            "mp4" not in media["format"]["format_name"] or len(streams) != 1
            or streams[0].get("codec_type") != "video"
            or streams[0].get("codec_name") != "h264"
            or streams[0].get("pix_fmt") != "yuv420p"
            or int(streams[0].get("width", 0)) <= 0
            or int(streams[0].get("height", 0)) <= 0
            or float(media["format"]["duration"]) <= 0
        ):
            raise ShareVideoError(f"unsupported MP4 video format: {path}")
    except (OSError, subprocess.CalledProcessError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        if isinstance(exc, ShareVideoError):
            raise
        raise ShareVideoError(f"cannot verify MP4 video: {path}: {exc}") from exc


def load_share_videos(
    scan_result: ScanResult, runtime_result: RuntimeMappingResult, uid: str
) -> tuple[ShareVideo, ...]:
    """Read only the explicitly selected UID's registered GIF/MP4 pairs."""

    sources = []
    for module in scan_result.modules:
        for source in module.sources:
            meta = json.loads(source.meta_json_path.read_text(encoding="utf-8"))
            if meta.get("id") == uid:
                sources.append(source)
    if len(sources) != 1:
        raise ShareVideoError(f"expected one source for share video UID {uid}, found {len(sources)}")
    root = sources[0].conclusion_path
    registry_path = root / "videos/share_assets.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ShareVideoError(f"cannot read share registry: {registry_path}: {exc}") from exc
    if not isinstance(registry, dict) or registry.get("schemaVersion") != 1 or registry.get("knowledgeId") != uid:
        raise ShareVideoError("share registry header mismatch")
    associations = registry.get("associations")
    if not isinstance(associations, list) or not associations:
        raise ShareVideoError("share registry needs at least one association")

    images = {asset.id: asset for asset in runtime_result.assets if asset.type == "image"}
    seen_display: set[str] = set()
    seen_share: set[str] = set()
    seen_uri: set[str] = set()
    registered_files: set[str] = set()
    result: list[ShareVideo] = []
    for link in associations:
        if not isinstance(link, dict):
            raise ShareVideoError("association must be an object")
        display_id = link.get("displayAssetId")
        share_id = link.get("shareAssetId")
        if not isinstance(display_id, str) or not isinstance(share_id, str):
            raise ShareVideoError("association asset IDs must be strings")
        if display_id in seen_display or share_id in seen_share:
            raise ShareVideoError("duplicate or cross-linked animation asset")
        seen_display.add(display_id)
        seen_share.add(share_id)
        display_source = _relative_source(link.get("displaySource"), "images", ".gif")
        display_asset = images.get(display_id)
        expected_display_uri = f"resources/images/{uid}/{display_source.name}"
        if (
            display_asset is None or display_asset.knowledgeId != uid
            or display_asset.uri != expected_display_uri
            or link.get("displayAssetUri") != expected_display_uri
        ):
            raise ShareVideoError(f"GIF asset identity mismatch: {display_id}")
        gif_path = root / display_source
        if not gif_path.is_file() or not _is_sha256(link.get("displaySha256")) or _sha256(gif_path) != link["displaySha256"]:
            raise ShareVideoError(f"GIF source is missing or changed: {display_id}")

        share_source = _relative_source(link.get("shareSource"), "videos", ".mp4")
        share_uri = link.get("shareAssetUri")
        if (
            share_id != f"{uid}:share-video:{share_source.name}"
            or share_uri != f"resources/videos/{uid}/{share_source.name}"
            or share_uri in seen_uri
            or link.get("shareMimeType") != "video/mp4"
        ):
            raise ShareVideoError(f"share video identity mismatch: {share_id}")
        seen_uri.add(share_uri)
        registered_files.add(share_source.name)
        mp4_path = root / share_source
        if (
            not mp4_path.is_file() or mp4_path.is_symlink()
            or not isinstance(link.get("shareBytes"), int) or isinstance(link["shareBytes"], bool)
            or link["shareBytes"] != mp4_path.stat().st_size
            or not _is_sha256(link.get("shareSha256"))
            or _sha256(mp4_path) != link["shareSha256"]
        ):
            raise ShareVideoError(f"MP4 source is missing or changed: {share_id}")
        verify_mp4(mp4_path)
        result.append(ShareVideo({
            "displayAssetId": display_id,
            "displayAssetUri": display_asset.uri,
            "shareAssetId": share_id,
            "knowledgeId": uid,
            "uri": share_uri,
            "mimeType": "video/mp4",
            "bytes": link["shareBytes"],
            "sha256": link["shareSha256"],
        }, mp4_path))

    actual_files = {
        path.name for path in (root / "videos").iterdir()
        if path.name != "share_assets.json"
    }
    if actual_files != registered_files:
        raise ShareVideoError("videos directory has missing or unregistered assets")
    return tuple(sorted(result, key=lambda item: item.record["displayAssetId"]))
