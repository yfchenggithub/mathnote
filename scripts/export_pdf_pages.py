#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
export_pdf_pages.py

是什么
----
一个用于把 PDF 页面导出为高清图片的命令行工具。

它可以：
1. 导出 PDF 的某一页为图片
2. 导出 PDF 的连续页为图片
3. 导出 PDF 的多个不连续页为图片
4. 导出 PDF 的全部页面为图片
5. 可选生成小红书 3:4 封面图
6. 可自定义 DPI、输出目录、图片格式、文件名前缀
7. 文件名稳定，不依赖 pdftoppm 自动生成的页码规则

为什么
----
在制作数学讲义、二级结论 PDF、小红书图文、课程资料预览图时，
经常需要把 PDF 的某一页导出为高清图片。

直接截图的问题：
- 清晰度不可控
- 容易模糊
- 尺寸不统一
- 不方便批量处理
- 不适合自动化流水线

本脚本的目标：
- 高清
- 稳定
- 可批量
- 可维护
- 可扩展
- 适合长期沉淀到 LaTeX / PDF / 小红书内容生产流程中

依赖
----
1. Poppler

需要确保命令行可以直接运行：

    pdftoppm -h
    pdfinfo -h

Windows 下如果提示找不到命令，需要把 Poppler 的 bin 目录加入系统 PATH。

2. Pillow

用于生成小红书 3:4 封面图：

    pip install pillow


1. 日常高清，够用
    python.exe .\scripts\export_pdf_pages.py .\build\conclusion_pdfs\C024_ellipse_perimeter_ramanujan.pdf --pages 7 --dpi 400 --out-dir images --xhs-cover --cover-page 2 --xhs-size 1080x1440 --xhs-fit contain --xhs-margin 48 --format png

2. 推荐高清，优先用这个
python.exe .\scripts\export_pdf_pages.py .\build\conclusion_pdfs\C024_ellipse_perimeter_ramanujan.pdf --pages 7 --dpi 600 --out-dir images --xhs-cover --cover-page 2 --xhs-size 2160x2880 --xhs-fit contain --xhs-margin 96 --format png

3. 超高清，适合极端情况，通常不建议使用，除非你知道你在做什么：
    python.exe .\scripts\export_pdf_pages.py .\build\conclusion_pdfs\C024_ellipse_perimeter_ramanujan.pdf --pages 7 --dpi 800 --out-dir images --xhs-cover --cover-page 2 --xhs-size 3240x4320 --xhs-fit contain --xhs-margin 144 --format png

怎么用
----

一、导出第 7 页：

    python scripts/export_pdf_pages.py input.pdf --pages 7

二、导出第 1 到第 6 页：

    python scripts/export_pdf_pages.py input.pdf --pages 1-6

三、导出第 1、3、5 页：

    python scripts/export_pdf_pages.py input.pdf --pages 1,3,5

四、导出第 1 页、第 3 到第 6 页、第 10 页：

    python scripts/export_pdf_pages.py input.pdf --pages 1,3-6,10

五、导出全部页面：

    python scripts/export_pdf_pages.py input.pdf --pages all

六、导出第 7 页，并用第 2 页生成小红书封面：

    python scripts/export_pdf_pages.py input.pdf --pages 7 --xhs-cover --cover-page 2

七、导出第 7 页，400 DPI，并用第 2 页生成 1080x1440 小红书封面：

    python scripts/export_pdf_pages.py input.pdf --pages 7 --dpi 400 --out-dir images --xhs-cover --cover-page 2 --xhs-size 1080x1440/1242x1656/1440x1920

八、数学讲义推荐命令：

    python scripts/export_pdf_pages.py input.pdf --pages 7 --dpi 400 --out-dir images --xhs-cover --cover-page 2 --xhs-size 1080x1440 --xhs-fit contain


输出文件示例
----
如果输入：

    C024_ellipse_perimeter_ramanujan.pdf

执行：

    python scripts/export_pdf_pages.py C024_ellipse_perimeter_ramanujan.pdf --pages 7 --xhs-cover --cover-page 2

会生成：

    images/C024_ellipse_perimeter_ramanujan_page_007.png
    images/C024_ellipse_perimeter_ramanujan_page_002.png
    images_xhs/C024_ellipse_perimeter_ramanujan_xhs_cover_page_002.png

设计说明
----
本脚本导出单页时使用：

    pdftoppm -singlefile

这样 pdftoppm 不会自动追加页码。

也就是说，最终文件名由脚本完全控制，例如：

    xxx_page_002.png

避免不同 Poppler 版本生成 xxx-2.png、xxx-02.png、xxx-000002.png
导致后续找不到文件的问题。
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Literal

from PIL import Image

SUPPORTED_FORMATS = {"png", "jpg", "jpeg"}
XHS_FIT_MODES = {"contain", "cover"}

PageSelection = Literal["all"] | list[int]


def check_pdftoppm_available() -> None:
    """
    检查 pdftoppm 是否可用。
    """
    if shutil.which("pdftoppm") is None:
        raise RuntimeError(
            "找不到 pdftoppm 命令。\n\n"
            "请先安装 Poppler，并把 Poppler 的 bin 目录加入系统 PATH。\n"
            "安装后在命令行执行下面命令验证：\n\n"
            "    pdftoppm -h\n"
        )


def check_pdfinfo_available() -> bool:
    """
    检查 pdfinfo 是否可用。

    pdfinfo 通常随 Poppler 一起安装，用于读取 PDF 总页数。
    """
    return shutil.which("pdfinfo") is not None


def get_pdf_page_count(pdf_path: Path) -> int | None:
    """
    获取 PDF 总页数。

    优先使用 Poppler 自带的 pdfinfo。
    如果读取失败，返回 None。
    """
    if not check_pdfinfo_available():
        return None

    result = subprocess.run(
        ["pdfinfo", str(pdf_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if result.returncode != 0:
        return None

    match = re.search(r"^Pages:\s+(\d+)\s*$", result.stdout, re.MULTILINE)
    if not match:
        return None

    return int(match.group(1))


def parse_pages(page_text: str) -> PageSelection:
    """
    解析页码参数。

    支持：
    - all
    - 3
    - 1-6
    - 1,3,5
    - 1,3-6,10

    注意：
    PDF 页码从 1 开始，不是从 0 开始。
    """
    page_text = page_text.strip().lower()

    if page_text == "all":
        return "all"

    pages: set[int] = set()

    for part in page_text.split(","):
        part = part.strip()

        if not part:
            continue

        if "-" in part:
            start_text, end_text = part.split("-", 1)

            if not start_text.isdigit() or not end_text.isdigit():
                raise ValueError(f"页码范围格式不合法：{part}")

            start = int(start_text)
            end = int(end_text)

            if start <= 0 or end <= 0:
                raise ValueError("页码必须从 1 开始。")

            if start > end:
                raise ValueError(f"页码范围不合法：{part}")

            pages.update(range(start, end + 1))
        else:
            if not part.isdigit():
                raise ValueError(f"页码格式不合法：{part}")

            page = int(part)

            if page <= 0:
                raise ValueError("页码必须从 1 开始。")

            pages.add(page)

    if not pages:
        raise ValueError("没有解析到有效页码。")

    return sorted(pages)


def normalize_image_format(image_format: str) -> str:
    """
    统一图片格式名称。

    内部统一：
    - png
    - jpg

    用户输入 jpeg 时，自动转成 jpg。
    """
    image_format = image_format.lower().strip()

    if image_format not in SUPPORTED_FORMATS:
        raise ValueError(f"不支持的图片格式：{image_format}")

    if image_format == "jpeg":
        return "jpg"

    return image_format


def get_image_suffix(image_format: str) -> str:
    """
    获取图片文件后缀。
    """
    image_format = normalize_image_format(image_format)

    if image_format == "png":
        return "png"

    if image_format == "jpg":
        return "jpg"

    raise ValueError(f"不支持的图片格式：{image_format}")


def build_base_name(pdf_path: Path, prefix: str | None) -> str:
    """
    构造输出文件基础名。
    """
    return prefix if prefix else pdf_path.stem


def build_page_output_prefix(
    pdf_path: Path,
    out_dir: Path,
    prefix: str | None,
    page: int,
) -> Path:
    """
    构造单页导出的输出前缀。

    注意：
    这里配合 pdftoppm 的 -singlefile 使用。

    例如：
        output_prefix = images/C024_page_002

    pdftoppm 会生成：
        images/C024_page_002.png

    这样就不再依赖 pdftoppm 自己的页码命名规则。
    """
    base_name = build_base_name(pdf_path=pdf_path, prefix=prefix)
    return out_dir / f"{base_name}_page_{page:03d}"


def build_page_output_image_path(
    output_prefix: Path,
    image_format: str,
) -> Path:
    """
    根据我们自己控制的 output_prefix 生成最终图片路径。

    因为使用了 pdftoppm -singlefile，所以最终文件名是：

        output_prefix + .png
        output_prefix + .jpg
    """
    suffix = get_image_suffix(image_format)
    return output_prefix.with_suffix(f".{suffix}")


def run_pdftoppm_single_page(
    pdf_path: Path,
    out_prefix: Path,
    page: int,
    dpi: int,
    image_format: str,
) -> Path:
    """
    导出 PDF 的单独一页。

    关键点：
    使用 -singlefile，让 pdftoppm 不再自动追加页码。
    最终文件名由我们自己控制。

    例如：
        out_prefix = images/C024_page_002

    生成：
        images/C024_page_002.png
    """
    image_format = normalize_image_format(image_format)

    cmd = [
        "pdftoppm",
        "-f",
        str(page),
        "-l",
        str(page),
        "-singlefile",
    ]

    if image_format == "png":
        cmd.append("-png")
    elif image_format == "jpg":
        cmd.append("-jpeg")
    else:
        raise ValueError(f"不支持的图片格式：{image_format}")

    cmd.extend(["-r", str(dpi)])
    cmd.append(str(pdf_path))
    cmd.append(str(out_prefix))

    print("执行命令：")
    print(" ".join(cmd))
    print()

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if result.returncode != 0:
        raise RuntimeError(
            "pdftoppm 执行失败。\n\n"
            f"命令：{' '.join(cmd)}\n\n"
            f"stderr:\n{result.stderr}"
        )

    output_image_path = build_page_output_image_path(
        output_prefix=out_prefix,
        image_format=image_format,
    )

    if not output_image_path.exists():
        raise FileNotFoundError(
            "pdftoppm 执行成功，但没有找到预期输出文件。\n\n"
            f"预期文件：{output_image_path}\n\n"
            "这通常说明当前 Poppler 版本的 -singlefile 行为异常，"
            "或者输出目录没有写入权限。"
        )

    return output_image_path


def validate_pages_against_pdf(
    pdf_path: Path,
    pages: PageSelection,
    cover_page: int | None,
) -> None:
    """
    校验页码是否超过 PDF 总页数。

    如果 pdfinfo 不可用，则跳过校验。
    """
    page_count = get_pdf_page_count(pdf_path)

    if page_count is None:
        return

    check_pages: list[int] = []

    if pages == "all":
        check_pages.extend(range(1, page_count + 1))
    else:
        check_pages.extend(pages)

    if cover_page is not None:
        check_pages.append(cover_page)

    for page in check_pages:
        if page > page_count:
            raise ValueError(
                f"页码超出 PDF 总页数：第 {page} 页。\n"
                f"当前 PDF 总页数为：{page_count} 页。"
            )


def export_pdf_pages(
    pdf_path: Path,
    pages: PageSelection,
    out_dir: Path,
    dpi: int,
    image_format: str,
    prefix: str | None,
) -> dict[int, Path]:
    """
    导出 PDF 页面为图片。

    返回：
        {
            1: Path("images/C024_page_001.png"),
            2: Path("images/C024_page_002.png")
        }

    设计说明：
    - 所有页面都逐页导出
    - 每一页都使用 -singlefile
    - 文件名完全由脚本控制
    - 不再依赖 pdftoppm 自动生成的页码文件名
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF 文件不存在：{pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"输入文件不是 PDF：{pdf_path}")

    if dpi <= 0:
        raise ValueError("DPI 必须是正整数。")

    image_format = normalize_image_format(image_format)
    out_dir.mkdir(parents=True, exist_ok=True)

    if pages == "all":
        page_count = get_pdf_page_count(pdf_path)

        if page_count is None:
            raise RuntimeError(
                "无法获取 PDF 总页数。\n\n"
                "原因可能是 pdfinfo 不可用。\n"
                "请确认 Poppler 安装完整，并且 pdfinfo 可以在命令行运行：\n\n"
                "    pdfinfo your.pdf\n"
            )

        page_list = list(range(1, page_count + 1))
    else:
        page_list = pages

    exported: dict[int, Path] = {}

    for page in page_list:
        out_prefix = build_page_output_prefix(
            pdf_path=pdf_path,
            out_dir=out_dir,
            prefix=prefix,
            page=page,
        )

        output_image_path = run_pdftoppm_single_page(
            pdf_path=pdf_path,
            out_prefix=out_prefix,
            page=page,
            dpi=dpi,
            image_format=image_format,
        )

        exported[page] = output_image_path

    print(f"完成：已导出页面到目录：{out_dir}")
    return exported


def parse_size(size_text: str) -> tuple[int, int]:
    """
    解析尺寸字符串。

    支持：
        1080x1440
        1242x1656
        1440x1920
    """
    match = re.fullmatch(r"(\d+)x(\d+)", size_text.strip().lower())

    if not match:
        raise ValueError(f"尺寸格式不正确：{size_text}\n" "正确示例：1080x1440")

    width = int(match.group(1))
    height = int(match.group(2))

    if width <= 0 or height <= 0:
        raise ValueError("图片宽高必须是正整数。")

    return width, height


def parse_hex_color(color_text: str) -> tuple[int, int, int]:
    """
    解析十六进制颜色。

    支持：
        #FFFFFF
        FFFFFF
    """
    color_text = color_text.strip()

    if color_text.startswith("#"):
        color_text = color_text[1:]

    if not re.fullmatch(r"[0-9a-fA-F]{6}", color_text):
        raise ValueError(f"颜色格式不正确：{color_text}，示例：#FFFFFF")

    r = int(color_text[0:2], 16)
    g = int(color_text[2:4], 16)
    b = int(color_text[4:6], 16)

    return r, g, b


def resize_image_contain(
    image: Image.Image,
    box_width: int,
    box_height: int,
) -> Image.Image:
    """
    等比例缩放图片，使其完整放进目标区域。

    不裁剪内容。
    适合数学公式、讲义 PDF、推导过程。
    """
    src_width, src_height = image.size
    scale = min(box_width / src_width, box_height / src_height)

    new_width = max(1, int(src_width * scale))
    new_height = max(1, int(src_height * scale))

    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


def resize_image_cover(
    image: Image.Image,
    box_width: int,
    box_height: int,
) -> Image.Image:
    """
    等比例缩放图片，使其铺满目标区域。

    可能裁剪边缘内容。
    适合照片类封面，不太适合数学讲义。
    """
    src_width, src_height = image.size
    scale = max(box_width / src_width, box_height / src_height)

    new_width = max(1, int(src_width * scale))
    new_height = max(1, int(src_height * scale))

    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    left = max(0, (new_width - box_width) // 2)
    top = max(0, (new_height - box_height) // 2)
    right = left + box_width
    bottom = top + box_height

    return resized.crop((left, top, right, bottom))


def create_xhs_cover(
    source_image_path: Path,
    output_path: Path,
    size: tuple[int, int],
    fit: str,
    background_color: str,
    margin: int,
) -> Path:
    """
    根据导出的 PDF 页面图片，生成小红书 3:4 封面图。

    默认策略：
    - 画布比例：3:4
    - 背景：白色
    - 图片：居中
    - 模式：contain，不裁剪内容

    参数：
    - source_image_path: 原始导出图片
    - output_path: 小红书封面输出路径
    - size: 封面尺寸，例如 1080x1440
    - fit:
        contain: 完整显示，不裁剪
        cover: 铺满画布，可能裁剪
    - background_color: 背景色，例如 #FFFFFF
    - margin: 四周留白
    """
    if not source_image_path.exists():
        raise FileNotFoundError(f"源图片不存在：{source_image_path}")

    if fit not in XHS_FIT_MODES:
        raise ValueError(f"不支持的 xhs-fit：{fit}")

    canvas_width, canvas_height = size

    if margin < 0:
        raise ValueError("margin 不能为负数。")

    if margin * 2 >= canvas_width or margin * 2 >= canvas_height:
        raise ValueError("margin 过大，已经超过画布尺寸。")

    bg_rgb = parse_hex_color(background_color)

    source_image = Image.open(source_image_path).convert("RGB")

    canvas = Image.new(
        mode="RGB",
        size=(canvas_width, canvas_height),
        color=bg_rgb,
    )

    box_width = canvas_width - margin * 2
    box_height = canvas_height - margin * 2

    if fit == "contain":
        processed = resize_image_contain(
            image=source_image,
            box_width=box_width,
            box_height=box_height,
        )
    else:
        processed = resize_image_cover(
            image=source_image,
            box_width=box_width,
            box_height=box_height,
        )

    paste_x = margin + (box_width - processed.width) // 2
    paste_y = margin + (box_height - processed.height) // 2

    canvas.paste(processed, (paste_x, paste_y))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format="PNG", optimize=True)

    return output_path


def pick_default_cover_page(pages: PageSelection) -> int:
    """
    选择默认封面页。

    如果用户指定了 pages：
    - pages=2，则封面默认用第 2 页
    - pages=1,3,5，则封面默认用第 1 页
    - pages=all，则封面默认用第 1 页
    """
    if pages == "all":
        return 1

    return pages[0]


def ensure_cover_page_exported(
    pdf_path: Path,
    exported: dict[int, Path],
    cover_page: int,
    out_dir: Path,
    dpi: int,
    image_format: str,
    prefix: str | None,
) -> dict[int, Path]:
    """
    确保封面页已经导出成图片。

    如果用户导出的是第 7 页，但是指定 cover-page 为 2，
    那么这里会额外导出第 2 页，用来生成封面。
    """
    if cover_page in exported and exported[cover_page].exists():
        return exported

    print(f"封面页第 {cover_page} 页尚未导出，正在额外导出该页...")
    print()

    extra_exported = export_pdf_pages(
        pdf_path=pdf_path,
        pages=[cover_page],
        out_dir=out_dir,
        dpi=dpi,
        image_format=image_format,
        prefix=prefix,
    )

    exported.update(extra_exported)
    return exported


def build_xhs_cover_output_path(
    pdf_path: Path,
    xhs_out_dir: Path,
    prefix: str | None,
    cover_page: int,
) -> Path:
    """
    构造小红书封面输出路径。

    例如：
        images_xhs/C024_xhs_cover_page_002.png
    """
    base_name = build_base_name(pdf_path=pdf_path, prefix=prefix)
    return xhs_out_dir / f"{base_name}_xhs_cover_page_{cover_page:03d}.png"


def create_arg_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器。
    """
    parser = argparse.ArgumentParser(
        description="把 PDF 页面导出为图片，并可选生成小红书 3:4 封面图。",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "pdf",
        help="输入 PDF 文件路径，例如 C024.pdf",
    )

    parser.add_argument(
        "--pages",
        default="all",
        help=("要导出的页码。\n" "支持：all、3、1-6、1,3,5、1,3-6,10\n" "默认：all"),
    )

    parser.add_argument(
        "--out-dir",
        default="images",
        help="普通页面图片输出目录，默认：images",
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=400,
        help="导出图片 DPI，默认：400。小红书/讲义预览建议 300~400。",
    )

    parser.add_argument(
        "--format",
        default="png",
        choices=sorted(SUPPORTED_FORMATS),
        help="导出图片格式，默认：png",
    )

    parser.add_argument(
        "--prefix",
        default=None,
        help="输出文件名前缀。默认使用 PDF 文件名。",
    )

    parser.add_argument(
        "--xhs-cover",
        action="store_true",
        help="是否生成小红书 3:4 封面图。",
    )

    parser.add_argument(
        "--cover-page",
        type=int,
        default=None,
        help=(
            "指定用 PDF 第几页生成小红书封面。\n"
            "默认：使用 pages 中的第一页；如果 pages=all，则默认第 1 页。"
        ),
    )

    parser.add_argument(
        "--xhs-size",
        default="1080x1440",
        help=("小红书封面尺寸，默认：1080x1440。\n" "也可以用：1242x1656、1440x1920。"),
    )

    parser.add_argument(
        "--xhs-out-dir",
        default="images_xhs",
        help="小红书封面输出目录，默认：images_xhs",
    )

    parser.add_argument(
        "--xhs-fit",
        default="contain",
        choices=sorted(XHS_FIT_MODES),
        help=(
            "小红书封面适配方式，默认：contain。\n"
            "contain：完整显示，不裁内容，推荐数学讲义。\n"
            "cover：铺满画布，可能裁剪边缘。"
        ),
    )

    parser.add_argument(
        "--xhs-bg",
        default="#FFFFFF",
        help="小红书封面背景色，默认：#FFFFFF",
    )

    parser.add_argument(
        "--xhs-margin",
        type=int,
        default=48,
        help="小红书封面四周留白，默认：48 像素。",
    )

    return parser


def main() -> int:
    """
    程序入口。
    """
    parser = create_arg_parser()
    args = parser.parse_args()

    try:
        check_pdftoppm_available()

        pdf_path = Path(args.pdf).resolve()
        out_dir = Path(args.out_dir).resolve()
        image_format = normalize_image_format(args.format)
        pages = parse_pages(args.pages)

        cover_page = args.cover_page
        if args.xhs_cover and cover_page is None:
            cover_page = pick_default_cover_page(pages)

        if cover_page is not None and cover_page <= 0:
            raise ValueError("cover-page 必须从 1 开始。")

        validate_pages_against_pdf(
            pdf_path=pdf_path,
            pages=pages,
            cover_page=cover_page,
        )

        exported = export_pdf_pages(
            pdf_path=pdf_path,
            pages=pages,
            out_dir=out_dir,
            dpi=args.dpi,
            image_format=image_format,
            prefix=args.prefix,
        )

        if args.xhs_cover:
            assert cover_page is not None

            exported = ensure_cover_page_exported(
                pdf_path=pdf_path,
                exported=exported,
                cover_page=cover_page,
                out_dir=out_dir,
                dpi=args.dpi,
                image_format=image_format,
                prefix=args.prefix,
            )

            source_image_path = exported[cover_page]

            xhs_size = parse_size(args.xhs_size)
            xhs_out_dir = Path(args.xhs_out_dir).resolve()

            xhs_output_path = build_xhs_cover_output_path(
                pdf_path=pdf_path,
                xhs_out_dir=xhs_out_dir,
                prefix=args.prefix,
                cover_page=cover_page,
            )

            create_xhs_cover(
                source_image_path=source_image_path,
                output_path=xhs_output_path,
                size=xhs_size,
                fit=args.xhs_fit,
                background_color=args.xhs_bg,
                margin=args.xhs_margin,
            )

            print()
            print("小红书 3:4 封面图已生成：")
            print(xhs_output_path)

        print()
        print("全部完成。")
        return 0

    except Exception as exc:
        print("错误：")
        print(exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
