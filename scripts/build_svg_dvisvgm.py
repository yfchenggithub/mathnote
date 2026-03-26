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
import shutil
from typing import Optional
import re

# 解决 Windows 中文输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


# ==============================
# 配置区
# ==============================
CONFIG = {
    # PDF 裁剪
    "use_pdfcrop": True,
    # SVG 转换
    "no_fonts": True,
    "exact": True,
    "bbox": "min",
    # SVG 压缩
    "use_svgo": True,
    # 模式：
    # "default" → 使用 svgo 内置优化
    # "config"  → 使用 svgo.config.js
    "svgo_mode": "config",
    # 可选：自定义 config 文件名（增强扩展性）
    "svgo_config_name": "svgo.config.js",
}

# ==============================
# 命名系统（核心）
# ==============================

# ==============================
# 从完整路径解析 topic（工业级稳健版）
# ==============================


def get_topic(target_dir: Path) -> str:
    """
    从 target_dir 的最后一级目录名中提取 topic

    示例：
    D:/mathnote/03-conic/C016_Hyperbola_Focus_Triangle_Centers
    → C016
    """

    # 1️⃣ 取最后一级目录名（关键点）
    last_dir = target_dir.name

    # 2️⃣ 按 "_" 分割
    parts = last_dir.split("_")

    # 3️⃣ 取前缀
    topic = parts[0]

    # 4️⃣ 安全校验（工业级必须）
    # ✅ 强校验：必须类似 C016 / I01
    if not re.match(r"^[A-Z]\d{3}$", topic):
        raise ValueError(f"[命名系统] 非法 topic 格式: {topic} (路径: {target_dir})")

    return topic


def fname(target_dir: Path, stage: str, state: str, ext: str):
    topic = get_topic(target_dir)
    return f"{topic}.{stage}.{state}.{ext}"


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

    tex_path = target_dir / fname(target_dir, "source", "raw", "tex")
    tex_path.write_text(content, encoding="utf-8")
    print(f"[生成] {tex_path.name}")


def compile_pdf(target_dir: Path):
    tex_name = fname(target_dir, "source", "raw", "tex")
    pdf_name = fname(target_dir, "build", "raw", "pdf")

    cmd = f"latexmk -xelatex -interaction=nonstopmode -halt-on-error {tex_name}"
    run_command(cmd, cwd=target_dir)

    # latexmk 默认输出同名 PDF → 重命名
    original_pdf = target_dir / tex_name.replace(".tex", ".pdf")
    target_pdf = target_dir / pdf_name

    if original_pdf.exists():
        # 如果目标已存在则先删除，防止 Windows 下 rename 失败
        if target_pdf.exists():
            target_pdf.unlink()
        original_pdf.rename(target_pdf)
    else:
        raise FileNotFoundError(f"编译失败，未找到 PDF: {original_pdf}")

    print(f"[PDF] {target_pdf.name}")

    # 3. 执行清理（仅清理中间文件，保留 PDF）
    # -c 表示清理中间文件；-silent 减少清理时的日志输出
    clean_cmd = f"latexmk -c {tex_name}"
    run_command(clean_cmd, cwd=target_dir, allow_fail=True)
    print(f"[Clean] 中间文件已清理")


# ==============================
# ⭐ 新增：PDF 裁剪（增强点）
# ==============================


def crop_pdf(target_dir: Path):
    """
    使用 pdfcrop 去除白边
    """

    if not CONFIG["use_pdfcrop"]:
        return fname(target_dir, "build", "raw", "pdf")

    print("\n[步骤] PDF 裁剪（pdfcrop）")

    input_pdf = fname(target_dir, "build", "raw", "pdf")
    output_pdf = fname(target_dir, "crop", "cropped", "pdf")

    # ⚠️ 允许失败（防止环境没装 pdfcrop）
    run_command(f"pdfcrop {input_pdf} {output_pdf}", cwd=target_dir, allow_fail=True)

    # 如果裁剪成功，用 output.pdf，否则 fallback
    cropped = target_dir / output_pdf

    if cropped.exists():
        print("✔ 使用裁剪后的 PDF")
        return output_pdf
    else:
        print("⚠️ 使用原始 PDF（未裁剪）")
        return input_pdf


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

    svg_name = fname(target_dir, "vector", "dvisvgm", "svg")
    cmd = f'dvisvgm --pdf "{pdf_name}" ' f'-o "{svg_name}" ' f"{options_str}"

    run_command(cmd, cwd=target_dir)
    print(f"[SVG] {svg_name}")
    return svg_name


def optimize_svg(target_dir: Path, input_svg: str):
    if not CONFIG.get("use_svgo", False):
        return

    input_path = target_dir / input_svg
    output_svg = fname(target_dir, "optimize", "svgo", "svg")
    output_path = target_dir / output_svg

    if not input_path.exists():
        raise FileNotFoundError(f"[SVGO] SVG not found: {input_path}")

    # 1️⃣ 查找 svgo 可执行文件（跨平台）
    svgo_bin = shutil.which("svgo") or shutil.which("svgo.cmd")

    if not svgo_bin:
        raise RuntimeError(
            "[SVGO] svgo not found. Please install via `npm i -g svgo` "
            "or add it to PATH."
        )

    # 3️⃣ 构建命令（关键点：--config）
    mode = CONFIG.get("svgo_mode", "config")

    # 2️⃣ 构建命令
    cmd = [svgo_bin, input_svg, "-o", output_svg]

    if mode == "config":
        config_path = _find_svgo_config(
            target_dir,
            CONFIG.get("svgo_config_name", "svgo.config.js"),
        )
        if config_path:
            cmd.extend(["--config", str(config_path)])
        else:
            print(f"[SVGO] not found svgo.config.js, use default svgo")

    elif mode == "default":
        # 👉 什么都不加，走 svgo 默认 preset
        pass

    else:
        raise ValueError(f"[SVGO] Unknown mode: {mode}")
    # 4️⃣ 执行
    run_command(cmd, cwd=target_dir)
    print(f"[SVGO] {output_svg}")
    # 👉 生成 final（软标准）
    final_svg = target_dir / fname(target_dir, "final", "clean", "svg")
    shutil.copy(output_path, final_svg)


def _find_svgo_config(start_dir: Path, config_name: str) -> Optional[Path]:
    """
    向上查找 svgo 配置文件（支持自定义名称）

    行为：
    - 找到：返回 Path
    - 未找到：返回 None（不抛异常）

    参数：
    - start_dir: 起始目录
    - config_name: 配置文件名（如 svgo.config.js）

    返回：
    - Optional[Path]
    """

    current = start_dir.resolve()

    for parent in [current] + list(current.parents):
        candidate = parent / config_name
        if candidate.exists():
            return candidate

    return None


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

    svg_name = convert_pdf_to_svg(target_dir, pdf_name)
    # svg_path = target_dir / "output.svg"
    # lighten_watermark_svg(
    #     svg_path, opacity=0.02, watermark_text="OK-SHUXUE"  # ⭐ 推荐更浅一点
    # )
    optimize_svg(target_dir, svg_name)

    final_name = fname(target_dir, "final", "clean", "svg")
    print(f"\n✅ 完成！最终输出: {final_name}")


# ==============================
# CLI
# ==============================


def main():
    if len(sys.argv) != 3:
        print("usage：python build_svg_dvisvgm.py <module> <conclusion>")
        return

    base_dir = Path("D:/mathnote")
    module = sys.argv[1]
    topic = sys.argv[2]

    build_one(base_dir, module, topic)


if __name__ == "__main__":
    main()
