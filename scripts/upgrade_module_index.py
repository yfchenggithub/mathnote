#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
============================================================
模块二级目录编号升级工具（F01 → F001）
============================================================

【功能说明】
本脚本用于批量将如下目录结构：

    00_set/
        S01_Subset_Count/
        S02_xxx/

转换为：

    00_set/
        S001_Subset_Count/
        S002_xxx/

并同步更新所有 LaTeX 文件中的引用路径，例如：

    \input{00_set/S01_Subset_Count/main.tex}
    → \input{00_set/S001_Subset_Count/main.tex}

------------------------------------------------------------

【支持功能】
✔ 目录重命名
✔ .tex 文件内容同步替换
✔ 自动扫描 main.tex / index.tex
✔ dry-run（仅预览，不修改）
✔ apply（实际执行）
✔ 模块过滤（只处理指定模块）

------------------------------------------------------------

【使用示例】

# 1. 预览（推荐先执行）
python upgrade_module_index.py --root D:/mathnote --dry-run

# 2. 实际执行
python upgrade_module_index.py --root D:/mathnote --apply

# 3. 只处理部分模块
python upgrade_module_index.py --root D:/mathnote --modules 00_set 01_function --apply

------------------------------------------------------------

【注意事项】
⚠ 强烈建议先使用 --dry-run 查看变更
⚠ 建议配合 Git 使用，方便回滚
⚠ 仅处理符合规则：字母 + 两位数字 + 下划线 的目录

============================================================
"""

import os
import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple


# =============================
# 配置区（可扩展）
# =============================

# 模块命名范围（可扩展）
DEFAULT_MODULE_RANGE = [
    f"{i:02d}_{name}"
    for i, name in enumerate(
        [
            "set",
            "function",
            "sequence",
            "conic",
            "vector",
            "geometry-solid",
            "probability-stat",
            "inequality",
            "trigonometry",
            "geometry-plane",
        ]
    )
]

# 目录匹配规则：F01_xxx
DIR_PATTERN = re.compile(r"^([A-Z])(\d{2})_(.+)$")


# =============================
# 工具函数
# =============================


def build_new_name(old_name: str) -> str:
    """
    将 F01_xxx → F001_xxx
    """
    match = DIR_PATTERN.match(old_name)
    if not match:
        return None

    prefix, num, suffix = match.groups()
    new_num = f"{int(num):03d}"  # 三位
    return f"{prefix}{new_num}_{suffix}"


def scan_subdirs(module_path: Path) -> Dict[str, str]:
    """
    扫描需要重命名的目录
    返回：{旧名: 新名}
    """
    mapping = {}

    for item in module_path.iterdir():
        if item.is_dir():
            new_name = build_new_name(item.name)
            if new_name and new_name != item.name:
                mapping[item.name] = new_name

    return mapping


def replace_in_file(file_path: Path, mapping: Dict[str, str], dry_run: bool):
    """
    替换文件中的路径引用
    """
    content = file_path.read_text(encoding="utf-8")

    new_content = content
    for old, new in mapping.items():
        new_content = new_content.replace(old, new)

    if new_content != content:
        print(f"[UPDATE] {file_path}")

        if not dry_run:
            file_path.write_text(new_content, encoding="utf-8")


def process_module(module_path: Path, dry_run: bool):
    """
    处理单个模块
    """
    print(f"\n=== 模块: {module_path.name} ===")

    mapping = scan_subdirs(module_path)

    if not mapping:
        print("无需要处理的目录")
        return

    # 打印变更
    for old, new in mapping.items():
        print(f"[RENAME] {old} → {new}")

    # 1️⃣ 修改 tex 文件
    for root, _, files in os.walk(module_path):
        for file in files:
            if file.endswith(".tex"):
                file_path = Path(root) / file
                replace_in_file(file_path, mapping, dry_run)

    # 2️⃣ 重命名目录（必须最后做）
    if not dry_run:
        for old, new in mapping.items():
            old_path = module_path / old
            new_path = module_path / new

            if not new_path.exists():
                old_path.rename(new_path)
            else:
                print(f"[WARN] 已存在: {new_path}")


# =============================
# 主函数
# =============================


def main():
    parser = argparse.ArgumentParser(description="模块编号升级工具")

    parser.add_argument("--root", required=True, help="项目根目录")
    parser.add_argument("--modules", nargs="*", help="指定模块（可选）")
    parser.add_argument("--dry-run", action="store_true", help="仅预览")
    parser.add_argument("--apply", action="store_true", help="实际执行")

    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("❌ 必须指定 --dry-run 或 --apply")
        return

    root = Path(args.root)

    modules = args.modules if args.modules else DEFAULT_MODULE_RANGE

    print("====================================")
    print("模块编号升级工具")
    print("模式:", "DRY-RUN" if args.dry_run else "APPLY")
    print("====================================")

    for module in modules:
        module_path = root / module

        if not module_path.exists():
            print(f"[跳过] 模块不存在: {module}")
            continue

        process_module(module_path, args.dry_run)

    print("\n✅ 完成")


if __name__ == "__main__":
    main()
