#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
============================================================
📦 LaTeX 项目命名规范重构工具（工业级版本）
============================================================

【工具目标】
----------------------------------------
统一 LaTeX 项目中的命名规范，并确保：
✔ 路径引用同步更新
✔ 编译通过后才应用修改
✔ 全流程可回滚
✔ 支持 dry-run 预览
✔ 生成完整变更日志

----------------------------------------
【适用场景】
----------------------------------------
- 数学讲义 / 教材工程
- 大型 LaTeX 项目结构重构
- 命名规范统一（破窗修复）

----------------------------------------
【命名规则】
----------------------------------------

1️⃣ 模块目录
    00-set → 00_set
    09-geometry-plane → 09_geometry-plane（仅改第一个 -）

2️⃣ 二级结论目录
    S01-arithmetic-seq → S001_arithmetic-seq
    F01-monotonicity → F001_monotonicity

    规则：
    - 字母 + 两位数字 → 三位数字
    - 第一个 - → _
    - 后续 - 保留

3️⃣ tex 文件
    01_statement.tex → 01_statement.tex

----------------------------------------
【核心流程（非常重要）】
----------------------------------------

    Step 1: 扫描项目 → 构建 rename 映射表
    Step 2: 复制项目到 TEMP 目录
    Step 3: 在 TEMP 中：
            - 替换所有 LaTeX 引用
            - 执行重命名
            - 执行 build.bat
    Step 4:
        ✔ 成功 → 备份原项目 → 应用修改
        ❌ 失败 → 终止（原项目不动）

----------------------------------------
【使用方式】
----------------------------------------

1️⃣ 预览修改（强烈建议先执行）
    python rename_tool.py --dry-run

2️⃣ 执行修改（带编译校验）
    python rename_tool.py --apply

3️⃣ 回滚（恢复到修改前）
    python rename_tool.py --rollback

----------------------------------------
【目录结构变化示例】
----------------------------------------

    S01-arithmetic-seq/
        01_statement.tex

    ↓↓↓

    S001_arithmetic-seq/
        01_statement.tex

----------------------------------------
【日志输出】
----------------------------------------

生成文件：
    rename_log.json

内容包括：
    - 执行时间
    - 所有 rename 映射

----------------------------------------
【安全机制】
----------------------------------------

✔ TEMP 测试（不污染原项目）
✔ 自动备份（_backup）
✔ 编译失败自动终止
✔ 支持一键 rollback

----------------------------------------
【注意事项】
----------------------------------------

❗ build.bat 必须无交互（否则会卡死）
❗ 建议使用 latexmk 自动编译
❗ 强烈建议先 git commit

============================================================
"""

import os
import re
import shutil
import subprocess
import argparse
import json
from pathlib import Path
from datetime import datetime

# =========================
# 📁 路径配置
# =========================
ROOT = Path(".").resolve()
BACKUP_DIR = ROOT.parent / (ROOT.name + "_backup")
TEMP_DIR = ROOT.parent / (ROOT.name + "_tmp")
LOG_FILE = ROOT / "rename_log.json"


# =========================
# 🧠 命名规则函数
# =========================
def rename_module(name: str) -> str:
    """
    模块目录命名规则：
    00-set → 00_set
    仅替换第一个 -
    """
    return re.sub(r"^(\d{2})-(.+)", r"\1_\2", name, count=1)


def rename_submodule(name: str) -> str:
    """
    二级结论目录：
    S01-arithmetic → S001_arithmetic
    """
    m = re.match(r"^([A-Z])(\d{2})-(.+)", name)
    if m:
        prefix, num, rest = m.groups()
        return f"{prefix}{int(num):03d}_{rest}"
    return name


def rename_tex(name: str) -> str:
    """
    tex 文件：
    01_statement.tex → 01_statement.tex
    """
    return re.sub(r"^(\d{2})-(.+\.tex)", r"\1_\2", name)


# =========================
# 🔍 构建 rename 映射
# =========================
def build_mapping(root: Path):
    """
    遍历整个项目，构建 rename 映射表

    返回：
        {
            old_path: new_path
        }
    """
    mapping = {}

    for path in root.rglob("*"):
        new_name = path.name

        if path.is_dir():
            new_name = rename_module(new_name)
            new_name = rename_submodule(new_name)

        elif path.suffix == ".tex":
            new_name = rename_tex(new_name)

        if new_name != path.name:
            mapping[str(path)] = str(path.with_name(new_name))

    return mapping


# =========================
# ✏️ 替换 LaTeX 引用
# =========================
import re
from pathlib import Path


def replace_refs(root, mapping):
    """
    工业级 LaTeX 路径替换：
    ✔ 支持带路径
    ✔ 支持不带 .tex
    ✔ 只作用于 \input / \include
    """

    def replace_path(match):
        original = match.group(1)  # 取出 {...} 内内容

        new_path = original

        for old, new in mapping.items():
            old_p = Path(old)
            new_p = Path(new)

            old_stem = old_p.stem
            new_stem = new_p.stem

            old_name = old_p.name
            new_name = new_p.name

            # 1️⃣ 替换完整文件名
            new_path = new_path.replace(old_name, new_name)

            # 2️⃣ 替换无扩展名（关键）
            new_path = new_path.replace(old_stem, new_stem)

        return "{" + new_path + "}"

    pattern = re.compile(r"\\(input|include)\{([^}]*)\}")

    for tex in root.rglob("*.tex"):
        content = tex.read_text(encoding="utf-8")

        def repl(m):
            cmd = m.group(1)
            path = m.group(2)

            new_path = path

            for old, new in mapping.items():
                old_p = Path(old)
                new_p = Path(new)

                old_stem = old_p.stem
                new_stem = new_p.stem

                old_name = old_p.name
                new_name = new_p.name

                new_path = new_path.replace(old_name, new_name)
                new_path = new_path.replace(old_stem, new_stem)

            return f"\\{cmd}{{{new_path}}}"

        new_content = pattern.sub(repl, content)

        tex.write_text(new_content, encoding="utf-8")


# =========================
# 📁 执行重命名
# =========================
def apply_rename(mapping):
    """
    按路径深度排序执行 rename
    防止父目录先改导致路径失效
    """
    items = sorted(mapping.items(), key=lambda x: -len(x[0]))

    for old, new in items:
        if os.path.exists(old):
            os.rename(old, new)


# =========================
# ⚙️ 编译检测
# =========================
def run_build(root: Path):
    """
    执行 build.bat
    返回 True / False
    """
    try:
        result = subprocess.run(
            ["cmd", "/c", "build.bat"],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=180,
        )
        return result.returncode == 0
    except Exception:
        return False


# =========================
# 🧾 日志记录
# =========================
def save_log(mapping):
    data = {"time": str(datetime.now()), "mapping": mapping}
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# =========================
# 🔄 回滚机制
# =========================
def rollback():
    """
    删除当前项目 → 恢复 backup
    """
    if not BACKUP_DIR.exists():
        print("❌ 没有备份，无法回滚")
        return

    if ROOT.exists():
        shutil.rmtree(ROOT)

    shutil.copytree(BACKUP_DIR, ROOT)
    print("✅ 已回滚")


# =========================
# 👀 dry-run
# =========================
def dry_run(mapping):
    print("\n🔍 变更预览：\n")
    for old, new in mapping.items():
        print(f"{old}  →  {new}")
    print(f"\n共 {len(mapping)} 项")


# =========================
# 🚀 主执行逻辑
# =========================
def apply():
    """
    工业级执行流程：
    TEMP → 编译验证 → 正式应用
    """
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)

    print("📦 创建临时环境...")
    shutil.copytree(ROOT, TEMP_DIR)

    mapping = build_mapping(TEMP_DIR)

    print("✏️ 替换引用...")
    replace_refs(TEMP_DIR, mapping)

    print("📁 重命名...")
    apply_rename(mapping)

    print("⚙️ 编译测试...")
    if not run_build(TEMP_DIR):
        print("❌ 编译失败，终止")
        shutil.rmtree(TEMP_DIR)
        return

    print("💾 创建备份...")
    if BACKUP_DIR.exists():
        shutil.rmtree(BACKUP_DIR)
    shutil.copytree(ROOT, BACKUP_DIR)

    print("🚀 应用修改...")
    mapping_real = build_mapping(ROOT)
    replace_refs(ROOT, mapping_real)
    apply_rename(mapping_real)

    save_log(mapping_real)

    shutil.rmtree(TEMP_DIR)

    print("🎉 完成（支持回滚）")


# =========================
# 🧩 CLI 入口
# =========================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LaTeX 命名规范重构工具（工业级）")

    parser.add_argument("--dry-run", action="store_true", help="预览修改")
    parser.add_argument("--apply", action="store_true", help="执行修改")
    parser.add_argument("--rollback", action="store_true", help="回滚")

    args = parser.parse_args()

    if args.rollback:
        rollback()
    else:
        mapping = build_mapping(ROOT)

        if args.dry_run:
            dry_run(mapping)
        elif args.apply:
            apply()
        else:
            print("请使用 --dry-run 或 --apply")
