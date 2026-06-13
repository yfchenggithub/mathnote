#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate a Douyin image-post package for selected conclusion IDs and optionally
open Douyin Creator Center for semi-automatic draft filling.

The script keeps final publishing manual: it renders reusable image cards,
uploads/fills what it can through a local Chrome session, and leaves the user
to review the post before clicking publish.

Examples:
    python scripts/douyin_publish_assistant.py G003 --package-only
    python scripts/douyin_publish_assistant.py G003
    python scripts/douyin_publish_assistant.py G003 --card-size 1080x1440
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
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "build" / "douyin_posts"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports" / "douyin_publish_assistant_report.json"
DEFAULT_MINICODE_PATH = PROJECT_ROOT / "assets" / "figures" / "MiniCode.png"
DEFAULT_CHROME_PATH = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
DEFAULT_PROFILE_DIR = PROJECT_ROOT / "build" / "douyin_chrome_profile"
DEFAULT_DOUYIN_URL = "https://creator.douyin.com/creator-micro/content/upload"
DEFAULT_CARD_SIZE = "1080x1440"
DEFAULT_CARD_DPR = 1.0
DEFAULT_MUSIC_QUERY = "时光静好"
DEFAULT_LOCATION_QUERY = "东南大学(九龙湖校区)"
DOUYIN_MAX_ASPECT_RATIO = 2.0
DOUYIN_RECOMMENDED_RATIOS = "3:4 or 4:3"
DOUYIN_TITLE_LIMIT = 20
DOUYIN_TOPIC_LIMIT = 5
DOUYIN_IMAGE_TAB_SELECTOR = "#root > div > div > div.tab-container-DjaX1b > div.tab-item-BcCLTS.active-i8Pu0m"
DOUYIN_IMAGE_UPLOAD_BUTTON_SELECTOR = (
    "#root > div > div > div.semi-tabs.semi-tabs-top > div > div.semi-tabs-pane-active.semi-tabs-pane "
    "> div > div > div.container-drag-VAfIfu > div > div.container-drag-upload-tL99XD > button"
)
DOUYIN_MUSIC_OPEN_BUTTON_SELECTOR = (
    "#DCPF > div > div.content-left-F3wKrk > div > div:nth-child(2) > div:nth-child(2) "
    "> div:nth-child(1) > div.content-child-V0CB7w.content-limit-width-zybqBW "
    "> div > div > div.container-right-uW7Pj1 > span"
)
DOUYIN_MUSIC_SEARCH_SELECTOR = (
    "body > div:nth-child(19) > div > div.semi-sidesheet-inner.semi-sidesheet-inner-wrap "
    "> div > div.semi-sidesheet-body > div.show-fRSVmd.music-selector-container-Bvb7uP "
    "> div.music-search-jpUg0G > div > input"
)
DOUYIN_MUSIC_CHOICE_SELECTOR = (
    "body > div:nth-child(19) > div > div.semi-sidesheet-inner.semi-sidesheet-inner-wrap "
    "> div > div.semi-sidesheet-body > div.show-fRSVmd.music-selector-container-Bvb7uP "
    "> div.music-collection-container-cTsB7J > div > div:nth-child(2) > div "
    "> div.card-container-left-Sww1pX"
)
DOUYIN_LOCATION_SELECTOR = (
    "#douyin_creator_pc_anchor_jump > div.anchor-container-lYY4ni "
    "> div.anchor-component-_ST7rj > div > div > div.semi-select-selection > div > div"
)
LOGGER = logging.getLogger("douyin_publish_assistant")


class DouyinAssistantError(RuntimeError):
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
    douyin_url: str
    card_size: tuple[int, int]
    card_dpr: float
    music_query: str
    location_query: str
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
    if width < 360 or height < 360:
        raise argparse.ArgumentTypeError("card size is too small")
    aspect = max(width, height) / min(width, height)
    if aspect > DOUYIN_MAX_ASPECT_RATIO:
        raise argparse.ArgumentTypeError(
            "Douyin image posts should not exceed a 1:2 or 2:1 aspect ratio; "
            f"recommended ratios are {DOUYIN_RECOMMENDED_RATIOS}"
        )
    return width, height


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and optionally fill a Douyin image-post draft.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/douyin_publish_assistant.py G003 --package-only\n"
            "  python scripts/douyin_publish_assistant.py G003\n"
            "  python scripts/douyin_publish_assistant.py G003 --card-size 1080x1440  # 3:4\n"
            "  python scripts/douyin_publish_assistant.py G003 --card-size 1440x1080  # 4:3\n"
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
    parser.add_argument("--douyin-url", default=DEFAULT_DOUYIN_URL)
    parser.add_argument(
        "--music",
        default=DEFAULT_MUSIC_QUERY,
        help='Music keyword to search/select. Use "" to skip. Default: 时光静好.',
    )
    parser.add_argument(
        "--location",
        default=DEFAULT_LOCATION_QUERY,
        help='Location/anchor keyword to search/select. Use "" to skip. Default: 东南大学(九龙湖校区).',
    )
    parser.add_argument(
        "--card-size",
        type=parse_size,
        default=parse_size(DEFAULT_CARD_SIZE),
        help=(
            "Rendered image size. Default: 1080x1440 (3:4). "
            "Douyin recommends 3:4 or 4:3 and does not recommend ratios beyond 1:2/2:1."
        ),
    )
    parser.add_argument("--card-dpr", type=float, default=DEFAULT_CARD_DPR)
    parser.add_argument(
        "--package-only",
        action="store_true",
        help="Only generate files. Do not open Chrome or fill Douyin Creator Center.",
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
        help="Seconds to wait for Douyin Creator Center after login. 0 means wait forever. Default: 0.",
    )
    parser.add_argument(
        "--upload-wait-sec",
        type=int,
        default=60,
        help="Seconds to wait for image upload/processing to settle. Default: 60.",
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
    return channels.read_json(path, default=default)


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
        raise DouyinAssistantError(str(exc)) from exc
    missing = [item_id for item_id in ids if item_id not in canonical]
    if missing:
        raise DouyinAssistantError(
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
        douyin_url=str(args.douyin_url),
        card_size=args.card_size,
        card_dpr=max(1.0, float(args.card_dpr)),
        music_query=clean_text(args.music),
        location_query=clean_text(args.location),
        package_only=bool(args.package_only),
        force=bool(args.force),
        editor_wait_sec=max(0, int(args.editor_wait_sec)),
        upload_wait_sec=max(5, int(args.upload_wait_sec)),
        review_wait_sec=max(0, int(args.review_wait_sec)),
        log_level=str(args.log_level).upper(),
    )


def douyin_title(record: dict[str, Any], item_id: str) -> str:
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
        if value and len(value) <= DOUYIN_TITLE_LIMIT:
            return value
    return truncate_text(candidates[0] if candidates else item_id, DOUYIN_TITLE_LIMIT)


def douyin_topics(record: dict[str, Any]) -> list[str]:
    candidates = [
        "高中数学",
        "高考数学",
        "数学解题",
        "二级结论",
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
    return dedupe_keep_order(topics)[:DOUYIN_TOPIC_LIMIT]


def build_caption(record: dict[str, Any], *, item_id: str) -> str:
    summary = channels.record_summary(record)
    topics = douyin_topics(record)
    topic_text = " ".join(f"#{topic}" for topic in topics)
    lines = [
        summary or "这是一条高中数学二级结论复盘卡片。",
        "",
        "看图顺序：封面 -> 导读 -> 核心结论 -> 理解直观 -> 证明过程 -> 例题应用 -> 易错提醒 -> 复盘总结。",
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
    return f"""# 抖音图文发布检查清单：{item_id}

1. 打开 `preview.html` 检查 {result.card_count} 张图的顺序、文字截断、公式图片和小程序码。
2. 确认图片比例不超过 1:2 或 2:1；推荐比例为 3:4 或 4:3，默认 `1080x1440` 即 3:4。
3. 确认第一张图适合做抖音图文封面，作品描述标题不超过 20 个字，话题不超过 5 个。
4. 运行不带 `--package-only` 的脚本，让 Chrome 打开抖音创作者中心。
5. 登录后检查图片顺序、标题、正文、话题、音乐、位置锚点和最后一张小程序引流卡。
6. 确认无误后人工点击发布；脚本默认不会点击最终发布按钮。

抖音标题：`{result.title}`

生成图片：
{image_lines}

文案：`{result.caption_path}`
预览：`{result.preview_html_path}`
"""


def package_one_item(item_id: str, record: dict[str, Any], config: Config) -> PackageResult:
    output_dir = config.output_dir / item_id
    output_dir.mkdir(parents=True, exist_ok=True)
    title = douyin_title(record, item_id)
    topics = douyin_topics(record)
    LOGGER.info("Generating Douyin package | %s", item_id)

    card_specs = channels.build_card_specs(record, item_id=item_id, config=config)
    card_paths, html_paths = channels.render_cards(card_specs, output_dir=output_dir, config=config)
    cover_path = card_paths[0] if card_paths else output_dir / "cards" / "01_cover.png"
    caption = build_caption(record, item_id=item_id)

    caption_path = output_dir / "caption.txt"
    manifest_path = output_dir / "manifest.json"
    preview_html_path = output_dir / "preview.html"
    checklist_path = output_dir / "douyin_publish_checklist.md"
    post_payload_path = output_dir / "douyin_post.json"

    write_text(caption_path, caption)
    write_text(preview_html_path, render_preview_html(title, card_paths, caption))

    payload = {
        "id": item_id,
        "title": title,
        "generated_at": now_iso(),
        "douyin_url": config.douyin_url,
        "music_query": config.music_query,
        "location_query": config.location_query,
        "caption_path": str(caption_path),
        "caption": caption,
        "card_size": {"width": config.card_size[0], "height": config.card_size[1]},
        "image_aspect_policy": {
            "max_aspect_ratio": DOUYIN_MAX_ASPECT_RATIO,
            "recommended_ratios": DOUYIN_RECOMMENDED_RATIOS,
        },
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
        "music_query": config.music_query,
        "location_query": config.location_query,
        "image_aspect_policy": {
            "max_aspect_ratio": DOUYIN_MAX_ASPECT_RATIO,
            "recommended_ratios": DOUYIN_RECOMMENDED_RATIOS,
        },
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
        raise DouyinAssistantError(
            "Playwright is required for draft filling. Install the Python package first."
        ) from exc


def first_visible_locator(page: Any, selectors: Sequence[str], *, timeout_ms: int = 1200) -> Any | None:
    return channels.first_visible_locator(page, selectors, timeout_ms=timeout_ms)


def last_visible_locator(page: Any, selectors: Sequence[str], *, timeout_ms: int = 1200) -> Any | None:
    return channels.last_visible_locator(page, selectors, timeout_ms=timeout_ms)


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


def wait_for_douyin_ready(page: Any, *, timeout_sec: int) -> bool:
    deadline = None if timeout_sec <= 0 else time.monotonic() + timeout_sec
    selectors = [
        "text=发布作品",
        "text=发布图文",
        "text=发布视频",
        "text=内容管理",
        "text=作品管理",
        "text=创作服务平台",
        "text=上传",
    ]
    last_notice = time.monotonic()
    while deadline is None or time.monotonic() < deadline:
        if first_visible_locator(page, selectors, timeout_ms=1000) is not None:
            return True
        body_text = visible_body_text(page)
        if "登录" in body_text or "扫码" in body_text or "验证码" in body_text:
            now = time.monotonic()
            if now - last_notice >= 20:
                LOGGER.warning("Still waiting for Douyin login. Please scan/login in Chrome.")
                last_notice = now
        page.wait_for_timeout(700)
    return False


def click_first_text(page: Any, labels: Sequence[str], *, timeout_ms: int = 1200) -> bool:
    selectors: list[str] = []
    for label in labels:
        selectors.extend(
            [
                f"button:has-text('{label}')",
                f"a:has-text('{label}')",
                f"[role=button]:has-text('{label}')",
                f"text={label}",
            ]
        )
    target = first_visible_locator(page, selectors, timeout_ms=timeout_ms)
    if target is None:
        return False
    try:
        target.click(timeout=2500)
        page.wait_for_timeout(500)
        return True
    except Exception as exc:
        LOGGER.debug("Could not click text %s: %s", labels, exc)
        return False


def click_by_dom_text(page: Any, labels: Sequence[str]) -> bool:
    try:
        return bool(
            page.evaluate(
                """
                (labels) => {
                  const normalize = (value) => String(value || "").replace(/\\s+/g, " ").trim();
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
                  const candidates = Array.from(document.querySelectorAll("button,a,[role='button'],div,span"))
                    .filter((el) => {
                      if (!isVisible(el)) return false;
                      const text = normalize(el.textContent);
                      if (!text || text.length > 30) return false;
                      return labels.some((label) => text === label || text.includes(label));
                    })
                    .sort((a, b) => {
                      const ar = a.getBoundingClientRect();
                      const br = b.getBoundingClientRect();
                      return ar.top === br.top ? ar.left - br.left : ar.top - br.top;
                    });
                  if (!candidates.length) return false;
                  candidates[0].click();
                  return true;
                }
                """,
                list(labels),
            )
        )
    except Exception as exc:
        LOGGER.debug("DOM text click failed for %s: %s", labels, exc)
        return False


def click_selector_if_text_matches(
    page: Any,
    selector: str,
    expected_text: str,
    *,
    label: str,
    timeout_ms: int = 1200,
) -> bool:
    locator = first_visible_locator(page, [selector], timeout_ms=timeout_ms)
    if locator is None:
        return False
    try:
        text = clean_text(locator.inner_text(timeout=500))
    except Exception:
        text = ""
    if expected_text not in text:
        LOGGER.debug(
            "Douyin %s selector text did not match %s: %s",
            label,
            expected_text,
            text,
        )
        return False
    try:
        locator.click(timeout=2500)
        page.wait_for_timeout(500)
        LOGGER.info("Clicked Douyin %s via verified selector.", label)
        return True
    except Exception as exc:
        LOGGER.debug("Could not click Douyin %s via verified selector: %s", label, exc)
        return False


def douyin_form_has_file_input(page: Any) -> bool:
    try:
        return page.locator('input[type="file"]').count() > 0
    except Exception:
        return False


def click_douyin_image_tab(page: Any) -> bool:
    clicked = (
        click_selector_if_text_matches(
            page,
            DOUYIN_IMAGE_TAB_SELECTOR,
            "发布图文",
            label="image tab",
            timeout_ms=1000,
        )
        or click_first_text(page, ["发布图文"], timeout_ms=1500)
        or click_by_dom_text(page, ["发布图文"])
    )
    if clicked:
        page.wait_for_timeout(800)
        return True
    LOGGER.debug("Douyin image tab was not clicked automatically.")
    return False


def open_douyin_image_publish_form(page: Any, config: Config) -> bool:
    LOGGER.info("Trying to open Douyin image-post form.")

    click_douyin_image_tab(page)
    if first_visible_locator(page, [DOUYIN_IMAGE_UPLOAD_BUTTON_SELECTOR], timeout_ms=1500) is not None:
        return True

    if douyin_form_has_file_input(page) and "发布图文" in visible_body_text(page):
        return True

    click_first_text(page, ["发布作品", "发布内容", "发布"], timeout_ms=1500) or click_by_dom_text(
        page, ["发布作品", "发布内容", "发布"]
    )
    page.wait_for_timeout(700)
    click_douyin_image_tab(page) or click_first_text(
        page, ["发布图文", "图文", "上传图文"], timeout_ms=1800
    ) or click_by_dom_text(page, ["发布图文", "上传图文", "图文"])
    page.wait_for_timeout(1200)

    if first_visible_locator(page, [DOUYIN_IMAGE_UPLOAD_BUTTON_SELECTOR], timeout_ms=1000) is not None:
        return True

    if douyin_form_has_file_input(page) and "发布图文" in visible_body_text(page):
        return True

    # Some Creator Center builds require entering the upload page directly.
    if page.url.rstrip("/") != config.douyin_url.rstrip("/"):
        try:
            page.goto(config.douyin_url, wait_until="domcontentloaded")
            page.wait_for_timeout(1500)
        except Exception as exc:
            LOGGER.debug("Could not navigate to Douyin upload URL: %s", exc)

    click_douyin_image_tab(page)
    if first_visible_locator(page, [DOUYIN_IMAGE_UPLOAD_BUTTON_SELECTOR], timeout_ms=1500) is not None:
        return True

    if douyin_form_has_file_input(page) and "发布图文" in visible_body_text(page):
        return True

    LOGGER.warning("Could not detect Douyin image-post upload form automatically.")
    return False


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
            LOGGER.info("Selected %d Douyin image(s) via file input.", len(paths))
            return True
        except Exception as exc:
            LOGGER.debug("Douyin file input upload failed at index %d: %s", index, exc)
    return False


def upload_images_via_file_chooser(page: Any, image_paths: Sequence[Path]) -> bool:
    paths = [str(path) for path in image_paths if path.is_file()]
    if not paths:
        return False
    triggers = [
        DOUYIN_IMAGE_UPLOAD_BUTTON_SELECTOR,
        "text=上传图片",
        "text=选择图片",
        "text=上传图文",
        "text=点击上传",
        "button:has-text('上传')",
        "[role=button]:has-text('上传')",
    ]
    trigger = first_visible_locator(page, triggers, timeout_ms=1500)
    if trigger is None:
        return False
    try:
        with page.expect_file_chooser(timeout=5000) as chooser_info:
            trigger.click()
        chooser_info.value.set_files(paths)
        LOGGER.info("Selected %d Douyin image(s) via file chooser.", len(paths))
        return True
    except Exception as exc:
        LOGGER.debug("Douyin file chooser upload failed: %s", exc)
        return False


def upload_douyin_images(page: Any, image_paths: Sequence[Path], config: Config) -> bool:
    if upload_images_via_file_chooser(page, image_paths) or upload_images_via_file_input(page, image_paths):
        wait_for_douyin_upload_settled(page, timeout_sec=config.upload_wait_sec)
        return True
    LOGGER.warning("Could not upload images automatically. Please upload them manually.")
    return False


def wait_for_douyin_upload_settled(page: Any, *, timeout_sec: int) -> bool:
    bad_words = ("上传失败", "解析失败", "校验失败", "处理失败", "失败")
    busy_words = ("上传中", "正在上传", "处理中", "正在处理", "解析中", "校验中", "加载中")
    deadline = time.monotonic() + timeout_sec
    stable_since: float | None = None
    while time.monotonic() < deadline:
        text = visible_body_text(page)
        if any(word in text for word in bad_words):
            LOGGER.warning("Douyin upload page may contain an error: %s", compact_log_text(text))
            return False
        busy = any(word in text for word in busy_words) or bool(re.search(r"\b\d{1,3}\s*%", text))
        if not busy:
            if stable_since is None:
                stable_since = time.monotonic()
            elif time.monotonic() - stable_since >= 3:
                LOGGER.info("Douyin upload appears settled.")
                return True
        else:
            stable_since = None
        page.wait_for_timeout(800)
    LOGGER.warning("Timed out waiting for Douyin upload to settle.")
    return False


def fill_locator_with_keyboard(page: Any, locator: Any, text: str) -> bool:
    try:
        locator.click(timeout=2500)
        page.keyboard.press("Control+A")
        page.keyboard.insert_text(text)
        page.wait_for_timeout(200)
        return True
    except Exception as exc:
        LOGGER.debug("Keyboard fill failed: %s", exc)
        return False


def fill_text_field(page: Any, selectors: Sequence[str], text: str, label: str) -> bool:
    locator = first_visible_locator(page, selectors, timeout_ms=1200)
    if locator is not None and fill_locator_with_keyboard(page, locator, text):
        LOGGER.info("Filled Douyin %s.", label)
        return True
    return fill_text_field_by_dom_hint(page, text, label=label)


def fill_text_field_by_dom_hint(page: Any, text: str, *, label: str) -> bool:
    try:
        result = page.evaluate(
            """
            ({ text, label }) => {
              const hints = label === "title"
                ? ["标题", "作品标题", "添加标题", "请输入标题"]
                : ["正文", "描述", "作品描述", "添加描述", "请输入描述", "说点什么"];
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
        LOGGER.info("Filled Douyin %s via DOM hint.", label)
        return True
    LOGGER.debug("DOM hint fill did not find Douyin %s: %s", label, result)
    return False


def fill_douyin_title(page: Any, title: str) -> bool:
    selectors = [
        'textarea[placeholder*="标题"]',
        'input[placeholder*="标题"]',
        '[contenteditable="true"][data-placeholder*="标题"]',
        '[contenteditable="true"][placeholder*="标题"]',
        '[role="textbox"][aria-label*="标题"]',
    ]
    if fill_text_field(page, selectors, title, "title"):
        return True
    LOGGER.warning("Could not fill Douyin title automatically. Please paste it manually: %s", title)
    return False


def fill_douyin_caption(page: Any, caption: str) -> bool:
    selectors = [
        'textarea[placeholder*="描述"]',
        'textarea[placeholder*="正文"]',
        'textarea[placeholder*="说点什么"]',
        'textarea[placeholder*="添加"]',
        '[contenteditable="true"][data-placeholder*="描述"]',
        '[contenteditable="true"][data-placeholder*="正文"]',
        '[contenteditable="true"][data-placeholder*="说点什么"]',
        '[contenteditable="true"][placeholder*="描述"]',
        '[role="textbox"][aria-label*="描述"]',
        '[role="textbox"][aria-label*="正文"]',
    ]
    if fill_text_field(page, selectors, caption, "caption"):
        return True
    LOGGER.warning("Could not fill Douyin caption automatically. Use caption.txt as fallback.")
    return False


def fill_exact_selector_with_text(
    page: Any,
    selector: str,
    text: str,
    *,
    label: str,
    press_enter: bool = False,
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
        if press_enter:
            page.keyboard.press("Enter")
        page.wait_for_timeout(400)
        LOGGER.info("Filled Douyin %s via exact selector.", label)
        return True
    except Exception as exc:
        LOGGER.debug("Could not fill Douyin %s via exact selector: %s", label, exc)
        return False


def click_exact_selector(page: Any, selector: str, *, label: str, timeout_ms: int = 2500) -> bool:
    locator = first_visible_locator(page, [selector], timeout_ms=timeout_ms)
    if locator is None:
        return False
    try:
        locator.click(timeout=2500)
        page.wait_for_timeout(500)
        LOGGER.info("Clicked Douyin %s via exact selector.", label)
        return True
    except Exception as exc:
        LOGGER.debug("Could not click Douyin %s via exact selector: %s", label, exc)
        return False


def douyin_music_search_selectors() -> list[str]:
    return [
        DOUYIN_MUSIC_SEARCH_SELECTOR,
        "[class*='music-search'] input",
        "input[placeholder*='搜索音乐']",
        "input[placeholder*='搜索歌名']",
        "input[placeholder*='音乐']",
        "input[placeholder*='歌名']",
        "input[placeholder*='搜索']",
    ]


def open_douyin_music_selector(page: Any) -> bool:
    if first_visible_locator(page, douyin_music_search_selectors(), timeout_ms=800) is not None:
        return True
    opened = click_exact_selector(
        page,
        DOUYIN_MUSIC_OPEN_BUTTON_SELECTOR,
        label="music open button",
        timeout_ms=1800,
    )
    if opened and first_visible_locator(page, douyin_music_search_selectors(), timeout_ms=2500) is not None:
        return True
    opened = opened or click_first_text(
        page,
        ["选择音乐", "添加音乐", "音乐", "配乐"],
        timeout_ms=1500,
    ) or click_by_dom_text(page, ["选择音乐", "添加音乐", "音乐", "配乐"])
    if opened:
        page.wait_for_timeout(900)
    return first_visible_locator(page, douyin_music_search_selectors(), timeout_ms=2500) is not None


def click_douyin_music_candidate_by_text(page: Any, query: str) -> bool:
    try:
        result = page.evaluate(
            """
            (query) => {
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
                "[class*='card-container-left'], [class*='music-card'], [class*='music-item'], div, li"
              ))
                .filter((el) => {
                  if (!isVisible(el)) return false;
                  const text = normalize(el.textContent);
                  const rect = el.getBoundingClientRect();
                  return text
                    && text.length <= 120
                    && text.includes(query)
                    && rect.width >= 80
                    && rect.height >= 24
                    && rect.height <= 180;
                })
                .sort((a, b) => {
                  const ar = a.getBoundingClientRect();
                  const br = b.getBoundingClientRect();
                  return ar.top === br.top ? ar.left - br.left : ar.top - br.top;
                });
              if (!candidates.length) return false;
              click(candidates[0]);
              return true;
            }
            """,
            query,
        )
    except Exception as exc:
        LOGGER.debug("Could not click Douyin music candidate by text: %s", exc)
        return False
    return bool(result)


def select_douyin_music(page: Any, query: str) -> bool:
    query = clean_text(query)
    if not query:
        LOGGER.info("Skipping Douyin music selection.")
        return True
    if not open_douyin_music_selector(page):
        LOGGER.warning("Could not open Douyin music selector. Please select music manually: %s", query)
        return False
    filled = False
    for selector in douyin_music_search_selectors():
        if fill_exact_selector_with_text(
            page,
            selector,
            query,
            label="music search",
            press_enter=True,
            timeout_ms=1000,
        ):
            filled = True
            break
    if not filled:
        LOGGER.warning("Could not type Douyin music search automatically: %s", query)
        return False
    page.wait_for_timeout(1200)
    if click_exact_selector(page, DOUYIN_MUSIC_CHOICE_SELECTOR, label="music choice", timeout_ms=3500):
        LOGGER.info("Selected Douyin music: %s", query)
        return True
    if click_douyin_music_candidate_by_text(page, query):
        LOGGER.info("Selected Douyin music by text fallback: %s", query)
        return True
    LOGGER.warning("Could not select Douyin music automatically. Please choose it manually: %s", query)
    return False


def click_douyin_option_by_text(page: Any, query: str) -> bool:
    try:
        result = page.evaluate(
            """
            (query) => {
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
                ".semi-select-option, [role='option'], [class*='option'], [class*='dropdown'] div, li"
              ));
              const fallback = Array.from(document.querySelectorAll("div, li, span"));
              const candidates = [...preferred, ...fallback]
                .filter((el, index, arr) => arr.indexOf(el) === index)
                .filter((el) => {
                  if (!isVisible(el)) return false;
                  const text = normalize(el.textContent);
                  const rect = el.getBoundingClientRect();
                  return text
                    && text.length <= 160
                    && text.includes(query)
                    && rect.width >= 80
                    && rect.height >= 20
                    && rect.height <= 180;
                })
                .sort((a, b) => {
                  const aPreferred = a.matches(".semi-select-option, [role='option'], [class*='option']") ? 0 : 1;
                  const bPreferred = b.matches(".semi-select-option, [role='option'], [class*='option']") ? 0 : 1;
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
            query,
        )
    except Exception as exc:
        LOGGER.debug("Could not click Douyin option by text: %s", exc)
        return False
    return bool(result)


def fill_douyin_location(page: Any, query: str) -> bool:
    query = clean_text(query)
    if not query:
        LOGGER.info("Skipping Douyin location/anchor selection.")
        return True
    selectors = [
        DOUYIN_LOCATION_SELECTOR,
        "#douyin_creator_pc_anchor_jump .semi-select-selection",
        "text=添加位置",
        "text=位置",
    ]
    target = first_visible_locator(page, selectors, timeout_ms=2200)
    if target is None:
        LOGGER.warning("Could not find Douyin location/anchor selector. Please fill manually: %s", query)
        return False
    try:
        target.click(timeout=2500)
        page.wait_for_timeout(500)
        page.keyboard.press("Control+A")
        page.keyboard.insert_text(query)
        page.wait_for_timeout(1200)
    except Exception as exc:
        LOGGER.warning("Could not type Douyin location/anchor automatically: %s", exc)
        return False
    if click_douyin_option_by_text(page, query):
        LOGGER.info("Selected Douyin location/anchor: %s", query)
        return True
    try:
        page.keyboard.press("Enter")
        page.wait_for_timeout(500)
        LOGGER.info("Pressed Enter after typing Douyin location/anchor: %s", query)
        return True
    except Exception as exc:
        LOGGER.warning("Could not confirm Douyin location/anchor. Please choose manually: %s | %s", query, exc)
        return False


def fill_douyin_draft(result: PackageResult, config: Config) -> None:
    if not config.chrome_path.is_file():
        raise DouyinAssistantError(f"Chrome executable not found: {config.chrome_path}")
    payload = read_json(Path(result.post_payload_path))
    if not isinstance(payload, dict):
        raise DouyinAssistantError(f"Invalid Douyin post payload: {result.post_payload_path}")
    image_paths = [Path(str(path)) for path in payload.get("card_paths", [])]
    title = truncate_text(str(payload.get("title") or result.title), DOUYIN_TITLE_LIMIT)
    caption = str(payload.get("caption") or Path(result.caption_path).read_text(encoding="utf-8"))
    music_query = clean_text(payload.get("music_query") or config.music_query)
    location_query = clean_text(payload.get("location_query") or config.location_query)

    sync_playwright = import_playwright()
    LOGGER.info("Opening Douyin Creator Center in local Chrome | %s", config.chrome_path)
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
        page.goto(config.douyin_url, wait_until="domcontentloaded")
        LOGGER.info("Waiting for Douyin Creator Center. Scan/login if prompted.")
        if not wait_for_douyin_ready(page, timeout_sec=config.editor_wait_sec):
            LOGGER.warning(
                "Douyin Creator Center was not detected within %d seconds. "
                "If a login page is showing, complete login and rerun.",
                config.editor_wait_sec,
            )
            return

        open_douyin_image_publish_form(page, config)
        upload_douyin_images(page, image_paths, config)
        fill_douyin_title(page, title)
        fill_douyin_caption(page, caption)
        select_douyin_music(page, music_query)
        fill_douyin_location(page, location_query)

        LOGGER.info(
            "Douyin draft fill attempted. Please review and click publish manually. "
            "Keeping Chrome open for %d seconds.",
            config.review_wait_sec,
        )
        if config.review_wait_sec:
            time.sleep(config.review_wait_sec)
        context.close()


def orchestrate(config: Config) -> dict[str, Any]:
    canonical = read_json(config.canonical_path)
    if not isinstance(canonical, dict):
        raise DouyinAssistantError(f"Canonical JSON must be an object: {config.canonical_path}")

    report: dict[str, Any] = {
        "generated_at": now_iso(),
        "ids": list(config.ids),
        "canonical": str(config.canonical_path),
        "output_dir": str(config.output_dir),
        "package_only": config.package_only,
        "douyin_url": config.douyin_url,
        "music_query": config.music_query,
        "location_query": config.location_query,
        "items": [],
    }

    for item_id in config.ids:
        record = canonical[item_id]
        try:
            result = package_one_item(item_id, record, config)
            report["items"].append(asdict(result))
            write_json(config.report_path, report)
            if not config.package_only:
                fill_douyin_draft(result, config)
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
            raise DouyinAssistantError(f"Canonical JSON must be an object: {canonical_path}")
        config = build_config(args, canonical)
        configure_logging(config.log_level)
        LOGGER.info("Douyin target IDs | %s", ", ".join(config.ids))
        report = orchestrate(config)
        success_count = sum(1 for item in report["items"] if item.get("status") == "success")
        LOGGER.info(
            "Douyin assistant complete | success=%d/%d | report=%s",
            success_count,
            len(config.ids),
            config.report_path,
        )
        return 0
    except (DouyinAssistantError, channels.ChannelsAssistantError) as exc:
        LOGGER.error("%s", exc)
        return 1
    except KeyboardInterrupt:
        LOGGER.error("Interrupted by user.")
        return 130
    except Exception:
        LOGGER.exception("Unexpected Douyin assistant failure")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
