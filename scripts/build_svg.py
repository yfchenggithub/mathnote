#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
LaTeX → PDF → SVG 自动生成脚本（高质量矢量版）
============================================================

【功能介绍】
基于 build_webp.py 扩展，实现：

1. 合并 6 个 tex → 61.tex
2. 编译生成 PDF
3. 自动裁剪白边（pdfcrop）
4. PDF → SVG（Inkscape）
5. 自动裁剪 + 去边距 + 居中
6. SVG 压缩（svgo）

【特点】
- 完全复用原有流程（可维护性强）
- 矢量输出（无限清晰）
- 自动优化（适合小程序）
- 可扩展（可继续接 WebP / HTML）

【输出】
    output.svg（最终结果）

============================================================
"""

import os
import subprocess
from pathlib import Path
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# ==============================
# 配置区（核心优化参数）
# ==============================
CONFIG = {
    "svg_scale": 1.5,  # 放大比例（防止细线过细）
    "use_svgo": True,  # 是否压缩 SVG
}


# ==============================
# 工具函数
# ==============================


def run_command(cmd, cwd=None):
    print(f"\n[执行] {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)

    if result.returncode != 0:
        raise RuntimeError(f"命令执行失败: {cmd}")


def check_file_exists(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")


# ==============================
# 核心功能（基本复用）
# ==============================


def generate_main_tex(target_dir: Path):
    tex_files = [
        "01-statement.tex",
        "02-explanation.tex",
        "03-proof.tex",
        "04-examples.tex",
        "05-traps.tex",
        "06-summary.tex",
    ]

    for f in tex_files:
        check_file_exists(target_dir / f)

    content = r"""
\documentclass{article}
\def\rootpath{D:/mathnote}
\input{\rootpath/preamble.tex}
\input{\rootpath/settings.tex}
\begin{document}
"""

    for f in tex_files:
        content += f"\\input{{{f}}}\n"

    content += "\\end{document}"

    main_tex_path = target_dir / "61.tex"
    main_tex_path.write_text(content, encoding="utf-8")

    print(f"[生成] 61.tex 完成: {main_tex_path}")


def compile_pdf(target_dir: Path):
    run_command(
        "latexmk -xelatex -interaction=nonstopmode -halt-on-error 61.tex",
        cwd=target_dir,
    )


def crop_pdf(target_dir: Path):
    """
    PDF 裁剪（去白边）
    """
    run_command("pdfcrop 61.pdf output.pdf", cwd=target_dir)


# ==============================
# ⭐ 核心新增：PDF → SVG
# ==============================


def convert_to_svg(target_dir: Path):
    """
    PDF → SVG（高质量）
    """

    scale = CONFIG["svg_scale"]

    cmd = (
        f'inkscape "output.pdf" '
        f"--export-type=svg "
        f'--export-filename="output.svg" '
        f"--export-area-drawing "  # ⭐ 自动裁剪
        f"--export-text-to-path "  # ⭐ 字体转路径（防丢）
        f"--export-dpi=300 "
    )

    run_command(cmd, cwd=target_dir)


# ==============================
# ⭐ SVG 后处理（优化）
# ==============================


def optimize_svg(target_dir: Path):
    """
    SVG 压缩优化（svgo）
    """
    if not CONFIG["use_svgo"]:
        return

    svg_path = target_dir / "output.svg"

    if not svg_path.exists():
        raise FileNotFoundError("SVG 文件不存在，无法优化")

    cmd = f'svgo.cmd "{svg_path}"'
    run_command(cmd)


# ==============================
# 主流程
# ==============================


def build_one(base_dir: Path, module: str, topic: str):
    target_dir = base_dir / module / topic

    print(f"\n========== 开始处理 ==========")
    print(f"模块: {module}")
    print(f"结论: {topic}")
    print(f"路径: {target_dir}")

    if not target_dir.exists():
        raise FileNotFoundError(f"目录不存在: {target_dir}")

    generate_main_tex(target_dir)
    compile_pdf(target_dir)
    crop_pdf(target_dir)

    # ⭐ 核心新增流程
    convert_to_svg(target_dir)
    optimize_svg(target_dir)

    print("\n完成！输出文件: output.svg")


# ==============================
# CLI入口（完全复用）
# ==============================


def main():
    """
    使用方式：

    python build_svg.py 07-inequality I01_Compound_Inequality_Transformation
    """

    import sys

    if len(sys.argv) != 3:
        print("\n用法：")
        print("python build_svg.py <模块名> <二级结论名>")
        return

    base_dir = Path("D:/mathnote")
    module = sys.argv[1]
    topic = sys.argv[2]

    build_one(base_dir, module, topic)


if __name__ == "__main__":
    main()
