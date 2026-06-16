#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate a Bilibili article package for selected conclusion IDs and optionally
open Bilibili Creator Center for semi-automatic draft filling.

The script keeps final publishing manual. It prepares Zhihu-style article
blocks, uploads/fills what it can through a local Chrome session, and leaves
the user to review before clicking publish.

Examples:
    python scripts/bilibili_publish_assistant.py G003 --package-only
    python scripts/bilibili_publish_assistant.py G003
    python scripts/bilibili_publish_assistant.py G003 --bilibili-url https://member.bilibili.com/platform/upload/text/new-edit
"""

from __future__ import annotations

import argparse
import html
import json
import logging
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Sequence

import channels_publish_assistant as channels
import zhihu_publish_assistant as zhihu

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

DEFAULT_CANONICAL_PATH = PROJECT_ROOT / "data" / "content" / "canonical_content_v2.json"
DEFAULT_PUBLIC_DIR = PROJECT_ROOT / "public"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "build" / "bilibili_posts"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports" / "bilibili_publish_assistant_report.json"
DEFAULT_MINICODE_PATH = PROJECT_ROOT / "assets" / "figures" / "MiniCode.png"
DEFAULT_CHROME_PATH = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
DEFAULT_PROFILE_DIR = PROJECT_ROOT / "build" / "bilibili_chrome_profile"
DEFAULT_BILIBILI_URL = "https://member.bilibili.com/platform/upload/text/new-edit"
DEFAULT_WECHAT_DRAFTS_DIR = PROJECT_ROOT / "build" / "wechat_drafts"
DEFAULT_CARD_SIZE = "1080x1440"
DEFAULT_CARD_DPR = 1.0
DEFAULT_COVER_SIZE = "1200x675"
DEFAULT_WECHAT_SHOT_WIDTH = 720
DEFAULT_WECHAT_SHOT_DPR = 2.0
BILIBILI_TITLE_LIMIT = 30
BILIBILI_TOPIC_LIMIT = 10
BILIBILI_IMAGE_LIMIT = 9
LOGGER = logging.getLogger("bilibili_publish_assistant")

BILIBILI_NEW_CREATION_SELECTOR = "#app > div > div.new-creation > button"
BILIBILI_NEW_CREATION_STABLE_SELECTORS = (
    "button.new-creation_button",
    ".new-creation button.new-creation_button",
    ".read-draft .new-creation button.new-creation_button",
    "button.vui_button.vui_button--blue.new-creation_button",
)
BILIBILI_TITLE_INPUT_SELECTOR = (
    "#app > div.body > div.main > div.content > div.title-input.title > textarea"
)
BILIBILI_CONTENT_EDITOR_SELECTOR = (
    "#app > div.body > div.main > div.content > div.editor-container.eva3-web-editor "
    "> div.tiptap.ProseMirror.eva3-editor"
)
BILIBILI_EDITOR_FRAME_URL_FRAGMENT = "member.bilibili.com/york/read-editor"
BILIBILI_IMAGE_TOOLBAR_SELECTOR = "#app > div.header > div > eva3-toolbar-image"
BILIBILI_TITLE_FIELD_SELECTORS = (
    BILIBILI_TITLE_INPUT_SELECTOR,
    "textarea.title-input__inner",
    "textarea[placeholder*='请输入标题']",
    "input[placeholder*='标题']",
    "textarea[placeholder*='标题']",
    "[contenteditable='true'][data-placeholder*='标题']",
    "[role='textbox'][aria-label*='标题']",
)
BILIBILI_BODY_EDITOR_SELECTORS = (
    BILIBILI_CONTENT_EDITOR_SELECTOR,
    ".tiptap.ProseMirror.eva3-editor",
    "div.ProseMirror.eva3-editor",
    "[contenteditable='true'][data-placeholder*='请输入正文']",
    "[contenteditable='true'][placeholder*='请输入正文']",
    ".ProseMirror[contenteditable='true']",
    "[contenteditable='true']",
    "[role='textbox']",
)


class BilibiliAssistantError(RuntimeError):
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
    bilibili_url: str
    card_size: tuple[int, int]
    card_dpr: float
    cover_size: tuple[int, int]
    wechat_drafts_dir: Path
    content_mode: str
    wechat_shot_width: int
    wechat_shot_dpr: float
    force_cover: bool
    section_keys: tuple[str, ...]
    package_only: bool
    force: bool
    editor_wait_sec: int
    upload_wait_sec: int
    review_wait_sec: int
    log_level: str


@dataclass
class PackageResult:
    id: str
    title: str
    output_dir: str
    cover_path: str
    article_blocks_path: str
    manifest_path: str
    preview_html_path: str
    body_markdown_path: str
    body_html_path: str
    checklist_path: str
    post_payload_path: str
    formula_asset_count: int
    missing_asset_count: int
    upload_asset_count: int
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


def parse_size(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"\s*(\d+)x(\d+)\s*", value.lower())
    if not match:
        raise argparse.ArgumentTypeError("expected size like 1080x1440")
    width = int(match.group(1))
    height = int(match.group(2))
    if width < 360 or height < 480:
        raise argparse.ArgumentTypeError("card size is too small")
    aspect = max(width, height) / min(width, height)
    if aspect > 2.0:
        raise argparse.ArgumentTypeError("article card ratio should not exceed 1:2 or 2:1")
    return width, height


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and optionally fill a Bilibili article draft.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/bilibili_publish_assistant.py G003 --package-only\n"
            "  python scripts/bilibili_publish_assistant.py G003\n"
            "  python scripts/bilibili_publish_assistant.py G003 --card-size 900x1200\n"
        ),
    )
    parser.add_argument("ids", nargs="+", help="Conclusion IDs, e.g. G003 or G003,T008.")
    parser.add_argument("--canonical-json", default=str(DEFAULT_CANONICAL_PATH))
    parser.add_argument("--public-dir", default=str(DEFAULT_PUBLIC_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--report", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--minicode", default=str(DEFAULT_MINICODE_PATH))
    parser.add_argument("--wechat-drafts-dir", default=str(DEFAULT_WECHAT_DRAFTS_DIR))
    parser.add_argument("--chrome", default=str(DEFAULT_CHROME_PATH))
    parser.add_argument("--profile-dir", default=str(DEFAULT_PROFILE_DIR))
    parser.add_argument("--bilibili-url", default=DEFAULT_BILIBILI_URL)
    parser.add_argument(
        "--card-size",
        type=parse_size,
        default=parse_size(DEFAULT_CARD_SIZE),
        help="Rendered image size. Default: 1080x1440.",
    )
    parser.add_argument("--card-dpr", type=float, default=DEFAULT_CARD_DPR)
    parser.add_argument(
        "--cover-size",
        type=parse_size,
        default=parse_size(DEFAULT_COVER_SIZE),
        help="Generated article cover size. Default: 1200x675.",
    )
    parser.add_argument(
        "--content-mode",
        choices=("wechat-image", "blocks"),
        default="wechat-image",
        help="Match Zhihu assistant content mode. Default: wechat-image.",
    )
    parser.add_argument("--wechat-shot-width", type=int, default=DEFAULT_WECHAT_SHOT_WIDTH)
    parser.add_argument("--wechat-shot-dpr", type=float, default=DEFAULT_WECHAT_SHOT_DPR)
    parser.add_argument("--force-cover", action="store_true")
    parser.add_argument(
        "--section-keys",
        nargs="*",
        default=list(zhihu.DEFAULT_SECTION_KEYS),
        help="Section keys for --content-mode blocks. Defaults to the Zhihu assistant sections.",
    )
    parser.add_argument(
        "--package-only",
        action="store_true",
        help="Only generate files. Do not open Chrome or fill Bilibili.",
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
        help="Seconds to wait for Bilibili after login. 0 means wait forever. Default: 0.",
    )
    parser.add_argument(
        "--upload-wait-sec",
        type=int,
        default=90,
        help="Seconds to wait for image upload/processing to settle. Default: 90.",
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


def read_json(path: Path, default: Any = None) -> Any:
    try:
        return channels.read_json(path, default=default)
    except Exception as exc:
        raise BilibiliAssistantError(str(exc)) from exc


def write_text(path: Path, text: str) -> None:
    channels.write_text(path, text)


def write_json(path: Path, data: Any) -> None:
    channels.write_json(path, data)


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def clean_text(text: Any) -> str:
    return channels.clean_text(text)


def truncate_text(text: str, limit: int) -> str:
    return channels.truncate_text(text, limit)


def dedupe_keep_order(values: Iterable[str]) -> list[str]:
    return channels.dedupe_keep_order(values)


def build_config(args: argparse.Namespace, canonical: dict[str, Any]) -> Config:
    try:
        ids = channels.normalize_ids(args.ids)
    except Exception as exc:
        raise BilibiliAssistantError(str(exc)) from exc
    missing = [item_id for item_id in ids if item_id not in canonical]
    if missing:
        raise BilibiliAssistantError(
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
        bilibili_url=str(args.bilibili_url),
        card_size=args.card_size,
        card_dpr=max(1.0, float(args.card_dpr)),
        cover_size=args.cover_size,
        wechat_drafts_dir=Path(args.wechat_drafts_dir).resolve(),
        content_mode=str(args.content_mode),
        wechat_shot_width=max(360, int(args.wechat_shot_width)),
        wechat_shot_dpr=max(1.0, float(args.wechat_shot_dpr)),
        force_cover=bool(args.force_cover),
        section_keys=tuple(args.section_keys or zhihu.DEFAULT_SECTION_KEYS),
        package_only=bool(args.package_only),
        force=bool(args.force),
        editor_wait_sec=max(0, int(args.editor_wait_sec)),
        upload_wait_sec=max(5, int(args.upload_wait_sec)),
        review_wait_sec=max(0, int(args.review_wait_sec)),
        log_level=str(args.log_level).upper(),
    )


def zhihu_config_for(config: Config) -> zhihu.Config:
    return zhihu.Config(
        ids=config.ids,
        canonical_path=config.canonical_path,
        public_dir=config.public_dir,
        output_dir=config.output_dir,
        report_path=config.report_path,
        minicode_path=config.minicode_path,
        wechat_drafts_dir=config.wechat_drafts_dir,
        chrome_path=config.chrome_path,
        profile_dir=config.profile_dir,
        zhihu_write_url="",
        cover_size=config.cover_size,
        content_mode=config.content_mode,
        wechat_shot_width=config.wechat_shot_width,
        wechat_shot_dpr=config.wechat_shot_dpr,
        force_cover=config.force_cover,
        package_only=config.package_only,
        editor_wait_sec=max(5, config.editor_wait_sec),
        review_wait_sec=config.review_wait_sec,
        section_keys=config.section_keys,
        log_level=config.log_level,
    )


def bilibili_title(record: dict[str, Any], item_id: str) -> str:
    title = zhihu.zhihu_title(record, item_id)
    if len(clean_text(title)) <= BILIBILI_TITLE_LIMIT:
        return title
    base = clean_text(channels.record_title(record, item_id))
    compact = re.sub(r"\s+", "", base)
    short = re.split(r"[：:，,（(]", compact, maxsplit=1)[0].strip()
    candidates = [f"{item_id} {short}", f"{item_id} {compact}"]
    for candidate in candidates:
        value = clean_text(candidate)
        if value and len(value) <= BILIBILI_TITLE_LIMIT:
            return value
    return truncate_text(candidates[0] if candidates else item_id, BILIBILI_TITLE_LIMIT)


def bilibili_topics(record: dict[str, Any], item_id: str) -> list[str]:
    topics = zhihu.zhihu_topics(record, item_id)
    cleaned: list[str] = []
    for value in topics:
        topic = re.sub(r"^[#＃]+|[#＃]+$", "", clean_text(value))
        topic = re.sub(r"\s+", "", topic)
        if topic and len(topic) <= 18:
            cleaned.append(topic)
    return dedupe_keep_order(cleaned)[:BILIBILI_TOPIC_LIMIT]


def bilibili_topic_text(topics: Sequence[str]) -> str:
    return " ".join(f"#{topic}#" for topic in topics if clean_text(topic))


def render_checklist(item_id: str, result: PackageResult) -> str:
    topics_text = "、".join(result.topics)
    return f"""# B站文章发布检查清单：{item_id}

1. 打开 `preview.html` 检查封面、标题、正文和公式/分段图片顺序。
2. 确认 `assets_manifest.json` 中 `missing_asset_count` 为 {result.missing_asset_count}；若不为 0，发布前需要补齐资源。
3. 运行不带 `--package-only` 的脚本，让 Chrome 打开 B站文章发布页。
4. 登录后检查标题、正文、公式图片、话题和最后一张小程序引流卡。
5. 确认无误后人工点击发布；脚本默认不会点击最终发布按钮。

B站标题：`{result.title}`

生成文件：

- 封面：`{result.cover_path}`
- 正文 blocks：`{result.article_blocks_path}`
- 正文 Markdown：`{result.body_markdown_path}`
- 正文 HTML：`{result.body_html_path}`
- 资源清单：`{result.manifest_path}`
- 预览：`{result.preview_html_path}`

推荐话题：{topics_text}
"""


def package_one_item(item_id: str, record: dict[str, Any], config: Config) -> PackageResult:
    output_dir = config.output_dir / item_id
    output_dir.mkdir(parents=True, exist_ok=True)
    title = bilibili_title(record, item_id)
    topics = bilibili_topics(record, item_id)
    zhihu_config = zhihu_config_for(config)
    LOGGER.info("Generating Bilibili package | %s", item_id)

    cover_path = output_dir / "cover.png"
    article_blocks_path = output_dir / "article_blocks.json"
    manifest_path = output_dir / "manifest.json"
    preview_html_path = output_dir / "preview.html"
    body_md_path = output_dir / "body.md"
    body_html_path = output_dir / "body.html"
    assets_manifest_path = output_dir / "assets_manifest.json"
    checklist_path = output_dir / "bilibili_publish_checklist.md"
    post_payload_path = output_dir / "bilibili_post.json"

    zhihu.generate_cover(record, item_id=item_id, config=zhihu_config, output_path=cover_path)

    asset_refs: list[zhihu.AssetRef] = []
    if config.content_mode == "wechat-image":
        image_blocks = zhihu.build_wechat_image_blocks(
            record,
            item_id=item_id,
            config=zhihu_config,
            output_dir=output_dir,
        )
        blocks = [
            zhihu.build_zhihu_required_text_block(record, item_id),
            *image_blocks,
            zhihu.build_zhihu_ebook_text_block(item_id),
        ]
    else:
        blocks = zhihu.build_article_blocks(
            record,
            item_id=item_id,
            config=zhihu_config,
            asset_refs=asset_refs,
        )

    upload_assets = zhihu.prepare_zhihu_upload_assets(blocks, output_dir)
    all_formula_refs = zhihu.collect_all_formula_refs(record, config.public_dir)
    by_url = {ref.asset_url: ref for ref in all_formula_refs}
    for ref in asset_refs:
        by_url.setdefault(ref.asset_url, ref)
    formula_refs = list(by_url.values())
    missing = [ref for ref in formula_refs if not ref.exists]

    body_md = zhihu.render_body_markdown(blocks)
    body_html = zhihu.render_body_html(blocks)
    preview_html = zhihu.render_preview_html(title, body_html, cover_path)

    write_json(
        article_blocks_path,
        {
            "id": item_id,
            "title": title,
            "zhihu_title": zhihu.zhihu_title(record, item_id),
            "cover_path": str(cover_path),
            "topics": topics,
            "generated_at": now_iso(),
            "content_mode": config.content_mode,
            "blocks": blocks,
        },
    )
    write_text(body_md_path, body_md)
    write_text(body_html_path, body_html + "\n")
    write_text(preview_html_path, preview_html)

    assets_manifest = {
        "id": item_id,
        "title": title,
        "zhihu_title": zhihu.zhihu_title(record, item_id),
        "generated_at": now_iso(),
        "cover": {"path": str(cover_path), "exists": cover_path.is_file()},
        "topics": topics,
        "content_mode": config.content_mode,
        "formula_asset_count": len(formula_refs),
        "missing_asset_count": len(missing),
        "upload_asset_count": len(upload_assets),
        "assets": [asdict(ref) for ref in formula_refs],
        "upload_assets": upload_assets,
        "missing_assets": [asdict(ref) for ref in missing],
    }
    write_json(assets_manifest_path, assets_manifest)

    payload = {
        "id": item_id,
        "title": title,
        "zhihu_title": zhihu.zhihu_title(record, item_id),
        "generated_at": now_iso(),
        "bilibili_url": config.bilibili_url,
        "content_mode": config.content_mode,
        "cover_path": str(cover_path),
        "article_blocks_path": str(article_blocks_path),
        "body_markdown_path": str(body_md_path),
        "body_html_path": str(body_html_path),
        "manifest_path": str(assets_manifest_path),
        "blocks": blocks,
        "topics": topics,
        "minicode_path": str(config.minicode_path),
    }
    write_json(post_payload_path, payload)

    manifest = {
        "id": item_id,
        "title": title,
        "zhihu_title": zhihu.zhihu_title(record, item_id),
        "generated_at": now_iso(),
        "output_dir": str(output_dir),
        "content_mode": config.content_mode,
        "cover_path": str(cover_path),
        "article_blocks_path": str(article_blocks_path),
        "body_markdown_path": str(body_md_path),
        "body_html_path": str(body_html_path),
        "preview_html_path": str(preview_html_path),
        "post_payload_path": str(post_payload_path),
        "assets_manifest_path": str(assets_manifest_path),
        "formula_asset_count": len(formula_refs),
        "missing_asset_count": len(missing),
        "upload_asset_count": len(upload_assets),
        "topics": topics,
        "minicode": {"path": str(config.minicode_path), "exists": config.minicode_path.is_file()},
    }
    write_json(manifest_path, manifest)

    result = PackageResult(
        id=item_id,
        title=title,
        output_dir=str(output_dir),
        cover_path=str(cover_path),
        article_blocks_path=str(article_blocks_path),
        manifest_path=str(assets_manifest_path),
        preview_html_path=str(preview_html_path),
        body_markdown_path=str(body_md_path),
        body_html_path=str(body_html_path),
        checklist_path=str(checklist_path),
        post_payload_path=str(post_payload_path),
        formula_asset_count=len(formula_refs),
        missing_asset_count=len(missing),
        upload_asset_count=len(upload_assets),
        topics=topics,
    )
    if missing:
        result.warnings.append(f"{len(missing)} referenced asset(s) are missing.")
    write_text(checklist_path, render_checklist(item_id, result))
    return result


def import_playwright() -> Any:
    try:
        return channels.import_playwright()
    except Exception as exc:
        raise BilibiliAssistantError(
            "Playwright is required for draft filling. Install the Python package first."
        ) from exc


def first_visible_locator(page: Any, selectors: Sequence[str], *, timeout_ms: int = 1200) -> Any | None:
    return channels.first_visible_locator(page, selectors, timeout_ms=timeout_ms)


def bilibili_scope_label(scope: Any) -> str:
    return str(getattr(scope, "url", "") or "main-page")


def iter_bilibili_editor_scopes(page: Any) -> list[Any]:
    frames = list(getattr(page, "frames", []) or [])
    preferred = [
        frame
        for frame in frames
        if BILIBILI_EDITOR_FRAME_URL_FRAGMENT in str(getattr(frame, "url", "") or "")
    ]
    main = [page]
    rest = [
        frame
        for frame in frames
        if frame not in preferred and frame is not getattr(page, "main_frame", None)
    ]
    return [*preferred, *main, *rest]


def first_visible_locator_in_scopes(
    page: Any,
    selectors: Sequence[str],
    *,
    timeout_ms: int = 1200,
) -> tuple[Any, Any, str] | None:
    deadline = time.monotonic() + max(0.2, timeout_ms / 1000)
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        for scope in iter_bilibili_editor_scopes(page):
            for selector in selectors:
                try:
                    locator = scope.locator(selector).first
                    locator.wait_for(state="visible", timeout=250)
                    return scope, locator, selector
                except Exception as exc:
                    last_error = exc
                    continue
        page.wait_for_timeout(150)
    if last_error:
        LOGGER.debug("No visible Bilibili locator in frames: %s", last_error)
    return None


def wait_for_visible_locator(page: Any, selectors: Sequence[str], *, timeout_ms: int = 12000) -> Any | None:
    found = first_visible_locator_in_scopes(page, selectors, timeout_ms=timeout_ms)
    return found[1] if found else None


def bilibili_dom_selector_state(page: Any) -> dict[str, Any]:
    script = """
    ({ titleSelectors, editorSelectors }) => {
      const isVisible = (el) => {
        if (!el) return false;
        const rect = el.getBoundingClientRect();
        const style = window.getComputedStyle(el);
        return rect.width > 0 && rect.height > 0
          && style.display !== "none" && style.visibility !== "hidden";
      };
      const find = (selectors) => {
        for (const selector of selectors) {
          try {
            const el = document.querySelector(selector);
            if (el) return { selector, visible: isVisible(el) };
          } catch (_) {}
        }
        return null;
      };
      return { title: find(titleSelectors), editor: find(editorSelectors) };
    }
    """
    args = {
        "titleSelectors": list(BILIBILI_TITLE_FIELD_SELECTORS),
        "editorSelectors": list(BILIBILI_BODY_EDITOR_SELECTORS),
    }
    for scope in iter_bilibili_editor_scopes(page):
        try:
            result = scope.evaluate(script, args)
        except Exception:
            continue
        if isinstance(result, dict) and (result.get("title") or result.get("editor")):
            result["scope"] = bilibili_scope_label(scope)
            return result
    return {}


def visible_body_text(page: Any) -> str:
    try:
        return str(page.locator("body").inner_text(timeout=700) or "")
    except Exception:
        return ""


def compact_log_text(text: str, limit: int = 240) -> str:
    compact = " ".join(str(text or "").split())
    if len(compact) <= limit:
        return compact
    return compact[: max(0, limit - 3)] + "..."


def is_bilibili_new_edit_page(page: Any) -> bool:
    current_url = str(getattr(page, "url", "") or "")
    return "member.bilibili.com/platform/upload/text/new-edit" in current_url


def wait_for_bilibili_ready(page: Any, *, timeout_sec: int) -> bool:
    deadline = None if timeout_sec <= 0 else time.monotonic() + timeout_sec
    selectors = [
        BILIBILI_NEW_CREATION_SELECTOR,
        *BILIBILI_TITLE_FIELD_SELECTORS,
        *BILIBILI_BODY_EDITOR_SELECTORS,
        "text=新的创作",
        "text=新建创作",
        "text=发布文章",
        "text=文章",
        "text=图片",
        "text=上传图片",
    ]
    last_notice = 0.0
    while True:
        if first_visible_locator(page, selectors, timeout_ms=1000) is not None:
            return True
        body_text = visible_body_text(page)
        current_url = str(getattr(page, "url", "") or "")
        if is_bilibili_new_edit_page(page):
            LOGGER.info("Detected Bilibili article editor by new-edit URL.")
            return True
        if "member.bilibili.com/platform/upload/text" in current_url and any(
            marker in body_text
            for marker in (
                "创作中心",
                "专栏投稿",
                "新的创作",
                "草稿箱",
                "图片格式",
                "可发专栏数",
            )
        ):
            LOGGER.info("Detected Bilibili article page by URL/body text.")
            return True
        if deadline is not None and time.monotonic() >= deadline:
            return False
        now = time.monotonic()
        if now - last_notice >= 20:
            LOGGER.warning(
                "Still waiting for Bilibili article page. Current url=%s text=%s",
                current_url,
                compact_log_text(body_text, limit=120),
            )
            last_notice = now
        page.wait_for_timeout(1000)


def click_by_dom_text(page: Any, texts: Sequence[str], *, max_text_len: int = 120) -> bool:
    clean_texts = [clean_text(text) for text in texts if clean_text(text)]
    if not clean_texts:
        return False
    try:
        result = page.evaluate(
            """
            ({ texts, maxTextLen }) => {
              const normalize = (value) => String(value || "").replace(/\\s+/g, " ").trim();
              const isVisible = (el) => {
                const rect = el.getBoundingClientRect();
                const style = el.ownerDocument.defaultView.getComputedStyle(el);
                return rect.width > 0
                  && rect.height > 0
                  && style.display !== "none"
                  && style.visibility !== "hidden";
              };
              const click = (el) => {
                el.scrollIntoView?.({ block: "center", inline: "nearest" });
                el.dispatchEvent(new MouseEvent("mousedown", { bubbles: true, composed: true }));
                el.dispatchEvent(new MouseEvent("mouseup", { bubbles: true, composed: true }));
                el.click?.();
              };
              const candidates = Array.from(document.querySelectorAll(
                "button, [role='button'], [class*='button'], [class*='btn'], li, div, span"
              ))
                .filter((el, index, arr) => arr.indexOf(el) === index)
                .filter((el) => {
                  if (!isVisible(el)) return false;
                  const text = normalize(el.textContent);
                  const rect = el.getBoundingClientRect();
                  return text
                    && text.length <= maxTextLen
                    && texts.some((target) => text.includes(target))
                    && rect.width >= 18
                    && rect.height >= 14
                    && rect.height <= 220;
                })
                .sort((a, b) => {
                  const aPreferred = a.matches("button, [role='button'], [class*='button'], [class*='btn']") ? 0 : 1;
                  const bPreferred = b.matches("button, [role='button'], [class*='button'], [class*='btn']") ? 0 : 1;
                  if (aPreferred !== bPreferred) return aPreferred - bPreferred;
                  const ar = a.getBoundingClientRect();
                  const br = b.getBoundingClientRect();
                  return ar.top === br.top ? ar.left - br.left : ar.top - br.top;
                });
              if (!candidates.length) return false;
              click(candidates[0]);
              return true;
            }
            """,
            {"texts": clean_texts, "maxTextLen": max_text_len},
        )
    except Exception as exc:
        LOGGER.debug("Could not click Bilibili element by text: %s", exc)
        return False
    return bool(result)


def click_bilibili_new_creation(page: Any) -> bool:
    script = """
    ({ exactSelector, stableSelectors }) => {
      const normalize = (value) => String(value || "").replace(/\\s+/g, " ").trim();
      const isVisible = (el) => {
        const rect = el.getBoundingClientRect();
        const style = window.getComputedStyle(el);
        return rect.width > 0 && rect.height > 0
          && style.display !== "none" && style.visibility !== "hidden";
      };
      const click = (button, method) => {
        button.scrollIntoView?.({ block: "center", inline: "nearest" });
        button.focus?.();
        button.dispatchEvent(new MouseEvent("pointerdown", { bubbles: true, composed: true }));
        button.dispatchEvent(new MouseEvent("mousedown", { bubbles: true, composed: true }));
        button.dispatchEvent(new MouseEvent("pointerup", { bubbles: true, composed: true }));
        button.dispatchEvent(new MouseEvent("mouseup", { bubbles: true, composed: true }));
        button.click?.();
        return { ok: true, method, text: normalize(button.textContent) };
      };

      const exact = document.querySelector(exactSelector);
      if (exact && isVisible(exact)) return click(exact, "exact");

      for (const selector of stableSelectors) {
        const stable = document.querySelector(selector);
        if (stable && isVisible(stable)) return click(stable, selector);
      }

      const relaxed = document.querySelector("#app div.new-creation button");
      if (relaxed && isVisible(relaxed)) return click(relaxed, "relaxed");

      const candidates = Array.from(document.querySelectorAll("button, [role='button'], [class*='button'], [class*='btn']"))
        .filter((el) => isVisible(el))
        .map((el) => ({ el, text: normalize(el.textContent) }))
        .filter((item) => item.text.includes("新的创作") || item.text.includes("新建创作"))
        .sort((a, b) => {
          const ar = a.el.getBoundingClientRect();
          const br = b.el.getBoundingClientRect();
          return ar.top === br.top ? ar.left - br.left : ar.top - br.top;
        });
      if (candidates.length) return click(candidates[0].el, "text");

      return { ok: false, bodyText: normalize(document.body?.innerText).slice(0, 180) };
    }
    """
    last_result: Any = None
    for frame in page.frames:
        try:
            result = frame.evaluate(
                script,
                {
                    "exactSelector": BILIBILI_NEW_CREATION_SELECTOR,
                    "stableSelectors": list(BILIBILI_NEW_CREATION_STABLE_SELECTORS),
                },
            )
        except Exception as exc:
            LOGGER.debug("Could not inspect Bilibili new creation frame %s: %s", getattr(frame, "url", ""), exc)
            continue
        last_result = result
        if isinstance(result, dict) and result.get("ok"):
            page.wait_for_timeout(800)
            LOGGER.info(
                "Clicked Bilibili new creation button via %s selector/text in frame %s.",
                result.get("method"),
                getattr(frame, "url", ""),
            )
            return True
    LOGGER.warning(
        "Bilibili new creation button was not found by exact/relaxed/text selector. Last result=%s",
        last_result,
    )
    return False


def log_bilibili_creation_button_candidates(page: Any) -> None:
    script = """
    () => {
      const normalize = (value) => String(value || "").replace(/\\s+/g, " ").trim();
      return Array.from(document.querySelectorAll("button, [role='button'], [class*='button'], [class*='btn']"))
        .map((el) => {
          const rect = el.getBoundingClientRect();
          const style = window.getComputedStyle(el);
          return {
            tag: String(el.tagName || "").toLowerCase(),
            text: normalize(el.textContent),
            className: String(el.className || ""),
            id: String(el.id || ""),
            visible: rect.width > 0 && rect.height > 0 && style.display !== "none" && style.visibility !== "hidden",
            rect: { x: Math.round(rect.x), y: Math.round(rect.y), w: Math.round(rect.width), h: Math.round(rect.height) },
          };
        })
        .filter((item) => item.text.includes("创作") || item.className.includes("creation"))
        .slice(0, 12);
    }
    """
    summaries: list[Any] = []
    for frame in page.frames:
        try:
            result = frame.evaluate(script)
        except Exception:
            continue
        if result:
            summaries.append({"frame": getattr(frame, "url", ""), "items": result})
    LOGGER.warning("Bilibili creation button candidates: %s", summaries)


def wait_for_bilibili_article_editor(page: Any, *, timeout_sec: int = 15) -> bool:
    deadline = time.monotonic() + max(1, timeout_sec)
    selectors = [*BILIBILI_TITLE_FIELD_SELECTORS, *BILIBILI_BODY_EDITOR_SELECTORS]
    while time.monotonic() < deadline:
        found = first_visible_locator_in_scopes(page, selectors, timeout_ms=800)
        if found is not None:
            scope, _, selector = found
            LOGGER.info(
                "Bilibili article editor is ready in frame %s via selector %s.",
                bilibili_scope_label(scope),
                selector,
            )
            return True
        state = bilibili_dom_selector_state(page)
        if state.get("title") or state.get("editor"):
            LOGGER.info("Bilibili article editor is ready by DOM selector: %s", state)
            return True
        page.wait_for_timeout(700)
    LOGGER.warning(
        "Bilibili article editor did not appear after clicking new creation. Current url=%s text=%s",
        str(getattr(page, "url", "") or ""),
        compact_log_text(visible_body_text(page), limit=160),
    )
    return False


def open_bilibili_article_editor(page: Any) -> bool:
    if is_bilibili_new_edit_page(page):
        return wait_for_bilibili_article_editor(page, timeout_sec=30)
    if first_visible_locator_in_scopes(
        page,
        [*BILIBILI_TITLE_FIELD_SELECTORS, *BILIBILI_BODY_EDITOR_SELECTORS],
        timeout_ms=1000,
    ) is not None:
        return True
    if click_bilibili_new_creation(page):
        if wait_for_bilibili_article_editor(page, timeout_sec=15):
            return True
    if first_visible_locator(page, [BILIBILI_NEW_CREATION_SELECTOR], timeout_ms=1200) is not None:
        try:
            page.locator(BILIBILI_NEW_CREATION_SELECTOR).first.click(timeout=2500)
            page.wait_for_timeout(1200)
            LOGGER.info("Clicked Bilibili new creation button.")
            if wait_for_bilibili_article_editor(page, timeout_sec=15):
                return True
        except Exception as exc:
            LOGGER.debug("Could not click Bilibili new creation button: %s", exc)
    clicked = click_by_dom_text(
        page,
        ["新的创作", "新建创作", "开始创作", "写文章"],
        max_text_len=80,
    )
    if clicked:
        page.wait_for_timeout(1000)
    opened = wait_for_bilibili_article_editor(page, timeout_sec=15)
    if not opened:
        log_bilibili_creation_button_candidates(page)
    return opened


def upload_images_via_file_input(page: Any, image_paths: Sequence[Path]) -> bool:
    paths = [str(path) for path in image_paths if path.is_file()]
    if not paths:
        LOGGER.warning("No uploadable image files found.")
        return False
    for scope in iter_bilibili_editor_scopes(page):
        try:
            inputs = scope.locator('input[type="file"]')
            count = inputs.count()
        except Exception:
            continue
        for index in range(count - 1, -1, -1):
            item = inputs.nth(index)
            try:
                accept = str(item.get_attribute("accept", timeout=500) or "").lower()
            except Exception:
                accept = ""
            if accept and not any(token in accept for token in ("image", ".png", ".jpg", ".jpeg", ".webp")):
                continue
            try:
                item.set_input_files(paths, timeout=5000)
                LOGGER.info(
                    "Selected %d Bilibili image(s) via file input in frame %s.",
                    len(paths),
                    bilibili_scope_label(scope),
                )
                return True
            except Exception as exc:
                LOGGER.debug(
                    "Bilibili file input upload failed at index %d in %s: %s",
                    index,
                    bilibili_scope_label(scope),
                    exc,
                )
    return False


def bilibili_image_toolbar_exists(page: Any) -> bool:
    script = """
    (selector) => {
      const host = document.querySelector(selector);
      const icon = host?.shadowRoot?.querySelector("eva3-dropdown > eva3-icon");
      const svg = icon?.shadowRoot?.querySelector("svg");
      return Boolean(svg || icon || host);
    }
    """
    for scope in iter_bilibili_editor_scopes(page):
        try:
            if scope.evaluate(script, BILIBILI_IMAGE_TOOLBAR_SELECTOR):
                return True
        except Exception:
            continue
    return False


def click_bilibili_image_toolbar(page: Any) -> bool:
    script = """
    (selector) => {
      const host = document.querySelector(selector);
      const icon = host?.shadowRoot?.querySelector("eva3-dropdown > eva3-icon");
      const svg = icon?.shadowRoot?.querySelector("svg");
      const target = svg || icon || host;
      if (!target) return false;
      target.scrollIntoView?.({ block: "center", inline: "nearest" });
      target.dispatchEvent(new MouseEvent("mousedown", { bubbles: true, composed: true }));
      target.dispatchEvent(new MouseEvent("mouseup", { bubbles: true, composed: true }));
      target.click?.();
      return true;
    }
    """
    for scope in iter_bilibili_editor_scopes(page):
        try:
            if scope.evaluate(script, BILIBILI_IMAGE_TOOLBAR_SELECTOR):
                LOGGER.debug("Clicked Bilibili image toolbar in frame %s.", bilibili_scope_label(scope))
                return True
        except Exception as exc:
            LOGGER.debug(
                "Could not click Bilibili image toolbar via shadow DOM in %s: %s",
                bilibili_scope_label(scope),
                exc,
            )
    return False


def upload_images_via_shadow_toolbar(page: Any, image_paths: Sequence[Path]) -> bool:
    paths = [str(path) for path in image_paths if path.is_file()]
    if not paths or not bilibili_image_toolbar_exists(page):
        return False
    try:
        with page.expect_file_chooser(timeout=5000) as chooser_info:
            if not click_bilibili_image_toolbar(page):
                raise BilibiliAssistantError("Bilibili image toolbar click returned false")
        chooser_info.value.set_files(paths)
        LOGGER.info("Selected %d Bilibili image(s) via shadow toolbar.", len(paths))
        return True
    except Exception as exc:
        LOGGER.debug("Bilibili shadow toolbar did not open file chooser directly: %s", exc)
    try:
        if click_bilibili_image_toolbar(page):
            page.wait_for_timeout(600)
    except Exception:
        pass
    return upload_images_via_file_input(page, [Path(path) for path in paths])


def upload_images_via_file_chooser(page: Any, image_paths: Sequence[Path]) -> bool:
    paths = [str(path) for path in image_paths if path.is_file()]
    if not paths:
        return False
    triggers = [
        "eva3-toolbar-image eva3-dropdown eva3-icon svg",
        "eva3-toolbar-image",
        "button:has-text('上传图片')",
        "button:has-text('添加图片')",
        "button:has-text('图片')",
        "[role=button]:has-text('上传图片')",
        "[role=button]:has-text('添加图片')",
        "[role=button]:has-text('图片')",
        "[aria-label*='图片']",
        "[title*='图片']",
        "text=上传图片",
        "text=添加图片",
        "text=图片",
    ]
    found = first_visible_locator_in_scopes(page, triggers, timeout_ms=1800)
    if found is None:
        return False
    _, trigger, _ = found
    try:
        with page.expect_file_chooser(timeout=5000) as chooser_info:
            trigger.click()
        chooser_info.value.set_files(paths)
        LOGGER.info("Selected %d Bilibili image(s) via file chooser.", len(paths))
        return True
    except Exception as exc:
        LOGGER.debug("Bilibili file chooser upload failed: %s", exc)
        return False


def upload_bilibili_images(page: Any, image_paths: Sequence[Path], config: Config) -> bool:
    limited_paths = [path for path in image_paths if path.is_file()][:BILIBILI_IMAGE_LIMIT]
    if (
        upload_images_via_shadow_toolbar(page, limited_paths)
        or upload_images_via_file_chooser(page, limited_paths)
        or upload_images_via_file_input(page, limited_paths)
    ):
        wait_for_bilibili_upload_settled(page, timeout_sec=config.upload_wait_sec)
        return True
    LOGGER.warning("Could not upload images automatically. Please upload them manually.")
    return False


def wait_for_bilibili_upload_settled(page: Any, *, timeout_sec: int) -> bool:
    bad_words = ("上传失败", "解析失败", "校验失败", "处理失败", "失败")
    busy_words = ("上传中", "正在上传", "处理中", "正在处理", "加载中")
    deadline = time.monotonic() + timeout_sec
    stable_since: float | None = None
    while time.monotonic() < deadline:
        text = visible_body_text(page)
        if any(word in text for word in bad_words):
            LOGGER.warning("Bilibili upload page may contain an error: %s", compact_log_text(text))
            return False
        busy = any(word in text for word in busy_words) or bool(re.search(r"\b\d{1,3}\s*%", text))
        if not busy:
            if stable_since is None:
                stable_since = time.monotonic()
            elif time.monotonic() - stable_since >= 2:
                LOGGER.info("Bilibili upload appears settled.")
                return True
        else:
            stable_since = None
        page.wait_for_timeout(800)
    LOGGER.warning("Timed out waiting for Bilibili upload to settle.")
    return False


def fill_locator_with_keyboard(page: Any, locator: Any, text: str) -> bool:
    try:
        locator.click(timeout=2500)
        page.wait_for_timeout(150)
        page.keyboard.press("Control+A")
        page.keyboard.insert_text(text)
        page.wait_for_timeout(300)
        return True
    except Exception as exc:
        LOGGER.debug("Keyboard fill failed: %s", exc)
        return False


def fill_text_field_by_dom_hint(page: Any, text: str, *, label: str) -> bool:
    script = """
    ({ text, label }) => {
      const hints = label === "title"
        ? ["标题", "请输入标题", "添加标题"]
        : ["正文", "内容", "编辑器", "请输入正文", "请输入内容"];
      const normalize = (value) => String(value || "").replace(/\\s+/g, " ").trim();
      const isEditable = (el) => {
        const tag = String(el.tagName || "").toLowerCase();
        const type = String(el.getAttribute("type") || "").toLowerCase();
        if (el.disabled || el.getAttribute("aria-disabled") === "true") return false;
        if (el.isContentEditable || el.getAttribute("role") === "textbox") return true;
        if (tag === "textarea") return true;
        if (tag === "input") {
          return !["button", "checkbox", "file", "hidden", "radio", "reset", "submit"].includes(type);
        }
        return false;
      };
      const isVisible = (el) => {
        const rect = el.getBoundingClientRect();
        const style = window.getComputedStyle(el);
        return rect.width > 0 && rect.height > 0
          && style.display !== "none" && style.visibility !== "hidden";
      };
      const score = (el) => {
        const attrs = [
          el.getAttribute("placeholder"),
          el.getAttribute("aria-label"),
          el.getAttribute("data-placeholder"),
          el.getAttribute("title"),
          el.textContent,
          el.parentElement?.textContent,
        ].map(normalize).join(" ");
        let value = 0;
        for (const hint of hints) {
          if (attrs.includes(hint)) value += 10;
        }
        const rect = el.getBoundingClientRect();
        if (label === "title" && rect.height <= 80) value += 2;
        if (label !== "title" && rect.height >= 40) value += 2;
        return value;
      };
      const candidates = Array.from(document.querySelectorAll("textarea,input,[contenteditable='true'],[role='textbox']"))
        .filter((el) => isEditable(el) && isVisible(el))
        .map((el) => ({ el, value: score(el) }))
        .filter((item) => item.value > 0)
        .sort((a, b) => b.value - a.value);
      if (!candidates.length) return { ok: false, reason: "no-candidate" };
      const el = candidates[0].el;
      el.scrollIntoView?.({ block: "center", inline: "nearest" });
      el.focus?.();
      if (el.isContentEditable || el.getAttribute("role") === "textbox") {
        document.execCommand("selectAll", false);
        document.execCommand("insertText", false, text);
      } else {
        el.value = text;
        el.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: text }));
        el.dispatchEvent(new Event("change", { bubbles: true }));
      }
      return { ok: true };
    }
    """
    args = {"text": text, "label": label}
    for scope in iter_bilibili_editor_scopes(page):
        try:
            result = scope.evaluate(script, args)
        except Exception as exc:
            LOGGER.debug("DOM hint fill failed for %s in %s: %s", label, bilibili_scope_label(scope), exc)
            continue
        if isinstance(result, dict) and result.get("ok"):
            LOGGER.info("Filled Bilibili %s via DOM hint in frame %s.", label, bilibili_scope_label(scope))
            return True
        LOGGER.debug("DOM hint fill did not find Bilibili %s in %s: %s", label, bilibili_scope_label(scope), result)
    return False


def fill_bilibili_title_by_dom_selector(page: Any, title: str) -> bool:
    script = """
    ({ selectors, text }) => {
      for (const selector of selectors) {
        let el = null;
        try {
          el = document.querySelector(selector);
        } catch (_) {}
        if (!el) continue;
        el.scrollIntoView?.({ block: "center", inline: "nearest" });
        el.focus?.();
        const tag = String(el.tagName || "").toLowerCase();
        if (tag === "textarea" || tag === "input") {
          const proto = tag === "textarea" ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
          const setter = Object.getOwnPropertyDescriptor(proto, "value")?.set;
          if (setter) setter.call(el, text);
          else el.value = text;
          el.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: text }));
          el.dispatchEvent(new Event("change", { bubbles: true }));
          return { ok: true, selector };
        }
        if (el.isContentEditable || el.getAttribute("role") === "textbox") {
          document.execCommand("selectAll", false);
          document.execCommand("insertText", false, text);
          return { ok: true, selector };
        }
      }
      return { ok: false };
    }
    """
    args = {"selectors": list(BILIBILI_TITLE_FIELD_SELECTORS), "text": title}
    for scope in iter_bilibili_editor_scopes(page):
        try:
            result = scope.evaluate(script, args)
        except Exception as exc:
            LOGGER.debug("Bilibili title DOM selector fill failed in %s: %s", bilibili_scope_label(scope), exc)
            continue
        if isinstance(result, dict) and result.get("ok"):
            LOGGER.info(
                "Filled Bilibili title via DOM selector in frame %s: %s",
                bilibili_scope_label(scope),
                result.get("selector"),
            )
            return True
    return False


def fill_text_field(page: Any, selectors: Sequence[str], text: str, label: str) -> bool:
    locator = first_visible_locator(page, selectors, timeout_ms=1400)
    if locator is not None and fill_locator_with_keyboard(page, locator, text):
        LOGGER.info("Filled Bilibili %s.", label)
        return True
    return fill_text_field_by_dom_hint(page, text, label=label)


def fill_bilibili_title(page: Any, title: str) -> bool:
    found = first_visible_locator_in_scopes(page, BILIBILI_TITLE_FIELD_SELECTORS, timeout_ms=15000)
    if found is not None:
        scope, locator, selector = found
        try:
            locator.fill(title, timeout=3000)
            LOGGER.info(
                "Filled Bilibili title in frame %s via selector %s.",
                bilibili_scope_label(scope),
                selector,
            )
            return True
        except Exception:
            if fill_locator_with_keyboard(page, locator, title):
                LOGGER.info(
                    "Filled Bilibili title by keyboard in frame %s via selector %s.",
                    bilibili_scope_label(scope),
                    selector,
                )
                return True
    if fill_bilibili_title_by_dom_selector(page, title):
        return True
    if fill_text_field_by_dom_hint(page, title, label="title"):
        return True
    LOGGER.warning("Could not fill Bilibili title automatically. Please paste it manually: %s", title)
    return False


def focus_bilibili_body_editor_by_dom_selector(page: Any) -> bool:
    script = """
    ({ selectors }) => {
      const isVisible = (el) => {
        const rect = el.getBoundingClientRect();
        const style = window.getComputedStyle(el);
        return rect.width > 0 && rect.height > 0
          && style.display !== "none" && style.visibility !== "hidden";
      };
      for (const selector of selectors) {
        let el = null;
        try {
          el = document.querySelector(selector);
        } catch (_) {}
        if (!el || !isVisible(el)) continue;
        el.scrollIntoView?.({ block: "center", inline: "nearest" });
        el.focus?.();
        el.dispatchEvent(new MouseEvent("mousedown", { bubbles: true, composed: true }));
        el.dispatchEvent(new MouseEvent("mouseup", { bubbles: true, composed: true }));
        el.click?.();
        return { ok: true, selector };
      }
      return { ok: false };
    }
    """
    args = {"selectors": list(BILIBILI_BODY_EDITOR_SELECTORS)}
    for scope in iter_bilibili_editor_scopes(page):
        try:
            result = scope.evaluate(script, args)
        except Exception as exc:
            LOGGER.debug("Bilibili editor DOM selector focus failed in %s: %s", bilibili_scope_label(scope), exc)
            continue
        if isinstance(result, dict) and result.get("ok"):
            LOGGER.info(
                "Focused Bilibili article editor via DOM selector in frame %s: %s",
                bilibili_scope_label(scope),
                result.get("selector"),
            )
            return True
    return False


def focus_bilibili_body_editor(page: Any) -> Any | None:
    found = first_visible_locator_in_scopes(page, BILIBILI_BODY_EDITOR_SELECTORS, timeout_ms=15000)
    if found is None:
        if focus_bilibili_body_editor_by_dom_selector(page):
            return True
        LOGGER.warning("Could not find Bilibili article editor. Use article_blocks.json manually.")
        return None
    scope, editor, selector = found
    try:
        editor.click(timeout=2500)
        page.wait_for_timeout(200)
        LOGGER.info(
            "Focused Bilibili article editor in frame %s via selector %s.",
            bilibili_scope_label(scope),
            selector,
        )
        return editor
    except Exception as exc:
        LOGGER.warning("Could not focus Bilibili article editor: %s", exc)
        return None


def upload_bilibili_image_into_editor(page: Any, image_path: Path, config: Config) -> bool:
    if not image_path.is_file():
        return False
    if upload_images_via_shadow_toolbar(page, [image_path]) or upload_images_via_file_chooser(page, [image_path]):
        wait_for_bilibili_upload_settled(page, timeout_sec=config.upload_wait_sec)
        try:
            page.keyboard.press("Enter")
            page.wait_for_timeout(200)
        except Exception:
            pass
        return True
    return False


def leave_manual_image_placeholder(page: Any, block: dict[str, Any], image_path: Path) -> None:
    label = str(block.get("alt") or block.get("latex") or image_path.name).strip()
    placeholder = f"[图片需手动上传：{label} | {image_path.name}]" if label else f"[图片需手动上传：{image_path.name}]"
    try:
        page.keyboard.insert_text(placeholder)
        page.keyboard.press("Enter")
        page.keyboard.press("Enter")
    except Exception as exc:
        LOGGER.warning("Could not insert manual image placeholder for %s: %s", image_path, exc)


def fill_bilibili_body_blocks(page: Any, blocks: list[dict[str, Any]], config: Config) -> bool:
    editor = focus_bilibili_body_editor(page)
    if editor is None:
        return False
    try:
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
    except Exception:
        pass

    manual_image_paths: list[Path] = []
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
                page.keyboard.insert_text(str(block.get("latex") or block.get("alt") or "[图片缺失]"))
                page.keyboard.press("Enter")
                page.keyboard.press("Enter")
                continue
            if not upload_bilibili_image_into_editor(page, path, config):
                manual_image_paths.append(path)
                LOGGER.warning("Bilibili image upload failed; leaving placeholder: %s", path)
                focus_bilibili_body_editor(page)
                leave_manual_image_placeholder(page, block, path)
        elif block_type == "divider":
            page.keyboard.insert_text("---")
            page.keyboard.press("Enter")
            page.keyboard.press("Enter")

    if manual_image_paths:
        LOGGER.warning(
            "Bilibili body fill finished with %d image(s) left for manual upload: %s",
            len(manual_image_paths),
            ", ".join(path.name for path in manual_image_paths),
        )
    LOGGER.info("Bilibili article body fill attempted. Please verify in Chrome.")
    return True


def fill_bilibili_draft(result: PackageResult, config: Config) -> None:
    if not config.chrome_path.is_file():
        raise BilibiliAssistantError(f"Chrome executable not found: {config.chrome_path}")
    payload = read_json(Path(result.post_payload_path))
    if not isinstance(payload, dict):
        raise BilibiliAssistantError(f"Invalid Bilibili post payload: {result.post_payload_path}")
    title = truncate_text(str(payload.get("title") or result.title), BILIBILI_TITLE_LIMIT)
    blocks = payload.get("blocks")
    if not isinstance(blocks, list):
        article_payload = read_json(Path(result.article_blocks_path))
        blocks = article_payload.get("blocks") if isinstance(article_payload, dict) else []
    if not isinstance(blocks, list):
        raise BilibiliAssistantError(f"Bilibili post payload missing blocks: {result.post_payload_path}")

    sync_playwright = import_playwright()
    LOGGER.info("Opening Bilibili in local Chrome | %s", config.chrome_path)
    config.profile_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(config.profile_dir),
            executable_path=str(config.chrome_path),
            headless=False,
            args=["--start-maximized"],
            no_viewport=True,
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(config.bilibili_url, wait_until="domcontentloaded")
        LOGGER.info("Waiting for Bilibili article editor. Scan/login if prompted.")
        if not wait_for_bilibili_ready(page, timeout_sec=config.editor_wait_sec):
            LOGGER.warning(
                "Bilibili publisher was not detected within %d seconds. "
                "If a login page is showing, complete login and rerun.",
                config.editor_wait_sec,
            )
            return

        if not open_bilibili_article_editor(page):
            LOGGER.warning("Bilibili article editor was not opened. Please open the editor manually and rerun.")
            return
        fill_bilibili_title(page, title)
        fill_bilibili_body_blocks(page, blocks, config)

        LOGGER.info(
            "Bilibili draft fill attempted. Please review and click publish manually. "
            "Keeping Chrome open for %d seconds.",
            config.review_wait_sec,
        )
        if config.review_wait_sec:
            time.sleep(config.review_wait_sec)
        context.close()


def orchestrate(config: Config) -> dict[str, Any]:
    canonical = read_json(config.canonical_path)
    if not isinstance(canonical, dict):
        raise BilibiliAssistantError(f"Canonical JSON must be an object: {config.canonical_path}")

    report: dict[str, Any] = {
        "generated_at": now_iso(),
        "ids": list(config.ids),
        "canonical": str(config.canonical_path),
        "output_dir": str(config.output_dir),
        "package_only": config.package_only,
        "bilibili_url": config.bilibili_url,
        "items": [],
    }

    for item_id in config.ids:
        record = canonical[item_id]
        try:
            result = package_one_item(item_id, record, config)
            report["items"].append(asdict(result))
            write_json(config.report_path, report)
            if not config.package_only:
                fill_bilibili_draft(result, config)
        except Exception as exc:
            LOGGER.exception("Failed processing %s", item_id)
            failed = PackageResult(
                id=item_id,
                title=item_id,
                output_dir=str(config.output_dir / item_id),
                cover_path="",
                article_blocks_path="",
                manifest_path="",
                preview_html_path="",
                body_markdown_path="",
                body_html_path="",
                checklist_path="",
                post_payload_path="",
                formula_asset_count=0,
                missing_asset_count=0,
                upload_asset_count=0,
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
            raise BilibiliAssistantError(f"Canonical JSON must be an object: {canonical_path}")
        config = build_config(args, canonical)
        configure_logging(config.log_level)
        LOGGER.info("Bilibili target IDs | %s", ", ".join(config.ids))
        report = orchestrate(config)
        success_count = sum(1 for item in report["items"] if item.get("status") == "success")
        LOGGER.info(
            "Bilibili assistant complete | success=%d/%d | report=%s",
            success_count,
            len(config.ids),
            config.report_path,
        )
        return 0
    except BilibiliAssistantError as exc:
        LOGGER.error("%s", exc)
        return 1
    except KeyboardInterrupt:
        LOGGER.error("Interrupted by user.")
        return 130
    except Exception:
        LOGGER.exception("Unexpected Bilibili assistant failure")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
