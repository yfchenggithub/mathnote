#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
LaTeX → PDF → WebP 图片自动生成脚本（支持模块 & 二级结论定制）
============================================================

【功能介绍】
本脚本用于将指定模块下的某个“二级结论”的 01~06.tex 文件：

    01-statement.tex
    02-explanation.tex
    03-proof.tex
    04-examples.tex
    05-traps.tex
    06-summary.tex

自动完成以下流程：

1. 合并为 61.tex
2. 编译生成 PDF
3. 自动裁剪白边
4. 转换为 WebP 图片（小体积，适合小程序）

【特点】
- 支持“模块级”和“二级结论级”精确生成
- 高可维护性（结构清晰、函数拆分）
- 易扩展（后续可加缓存 / 分块生成）

【目录示例】
D:\mathnote\
    └── 07-inequality\
        └── I01_Compound_Inequality_Transformation\
            ├── 01-statement.tex
            ├── 02-explanation.tex
            ├── 03-proof.tex
            ├── 04-examples.tex
            ├── 05-traps.tex
            ├── 06-summary.tex

【输出】
在当前二级结论目录下生成：
    output.webp

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
# 配置区（可扩展）
# ==============================
CONFIG = {
    "density": 300,  # 图片清晰度
    "quality": 90,  # WebP压缩质量
    "resize_width": 2000,  # 输出宽度（适配小程序）
}


# ==============================
# 工具函数
# ==============================


def run_command(cmd, cwd=None):
    """
    执行系统命令
    """
    print(f"\n[执行] {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)

    if result.returncode != 0:
        raise RuntimeError(f"命令执行失败: {cmd}")


def check_file_exists(path: Path):
    """
    检查文件是否存在
    """
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")


# ==============================
# 核心功能
# ==============================


def generate_main_tex(target_dir: Path):
    """
    生成 61.tex（合并6个tex）
    """

    tex_files = [
        "01-statement.tex",
        "02-explanation.tex",
        "03-proof.tex",
        "04-examples.tex",
        "05-traps.tex",
        "06-summary.tex",
    ]
    # 检查文件
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
    """
    编译 LaTeX 生成 PDF
    """
    run_command(
        "latexmk -xelatex -interaction=nonstopmode -halt-on-error 61.tex",
        cwd=target_dir,
    )


def crop_pdf(target_dir: Path):
    """
    裁剪 PDF 白边
    """
    run_command("pdfcrop 61.pdf output.pdf", cwd=target_dir)


def convert_to_webp(target_dir: Path):
    """
    PDF → WebP
    """
    density = CONFIG["density"]
    quality = CONFIG["quality"]
    width = CONFIG["resize_width"]

    cmd = (
        f"magick -density {density} output.pdf "
        f"-resize {width}x -quality {quality} output.webp"
    )

    run_command(cmd, cwd=target_dir)


# ==============================
# 主流程
# ==============================


def build_one(base_dir: Path, module: str, topic: str):
    """
    构建某个二级结论

    参数：
    - base_dir: 根目录（如 D:/mathnote）
    - module: 模块名（如 07-inequality）
    - topic: 二级结论名
    """

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
    convert_to_webp(target_dir)

    print("\n✅ 完成！输出文件: output.webp")


# ==============================
# CLI入口
# ==============================


def main():
    """
    使用方式：

    python build_images.py 07-inequality I01_Compound_Inequality_Transformation
    """

    import sys

    if len(sys.argv) != 3:
        print("\n用法：")
        print("python build_images.py <模块名> <二级结论名>")
        return

    base_dir = Path("D:/mathnote")
    module = sys.argv[1]
    topic = sys.argv[2]

    build_one(base_dir, module, topic)


if __name__ == "__main__":
    main()
