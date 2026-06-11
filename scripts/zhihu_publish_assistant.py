#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate a Zhihu publishing package for selected conclusion IDs and optionally
open a local Chrome instance for draft filling.

The first version intentionally does not render formula assets again. It reads
formula image references from canonical_content_v2.json and validates that the
referenced files already exist under public/static/formulas.

Examples:
    python scripts/zhihu_publish_assistant.py G003 --package-only
    python scripts/zhihu_publish_assistant.py G003
    python scripts/zhihu_publish_assistant.py G003 --chrome "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
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
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "build" / "zhihu_posts"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports" / "zhihu_publish_assistant_report.json"
DEFAULT_MINICODE_PATH = PROJECT_ROOT / "assets" / "figures" / "MiniCode.png"
DEFAULT_WECHAT_DRAFTS_DIR = PROJECT_ROOT / "build" / "wechat_drafts"
DEFAULT_CHROME_PATH = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
DEFAULT_PROFILE_DIR = PROJECT_ROOT / "build" / "zhihu_chrome_profile"
DEFAULT_ZHIHU_WRITE_URL = "https://zhuanlan.zhihu.com/write"
DEFAULT_COVER_SIZE = "1200x675"
DEFAULT_WECHAT_SHOT_WIDTH = 720
DEFAULT_WECHAT_SHOT_DPR = 2.0
ZHIHU_ACCOUNT_TARGET_COUNT = 500
ZHIHU_ACCOUNT_CURRENT_COUNT = 149
ZHIHU_TOPIC_COUNT = 6
ID_PATTERN = re.compile(r"^[A-Za-z]\d{3}$")

SECTION_TITLE_MAP = {
    "core_formula": "核心公式",
    "conditions": "适用条件",
    "statement": "命题表述",
    "explanation": "理解与直觉",
    "proof": "证明过程",
    "examples": "例题应用",
    "traps": "易错提醒",
    "summary": "复盘总结",
}

DEFAULT_SECTION_KEYS = (
    "core_formula",
    "conditions",
    "statement",
    "explanation",
    "proof",
    "examples",
    "traps",
    "summary",
)

MINICODE_ASSET_URL = "/assets/figures/MiniCode.png"
LOGGER = logging.getLogger("zhihu_publish_assistant")


class ZhihuAssistantError(RuntimeError):
    """Readable error for expected assistant failures."""


@dataclass(frozen=True)
class Config:
    ids: tuple[str, ...]
    canonical_path: Path
    public_dir: Path
    output_dir: Path
    report_path: Path
    minicode_path: Path
    wechat_drafts_dir: Path
    chrome_path: Path
    profile_dir: Path
    zhihu_write_url: str
    cover_size: tuple[int, int]
    content_mode: str
    wechat_shot_width: int
    wechat_shot_dpr: float
    force_cover: bool
    package_only: bool
    editor_wait_sec: int
    review_wait_sec: int
    section_keys: tuple[str, ...]
    log_level: str


@dataclass
class AssetRef:
    kind: str
    asset_url: str
    local_path: str
    exists: bool
    latex: str = ""
    width_px: int | None = None
    height_px: int | None = None
    display_width_px: int | None = None
    display_height_px: int | None = None


@dataclass
class PackageResult:
    id: str
    title: str
    output_dir: str
    cover_path: str
    article_blocks_path: str
    preview_html_path: str
    body_markdown_path: str
    body_html_path: str
    manifest_path: str
    checklist_path: str
    formula_asset_count: int
    missing_asset_count: int
    topics: list[str] = field(default_factory=list)
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
        raise argparse.ArgumentTypeError("expected size like 1200x675")
    width = int(match.group(1))
    height = int(match.group(2))
    if width < 400 or height < 225:
        raise argparse.ArgumentTypeError("cover size is too small")
    return width, height


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and optionally fill a Zhihu draft for conclusion IDs.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/zhihu_publish_assistant.py G003 --package-only\n"
            "  python scripts/zhihu_publish_assistant.py G003\n"
            '  python scripts/zhihu_publish_assistant.py G003 --chrome "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"\n'
        ),
    )
    parser.add_argument(
        "ids", nargs="+", help="Conclusion IDs, e.g. G003 or G003,T008."
    )
    parser.add_argument("--canonical-json", default=str(DEFAULT_CANONICAL_PATH))
    parser.add_argument("--public-dir", default=str(DEFAULT_PUBLIC_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--report", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--minicode", default=str(DEFAULT_MINICODE_PATH))
    parser.add_argument("--wechat-drafts-dir", default=str(DEFAULT_WECHAT_DRAFTS_DIR))
    parser.add_argument("--chrome", default=str(DEFAULT_CHROME_PATH))
    parser.add_argument("--profile-dir", default=str(DEFAULT_PROFILE_DIR))
    parser.add_argument("--draft-url", default=DEFAULT_ZHIHU_WRITE_URL)
    parser.add_argument(
        "--cover-size", type=parse_size, default=parse_size(DEFAULT_COVER_SIZE)
    )
    parser.add_argument(
        "--content-mode",
        choices=("wechat-image", "blocks"),
        default="wechat-image",
        help="wechat-image renders the existing WeChat article as one long image. blocks inserts structured text/images.",
    )
    parser.add_argument(
        "--wechat-shot-width", type=int, default=DEFAULT_WECHAT_SHOT_WIDTH
    )
    parser.add_argument(
        "--wechat-shot-dpr", type=float, default=DEFAULT_WECHAT_SHOT_DPR
    )
    parser.add_argument("--force-cover", action="store_true")
    parser.add_argument(
        "--package-only",
        action="store_true",
        help="Only generate files. Do not open Chrome or fill a Zhihu draft.",
    )
    parser.add_argument(
        "--editor-wait-sec",
        type=int,
        default=90,
        help="Seconds to wait for the Zhihu editor before filling. Default: 90.",
    )
    parser.add_argument(
        "--review-wait-sec",
        type=int,
        default=600,
        help="Seconds to keep Chrome open after filling. Default: 600.",
    )
    parser.add_argument(
        "--section-keys",
        nargs="*",
        default=None,
        help="Canonical section keys to include. Default: all standard sections.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
    )
    return parser.parse_args()


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        if default is not None:
            return default
        raise ZhihuAssistantError(f"JSON file not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ZhihuAssistantError(f"Invalid JSON in {path}: {exc}") from exc


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


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
        raise ZhihuAssistantError(
            "Invalid conclusion ID(s): "
            + ", ".join(invalid)
            + ". Expected values like G003."
        )
    ids = tuple(dedupe_keep_order(normalized))
    if not ids:
        raise ZhihuAssistantError("At least one conclusion ID is required.")
    return ids


def build_config(args: argparse.Namespace, canonical: dict[str, Any]) -> Config:
    ids = normalize_ids(args.ids)
    missing = [item_id for item_id in ids if item_id not in canonical]
    if missing:
        raise ZhihuAssistantError(
            "Conclusion ID(s) not found in canonical JSON: " + ", ".join(missing)
        )
    section_keys = tuple(args.section_keys or DEFAULT_SECTION_KEYS)
    return Config(
        ids=ids,
        canonical_path=Path(args.canonical_json).resolve(),
        public_dir=Path(args.public_dir).resolve(),
        output_dir=Path(args.output_dir).resolve(),
        report_path=Path(args.report).resolve(),
        minicode_path=Path(args.minicode).resolve(),
        wechat_drafts_dir=Path(args.wechat_drafts_dir).resolve(),
        chrome_path=Path(args.chrome).resolve(),
        profile_dir=Path(args.profile_dir).resolve(),
        zhihu_write_url=str(args.draft_url),
        cover_size=args.cover_size,
        content_mode=str(args.content_mode),
        wechat_shot_width=max(360, int(args.wechat_shot_width)),
        wechat_shot_dpr=max(1.0, float(args.wechat_shot_dpr)),
        force_cover=bool(args.force_cover),
        package_only=bool(args.package_only),
        editor_wait_sec=max(5, int(args.editor_wait_sec)),
        review_wait_sec=max(0, int(args.review_wait_sec)),
        section_keys=section_keys,
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


def record_title(record: dict[str, Any], item_id: str) -> str:
    meta = record.get("meta") if isinstance(record.get("meta"), dict) else {}
    title = str(meta.get("title") or record.get("title") or item_id).strip()
    return title or item_id


def record_summary(record: dict[str, Any]) -> str:
    meta = record.get("meta") if isinstance(record.get("meta"), dict) else {}
    content = record.get("content") if isinstance(record.get("content"), dict) else {}
    plain = content.get("plain") if isinstance(content.get("plain"), dict) else {}
    return str(meta.get("summary") or plain.get("summary") or "").strip()


def record_category(record: dict[str, Any]) -> str:
    meta = record.get("meta") if isinstance(record.get("meta"), dict) else {}
    return str(meta.get("category") or "").strip()


def record_tags(record: dict[str, Any]) -> list[str]:
    meta = record.get("meta") if isinstance(record.get("meta"), dict) else {}
    raw_tags = meta.get("tags") if isinstance(meta.get("tags"), list) else []
    return [clean_text(tag) for tag in raw_tags if clean_text(tag)]


def record_aliases(record: dict[str, Any]) -> list[str]:
    meta = record.get("meta") if isinstance(record.get("meta"), dict) else {}
    raw_aliases = meta.get("aliases") if isinstance(meta.get("aliases"), list) else []
    return [clean_text(alias) for alias in raw_aliases if clean_text(alias)]


def zhihu_topics(record: dict[str, Any], item_id: str) -> list[str]:
    fixed = ["高中数学", "高考数学", "二级结论"]
    category = record_category(record)
    title = record_title(record, item_id)
    candidates: list[tuple[str, int, int]] = []

    def add_candidate(topic: str, score: int, order: int) -> None:
        topic = clean_text(topic)
        if not topic or topic in fixed:
            return
        candidates.append((topic, score, order))

    if category:
        add_candidate(category, 1000, 0)

    seo_priority = {
        "函数": 950,
        "数列": 940,
        "圆锥曲线": 930,
        "立体几何": 920,
        "平面几何": 910,
        "三角函数": 900,
        "导数": 890,
        "概率统计": 880,
        "向量": 870,
        "不等式": 860,
        "外接球": 820,
        "三棱锥": 800,
        "椭圆": 790,
        "双曲线": 780,
        "抛物线": 770,
    }
    for index, tag in enumerate(record_tags(record), start=1):
        score = seo_priority.get(tag, 500)
        if tag in title:
            score += 80
        add_candidate(tag, score, index)
    for index, alias in enumerate(record_aliases(record), start=100):
        score = seo_priority.get(alias, 360)
        if alias in title:
            score += 40
        add_candidate(alias, score, index)

    best_by_topic: dict[str, tuple[str, int, int]] = {}
    for topic, score, order in candidates:
        previous = best_by_topic.get(topic)
        if previous is None or (score, -order) > (previous[1], -previous[2]):
            best_by_topic[topic] = (topic, score, order)

    ranked = sorted(
        best_by_topic.values(), key=lambda item: (-item[1], item[2], item[0])
    )
    return dedupe_keep_order([*fixed, *(topic for topic, _score, _order in ranked)])[
        :ZHIHU_TOPIC_COUNT
    ]


def zhihu_title(record: dict[str, Any], item_id: str) -> str:
    base = record_title(record, item_id)
    prefix = f"高中数学二级结论 {item_id}"
    if base.startswith(prefix):
        return truncate_text(base, 80)
    return truncate_text(f"{prefix}：{base}", 80)


def token_latex_text(latex: str) -> str:
    latex = str(latex or "").strip()
    return f"${latex}$" if latex else ""


def text_from_tokens(tokens: Any) -> str:
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
    if not value:
        return None
    if re.match(r"^https?://", value, flags=re.I):
        return None
    normalized = value.lstrip("/").replace("/", os.sep)
    return public_dir / normalized


def formula_should_display(node: dict[str, Any], *, force_block: bool = False) -> bool:
    if force_block:
        return True
    latex = str(node.get("latex") or "").strip()
    compact = re.sub(r"\s+", "", latex)
    if not latex:
        return False
    if "\\begin{" in latex or "\\\\" in latex:
        return True
    if "\\quad" in latex or "\\qquad" in latex:
        return True
    if len(compact) > 30:
        return True
    if "=" in compact and len(compact) > 16:
        return True
    return False


def make_asset_ref(
    kind: str, node: dict[str, Any], public_dir: Path
) -> AssetRef | None:
    asset_url = resolve_asset_url(node)
    if not asset_url:
        return None
    local = local_asset_path(public_dir, asset_url)
    asset = node.get("asset") if isinstance(node.get("asset"), dict) else {}
    return AssetRef(
        kind=kind,
        asset_url=asset_url,
        local_path=str(local) if local else "",
        exists=bool(local and local.is_file()),
        latex=str(node.get("latex") or ""),
        width_px=(
            int(asset["width_px"]) if isinstance(asset.get("width_px"), int) else None
        ),
        height_px=(
            int(asset["height_px"]) if isinstance(asset.get("height_px"), int) else None
        ),
        display_width_px=(
            int(asset["display_width_px"])
            if isinstance(asset.get("display_width_px"), int)
            else None
        ),
        display_height_px=(
            int(asset["display_height_px"])
            if isinstance(asset.get("display_height_px"), int)
            else None
        ),
    )


def append_paragraph(blocks: list[dict[str, Any]], text: str) -> None:
    normalized = str(text or "").strip()
    if normalized:
        blocks.append({"type": "paragraph", "text": normalized})


def append_heading(blocks: list[dict[str, Any]], text: str, level: int = 2) -> None:
    normalized = str(text or "").strip()
    if normalized:
        blocks.append({"type": "heading", "level": level, "text": normalized})


def append_formula_image(
    blocks: list[dict[str, Any]],
    node: dict[str, Any],
    *,
    public_dir: Path,
    asset_refs: list[AssetRef],
) -> None:
    ref = make_asset_ref("formula_image", node, public_dir)
    latex = str(node.get("latex") or "").strip()
    if ref is None:
        append_paragraph(blocks, token_latex_text(latex))
        return
    asset_refs.append(ref)
    blocks.append(
        {
            "type": "formula_image",
            "latex": latex,
            "asset_url": ref.asset_url,
            "local_path": ref.local_path,
            "source_local_path": ref.local_path,
            "exists": ref.exists,
            "alt": latex or "公式",
        }
    )


def append_tokens_as_blocks(
    blocks: list[dict[str, Any]],
    tokens: Any,
    *,
    public_dir: Path,
    asset_refs: list[AssetRef],
) -> None:
    if not isinstance(tokens, list):
        append_paragraph(blocks, clean_text(tokens))
        return

    inline_parts: list[str] = []

    def flush_inline() -> None:
        if inline_parts:
            append_paragraph(blocks, "".join(inline_parts))
            inline_parts.clear()

    for token in tokens:
        if isinstance(token, str):
            inline_parts.append(token)
            continue
        if not isinstance(token, dict):
            continue
        token_type = str(token.get("type") or "text")
        if token_type == "text":
            inline_parts.append(str(token.get("text") or ""))
        elif token_type == "line_break":
            inline_parts.append("\n")
        elif token_type in {"math_inline", "math_display", "math_block"}:
            inline_parts.append(token_latex_text(str(token.get("latex") or "")))
        elif token_type == "math_image":
            if formula_should_display(token):
                flush_inline()
                append_formula_image(
                    blocks, token, public_dir=public_dir, asset_refs=asset_refs
                )
            else:
                inline_parts.append(token_latex_text(str(token.get("latex") or "")))
                ref = make_asset_ref("inline_formula_image", token, public_dir)
                if ref:
                    asset_refs.append(ref)
        elif token_type == "ref":
            inline_parts.append(str(token.get("text") or token.get("target_id") or ""))

    flush_inline()


def convert_block_to_article_blocks(
    source_block: dict[str, Any],
    *,
    public_dir: Path,
    asset_refs: list[AssetRef],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    block_type = str(source_block.get("type") or "paragraph")

    if block_type == "paragraph":
        append_tokens_as_blocks(
            output,
            source_block.get("tokens"),
            public_dir=public_dir,
            asset_refs=asset_refs,
        )
    elif block_type in {"math_image", "math_block", "math_display"}:
        append_formula_image(
            output, source_block, public_dir=public_dir, asset_refs=asset_refs
        )
    elif block_type == "theorem_group":
        items = source_block.get("items")
        if isinstance(items, list):
            for item in items:
                if not isinstance(item, dict):
                    continue
                append_heading(output, str(item.get("title") or "结论"), level=3)
                append_tokens_as_blocks(
                    output,
                    item.get("desc_tokens"),
                    public_dir=public_dir,
                    asset_refs=asset_refs,
                )
    elif block_type == "bullet_list":
        items = source_block.get("items")
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    text = text_from_tokens(item.get("tokens"))
                else:
                    text = clean_text(item)
                append_paragraph(output, f"- {text}")
    elif block_type == "proof_steps":
        steps = source_block.get("steps")
        if isinstance(steps, list):
            for index, step in enumerate(steps, start=1):
                if not isinstance(step, dict):
                    continue
                append_heading(
                    output, str(step.get("title") or f"步骤 {index}"), level=3
                )
                for child in step.get("content") or []:
                    if isinstance(child, dict):
                        output.extend(
                            convert_block_to_article_blocks(
                                child, public_dir=public_dir, asset_refs=asset_refs
                            )
                        )
    elif block_type == "example":
        append_heading(output, str(source_block.get("title") or "例题"), level=3)
        for label, key in (
            ("题目", "problem"),
            ("解题步骤", "solution"),
            ("关键结论", "answer"),
        ):
            content = source_block.get(key)
            if not content:
                continue
            append_heading(output, label, level=4)
            for child in content if isinstance(content, list) else [content]:
                if isinstance(child, dict):
                    output.extend(
                        convert_block_to_article_blocks(
                            child, public_dir=public_dir, asset_refs=asset_refs
                        )
                    )
    elif block_type in {"warning", "summary_box"}:
        append_heading(output, str(source_block.get("title") or ""), level=3)
        content = source_block.get("content")
        for child in content if isinstance(content, list) else [content]:
            if isinstance(child, dict):
                output.extend(
                    convert_block_to_article_blocks(
                        child, public_dir=public_dir, asset_refs=asset_refs
                    )
                )
    elif block_type == "divider":
        output.append({"type": "divider"})
    else:
        # Keep a readable fallback instead of silently losing content.
        text = text_from_tokens(source_block.get("tokens"))
        if not text and "latex" in source_block:
            text = token_latex_text(str(source_block.get("latex") or ""))
        append_paragraph(output, text)

    return output


def build_article_blocks(
    record: dict[str, Any],
    *,
    item_id: str,
    config: Config,
    asset_refs: list[AssetRef],
) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    title = zhihu_title(record, item_id)
    summary = record_summary(record)

    append_heading(blocks, title, level=1)
    if summary:
        append_paragraph(blocks, summary)

    content = record.get("content") if isinstance(record.get("content"), dict) else {}
    sections = (
        content.get("sections") if isinstance(content.get("sections"), list) else []
    )
    wanted = set(config.section_keys)
    for section in sections:
        if not isinstance(section, dict):
            continue
        key = str(section.get("key") or "")
        if key not in wanted:
            continue
        section_title = str(section.get("title") or SECTION_TITLE_MAP.get(key) or key)
        append_heading(blocks, section_title, level=2)
        section_blocks = (
            section.get("blocks") if isinstance(section.get("blocks"), list) else []
        )
        for source_block in section_blocks:
            if not isinstance(source_block, dict):
                continue
            blocks.extend(
                convert_block_to_article_blocks(
                    source_block,
                    public_dir=config.public_dir,
                    asset_refs=asset_refs,
                )
            )

    append_heading(blocks, "更多资料", level=2)
    append_paragraph(
        blocks,
        f"想查看高清 PDF 或搜索更多高中数学二级结论，可以长按识别下方小程序码；进入小程序后可直接搜索 {item_id}。",
    )
    minicode_exists = config.minicode_path.is_file()
    asset_refs.append(
        AssetRef(
            kind="minicode",
            asset_url=MINICODE_ASSET_URL,
            local_path=str(config.minicode_path),
            exists=minicode_exists,
        )
    )
    blocks.append(
        {
            "type": "image_block",
            "asset_url": MINICODE_ASSET_URL,
            "local_path": str(config.minicode_path),
            "exists": minicode_exists,
            "alt": "数秒查小程序码",
            "caption": "长按识别小程序码，搜索结论 ID 获取高清 PDF。",
        }
    )
    return blocks


def collect_all_formula_refs(
    record: dict[str, Any], public_dir: Path
) -> list[AssetRef]:
    refs: dict[str, AssetRef] = {}

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            node_type = str(node.get("type") or "")
            if node_type in {"math_image", "image_block"} or "asset" in node:
                ref = make_asset_ref("formula_image", node, public_dir)
                if ref and ref.asset_url not in refs:
                    refs[ref.asset_url] = ref
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(record)
    return list(refs.values())


def prepare_zhihu_upload_assets(
    blocks: list[dict[str, Any]], output_dir: Path
) -> list[dict[str, Any]]:
    upload_assets: list[dict[str, Any]] = []
    counters = {"formula_image": 0, "image_block": 0}
    for block in blocks:
        block_type = str(block.get("type") or "")
        if block_type not in {"formula_image", "image_block"}:
            continue
        source_path = Path(str(block.get("local_path") or ""))
        if not source_path.is_file():
            continue
        counters[block_type] += 1
        subdir = "formulas" if block_type == "formula_image" else "images"
        prefix = "formula" if block_type == "formula_image" else "image"
        upload_path = (
            output_dir
            / "upload_assets"
            / subdir
            / f"{prefix}_{counters[block_type]:03d}.png"
        )
        convert_to_zhihu_png(source_path, upload_path)
        block["source_local_path"] = str(source_path)
        block["local_path"] = str(upload_path)
        block["upload_prepared"] = upload_path.is_file()
        upload_assets.append(
            {
                "type": block_type,
                "source_local_path": str(source_path),
                "local_path": str(upload_path),
                "exists": upload_path.is_file(),
                "asset_url": block.get("asset_url", ""),
                "latex": block.get("latex", ""),
            }
        )
    return upload_assets


def convert_to_zhihu_png(source_path: Path, output_path: Path) -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise ZhihuAssistantError(
            "Pillow is required for Zhihu image conversion."
        ) from exc

    image = Image.open(source_path)
    if image.mode in {"RGBA", "LA"} or (
        image.mode == "P" and "transparency" in image.info
    ):
        rgba = image.convert("RGBA")
        white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        white.alpha_composite(rgba)
        rgb = white.convert("RGB")
    else:
        rgb = image.convert("RGB")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Do not pass through metadata such as 216dpi; Zhihu's parser is happier
    # with a plain RGB PNG.
    rgb.save(output_path, format="PNG", optimize=True)


ZHIHU_WECHAT_CONTENT_SECTION_KEYS = (
    "statement",
    "explanation",
    "proof",
    "examples",
    "traps",
    "summary",
)

ZHIHU_WECHAT_SECTION_TITLE_TO_KEY = {
    "二级结论": "statement",
    "理解说明": "explanation",
    "证明": "proof",
    "典型例题": "examples",
    "易错提醒": "traps",
    "结论小结": "summary",
}

ZHIHU_WECHAT_PART_LABELS = {
    "preface": "前言",
    "statement": "二级结论",
    "explanation": "理解说明",
    "proof": "证明",
    "examples": "典型例题",
    "traps": "易错提醒",
    "summary": "结论小结",
    "minicode": "小程序入口",
}


def build_wechat_section_image_blocks(
    record: dict[str, Any],
    *,
    item_id: str,
    config: Config,
    output_dir: Path,
) -> list[dict[str, Any]]:
    parts = build_wechat_article_image_parts(
        record,
        item_id=item_id,
        config=config,
    )
    image_dir = output_dir / "wechat_section_images"
    html_dir = output_dir / "wechat_section_html"
    blocks: list[dict[str, Any]] = []
    for index, part in enumerate(parts, start=1):
        key = str(part["key"])
        label = str(part["label"])
        html_path = html_dir / f"{index:02d}_{key}.html"
        image_path = image_dir / f"{index:02d}_{key}.png"
        write_text(html_path, str(part["html"]))
        screenshot_html_to_png(
            html_path,
            image_path,
            chrome_path=config.chrome_path,
            width=config.wechat_shot_width,
            device_scale_factor=config.wechat_shot_dpr,
        )
        blocks.append(
            {
                "type": "image_block",
                "asset_url": f"zhihu://wechat_section/{key}",
                "local_path": str(image_path),
                "exists": image_path.is_file(),
                "alt": f"{item_id} {label}",
                "caption": "",
                "section_key": key,
                "section_order": index,
            }
        )
    return blocks


def build_wechat_article_image_parts(
    record: dict[str, Any],
    *,
    item_id: str,
    config: Config,
) -> list[dict[str, str]]:
    article_html = read_localized_wechat_article_html(
        item_id=item_id,
        config=config,
    )
    section_html_by_key = extract_wechat_content_sections(article_html)
    missing = [
        key
        for key in ZHIHU_WECHAT_CONTENT_SECTION_KEYS
        if key not in section_html_by_key
    ]
    if missing:
        raise ZhihuAssistantError(
            "WeChat article HTML missing section(s): " + ", ".join(missing)
        )

    title = zhihu_title(record, item_id)
    parts: list[dict[str, str]] = [
        {
            "key": "preface",
            "label": ZHIHU_WECHAT_PART_LABELS["preface"],
            "html": wrap_zhihu_wechat_part_html(
                render_zhihu_preface_card(record, item_id=item_id),
                title=f"{title} - 前言",
                shot_width=config.wechat_shot_width,
            ),
        }
    ]
    for key in ZHIHU_WECHAT_CONTENT_SECTION_KEYS:
        label = ZHIHU_WECHAT_PART_LABELS[key]
        parts.append(
            {
                "key": key,
                "label": label,
                "html": wrap_zhihu_wechat_part_html(
                    section_html_by_key[key],
                    title=f"{title} - {label}",
                    shot_width=config.wechat_shot_width,
                ),
            }
        )
    parts.append(
        {
            "key": "minicode",
            "label": ZHIHU_WECHAT_PART_LABELS["minicode"],
            "html": wrap_zhihu_wechat_part_html(
                render_zhihu_minicode_card(record, item_id=item_id, config=config),
                title=f"{title} - 小程序入口",
                shot_width=config.wechat_shot_width,
            ),
        }
    )
    return parts


def read_localized_wechat_article_html(*, item_id: str, config: Config) -> str:
    article_dir = config.wechat_drafts_dir / item_id
    article_path = article_dir / "article.html"
    manifest_path = article_dir / "asset_manifest.json"
    if not article_path.is_file():
        raise ZhihuAssistantError(
            f"WeChat article HTML not found: {article_path}. "
            "Run generate_wechat_drafts.py for this ID first, or use --content-mode blocks."
        )
    article_html = article_path.read_text(encoding="utf-8")
    return localize_wechat_article_images(article_html, manifest_path)


def extract_wechat_content_sections(article_html: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    for section_html in split_top_level_wechat_sections(article_html):
        heading = first_section_heading_text(section_html)
        key = ZHIHU_WECHAT_SECTION_TITLE_TO_KEY.get(heading)
        if key:
            sections[key] = section_html
    return sections


def split_top_level_wechat_sections(article_html: str) -> list[str]:
    root_match = re.search(r"<section\b[^>]*>", article_html, flags=re.IGNORECASE)
    if not root_match:
        return []
    pos = root_match.end()
    depth = 0
    start: int | None = None
    sections: list[str] = []
    tag_re = re.compile(r"</?section\b[^>]*>", flags=re.IGNORECASE)
    for match in tag_re.finditer(article_html, pos):
        tag = match.group(0)
        is_close = tag.startswith("</")
        if is_close:
            if depth == 0:
                break
            depth -= 1
            if depth == 0 and start is not None:
                sections.append(article_html[start : match.end()])
                start = None
        else:
            if depth == 0:
                start = match.start()
            depth += 1
    return sections


def first_section_heading_text(section_html: str) -> str:
    match = re.search(
        r"<p\b[^>]*background\s*:[^>]*>(.*?)</p>",
        section_html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return ""
    text = re.sub(r"<[^>]+>", "", match.group(1))
    return html.unescape(" ".join(text.split()))


def wrap_zhihu_wechat_part_html(inner_html: str, *, title: str, shot_width: int) -> str:
    page_title = html.escape(title, quote=False)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{page_title}</title>
  <style>
    html, body {{
      margin: 0;
      padding: 0;
      background: #c9edcf;
      color: #1f2933;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
    }}
    body {{
      width: {shot_width}px;
      overflow-x: hidden;
    }}
    .zhihu-shot-page {{
      width: {shot_width}px;
      background: #c9edcf;
      padding: 18px 12px 22px;
      box-sizing: border-box;
    }}
    .zhihu-shot-inner {{
      max-width: 677px;
      margin: 0 auto;
    }}
    .zhihu-shot-inner > section:first-child {{
      margin-top: 0 !important;
    }}
    .zhihu-shot-inner > section:last-child {{
      margin-bottom: 0 !important;
    }}
    img {{
      max-width: 100%;
    }}
  </style>
</head>
<body>
  <main class="zhihu-shot-page">
    <div class="zhihu-shot-inner">
      {inner_html}
    </div>
  </main>
</body>
</html>
"""


def render_zhihu_preface_card(record: dict[str, Any], *, item_id: str) -> str:
    summary = record_summary(record) or record_title(record, item_id)
    return f"""
<section style="margin:0;padding:24px 22px 24px;background:#FFFDF8;border:1px solid #E8D9C5;border-radius:12px;box-sizing:border-box;">
  <p style="margin:0 0 12px;"><span style="display:inline-block;padding:4px 13px;border-radius:999px;background:#DDF4E8;color:#146B52;font-size:15px;line-height:1.4;font-weight:700;">前言</span></p>
  <p style="margin:0 0 8px;color:#164554;font-size:22px;line-height:1.45;font-weight:800;">本篇包含</p>
  <p style="margin:0 0 18px;color:#1f2933;font-size:18px;line-height:1.8;">• <strong>{html.escape(item_id, quote=False)}</strong>：{html.escape(summary, quote=False)}</p>
  <p style="margin:0;color:#6b7280;font-size:15px;line-height:1.8;">阅读建议：先看适用条件，再看核心公式，最后看易错提醒。公式较多的部分建议收藏后反复复看。</p>
</section>
"""


def build_zhihu_required_text_block(
    record: dict[str, Any], item_id: str
) -> dict[str, Any]:
    title = record_title(record, item_id)
    summary = record_summary(record)
    text = (
        f"本号计划系统整理 {ZHIHU_ACCOUNT_TARGET_COUNT} 条高中数学常用二级结论，"
        f"目前已经整理了 {ZHIHU_ACCOUNT_CURRENT_COUNT} 条。"
        f"本文是其中的 {item_id}：{title}。"
        "下方按前言、二级结论、理解说明、证明、典型例题、易错提醒、复盘总结和小程序入口分段展示。"
    )
    if summary:
        text += f"核心提示：{summary}"
    if len(clean_text(text)) <= 20:
        text += "请结合下方分段图片阅读完整推导、例题和易错提醒。"
    return {
        "type": "paragraph",
        "text": text,
        "purpose": "zhihu_required_text",
    }


def build_zhihu_ebook_text_block(item_id: str) -> dict[str, Any]:
    return {
        "type": "paragraph",
        "text": f"需要电子版的同学，点赞+关注后，斯信发送“{item_id}”聆取。",
        "purpose": "zhihu_ebook_cta",
    }


def render_zhihu_minicode_card(
    record: dict[str, Any], *, item_id: str, config: Config
) -> str:
    if not config.minicode_path.is_file():
        raise ZhihuAssistantError(f"MiniCode image not found: {config.minicode_path}")
    tags = []
    meta = record.get("meta") if isinstance(record.get("meta"), dict) else {}
    raw_tags = meta.get("tags") if isinstance(meta.get("tags"), list) else []
    for tag in raw_tags:
        text = clean_text(tag)
        if text:
            tags.append(text)
    examples = "、".join([item_id] + tags[:3])
    minicode_src = config.minicode_path.resolve().as_uri()
    return f"""
<section style="margin:0;padding:28px 28px 28px;background:#FFFDF8;border:1px solid #E8D9C5;border-radius:12px;box-sizing:border-box;text-align:center;">
  <p style="margin:0 0 18px;"><span style="display:inline-block;padding:4px 13px;border-radius:999px;background:#DDF4E8;color:#146B52;font-size:15px;line-height:1.4;font-weight:700;">小程序入口</span></p>
  <h1 style="margin:0 0 18px;color:#164554;font-size:30px;line-height:1.28;font-weight:800;">想查更多二级结论，可以用「数秒查」</h1>
  <p style="margin:0 0 20px;color:#374151;font-size:18px;line-height:1.8;">支持关键词搜索、热门结论、最近更新、收藏和高清 PDF 下载。</p>
  <img src="{html.escape(minicode_src, quote=True)}" alt="数秒查小程序码" style="display:block;width:230px;max-width:58%;height:auto;margin:0 auto 22px;"/>
  <p style="margin:0 0 14px;color:#1f2933;font-size:17px;line-height:1.8;text-align:left;"><strong>使用方式：</strong> 长按识别小程序码，进入后搜索结论 ID 或关键词。</p>
  <p style="margin:0;color:#6b7280;font-size:15px;line-height:1.7;">例如可以搜索：{html.escape(examples, quote=False)}。</p>
</section>
"""


def build_wechat_image_blocks(
    record: dict[str, Any],
    *,
    item_id: str,
    config: Config,
    output_dir: Path,
) -> list[dict[str, Any]]:
    return build_wechat_section_image_blocks(
        record,
        item_id=item_id,
        config=config,
        output_dir=output_dir,
    )

    image_path = output_dir / "wechat_article_long.png"
    html_path = output_dir / "wechat_article_render.html"
    render_wechat_article_long_image(
        record,
        item_id=item_id,
        config=config,
        html_output_path=html_path,
        image_output_path=image_path,
    )
    return [
        {
            "type": "image_block",
            "asset_url": "zhihu://wechat_article_long",
            "local_path": str(image_path),
            "exists": image_path.is_file(),
            "alt": f"{item_id} 公众号同款长图",
            "caption": "",
        }
    ]


def render_wechat_article_long_image(
    record: dict[str, Any],
    *,
    item_id: str,
    config: Config,
    html_output_path: Path,
    image_output_path: Path,
) -> None:
    article_dir = config.wechat_drafts_dir / item_id
    article_path = article_dir / "article.html"
    manifest_path = article_dir / "asset_manifest.json"
    if not article_path.is_file():
        raise ZhihuAssistantError(
            f"WeChat article HTML not found: {article_path}. "
            "Run generate_wechat_drafts.py for this ID first, or use --content-mode blocks."
        )
    article_html = article_path.read_text(encoding="utf-8")
    article_html = localize_wechat_article_images(article_html, manifest_path)
    page_html = wrap_wechat_article_for_screenshot(
        article_html,
        record=record,
        item_id=item_id,
        shot_width=config.wechat_shot_width,
    )
    write_text(html_output_path, page_html)
    screenshot_html_to_png(
        html_output_path,
        image_output_path,
        chrome_path=config.chrome_path,
        width=config.wechat_shot_width,
        device_scale_factor=config.wechat_shot_dpr,
    )


def localize_wechat_article_images(article_html: str, manifest_path: Path) -> str:
    if not manifest_path.is_file():
        return article_html
    manifest = read_json(manifest_path, default={})
    images = manifest.get("article_images") if isinstance(manifest, dict) else None
    if not isinstance(images, list):
        return article_html
    result = article_html
    for item in images:
        if not isinstance(item, dict):
            continue
        local_path = Path(str(item.get("local_path") or ""))
        if not local_path.is_file():
            continue
        local_uri = local_path.resolve().as_uri()
        for key in ("wechat_url", "asset_url"):
            url = str(item.get(key) or "")
            if url:
                result = result.replace(url, local_uri)
                result = result.replace(html.escape(url, quote=True), local_uri)
    return result


def wrap_wechat_article_for_screenshot(
    article_html: str,
    *,
    record: dict[str, Any],
    item_id: str,
    shot_width: int,
) -> str:
    title = html.escape(zhihu_title(record, item_id), quote=False)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{title}</title>
  <style>
    html, body {{
      margin: 0;
      padding: 0;
      background: #c9edcf;
      color: #1f2933;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
    }}
    body {{
      width: {shot_width}px;
      overflow-x: hidden;
    }}
    .wechat-shot-page {{
      width: {shot_width}px;
      min-height: 100vh;
      background: #c9edcf;
      padding: 24px 0 48px;
      box-sizing: border-box;
    }}
    img {{
      max-width: 100%;
    }}
  </style>
</head>
<body>
  <main class="wechat-shot-page">
    {article_html}
  </main>
</body>
</html>
"""


def screenshot_html_to_png(
    html_path: Path,
    image_path: Path,
    *,
    chrome_path: Path,
    width: int,
    device_scale_factor: float,
) -> None:
    if not chrome_path.is_file():
        raise ZhihuAssistantError(f"Chrome executable not found: {chrome_path}")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise ZhihuAssistantError(
            "Playwright is required to render the WeChat article long image."
        ) from exc

    image_path.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        viewport_height = 1200
        browser = playwright.chromium.launch(
            executable_path=str(chrome_path),
            headless=True,
        )
        page = browser.new_page(
            viewport={"width": width, "height": viewport_height},
            device_scale_factor=device_scale_factor,
        )
        page.goto(html_path.resolve().as_uri(), wait_until="load")
        page.wait_for_load_state("networkidle", timeout=10000)
        page.wait_for_timeout(600)
        try:
            scroll_height = int(
                page.evaluate("() => Math.ceil(document.documentElement.scrollHeight)")
            )
        except Exception:
            scroll_height = 0
        if scroll_height > viewport_height:
            page.screenshot(path=str(image_path), full_page=True)
            browser.close()
            return

        clip = None
        try:
            metrics = page.evaluate("""
                () => {
                  const main = document.querySelector('main') || document.body;
                  const root = main.getBoundingClientRect();
                  let bottom = root.top;
                  for (const el of main.querySelectorAll('*')) {
                    const style = window.getComputedStyle(el);
                    if (style.display === 'none' || style.visibility === 'hidden') continue;
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {
                      bottom = Math.max(bottom, rect.bottom);
                    }
                  }
                  return {
                    x: Math.max(0, root.left),
                    y: Math.max(0, root.top),
                    width: Math.max(1, root.width),
                    height: Math.max(1, Math.ceil(bottom - root.top))
                  };
                }
                """)
            if isinstance(metrics, dict):
                clip = {
                    "x": max(0, float(metrics["x"])),
                    "y": max(0, float(metrics["y"])),
                    "width": min(float(width), float(metrics["width"])),
                    "height": max(1.0, float(metrics["height"])),
                }
        except Exception:
            clip = None
        if clip:
            page.screenshot(path=str(image_path), clip=clip)
        else:
            page.screenshot(path=str(image_path), full_page=True)
        browser.close()


def find_font(size: int, *, bold: bool = False) -> Any:
    try:
        from PIL import ImageFont
    except ImportError as exc:
        raise ZhihuAssistantError("Pillow is required for cover generation.") from exc

    candidates = [
        Path(r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
        Path(r"C:\Windows\Fonts\simsun.ttc"),
        Path(
            r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"
        ),
    ]
    for path in candidates:
        if path.is_file():
            try:
                return ImageFont.truetype(str(path), size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def text_size(draw: Any, text: str, font: Any) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def fit_font(
    draw: Any,
    text: str,
    max_width: int,
    initial_size: int,
    min_size: int,
    *,
    bold: bool,
) -> Any:
    size = initial_size
    while size > min_size:
        font = find_font(size, bold=bold)
        width, _height = text_size(draw, text, font)
        if width <= max_width:
            return font
        size -= 2
    return find_font(min_size, bold=bold)


def wrap_text(
    draw: Any, text: str, font: Any, max_width: int, max_lines: int
) -> list[str]:
    chars = list(str(text or ""))
    lines: list[str] = []
    current = ""
    for char in chars:
        trial = current + char
        width, _height = text_size(draw, trial, font)
        if width <= max_width or not current:
            current = trial
            continue
        lines.append(current)
        current = char
        if len(lines) >= max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    if len(lines) == max_lines and len("".join(lines)) < len(text):
        lines[-1] = lines[-1].rstrip("，。；：,. ") + "…"
    return lines


def primary_formula_node(record: dict[str, Any]) -> dict[str, Any] | None:
    content = record.get("content") if isinstance(record.get("content"), dict) else {}
    formula = content.get("primary_formula")
    return formula if isinstance(formula, dict) else None


def primary_formula_path(record: dict[str, Any], public_dir: Path) -> Path | None:
    formula = primary_formula_node(record)
    if not formula:
        return None
    asset_url = resolve_asset_url(formula)
    local = local_asset_path(public_dir, asset_url)
    return local if local and local.is_file() else None


def generate_cover(
    record: dict[str, Any], *, item_id: str, config: Config, output_path: Path
) -> None:
    if output_path.exists() and not config.force_cover:
        return
    try:
        from PIL import Image, ImageDraw, ImageOps, ImageChops
    except ImportError as exc:
        raise ZhihuAssistantError("Pillow is required for cover generation.") from exc

    width, height = config.cover_size
    image = Image.new("RGB", (width, height), "#0b3c4a")
    draw = ImageDraw.Draw(image)

    for y in range(height):
        ratio = y / max(height - 1, 1)
        r = int(9 + 18 * ratio)
        g = int(54 + 38 * ratio)
        b = int(69 + 38 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    margin = int(width * 0.07)
    top = int(height * 0.07)
    category = record_category(record)
    title = record_title(record, item_id)
    formula_path = primary_formula_path(record, config.public_dir)
    formula = primary_formula_node(record)
    formula_latex = str(formula.get("latex") if formula else "")

    brand_font = find_font(int(width * 0.031), bold=True)
    chip_font = find_font(int(width * 0.026), bold=True)
    title_font = find_font(int(width * 0.064), bold=True)
    sub_font = find_font(int(width * 0.032), bold=False)

    draw.text(
        (margin, top), "数秒查 · 高中数学二级结论", font=brand_font, fill="#d8edf0"
    )

    chip = f"{category or '高中数学'} · {item_id}"
    chip_w, chip_h = text_size(draw, chip, chip_font)
    pad_x = int(width * 0.022)
    pad_y = int(height * 0.012)
    chip_box = [
        width - margin - chip_w - pad_x * 2,
        top,
        width - margin,
        top + chip_h + pad_y * 2,
    ]
    draw.rounded_rectangle(chip_box, radius=chip_h, outline="#a7d6d9", width=2)
    draw.text(
        (chip_box[0] + pad_x, chip_box[1] + pad_y), chip, font=chip_font, fill="#e4f5f5"
    )

    title_y = int(height * 0.23)
    title_lines = wrap_text(draw, title, title_font, int(width * 0.82), 2)
    for line in title_lines:
        draw.text((margin, title_y), line, font=title_font, fill="#ffffff")
        title_y += int(height * 0.12)

    summary = truncate_text(record_summary(record), 34)
    if summary:
        summary_font = fit_font(
            draw,
            summary,
            max_width=int(width * 0.76),
            initial_size=int(width * 0.032),
            min_size=int(width * 0.023),
            bold=False,
        )
        draw.text(
            (margin, title_y + int(height * 0.035)),
            summary,
            font=summary_font,
            fill="#f4d35e",
        )

    formula_box = [
        margin,
        int(height * 0.61),
        width - margin,
        int(height * 0.89),
    ]
    draw.rounded_rectangle(formula_box, radius=int(width * 0.018), fill="#f8f5ec")

    if formula_path:
        formula_img = Image.open(formula_path).convert("RGBA")
        alpha = formula_img.getchannel("A")
        bbox = alpha.getbbox()
        if bbox:
            formula_img = formula_img.crop(bbox)
            alpha = formula_img.getchannel("A")
        flat = Image.new("RGBA", formula_img.size, (255, 255, 255, 255))
        flat.alpha_composite(formula_img)
        gray = ImageOps.grayscale(flat)
        mask = gray.point(
            lambda p: 0 if p >= 245 else max(0, min(255, int((245 - p) * 255 / 170)))
        )
        try:
            mask = ImageChops.multiply(mask, alpha)
        except Exception:
            pass
        bbox = mask.getbbox()
        if bbox:
            mask = mask.crop(bbox)
        tinted = Image.new("RGBA", mask.size, (16, 66, 78, 0))
        tinted.putalpha(mask)
        formula_img = tinted
        max_w = formula_box[2] - formula_box[0] - int(width * 0.10)
        max_h = formula_box[3] - formula_box[1] - int(height * 0.09)
        scale = min(max_w / formula_img.width, max_h / formula_img.height, 5.5)
        new_size = (
            max(1, int(formula_img.width * scale)),
            max(1, int(formula_img.height * scale)),
        )
        formula_img = formula_img.resize(new_size, Image.LANCZOS)
        x = formula_box[0] + (formula_box[2] - formula_box[0] - new_size[0]) // 2
        y = formula_box[1] + (formula_box[3] - formula_box[1] - new_size[1]) // 2
        image.paste(formula_img, (x, y), formula_img)
    elif formula_latex:
        fallback = truncate_text(formula_latex, 60)
        fallback_font = fit_font(
            draw,
            fallback,
            max_width=formula_box[2] - formula_box[0] - int(width * 0.10),
            initial_size=int(width * 0.044),
            min_size=int(width * 0.026),
            bold=False,
        )
        tw, th = text_size(draw, fallback, fallback_font)
        draw.text(
            (
                formula_box[0] + (formula_box[2] - formula_box[0] - tw) // 2,
                formula_box[1] + (formula_box[3] - formula_box[1] - th) // 2,
            ),
            fallback,
            font=fallback_font,
            fill="#10424e",
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format="PNG")


def block_to_markdown(block: dict[str, Any]) -> str:
    block_type = str(block.get("type") or "")
    if block_type == "heading":
        level = int(block.get("level") or 2)
        level = min(max(level, 1), 4)
        return "#" * level + " " + str(block.get("text") or "").strip()
    if block_type == "paragraph":
        return str(block.get("text") or "").strip()
    if block_type in {"formula_image", "image_block"}:
        alt = str(block.get("alt") or block.get("latex") or "图片").replace("\n", " ")
        path = str(block.get("local_path") or "")
        caption = str(block.get("caption") or "").strip()
        text = f"![{alt}]({path})"
        if caption:
            text += f"\n\n{caption}"
        return text
    if block_type == "divider":
        return "---"
    return ""


def block_to_html(block: dict[str, Any]) -> str:
    block_type = str(block.get("type") or "")
    if block_type == "heading":
        level = int(block.get("level") or 2)
        level = min(max(level, 1), 4)
        text = html.escape(str(block.get("text") or ""), quote=False)
        return f"<h{level}>{text}</h{level}>"
    if block_type == "paragraph":
        text = html.escape(str(block.get("text") or ""), quote=False).replace(
            "\n", "<br/>"
        )
        return f"<p>{text}</p>"
    if block_type in {"formula_image", "image_block"}:
        path = Path(str(block.get("local_path") or ""))
        src = (
            path.as_uri() if path.is_absolute() else html.escape(str(path), quote=True)
        )
        alt = html.escape(
            str(block.get("alt") or block.get("latex") or "图片"), quote=True
        )
        css_class = (
            "formula-image" if block_type == "formula_image" else "article-image"
        )
        caption = html.escape(str(block.get("caption") or ""), quote=False)
        caption_html = f"<figcaption>{caption}</figcaption>" if caption else ""
        return f'<figure><img class="{css_class}" src="{src}" alt="{alt}"/>{caption_html}</figure>'
    if block_type == "divider":
        return "<hr/>"
    return ""


def render_body_markdown(blocks: list[dict[str, Any]]) -> str:
    pieces = [block_to_markdown(block) for block in blocks]
    return "\n\n".join(piece for piece in pieces if piece.strip()) + "\n"


def render_body_html(blocks: list[dict[str, Any]]) -> str:
    return "\n".join(block_to_html(block) for block in blocks if block_to_html(block))


def render_preview_html(title: str, body_html: str, cover_path: Path) -> str:
    cover_src = cover_path.as_uri()
    page_title = html.escape(title, quote=False)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{page_title}</title>
  <style>
    body {{
      margin: 0;
      background: #f4f4f2;
      color: #1f2933;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
    }}
    main {{
      width: min(820px, calc(100% - 32px));
      margin: 28px auto 56px;
      background: #ffffff;
      padding: 28px;
      box-sizing: border-box;
      box-shadow: 0 12px 40px rgba(15, 23, 42, 0.08);
    }}
    .cover {{
      width: 100%;
      border-radius: 6px;
      display: block;
      margin: 0 0 28px;
    }}
    h1 {{ font-size: 28px; line-height: 1.35; margin: 20px 0 16px; }}
    h2 {{ font-size: 22px; line-height: 1.45; margin: 30px 0 12px; border-bottom: 1px solid #e5e7eb; padding-bottom: 6px; }}
    h3 {{ font-size: 18px; line-height: 1.55; margin: 22px 0 8px; color: #164554; }}
    h4 {{ font-size: 16px; line-height: 1.55; margin: 18px 0 6px; color: #374151; }}
    p {{ font-size: 16px; line-height: 1.9; margin: 10px 0; }}
    figure {{ margin: 18px 0; text-align: center; }}
    figure img {{ max-width: 100%; height: auto; }}
    .formula-image {{ max-height: 170px; }}
    .article-image {{ width: 100%; max-width: 100%; }}
    figcaption {{ color: #6b7280; font-size: 14px; margin-top: 8px; }}
    code {{ white-space: pre-wrap; }}
  </style>
</head>
<body>
  <main>
    <img class="cover" src="{cover_src}" alt="cover"/>
    {body_html}
  </main>
</body>
</html>
"""


def render_checklist(item_id: str, result: PackageResult) -> str:
    topics_text = "、".join(result.topics)
    return f"""# 知乎发布检查清单：{item_id}

1. 打开 `preview.html` 检查封面、标题、正文和公式顺序。
2. 确认 `assets_manifest.json` 中 `missing_asset_count` 为 0。
3. 运行不带 `--package-only` 的脚本，让 Chrome 打开知乎写文章页。
4. 登录知乎后检查标题、封面、正文、公式图片和小程序码。
5. 确认无误后人工点击发布。

生成文件：

- 封面：`{result.cover_path}`
- 正文 blocks：`{result.article_blocks_path}`
- 预览：`{result.preview_html_path}`
- 资源清单：`{result.manifest_path}`

推荐话题：{topics_text}
"""


def package_one_item(
    item_id: str, record: dict[str, Any], config: Config
) -> PackageResult:
    output_dir = config.output_dir / item_id
    output_dir.mkdir(parents=True, exist_ok=True)
    title = zhihu_title(record, item_id)
    topics = zhihu_topics(record, item_id)
    cover_path = output_dir / "cover.png"
    article_blocks_path = output_dir / "article_blocks.json"
    preview_html_path = output_dir / "preview.html"
    body_md_path = output_dir / "body.md"
    body_html_path = output_dir / "body.html"
    manifest_path = output_dir / "assets_manifest.json"
    checklist_path = output_dir / "zhihu_publish_checklist.md"

    LOGGER.info("Generating Zhihu package | %s", item_id)
    generate_cover(record, item_id=item_id, config=config, output_path=cover_path)

    asset_refs: list[AssetRef] = []
    if config.content_mode == "wechat-image":
        image_blocks = build_wechat_image_blocks(
            record,
            item_id=item_id,
            config=config,
            output_dir=output_dir,
        )
        blocks = [
            build_zhihu_required_text_block(record, item_id),
            *image_blocks,
            build_zhihu_ebook_text_block(item_id),
        ]
    else:
        blocks = build_article_blocks(
            record, item_id=item_id, config=config, asset_refs=asset_refs
        )
    upload_assets = prepare_zhihu_upload_assets(blocks, output_dir)
    all_formula_refs = collect_all_formula_refs(record, config.public_dir)
    by_url = {ref.asset_url: ref for ref in all_formula_refs}
    for ref in asset_refs:
        by_url.setdefault(ref.asset_url, ref)
    formula_refs = list(by_url.values())
    missing = [ref for ref in formula_refs if not ref.exists]

    body_md = render_body_markdown(blocks)
    body_html = render_body_html(blocks)
    preview_html = render_preview_html(title, body_html, cover_path)

    write_json(
        article_blocks_path,
        {
            "id": item_id,
            "title": title,
            "cover_path": str(cover_path),
            "topics": topics,
            "generated_at": now_iso(),
            "blocks": blocks,
        },
    )
    write_text(body_md_path, body_md)
    write_text(body_html_path, body_html + "\n")
    write_text(preview_html_path, preview_html)

    manifest = {
        "id": item_id,
        "title": title,
        "generated_at": now_iso(),
        "cover": {"path": str(cover_path), "exists": cover_path.is_file()},
        "topics": topics,
        "formula_asset_count": len(formula_refs),
        "missing_asset_count": len(missing),
        "upload_asset_count": len(upload_assets),
        "assets": [asdict(ref) for ref in formula_refs],
        "upload_assets": upload_assets,
        "missing_assets": [asdict(ref) for ref in missing],
    }
    write_json(manifest_path, manifest)

    result = PackageResult(
        id=item_id,
        title=title,
        output_dir=str(output_dir),
        cover_path=str(cover_path),
        article_blocks_path=str(article_blocks_path),
        preview_html_path=str(preview_html_path),
        body_markdown_path=str(body_md_path),
        body_html_path=str(body_html_path),
        manifest_path=str(manifest_path),
        checklist_path=str(checklist_path),
        formula_asset_count=len(formula_refs),
        missing_asset_count=len(missing),
        topics=topics,
        warnings=[],
    )
    if missing:
        result.warnings.append(f"{len(missing)} referenced asset(s) are missing.")
    write_text(checklist_path, render_checklist(item_id, result))
    return result


def load_package_blocks(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    if not isinstance(payload, dict):
        raise ZhihuAssistantError(f"Invalid article blocks file: {path}")
    if not isinstance(payload.get("blocks"), list):
        raise ZhihuAssistantError(f"article_blocks.json missing blocks list: {path}")
    return payload


def fill_zhihu_draft(result: PackageResult, config: Config) -> None:
    if not config.chrome_path.is_file():
        raise ZhihuAssistantError(f"Chrome executable not found: {config.chrome_path}")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise ZhihuAssistantError(
            "Playwright is required for draft filling. Install the Python package first."
        ) from exc

    payload = load_package_blocks(Path(result.article_blocks_path))
    title = str(payload.get("title") or result.title)
    blocks = payload["blocks"]
    topics = [
        str(item).strip() for item in payload.get("topics", []) if str(item).strip()
    ]

    LOGGER.info("Opening Zhihu draft in local Chrome | %s", config.chrome_path)
    config.profile_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(config.profile_dir),
            executable_path=str(config.chrome_path),
            headless=False,
            args=["--start-maximized"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(config.zhihu_write_url, wait_until="domcontentloaded")
        LOGGER.info("Waiting for Zhihu editor to become ready.")
        if not wait_for_editor_ready(page, timeout_sec=config.editor_wait_sec):
            LOGGER.warning(
                "Zhihu editor was not detected within %d seconds. "
                "If a login or verification page is showing, rerun after completing it.",
                config.editor_wait_sec,
            )
            return

        try_fill_title(page, title)
        try_fill_body(page, blocks)
        try_upload_cover(page, Path(result.cover_path))
        try_add_topics(page, topics)

        LOGGER.info(
            "Draft fill attempted. Keeping Chrome open for %d seconds for review.",
            config.review_wait_sec,
        )
        if config.review_wait_sec:
            time.sleep(config.review_wait_sec)
        context.close()


def first_visible_locator(
    page: Any, selectors: Sequence[str], *, timeout_ms: int = 1500
) -> Any | None:
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            locator.wait_for(state="visible", timeout=timeout_ms)
            return locator
        except Exception:
            continue
    return None


def try_add_topics(page: Any, topics: Sequence[str]) -> None:
    topics = [clean_text(topic) for topic in topics if clean_text(topic)]
    if not topics:
        return
    try:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(600)
        added: list[str] = []
        for topic in topics[:ZHIHU_TOPIC_COUNT]:
            if add_zhihu_topic(page, topic):
                added.append(topic)
            else:
                LOGGER.warning("Could not add Zhihu topic automatically: %s", topic)
        if added:
            LOGGER.info("Zhihu topics attempted: %s", "、".join(added))
    except Exception as exc:
        LOGGER.warning("Zhihu topic automation failed: %s", exc)


def add_zhihu_topic(page: Any, topic: str) -> bool:
    trigger_selectors = [
        'button:has-text("添加话题")',
        "text=+ 添加话题",
        "text=+添加话题",
        "text=添加话题",
        '[aria-label*="添加话题"]',
    ]
    trigger = first_visible_locator(page, trigger_selectors, timeout_ms=1200)
    if trigger is None:
        return False
    try:
        trigger.click()
        page.wait_for_timeout(300)
    except Exception:
        return False

    input_selectors = [
        'input[placeholder*="话题"]',
        'input[placeholder*="搜索"]',
        'input[placeholder*="请输入"]',
        'textarea[placeholder*="话题"]',
        '[contenteditable="true"][data-placeholder*="话题"]',
        '[contenteditable="true"][placeholder*="话题"]',
    ]
    topic_input = first_visible_locator(page, input_selectors, timeout_ms=1800)
    if topic_input is None:
        return False

    try:
        topic_input.click()
        page.keyboard.press("Control+A")
        page.keyboard.insert_text(topic)
        page.wait_for_timeout(900)
        if click_zhihu_topic_suggestion(page, topic):
            page.wait_for_timeout(500)
            return True
        page.keyboard.press("Enter")
        page.wait_for_timeout(500)
        return True
    except Exception as exc:
        LOGGER.debug("Add Zhihu topic failed for %s: %s", topic, exc)
        return False


def click_zhihu_topic_suggestion(page: Any, topic: str) -> bool:
    try:
        result = page.evaluate(
            """
            (topic) => {
              const active = document.activeElement;
              const activeRect = active && active.getBoundingClientRect
                ? active.getBoundingClientRect()
                : {top: 0};
              const all = Array.from(document.querySelectorAll('body *'));
              const candidates = [];
              for (const el of all) {
                const text = (el.textContent || '').trim();
                if (!text || !text.includes(topic)) continue;
                const style = window.getComputedStyle(el);
                if (style.display === 'none' || style.visibility === 'hidden') continue;
                const rect = el.getBoundingClientRect();
                if (rect.width <= 0 || rect.height <= 0) continue;
                if (rect.bottom < activeRect.top - 8) continue;
                if (rect.width > 760 || rect.height > 120) continue;
                candidates.push({
                  el,
                  exact: text === topic ? 1 : 0,
                  top: rect.top,
                  area: rect.width * rect.height,
                });
              }
              candidates.sort((a, b) =>
                b.exact - a.exact || a.top - b.top || a.area - b.area
              );
              const picked = candidates[0];
              if (!picked) return false;
              picked.el.click();
              return true;
            }
            """,
            topic,
        )
        return bool(result)
    except Exception as exc:
        LOGGER.debug("Click Zhihu topic suggestion failed for %s: %s", topic, exc)
        return False


def wait_for_editor_ready(page: Any, *, timeout_sec: int) -> bool:
    selectors = [
        'textarea[placeholder*="请输入标题"]',
        'input[placeholder*="请输入标题"]',
        'textarea[placeholder*="标题"]',
        'input[placeholder*="标题"]',
        '[contenteditable="true"][data-placeholder*="请输入标题"]',
        '[contenteditable="true"][data-placeholder*="标题"]',
        '[contenteditable="true"]:has-text("请输入正文")',
        "text=请输入正文",
        "text=请输入标题",
        '.public-DraftEditor-content[contenteditable="true"]',
        '.ProseMirror[contenteditable="true"]',
    ]
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        if first_visible_locator(page, selectors, timeout_ms=1000) is not None:
            return True
        page.wait_for_timeout(500)
    return False


def try_fill_title(page: Any, title: str) -> None:
    selectors = [
        'textarea[placeholder*="请输入标题"]',
        'input[placeholder*="请输入标题"]',
        'textarea[placeholder*="标题"]',
        'input[placeholder*="标题"]',
        '[contenteditable="true"][data-placeholder*="请输入标题"]',
        '[contenteditable="true"][data-placeholder*="标题"]',
        '[contenteditable="true"][placeholder*="请输入标题"]',
        '[contenteditable="true"][placeholder*="标题"]',
        ".WriteIndex-titleInput textarea",
        ".WriteIndex-titleInput input",
    ]
    locator = first_visible_locator(page, selectors)
    if locator is None:
        LOGGER.warning(
            "Could not find title input. Please paste the title manually: %s", title
        )
        return
    try:
        locator.click()
        page.keyboard.press("Control+A")
        page.keyboard.insert_text(title)
        LOGGER.info("Title filled.")
    except Exception as exc:
        LOGGER.warning("Title fill failed: %s", exc)


def try_upload_cover(page: Any, cover_path: Path) -> None:
    if not cover_path.is_file():
        LOGGER.warning("Cover image not found, skipping upload: %s", cover_path)
        return

    # Important: do not fall back to global input[type=file]. Zhihu also has
    # editor image upload inputs, and using the first global input inserts the
    # cover into the article body instead of the publish-settings cover slot.
    trigger_selectors = [
        "text=添加文章封面",
        "text=上传文章封面",
        "text=更换文章封面",
        "text=添加封面",
        '[aria-label*="文章封面"]',
    ]
    try:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(500)
        trigger = first_visible_locator(page, trigger_selectors, timeout_ms=1200)
        if trigger is None:
            LOGGER.warning(
                "Could not find Zhihu cover trigger. Cover was not uploaded to avoid inserting it into the body."
            )
            return

        try:
            with page.expect_file_chooser(timeout=3000) as file_chooser_info:
                trigger.click()
            file_chooser_info.value.set_files(str(cover_path))
            LOGGER.info("Cover uploaded via Zhihu cover file chooser.")
            return
        except Exception as chooser_exc:
            LOGGER.debug("Cover trigger did not open a file chooser: %s", chooser_exc)

        scoped_input = cover_input_near_trigger(page, trigger)
        if scoped_input is not None:
            scoped_input.set_input_files(str(cover_path), timeout=3000)
            LOGGER.info("Cover uploaded via scoped cover input.")
            return

        LOGGER.warning(
            "Zhihu cover trigger was found, but no cover-specific file input was available."
        )
    except Exception as exc:
        LOGGER.warning("Cover upload failed: %s", exc)


def cover_input_near_trigger(page: Any, trigger: Any) -> Any | None:
    try:
        handle = trigger.element_handle(timeout=1000)
        if handle is None:
            return None
        input_handle = handle.evaluate_handle("""
            (node) => {
              let current = node;
              for (let depth = 0; current && depth < 7; depth += 1) {
                if (current.querySelector) {
                  const input = current.querySelector('input[type="file"]');
                  if (input) return input;
                }
                current = current.parentElement;
              }
              return null;
            }
            """)
        element = input_handle.as_element()
        return element
    except Exception:
        return None


def try_fill_body(page: Any, blocks: list[dict[str, Any]]) -> None:
    editor_selectors = [
        'textarea[placeholder*="请输入正文"]',
        'textarea[placeholder*="正文"]',
        '[contenteditable="true"][data-placeholder*="正文"]',
        '[contenteditable="true"][data-placeholder*="请输入正文"]',
        '[contenteditable="true"][placeholder*="正文"]',
        '.public-DraftEditor-content[contenteditable="true"]',
        '.ProseMirror[contenteditable="true"]',
        '[contenteditable="true"]',
    ]
    editor = first_visible_locator(page, editor_selectors, timeout_ms=2000)
    if editor is None:
        LOGGER.warning(
            "Could not find body editor. Use article_blocks.json for manual fallback."
        )
        return

    try:
        editor.click()
    except Exception as exc:
        LOGGER.warning("Could not focus body editor: %s", exc)
        return

    for block in blocks:
        block_type = str(block.get("type") or "")
        if block_type == "heading":
            text = str(block.get("text") or "").strip()
            if text:
                page.keyboard.insert_text(text)
                page.keyboard.press("Enter")
                page.keyboard.press("Enter")
        elif block_type == "paragraph":
            text = str(block.get("text") or "").strip()
            if text:
                page.keyboard.insert_text(text)
                page.keyboard.press("Enter")
                page.keyboard.press("Enter")
        elif block_type in {"formula_image", "image_block"}:
            path = Path(str(block.get("local_path") or ""))
            if not path.is_file():
                page.keyboard.insert_text(
                    str(block.get("latex") or block.get("alt") or "[图片缺失]")
                )
                page.keyboard.press("Enter")
                page.keyboard.press("Enter")
                continue
            if not try_upload_image_into_editor(page, path):
                raise ZhihuAssistantError(
                    f"Zhihu modal image upload failed; no alternate upload path will be used: {path}"
                )
        elif block_type == "divider":
            page.keyboard.insert_text("---")
            page.keyboard.press("Enter")
            page.keyboard.press("Enter")
    LOGGER.info("Body fill attempted. Please verify in Chrome.")


def try_upload_image_into_editor(page: Any, image_path: Path) -> bool:
    button_selectors = [
        'button[aria-label*="图片"]',
        'button:has-text("图片")',
        '[aria-label*="图片"]',
        "text=图片",
        'button[aria-label*="ͼƬ"]',
        'button:has-text("ͼƬ")',
        '[aria-label*="ͼƬ"]',
        "text=ͼƬ",
    ]
    try:
        button = first_visible_locator(page, button_selectors, timeout_ms=500)
        if button is not None:
            button.click()
        if upload_image_via_zhihu_upload_modal(page, image_path):
            return True
    except Exception as exc:
        LOGGER.debug("Image upload failed for %s: %s", image_path, exc)
    return False


def upload_image_via_zhihu_upload_modal(page: Any, image_path: Path) -> bool:
    modal_ready_selectors = [
        "text=上传图片",
        "text=本地图片上传",
        "text=手机扫码上传",
        "text=AI 配图",
    ]
    if first_visible_locator(page, modal_ready_selectors, timeout_ms=2500) is None:
        return False

    local_upload_selectors = [
        'button:has-text("本地图片上传")',
        "text=本地图片上传",
        '[aria-label*="本地图片上传"]',
    ]
    trigger = first_visible_locator(page, local_upload_selectors, timeout_ms=1500)
    if trigger is None:
        LOGGER.debug(
            "Zhihu upload modal opened, but local upload trigger was not found."
        )
        return False

    try:
        with page.expect_file_chooser(timeout=5000) as chooser_info:
            trigger.click()
        chooser_info.value.set_files(str(image_path))
        LOGGER.debug("Selected local image in Zhihu upload modal: %s", image_path.name)
    except Exception as chooser_exc:
        LOGGER.debug("Local upload trigger did not open file chooser: %s", chooser_exc)
        if not set_zhihu_upload_modal_file_input(page, image_path):
            return False

    if not wait_for_zhihu_image_modal_upload_ready(
        page, image_path.name, timeout_sec=35
    ):
        return False
    return click_zhihu_insert_image_button(page)


def set_zhihu_upload_modal_file_input(page: Any, image_path: Path) -> bool:
    try:
        # This stays inside the already opened Zhihu upload modal.
        # It only handles cases where Playwright misses the file chooser event.
        inputs = page.locator('input[type="file"]')
        for index in range(inputs.count() - 1, -1, -1):
            item = inputs.nth(index)
            try:
                item.set_input_files(str(image_path), timeout=1200)
                return True
            except Exception:
                continue
    except Exception:
        return False
    return False


def wait_for_zhihu_image_modal_upload_ready(
    page: Any, file_name: str, *, timeout_sec: int
) -> bool:
    bad_words = ("解析失败", "上传失败", "校验失败", "检测失败", "文件解析失败", "失败")
    busy_words = (
        "上传中",
        "解析中",
        "校验中",
        "检测中",
        "处理中",
        "加载中",
        "正在上传",
        "正在解析",
        "正在校验",
        "正在检测",
        "正在处理",
    )
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        text = zhihu_visible_body_text(page)
        if any(word in text for word in bad_words):
            LOGGER.warning(
                "Zhihu image upload failed for %s: %s",
                file_name,
                compact_log_text(text),
            )
            return False
        if any(word in text for word in busy_words) or re.search(
            r"\b\d{1,3}\s*%", text
        ):
            LOGGER.debug(
                "Zhihu image still processing | %s | %s",
                file_name,
                compact_log_text(text),
            )
            page.wait_for_timeout(700)
            continue
        if "已上传" in text and ("插入图片" in text or "插入" in text):
            button = zhihu_insert_image_button(page)
            try:
                if button is not None and button.is_enabled(timeout=250):
                    return True
            except Exception:
                pass
        page.wait_for_timeout(500)
    LOGGER.warning(
        "Timed out waiting for Zhihu image upload to become ready: %s", file_name
    )
    return False


def zhihu_insert_image_button(page: Any) -> Any | None:
    selectors = [
        'button:has-text("插入图片")',
        "text=插入图片",
        'button:has-text("插入")',
    ]
    for selector in selectors:
        locator = page.locator(selector).last
        try:
            if locator.count() and locator.is_visible(timeout=250):
                return locator
        except Exception:
            continue
    return None


def click_zhihu_insert_image_button(page: Any) -> bool:
    button = zhihu_insert_image_button(page)
    if button is None:
        return False
    try:
        button.click()
        page.wait_for_timeout(800)
        return True
    except Exception as exc:
        LOGGER.debug("Failed clicking Zhihu insert image button: %s", exc)
        return False


def zhihu_visible_body_text(page: Any) -> str:
    try:
        text = page.locator("body").inner_text(timeout=500)
        return str(text or "")
    except Exception:
        return ""


def compact_log_text(text: str, limit: int = 240) -> str:
    compact = " ".join(str(text or "").split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1] + "…"


def orchestrate(config: Config) -> dict[str, Any]:
    canonical = read_json(config.canonical_path)
    if not isinstance(canonical, dict):
        raise ZhihuAssistantError(
            f"Canonical JSON must be an object: {config.canonical_path}"
        )

    report: dict[str, Any] = {
        "generated_at": now_iso(),
        "ids": list(config.ids),
        "canonical": str(config.canonical_path),
        "output_dir": str(config.output_dir),
        "package_only": config.package_only,
        "items": [],
    }

    for item_id in config.ids:
        record = canonical[item_id]
        try:
            result = package_one_item(item_id, record, config)
            report["items"].append(asdict(result))
            if not config.package_only:
                fill_zhihu_draft(result, config)
        except Exception as exc:
            LOGGER.exception("Failed processing %s", item_id)
            failed = PackageResult(
                id=item_id,
                title=item_id,
                output_dir=str(config.output_dir / item_id),
                cover_path="",
                article_blocks_path="",
                preview_html_path="",
                body_markdown_path="",
                body_html_path="",
                manifest_path="",
                checklist_path="",
                formula_asset_count=0,
                missing_asset_count=0,
                status="failed",
                error=str(exc),
            )
            report["items"].append(asdict(failed))
            raise
        finally:
            write_json(config.report_path, report)

    return report


def main() -> int:
    configure_console_encoding()
    args = parse_args()
    try:
        canonical_path = Path(args.canonical_json).resolve()
        canonical = read_json(canonical_path)
        if not isinstance(canonical, dict):
            raise ZhihuAssistantError(
                f"Canonical JSON must be an object: {canonical_path}"
            )
        config = build_config(args, canonical)
        configure_logging(config.log_level)
        LOGGER.info("Zhihu target IDs | %s", ", ".join(config.ids))
        report = orchestrate(config)
        success_count = sum(
            1 for item in report["items"] if item.get("status") == "success"
        )
        LOGGER.info(
            "Zhihu assistant complete | success=%d/%d | report=%s",
            success_count,
            len(config.ids),
            config.report_path,
        )
        return 0
    except ZhihuAssistantError as exc:
        LOGGER.error("%s", exc)
        return 1
    except KeyboardInterrupt:
        LOGGER.error("Interrupted by user.")
        return 130
    except Exception:
        LOGGER.exception("Unexpected Zhihu assistant failure")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
