"""Validate C002's local GIF-to-MP4 handoff before Publisher support exists."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


UID_ROOT = Path(__file__).resolve().parents[1]
REGISTRY = UID_ROOT / "videos/share_assets.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(root: Path = UID_ROOT, registry: Path = REGISTRY, *, data: dict | None = None) -> dict:
    if data is None:
        data = json.loads(registry.read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 1 or data.get("knowledgeId") != "C002":
        raise ValueError("invalid C002 share registry header")
    links = data.get("associations")
    if not isinstance(links, list) or not links:
        raise ValueError("share registry must contain associations")
    display_ids: set[str] = set()
    share_ids: set[str] = set()
    for link in links:
        if not isinstance(link, dict):
            raise ValueError("association must be an object")
        display_id = link.get("displayAssetId")
        share_id = link.get("shareAssetId")
        if not isinstance(display_id, str) or not isinstance(share_id, str):
            raise ValueError("asset IDs must be strings")
        if display_id in display_ids or share_id in share_ids:
            raise ValueError("asset association is not one-to-one")
        display_ids.add(display_id)
        share_ids.add(share_id)
        display_uri = link.get("displayAssetUri")
        if display_uri != f"resources/images/C002/{display_id.removeprefix('C002:image:')}":
            raise ValueError("display URI does not match Publisher asset ID")
        expected = (
            ("displaySource", "images", ".gif", "displaySha256"),
            ("shareSource", "videos", ".mp4", "shareSha256"),
        )
        for key, directory, suffix, hash_key in expected:
            source = link.get(key)
            if not isinstance(source, str):
                raise ValueError(f"{key} must be a path")
            relative = Path(source)
            if relative.is_absolute() or ".." in relative.parts or not relative.parts or relative.parts[0] != directory or relative.suffix != suffix:
                raise ValueError(f"unsafe {key}: {source}")
            path = root / relative
            if not path.is_file() or sha256(path) != link.get(hash_key):
                raise ValueError(f"missing or mismatched {key}: {source}")
        if display_id != f"C002:image:{Path(link['displaySource']).name}":
            raise ValueError("display ID does not match source")
        if share_id != f"C002:share-video:{Path(link['shareSource']).name}":
            raise ValueError("share ID does not match source")
        mp4 = root / link["shareSource"]
        if link.get("shareMimeType") != "video/mp4" or link.get("shareBytes") != mp4.stat().st_size:
            raise ValueError("share metadata mismatch")
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration,format_name:stream=codec_name,codec_type,pix_fmt,width,height,r_frame_rate",
             "-of", "json", str(mp4)],
            capture_output=True, text=True, check=True,
        )
        media = json.loads(probe.stdout)
        streams = media["streams"]
        if len(streams) != 1 or streams[0] != {
            "codec_name": "h264", "codec_type": "video", "width": 576, "height": 1024,
            "pix_fmt": "yuv420p", "r_frame_rate": "24/1",
        }:
            raise ValueError("MP4 video specification mismatch")
        if "mp4" not in media["format"]["format_name"] or not 13.3 < float(media["format"]["duration"]) < 13.5:
            raise ValueError("MP4 container or duration mismatch")
        atoms = mp4.read_bytes()
        if not 0 < atoms.find(b"moov") < atoms.find(b"mdat"):
            raise ValueError("MP4 faststart atom order missing")
    return {"knowledgeId": data["knowledgeId"], "associations": len(links)}


if __name__ == "__main__":
    print(json.dumps(validate(), sort_keys=True))
