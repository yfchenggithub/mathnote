#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate a WeChat Channels image-post package for selected conclusion IDs and
optionally open Channels Assistant for draft filling.

The script intentionally keeps final publishing manual. It prepares a concise
multi-image post, uploads/fills what it can through a local Chrome session, and
leaves the user to review and click publish.

Examples:
    python scripts/channels_publish_assistant.py G003 --package-only
    python scripts/channels_publish_assistant.py G003
    python scripts/channels_publish_assistant.py G003 --card-size 1080x1440
"""

from __future__ import annotations

import argparse
import html
import json
import logging
import os
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

DEFAULT_CANONICAL_PATH = PROJECT_ROOT / "data" / "content" / "canonical_content_v2.json"
DEFAULT_PUBLIC_DIR = PROJECT_ROOT / "public"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "build" / "channels_posts"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports" / "channels_publish_assistant_report.json"
DEFAULT_MINICODE_PATH = PROJECT_ROOT / "assets" / "figures" / "MiniCode.png"
DEFAULT_CHROME_PATH = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
DEFAULT_PROFILE_DIR = PROJECT_ROOT / "build" / "channels_chrome_profile"
DEFAULT_CHANNELS_URL = "https://channels.weixin.qq.com/"
DEFAULT_CARD_SIZE = "1080x1440"
DEFAULT_CARD_DPR = 1.0
DEFAULT_MUSIC_QUERY = "\u65f6\u5149\u9759\u597d"
ID_PATTERN = re.compile(r"^[A-Za-z]\d{3}$")
LOGGER = logging.getLogger("channels_publish_assistant")

SECTION_TITLES = {
    "core_formula": "核心公式",
    "conditions": "适用条件",
    "statement": "命题表述",
    "explanation": "理解与直觉",
    "proof": "证明过程",
    "examples": "例题应用",
    "traps": "易错提醒",
    "summary": "复盘总结",
}

CARD_ACCENTS = {
    "cover": "#15616D",
    "intro": "#15616D",
    "core": "#2F6F3E",
    "explanation": "#315A7D",
    "proof": "#6A4C93",
    "examples": "#8A5A1F",
    "traps": "#9B2C2C",
    "summary": "#3A6B58",
    "minicode": "#146B52",
}

CHANNELS_FIXED_TOPICS = ("高中数学", "高考数学", "二级结论")
HEADING_ONLY_PATTERN = re.compile(
    r"^(一句话直觉|一句话核心|核心拆解|思路提示|正式推导|使用条件|关键公式|考点价值|顿悟点|使用场景|"
    r"例\s*\d+.*|易错点[一二三四五六七八九十]?.*)$"
)


class ChannelsAssistantError(RuntimeError):
    """Readable error for expected assistant failures."""


@dataclass(frozen=True)
class Config:
    ids: tuple[str, ...]
    canonical_path: Path
    public_dir: Path
    output_dir: Path
    report_path: Path
    minicode_path: Path
    chrome_path: Path
    profile_dir: Path
    channels_url: str
    card_size: tuple[int, int]
    card_dpr: float
    music_query: str
    package_only: bool
    force: bool
    editor_wait_sec: int
    review_wait_sec: int
    log_level: str


@dataclass(frozen=True)
class CardSpec:
    slug: str
    filename: str
    title: str
    subtitle: str
    body_html: str
    accent: str
    footer: str


@dataclass
class PackageResult:
    id: str
    title: str
    output_dir: str
    cards_dir: str
    cover_path: str
    card_paths: list[str]
    caption_path: str
    manifest_path: str
    preview_html_path: str
    checklist_path: str
    post_payload_path: str
    card_count: int
    status: str = "success"
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


def parse_size(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"\s*(\d+)x(\d+)\s*", value.lower())
    if not match:
        raise argparse.ArgumentTypeError("expected size like 1080x1440")
    width = int(match.group(1))
    height = int(match.group(2))
    if width < 360 or height < 480:
        raise argparse.ArgumentTypeError("card size is too small")
    return width, height


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and optionally fill a WeChat Channels image post.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/channels_publish_assistant.py G003 --package-only\n"
            "  python scripts/channels_publish_assistant.py G003\n"
            "  python scripts/channels_publish_assistant.py G003 --card-size 1080x1440\n"
        ),
    )
    parser.add_argument("ids", nargs="+", help="Conclusion IDs, e.g. G003 or G003,T008.")
    parser.add_argument("--canonical-json", default=str(DEFAULT_CANONICAL_PATH))
    parser.add_argument("--public-dir", default=str(DEFAULT_PUBLIC_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--report", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--minicode", default=str(DEFAULT_MINICODE_PATH))
    parser.add_argument("--chrome", default=str(DEFAULT_CHROME_PATH))
    parser.add_argument("--profile-dir", default=str(DEFAULT_PROFILE_DIR))
    parser.add_argument("--channels-url", default=DEFAULT_CHANNELS_URL)
    parser.add_argument("--card-size", type=parse_size, default=parse_size(DEFAULT_CARD_SIZE))
    parser.add_argument("--card-dpr", type=float, default=DEFAULT_CARD_DPR)
    parser.add_argument(
        "--music",
        default=DEFAULT_MUSIC_QUERY,
        help="Music keyword to search/select in Channels Assistant. Default: 时光静好.",
    )
    parser.add_argument(
        "--package-only",
        action="store_true",
        help="Only generate files. Do not open Chrome or fill Channels Assistant.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate card images even if output files already exist.",
    )
    parser.add_argument(
        "--editor-wait-sec",
        type=int,
        default=0,
        help="Seconds to wait for Channels Assistant after login. 0 means wait forever. Default: 0.",
    )
    parser.add_argument(
        "--review-wait-sec",
        type=int,
        default=600,
        help="Seconds to keep Chrome open after filling. Default: 600.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
    )
    return parser.parse_args()


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


def normalize_ids(raw_values: Sequence[str]) -> tuple[str, ...]:
    normalized: list[str] = []
    invalid: list[str] = []
    for raw in split_csv_tokens(raw_values):
        value = raw.upper()
        if ID_PATTERN.fullmatch(value):
            normalized.append(value)
        else:
            invalid.append(raw)
    if invalid:
        raise ChannelsAssistantError(
            "Invalid conclusion ID(s): "
            + ", ".join(invalid)
            + ". Expected values like G003."
        )
    ids = tuple(dedupe_keep_order(normalized))
    if not ids:
        raise ChannelsAssistantError("At least one conclusion ID is required.")
    return ids


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        if default is not None:
            return default
        raise ChannelsAssistantError(f"JSON file not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ChannelsAssistantError(f"Invalid JSON in {path}: {exc}") from exc


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def build_config(args: argparse.Namespace, canonical: dict[str, Any]) -> Config:
    ids = normalize_ids(args.ids)
    missing = [item_id for item_id in ids if item_id not in canonical]
    if missing:
        raise ChannelsAssistantError(
            "Conclusion ID(s) not found in canonical JSON: " + ", ".join(missing)
        )
    return Config(
        ids=ids,
        canonical_path=Path(args.canonical_json).resolve(),
        public_dir=Path(args.public_dir).resolve(),
        output_dir=Path(args.output_dir).resolve(),
        report_path=Path(args.report).resolve(),
        minicode_path=Path(args.minicode).resolve(),
        chrome_path=Path(args.chrome).resolve(),
        profile_dir=Path(args.profile_dir).resolve(),
        channels_url=str(args.channels_url),
        card_size=args.card_size,
        card_dpr=max(1.0, float(args.card_dpr)),
        music_query=clean_text(args.music) or DEFAULT_MUSIC_QUERY,
        package_only=bool(args.package_only),
        force=bool(args.force),
        editor_wait_sec=max(0, int(args.editor_wait_sec)),
        review_wait_sec=max(0, int(args.review_wait_sec)),
        log_level=str(args.log_level).upper(),
    )


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def clean_text(text: Any) -> str:
    return " ".join(str(text or "").split())


def truncate_text(text: str, limit: int) -> str:
    normalized = clean_text(text)
    if len(normalized) <= limit:
        return normalized
    if limit <= 1:
        return normalized[:limit]
    return normalized[: limit - 1].rstrip() + "…"


def record_meta(record: dict[str, Any]) -> dict[str, Any]:
    meta = record.get("meta")
    return meta if isinstance(meta, dict) else {}


def record_title(record: dict[str, Any], item_id: str) -> str:
    title = str(record_meta(record).get("title") or record.get("title") or item_id).strip()
    return title or item_id


def record_summary(record: dict[str, Any]) -> str:
    meta = record_meta(record)
    content = record.get("content") if isinstance(record.get("content"), dict) else {}
    plain = content.get("plain") if isinstance(content.get("plain"), dict) else {}
    return str(meta.get("summary") or plain.get("summary") or "").strip()


def record_category(record: dict[str, Any]) -> str:
    return str(record_meta(record).get("category") or "").strip()


def record_tags(record: dict[str, Any]) -> list[str]:
    raw_tags = record_meta(record).get("tags")
    if not isinstance(raw_tags, list):
        return []
    return [clean_text(tag) for tag in raw_tags if clean_text(tag)]


def record_aliases(record: dict[str, Any]) -> list[str]:
    raw_aliases = record_meta(record).get("aliases")
    if not isinstance(raw_aliases, list):
        return []
    return [clean_text(alias) for alias in raw_aliases if clean_text(alias)]


def channels_title(record: dict[str, Any], item_id: str) -> str:
    return truncate_text(f"高中数学二级结论 {item_id}：{record_title(record, item_id)}", 64)


def channels_image_title(record: dict[str, Any], item_id: str) -> str:
    title = record_title(record, item_id)
    compact = re.sub(r"\s+", "", title)
    short = re.split(r"[：:]", compact, maxsplit=1)[0].strip()
    candidates = [short, compact, *record_aliases(record)]
    for candidate in candidates:
        value = clean_text(candidate)
        if value and len(f"{item_id} {value}") <= 22:
            return f"{item_id} {value}"
    return f"{item_id} {compact}"[:22]


def channels_topics(record: dict[str, Any]) -> list[str]:
    candidates = [
        *CHANNELS_FIXED_TOPICS,
        record_category(record),
        *record_tags(record),
        *record_aliases(record),
    ]
    topics: list[str] = []
    for value in candidates:
        topic = clean_text(value)
        if not topic:
            continue
        topic = re.sub(r"\s+", "", topic)
        if len(topic) > 18:
            continue
        topics.append(topic)
    return dedupe_keep_order(topics)[:8]


def find_section(record: dict[str, Any], key: str) -> dict[str, Any] | None:
    content = record.get("content") if isinstance(record.get("content"), dict) else {}
    sections = content.get("sections") if isinstance(content.get("sections"), list) else []
    for section in sections:
        if isinstance(section, dict) and str(section.get("key") or "") == key:
            return section
    return None


def resolve_asset_url(node: dict[str, Any]) -> str:
    asset = node.get("asset") if isinstance(node.get("asset"), dict) else {}
    for key in ("png", "webp", "src", "url"):
        value = asset.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for key in ("src", "url", "asset_url"):
        value = node.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def local_asset_path(public_dir: Path, asset_url: str) -> Path | None:
    value = str(asset_url or "").strip()
    if not value or re.match(r"^https?://", value, flags=re.I):
        return None
    normalized = value.lstrip("/").replace("/", os.sep)
    return public_dir / normalized


def asset_uri(public_dir: Path, asset_url: str) -> str:
    path = local_asset_path(public_dir, asset_url)
    if path and path.is_file():
        return path.resolve().as_uri()
    return ""


def token_latex_text(latex: str) -> str:
    value = str(latex or "").strip()
    return value if value else ""


def plain_from_tokens(tokens: Any) -> str:
    if not isinstance(tokens, list):
        return clean_text(tokens)
    pieces: list[str] = []
    for token in tokens:
        if isinstance(token, str):
            pieces.append(token)
            continue
        if not isinstance(token, dict):
            continue
        token_type = str(token.get("type") or "text")
        if token_type == "text":
            pieces.append(str(token.get("text") or ""))
        elif token_type == "line_break":
            pieces.append("\n")
        elif token_type in {"math_inline", "math_display", "math_block", "math_image"}:
            pieces.append(token_latex_text(str(token.get("latex") or "")))
        elif token_type == "ref":
            pieces.append(str(token.get("text") or token.get("target_id") or ""))
    return "".join(pieces).strip()


def block_plain_text(block: dict[str, Any]) -> str:
    block_type = str(block.get("type") or "")
    if block_type == "paragraph":
        return plain_from_tokens(block.get("tokens"))
    if block_type in {"math_image", "math_inline", "math_display", "math_block"}:
        return token_latex_text(str(block.get("latex") or ""))
    if block_type == "theorem_group":
        pieces: list[str] = []
        items = block.get("items") if isinstance(block.get("items"), list) else []
        for item in items:
            if not isinstance(item, dict):
                continue
            pieces.append(str(item.get("title") or ""))
            pieces.append(plain_from_tokens(item.get("desc_tokens")))
        return "\n".join(piece for piece in pieces if piece)
    return clean_text(block.get("text") or block.get("latex") or "")


def block_weight(block: dict[str, Any]) -> int:
    block_type = str(block.get("type") or "")
    if block_type == "theorem_group":
        return max(160, len(block_plain_text(block)) // 2)
    if block_type in {"math_image", "math_inline", "math_display", "math_block"}:
        return 90
    text_len = len(block_plain_text(block))
    return max(40, text_len)


def render_math_html(
    node: dict[str, Any],
    *,
    public_dir: Path,
    inline: bool,
) -> str:
    latex = str(node.get("latex") or "").strip()
    url = resolve_asset_url(node)
    src = asset_uri(public_dir, url)
    if not src:
        text = html.escape(latex or "公式", quote=False)
        tag = "span" if inline else "div"
        return f'<{tag} class="math-text">{text}</{tag}>'

    asset = node.get("asset") if isinstance(node.get("asset"), dict) else {}
    display_width = int(asset.get("display_width_px") or 0) if isinstance(asset, dict) else 0
    display_height = int(asset.get("display_height_px") or 0) if isinstance(asset, dict) else 0
    if inline:
        css_width = min(max(round(display_width * 1.55), 22), 240) if display_width else 48
        cls = "math-img inline"
    else:
        is_display_formula = (
            display_height >= 30
            or "\\frac" in latex
            or "\\sqrt" in latex
            or "\\begin" in latex
        )
        scale = 2.45 if is_display_formula else 1.75
        min_width = 115 if is_display_formula else 38
        css_width = min(max(round(display_width * scale), min_width), 660) if display_width else 170
        cls = "math-img block"
    alt = html.escape(latex or "公式", quote=True)
    return f'<img class="{cls}" src="{html.escape(src, quote=True)}" alt="{alt}" style="width:{css_width}px;"/>'


def render_tokens_html(tokens: Any, *, public_dir: Path) -> str:
    if not isinstance(tokens, list):
        return html.escape(str(tokens or ""), quote=False)
    pieces: list[str] = []
    for token in tokens:
        if isinstance(token, str):
            pieces.append(html.escape(token, quote=False))
            continue
        if not isinstance(token, dict):
            continue
        token_type = str(token.get("type") or "text")
        if token_type == "text":
            pieces.append(html.escape(str(token.get("text") or ""), quote=False))
        elif token_type == "line_break":
            pieces.append("<br/>")
        elif token_type in {"math_inline", "math_display", "math_block", "math_image"}:
            pieces.append(render_math_html(token, public_dir=public_dir, inline=True))
        elif token_type == "ref":
            pieces.append(
                html.escape(str(token.get("text") or token.get("target_id") or ""), quote=False)
            )
    return "".join(pieces)


def render_paragraph_html(block: dict[str, Any], *, public_dir: Path) -> str:
    heading, content = paragraph_heading_and_body(block, public_dir=public_dir)
    if heading:
        return (
            f'<p class="minor-heading">{html.escape(heading, quote=False)}</p>'
            f'<p>{content}</p>'
        )
    return f"<p>{content}</p>"


def paragraph_heading_and_body(
    block: dict[str, Any], *, public_dir: Path
) -> tuple[str, str]:
    text = plain_from_tokens(block.get("tokens"))
    content = render_tokens_html(block.get("tokens"), public_dir=public_dir)
    first_line = text.splitlines()[0].strip() if text else ""
    has_body_after_heading = "\n" in text and len(first_line) <= 18
    heading_only = bool(first_line) and "\n" not in text and (
        (len(first_line) <= 24 and first_line.endswith(("：", ":")))
        or bool(HEADING_ONLY_PATTERN.fullmatch(first_line))
    )
    if not (has_body_after_heading or heading_only):
        return "", content
    escaped_heading = html.escape(first_line, quote=False)
    if heading_only:
        return first_line, ""
    body = content.replace(escaped_heading, "", 1)
    body = re.sub(r"^(?:\s|<br\s*/?>)+", "", body)
    return first_line, body


def is_math_block(block: Any) -> bool:
    return isinstance(block, dict) and str(block.get("type") or "") in {
        "math_image",
        "math_inline",
        "math_display",
        "math_block",
    }


def is_inline_sized_math_block(block: dict[str, Any]) -> bool:
    if not is_math_block(block):
        return False
    latex = str(block.get("latex") or "")
    if "\\begin" in latex or "\\frac" in latex or "\\sqrt" in latex:
        return False
    asset = block.get("asset") if isinstance(block.get("asset"), dict) else {}
    display_width = int(asset.get("display_width_px") or 0) if isinstance(asset, dict) else 0
    display_height = int(asset.get("display_height_px") or 0) if isinstance(asset, dict) else 0
    if not display_width and not display_height:
        return len(latex) <= 24
    return display_width <= 180 and display_height <= 26


def append_inline_piece(pieces: list[str], piece: str) -> None:
    if not piece:
        return
    if pieces:
        pieces.append(" ")
    pieces.append(piece)


def render_compact_unit(
    blocks: list[Any], index: int, *, public_dir: Path
) -> tuple[str, int, int, int]:
    block = blocks[index]
    if not isinstance(block, dict):
        return "", index + 1, 0, 1
    if str(block.get("type") or "") != "paragraph":
        return render_block_html(block, public_dir=public_dir), index + 1, block_weight(block), 1

    heading, body = paragraph_heading_and_body(block, public_dir=public_dir)
    pieces: list[str] = []
    append_inline_piece(pieces, body)
    weight = block_weight(block)
    consumed = 1
    next_index = index + 1

    while next_index < len(blocks):
        next_block = blocks[next_index]
        if not isinstance(next_block, dict):
            break
        next_type = str(next_block.get("type") or "")
        if is_inline_sized_math_block(next_block):
            append_inline_piece(
                pieces,
                render_math_html(next_block, public_dir=public_dir, inline=True),
            )
            weight += block_weight(next_block)
            consumed += 1
            next_index += 1
            continue
        if next_type == "paragraph":
            next_heading, next_body = paragraph_heading_and_body(
                next_block, public_dir=public_dir
            )
            if next_heading:
                break
            append_inline_piece(pieces, next_body)
            weight += block_weight(next_block)
            consumed += 1
            next_index += 1
            continue
        break

    parts: list[str] = []
    if heading:
        parts.append(f'<p class="minor-heading">{html.escape(heading, quote=False)}</p>')
    if pieces:
        parts.append(f"<p>{''.join(pieces)}</p>")
    return "".join(parts), next_index, weight, consumed


def render_theorem_group_html(block: dict[str, Any], *, public_dir: Path) -> str:
    items = block.get("items") if isinstance(block.get("items"), list) else []
    if not items:
        return ""
    parts = ['<div class="theorem-list">']
    for item in items[:4]:
        if not isinstance(item, dict):
            continue
        title = html.escape(str(item.get("title") or "结论"), quote=False)
        body = render_tokens_html(item.get("desc_tokens"), public_dir=public_dir)
        parts.append(
            '<section class="theorem-item">'
            f'<h3>{title}</h3>'
            f'<p>{body}</p>'
            "</section>"
        )
    parts.append("</div>")
    if len(items) > 4:
        parts.append('<p class="more-note">更多等价表述见完整推导。</p>')
    return "".join(parts)


def render_block_html(block: dict[str, Any], *, public_dir: Path) -> str:
    block_type = str(block.get("type") or "")
    if block_type == "paragraph":
        return render_paragraph_html(block, public_dir=public_dir)
    if block_type in {"math_image", "math_inline", "math_display", "math_block"}:
        return f'<div class="formula-box">{render_math_html(block, public_dir=public_dir, inline=False)}</div>'
    if block_type == "theorem_group":
        return render_theorem_group_html(block, public_dir=public_dir)
    if isinstance(block.get("tokens"), list):
        return f'<p>{render_tokens_html(block.get("tokens"), public_dir=public_dir)}</p>'
    text = clean_text(block.get("text") or block.get("latex") or "")
    return f"<p>{html.escape(text, quote=False)}</p>" if text else ""


def limited_section_html(
    section: dict[str, Any] | None,
    *,
    public_dir: Path,
    max_weight: int,
    max_blocks: int,
) -> tuple[str, bool]:
    if not section:
        return '<p class="muted">暂无内容。</p>', False
    blocks = section.get("blocks") if isinstance(section.get("blocks"), list) else []
    parts: list[str] = []
    total = 0
    block_total = 0
    truncated = False
    index = 0
    while index < len(blocks):
        rendered, next_index, weight, consumed = render_compact_unit(
            blocks, index, public_dir=public_dir
        )
        if not rendered:
            index = next_index
            continue
        if parts and (total + weight > max_weight or block_total + consumed > max_blocks):
            truncated = True
            break
        parts.append(rendered)
        total += weight
        block_total += consumed
        index = next_index
    if not parts:
        return '<p class="muted">暂无内容。</p>', False
    return "\n".join(parts), truncated


def render_section_panel(
    record: dict[str, Any],
    *,
    key: str,
    public_dir: Path,
    max_weight: int,
    max_blocks: int,
) -> tuple[str, bool]:
    section = find_section(record, key)
    section_title = SECTION_TITLES.get(key, key)
    body, truncated = limited_section_html(
        section, public_dir=public_dir, max_weight=max_weight, max_blocks=max_blocks
    )
    return (
        f'<section class="section-panel"><h2>{html.escape(section_title, quote=False)}</h2>{body}</section>',
        truncated,
    )


def card_footer(item_id: str, page_index: int, page_count: int) -> str:
    return f"{item_id} · {page_index:02d}/{page_count:02d} · ok-shuxue"


def split_channels_cover_title(title: str) -> tuple[str, str]:
    parts = re.split(r"[：:]", clean_text(title), maxsplit=1)
    main = parts[0].strip() if parts else clean_text(title)
    subtitle = parts[1].strip() if len(parts) > 1 else ""
    return main or clean_text(title), subtitle


def build_card_specs(record: dict[str, Any], *, item_id: str, config: Config) -> list[CardSpec]:
    title = record_title(record, item_id)
    cover_main, cover_subtitle = split_channels_cover_title(title)
    summary = record_summary(record)
    tags = record_tags(record)
    category = record_category(record)
    tag_html = "".join(
        f"<span>{html.escape(tag, quote=False)}</span>"
        for tag in [category, *tags[:5]]
        if clean_text(tag)
    )
    poster_tag_html = "".join(
        f"<span>{html.escape(tag, quote=False)}</span>"
        for tag in [category, *tags[:4]]
        if clean_text(tag)
    )
    cover_body = f"""
<div class="poster-layout">
  <div class="poster-kicker">高中数学二级结论 · {html.escape(item_id, quote=False)}</div>
  <h1 class="poster-title">{html.escape(cover_main, quote=False)}</h1>
  <p class="poster-subtitle">{html.escape(cover_subtitle or summary or '一个结论，直接抓住做题入口', quote=False)}</p>
  <div class="poster-rule"></div>
  <p class="poster-summary">{html.escape(summary or '先看条件，再看结论，最后避开易错点。', quote=False)}</p>
  <div class="poster-tags">{poster_tag_html}</div>
  <div class="poster-bottom">收藏复盘 · 完整推导见最后一张小程序码</div>
</div>
"""
    intro_body = f"""
<div class="cover-mark">二级结论 · {html.escape(item_id, quote=False)}</div>
<h1 class="cover-title">{html.escape(title, quote=False)}</h1>
<p class="cover-summary">{html.escape(summary or '一图抓住核心结论、适用条件和常见坑点。', quote=False)}</p>
<div class="tag-row">{tag_html}</div>
<div class="cover-tip">适合收藏复盘：先看条件，再看公式，最后看易错点。</div>
"""

    cards: list[CardSpec] = [
        CardSpec(
            slug="cover",
            filename="01_cover.png",
            title="",
            subtitle="",
            body_html=cover_body,
            accent=CARD_ACCENTS["cover"],
            footer="",
        ),
        CardSpec(
            slug="intro",
            filename="02_intro.png",
            title="",
            subtitle="",
            body_html=intro_body,
            accent=CARD_ACCENTS["intro"],
            footer="",
        )
    ]

    core_parts: list[str] = []
    truncated_any = False
    for key, max_weight, max_blocks in (
        ("core_formula", 420, 3),
        ("conditions", 420, 3),
        ("statement", 900, 2),
    ):
        html_part, truncated = render_section_panel(
            record,
            key=key,
            public_dir=config.public_dir,
            max_weight=max_weight,
            max_blocks=max_blocks,
        )
        core_parts.append(html_part)
        truncated_any = truncated_any or truncated
    if truncated_any:
        core_parts.append('<p class="more-note">完整命题表述见小程序中的高清版。</p>')
    cards.append(
        CardSpec(
            slug="core",
            filename="03_core.png",
            title="核心结论",
            subtitle="先确认条件，再使用公式",
            body_html="\n".join(core_parts),
            accent=CARD_ACCENTS["core"],
            footer="",
        )
    )

    section_cards = [
        ("explanation", "04_explanation.png", "理解与直觉", "为什么球心会落在这条线上", 620, 9),
        ("proof", "05_proof.png", "证明过程", "把等距条件转成几何位置", 820, 11),
        ("examples", "06_example.png", "例题应用", "看到侧棱相等，优先找底面外心", 620, 10),
        ("traps", "07_traps.png", "易错提醒", "这个结论不是任意三棱锥都能用", 650, 10),
        ("summary", "08_summary.png", "复盘总结", "使用条件、关键公式和检查点", 820, 12),
    ]
    for key, filename, card_title, subtitle, max_weight, max_blocks in section_cards:
        panel, truncated = render_section_panel(
            record,
            key=key,
            public_dir=config.public_dir,
            max_weight=max_weight,
            max_blocks=max_blocks,
        )
        body = panel
        if truncated:
            body += '<p class="more-note">本卡片为精简版，完整推导和高清 PDF 可在最后一张图扫码获取。</p>'
        cards.append(
            CardSpec(
                slug=key,
                filename=filename,
                title=card_title,
                subtitle=subtitle,
                body_html=body,
                accent=CARD_ACCENTS[key],
                footer="",
            )
        )

    minicode_src = config.minicode_path.resolve().as_uri() if config.minicode_path.is_file() else ""
    if not minicode_src:
        raise ChannelsAssistantError(f"MiniCode image not found: {config.minicode_path}")
    examples = "、".join([item_id, *tags[:3]])
    minicode_body = f"""
<div class="minicode-layout">
  <div>
    <p class="minor-heading">小程序入口</p>
    <h1 class="minicode-title">想看完整推导和高清 PDF？</h1>
    <p>长按识别小程序码，进入后直接搜索 <strong>{html.escape(item_id, quote=False)}</strong>。</p>
    <p>也可以搜索关键词：{html.escape(examples, quote=False)}</p>
    <p class="more-note">更多高中数学二级结论会持续整理到小程序里。</p>
  </div>
  <img class="minicode-img" src="{html.escape(minicode_src, quote=True)}" alt="小程序码"/>
</div>
"""
    cards.append(
        CardSpec(
            slug="minicode",
            filename="09_minicode.png",
            title="继续查完整资料",
            subtitle="长按识别小程序码",
            body_html=minicode_body,
            accent=CARD_ACCENTS["minicode"],
            footer="",
        )
    )

    page_count = len(cards)
    return [
        CardSpec(
            slug=card.slug,
            filename=card.filename,
            title=card.title,
            subtitle=card.subtitle,
            body_html=card.body_html,
            accent=card.accent,
            footer=card_footer(item_id, index, page_count),
        )
        for index, card in enumerate(cards, start=1)
    ]


def render_card_html(card: CardSpec, *, size: tuple[int, int]) -> str:
    width, height = size
    page_title = html.escape(card.title or card.slug, quote=False)
    title_html = (
        f'<header class="card-header"><p class="eyebrow">高中数学二级结论</p>'
        f'<h1>{html.escape(card.title, quote=False)}</h1>'
        f'<p class="subtitle">{html.escape(card.subtitle, quote=False)}</p></header>'
        if card.title
        else ""
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{page_title}</title>
  <style>
    :root {{
      --scale: 1;
      --accent: {card.accent};
      --w: {width}px;
      --h: {height}px;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{
      margin: 0;
      width: var(--w);
      height: var(--h);
      overflow: hidden;
      background: #f1f5f2;
      color: #172026;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif;
      letter-spacing: 0;
    }}
    .card {{
      position: relative;
      width: var(--w);
      height: var(--h);
      padding: 70px 74px 78px;
      overflow: hidden;
      background: #fffdf8;
      border-top: 24px solid var(--accent);
    }}
    .card::before {{
      content: "";
      position: absolute;
      left: 0;
      top: 24px;
      bottom: 0;
      width: 16px;
      background: var(--accent);
      opacity: 0.95;
    }}
    .card-header {{
      margin: 0 0 30px;
      padding-bottom: 24px;
      border-bottom: 2px solid #e6e1d8;
    }}
    .eyebrow {{
      margin: 0 0 12px;
      color: var(--accent);
      font-size: calc(28px * var(--scale));
      line-height: 1.2;
      font-weight: 800;
    }}
    h1 {{
      margin: 0;
      color: #13272e;
      font-size: calc(58px * var(--scale));
      line-height: 1.16;
      font-weight: 900;
    }}
    .subtitle {{
      margin: 14px 0 0;
      color: #59656b;
      font-size: calc(30px * var(--scale));
      line-height: 1.45;
    }}
    .content {{
      font-size: calc(30px * var(--scale));
      line-height: 1.62;
    }}
    .section-panel {{
      margin: 0 0 22px;
      padding: 0;
    }}
    .section-panel h2 {{
      margin: 0 0 12px;
      color: var(--accent);
      font-size: calc(34px * var(--scale));
      line-height: 1.25;
      font-weight: 850;
    }}
    p {{
      margin: 10px 0;
      color: #172026;
      font-size: calc(30px * var(--scale));
      line-height: 1.62;
    }}
    strong {{ color: #0f252c; font-weight: 850; }}
    .minor-heading {{
      margin: 18px 0 8px;
      color: var(--accent);
      font-size: calc(30px * var(--scale));
      line-height: 1.3;
      font-weight: 850;
    }}
    .muted {{
      color: #6a7379;
    }}
    .more-note {{
      margin-top: 16px;
      padding: 12px 16px;
      color: #48545a;
      background: #f4f1e8;
      border-left: 7px solid var(--accent);
      font-size: calc(25px * var(--scale));
      line-height: 1.55;
    }}
    .math-text {{
      display: inline-block;
      margin: 0 4px;
      padding: 0 5px;
      color: #20303a;
      background: #f2f5f7;
      border-radius: 4px;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 0.92em;
      line-height: 1.2;
    }}
    .math-img {{
      height: auto;
      max-width: 100%;
      object-fit: contain;
    }}
    .math-img.inline {{
      display: inline-block;
      vertical-align: -0.28em;
      margin: 0 2px;
    }}
    .math-img.block {{
      display: block;
      margin: 4px auto 8px;
    }}
    .formula-box {{
      margin: 4px 0 8px;
      text-align: center;
    }}
    .theorem-list {{
      display: grid;
      gap: 14px;
    }}
    .theorem-item {{
      padding: 16px 18px;
      background: #f7f4ec;
      border-left: 7px solid var(--accent);
    }}
    .theorem-item h3 {{
      margin: 0 0 8px;
      color: #243238;
      font-size: calc(28px * var(--scale));
      line-height: 1.25;
      font-weight: 850;
    }}
    .theorem-item p {{
      margin: 0;
      font-size: calc(26px * var(--scale));
      line-height: 1.58;
    }}
    .cover-mark {{
      display: inline-block;
      margin: 30px 0 34px;
      padding: 9px 18px;
      color: #ffffff;
      background: var(--accent);
      font-size: calc(30px * var(--scale));
      line-height: 1.3;
      font-weight: 850;
    }}
    .cover-title {{
      margin: 0 0 28px;
      color: #10262e;
      font-size: calc(72px * var(--scale));
      line-height: 1.15;
      font-weight: 920;
    }}
    .cover-summary {{
      margin: 0 0 34px;
      color: #2c3940;
      font-size: calc(36px * var(--scale));
      line-height: 1.58;
    }}
    .tag-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin: 0 0 44px;
    }}
    .tag-row span {{
      display: inline-block;
      padding: 8px 14px;
      color: var(--accent);
      background: #eef5ef;
      border: 2px solid #d7e5da;
      font-size: calc(24px * var(--scale));
      line-height: 1.2;
      font-weight: 780;
    }}
    .cover-tip {{
      margin-top: 44px;
      padding: 22px 24px;
      color: #344047;
      background: #f4f1e8;
      border-left: 9px solid var(--accent);
      font-size: calc(30px * var(--scale));
      line-height: 1.55;
      font-weight: 700;
    }}
    .minicode-layout {{
      display: grid;
      grid-template-columns: 1fr;
      align-items: center;
      min-height: 1000px;
      text-align: center;
    }}
    .minicode-title {{
      margin: 0 0 26px;
      color: #10262e;
      font-size: calc(60px * var(--scale));
      line-height: 1.18;
      font-weight: 900;
    }}
    .minicode-img {{
      display: block;
      width: min(460px, 58%);
      height: auto;
      margin: 34px auto 0;
      padding: 18px;
      background: #ffffff;
      border: 2px solid #dfe7df;
    }}
    .footer {{
      position: absolute;
      left: 74px;
      right: 74px;
      bottom: 34px;
      padding-top: 16px;
      border-top: 2px solid #e8e2d6;
      color: #7a8488;
      font-size: 22px;
      line-height: 1.2;
      text-align: right;
    }}
    .card-cover {{
      padding: 78px 72px 76px;
      color: #ffffff;
      background: #135f64;
      border-top: 0;
    }}
    .card-cover::before {{
      display: none;
    }}
    .card-cover::after {{
      content: "";
      position: absolute;
      left: 72px;
      right: 72px;
      bottom: 146px;
      height: 2px;
      background: rgba(255,255,255,0.34);
    }}
    .poster-layout {{
      min-height: 1160px;
      display: flex;
      flex-direction: column;
    }}
    .poster-kicker {{
      align-self: flex-start;
      margin: 8px 0 82px;
      padding: 12px 18px;
      color: #135f64;
      background: #fffdf8;
      font-size: calc(28px * var(--scale));
      line-height: 1.25;
      font-weight: 900;
    }}
    .poster-title {{
      margin: 0;
      color: #ffffff;
      font-size: calc(82px * var(--scale));
      line-height: 1.08;
      font-weight: 940;
    }}
    .poster-subtitle {{
      margin: 28px 0 0;
      max-width: 860px;
      color: #e8fbf7;
      font-size: calc(42px * var(--scale));
      line-height: 1.28;
      font-weight: 780;
    }}
    .poster-rule {{
      width: 132px;
      height: 10px;
      margin: 54px 0 34px;
      background: #fffdf8;
    }}
    .poster-summary {{
      max-width: 860px;
      margin: 0;
      color: #eef7f4;
      font-size: calc(32px * var(--scale));
      line-height: 1.58;
    }}
    .poster-tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: auto;
      padding-bottom: 74px;
    }}
    .poster-tags span {{
      display: inline-block;
      padding: 9px 15px;
      color: #0d5358;
      background: #fffdf8;
      font-size: calc(24px * var(--scale));
      line-height: 1.2;
      font-weight: 850;
    }}
    .poster-bottom {{
      position: absolute;
      left: 74px;
      right: 74px;
      bottom: 72px;
      color: rgba(255,255,255,0.82);
      font-size: calc(26px * var(--scale));
      line-height: 1.35;
      font-weight: 760;
      text-align: left;
    }}
    .card-cover .footer {{
      color: rgba(255,255,255,0.76);
      border-top-color: rgba(255,255,255,0.34);
    }}
  </style>
</head>
<body>
  <main class="card card-{html.escape(card.slug, quote=True)}">
    {title_html}
    <section class="content">
      {card.body_html}
    </section>
    <footer class="footer">{html.escape(card.footer, quote=False)}</footer>
  </main>
</body>
</html>
"""


def import_playwright() -> Any:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise ChannelsAssistantError(
            "Playwright is required. Install the Python package and browser support first."
        ) from exc
    return sync_playwright


def render_cards(
    card_specs: list[CardSpec],
    *,
    output_dir: Path,
    config: Config,
) -> tuple[list[Path], list[Path]]:
    if not config.chrome_path.is_file():
        raise ChannelsAssistantError(f"Chrome executable not found: {config.chrome_path}")
    sync_playwright = import_playwright()
    cards_dir = output_dir / "cards"
    html_dir = output_dir / "card_html"
    cards_dir.mkdir(parents=True, exist_ok=True)
    html_dir.mkdir(parents=True, exist_ok=True)
    if config.force:
        for directory, pattern in ((cards_dir, "*.png"), (html_dir, "*.html")):
            for old_path in directory.glob(pattern):
                if old_path.is_file():
                    old_path.unlink()
    image_paths: list[Path] = []
    html_paths: list[Path] = []
    width, height = config.card_size

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=str(config.chrome_path),
            headless=True,
        )
        page = browser.new_page(
            viewport={"width": width, "height": height},
            device_scale_factor=config.card_dpr,
        )
        for card in card_specs:
            html_path = html_dir / card.filename.replace(".png", ".html")
            image_path = cards_dir / card.filename
            write_text(html_path, render_card_html(card, size=config.card_size))
            html_paths.append(html_path)
            image_paths.append(image_path)
            if image_path.is_file() and not config.force:
                LOGGER.info("Card exists, skipping render | %s", image_path)
                continue
            page.goto(html_path.resolve().as_uri(), wait_until="load")
            try:
                page.evaluate("() => document.fonts && document.fonts.ready")
            except Exception:
                pass
            page.wait_for_timeout(250)
            fit_result = page.evaluate(
                """
                () => {
                  const card = document.querySelector('.card');
                  let scale = 1.0;
                  if (!card) return {scale, overflow: false};
                  for (let i = 0; i < 9; i += 1) {
                    const overflow =
                      card.scrollHeight > card.clientHeight + 2 ||
                      card.scrollWidth > card.clientWidth + 2;
                    if (!overflow) return {scale, overflow: false};
                    scale = Math.max(0.74, scale - 0.035);
                    document.documentElement.style.setProperty('--scale', String(scale));
                  }
                  return {
                    scale,
                    overflow:
                      card.scrollHeight > card.clientHeight + 2 ||
                      card.scrollWidth > card.clientWidth + 2
                  };
                }
                """
            )
            if isinstance(fit_result, dict) and fit_result.get("overflow"):
                LOGGER.warning("Card may still overflow after fitting | %s", card.filename)
            page.screenshot(
                path=str(image_path),
                clip={"x": 0, "y": 0, "width": width, "height": height},
            )
            LOGGER.info("Rendered card | %s", image_path)
        browser.close()
    return image_paths, html_paths


def build_caption(record: dict[str, Any], *, item_id: str) -> str:
    summary = record_summary(record)
    topics = channels_topics(record)
    topic_text = " ".join(f"#{topic}" for topic in topics)
    lines = [
        summary or "这是一条高中数学二级结论复盘卡片。",
        "",
        "看图顺序：封面 → 导读 → 核心结论 → 理解直觉 → 证明过程 → 例题应用 → 易错提醒 → 复盘总结。",
        f"最后一张图有小程序码，进入后搜索 {item_id} 可以查看完整推导和高清 PDF。",
        "",
        topic_text,
    ]
    return "\n".join(line for line in lines if line is not None).strip() + "\n"


def render_preview_html(title: str, image_paths: Sequence[Path], caption: str) -> str:
    images = "\n".join(
        f'<figure><img src="{path.resolve().as_uri()}" alt="{html.escape(path.name, quote=True)}"/><figcaption>{html.escape(path.name, quote=False)}</figcaption></figure>'
        for path in image_paths
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{html.escape(title, quote=False)}</title>
  <style>
    body {{
      margin: 0;
      background: #f3f5f2;
      color: #172026;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
    }}
    main {{
      width: min(1180px, calc(100% - 32px));
      margin: 28px auto 60px;
    }}
    h1 {{ font-size: 28px; line-height: 1.35; margin: 0 0 18px; }}
    pre {{
      white-space: pre-wrap;
      padding: 18px;
      background: #ffffff;
      border: 1px solid #dde4dd;
      line-height: 1.75;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 18px;
      margin-top: 24px;
    }}
    figure {{ margin: 0; background: #ffffff; padding: 10px; border: 1px solid #dde4dd; }}
    img {{ display: block; width: 100%; height: auto; }}
    figcaption {{ color: #657177; font-size: 13px; margin-top: 8px; }}
  </style>
</head>
<body>
  <main>
    <h1>{html.escape(title, quote=False)}</h1>
    <pre>{html.escape(caption, quote=False)}</pre>
    <section class="grid">
      {images}
    </section>
  </main>
</body>
</html>
"""


def render_checklist(item_id: str, result: PackageResult) -> str:
    image_lines = "\n".join(f"- `{path}`" for path in result.card_paths)
    return f"""# 视频号图文发布检查清单：{item_id}

1. 打开 `preview.html` 检查 {result.card_count} 张图的顺序、文字截断、公式图片和小程序码。
2. 确认 `manifest.json` 里的 `card_count` 为 {result.card_count}，第一张图即视频号封面。
3. 运行不带 `--package-only` 的脚本，让 Chrome 打开视频号助手。
4. 登录后检查图片顺序、文案、话题和最后一张小程序引流卡。
5. 确认无误后人工点击发布。

视频号封面：`{result.cover_path}`

生成图片：

{image_lines}

文案：`{result.caption_path}`
预览：`{result.preview_html_path}`
"""


def package_one_item(item_id: str, record: dict[str, Any], config: Config) -> PackageResult:
    output_dir = config.output_dir / item_id
    output_dir.mkdir(parents=True, exist_ok=True)
    title = channels_title(record, item_id)
    LOGGER.info("Generating Channels package | %s", item_id)

    card_specs = build_card_specs(record, item_id=item_id, config=config)
    card_paths, html_paths = render_cards(card_specs, output_dir=output_dir, config=config)
    cover_path = card_paths[0] if card_paths else output_dir / "cards" / "01_cover.png"
    caption = build_caption(record, item_id=item_id)

    caption_path = output_dir / "caption.txt"
    manifest_path = output_dir / "manifest.json"
    preview_html_path = output_dir / "preview.html"
    checklist_path = output_dir / "channels_publish_checklist.md"
    post_payload_path = output_dir / "channels_post.json"

    write_text(caption_path, caption)
    write_text(preview_html_path, render_preview_html(title, card_paths, caption))

    payload = {
        "id": item_id,
        "title": title,
        "image_title": channels_image_title(record, item_id),
        "generated_at": now_iso(),
        "channels_url": config.channels_url,
        "caption_path": str(caption_path),
        "caption": caption,
        "card_size": {"width": config.card_size[0], "height": config.card_size[1]},
        "cover_path": str(cover_path),
        "card_paths": [str(path) for path in card_paths],
        "card_html_paths": [str(path) for path in html_paths],
        "topics": channels_topics(record),
        "minicode_path": str(config.minicode_path),
    }
    write_json(post_payload_path, payload)

    manifest = {
        "id": item_id,
        "title": title,
        "generated_at": now_iso(),
        "output_dir": str(output_dir),
        "card_count": len(card_paths),
        "cover_path": str(cover_path),
        "card_paths": [str(path) for path in card_paths],
        "card_html_paths": [str(path) for path in html_paths],
        "caption_path": str(caption_path),
        "preview_html_path": str(preview_html_path),
        "post_payload_path": str(post_payload_path),
        "minicode": {"path": str(config.minicode_path), "exists": config.minicode_path.is_file()},
    }
    write_json(manifest_path, manifest)

    result = PackageResult(
        id=item_id,
        title=title,
        output_dir=str(output_dir),
        cards_dir=str(output_dir / "cards"),
        cover_path=str(cover_path),
        card_paths=[str(path) for path in card_paths],
        caption_path=str(caption_path),
        manifest_path=str(manifest_path),
        preview_html_path=str(preview_html_path),
        checklist_path=str(checklist_path),
        post_payload_path=str(post_payload_path),
        card_count=len(card_paths),
    )
    write_text(checklist_path, render_checklist(item_id, result))
    return result


def first_visible_locator(
    page: Any, selectors: Sequence[str], *, timeout_ms: int = 1200
) -> Any | None:
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            locator.wait_for(state="visible", timeout=timeout_ms)
            return locator
        except Exception:
            continue
    return None


def last_visible_locator(
    page: Any, selectors: Sequence[str], *, timeout_ms: int = 1200
) -> Any | None:
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        for selector in selectors:
            try:
                locator = page.locator(selector)
                count = locator.count()
            except Exception:
                continue
            for index in range(count - 1, -1, -1):
                item = locator.nth(index)
                try:
                    item.wait_for(state="visible", timeout=150)
                    return item
                except Exception:
                    continue
        page.wait_for_timeout(100)
    return None


def clear_active_focus(page: Any) -> None:
    try:
        page.evaluate(
            """
            () => {
              const active = document.activeElement;
              if (active && typeof active.blur === "function") {
                active.blur();
              }
            }
            """
        )
    except Exception:
        pass


def active_element_is_editable(page: Any) -> bool:
    try:
        return bool(
            page.evaluate(
                """
                () => {
                  const el = document.activeElement;
                  if (!el) {
                    return false;
                  }
                  const tag = String(el.tagName || "").toLowerCase();
                  const type = String(el.getAttribute("type") || "").toLowerCase();
                  if (el.disabled || el.getAttribute("aria-disabled") === "true") {
                    return false;
                  }
                  if (el.isContentEditable || el.getAttribute("role") === "textbox") {
                    return true;
                  }
                  if (tag === "textarea") {
                    return true;
                  }
                  if (tag === "input") {
                    return !["button", "checkbox", "file", "hidden", "radio", "reset", "submit"].includes(type);
                  }
                  return false;
                }
                """
            )
        )
    except Exception:
        return False


def wait_for_user_click_editable(page: Any, label: str) -> None:
    clear_active_focus(page)
    LOGGER.warning("请手动点击%s输入框；脚本会一直等待，检测到光标后自动输入。", label)
    last_notice = time.monotonic()
    while True:
        if active_element_is_editable(page):
            page.wait_for_timeout(250)
            LOGGER.info("Detected focused %s input.", label)
            return
        now = time.monotonic()
        if now - last_notice >= 20:
            LOGGER.warning("Still waiting: please click %s input.", label)
            last_notice = now
        page.wait_for_timeout(700)


def wait_for_channels_ready(page: Any, *, timeout_sec: int) -> bool:
    deadline = None if timeout_sec <= 0 else time.monotonic() + timeout_sec
    selectors = [
        "text=\u9996\u9875",
        "text=视频号助手",
        "text=发表动态",
        "text=发布动态",
        "text=上传",
        "text=内容管理",
        "text=数据中心",
    ]
    last_notice = time.monotonic()
    while deadline is None or time.monotonic() < deadline:
        if first_visible_locator(page, selectors, timeout_ms=1000) is not None:
            return True
        now = time.monotonic()
        if deadline is None and now - last_notice >= 20:
            LOGGER.warning("Still waiting for Channels Assistant. Please scan/login if prompted.")
            last_notice = now
        page.wait_for_timeout(700)
    return False


def try_open_channels_publish(page: Any) -> bool:
    selectors = [
        "text=发表动态",
        "text=发布动态",
        "text=发表图文",
        "button:has-text('发表动态')",
        "button:has-text('发布动态')",
        "button:has-text('上传')",
        "text=上传",
    ]
    trigger = first_visible_locator(page, selectors, timeout_ms=1000)
    if trigger is None:
        LOGGER.warning("Could not find Channels publish entry. Please open the image-post dialog manually.")
        return False
    try:
        trigger.click()
        page.wait_for_timeout(900)
        return True
    except Exception as exc:
        LOGGER.warning("Could not click Channels publish entry: %s", exc)
        return False


def try_select_channels_image_mode(page: Any) -> None:
    selectors = [
        "text=图文",
        "text=图片",
        "button:has-text('图文')",
        "button:has-text('图片')",
        "[role=tab]:has-text('图文')",
        "[role=tab]:has-text('图片')",
    ]
    trigger = first_visible_locator(page, selectors, timeout_ms=700)
    if trigger is None:
        return
    try:
        trigger.click()
        page.wait_for_timeout(500)
    except Exception:
        return


def try_upload_channels_images(page: Any, image_paths: Sequence[Path]) -> bool:
    files = [str(path) for path in image_paths if path.is_file()]
    if not files:
        LOGGER.warning("No card images are available for upload.")
        return False

    upload_selectors = [
        "text=上传图片",
        "text=添加图片",
        "text=选择图片",
        "text=图片上传",
        "button:has-text('上传图片')",
        "button:has-text('添加图片')",
        "button:has-text('选择图片')",
    ]
    trigger = first_visible_locator(page, upload_selectors, timeout_ms=1000)
    if trigger is not None:
        try:
            with page.expect_file_chooser(timeout=3000) as file_chooser_info:
                trigger.click()
            file_chooser_info.value.set_files(files)
            LOGGER.info("Selected Channels image files via file chooser.")
            return True
        except Exception as exc:
            LOGGER.debug("Channels file chooser path failed: %s", exc)

    try:
        inputs = page.locator('input[type="file"]')
        for index in range(inputs.count() - 1, -1, -1):
            item = inputs.nth(index)
            try:
                item.set_input_files(files, timeout=2500)
                LOGGER.info("Selected Channels image files via input[type=file].")
                return True
            except Exception:
                continue
    except Exception as exc:
        LOGGER.debug("Channels file input path failed: %s", exc)

    LOGGER.warning("Could not upload images automatically. Please use the generated cards manually.")
    return False


def try_fill_channels_caption(page: Any, caption: str) -> bool:
    selectors = [
        'textarea[placeholder*="描述"]',
        'textarea[placeholder*="文案"]',
        'textarea[placeholder*="说点"]',
        'textarea[placeholder*="内容"]',
        '[contenteditable="true"][data-placeholder*="描述"]',
        '[contenteditable="true"][data-placeholder*="文案"]',
        '[contenteditable="true"][placeholder*="描述"]',
        '[contenteditable="true"][placeholder*="文案"]',
        'textarea',
        '[contenteditable="true"]',
    ]
    locator = first_visible_locator(page, selectors, timeout_ms=1200)
    if locator is None:
        LOGGER.warning("Could not find Channels caption input. Please paste caption.txt manually.")
        return False
    try:
        locator.click()
        page.keyboard.press("Control+A")
        page.keyboard.insert_text(caption)
        LOGGER.info("Channels caption filled.")
        return True
    except Exception as exc:
        LOGGER.warning("Channels caption fill failed: %s", exc)
        return False


def click_channels_home(page: Any, *, wait_forever: bool = True) -> bool:
    selectors = [
        "text=\u9996\u9875",
        "button:has-text('\u9996\u9875')",
        "a:has-text('\u9996\u9875')",
        "[role=menuitem]:has-text('\u9996\u9875')",
    ]
    last_notice = 0.0
    while True:
        trigger = first_visible_locator(page, selectors, timeout_ms=1200)
        if trigger is not None:
            try:
                trigger.scroll_into_view_if_needed(timeout=1000)
                trigger.click()
                page.wait_for_timeout(900)
                LOGGER.info("Clicked 首页.")
                return True
            except Exception as exc:
                LOGGER.warning("Could not click 首页: %s", exc)
                if not wait_forever:
                    return False

        if not wait_forever:
            LOGGER.warning("Could not find 首页. Continuing from the current page.")
            return False

        now = time.monotonic()
        if now - last_notice >= 20:
            LOGGER.warning("Still waiting for 首页. Please scan/login if prompted.")
            last_notice = now
        page.wait_for_timeout(1000)


def click_channels_recent_images(page: Any) -> bool:
    selectors = [
        "text=\u6700\u8fd1\u56fe\u6587",
        "button:has-text('\u6700\u8fd1\u56fe\u6587')",
        "[role=tab]:has-text('\u6700\u8fd1\u56fe\u6587')",
    ]
    trigger = first_visible_locator(page, selectors, timeout_ms=1200)
    if trigger is None:
        LOGGER.warning("Could not find 最近图文. Please click it manually.")
        return False
    try:
        trigger.scroll_into_view_if_needed(timeout=1000)
        trigger.click()
        page.wait_for_timeout(700)
        LOGGER.info("Clicked 最近图文.")
        return True
    except Exception as exc:
        LOGGER.warning("Could not click 最近图文: %s", exc)
        return False


def click_channels_publish_images(page: Any) -> bool:
    selectors = [
        "text=\u53d1\u8868\u56fe\u6587",
        "button:has-text('\u53d1\u8868\u56fe\u6587')",
    ]
    trigger = first_visible_locator(page, selectors, timeout_ms=1200)
    if trigger is None:
        LOGGER.warning("Could not find 发表图文. Please click it manually.")
        return False
    try:
        trigger.scroll_into_view_if_needed(timeout=1000)
        trigger.click()
        page.wait_for_timeout(1000)
        LOGGER.info("Clicked 发表图文.")
        return True
    except Exception as exc:
        LOGGER.warning("Could not click 发表图文: %s", exc)
        return False


def wait_for_channels_image_form(page: Any, *, timeout_sec: int = 20) -> bool:
    selectors = [
        'input[placeholder*="\u6dfb\u52a0\u6807\u9898"]',
        'input[placeholder*="22"]',
        'textarea[placeholder*="\u6dfb\u52a0\u63cf\u8ff0"]',
        'textarea[placeholder*="1000"]',
        "text=\u53d1\u5e03\u56fe\u7247\u52a8\u6001",
        "text=\u56fe\u6587\u6807\u9898",
        "text=\u56fe\u6587\u63cf\u8ff0",
    ]
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        if first_visible_locator(page, selectors, timeout_ms=700) is not None:
            return True
        page.wait_for_timeout(500)
    LOGGER.warning("Channels image form was not detected.")
    return False


def upload_channels_all_images_from_form(
    page: Any, image_paths: Sequence[Path]
) -> bool:
    files = [str(path) for path in image_paths if path.is_file()]
    if not files:
        LOGGER.warning("No card images are available for upload.")
        return False

    upload_selectors = [
        "text=\u53d1\u5e03\u56fe\u7247\u52a8\u6001",
        "text=\u53ef\u4e0a\u4f20",
        "text=\u6700\u591a18\u5f20\u56fe\u7247",
        "text=\u4e0a\u4f20\u56fe\u7247",
        "text=\u6dfb\u52a0\u56fe\u7247",
        "text=\u9009\u62e9\u56fe\u7247",
        "button:has-text('\u4e0a\u4f20\u56fe\u7247')",
        "button:has-text('\u6dfb\u52a0\u56fe\u7247')",
        "button:has-text('\u9009\u62e9\u56fe\u7247')",
    ]
    trigger = first_visible_locator(page, upload_selectors, timeout_ms=1200)
    if trigger is not None:
        try:
            trigger.scroll_into_view_if_needed(timeout=1000)
            with page.expect_file_chooser(timeout=4000) as file_chooser_info:
                trigger.click()
            file_chooser_info.value.set_files(files)
            LOGGER.info("Uploaded all Channels images via the form upload area.")
            return True
        except Exception as exc:
            LOGGER.debug("Channels form upload chooser failed: %s", exc)

    try:
        inputs = page.locator('input[type="file"]')
        for index in range(inputs.count() - 1, -1, -1):
            item = inputs.nth(index)
            try:
                item.set_input_files(files, timeout=3000)
                LOGGER.info("Uploaded all Channels images via input[type=file].")
                return True
            except Exception:
                continue
    except Exception as exc:
        LOGGER.debug("Channels form upload input failed: %s", exc)

    LOGGER.warning("Could not upload images automatically. Please upload the generated cards manually.")
    return False


def fill_channels_image_title(page: Any, title: str) -> bool:
    selectors = [
        'input[placeholder*="\u6dfb\u52a0\u6807\u9898"]',
        'input[placeholder*="22"]',
        '[contenteditable="true"][data-placeholder*="\u6dfb\u52a0\u6807\u9898"]',
        '[contenteditable="true"][placeholder*="\u6dfb\u52a0\u6807\u9898"]',
    ]
    locator = first_visible_locator(page, selectors, timeout_ms=1200)
    if locator is None:
        LOGGER.warning("Could not find 图文标题 input. Please fill it manually: %s", title)
        return False
    try:
        locator.scroll_into_view_if_needed(timeout=1000)
        locator.click()
        page.keyboard.press("Control+A")
        page.keyboard.insert_text(title)
        LOGGER.info("Filled 图文标题.")
        return True
    except Exception as exc:
        LOGGER.warning("Could not fill 图文标题: %s", exc)
        return False


def fill_wujie_input_by_selector(
    page: Any,
    selector: str,
    text: str,
    *,
    press_enter: bool = False,
) -> bool:
    try:
        result = page.evaluate(
            """
            ({ selector, text, pressEnter }) => {
              const getWujieDoc = () => {
                const app = document.querySelector("#container-wrap > div.container-center > div > wujie-app")
                  || document.querySelector("wujie-app[data-wujie-id='content']")
                  || document.querySelector("wujie-app");
                if (!app) {
                  return { error: "没有找到 wujie-app" };
                }

                const root = app.shadowRoot;
                if (!root) {
                  return { error: "没有找到 shadowRoot" };
                }

                const iframe = root.querySelector("iframe");
                const doc = iframe
                  ? (iframe.contentDocument || iframe.contentWindow?.document)
                  : root;
                if (!doc) {
                  return { error: "没有找到 wujie 文档" };
                }
                return { doc };
              };

              const { doc, error } = getWujieDoc();
              if (!doc) {
                return { ok: false, error };
              }

              const el = doc.querySelector(selector);
              if (!el) {
                return { ok: false, error: `没有找到 selector: ${selector}` };
              }

              const ownerDoc = el.ownerDocument || doc;
              const win = ownerDoc.defaultView || window;
              el.scrollIntoView?.({ block: "center", inline: "nearest" });
              el.focus();

              if (el.isContentEditable) {
                const selection = win.getSelection?.();
                if (selection) {
                  const range = ownerDoc.createRange();
                  range.selectNodeContents(el);
                  selection.removeAllRanges();
                  selection.addRange(range);
                }
                let inserted = false;
                try {
                  inserted = Boolean(ownerDoc.execCommand?.("insertText", false, text));
                } catch (_) {
                  inserted = false;
                }
                if (!inserted) {
                  el.textContent = text;
                }
              } else {
                const valueSetter = Object.getOwnPropertyDescriptor(el, "value")?.set
                  || Object.getOwnPropertyDescriptor(Object.getPrototypeOf(el), "value")?.set;
                if (valueSetter) {
                  valueSetter.call(el, "");
                } else {
                  el.value = "";
                }
                el.dispatchEvent(new Event("input", { bubbles: true, composed: true }));
                if (valueSetter) {
                  valueSetter.call(el, text);
                } else {
                  el.value = text;
                }
              }

              try {
                el.dispatchEvent(new InputEvent("input", {
                  inputType: "insertText",
                  data: text,
                  bubbles: true,
                  composed: true,
                }));
              } catch (_) {
                el.dispatchEvent(new Event("input", { bubbles: true, composed: true }));
              }
              el.dispatchEvent(new Event("change", { bubbles: true, composed: true }));

              if (pressEnter) {
                const keyboardOptions = {
                  key: "Enter",
                  code: "Enter",
                  keyCode: 13,
                  which: 13,
                  bubbles: true,
                  composed: true,
                };
                el.dispatchEvent(new KeyboardEvent("keydown", keyboardOptions));
                el.dispatchEvent(new KeyboardEvent("keypress", keyboardOptions));
                el.dispatchEvent(new KeyboardEvent("keyup", keyboardOptions));
              }

              return { ok: true };
            }
            """,
            {"selector": selector, "text": text, "pressEnter": press_enter},
        )
    except Exception as exc:
        LOGGER.debug("Wujie selector fill failed for %s: %s", selector, exc)
        return False

    if isinstance(result, dict) and result.get("ok"):
        return True
    LOGGER.debug("Wujie selector not available: %s", result)
    return False


def click_wujie_selector(page: Any, selector: str) -> bool:
    try:
        result = page.evaluate(
            """
            ({ selector }) => {
              const getWujieDoc = () => {
                const app = document.querySelector("#container-wrap > div.container-center > div > wujie-app")
                  || document.querySelector("wujie-app[data-wujie-id='content']")
                  || document.querySelector("wujie-app");
                if (!app) {
                  return { error: "没有找到 wujie-app" };
                }
                const root = app.shadowRoot;
                if (!root) {
                  return { error: "没有找到 shadowRoot" };
                }
                const iframe = root.querySelector("iframe");
                const doc = iframe
                  ? (iframe.contentDocument || iframe.contentWindow?.document)
                  : root;
                if (!doc) {
                  return { error: "没有找到 wujie 文档" };
                }
                return { doc };
              };

              const { doc, error } = getWujieDoc();
              if (!doc) {
                return { ok: false, error };
              }
              const el = doc.querySelector(selector);
              if (!el) {
                return { ok: false, error: `没有找到 selector: ${selector}` };
              }
              el.scrollIntoView?.({ block: "center", inline: "nearest" });
              el.focus?.();
              el.click?.();
              el.dispatchEvent(new MouseEvent("mousedown", { bubbles: true, composed: true }));
              el.dispatchEvent(new MouseEvent("mouseup", { bubbles: true, composed: true }));
              el.dispatchEvent(new MouseEvent("click", { bubbles: true, composed: true }));
              return { ok: true };
            }
            """,
            {"selector": selector},
        )
    except Exception as exc:
        LOGGER.debug("Wujie selector click failed for %s: %s", selector, exc)
        return False
    if isinstance(result, dict) and result.get("ok"):
        return True
    LOGGER.debug("Wujie click selector not available: %s", result)
    return False


def click_first_visible_button_text_in_wujie(page: Any, text: str) -> bool:
    try:
        result = page.evaluate(
            """
            ({ text }) => {
              const getWujieDoc = () => {
                const app = document.querySelector("#container-wrap > div.container-center > div > wujie-app")
                  || document.querySelector("wujie-app[data-wujie-id='content']")
                  || document.querySelector("wujie-app");
                if (!app) {
                  return { error: "没有找到 wujie-app" };
                }
                const root = app.shadowRoot;
                if (!root) {
                  return { error: "没有找到 shadowRoot" };
                }
                const iframe = root.querySelector("iframe");
                const doc = iframe
                  ? (iframe.contentDocument || iframe.contentWindow?.document)
                  : root;
                if (!doc) {
                  return { error: "没有找到 wujie 文档" };
                }
                return { doc };
              };
              const normalize = (value) => String(value || "")
                .replace(/\\s+/g, " ")
                .trim();
              const isVisible = (el) => {
                const rect = el.getBoundingClientRect();
                const style = el.ownerDocument.defaultView.getComputedStyle(el);
                return rect.width > 0
                  && rect.height > 0
                  && style.display !== "none"
                  && style.visibility !== "hidden";
              };

              const { doc, error } = getWujieDoc();
              if (!doc) {
                return { ok: false, error };
              }
              const buttons = Array.from(doc.querySelectorAll("button,[role='button'],a,span,div"))
                .filter((el) => isVisible(el) && normalize(el.textContent) === text);
              buttons.sort((a, b) => {
                const ar = a.getBoundingClientRect();
                const br = b.getBoundingClientRect();
                return ar.top === br.top ? ar.left - br.left : ar.top - br.top;
              });
              if (!buttons.length) {
                return { ok: false, error: `没有找到按钮: ${text}` };
              }
              buttons[0].scrollIntoView?.({ block: "center", inline: "nearest" });
              buttons[0].click?.();
              buttons[0].dispatchEvent(new MouseEvent("click", { bubbles: true, composed: true }));
              return { ok: true };
            }
            """,
            {"text": text},
        )
    except Exception as exc:
        LOGGER.debug("Wujie button click failed for %s: %s", text, exc)
        return False
    if isinstance(result, dict) and result.get("ok"):
        return True
    LOGGER.debug("Wujie button not available: %s", result)
    return False


def fill_channels_image_description_in_wujie(page: Any, caption: str) -> bool:
    selectors = [
        (
            "#container-wrap > div.container-center > div > div > div.main-body-wrap.post-create "
            "> div.main-body > div > div.post-edit-wrap.material-edit-wrap > div.form "
            "> div.form-item.flex-start > div.form-item-body > div > div.input-editor"
        ),
        ".post-desc-box .input-editor[contenteditable][data-placeholder*='\u6dfb\u52a0\u63cf\u8ff0']",
        ".input-editor[contenteditable][data-placeholder*='\u6dfb\u52a0\u63cf\u8ff0']",
    ]
    for selector in selectors:
        if fill_wujie_input_by_selector(page, selector, caption):
            LOGGER.info("Filled 图文描述 via wujie editor.")
            return True
    return False


def fill_channels_image_description(page: Any, caption: str) -> bool:
    if fill_channels_image_description_in_wujie(page, caption):
        return True

    selectors = [
        'textarea[placeholder*="\u6dfb\u52a0\u63cf\u8ff0"]',
        'textarea[placeholder*="1000"]',
        'textarea[placeholder*="\u63cf\u8ff0"]',
        '[contenteditable="true"][data-placeholder*="\u6dfb\u52a0\u63cf\u8ff0"]',
        '[contenteditable="true"][data-placeholder*="\u63cf\u8ff0"]',
        '[contenteditable="true"][placeholder*="\u6dfb\u52a0\u63cf\u8ff0"]',
        '[contenteditable="true"][placeholder*="\u63cf\u8ff0"]',
        'textarea',
        '[contenteditable="true"]',
    ]
    locator = first_visible_locator(page, selectors, timeout_ms=1200)
    try:
        if locator is not None:
            locator.scroll_into_view_if_needed(timeout=1000)
            locator.click()
        else:
            wait_for_user_click_editable(page, "\u56fe\u6587\u63cf\u8ff0")
        page.keyboard.press("Control+A")
        page.keyboard.insert_text(caption)
        LOGGER.info("Filled 图文描述.")
        return True
    except Exception as exc:
        LOGGER.warning("Could not fill 图文描述: %s", exc)
        return False


def click_channels_music_placeholder(page: Any) -> bool:
    music_selectors = [
        (
            "#container-wrap > div.container-center > div > div > div.main-body-wrap.post-create "
            "> div.main-body > div > div.post-edit-wrap.material-edit-wrap > div.form "
            "> div:nth-child(6) > div.form-item-body > div"
        ),
        (
            "#container-wrap > div.container-center > div > div > div.main-body-wrap.post-create "
            "> div.main-body > div > div.post-edit-wrap.material-edit-wrap > div.form "
            "> div:nth-child(6) .form-item-body"
        ),
        (
            "#container-wrap > div.container-center > div > div > div.main-body-wrap.post-create "
            "> div.main-body > div > div.post-edit-wrap.material-edit-wrap > div.form "
            "> div:nth-child(7) > div.form-item-body > div"
        ),
        (
            "#container-wrap > div.container-center > div > div > div.main-body-wrap.post-create "
            "> div.main-body > div > div.post-edit-wrap.material-edit-wrap > div.form "
            "> div:nth-child(7) .form-item-body"
        ),
    ]
    for selector in music_selectors:
        if click_wujie_selector(page, selector):
            page.wait_for_timeout(500)
            return True

    selectors = [
        "text=\u9009\u62e9\u80cc\u666f\u97f3\u4e50",
        "[placeholder*='\u9009\u62e9\u80cc\u666f\u97f3\u4e50']",
        "[aria-label*='\u9009\u62e9\u80cc\u666f\u97f3\u4e50']",
        "[title*='\u9009\u62e9\u80cc\u666f\u97f3\u4e50']",
        "[class*='select']:has-text('\u9009\u62e9\u80cc\u666f\u97f3\u4e50')",
        "[class*='Select']:has-text('\u9009\u62e9\u80cc\u666f\u97f3\u4e50')",
    ]
    trigger = first_visible_locator(page, selectors, timeout_ms=900)
    if trigger is None:
        return False
    try:
        trigger.scroll_into_view_if_needed(timeout=1200)
        trigger.click()
        page.wait_for_timeout(500)
        return True
    except Exception as exc:
        LOGGER.debug("Could not click music placeholder: %s", exc)
        return False


def search_channels_music_in_wujie(page: Any, query: str) -> bool:
    selectors = [
        (
            "#container-wrap > div.container-center > div > div > div.main-body-wrap.post-create "
            "> div.main-body > div > div.post-edit-wrap.material-edit-wrap > div.form "
            "> div:nth-child(6) > div.form-item-body > div > div.link-list-options "
            "> div.common-padding.search-wrap > div > div.weui-desktop-form__input-area "
            "> span > input"
        ),
        (
            "#container-wrap > div.container-center > div > div > div.main-body-wrap.post-create "
            "> div.main-body > div > div.post-edit-wrap.material-edit-wrap > div.form "
            "> div:nth-child(6) input.weui-desktop-form__input[placeholder*='\u641c\u7d22\u6b4c\u540d']"
        ),
        "input.weui-desktop-form__input[placeholder*='\u641c\u7d22\u6b4c\u540d']",
        "input[placeholder='\u641c\u7d22\u6b4c\u540d/\u6b4c\u624b/\u6b4c\u8bcd/\u60c5\u7eea']",
        (
            "#container-wrap > div.container-center > div > div > div.main-body-wrap.post-create "
            "> div.main-body > div > div.post-edit-wrap.material-edit-wrap > div.form "
            "> div:nth-child(7) > div.form-item-body > div > div.link-list-options "
            "> div.common-padding.search-wrap > div > div.weui-desktop-form__input-area "
            "> span > input"
        ),
    ]
    for selector in selectors:
        if fill_wujie_input_by_selector(page, selector, query, press_enter=True):
            LOGGER.info("Searched Channels music via wujie selector: %s.", query)
            return True
    return False


def hover_first_channels_music_result_and_click_select_in_wujie(page: Any, query: str) -> bool:
    try:
        result = page.evaluate(
            """
            async ({ query }) => {
              const getWujieDoc = () => {
                const app = document.querySelector("#container-wrap > div.container-center > div > wujie-app")
                  || document.querySelector("wujie-app[data-wujie-id='content']")
                  || document.querySelector("wujie-app");
                if (!app) {
                  return { error: "没有找到 wujie-app" };
                }
                const root = app.shadowRoot;
                if (!root) {
                  return { error: "没有找到 shadowRoot" };
                }
                const iframe = root.querySelector("iframe");
                const doc = iframe
                  ? (iframe.contentDocument || iframe.contentWindow?.document)
                  : root;
                if (!doc) {
                  return { error: "没有找到 wujie 文档" };
                }
                return { doc };
              };
              const normalize = (value) => String(value || "")
                .replace(/\\s+/g, " ")
                .trim();
              const isVisible = (el) => {
                const rect = el.getBoundingClientRect();
                const style = el.ownerDocument.defaultView.getComputedStyle(el);
                return rect.width > 0
                  && rect.height > 0
                  && style.display !== "none"
                  && style.visibility !== "hidden";
              };
              const visibleButtons = (scope) => Array.from(scope.querySelectorAll("button,[role='button'],a,span,div"))
                .filter((el) => isVisible(el) && normalize(el.textContent) === "选择")
                .sort((a, b) => {
                  const ar = a.getBoundingClientRect();
                  const br = b.getBoundingClientRect();
                  return ar.top === br.top ? ar.left - br.left : ar.top - br.top;
                });
              const hover = (el) => {
                const rect = el.getBoundingClientRect();
                const options = {
                  bubbles: true,
                  composed: true,
                  view: el.ownerDocument.defaultView,
                  clientX: rect.left + rect.width / 2,
                  clientY: rect.top + rect.height / 2,
                };
                for (const type of ["pointerover", "pointerenter", "mouseover", "mouseenter", "mousemove"]) {
                  el.dispatchEvent(new MouseEvent(type, options));
                }
              };
              const click = (el) => {
                el.scrollIntoView?.({ block: "center", inline: "nearest" });
                hover(el);
                el.click?.();
                el.dispatchEvent(new MouseEvent("mousedown", { bubbles: true, composed: true }));
                el.dispatchEvent(new MouseEvent("mouseup", { bubbles: true, composed: true }));
                el.dispatchEvent(new MouseEvent("click", { bubbles: true, composed: true }));
              };

              const { doc, error } = getWujieDoc();
              if (!doc) {
                return { ok: false, error };
              }

              const input = doc.querySelector(
                "#container-wrap > div.container-center > div > div > div.main-body-wrap.post-create "
                + "> div.main-body > div > div.post-edit-wrap.material-edit-wrap > div.form "
                + "> div:nth-child(6) > div.form-item-body > div > div.link-list-options "
                + "> div.common-padding.search-wrap > div > div.weui-desktop-form__input-area > span > input"
              ) || doc.querySelector("input.weui-desktop-form__input[placeholder*='搜索歌名']");
              const scope = input?.closest(".link-list-options") || doc;
              const firstResult = doc.querySelector(
                "#container-wrap > div.container-center > div > div > div.main-body-wrap.post-create "
                + "> div.main-body > div > div.post-edit-wrap.material-edit-wrap > div.form "
                + "> div:nth-child(6) > div.form-item-body > div > div.link-list-options "
                + "> div.common-padding.content > div.bgm-content-wrap > div > div > div.content-wrap "
                + "> div:nth-child(1) > div > div"
              );
              let buttons = [];

              if (firstResult && isVisible(firstResult)) {
                firstResult.scrollIntoView?.({ block: "center", inline: "nearest" });
                hover(firstResult);
                await new Promise((resolve) => setTimeout(resolve, 350));
                buttons = visibleButtons(firstResult);
                if (!buttons.length) {
                  buttons = visibleButtons(firstResult.parentElement || scope);
                }
                if (!buttons.length) {
                  buttons = visibleButtons(scope);
                }
                if (buttons.length) {
                  click(buttons[0]);
                  return { ok: true, method: "first-result-path" };
                }
              }

              buttons = visibleButtons(scope);
              if (buttons.length) {
                click(buttons[0]);
                return { ok: true, method: "visible-button" };
              }

              const candidates = Array.from(scope.querySelectorAll("div,li"))
                .filter((el) => {
                  if (!isVisible(el)) {
                    return false;
                  }
                  const text = normalize(el.textContent);
                  const rect = el.getBoundingClientRect();
                  return text.includes(query)
                    && rect.width >= 180
                    && rect.height >= 32
                    && rect.height <= 180;
                })
                .sort((a, b) => {
                  const ar = a.getBoundingClientRect();
                  const br = b.getBoundingClientRect();
                  return ar.top === br.top
                    ? (ar.width * ar.height) - (br.width * br.height)
                    : ar.top - br.top;
                });

              for (const row of candidates) {
                row.scrollIntoView?.({ block: "center", inline: "nearest" });
                hover(row);
                await new Promise((resolve) => setTimeout(resolve, 300));
                buttons = visibleButtons(scope);
                if (buttons.length) {
                  click(buttons[0]);
                  return { ok: true, method: "hover-query-row" };
                }
              }

              const fallbackRows = Array.from(scope.querySelectorAll("div,li"))
                .filter((el) => {
                  if (!isVisible(el)) {
                    return false;
                  }
                  const text = normalize(el.textContent);
                  const rect = el.getBoundingClientRect();
                  return text
                    && !text.includes("不添加音乐")
                    && !text.includes("搜索歌名")
                    && rect.width >= 180
                    && rect.height >= 40
                    && rect.height <= 180;
                })
                .sort((a, b) => {
                  const ar = a.getBoundingClientRect();
                  const br = b.getBoundingClientRect();
                  return ar.top === br.top ? ar.left - br.left : ar.top - br.top;
                });

              for (const row of fallbackRows.slice(0, 5)) {
                hover(row);
                await new Promise((resolve) => setTimeout(resolve, 250));
                buttons = visibleButtons(scope);
                if (buttons.length) {
                  click(buttons[0]);
                  return { ok: true, method: "hover-fallback-row" };
                }
              }

              return { ok: false, error: "没有找到可点击的第一个音乐选择按钮" };
            }
            """,
            {"query": query},
        )
    except Exception as exc:
        LOGGER.debug("Could not hover/click first Channels music result: %s", exc)
        return False

    if isinstance(result, dict) and result.get("ok"):
        LOGGER.info("Selected Channels music after hover: %s.", query)
        return True
    LOGGER.debug("Hover music selection failed: %s", result)
    return False


def click_first_visible_button_text(page: Any, text: str) -> bool:
    try:
        return bool(
            page.evaluate(
                """
                (text) => {
                  const normalize = (value) => String(value || "")
                    .replace(/\\s+/g, " ")
                    .trim();
                  const isVisible = (el) => {
                    const rect = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);
                    return rect.width > 0
                      && rect.height > 0
                      && rect.bottom >= 0
                      && rect.right >= 0
                      && rect.top <= window.innerHeight
                      && rect.left <= window.innerWidth
                      && style.display !== "none"
                      && style.visibility !== "hidden";
                  };
                  const buttons = Array.from(document.querySelectorAll("button,[role='button']"))
                    .filter((el) => isVisible(el) && normalize(el.textContent) === text);
                  buttons.sort((a, b) => {
                    const ar = a.getBoundingClientRect();
                    const br = b.getBoundingClientRect();
                    return ar.top === br.top ? ar.left - br.left : ar.top - br.top;
                  });
                  if (!buttons.length) {
                    return false;
                  }
                  buttons[0].click();
                  return true;
                }
                """,
                text,
            )
        )
    except Exception as exc:
        LOGGER.debug("Could not click button text %s: %s", text, exc)
        return False


def select_channels_music(page: Any, query: str) -> bool:
    query = clean_text(query) or DEFAULT_MUSIC_QUERY
    opened = click_channels_music_placeholder(page)
    if not opened:
        LOGGER.warning("Could not open 音乐 selector automatically.")

    page.wait_for_timeout(500)
    if search_channels_music_in_wujie(page, query):
        search = None
    else:
        search = last_visible_locator(
            page,
            [
                "#container-wrap > div.container-center > div > div > div.main-body-wrap.post-create > div.main-body > div > div.post-edit-wrap.material-edit-wrap > div.form > div:nth-child(6) > div.form-item-body > div > div.link-list-options > div.common-padding.search-wrap > div > div.weui-desktop-form__input-area > span > input",
                "input.weui-desktop-form__input[placeholder*='\u641c\u7d22\u6b4c\u540d']",
                "#container-wrap > div.container-center > div > div > div.main-body-wrap.post-create > div.main-body > div > div.post-edit-wrap.material-edit-wrap > div.form > div:nth-child(7) > div.form-item-body > div > div.link-list-options > div.common-padding.search-wrap > div > div.weui-desktop-form__input-area > span > input",
                '.ant-select-dropdown:not(.ant-select-dropdown-hidden) input',
                '[class*="select-dropdown"]:not([class*="hidden"]) input',
                '[class*="dropdown"]:not([class*="hidden"]) input',
                'input[placeholder*="\u641c\u7d22\u6b4c\u540d"]',
                'input[placeholder*="\u6b4c\u624b"]',
                'input[placeholder*="\u6b4c\u8bcd"]',
                'input[placeholder*="\u641c\u7d22"]',
                'input[aria-label*="\u641c\u7d22"]',
                'input[autocomplete="off"]',
            ],
            timeout_ms=1200,
        )
        try:
            if search is not None:
                search.click()
                page.keyboard.press("Control+A")
            else:
                wait_for_user_click_editable(page, "\u97f3\u4e50\u641c\u7d22")
            page.keyboard.insert_text(query)
            page.keyboard.press("Enter")
        except Exception as exc:
            LOGGER.warning("Could not search Channels music %s: %s", query, exc)
            return False

    first_visible_locator(
        page,
        ["text=\u641c\u7d22\u7ed3\u679c", f"text={query}"],
        timeout_ms=2500,
    )
    page.wait_for_timeout(800)
    if (
        hover_first_channels_music_result_and_click_select_in_wujie(page, query)
        or click_first_visible_button_text_in_wujie(page, "\u9009\u62e9")
        or click_first_visible_button_text(
        page, "\u9009\u62e9"
        )
    ):
        page.wait_for_timeout(600)
        LOGGER.info("Selected Channels music: %s.", query)
        return True

    choice = first_visible_locator(
        page,
        [
            "button:has-text('\u9009\u62e9')",
            "[role=button]:has-text('\u9009\u62e9')",
            "text=\u9009\u62e9",
        ],
        timeout_ms=1800,
    )
    if choice is None:
        choice = first_visible_locator(
            page,
            [f"text={query}", f"text={query[:4]}"],
            timeout_ms=1200,
        )
    if choice is None:
        LOGGER.warning("Could not find music result for %s. Please select it manually.", query)
        return False
    try:
        choice.click()
        page.wait_for_timeout(600)
        LOGGER.info("Selected Channels music: %s.", query)
        return True
    except Exception as exc:
        LOGGER.warning("Could not select Channels music %s: %s", query, exc)
        return False


def fill_channels_draft(result: PackageResult, config: Config) -> None:
    if not config.chrome_path.is_file():
        raise ChannelsAssistantError(f"Chrome executable not found: {config.chrome_path}")
    payload = read_json(Path(result.post_payload_path))
    if not isinstance(payload, dict):
        raise ChannelsAssistantError(f"Invalid Channels post payload: {result.post_payload_path}")
    image_paths = [Path(str(path)) for path in payload.get("card_paths", [])]
    caption = str(payload.get("caption") or Path(result.caption_path).read_text(encoding="utf-8"))
    image_title = truncate_text(
        str(payload.get("image_title") or payload.get("title") or result.title), 22
    )

    sync_playwright = import_playwright()
    LOGGER.info("Opening Channels Assistant in local Chrome | %s", config.chrome_path)
    config.profile_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(config.profile_dir),
            executable_path=str(config.chrome_path),
            headless=False,
            args=["--start-maximized"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(config.channels_url, wait_until="domcontentloaded")
        LOGGER.info("Waiting for Channels Assistant. Scan/login if prompted.")
        if not wait_for_channels_ready(page, timeout_sec=config.editor_wait_sec):
            LOGGER.warning(
                "Channels Assistant was not detected within %d seconds. "
                "If a login page is showing, complete login and rerun.",
                config.editor_wait_sec,
            )
            return

        click_channels_home(page)
        click_channels_recent_images(page)
        click_channels_publish_images(page)
        wait_for_channels_image_form(page)
        upload_channels_all_images_from_form(page, image_paths)
        fill_channels_image_title(page, image_title)
        fill_channels_image_description(page, caption)
        select_channels_music(page, config.music_query)

        LOGGER.info(
            "Channels draft fill attempted. Keeping Chrome open for %d seconds for review.",
            config.review_wait_sec,
        )
        if config.review_wait_sec:
            time.sleep(config.review_wait_sec)
        context.close()


def orchestrate(config: Config) -> dict[str, Any]:
    canonical = read_json(config.canonical_path)
    if not isinstance(canonical, dict):
        raise ChannelsAssistantError(f"Canonical JSON must be an object: {config.canonical_path}")

    report: dict[str, Any] = {
        "generated_at": now_iso(),
        "ids": list(config.ids),
        "canonical": str(config.canonical_path),
        "output_dir": str(config.output_dir),
        "package_only": config.package_only,
        "music_query": config.music_query,
        "items": [],
    }

    for item_id in config.ids:
        record = canonical[item_id]
        try:
            result = package_one_item(item_id, record, config)
            report["items"].append(asdict(result))
            write_json(config.report_path, report)
            if not config.package_only:
                fill_channels_draft(result, config)
        except Exception as exc:
            LOGGER.exception("Failed processing %s", item_id)
            failed = PackageResult(
                id=item_id,
                title=item_id,
                output_dir=str(config.output_dir / item_id),
                cards_dir=str(config.output_dir / item_id / "cards"),
                cover_path="",
                card_paths=[],
                caption_path="",
                manifest_path="",
                preview_html_path="",
                checklist_path="",
                post_payload_path="",
                card_count=0,
                status="failed",
                error=str(exc),
            )
            report["items"].append(asdict(failed))
            write_json(config.report_path, report)
            raise

    return report


def main() -> int:
    configure_console_encoding()
    args = parse_args()
    try:
        canonical_path = Path(args.canonical_json).resolve()
        canonical = read_json(canonical_path)
        if not isinstance(canonical, dict):
            raise ChannelsAssistantError(f"Canonical JSON must be an object: {canonical_path}")
        config = build_config(args, canonical)
        configure_logging(config.log_level)
        LOGGER.info("Channels target IDs | %s", ", ".join(config.ids))
        report = orchestrate(config)
        success_count = sum(1 for item in report["items"] if item.get("status") == "success")
        LOGGER.info(
            "Channels assistant complete | success=%d/%d | report=%s",
            success_count,
            len(config.ids),
            config.report_path,
        )
        return 0
    except ChannelsAssistantError as exc:
        LOGGER.error("%s", exc)
        return 1
    except KeyboardInterrupt:
        LOGGER.error("Interrupted by user.")
        return 130
    except Exception:
        LOGGER.exception("Unexpected Channels assistant failure")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
