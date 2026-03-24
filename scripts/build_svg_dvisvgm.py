#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
============================================================
LaTeX → PDF → SVG 自动生成脚本（最终稳定版 + 裁剪增强）
============================================================

【流程】

LaTeX → PDF
      ↓
pdfcrop（可选，强烈推荐）
      ↓
dvisvgm → SVG

【特点】

- ✅ 支持中文 + 数学
- ✅ 双重裁剪（pdfcrop + bbox）
- ✅ 无内容缺失
- ✅ 高稳定性
- ✅ 可扩展（分块 / JSON）

============================================================
"""

import subprocess
from pathlib import Path
import sys
import io

# 解决 Windows 中文输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


# ==============================
# 配置区
# ==============================
CONFIG = {
    # PDF 编译
    "latex_cmd": "latexmk -xelatex -interaction=nonstopmode -halt-on-error 61.tex",
    # PDF 裁剪
    "use_pdfcrop": True,
    # SVG 转换
    "no_fonts": True,
    "exact": True,
    "bbox": "min",
    # SVG 压缩
    "use_svgo": True,
}


# ==============================
# 工具函数
# ==============================


def run_command(cmd, cwd=None, allow_fail=False):
    print(f"\n[执行] {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)

    if result.returncode != 0:
        if allow_fail:
            print("⚠️ 命令失败，但已忽略")
        else:
            raise RuntimeError(f"命令执行失败: {cmd}")


def check_file_exists(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")


# ==============================
# 核心逻辑
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

    (target_dir / "61.tex").write_text(content, encoding="utf-8")
    print("[生成] 61.tex 完成")


def compile_pdf(target_dir: Path):
    run_command(CONFIG["latex_cmd"], cwd=target_dir)


# ==============================
# ⭐ 新增：PDF 裁剪（增强点）
# ==============================


def crop_pdf(target_dir: Path):
    """
    使用 pdfcrop 去除白边
    """

    if not CONFIG["use_pdfcrop"]:
        return

    print("\n[步骤] PDF 裁剪（pdfcrop）")

    # ⚠️ 允许失败（防止环境没装 pdfcrop）
    run_command("pdfcrop 61.pdf output.pdf", cwd=target_dir, allow_fail=True)

    # 如果裁剪成功，用 output.pdf，否则 fallback
    cropped = target_dir / "output.pdf"
    original = target_dir / "61.pdf"

    if cropped.exists():
        print("✔ 使用裁剪后的 PDF")
        return "output.pdf"
    else:
        print("⚠️ 使用原始 PDF（未裁剪）")
        return "61.pdf"


# ==============================
# SVG 转换
# ==============================


def convert_pdf_to_svg(target_dir: Path, pdf_name: str):
    options = []

    if CONFIG["no_fonts"]:
        options.append("--no-fonts")

    if CONFIG["exact"]:
        options.append("--exact")

    if CONFIG["bbox"]:
        options.append(f"--bbox={CONFIG['bbox']}")

    options_str = " ".join(options)

    cmd = f'dvisvgm --pdf "{pdf_name}" ' f'-o "output.svg" ' f"{options_str}"

    run_command(cmd, cwd=target_dir)


def optimize_svg(target_dir: Path):
    if not CONFIG["use_svgo"]:
        return

    run_command('svgo.cmd "output.svg"', cwd=target_dir)


def lighten_watermark_svg(svg_path: Path, opacity=0.03, watermark_text="MATHNOTE"):
    """
    精准降低 SVG 水印透明度（基于文本 + 旋转）
    """

    import re

    content = svg_path.read_text(encoding="utf-8")

    def replace_text_block(match):
        block = match.group(0)

        # 判断是否是水印
        if watermark_text in block and "rotate" in block:
            # 如果已经有 opacity，替换
            if "opacity=" in block:
                block = re.sub(r'opacity="[^"]*"', f'opacity="{opacity}"', block)
            else:
                block = block.replace("<text", f'<text opacity="{opacity}"')

        return block

    # 匹配所有 text 节点（跨行）
    content = re.sub(r"<text[\s\S]*?</text>", replace_text_block, content)

    svg_path.write_text(content, encoding="utf-8")
    print("✔ 水印透明度已优化（精准匹配）")


# ==============================
# 主流程
# ==============================


def build_one(base_dir: Path, module: str, topic: str):
    target_dir = base_dir / module / topic

    print("\n========== 开始处理 ==========")
    print(f"模块: {module}")
    print(f"结论: {topic}")

    generate_main_tex(target_dir)
    compile_pdf(target_dir)

    # ⭐ 关键：获取实际使用的 PDF
    pdf_name = crop_pdf(target_dir)

    convert_pdf_to_svg(target_dir, pdf_name)
    # svg_path = target_dir / "output.svg"
    # lighten_watermark_svg(
    #     svg_path, opacity=0.02, watermark_text="OK-SHUXUE"  # ⭐ 推荐更浅一点
    # )
    optimize_svg(target_dir)

    print("\n✅ 完成！输出: output.svg")


# ==============================
# CLI
# ==============================


def main():
    if len(sys.argv) != 3:
        print("用法：python build_svg_dvisvgm.py <模块> <结论>")
        return

    base_dir = Path("D:/mathnote")
    module = sys.argv[1]
    topic = sys.argv[2]

    build_one(base_dir, module, topic)


if __name__ == "__main__":
    main()
