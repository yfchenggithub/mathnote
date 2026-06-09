#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate WeChat Official Account drafts for selected second-level conclusions.

This script has one job: create draft articles in the WeChat Official Account
draft box. It does not publish articles.

Required environment variables by default:
    WECHAT_APP_ID
    WECHAT_APP_SECRET

Examples:
    python scripts/generate_wechat_drafts.py --ids G010
    python scripts/generate_wechat_drafts.py --ids G010,T002
    python scripts/generate_wechat_drafts.py --modules 05_geometry-solid
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import logging
import mimetypes
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

DEFAULT_CANONICAL_PATH = PROJECT_ROOT / "data" / "content" / "canonical_content_v2.json"
DEFAULT_PDF_MAP_PATH = PROJECT_ROOT / "build" / "conclusion_pdf_map.json"
DEFAULT_PUBLIC_DIR = PROJECT_ROOT / "public"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "build" / "wechat_drafts"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports" / "generate_wechat_drafts_report.json"
DEFAULT_MODULE_PREFIX_MAP = (
    PROJECT_ROOT / "12_pipeline" / "config" / "module_prefix_map.json"
)
DEFAULT_TOKEN_CACHE = DEFAULT_OUTPUT_DIR / "wechat_access_token_cache.json"
DEFAULT_UPLOAD_CACHE = DEFAULT_OUTPUT_DIR / "wechat_upload_cache.json"
MINICODE_ASSET_URL = "/assets/figures/MiniCode.png"
MINICODE_PATH = PROJECT_ROOT / "assets" / "figures" / "MiniCode.png"
DEFAULT_AUTHOR = ""
DEFAULT_COVER_BRAND = "ok-shuxue"
DEFAULT_COVER_SIZE = "1800x1000"
COVER_LAYOUT_VERSION = "v11"
WECHAT_TITLE_PREFIX = "二级结论"
MODULE_DISPLAY_NAMES = {
    "00_set": "集合",
    "01_function": "函数",
    "02_sequence": "数列",
    "03_conic": "圆锥曲线",
    "04_vector": "向量",
    "05_geometry-solid": "立体几何",
    "06_probability-stat": "概率统计",
    "07_inequality": "不等式",
    "08_trigonometry": "三角函数",
    "09_geometry-plane": "平面几何",
    "10_final": "综合压轴",
}
DEFAULT_SECTION_KEYS = (
    "statement",
    "explanation",
    "proof",
    "examples",
    "traps",
    "summary",
)

SECTION_BOX_STYLES = {
    "statement": {"title": "二级结论", "color": "#1F4E79", "bg": "#EAF2F8"},
    "explanation": {
        "title": "理解说明",
        "color": "#355C7D",
        "bg": "#F2F5F7",
        "west": True,
    },
    "proof": {"title": "证明", "color": "#6C5B7B", "bg": "#F3F0F7"},
    "examples": {"title": "典型例题", "color": "#2E7D32", "bg": "#EDF7ED"},
    "traps": {"title": "易错提醒", "color": "#8E2424", "bg": "#FBEAEA", "west": True},
    "summary": {"title": "结论小结", "color": "#5D4037", "bg": "#F5F0EB", "west": True},
}

COLORED_SUBHEADINGS = {
    "一句话核心",
    "一句话直觉",
    "核心拆解",
    "几何本质（高度对称）",
    "代数意义（比例系数）",
    "考点价值（直接公式）",
    "顿悟点",
    "使用场景",
    "思路提示",
    "正式推导",
    "结论回扣",
    "使用条件",
    "关键提醒",
}

WECHAT_API_BASE = "https://api.weixin.qq.com"
ACCESS_TOKEN_MARGIN_SEC = 300
ID_PATTERN = re.compile(r"^[A-Za-z]\d{3}$")

LOGGER = logging.getLogger("generate_wechat_drafts")


class DraftError(RuntimeError):
    """Readable failure for expected draft-generation errors."""


@dataclass(frozen=True)
class WechatConfig:
    app_id: str
    app_secret: str
    timeout_sec: int
    token_cache_path: Path
    upload_cache_path: Path
    refresh_upload_cache: bool


@dataclass(frozen=True)
class DraftConfig:
    ids: tuple[str, ...]
    canonical_path: Path
    pdf_map_path: Path
    public_dir: Path
    output_dir: Path
    report_path: Path
    author: str
    cover_brand: str
    cover_size: tuple[int, int]
    force_cover: bool
    section_keys: tuple[str, ...]
    content_source_url_template: str
    need_open_comment: int
    only_fans_can_comment: int
    log_level: str
    wechat: WechatConfig


@dataclass
class ImageUpload:
    asset_url: str
    local_path: str
    sha256: str
    wechat_url: str
    cached: bool


@dataclass
class DraftItemReport:
    id: str
    title: str
    status: str
    output_dir: str
    cover_path: str
    cover_cached_upload: bool = False
    thumb_media_id: str | None = None
    article_media_id: str | None = None
    article_html: str | None = None
    draft_payload: str | None = None
    asset_manifest: str | None = None
    image_uploads: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    error: str | None = None


def configure_console_encoding() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None or not hasattr(stream, "reconfigure"):
            continue
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


def configure_logging(level_name: str) -> None:
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")


def split_csv_tokens(values: Sequence[str] | None) -> list[str]:
    tokens: list[str] = []
    for raw in values or ():
        for token in str(raw).split(","):
            piece = token.strip()
            if piece:
                tokens.append(piece)
    return tokens


def dedupe_keep_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def parse_size(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"\s*(\d+)x(\d+)\s*", value.lower())
    if not match:
        raise argparse.ArgumentTypeError("expected size like 1800x1000")
    width = int(match.group(1))
    height = int(match.group(2))
    if width < 300 or height < 180:
        raise argparse.ArgumentTypeError("cover size is too small")
    return width, height


def read_windows_persisted_env(name: str) -> str:
    if os.name != "nt":
        return ""
    try:
        import winreg
    except ImportError:
        return ""

    locations = (
        (winreg.HKEY_CURRENT_USER, r"Environment"),
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
        ),
    )
    for root, subkey in locations:
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


def read_env(name: str) -> str:
    return os.environ.get(name, "") or read_windows_persisted_env(name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate WeChat Official Account draft articles.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/generate_wechat_drafts.py --ids G010\n"
            "  python scripts/generate_wechat_drafts.py --ids G010,T002\n"
            "  python scripts/generate_wechat_drafts.py --modules 05_geometry-solid\n"
        ),
    )
    parser.add_argument(
        "positional_ids", nargs="*", help="Conclusion IDs, e.g. G010 T002."
    )
    parser.add_argument(
        "--ids",
        nargs="*",
        default=None,
        help="Conclusion IDs. Supports comma or space separated values.",
    )
    parser.add_argument(
        "--modules",
        nargs="*",
        default=None,
        help="Module dirs/slugs/prefixes, e.g. 05_geometry-solid or G.",
    )
    parser.add_argument("--canonical-json", default=str(DEFAULT_CANONICAL_PATH))
    parser.add_argument("--pdf-map-json", default=str(DEFAULT_PDF_MAP_PATH))
    parser.add_argument("--public-dir", default=str(DEFAULT_PUBLIC_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--report", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--appid-env", default="WECHAT_APP_ID")
    parser.add_argument("--secret-env", default="WECHAT_APP_SECRET")
    parser.add_argument(
        "--author",
        default=DEFAULT_AUTHOR,
        help="Optional author shown in WeChat preview. Default: omitted.",
    )
    parser.add_argument("--cover-brand", default=DEFAULT_COVER_BRAND)
    parser.add_argument(
        "--cover-size", type=parse_size, default=parse_size(DEFAULT_COVER_SIZE)
    )
    parser.add_argument(
        "--force-cover",
        action="store_true",
        help="Regenerate cover PNG files even when they exist.",
    )
    parser.add_argument(
        "--refresh-upload-cache",
        action="store_true",
        help="Ignore cached WeChat image upload results and upload again.",
    )
    parser.add_argument(
        "--section-keys",
        nargs="*",
        default=None,
        help=(
            "Canonical section keys to include. Default: "
            + ",".join(DEFAULT_SECTION_KEYS)
        ),
    )
    parser.add_argument(
        "--content-source-url-template",
        default="",
        help=(
            "Optional article source URL template. Supports {id}, {pdf}, {title}. "
            "Default: empty string."
        ),
    )
    parser.add_argument("--need-open-comment", type=int, choices=(0, 1), default=0)
    parser.add_argument("--only-fans-can-comment", type=int, choices=(0, 1), default=0)
    parser.add_argument(
        "--timeout", type=int, default=30, help="HTTP timeout in seconds."
    )
    parser.add_argument(
        "--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING", "ERROR")
    )
    return parser.parse_args()


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        if default is not None:
            return default
        raise DraftError(f"JSON file not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise DraftError(f"Invalid JSON in {path}: {exc}") from exc


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def load_module_prefix_map() -> dict[str, str]:
    raw = read_json(DEFAULT_MODULE_PREFIX_MAP)
    if not isinstance(raw, dict):
        raise DraftError(f"Invalid module prefix map: {DEFAULT_MODULE_PREFIX_MAP}")
    result: dict[str, str] = {}
    for module, prefix in raw.items():
        module_name = str(module).strip()
        prefix_text = str(prefix).strip().upper()
        if module_name and re.fullmatch(r"[A-Z]", prefix_text):
            result[module_name] = prefix_text
    return result


def normalize_module_arg(raw: str, module_prefix_map: dict[str, str]) -> str:
    value = raw.strip()
    if not value:
        raise DraftError("Empty module argument.")
    upper = value.upper()
    if re.fullmatch(r"[A-Z]", upper):
        for module, prefix in module_prefix_map.items():
            if prefix == upper:
                return module
        raise DraftError(f"Unknown module prefix: {value}")
    if value in module_prefix_map:
        return value
    for module in module_prefix_map:
        if module.split("_", 1)[-1] == value:
            return module
    allowed = ", ".join(module_prefix_map)
    raise DraftError(f"Unknown module: {value}. Allowed: {allowed}")


def sort_ids(ids: Iterable[str]) -> list[str]:
    def key(value: str) -> tuple[str, int, str]:
        match = re.fullmatch(r"([A-Z])(\d{3})", value.upper())
        if not match:
            return (value.upper(), 0, value.upper())
        return (match.group(1), int(match.group(2)), value.upper())

    return sorted((item.upper() for item in ids), key=key)


def resolve_ids(args: argparse.Namespace, canonical: dict[str, Any]) -> tuple[str, ...]:
    module_prefix_map = load_module_prefix_map()
    raw_ids = split_csv_tokens(args.ids) + split_csv_tokens(args.positional_ids)
    ids: list[str] = []
    invalid: list[str] = []
    for raw_id in raw_ids:
        normalized = raw_id.upper()
        if not ID_PATTERN.fullmatch(normalized):
            invalid.append(raw_id)
        else:
            ids.append(normalized)

    if invalid:
        raise DraftError(
            "Invalid conclusion ID(s): "
            + ", ".join(invalid)
            + ". Expected values like G010."
        )

    for raw_module in split_csv_tokens(args.modules):
        module = normalize_module_arg(raw_module, module_prefix_map)
        prefix = module_prefix_map[module]
        ids.extend(
            item_id
            for item_id in canonical.keys()
            if isinstance(item_id, str) and item_id.startswith(prefix)
        )

    ids = sort_ids(dedupe_keep_order(ids))
    if not ids:
        raise DraftError("Provide at least one --ids value or one --modules value.")

    missing = [item_id for item_id in ids if item_id not in canonical]
    if missing:
        raise DraftError("Canonical content missing ID(s): " + ", ".join(missing))
    return tuple(ids)


def build_config(args: argparse.Namespace) -> DraftConfig:
    canonical_path = Path(args.canonical_json).resolve()
    canonical = read_json(canonical_path)
    if not isinstance(canonical, dict):
        raise DraftError(f"Canonical JSON must be an object: {canonical_path}")
    output_dir = Path(args.output_dir).resolve()

    app_id = read_env(str(args.appid_env)).strip()
    app_secret = read_env(str(args.secret_env)).strip()
    if not app_id:
        raise DraftError(f"Missing WeChat app id. Set ${args.appid_env}.")
    if not app_secret:
        raise DraftError(f"Missing WeChat app secret. Set ${args.secret_env}.")
    if int(args.timeout) <= 0:
        raise DraftError("--timeout must be > 0.")

    section_keys = (
        tuple(split_csv_tokens(args.section_keys))
        if args.section_keys
        else DEFAULT_SECTION_KEYS
    )

    return DraftConfig(
        ids=resolve_ids(args, canonical),
        canonical_path=canonical_path,
        pdf_map_path=Path(args.pdf_map_json).resolve(),
        public_dir=Path(args.public_dir).resolve(),
        output_dir=output_dir,
        report_path=Path(args.report).resolve(),
        author=str(args.author).strip(),
        cover_brand=str(args.cover_brand).strip(),
        cover_size=tuple(args.cover_size),
        force_cover=bool(args.force_cover),
        section_keys=section_keys,
        content_source_url_template=str(args.content_source_url_template).strip(),
        need_open_comment=int(args.need_open_comment),
        only_fans_can_comment=int(args.only_fans_can_comment),
        log_level=str(args.log_level),
        wechat=WechatConfig(
            app_id=app_id,
            app_secret=app_secret,
            timeout_sec=int(args.timeout),
            token_cache_path=output_dir / DEFAULT_TOKEN_CACHE.name,
            upload_cache_path=output_dir / DEFAULT_UPLOAD_CACHE.name,
            refresh_upload_cache=bool(args.refresh_upload_cache),
        ),
    )


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def app_cache_key(app_id: str) -> str:
    return sha256_text(app_id)[:16]


def http_json(
    url: str,
    *,
    method: str = "GET",
    payload: Any = None,
    timeout: int = 30,
) -> dict[str, Any]:
    headers: dict[str, str] = {}
    data: bytes | None = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except Exception as exc:
        raise DraftError(f"WeChat HTTP request failed: {url}\n{exc}") from exc
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise DraftError(f"WeChat response is not JSON: {url}\n{raw[:500]!r}") from exc
    if not isinstance(parsed, dict):
        raise DraftError(f"WeChat response must be an object: {url}")
    errcode = parsed.get("errcode")
    if errcode not in (None, 0, "0"):
        errmsg = parsed.get("errmsg", "")
        raise DraftError(f"WeChat API error {errcode}: {errmsg}")
    return parsed


def post_multipart(
    url: str,
    *,
    files: dict[str, Path],
    fields: dict[str, str] | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    boundary = f"----mathnote-wechat-{time.time_ns()}"
    chunks: list[bytes] = []

    for key, value in (fields or {}).items():
        chunks.append(f"--{boundary}\r\n".encode("utf-8"))
        chunks.append(
            f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode("utf-8")
        )
        chunks.append(str(value).encode("utf-8"))
        chunks.append(b"\r\n")

    for field_name, path in files.items():
        filename = path.name
        mime_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        chunks.append(f"--{boundary}\r\n".encode("utf-8"))
        chunks.append(
            (
                f'Content-Disposition: form-data; name="{field_name}"; '
                f'filename="{filename}"\r\n'
            ).encode("utf-8")
        )
        chunks.append(f"Content-Type: {mime_type}\r\n\r\n".encode("utf-8"))
        chunks.append(path.read_bytes())
        chunks.append(b"\r\n")

    chunks.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(chunks)
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except Exception as exc:
        raise DraftError(f"WeChat multipart request failed: {url}\n{exc}") from exc
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise DraftError(f"WeChat response is not JSON: {url}\n{raw[:500]!r}") from exc
    if not isinstance(parsed, dict):
        raise DraftError(f"WeChat response must be an object: {url}")
    errcode = parsed.get("errcode")
    if errcode not in (None, 0, "0"):
        errmsg = parsed.get("errmsg", "")
        raise DraftError(f"WeChat API error {errcode}: {errmsg}")
    return parsed


def load_cache(path: Path) -> dict[str, Any]:
    payload = read_json(path, default={})
    if not isinstance(payload, dict):
        return {}
    return payload


def save_cache(path: Path, payload: dict[str, Any]) -> None:
    payload.setdefault("version", 1)
    write_json(path, payload)


def get_access_token(config: WechatConfig) -> str:
    cache = load_cache(config.token_cache_path)
    tokens = cache.setdefault("tokens", {})
    key = app_cache_key(config.app_id)
    now = int(time.time())
    cached = tokens.get(key) if isinstance(tokens, dict) else None
    if isinstance(cached, dict):
        token = str(cached.get("access_token", ""))
        expires_at = int(cached.get("expires_at", 0) or 0)
        if token and expires_at > now + ACCESS_TOKEN_MARGIN_SEC:
            LOGGER.info("Using cached WeChat access_token.")
            return token

    query = urllib.parse.urlencode(
        {
            "grant_type": "client_credential",
            "appid": config.app_id,
            "secret": config.app_secret,
        }
    )
    url = f"{WECHAT_API_BASE}/cgi-bin/token?{query}"
    payload = http_json(url, timeout=config.timeout_sec)
    token = str(payload.get("access_token", "")).strip()
    if not token:
        raise DraftError("WeChat access_token response has no access_token.")
    expires_in = int(payload.get("expires_in", 7200) or 7200)
    tokens[key] = {
        "access_token": token,
        "expires_at": now + expires_in,
        "updated_at": now_iso(),
    }
    cache["tokens"] = tokens
    save_cache(config.token_cache_path, cache)
    return token


def cache_upload_lookup(
    cache: dict[str, Any],
    *,
    bucket: str,
    key: str,
    field: str,
    refresh: bool,
) -> str | None:
    if refresh:
        return None
    entries = cache.get(bucket)
    if not isinstance(entries, dict):
        return None
    entry = entries.get(key)
    if not isinstance(entry, dict):
        return None
    value = str(entry.get(field, "")).strip()
    return value or None


def cache_upload_store(
    cache: dict[str, Any],
    *,
    bucket: str,
    key: str,
    entry: dict[str, Any],
) -> None:
    entries = cache.setdefault(bucket, {})
    if not isinstance(entries, dict):
        entries = {}
        cache[bucket] = entries
    entry["updated_at"] = now_iso()
    entries[key] = entry


def upload_cover_material(
    *,
    config: WechatConfig,
    access_token: str,
    cover_path: Path,
    upload_cache: dict[str, Any],
) -> tuple[str, bool]:
    digest = sha256_file(cover_path)
    key = f"{app_cache_key(config.app_id)}:{digest}"
    cached = cache_upload_lookup(
        upload_cache,
        bucket="cover_material",
        key=key,
        field="media_id",
        refresh=config.refresh_upload_cache,
    )
    if cached:
        return cached, True

    query = urllib.parse.urlencode({"access_token": access_token, "type": "image"})
    url = f"{WECHAT_API_BASE}/cgi-bin/material/add_material?{query}"
    payload = post_multipart(
        url,
        files={"media": cover_path},
        timeout=config.timeout_sec,
    )
    media_id = str(payload.get("media_id", "")).strip()
    if not media_id:
        raise DraftError(
            f"WeChat permanent image upload returned no media_id: {payload}"
        )
    cache_upload_store(
        upload_cache,
        bucket="cover_material",
        key=key,
        entry={
            "media_id": media_id,
            "url": payload.get("url", ""),
            "path": str(cover_path),
            "sha256": digest,
        },
    )
    return media_id, False


def upload_article_image(
    *,
    config: WechatConfig,
    access_token: str,
    path: Path,
    upload_cache: dict[str, Any],
) -> tuple[str, str, bool]:
    digest = sha256_file(path)
    key = f"{app_cache_key(config.app_id)}:{digest}"
    cached = cache_upload_lookup(
        upload_cache,
        bucket="article_images",
        key=key,
        field="url",
        refresh=config.refresh_upload_cache,
    )
    if cached:
        return cached, digest, True

    query = urllib.parse.urlencode({"access_token": access_token})
    url = f"{WECHAT_API_BASE}/cgi-bin/media/uploadimg?{query}"
    payload = post_multipart(
        url,
        files={"media": path},
        timeout=config.timeout_sec,
    )
    wechat_url = str(payload.get("url", "")).strip()
    if not wechat_url:
        raise DraftError(f"WeChat article image upload returned no url: {payload}")
    cache_upload_store(
        upload_cache,
        bucket="article_images",
        key=key,
        entry={
            "url": wechat_url,
            "path": str(path),
            "sha256": digest,
        },
    )
    return wechat_url, digest, False


def add_wechat_draft(
    *,
    config: WechatConfig,
    access_token: str,
    article: dict[str, Any],
) -> str:
    query = urllib.parse.urlencode({"access_token": access_token})
    url = f"{WECHAT_API_BASE}/cgi-bin/draft/add?{query}"
    payload = http_json(
        url,
        method="POST",
        payload={"articles": [article]},
        timeout=config.timeout_sec,
    )
    media_id = str(payload.get("media_id", "")).strip()
    if not media_id:
        raise DraftError(f"WeChat draft add returned no media_id: {payload}")
    return media_id


def local_asset_path(public_dir: Path, asset_url: str) -> Path | None:
    text = str(asset_url or "").strip()
    if not text or re.match(r"^https?://", text, flags=re.I):
        return None
    normalized = text.split("?", 1)[0].split("#", 1)[0].replace("\\", "/")
    if normalized.startswith("/"):
        normalized = normalized[1:]
    if normalized.startswith("assets/"):
        return PROJECT_ROOT / normalized
    return public_dir / normalized


def resolve_asset_url(node: dict[str, Any]) -> str:
    asset = node.get("asset")
    if isinstance(asset, dict) and isinstance(asset.get("png"), str):
        return str(asset["png"])
    if isinstance(node.get("src"), str):
        return str(node["src"])
    return ""


def iter_dict_nodes(root: Any):
    stack = [root]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            yield node
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)


def prepare_record_for_formula_render(record: dict[str, Any]) -> dict[str, Any]:
    prepared = copy.deepcopy(record)
    for node in iter_dict_nodes(prepared):
        primary = node.get("primary_formula")
        if (
            isinstance(primary, dict)
            and isinstance(primary.get("latex"), str)
            and primary["latex"].strip()
        ):
            primary["type"] = "math_block"
            primary["need_image"] = "true"

        latex = node.get("latex")
        node_type = str(node.get("type", ""))
        if not isinstance(latex, str) or not latex.strip():
            continue
        if node_type in {"math_image", "math_inline", "math_display", "math_block"}:
            node["type"] = (
                "math_inline"
                if node_type in {"math_inline", "math_display"}
                else "math_block"
            )
            node["need_image"] = "true"
    return prepared


def render_formula_assets_for_records(
    *,
    records: dict[str, Any],
    config: DraftConfig,
) -> dict[str, Any]:
    prepared = {
        item_id: prepare_record_for_formula_render(record)
        for item_id, record in records.items()
    }
    tmp_dir = config.output_dir / "_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    input_path = tmp_dir / "wechat_formula_input.json"
    output_path = tmp_dir / "wechat_formula_rendered.json"
    write_json(input_path, prepared)

    command = [
        "node",
        str(SCRIPT_DIR / "render_math_assets.mjs"),
        "--input",
        str(input_path),
        "--output",
        str(output_path),
        "--out-dir",
        str(config.public_dir / "static" / "formulas"),
        "--asset-base",
        "/static/formulas",
    ]
    LOGGER.info("Rendering/reusing formula assets for WeChat drafts.")
    result = subprocess.run(
        command,
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise DraftError(
            "Formula asset rendering failed.\n"
            f"Command: {' '.join(command)}\n"
            f"stdout:\n{result.stdout[-2000:]}\n"
            f"stderr:\n{result.stderr[-2000:]}"
        )
    rendered = read_json(output_path)
    if not isinstance(rendered, dict):
        raise DraftError(f"Rendered formula JSON must be an object: {output_path}")
    return rendered


def collect_article_image_refs(
    record: dict[str, Any], public_dir: Path
) -> dict[str, Path]:
    refs: dict[str, Path] = {}
    for node in iter_dict_nodes(record):
        if not isinstance(node, dict):
            continue
        node_type = str(node.get("type", ""))
        if node_type not in {"math_image", "image_block"}:
            continue
        asset_url = resolve_asset_url(node)
        if not asset_url:
            continue
        local_path = local_asset_path(public_dir, asset_url)
        if local_path is None:
            raise DraftError(
                f"Cannot upload remote image URL as article image: {asset_url}"
            )
        if not local_path.is_file():
            raise DraftError(
                f"Article image asset missing: {asset_url} -> {local_path}"
            )
        refs.setdefault(asset_url, local_path)
    if not MINICODE_PATH.is_file():
        raise DraftError(f"Mini program code image missing: {MINICODE_PATH}")
    refs.setdefault(MINICODE_ASSET_URL, MINICODE_PATH)
    return refs


def truncate_text(text: str, limit: int) -> str:
    normalized = " ".join(str(text or "").split())
    if len(normalized) <= limit:
        return normalized
    if limit <= 1:
        return normalized[:limit]
    return normalized[: limit - 1].rstrip() + "…"


def record_title(record: dict[str, Any]) -> str:
    meta = record.get("meta") if isinstance(record.get("meta"), dict) else {}
    ext = record.get("ext") if isinstance(record.get("ext"), dict) else {}
    share = ext.get("share") if isinstance(ext.get("share"), dict) else {}
    title = str(
        share.get("title") or meta.get("title") or record.get("id") or ""
    ).strip()
    return title or "二级结论"


def module_display_name_from_slug(module: str) -> str:
    value = str(module or "").strip()
    if not value:
        return ""
    if value in MODULE_DISPLAY_NAMES:
        return MODULE_DISPLAY_NAMES[value]
    # Fallback: 05_geometry-solid -> geometry solid
    text = value.split("_", 1)[-1].replace("-", " ").replace("_", " ").strip()
    return text


def module_display_name_for_item(record: dict[str, Any], item_id: str) -> str:
    """Return the Chinese module name implied by the ID prefix.

    The source of truth is module_prefix_map.json, e.g. 05_geometry-solid -> G,
    so G009 can be rendered as “立体几何 G009”.
    """
    item = str(item_id or "").strip().upper()
    prefix = item[:1]
    if prefix:
        try:
            prefix_map = load_module_prefix_map()
        except Exception:
            prefix_map = {}
        for module, mapped_prefix in prefix_map.items():
            if str(mapped_prefix).strip().upper() == prefix:
                label = module_display_name_from_slug(module)
                if label:
                    return label

    category = record_category(record)
    return category or ""


def public_title_prefix(record: dict[str, Any], item_id: str) -> str:
    module_name = module_display_name_for_item(record, item_id)
    if module_name:
        return f"{WECHAT_TITLE_PREFIX} {module_name} {item_id}"
    return f"{WECHAT_TITLE_PREFIX} {item_id}"


def strip_title_prefix(title: str, item_id: str) -> str:
    """Remove old ID/module/keyword prefixes so new titles do not repeat themselves."""
    text = str(title or "").strip()
    item = re.escape(str(item_id or "").strip())
    # Handles both old titles like “二级结论 G009｜...” and new titles
    # like “二级结论 立体几何 G009｜...”.
    patterns = (
        rf"^\s*{WECHAT_TITLE_PREFIX}\s*(?:[\u4e00-\u9fa5A-Za-z0-9_\-]+\s*)*{item}\s*[｜|:：\-—]*\s*",
        rf"^\s*{item}\s*{WECHAT_TITLE_PREFIX}\s*[｜|:：\-—]*\s*",
        rf"^\s*高中数学{WECHAT_TITLE_PREFIX}\s*[｜|:：\-—]*\s*",
        rf"^\s*{WECHAT_TITLE_PREFIX}\s*[｜|:：\-—]*\s*",
    )
    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.I).strip()
    return text or str(title or "").strip() or "数学结论"


def public_article_title(record: dict[str, Any], item_id: str) -> str:
    """WeChat article title: force 二级结论, module name and ID into the title."""
    base = strip_title_prefix(record_title(record), item_id)
    return truncate_text(f"{public_title_prefix(record, item_id)}｜{base}", 64)


def public_article_digest(record: dict[str, Any], item_id: str) -> str:
    raw = record_digest(record)
    if not raw:
        base = strip_title_prefix(record_title(record), item_id)
        raw = f"{base}，核心公式、适用条件、典型例题和易错提醒。"
    return truncate_text(f"{public_title_prefix(record, item_id)}：{raw}", 120)


def split_cover_title(record: dict[str, Any], item_id: str) -> tuple[str, str]:
    """Split title into cover main title and value subtitle.

    Example:
        正四面体外接球半径公式：棱长到半径一阶转换
        -> 正四面体外接球半径公式 / 棱长到半径一阶转换
    """
    base = strip_title_prefix(record_title(record), item_id)
    parts = re.split(r"[：:]", base, maxsplit=1)
    main = parts[0].strip() if parts else base.strip()
    subtitle = parts[1].strip() if len(parts) > 1 else "公式速查 · 条件清楚 · 直接使用"
    return truncate_text(main, 32), truncate_text(subtitle, 28)


def cover_kicker(record: dict[str, Any], item_id: str) -> str:
    return public_title_prefix(record, item_id)


def record_body_title(record: dict[str, Any]) -> str:
    meta = record.get("meta") if isinstance(record.get("meta"), dict) else {}
    title = str(meta.get("title") or "").strip()
    return title or record_title(record)


def record_digest(record: dict[str, Any]) -> str:
    meta = record.get("meta") if isinstance(record.get("meta"), dict) else {}
    ext = record.get("ext") if isinstance(record.get("ext"), dict) else {}
    share = ext.get("share") if isinstance(ext.get("share"), dict) else {}
    return truncate_text(str(share.get("desc") or meta.get("summary") or ""), 120)


def record_category(record: dict[str, Any]) -> str:
    meta = record.get("meta") if isinstance(record.get("meta"), dict) else {}
    identity = (
        record.get("identity") if isinstance(record.get("identity"), dict) else {}
    )
    return str(meta.get("category") or identity.get("module") or "").strip()


def primary_formula_node(record: dict[str, Any]) -> dict[str, Any] | None:
    content = record.get("content") if isinstance(record.get("content"), dict) else {}
    formula = content.get("primary_formula")
    return formula if isinstance(formula, dict) else None


def primary_formula_latex(record: dict[str, Any]) -> str:
    formula = primary_formula_node(record)
    if isinstance(formula, dict):
        return str(formula.get("latex") or "").strip()
    return ""


def primary_formula_local_path(record: dict[str, Any], public_dir: Path) -> Path | None:
    formula = primary_formula_node(record)
    if not isinstance(formula, dict):
        return None
    asset_url = resolve_asset_url(formula)
    if not asset_url:
        return None
    local_path = local_asset_path(public_dir, asset_url)
    if local_path and local_path.is_file():
        return local_path
    return None


def find_font(size: int, *, bold: bool = False):
    try:
        from PIL import ImageFont
    except ImportError as exc:
        raise DraftError(
            "Pillow is required for cover generation. Install pillow first."
        ) from exc

    candidates = []
    if os.name == "nt":
        windir = Path(os.environ.get("WINDIR", r"C:\Windows"))
        candidates.extend(
            [
                windir / "Fonts" / ("msyhbd.ttc" if bold else "msyh.ttc"),
                windir / "Fonts" / ("simhei.ttf" if bold else "simkai.ttf"),
                windir / "Fonts" / "simsun.ttc",
                windir / "Fonts" / "arial.ttf",
            ]
        )
    candidates.extend(
        [
            Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
            Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]
    )
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def text_width(draw: Any, text: str, font: Any) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return int(bbox[2] - bbox[0])


def wrap_text(
    draw: Any, text: str, font: Any, max_width: int, max_lines: int
) -> list[str]:
    words = list(text)
    lines: list[str] = []
    current = ""
    for char in words:
        candidate = current + char
        if text_width(draw, candidate, font) <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = char
        if len(lines) >= max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    if len(lines) == max_lines and "".join(lines) != text:
        lines[-1] = lines[-1].rstrip("，。；：、 ") + "…"
    return lines


def fit_font_to_width(
    draw: Any,
    text: str,
    *,
    max_width: int,
    initial_size: int,
    min_size: int,
    bold: bool = False,
):
    size = max(initial_size, min_size)
    while size > min_size:
        font = find_font(size, bold=bold)
        if text_width(draw, text, font) <= max_width:
            return font
        size -= 2
    return find_font(min_size, bold=bold)


def draw_centered_text(
    draw: Any,
    box: tuple[int, int, int, int] | list[int],
    text: str,
    font: Any,
    *,
    fill: str,
) -> None:
    left, top, right, bottom = map(int, box)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = left + (right - left - text_w) // 2 - bbox[0]
    y = top + (bottom - top - text_h) // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=fill)


def generate_cover(
    *,
    record: dict[str, Any],
    item_id: str,
    config: DraftConfig,
    output_path: Path,
) -> None:
    if output_path.exists() and not config.force_cover:
        return

    try:
        from PIL import Image, ImageDraw, ImageOps, ImageChops
    except ImportError as exc:
        raise DraftError(
            "Pillow is required for cover generation. Install pillow first."
        ) from exc

    width, height = config.cover_size
    image = Image.new("RGB", (width, height), "#f7f5ef")
    draw = ImageDraw.Draw(image)

    # Cover v7:
    # 1. Separate title and subtitle with noticeably more breathing room.
    # 2. Remove the white formula background completely.
    # 3. Extract only the dark strokes of the formula and render them in a light
    #    color onto a dark integrated panel.
    for x in range(width):
        ratio = x / max(width - 1, 1)
        r = int(11 + 21 * ratio)
        g = int(60 + 36 * ratio)
        b = int(74 + 42 * ratio)
        draw.line([(x, 0), (x, height)], fill=(r, g, b))

    margin = int(width * 0.07)
    top = int(height * 0.058)
    main_title, subtitle = split_cover_title(record, item_id)
    category = record_category(record)
    formula = primary_formula_latex(record)

    brand_font = find_font(int(width * 0.023), bold=True)
    title_font = find_font(int(width * 0.051), bold=True)
    small_font = find_font(int(width * 0.023), bold=False)

    brand = config.cover_brand.strip() or DEFAULT_COVER_BRAND
    if "数秒查" not in brand:
        brand = f"{brand} · 数秒查"
    draw.text((margin, top), brand, font=brand_font, fill="#D8EDF0")

    if category:
        chip_text = truncate_text(category, 16)
        chip_w = text_width(draw, chip_text, small_font) + int(width * 0.04)
        chip_h = int(height * 0.052)
        chip_x = width - margin - chip_w
        chip_y = top
        draw.rounded_rectangle(
            [chip_x, chip_y, chip_x + chip_w, chip_y + chip_h],
            radius=chip_h // 2,
            outline="#9FC9CE",
            width=2,
        )
        draw_centered_text(
            draw,
            [chip_x, chip_y, chip_x + chip_w, chip_y + chip_h],
            chip_text,
            small_font,
            fill="#D8EDF0",
        )

    kicker = cover_kicker(record, item_id)
    badge_pad_x = int(width * 0.030)
    badge_x = margin
    badge_y = int(height * 0.135)
    badge_max_w = int(width * 0.86)
    badge_h = int(height * 0.078)
    kicker_font = fit_font_to_width(
        draw,
        kicker,
        max_width=badge_max_w - badge_pad_x * 2,
        initial_size=int(width * 0.034),
        min_size=int(width * 0.024),
        bold=True,
    )
    badge_w = min(text_width(draw, kicker, kicker_font) + badge_pad_x * 2, badge_max_w)
    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
        radius=badge_h // 2,
        fill="#F4D35E",
    )
    draw_centered_text(
        draw,
        [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
        kicker,
        kicker_font,
        fill="#123F4C",
    )

    title_y = int(height * 0.255)
    title_lines = wrap_text(draw, main_title, title_font, int(width * 0.82), 2)
    for line in title_lines:
        draw.text((margin, title_y), line, font=title_font, fill="#FFFFFF")
        title_y += int(height * 0.112)

    subtitle_line = truncate_text(subtitle, 20)
    subtitle_font = fit_font_to_width(
        draw,
        subtitle_line,
        max_width=int(width * 0.68),
        initial_size=int(width * 0.028),
        min_size=int(width * 0.021),
        bold=True,
    )
    subtitle_y = title_y + int(height * 0.050)
    draw.text((margin, subtitle_y), subtitle_line, font=subtitle_font, fill="#F4D35E")

    # Remove the yellow divider and also remove the separate card feeling.
    # The formula should live directly inside the same teal gradient region as
    # the title area, with no extra box fill and no yellow line.
    formula_box = [margin, int(height * 0.555), width - margin, int(height * 0.905)]

    formula_path = primary_formula_local_path(record, config.public_dir)
    content_left = formula_box[0] + int(width * 0.015)
    content_right = formula_box[2] - int(width * 0.015)
    content_top = formula_box[1] + int(height * 0.020)
    content_bottom = formula_box[3] - int(height * 0.020)

    if formula_path:
        formula_img = Image.open(formula_path).convert("RGBA")

        # Robust formula extraction for both kinds of assets:
        # 1) already-transparent formula PNGs, and
        # 2) white-background formula PNGs.
        # Goal: remove the light background, keep dark strokes, and recolor the
        # formula into a light tone for the dark panel.
        alpha = formula_img.getchannel("A")
        alpha_bbox = alpha.getbbox()
        if alpha_bbox:
            formula_img = formula_img.crop(alpha_bbox)
            alpha = formula_img.getchannel("A")

        # Flatten on white first, then detect dark strokes from luminance.
        # IMPORTANT: do not use the original alpha as the final mask. Many formula
        # assets are opaque white-background PNGs; using alpha directly will turn
        # the whole white rectangle into a light block and the formula disappears.
        flat_rgb = Image.new("RGBA", formula_img.size, (255, 255, 255, 255))
        flat_rgb.alpha_composite(formula_img)
        gray = ImageOps.grayscale(flat_rgb)

        # Darker pixels become more opaque; near-white pixels disappear.
        stroke_mask = gray.point(
            lambda p: 0 if p >= 238 else max(0, min(255, int((238 - p) * 255 / 150)))
        )

        # Respect transparent backgrounds by multiplying with the original alpha,
        # but keep the dark-stroke mask as the source of truth.
        try:
            stroke_mask = ImageChops.multiply(stroke_mask, alpha)
        except Exception:
            pass

        bbox = stroke_mask.getbbox()
        if bbox:
            stroke_mask = stroke_mask.crop(bbox)
        else:
            # Fallback: if stroke detection fails, keep a normal dark formula on
            # a light-free panel by using the original cropped image's alpha.
            stroke_mask = alpha
            bbox = stroke_mask.getbbox()
            if bbox:
                stroke_mask = stroke_mask.crop(bbox)

        tinted = Image.new("RGBA", stroke_mask.size, (247, 245, 238, 0))
        tinted.putalpha(stroke_mask)
        formula_img = tinted

        max_w = int((content_right - content_left) * 0.995)
        max_h = int((content_bottom - content_top) * 0.985)
        scale = min(max_w / formula_img.width, max_h / formula_img.height, 7.2)
        new_size = (
            max(1, int(formula_img.width * scale)),
            max(1, int(formula_img.height * scale)),
        )
        formula_img = formula_img.resize(new_size, Image.LANCZOS)
        paste_x = content_left + (content_right - content_left - new_size[0]) // 2
        paste_y = content_top + (content_bottom - content_top - new_size[1]) // 2
        image.paste(formula_img, (paste_x, paste_y), formula_img)
    elif formula:
        fallback_formula = truncate_text(formula.replace("\n", " "), 84)
        formula_font = fit_font_to_width(
            draw,
            fallback_formula,
            max_width=content_right - content_left,
            initial_size=int(width * 0.052),
            min_size=int(width * 0.032),
            bold=False,
        )
        draw_centered_text(
            draw,
            [content_left, content_top, content_right, content_bottom],
            fallback_formula,
            formula_font,
            fill="#F7F5EF",
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format="PNG")


def escape_text(text: str) -> str:
    return html.escape(str(text), quote=False)


def text_to_html(text: str) -> str:
    parts = escape_text(text).splitlines()
    return "<br/>".join(parts)


def section_color(section_key: str) -> str:
    style = SECTION_BOX_STYLES.get(section_key)
    if style:
        return style["color"]
    return "#164554"


def paragraph_label_color(section_key: str, label: str) -> str:
    if section_key in {"statement", "traps"}:
        return section_color(section_key)
    if section_key == "examples" and re.match(
        r"^(?:例\s*\d+|题目|解题步骤|关键结论)", label
    ):
        return section_color(section_key)
    return "#111827"


def format_inline_labels(content_html: str, *, section_key: str = "") -> str:
    label_pattern = re.compile(
        r"(^|<br/>|[。；]\s*)"
        r"((?:"
        r"例\s*\d+"
        r"|"
        r"要点[一二三四五六七八九十]+"
        r"|步骤[一二三四五六七八九十]+"
        r"|考法[一二三四五六七八九十]+"
        r"|场景[一二三四五六七八九十]+"
        r"|条件\s*\d+"
        r"|易错点[一二三四五六七八九十]*"
        r"|正确理解"
        r"|错因分析"
        r"|第一步|第二步|第三步|第四步|第五步|第六步"
        r"|题目|解题步骤|关键结论|理由"
        r")[^：:<]{0,28}[：:])"
    )

    def replace(match: re.Match[str]) -> str:
        prefix = match.group(1)
        label = match.group(2)
        color = paragraph_label_color(section_key, label)
        return (
            f'{prefix}<strong style="font-weight:700;color:{color};">'
            f"{label}</strong>"
        )

    return label_pattern.sub(replace, content_html)


def split_first_line(raw_text: str) -> tuple[str, str]:
    lines = str(raw_text or "").splitlines()
    if not lines:
        return "", ""
    first = lines[0].strip()
    rest = "\n".join(lines[1:]).strip()
    return first, rest


def remove_first_line_html(content_html: str, first_line: str) -> str:
    prefix = text_to_html(first_line)
    candidates = (prefix + "<br/>", prefix)
    for candidate in candidates:
        if content_html.startswith(candidate):
            return content_html[len(candidate) :]
    return content_html


def normalize_paragraph_content_html(content_html: str) -> str:
    content_html = re.sub(
        r"^\s*[.．。]\s*(?=(?:理由|代入|因为|因此|所以|可用|可结合|两边|于是|解出|关键结论|在|设|又|由|再由|其中))",
        "",
        content_html,
    )
    if re.fullmatch(r"\s*[.．。]\s*", content_html):
        return ""
    return content_html


def render_paragraph_html(
    *,
    first_block: dict[str, Any],
    content_html: str,
    section_key: str = "",
) -> str:
    raw = paragraph_plain_text(first_block)
    first_line, _rest = split_first_line(raw)
    color = section_color(section_key)
    content_html = normalize_paragraph_content_html(content_html)
    if not content_html.strip():
        return ""

    if first_line in COLORED_SUBHEADINGS:
        body_html = remove_first_line_html(content_html, first_line)
        pieces = [
            f'<p style="margin:16px 0 8px;font-size:18px;line-height:1.45;'
            f'font-weight:700;color:{color};">{escape_text(first_line)}</p>'
        ]
        if body_html:
            pieces.append(
                f'<p style="margin:8px 0 14px;line-height:1.9;color:#111827;">'
                f"{format_inline_labels(body_html, section_key=section_key)}</p>"
            )
        return "".join(pieces)

    if section_key == "examples" and re.match(r"^例\s*\d+", first_line):
        body_html = remove_first_line_html(content_html, first_line)
        pieces = [
            f'<p style="margin:16px 0 8px;font-size:18px;line-height:1.45;'
            f'font-weight:700;color:{color};">{escape_text(first_line)}</p>'
        ]
        if body_html:
            pieces.append(
                f'<p style="margin:6px 0 12px;line-height:1.9;color:#111827;">'
                f"{format_inline_labels(body_html, section_key=section_key)}</p>"
            )
        return "".join(pieces)

    item_match = re.match(
        r"^((?:要点[一二三四五六七八九十]+|步骤[一二三四五六七八九十]+|考法[一二三四五六七八九十]+|场景[一二三四五六七八九十]+|"
        r"条件\s*\d+|易错点[一二三四五六七八九十]*|正确理解|错因分析|第一步|第二步|第三步|第四步|第五步|第六步)"
        r"[^：:]{0,32}(?:[：:]|$))$",
        first_line,
    )
    if item_match:
        body_html = remove_first_line_html(content_html, first_line)
        label = item_match.group(1)
        label_color = paragraph_label_color(section_key, label)
        if body_html:
            return (
                '<p style="margin:14px 0 4px;line-height:1.7;">'
                f'<strong style="font-weight:700;color:{label_color};">{escape_text(label)}</strong></p>'
                '<p style="margin:0 0 12px;padding-left:2.8em;line-height:1.9;color:#111827;">'
                f"{format_inline_labels(body_html, section_key=section_key)}</p>"
            )
        return (
            '<p style="margin:12px 0 8px;line-height:1.8;">'
            f'<strong style="font-weight:700;color:{label_color};">{escape_text(label)}</strong></p>'
        )

    return (
        '<p style="margin:10px 0;line-height:1.9;color:#111827;">'
        + format_inline_labels(content_html, section_key=section_key)
        + "</p>"
    )


def render_formula_image(
    node: dict[str, Any],
    *,
    upload_map: dict[str, str],
    inline: bool,
) -> str:
    asset_url = resolve_asset_url(node)
    wechat_url = upload_map.get(asset_url)
    if not wechat_url:
        latex = str(node.get("latex") or "").strip()
        return (
            f'<code style="font-size:14px;color:#374151;">{escape_text(latex)}</code>'
        )

    asset = node.get("asset") if isinstance(node.get("asset"), dict) else {}
    display_width = (
        int(asset.get("display_width_px") or 0) if isinstance(asset, dict) else 0
    )
    width_style = ""
    if display_width > 0:
        if inline:
            css_width = min(max(round(display_width * 1.05), 12), 180)
        else:
            css_width = min(max(round(display_width * 1.55), 42), 620)
        width_style = f"width:{css_width}px;"
    alt = escape_text(str(node.get("latex") or node.get("alt") or "公式"))
    if inline:
        style = (
            "display:inline-block;vertical-align:-0.42em;"
            "max-width:100%;height:auto;margin:0 2px;line-height:1;" + width_style
        )
        return f'<img src="{html.escape(wechat_url, quote=True)}" alt="{alt}" style="{style}"/>'
    style = (
        "display:block;max-width:100%;height:auto;margin:14px auto 20px;" + width_style
    )
    return f'<img src="{html.escape(wechat_url, quote=True)}" alt="{alt}" style="{style}"/>'


def render_tokens(tokens: Any, *, upload_map: dict[str, str]) -> str:
    if not isinstance(tokens, list):
        return text_to_html(str(tokens or ""))
    pieces: list[str] = []
    for token in tokens:
        if isinstance(token, str):
            pieces.append(text_to_html(token))
            continue
        if not isinstance(token, dict):
            continue
        token_type = str(token.get("type", "text"))
        if token_type == "text":
            pieces.append(text_to_html(str(token.get("text") or "")))
        elif token_type == "line_break":
            pieces.append("<br/>")
        elif token_type in {"math_image", "math_inline", "math_display", "math_block"}:
            pieces.append(
                render_formula_image(token, upload_map=upload_map, inline=True)
            )
        elif token_type == "ref":
            pieces.append(
                text_to_html(str(token.get("text") or token.get("target_id") or ""))
            )
    return "".join(pieces)


def is_paragraph_block(block: Any) -> bool:
    return isinstance(block, dict) and str(block.get("type", "")) == "paragraph"


def is_formula_block(block: Any) -> bool:
    if not isinstance(block, dict):
        return False
    return str(block.get("type", "")) in {
        "math_image",
        "math_block",
        "math_inline",
        "math_display",
    }


def paragraph_plain_text(block: dict[str, Any]) -> str:
    tokens = block.get("tokens")
    if not isinstance(tokens, list):
        return ""
    pieces: list[str] = []
    for token in tokens:
        if isinstance(token, str):
            pieces.append(token)
        elif isinstance(token, dict) and token.get("type") == "text":
            pieces.append(str(token.get("text") or ""))
    return "".join(pieces)


def paragraph_continues_inline_formula(block: dict[str, Any]) -> bool:
    text = paragraph_plain_text(block).strip()
    if not text:
        return False
    if text[0] in "，。；：、,.!?！？":
        return True
    if text[0] in "的得为是在与和及或中上下载由则可后前内外":
        return True
    if len(text) <= 10 and not text.endswith(("：", ":")):
        return True
    return False


def paragraph_opens_display_formula(block: dict[str, Any]) -> bool:
    text = paragraph_plain_text(block).strip()
    return text.endswith(
        (
            "：",
            ":",
            "则",
            "因此",
            "于是",
            "代入",
            "解出",
            "正确公式为",
            "公式为",
            "可结合高",
            "以及关系",
            "满足",
            "关系",
        )
    )


def paragraph_starts_reason(block: dict[str, Any]) -> bool:
    text = paragraph_plain_text(block).strip()
    text = re.sub(r"^[.．。]\s*", "", text)
    return text.startswith("理由")


def formula_has_display_shape(latex: str, compact: str) -> bool:
    return (
        "\\begin{" in latex
        or "\\\\" in latex
        or "\\quad" in latex
        or "\\qquad" in latex
        or "=" in compact
        or len(compact) > 36
    )


def formula_block_should_inline(
    block: dict[str, Any],
    *,
    previous_paragraph: dict[str, Any] | None,
    next_paragraph: dict[str, Any] | None,
    section_key: str = "",
) -> bool:
    latex = str(block.get("latex") or "").strip()
    if not latex:
        return False
    compact = re.sub(r"\s+", "", latex)
    if "\\begin{" in latex or "\\\\" in latex:
        return False
    if previous_paragraph is None and next_paragraph is None:
        return False
    has_display_shape = formula_has_display_shape(latex, compact)
    if has_display_shape and section_key in {"proof", "examples"}:
        return False
    if previous_paragraph is not None and paragraph_opens_display_formula(
        previous_paragraph
    ):
        if has_display_shape or section_key in {"proof", "examples"}:
            return False
    if (
        section_key in {"proof", "examples"}
        and next_paragraph is not None
        and paragraph_starts_reason(next_paragraph)
    ):
        return False
    if has_display_shape and len(compact) > 28:
        return False
    if next_paragraph is not None and paragraph_continues_inline_formula(
        next_paragraph
    ):
        return True
    if "=" not in compact and len(compact) <= 24:
        return True
    if (
        not has_display_shape
        and previous_paragraph is not None
        and next_paragraph is not None
        and len(compact) <= 42
    ):
        return True
    return False


def next_paragraph_after(blocks: list[Any], start_index: int) -> dict[str, Any] | None:
    for block in blocks[start_index + 1 :]:
        if is_paragraph_block(block):
            return block
        if not is_formula_block(block):
            return None
    return None


def render_blocks_sequence(
    blocks: Any,
    *,
    upload_map: dict[str, str],
    section_key: str = "",
) -> str:
    if not isinstance(blocks, list):
        return ""
    pieces: list[str] = []
    index = 0
    while index < len(blocks):
        block = blocks[index]
        if not is_paragraph_block(block):
            if isinstance(block, dict):
                pieces.append(
                    render_block(block, upload_map=upload_map, section_key=section_key)
                )
            index += 1
            continue

        paragraph_parts = [render_tokens(block.get("tokens"), upload_map=upload_map)]
        previous_paragraph = block
        changed = False
        last_was_inline_formula = False
        cursor = index + 1

        while cursor < len(blocks):
            current = blocks[cursor]
            if is_formula_block(current):
                following_paragraph = next_paragraph_after(blocks, cursor)
                if formula_block_should_inline(
                    current,
                    previous_paragraph=previous_paragraph,
                    next_paragraph=following_paragraph,
                    section_key=section_key,
                ):
                    paragraph_parts.append(
                        render_formula_image(
                            current, upload_map=upload_map, inline=True
                        )
                    )
                    changed = True
                    last_was_inline_formula = True
                    cursor += 1
                    continue
                break

            if last_was_inline_formula and is_paragraph_block(current):
                if paragraph_continues_inline_formula(current):
                    paragraph_parts.append(
                        render_tokens(current.get("tokens"), upload_map=upload_map)
                    )
                    previous_paragraph = current
                    last_was_inline_formula = False
                    cursor += 1
                    continue
                break

            break

        if changed:
            pieces.append(
                render_paragraph_html(
                    first_block=block,
                    content_html="".join(paragraph_parts),
                    section_key=section_key,
                )
            )
            index = cursor
        else:
            pieces.append(
                render_block(block, upload_map=upload_map, section_key=section_key)
            )
            index += 1

    return "".join(pieces)


def formula_token_should_display(
    token: dict[str, Any],
    *,
    section_key: str,
    current_plain: str = "",
) -> bool:
    if section_key not in {"proof", "examples"}:
        return False
    latex = str(token.get("latex") or "").strip()
    if not latex:
        return False
    compact = re.sub(r"\s+", "", latex)
    if (
        "\\begin{" in latex
        or "\\\\" in latex
        or "\\quad" in latex
        or "\\qquad" in latex
    ):
        return True
    if "=" not in compact:
        return False
    if len(compact) > 28:
        return True
    text = current_plain.strip()
    return text.endswith(
        (
            "为",
            "为：",
            "得",
            "得：",
            "则",
            "则：",
            "因此",
            "解得",
            "列方程",
            "公式为",
            "半径为",
            "高为",
        )
    )


def render_paragraph_block(
    block: dict[str, Any],
    *,
    upload_map: dict[str, str],
    section_key: str = "",
) -> str:
    tokens = block.get("tokens")
    if not isinstance(tokens, list):
        return render_paragraph_html(
            first_block=block,
            content_html=text_to_html(str(tokens or "")),
            section_key=section_key,
        )

    probe_plain: list[str] = []
    has_display_formula = False
    for token in tokens:
        if isinstance(token, str):
            probe_plain.append(token)
            continue
        if not isinstance(token, dict):
            continue
        token_type = str(token.get("type", "text"))
        if token_type == "text":
            probe_plain.append(str(token.get("text") or ""))
        elif token_type == "line_break":
            probe_plain.append("\n")
        elif token_type in {"math_image", "math_inline", "math_display", "math_block"}:
            if formula_token_should_display(
                token,
                section_key=section_key,
                current_plain="".join(probe_plain),
            ):
                has_display_formula = True
                break
            probe_plain.append(str(token.get("latex") or ""))
        elif token_type == "ref":
            probe_plain.append(str(token.get("text") or token.get("target_id") or ""))

    if not has_display_formula:
        return render_paragraph_html(
            first_block=block,
            content_html=render_tokens(tokens, upload_map=upload_map),
            section_key=section_key,
        )

    pieces: list[str] = []
    html_parts: list[str] = []
    plain_parts: list[str] = []

    def flush_paragraph() -> None:
        if not "".join(html_parts).strip():
            html_parts.clear()
            plain_parts.clear()
            return
        first_block = {
            "type": "paragraph",
            "tokens": [{"type": "text", "text": "".join(plain_parts)}],
        }
        pieces.append(
            render_paragraph_html(
                first_block=first_block,
                content_html="".join(html_parts),
                section_key=section_key,
            )
        )
        html_parts.clear()
        plain_parts.clear()

    for token in tokens:
        if isinstance(token, str):
            html_parts.append(text_to_html(token))
            plain_parts.append(token)
            continue
        if not isinstance(token, dict):
            continue
        token_type = str(token.get("type", "text"))
        if token_type == "text":
            text = str(token.get("text") or "")
            html_parts.append(text_to_html(text))
            plain_parts.append(text)
        elif token_type == "line_break":
            html_parts.append("<br/>")
            plain_parts.append("\n")
        elif token_type in {"math_image", "math_inline", "math_display", "math_block"}:
            if formula_token_should_display(
                token,
                section_key=section_key,
                current_plain="".join(plain_parts),
            ):
                flush_paragraph()
                pieces.append(
                    render_formula_image(token, upload_map=upload_map, inline=False)
                )
            else:
                html_parts.append(
                    render_formula_image(token, upload_map=upload_map, inline=True)
                )
                plain_parts.append(str(token.get("latex") or ""))
        elif token_type == "ref":
            text = str(token.get("text") or token.get("target_id") or "")
            html_parts.append(text_to_html(text))
            plain_parts.append(text)

    flush_paragraph()
    return "".join(pieces)


def render_step_content(
    blocks: Any,
    *,
    upload_map: dict[str, str],
    section_key: str = "",
) -> str:
    return render_blocks_sequence(
        blocks, upload_map=upload_map, section_key=section_key
    )


def render_bullet_list(
    block: dict[str, Any],
    *,
    upload_map: dict[str, str],
    section_key: str = "",
) -> str:
    items = block.get("items")
    if not isinstance(items, list):
        return ""
    lis: list[str] = []
    for item in items:
        if isinstance(item, dict):
            content = render_tokens(item.get("tokens"), upload_map=upload_map)
        else:
            content = text_to_html(str(item))
        lis.append(
            f'<li style="margin:7px 0;line-height:1.9;color:#111827;">'
            f"{format_inline_labels(content, section_key=section_key)}</li>"
        )
    return '<ul style="padding-left:1.2em;margin:8px 0 12px;">' + "".join(lis) + "</ul>"


def theorem_formula_should_display(token: dict[str, Any]) -> bool:
    latex = str(token.get("latex") or "").strip()
    if not latex:
        return False
    compact = latex.replace(" ", "")
    if "\\begin{" in latex or "\\\\" in latex:
        return True
    if "=" in compact or "\\quad" in latex or "\\qquad" in latex:
        return True
    return len(compact) > 28


def render_theorem_desc(
    tokens: Any,
    *,
    upload_map: dict[str, str],
    with_label: bool,
) -> str:
    color = section_color("statement")
    if not isinstance(tokens, list):
        text = text_to_html(str(tokens or ""))
        if with_label:
            return (
                '<p style="margin:6px 0 10px;padding-left:2.8em;line-height:1.9;">'
                f'<strong style="color:{color};">直观描述：</strong> '
                f"{text}</p>"
            )
        return f'<p style="margin:6px 0 10px;line-height:1.9;">{text}</p>'

    paragraphs: list[str] = []
    inline_parts: list[str] = []

    def flush_inline() -> None:
        if not inline_parts:
            return
        content = "".join(inline_parts)
        if with_label and not content.rstrip().endswith(
            ("。", "，", "；", "：", ".", "!", "?", "！", "？")
        ):
            content += "。"
        prefix = ""
        padding = "padding-left:2.8em;"
        if with_label:
            prefix = f'<strong style="color:{color};">直观描述：</strong> '
            padding = "padding-left:2.8em;"
        paragraphs.append(
            f'<p style="margin:6px 0 10px;{padding}line-height:1.9;">'
            + prefix
            + content
            + "</p>"
        )
        inline_parts.clear()

    for token in tokens:
        if isinstance(token, str):
            inline_parts.append(text_to_html(token))
            continue
        if not isinstance(token, dict):
            continue
        token_type = str(token.get("type", "text"))
        if token_type == "text":
            inline_parts.append(text_to_html(str(token.get("text") or "")))
            continue
        if token_type == "line_break":
            inline_parts.append("<br/>")
            continue
        if token_type in {"math_image", "math_inline", "math_display", "math_block"}:
            if theorem_formula_should_display(token):
                flush_inline()
                paragraphs.append(
                    '<section style="margin:10px 0 22px;text-align:center;">'
                    + render_formula_image(token, upload_map=upload_map, inline=False)
                    + "</section>"
                )
            else:
                inline_parts.append(
                    render_formula_image(token, upload_map=upload_map, inline=True)
                )
            continue
        if token_type == "ref":
            inline_parts.append(
                text_to_html(str(token.get("text") or token.get("target_id") or ""))
            )

    flush_inline()
    return "".join(paragraphs)


def render_theorem_group(block: dict[str, Any], *, upload_map: dict[str, str]) -> str:
    items = block.get("items")
    if not isinstance(items, list):
        return ""
    color = section_color("statement")
    pieces: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        title = escape_text(str(item.get("title") or "结论"))
        is_conclusion_item = "结论" in str(item.get("title") or "")
        desc = render_theorem_desc(
            item.get("desc_tokens"),
            upload_map=upload_map,
            with_label=is_conclusion_item,
        )
        pieces.append(
            '<section style="margin:18px 0 26px;">'
            f'<p style="margin:0 0 8px;font-size:17px;line-height:1.5;'
            f'font-weight:700;color:{color};">{title}</p>'
            f"{desc}"
            "</section>"
        )
    return "".join(pieces)


def render_proof_steps(
    block: dict[str, Any],
    *,
    upload_map: dict[str, str],
    section_key: str = "",
) -> str:
    steps = block.get("steps")
    if not isinstance(steps, list):
        return ""
    pieces: list[str] = []
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            continue
        title = escape_text(str(step.get("title") or f"步骤 {index}"))
        content = render_step_content(
            step.get("content"),
            upload_map=upload_map,
            section_key=section_key,
        )
        pieces.append(
            '<section style="margin:14px 0 18px;">'
            f'<p style="margin:0 0 8px;font-size:17px;line-height:1.5;'
            f'font-weight:700;color:#111827;">{title}</p>'
            f"{content}</section>"
        )
    return "".join(pieces)


def render_example(
    block: dict[str, Any],
    *,
    upload_map: dict[str, str],
    section_key: str = "",
) -> str:
    color = section_color("examples")
    title = escape_text(str(block.get("title") or "例题"))
    problem = render_step_content(
        block.get("problem"), upload_map=upload_map, section_key=section_key
    )
    solution = render_step_content(
        block.get("solution"), upload_map=upload_map, section_key=section_key
    )
    answer = render_step_content(
        block.get("answer"), upload_map=upload_map, section_key=section_key
    )
    body = (
        f'<p style="margin:0 0 6px;font-weight:700;color:{color};">题目：</p>'
        + problem
        + f'<p style="margin:10px 0 6px;font-weight:700;color:{color};">解题步骤：</p>'
        + solution
    )
    if answer:
        body += (
            f'<p style="margin:10px 0 6px;font-weight:700;color:{color};">关键结论：</p>'
            + answer
        )
    return (
        '<section style="margin:16px 0 22px;">'
        f'<p style="margin:0 0 8px;font-size:17px;line-height:1.5;'
        f'font-weight:700;color:{color};">{title}</p>'
        f"{body}</section>"
    )


def render_block(
    block: dict[str, Any],
    *,
    upload_map: dict[str, str],
    section_key: str = "",
) -> str:
    block_type = str(block.get("type", "paragraph"))
    if block_type == "paragraph":
        return render_paragraph_block(
            block, upload_map=upload_map, section_key=section_key
        )
    if block_type in {"math_image", "math_block", "math_inline"}:
        return render_formula_image(block, upload_map=upload_map, inline=False)
    if block_type == "image_block":
        return render_formula_image(block, upload_map=upload_map, inline=False)
    if block_type == "bullet_list":
        return render_bullet_list(block, upload_map=upload_map, section_key=section_key)
    if block_type == "theorem_group":
        return render_theorem_group(block, upload_map=upload_map)
    if block_type == "proof_steps":
        return render_proof_steps(block, upload_map=upload_map, section_key=section_key)
    if block_type == "warning":
        title = escape_text(str(block.get("title") or "提醒"))
        content = render_step_content(
            block.get("content"), upload_map=upload_map, section_key=section_key
        )
        title_color = (
            section_color(section_key) if section_key == "traps" else "#111827"
        )
        return (
            '<section style="margin:14px 0 18px;">'
            f'<p style="margin:0 0 8px;font-size:17px;line-height:1.5;'
            f'font-weight:700;color:{title_color};">{title}</p>'
            f"{content}</section>"
        )
    if block_type == "summary_box":
        title = escape_text(str(block.get("title") or "总结"))
        content = render_step_content(
            block.get("content"), upload_map=upload_map, section_key=section_key
        )
        title_color = (
            section_color(section_key) if section_key == "summary" else "#111827"
        )
        return (
            '<section style="margin:14px 0 18px;">'
            f'<p style="margin:0 0 8px;font-size:17px;line-height:1.5;'
            f'font-weight:700;color:{title_color};">{title}</p>'
            f"{content}</section>"
        )
    if block_type == "example":
        return render_example(block, upload_map=upload_map, section_key=section_key)
    if block_type == "divider":
        return '<hr style="border:0;border-top:1px solid #ece7dc;margin:18px 0;"/>'
    return ""


def render_minicode_cta(
    *,
    record: dict[str, Any],
    item_id: str,
    upload_map: dict[str, str],
) -> str:
    wechat_url = upload_map.get(MINICODE_ASSET_URL, "")
    if not wechat_url:
        return ""
    title = record_body_title(record)
    return (
        '<section style="margin:28px 0 4px;padding:18px 16px;'
        "background:#F7F5EF;border:1px solid #D6CAB8;"
        'border-left:4px solid #8D6E63;border-radius:6px;text-align:center;">'
        '<p style="margin:0 0 6px;font-size:18px;line-height:1.45;'
        'font-weight:700;color:#5D4037;">去小程序拿高清 PDF</p>'
        '<p style="margin:0 auto 14px;max-width:30em;text-align:left;'
        'line-height:1.8;color:#374151;">'
        "想查更多高中数学二级结论，可以在公众号后台回复：数秒查<br/>"
        "长按识别小程序码，进入数秒查小程序。可下载本文高清 PDF<br/>"
        "进入小程序后可直接搜索关键词，例如：<br/>"
        "圆锥曲线、向量、外接球、不等式、导数、三角函数、数列"
        "</p>"
        f'<img src="{html.escape(wechat_url, quote=True)}" alt="ok-shuxue小程序码" '
        'style="display:block;width:176px;max-width:62%;height:auto;margin:0 auto 10px;"/>'
        '<p style="margin:0;color:#6b7280;font-size:13px;line-height:1.7;">'
        f"可搜索：{escape_text(item_id)} · {escape_text(title)}"
        "</p>"
        "</section>"
    )


def render_article_html(
    record: dict[str, Any],
    *,
    item_id: str,
    config: DraftConfig,
    upload_map: dict[str, str],
) -> str:
    title = record_body_title(record)
    content = record.get("content") if isinstance(record.get("content"), dict) else {}
    sections = (
        content.get("sections") if isinstance(content.get("sections"), list) else []
    )
    wanted = set(config.section_keys)
    body: list[str] = [
        '<section style="max-width:677px;margin:0 auto;padding:0 0 16px;'
        'font-size:16px;line-height:1.85;color:#1f2933;">',
        f'<h1 style="font-size:22px;line-height:1.35;margin:0 0 18px;color:#111827;">{escape_text(title)}</h1>',
    ]

    for section in sections:
        if not isinstance(section, dict):
            continue
        key = str(section.get("key") or "")
        if key not in wanted:
            continue
        blocks = (
            section.get("blocks") if isinstance(section.get("blocks"), list) else []
        )
        section_content = render_blocks_sequence(
            blocks,
            upload_map=upload_map,
            section_key=key,
        )
        box_style = SECTION_BOX_STYLES.get(key)
        if box_style:
            section_title = escape_text(
                str(box_style.get("title") or section.get("title") or key)
            )
            color = str(box_style["color"])
            bg = str(box_style["bg"])
            left_border = "4px" if box_style.get("west") else "1px"
            body_padding = "16px 18px 20px" if key == "summary" else "14px 18px 18px"
            body.append(
                f'<section style="margin:22px 0;border:1px solid {color};'
                f"border-left:{left_border} solid {color};"
                f'background:{bg};border-radius:6px;overflow:hidden;">'
                f'<p style="margin:0;padding:8px 16px;background:{color};'
                f'color:#ffffff;font-size:20px;line-height:1.35;font-weight:700;">'
                f"{section_title}</p>"
                f'<section style="padding:{body_padding};">{section_content}</section>'
                "</section>"
            )
        else:
            section_title = escape_text(str(section.get("title") or key))
            body.append(
                '<section style="margin:22px 0 0;">'
                f'<h2 style="font-size:18px;line-height:1.4;margin:0 0 10px;'
                f'color:#164554;border-bottom:1px solid #e5e7eb;padding-bottom:6px;">{section_title}</h2>'
                f"{section_content}</section>"
            )

    body.append(
        render_minicode_cta(record=record, item_id=item_id, upload_map=upload_map)
    )
    body.append("</section>")
    return "".join(body)


def render_content_source_url(
    template: str,
    *,
    item_id: str,
    record: dict[str, Any],
    pdf_map: dict[str, Any],
) -> str:
    if not template:
        return ""
    pdf_name = str(pdf_map.get(item_id) or "")
    try:
        return template.format(
            id=item_id, pdf=pdf_name, title=public_article_title(record, item_id)
        )
    except Exception as exc:
        raise DraftError(f"Invalid --content-source-url-template: {exc}") from exc


def build_article_payload(
    *,
    record: dict[str, Any],
    item_id: str,
    html_content: str,
    thumb_media_id: str,
    config: DraftConfig,
    pdf_map: dict[str, Any],
) -> dict[str, Any]:
    article = {
        "title": public_article_title(record, item_id),
        "digest": public_article_digest(record, item_id),
        "content": html_content,
        "content_source_url": render_content_source_url(
            config.content_source_url_template,
            item_id=item_id,
            record=record,
            pdf_map=pdf_map,
        ),
        "thumb_media_id": thumb_media_id,
        "need_open_comment": config.need_open_comment,
        "only_fans_can_comment": config.only_fans_can_comment,
    }
    if config.author:
        article["author"] = truncate_text(config.author, 8)
    return article


def process_one_item(
    *,
    item_id: str,
    record: dict[str, Any],
    config: DraftConfig,
    access_token: str,
    upload_cache: dict[str, Any],
    pdf_map: dict[str, Any],
) -> DraftItemReport:
    item_output_dir = config.output_dir / item_id
    item_output_dir.mkdir(parents=True, exist_ok=True)
    title = public_article_title(record, item_id)
    cover_path = item_output_dir / f"cover_{COVER_LAYOUT_VERSION}.png"
    report = DraftItemReport(
        id=item_id,
        title=title,
        status="started",
        output_dir=str(item_output_dir),
        cover_path=str(cover_path),
    )

    generate_cover(
        record=record, item_id=item_id, config=config, output_path=cover_path
    )
    thumb_media_id, cover_cached = upload_cover_material(
        config=config.wechat,
        access_token=access_token,
        cover_path=cover_path,
        upload_cache=upload_cache,
    )
    report.cover_cached_upload = cover_cached
    report.thumb_media_id = thumb_media_id

    image_refs = collect_article_image_refs(record, config.public_dir)
    upload_map: dict[str, str] = {}
    image_uploads: list[ImageUpload] = []
    for asset_url, local_path in image_refs.items():
        wechat_url, digest, cached = upload_article_image(
            config=config.wechat,
            access_token=access_token,
            path=local_path,
            upload_cache=upload_cache,
        )
        upload_map[asset_url] = wechat_url
        image_uploads.append(
            ImageUpload(
                asset_url=asset_url,
                local_path=str(local_path),
                sha256=digest,
                wechat_url=wechat_url,
                cached=cached,
            )
        )

    html_content = render_article_html(
        record,
        item_id=item_id,
        config=config,
        upload_map=upload_map,
    )
    if len(html_content) > 19000:
        report.warnings.append(
            f"HTML content length is {len(html_content)} chars; WeChat may reject overly long content."
        )

    article = build_article_payload(
        record=record,
        item_id=item_id,
        html_content=html_content,
        thumb_media_id=thumb_media_id,
        config=config,
        pdf_map=pdf_map,
    )

    article_html_path = item_output_dir / "article.html"
    payload_path = item_output_dir / "draft_payload.json"
    manifest_path = item_output_dir / "asset_manifest.json"
    article_html_path.write_text(html_content, encoding="utf-8")
    write_json(payload_path, {"articles": [article]})
    write_json(
        manifest_path,
        {
            "id": item_id,
            "title": title,
            "cover": {
                "path": str(cover_path),
                "thumb_media_id": thumb_media_id,
                "cached_upload": cover_cached,
            },
            "article_images": [asdict(item) for item in image_uploads],
            "content_length": len(html_content),
        },
    )

    media_id = add_wechat_draft(
        config=config.wechat,
        access_token=access_token,
        article=article,
    )

    report.article_media_id = media_id
    report.article_html = str(article_html_path)
    report.draft_payload = str(payload_path)
    report.asset_manifest = str(manifest_path)
    report.image_uploads = [asdict(item) for item in image_uploads]
    report.status = "success"
    return report


def orchestrate(config: DraftConfig) -> dict[str, Any]:
    canonical = read_json(config.canonical_path)
    if not isinstance(canonical, dict):
        raise DraftError(f"Canonical JSON must be an object: {config.canonical_path}")
    pdf_map = read_json(config.pdf_map_path, default={})
    if not isinstance(pdf_map, dict):
        pdf_map = {}

    selected_raw = {item_id: canonical[item_id] for item_id in config.ids}
    selected = render_formula_assets_for_records(records=selected_raw, config=config)

    access_token = get_access_token(config.wechat)
    upload_cache = load_cache(config.wechat.upload_cache_path)

    report: dict[str, Any] = {
        "generated_at": now_iso(),
        "ids": list(config.ids),
        "canonical": str(config.canonical_path),
        "output_dir": str(config.output_dir),
        "items": [],
        "warnings": [],
    }

    try:
        for item_id in config.ids:
            LOGGER.info("Creating WeChat draft | %s", item_id)
            record = selected.get(item_id)
            if not isinstance(record, dict):
                raise DraftError(f"Rendered canonical missing ID: {item_id}")
            try:
                item_report = process_one_item(
                    item_id=item_id,
                    record=record,
                    config=config,
                    access_token=access_token,
                    upload_cache=upload_cache,
                    pdf_map=pdf_map,
                )
            except Exception as exc:
                item_report = DraftItemReport(
                    id=item_id,
                    title=public_article_title(record, item_id),
                    status="failed",
                    output_dir=str(config.output_dir / item_id),
                    cover_path=str(
                        config.output_dir
                        / item_id
                        / f"cover_{COVER_LAYOUT_VERSION}.png"
                    ),
                    error=str(exc),
                )
                report["items"].append(asdict(item_report))
                raise
            report["items"].append(asdict(item_report))
    finally:
        save_cache(config.wechat.upload_cache_path, upload_cache)
        write_json(config.report_path, report)

    return report


def main() -> int:
    configure_console_encoding()
    args = parse_args()
    try:
        config = build_config(args)
        configure_logging(config.log_level)
        LOGGER.info("Draft target IDs | %s", ", ".join(config.ids))
        report = orchestrate(config)
        success_count = sum(
            1 for item in report["items"] if item.get("status") == "success"
        )
        LOGGER.info(
            "WeChat draft generation complete | success=%d/%d | report=%s",
            success_count,
            len(config.ids),
            config.report_path,
        )
        return 0
    except DraftError as exc:
        LOGGER.error("%s", exc)
        return 1
    except KeyboardInterrupt:
        LOGGER.error("Interrupted by user.")
        return 130
    except Exception:
        LOGGER.exception("Unexpected WeChat draft generation failure")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
