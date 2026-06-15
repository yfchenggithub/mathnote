#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate a Xiaohongshu image-note package for selected conclusion IDs and
optionally open Xiaohongshu Creator Center for semi-automatic draft filling.

The script keeps final publishing manual: it renders reusable image cards,
uploads/fills what it can through a local Chrome session, selects the configured
collection when possible, and leaves the user to review the note before clicking
publish.

Examples:
    python scripts/xhs_publish_assistant.py G003 --package-only
    python scripts/xhs_publish_assistant.py G003
    python scripts/xhs_publish_assistant.py G003 --card-size 900x1200
    python scripts/xhs_publish_assistant.py G003 --collection ""
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

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

DEFAULT_CANONICAL_PATH = PROJECT_ROOT / "data" / "content" / "canonical_content_v2.json"
DEFAULT_PUBLIC_DIR = PROJECT_ROOT / "public"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "build" / "xhs_posts"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports" / "xhs_publish_assistant_report.json"
DEFAULT_MINICODE_PATH = PROJECT_ROOT / "assets" / "figures" / "MiniCode.png"
DEFAULT_CHROME_PATH = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
DEFAULT_PROFILE_DIR = PROJECT_ROOT / "build" / "xhs_chrome_profile"
DEFAULT_XHS_URL = (
    "https://creator.xiaohongshu.com/publish/publish"
    "?source=official&from=tab_switch&target=image"
)
DEFAULT_CARD_SIZE = "1080x1440"
DEFAULT_CARD_DPR = 1.0
DEFAULT_COLLECTION_TITLE = "高中数学 常用二级结论"
XHS_TITLE_LIMIT = 20
XHS_HASHTAG_LIMIT = 10
LOGGER = logging.getLogger("xhs_publish_assistant")

XHS_UPLOAD_BUTTON_SELECTOR = (
    "#web > div > div > div > div.upload-content > div.upload-wrapper > div > div > div "
    "> button.d-button.d-button-default.d-button-with-content.--color-static.bold."
    "--color-bg-fill.--color-text-paragraph.custom-button.bg-red.upload-button > div"
)
XHS_TITLE_INPUT_SELECTOR = (
    "#web > div > div > div.publish-page-container > div > div > div.publish-page-content "
    "> div.publish-page-content-base > div > div.flex > div.input "
    "> div.d-input-wrapper.d-inline-block.c-input_inner > div > input"
)
XHS_CAPTION_EDITOR_SELECTOR = (
    "#web > div > div > div.publish-page-container > div > div > div.publish-page-content "
    "> div.publish-page-content-base > div > div.editor-container > div.editor-content > div > div"
)
XHS_COLLECTION_BUTTON_SELECTOR = (
    "#web > div > div > div.publish-page-container > div > div > div.publish-page-content "
    "> div.publish-page-content-content-extra > div.publish-page-content-setting-content "
    "> div.collection-plugin-wrapper > div.collection-plugin-button"
)
XHS_FIRST_COLLECTION_SELECTOR = (
    "body > div.d-popover.d-popover-default.collection-plugin-popover > div "
    "> div:nth-child(1) > div > div"
)


class XhsAssistantError(RuntimeError):
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
    xhs_url: str
    card_size: tuple[int, int]
    card_dpr: float
    collection_title: str
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
    cards_dir: str
    cover_path: str
    card_paths: list[str]
    caption_path: str
    manifest_path: str
    preview_html_path: str
    checklist_path: str
    post_payload_path: str
    card_count: int
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
        raise argparse.ArgumentTypeError("image note card ratio should not exceed 1:2 or 2:1")
    return width, height


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and optionally fill a Xiaohongshu image-note draft.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/xhs_publish_assistant.py G003 --package-only\n"
            "  python scripts/xhs_publish_assistant.py G003\n"
            "  python scripts/xhs_publish_assistant.py G003 --card-size 900x1200\n"
            '  python scripts/xhs_publish_assistant.py G003 --collection ""\n'
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
    parser.add_argument("--xhs-url", default=DEFAULT_XHS_URL)
    parser.add_argument(
        "--card-size",
        type=parse_size,
        default=parse_size(DEFAULT_CARD_SIZE),
        help="Rendered image size. Default: 1080x1440. Use 900x1200 for the old XHS workflow.",
    )
    parser.add_argument("--card-dpr", type=float, default=DEFAULT_CARD_DPR)
    parser.add_argument(
        "--collection",
        default=DEFAULT_COLLECTION_TITLE,
        help='Collection to select after filling. Use "" to skip. Default: 高中数学 常用二级结论.',
    )
    parser.add_argument(
        "--package-only",
        action="store_true",
        help="Only generate files. Do not open Chrome or fill Xiaohongshu Creator Center.",
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
        help="Seconds to wait for Xiaohongshu Creator Center after login. 0 means wait forever. Default: 0.",
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
        raise XhsAssistantError(str(exc)) from exc


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
        raise XhsAssistantError(str(exc)) from exc
    missing = [item_id for item_id in ids if item_id not in canonical]
    if missing:
        raise XhsAssistantError(
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
        xhs_url=str(args.xhs_url),
        card_size=args.card_size,
        card_dpr=max(1.0, float(args.card_dpr)),
        collection_title=clean_text(args.collection),
        package_only=bool(args.package_only),
        force=bool(args.force),
        editor_wait_sec=max(0, int(args.editor_wait_sec)),
        upload_wait_sec=max(5, int(args.upload_wait_sec)),
        review_wait_sec=max(0, int(args.review_wait_sec)),
        log_level=str(args.log_level).upper(),
    )


def xhs_title(record: dict[str, Any], item_id: str) -> str:
    base = clean_text(channels.record_title(record, item_id))
    compact = re.sub(r"\s+", "", base)
    short = re.split(r"[：:，,（(]", compact, maxsplit=1)[0].strip()
    candidates = [
        f"{item_id} {short}",
        f"{item_id} {compact}",
        *[f"{item_id} {clean_text(alias)}" for alias in channels.record_aliases(record)],
    ]
    for candidate in candidates:
        value = clean_text(candidate)
        if value and len(value) <= XHS_TITLE_LIMIT:
            return value
    return truncate_text(candidates[0] if candidates else item_id, XHS_TITLE_LIMIT)


def xhs_topics(record: dict[str, Any]) -> list[str]:
    candidates = [
        "高考数学",
        "高中数学",
        "二级结论",
        "解题技巧",
        "数学老师",
        "学生复习",
        "数学笔记",
        "高中数学解题",
        channels.record_category(record),
        *channels.record_tags(record),
        *channels.record_aliases(record),
    ]
    topics: list[str] = []
    for value in candidates:
        topic = re.sub(r"^[#＃]+", "", clean_text(value))
        topic = re.sub(r"\s+", "", topic)
        if not topic or len(topic) > 18:
            continue
        topics.append(topic)
    return dedupe_keep_order(topics)[:XHS_HASHTAG_LIMIT]


def build_caption(record: dict[str, Any], *, item_id: str) -> str:
    summary = channels.record_summary(record)
    title = channels.record_title(record, item_id)
    topics = xhs_topics(record)
    topic_text = " ".join(f"#{topic}" for topic in topics)
    lines = [
        summary or f"{title}，这条高中数学二级结论适合做题前快速复盘。",
        "",
        "看图顺序：封面 -> 导读 -> 核心结论 -> 理解直觉 -> 证明过程 -> 例题应用 -> 易错提醒 -> 复盘总结。",
        f"注意先确认适用条件，再套公式。最后一张图可以进入小程序搜索 {item_id} 查看完整推导和高清 PDF。",
        "",
        topic_text,
    ]
    return "\n".join(line for line in lines if line is not None).strip() + "\n"


def render_preview_html(title: str, image_paths: Sequence[Path], caption: str) -> str:
    images = "\n".join(
        f'<figure><img src="{path.resolve().as_uri()}" alt="{html.escape(path.name, quote=True)}"/>'
        f"<figcaption>{html.escape(path.name, quote=False)}</figcaption></figure>"
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
      background: #f6f7f5;
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
      border: 1px solid #dfe5dc;
      line-height: 1.75;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 18px;
      margin-top: 24px;
    }}
    figure {{ margin: 0; background: #ffffff; padding: 10px; border: 1px solid #dfe5dc; }}
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
    return f"""# 小红书图文发布检查清单：{item_id}

1. 打开 `preview.html` 检查 {result.card_count} 张图的顺序、文字截断、公式图片和小程序码。
2. 确认第一张图适合做小红书封面，标题不超过 {XHS_TITLE_LIMIT} 个字，话题不超过 {XHS_HASHTAG_LIMIT} 个。
3. 运行不带 `--package-only` 的脚本，让 Chrome 打开小红书创作服务平台。
4. 登录后检查图片顺序、标题、正文描述、合集和最后一张小程序引流卡。
5. 确认无误后人工点击发布；脚本默认不会点击最终发布按钮。

小红书标题：`{result.title}`

生成图片：
{image_lines}

文案：`{result.caption_path}`
预览：`{result.preview_html_path}`
"""


def package_one_item(item_id: str, record: dict[str, Any], config: Config) -> PackageResult:
    output_dir = config.output_dir / item_id
    output_dir.mkdir(parents=True, exist_ok=True)
    title = xhs_title(record, item_id)
    topics = xhs_topics(record)
    LOGGER.info("Generating Xiaohongshu package | %s", item_id)

    card_specs = channels.build_card_specs(record, item_id=item_id, config=config)
    card_paths, html_paths = channels.render_cards(card_specs, output_dir=output_dir, config=config)
    cover_path = card_paths[0] if card_paths else output_dir / "cards" / "01_cover.png"
    caption = build_caption(record, item_id=item_id)

    caption_path = output_dir / "caption.txt"
    manifest_path = output_dir / "manifest.json"
    preview_html_path = output_dir / "preview.html"
    checklist_path = output_dir / "xhs_publish_checklist.md"
    post_payload_path = output_dir / "xhs_post.json"

    write_text(caption_path, caption)
    write_text(preview_html_path, render_preview_html(title, card_paths, caption))

    payload = {
        "id": item_id,
        "title": title,
        "generated_at": now_iso(),
        "xhs_url": config.xhs_url,
        "collection_title": config.collection_title,
        "caption_path": str(caption_path),
        "caption": caption,
        "card_size": {"width": config.card_size[0], "height": config.card_size[1]},
        "cover_path": str(cover_path),
        "card_paths": [str(path) for path in card_paths],
        "card_html_paths": [str(path) for path in html_paths],
        "topics": topics,
        "minicode_path": str(config.minicode_path),
    }
    write_json(post_payload_path, payload)

    manifest = {
        "id": item_id,
        "title": title,
        "generated_at": now_iso(),
        "output_dir": str(output_dir),
        "card_count": len(card_paths),
        "collection_title": config.collection_title,
        "cover_path": str(cover_path),
        "card_paths": [str(path) for path in card_paths],
        "card_html_paths": [str(path) for path in html_paths],
        "caption_path": str(caption_path),
        "preview_html_path": str(preview_html_path),
        "post_payload_path": str(post_payload_path),
        "topics": topics,
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
        topics=topics,
    )
    write_text(checklist_path, render_checklist(item_id, result))
    return result


def import_playwright() -> Any:
    try:
        return channels.import_playwright()
    except Exception as exc:
        raise XhsAssistantError(
            "Playwright is required for draft filling. Install the Python package first."
        ) from exc


def first_visible_locator(page: Any, selectors: Sequence[str], *, timeout_ms: int = 1200) -> Any | None:
    return channels.first_visible_locator(page, selectors, timeout_ms=timeout_ms)


def visible_body_text(page: Any) -> str:
    try:
        return str(page.locator("body").inner_text(timeout=700) or "")
    except Exception:
        return ""


def compact_log_text(text: str, limit: int = 240) -> str:
    compact = " ".join(str(text or "").split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1] + "…"


def wait_for_xhs_ready(page: Any, *, timeout_sec: int) -> bool:
    deadline = None if timeout_sec <= 0 else time.monotonic() + timeout_sec
    selectors = [
        "button.upload-button",
        "button:has-text('上传图片')",
        "text=上传图片",
        "text=发布图文",
        "text=填写标题",
        XHS_UPLOAD_BUTTON_SELECTOR,
        XHS_TITLE_INPUT_SELECTOR,
    ]
    last_notice = 0.0
    while True:
        if first_visible_locator(page, selectors, timeout_ms=1000) is not None:
            return True
        if deadline is not None and time.monotonic() >= deadline:
            return False
        now = time.monotonic()
        if now - last_notice >= 20:
            LOGGER.warning("Still waiting for Xiaohongshu Creator Center. Please scan/login if prompted.")
            last_notice = now
        page.wait_for_timeout(1000)


def upload_images_via_file_input(page: Any, image_paths: Sequence[Path]) -> bool:
    paths = [str(path) for path in image_paths if path.is_file()]
    if not paths:
        LOGGER.warning("No uploadable image files found.")
        return False
    try:
        inputs = page.locator('input[type="file"]')
        count = inputs.count()
    except Exception:
        return False
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
            LOGGER.info("Selected %d Xiaohongshu image(s) via file input.", len(paths))
            return True
        except Exception as exc:
            LOGGER.debug("Xiaohongshu file input upload failed at index %d: %s", index, exc)
    return False


def upload_images_via_file_chooser(page: Any, image_paths: Sequence[Path]) -> bool:
    paths = [str(path) for path in image_paths if path.is_file()]
    if not paths:
        return False
    triggers = [
        "button.upload-button",
        "button:has-text('上传图片')",
        "[role=button]:has-text('上传图片')",
        "text=上传图片",
        "text=选择图片",
        "text=点击上传",
        XHS_UPLOAD_BUTTON_SELECTOR,
    ]
    trigger = first_visible_locator(page, triggers, timeout_ms=1800)
    if trigger is None:
        return False
    try:
        with page.expect_file_chooser(timeout=5000) as chooser_info:
            trigger.click()
        chooser_info.value.set_files(paths)
        LOGGER.info("Selected %d Xiaohongshu image(s) via file chooser.", len(paths))
        return True
    except Exception as exc:
        LOGGER.debug("Xiaohongshu file chooser upload failed: %s", exc)
        return False


def upload_xhs_images(page: Any, image_paths: Sequence[Path], config: Config) -> bool:
    if upload_images_via_file_chooser(page, image_paths) or upload_images_via_file_input(page, image_paths):
        wait_for_xhs_publish_form(page, timeout_sec=config.upload_wait_sec)
        return True
    LOGGER.warning("Could not upload images automatically. Please upload them manually.")
    return False


def wait_for_xhs_publish_form(page: Any, *, timeout_sec: int) -> bool:
    deadline = time.monotonic() + timeout_sec
    selectors = [
        XHS_TITLE_INPUT_SELECTOR,
        XHS_CAPTION_EDITOR_SELECTOR,
        "input[placeholder*='标题']",
        "text=填写标题",
        "text=正文描述",
        "text=选择合集",
    ]
    bad_words = ("上传失败", "解析失败", "校验失败", "处理失败", "失败")
    while time.monotonic() < deadline:
        text = visible_body_text(page)
        if any(word in text for word in bad_words):
            LOGGER.warning("Xiaohongshu upload page may contain an error: %s", compact_log_text(text))
            return False
        if first_visible_locator(page, selectors, timeout_ms=800) is not None:
            LOGGER.info("Xiaohongshu publish form appears ready.")
            page.wait_for_timeout(1200)
            return True
        page.wait_for_timeout(800)
    LOGGER.warning("Timed out waiting for Xiaohongshu publish form.")
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


def fill_exact_selector_with_text(
    page: Any,
    selector: str,
    text: str,
    *,
    label: str,
    prefer_fill: bool = True,
    timeout_ms: int = 2500,
) -> bool:
    locator = first_visible_locator(page, [selector], timeout_ms=timeout_ms)
    if locator is None:
        return False
    try:
        locator.click(timeout=2500)
        page.wait_for_timeout(150)
        if prefer_fill:
            try:
                locator.fill(text, timeout=1500)
            except Exception:
                page.keyboard.press("Control+A")
                page.keyboard.insert_text(text)
        else:
            page.keyboard.press("Control+A")
            page.keyboard.insert_text(text)
        page.wait_for_timeout(400)
        LOGGER.info("Filled Xiaohongshu %s via exact selector.", label)
        return True
    except Exception as exc:
        LOGGER.debug("Could not fill Xiaohongshu %s via exact selector: %s", label, exc)
        return False


def fill_text_field_by_dom_hint(page: Any, text: str, *, label: str) -> bool:
    try:
        result = page.evaluate(
            """
            ({ text, label }) => {
              const hints = label === "title"
                ? ["填写标题", "标题", "请输入标题"]
                : ["正文描述", "正文", "描述", "说点什么", "请输入正文", "请输入描述"];
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
                if (label !== "title" && rect.height >= 60) value += 2;
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
            """,
            {"text": text, "label": label},
        )
    except Exception as exc:
        LOGGER.debug("DOM hint fill failed for %s: %s", label, exc)
        return False
    if isinstance(result, dict) and result.get("ok"):
        LOGGER.info("Filled Xiaohongshu %s via DOM hint.", label)
        return True
    LOGGER.debug("DOM hint fill did not find Xiaohongshu %s: %s", label, result)
    return False


def fill_text_field(page: Any, selectors: Sequence[str], text: str, label: str) -> bool:
    locator = first_visible_locator(page, selectors, timeout_ms=1400)
    if locator is not None and fill_locator_with_keyboard(page, locator, text):
        LOGGER.info("Filled Xiaohongshu %s.", label)
        return True
    return fill_text_field_by_dom_hint(page, text, label=label)


def fill_xhs_title(page: Any, title: str) -> bool:
    selectors = [
        XHS_TITLE_INPUT_SELECTOR,
        "input[placeholder*='标题']",
        "textarea[placeholder*='标题']",
        "[contenteditable='true'][data-placeholder*='标题']",
        "[role='textbox'][aria-label*='标题']",
    ]
    if fill_text_field(page, selectors, title, "title"):
        return True
    LOGGER.warning("Could not fill Xiaohongshu title automatically. Please paste it manually: %s", title)
    return False


def fill_xhs_caption(page: Any, caption: str) -> bool:
    selectors = [
        XHS_CAPTION_EDITOR_SELECTOR,
        "textarea[placeholder*='正文']",
        "textarea[placeholder*='描述']",
        "textarea[placeholder*='说点什么']",
        "[contenteditable='true'][data-placeholder*='正文']",
        "[contenteditable='true'][data-placeholder*='描述']",
        "[role='textbox'][aria-label*='正文']",
        "[role='textbox'][aria-label*='描述']",
    ]
    if fill_text_field(page, selectors, caption, "caption"):
        return True
    LOGGER.warning("Could not fill Xiaohongshu caption automatically. Use caption.txt as fallback.")
    return False


def click_exact_selector(page: Any, selector: str, *, label: str, timeout_ms: int = 2500) -> bool:
    locator = first_visible_locator(page, [selector], timeout_ms=timeout_ms)
    if locator is None:
        return False
    try:
        locator.click(timeout=2500)
        page.wait_for_timeout(500)
        LOGGER.info("Clicked Xiaohongshu %s via exact selector.", label)
        return True
    except Exception as exc:
        LOGGER.debug("Could not click Xiaohongshu %s via exact selector: %s", label, exc)
        return False


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
              const preferred = Array.from(document.querySelectorAll(
                "button, [role='button'], [role='option'], [class*='button'], [class*='option'], li, div"
              ));
              const candidates = preferred
                .filter((el, index, arr) => arr.indexOf(el) === index)
                .filter((el) => {
                  if (!isVisible(el)) return false;
                  const text = normalize(el.textContent);
                  const rect = el.getBoundingClientRect();
                  return text
                    && text.length <= maxTextLen
                    && texts.some((target) => text.includes(target))
                    && rect.width >= 20
                    && rect.height >= 16
                    && rect.height <= 220;
                })
                .sort((a, b) => {
                  const aPreferred = a.matches("button, [role='button'], [role='option'], [class*='button'], [class*='option']") ? 0 : 1;
                  const bPreferred = b.matches("button, [role='button'], [role='option'], [class*='button'], [class*='option']") ? 0 : 1;
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
        LOGGER.debug("Could not click Xiaohongshu element by text: %s", exc)
        return False
    return bool(result)


def select_xhs_collection(page: Any, collection_title: str) -> bool:
    collection_title = clean_text(collection_title)
    if not collection_title:
        LOGGER.info("Skipping Xiaohongshu collection selection.")
        return True
    opened = (
        click_exact_selector(
            page,
            XHS_COLLECTION_BUTTON_SELECTOR,
            label="collection button",
            timeout_ms=2500,
        )
        or click_by_dom_text(page, ["选择合集", "添加合集", "合集"], max_text_len=80)
    )
    if not opened:
        LOGGER.warning("Could not open Xiaohongshu collection selector. Please select manually: %s", collection_title)
        return False
    page.wait_for_timeout(800)
    if click_exact_selector(
        page,
        XHS_FIRST_COLLECTION_SELECTOR,
        label="first collection option",
        timeout_ms=2500,
    ):
        LOGGER.info("Selected first Xiaohongshu collection option: %s", collection_title)
        return True
    if click_by_dom_text(page, [collection_title], max_text_len=140):
        LOGGER.info("Selected Xiaohongshu collection by text: %s", collection_title)
        return True
    LOGGER.warning("Could not select Xiaohongshu collection automatically. Please choose manually: %s", collection_title)
    return False


def fill_xhs_draft(result: PackageResult, config: Config) -> None:
    if not config.chrome_path.is_file():
        raise XhsAssistantError(f"Chrome executable not found: {config.chrome_path}")
    payload = read_json(Path(result.post_payload_path))
    if not isinstance(payload, dict):
        raise XhsAssistantError(f"Invalid Xiaohongshu post payload: {result.post_payload_path}")
    image_paths = [Path(str(path)) for path in payload.get("card_paths", [])]
    title = truncate_text(str(payload.get("title") or result.title), XHS_TITLE_LIMIT)
    caption = str(payload.get("caption") or Path(result.caption_path).read_text(encoding="utf-8"))
    collection_title = clean_text(payload.get("collection_title") or config.collection_title)

    sync_playwright = import_playwright()
    LOGGER.info("Opening Xiaohongshu Creator Center in local Chrome | %s", config.chrome_path)
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
        page.goto(config.xhs_url, wait_until="domcontentloaded")
        LOGGER.info("Waiting for Xiaohongshu Creator Center. Scan/login if prompted.")
        if not wait_for_xhs_ready(page, timeout_sec=config.editor_wait_sec):
            LOGGER.warning(
                "Xiaohongshu Creator Center was not detected within %d seconds. "
                "If a login page is showing, complete login and rerun.",
                config.editor_wait_sec,
            )
            return

        upload_xhs_images(page, image_paths, config)
        wait_for_xhs_publish_form(page, timeout_sec=config.upload_wait_sec)
        fill_xhs_title(page, title)
        fill_xhs_caption(page, caption)
        select_xhs_collection(page, collection_title)

        LOGGER.info(
            "Xiaohongshu draft fill attempted. Please review and click publish manually. "
            "Keeping Chrome open for %d seconds.",
            config.review_wait_sec,
        )
        if config.review_wait_sec:
            time.sleep(config.review_wait_sec)
        context.close()


def orchestrate(config: Config) -> dict[str, Any]:
    canonical = read_json(config.canonical_path)
    if not isinstance(canonical, dict):
        raise XhsAssistantError(f"Canonical JSON must be an object: {config.canonical_path}")

    report: dict[str, Any] = {
        "generated_at": now_iso(),
        "ids": list(config.ids),
        "canonical": str(config.canonical_path),
        "output_dir": str(config.output_dir),
        "package_only": config.package_only,
        "xhs_url": config.xhs_url,
        "collection_title": config.collection_title,
        "items": [],
    }

    for item_id in config.ids:
        record = canonical[item_id]
        try:
            result = package_one_item(item_id, record, config)
            report["items"].append(asdict(result))
            write_json(config.report_path, report)
            if not config.package_only:
                fill_xhs_draft(result, config)
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
            raise XhsAssistantError(f"Canonical JSON must be an object: {canonical_path}")
        config = build_config(args, canonical)
        configure_logging(config.log_level)
        LOGGER.info("Xiaohongshu target IDs | %s", ", ".join(config.ids))
        report = orchestrate(config)
        success_count = sum(1 for item in report["items"] if item.get("status") == "success")
        LOGGER.info(
            "Xiaohongshu assistant complete | success=%d/%d | report=%s",
            success_count,
            len(config.ids),
            config.report_path,
        )
        return 0
    except XhsAssistantError as exc:
        LOGGER.error("%s", exc)
        return 1
    except KeyboardInterrupt:
        LOGGER.error("Interrupted by user.")
        return 130
    except Exception:
        LOGGER.exception("Unexpected Xiaohongshu assistant failure")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
