#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
export_pdf_pages.py

是什么
----
一个用于把 PDF 指定页面导出为图片的命令行工具。

它本质上是对 Poppler 工具 `pdftoppm` 的 Python 封装：
- 支持导出某一页
- 支持导出连续页
- 支持导出多个不连续页
- 支持导出全部页
- 支持 PNG / JPG
- 支持设置 DPI
- 支持自定义输出目录和文件名前缀

为什么
----
在制作数学讲义、小红书图文、PDF 预览图时，经常需要把 PDF 的某一页
导出为高清图片。直接手动截图容易不清晰，手动用软件导出也不利于批量处理。

使用这个脚本的好处：
1. 清晰度可控，比如 300 / 400 / 600 DPI
2. 命令统一，适合长期复用
3. 可以集成到 LaTeX / PDF 自动化流水线
4. 后续可以很容易扩展，比如加水印、裁剪、转 WebP 等功能

依赖
----
需要先安装 Poppler，并确保 `pdftoppm` 可以在命令行中直接运行。

Windows 下验证：

    pdftoppm -h

如果提示找不到命令，需要把 Poppler 的 bin 目录加入 PATH。

怎么用
----
1. 导出第 3 页：

    python export_pdf_pages.py input.pdf --pages 3

2. 导出第 1 到第 6 页：

    python export_pdf_pages.py input.pdf --pages 1-6

3. 导出第 1、3、5 页：

    python export_pdf_pages.py input.pdf --pages 1,3,5

4. 导出第 1 页、第 3 到第 6 页、第 10 页：

    python export_pdf_pages.py input.pdf --pages 1,3-6,10

5. 导出所有页：

    python export_pdf_pages.py input.pdf --pages all

6. 指定输出目录、DPI、格式：

    python export_pdf_pages.py input.pdf --pages 3 --out-dir images --dpi 400 --format png

7. 自定义输出文件名前缀：

    python export_pdf_pages.py C024.pdf --pages 2 --prefix C024_page --dpi 400

8. 导出到小红书预览图建议 300~400 DPI：
    python export_pdf_pages.py C024_ellipse_perimeter_ramanujan.pdf --pages 2 --dpi 400 --out-dir images

输出示例
----
如果执行：

    python export_pdf_pages.py C024.pdf --pages 2 --prefix C024_page

可能生成：

    images/C024_page-2.png
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SUPPORTED_FORMATS = {"png", "jpg", "jpeg"}


def check_pdftoppm_available() -> None:
    """
    检查 pdftoppm 是否可用。

    如果命令行里无法直接运行 pdftoppm，说明 Poppler 没有安装，
    或者 Poppler 的 bin 目录没有加入系统 PATH。
    """
    if shutil.which("pdftoppm") is None:
        raise RuntimeError(
            "找不到 pdftoppm 命令。\n\n"
            "请先安装 Poppler，并把 Poppler 的 bin 目录加入系统 PATH。\n"
            "安装完成后，在命令行执行下面命令验证：\n\n"
            "    pdftoppm -h\n"
        )


def parse_pages(page_text: str) -> str | list[int]:
    """
    解析页码参数。

    支持格式：
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
            start = int(start_text)
            end = int(end_text)

            if start <= 0 or end <= 0:
                raise ValueError("页码必须从 1 开始。")

            if start > end:
                raise ValueError(f"页码范围不合法：{part}")

            pages.update(range(start, end + 1))
        else:
            page = int(part)

            if page <= 0:
                raise ValueError("页码必须从 1 开始。")

            pages.add(page)

    if not pages:
        raise ValueError("没有解析到有效页码。")

    return sorted(pages)


def build_output_prefix(
    pdf_path: Path,
    out_dir: Path,
    prefix: str | None,
    page: int | None = None,
) -> Path:
    """
    构造 pdftoppm 的输出前缀。

    pdftoppm 的输出方式比较特殊：
    它不是直接指定最终文件名，而是指定一个输出前缀。

    例如：

        pdftoppm -f 3 -l 3 -png input.pdf images/page

    可能输出：

        images/page-3.png

    为了让单页导出时文件名更可控，这里给每一页都单独调用一次 pdftoppm。
    """
    base_name = prefix if prefix else pdf_path.stem

    if page is None:
        return out_dir / base_name

    return out_dir / f"{base_name}_page"


def run_pdftoppm(
    pdf_path: Path,
    out_prefix: Path,
    first_page: int | None,
    last_page: int | None,
    dpi: int,
    image_format: str,
) -> None:
    """
    执行 pdftoppm 命令。

    参数说明：
    - first_page / last_page 为 None 时，表示导出全部页
    - image_format 支持 png / jpg / jpeg
    """
    cmd = ["pdftoppm"]

    if first_page is not None:
        cmd.extend(["-f", str(first_page)])

    if last_page is not None:
        cmd.extend(["-l", str(last_page)])

    if image_format == "png":
        cmd.append("-png")
    elif image_format in {"jpg", "jpeg"}:
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


def export_pdf_pages(
    pdf_path: Path,
    pages: str | list[int],
    out_dir: Path,
    dpi: int,
    image_format: str,
    prefix: str | None,
) -> None:
    """
    导出 PDF 页面为图片。

    设计说明：
    - all：一次性导出所有页，效率高
    - 指定页：逐页导出，文件名更稳定，也方便后续扩展单页处理逻辑
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF 文件不存在：{pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"输入文件不是 PDF：{pdf_path}")

    if dpi <= 0:
        raise ValueError("DPI 必须是正整数。")

    image_format = image_format.lower()
    if image_format not in SUPPORTED_FORMATS:
        raise ValueError(f"不支持的图片格式：{image_format}")

    out_dir.mkdir(parents=True, exist_ok=True)

    if pages == "all":
        out_prefix = build_output_prefix(
            pdf_path=pdf_path,
            out_dir=out_dir,
            prefix=prefix,
            page=None,
        )

        run_pdftoppm(
            pdf_path=pdf_path,
            out_prefix=out_prefix,
            first_page=None,
            last_page=None,
            dpi=dpi,
            image_format=image_format,
        )

        print(f"完成：已导出全部页面到目录：{out_dir}")
        return

    for page in pages:
        out_prefix = build_output_prefix(
            pdf_path=pdf_path,
            out_dir=out_dir,
            prefix=prefix,
            page=page,
        )

        run_pdftoppm(
            pdf_path=pdf_path,
            out_prefix=out_prefix,
            first_page=page,
            last_page=page,
            dpi=dpi,
            image_format=image_format,
        )

    print(f"完成：已导出指定页面到目录：{out_dir}")


def create_arg_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器。
    """
    parser = argparse.ArgumentParser(
        description="把 PDF 的指定页面导出为图片。",
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
        help="输出目录，默认：images",
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
        help="图片格式，默认：png",
    )

    parser.add_argument(
        "--prefix",
        default=None,
        help="输出文件名前缀。默认使用 PDF 文件名。",
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
        pages = parse_pages(args.pages)

        export_pdf_pages(
            pdf_path=pdf_path,
            pages=pages,
            out_dir=out_dir,
            dpi=args.dpi,
            image_format=args.format,
            prefix=args.prefix,
        )

        return 0

    except Exception as exc:
        print("错误：")
        print(exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
