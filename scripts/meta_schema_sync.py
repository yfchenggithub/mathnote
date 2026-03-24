# -*- coding: utf-8 -*-
"""
=====================================================================
File Name : meta_schema_sync.py
Project   : 高中数学二级结论知识库 (Mathnote)
Author    : 程远锋
Version   : v4.0 (工业级重构版)
Created   : 2026

=====================================================================
【核心功能】
---------------------------------------------------------------------
本脚本用于：

    ✅ 批量同步 meta.json 与 META_SCHEMA（Python版本）
    ✅ 支持模块级 / 全量 / 单文件同步
    ✅ 支持安全模式（只补字段）与严格模式（补 + 删除）
    ✅ 支持 Dry Run（仅预览变更）
    ✅ 支持 Schema Version 自动升级
    ✅ 支持结构化日志输出（可追踪）

---------------------------------------------------------------------
【为什么需要它？】

随着二级结论数量增长（目标 500+）：

    - 手动维护 meta.json ❌ 不可行
    - 字段容易遗漏 ❌
    - 数据结构容易混乱 ❌

因此引入：

    👉 META_SCHEMA = 唯一数据标准

通过本脚本：

    ✔ 自动补字段
    ✔ 自动清理废字段
    ✔ 保持全项目结构统一

=====================================================================
【使用方法】
---------------------------------------------------------------------

# 1️⃣ 全量同步（默认安全模式） 只补字段，不删除 适合开发期
py meta_schema_sync.py

# 2️⃣ 指定模块同步 只处理指定模块（可扩展过滤逻辑）
py meta_schema_sync.py inequality

# 3️⃣ 单文件调试 不用每次扫全项目 调 schema 极其高效
py meta_schema_sync.py --file path/to/meta.json

# 4️⃣ 严格模式（删除多余字段）补字段 + 删除废字段 上线前用
py meta_schema_sync.py --mode strict

# 5️⃣ Dry Run（只看变更，不写入）防止误操作（非常关键）
py meta_schema_sync.py --dry-run

# 6️⃣ 组合使用
py meta_schema_sync.py inequality --mode strict --dry-run

=====================================================================
【设计原则】
---------------------------------------------------------------------
1. KISS：逻辑清晰，结构直观
2. 可扩展：支持未来 schema 升级
3. 可维护：函数拆分清晰
4. 安全优先：默认不删除用户数据
5. 可调试：支持单文件 & dry-run

=====================================================================
"""

import os
import sys
import json
import copy
from typing import Dict, Any, Tuple

# ==================== Schema 导入 ====================
from meta_schema import META_SCHEMA

# ==================== 全局配置 ====================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
from collections import defaultdict

id_map = defaultdict(list)  # 防止二级结论ID重复
module_stats = defaultdict(int)  # 已处理数量
module_total = defaultdict(int)  # 总数量
# ==================== 子结构 Schema（核心新增） ====================
VALID_BLOCK_TYPES = {
    "statement",
    "explanation",
    "proof",
    "example",
    "trap",
    "summary",
}

CONTENT_BLOCK_SCHEMA = {
    "type": "",
    "title": "",
    "content": "",
    "latex": "",
    "order": 0,
    "foldable": True,
}

# ==================== 模块白名单（核心新增） ====================
import re


def is_module_dir(name: str) -> bool:
    """
    判断是否为模块目录，如 03-conic
    """
    return re.match(r"^\d{2}-[a-z]+$", name) is not None


def is_conclusion_dir(name: str) -> bool:
    """
    判断是否为二级结论目录，如 C001_xxx
    """
    return re.match(r"^[A-Z]\d{3}_", name) is not None


# 自动生成白名单（推荐）
ALLOWED_MODULES = {d for d in os.listdir(PROJECT_ROOT) if is_module_dir(d)}

# ==================== 运行参数解析 ====================


def parse_args():
    args = sys.argv[1:]

    config = {
        "module": None,
        "file": None,
        "mode": "safe",  # safe / strict
        "dry_run": False,
    }

    i = 0
    while i < len(args):
        arg = args[i]

        if arg == "--file":
            config["file"] = args[i + 1]
            i += 1

        elif arg == "--mode":
            config["mode"] = args[i + 1]
            i += 1

        elif arg == "--dry-run":
            config["dry_run"] = True

        else:
            # 默认当作 module
            config["module"] = arg

        i += 1

    return config


# ==================== 工具函数 ====================


def is_empty(value):
    return value == "" or value == [] or value == {} or value is None


# ==================== 核心逻辑 ====================


def merge_schema(meta: Dict, schema: Dict, logs: list, stats: dict, path="") -> bool:
    """
    递归补全字段
    """
    changed = False

    for key, value in schema.items():
        full_key = f"{path}.{key}" if path else key

        if key not in meta:
            meta[key] = copy.deepcopy(value)
            logs.append(f"[ADD] {full_key}")
            stats["added"] += 1
            changed = True

        elif isinstance(value, dict) and isinstance(meta[key], dict):
            if merge_schema(meta[key], value, logs, stats, full_key):
                changed = True
        elif is_empty(meta[key]):
            stats["empty"] += 1
    return changed


def remove_extra_fields(
    meta: Dict, schema: Dict, logs: list, stats: dict, path=""
) -> bool:
    """
    删除 schema 外字段（严格模式）
    """
    changed = False

    for key in list(meta.keys()):
        full_key = f"{path}.{key}" if path else key

        if key not in schema:
            del meta[key]
            logs.append(f"[REMOVE] {full_key}")
            stats["removed"] += 1
            changed = True

        elif isinstance(meta[key], dict) and isinstance(schema.get(key), dict):
            if remove_extra_fields(meta[key], schema[key], logs, stats, full_key):
                changed = True

    return changed


def upgrade_version(
    meta: Dict,
    schema: Dict,
    logs: list,
    stats: dict,
) -> bool:
    """
    自动版本升级
    """
    changed = False

    old_v = meta.get("version", 0)
    new_v = schema.get("version", 0)

    if old_v < new_v:
        meta["version"] = new_v
        logs.append(f"[UPGRADE] version {old_v} → {new_v}")
        changed = True

    return changed


# ==================== contentBlocks 专用处理（核心新增） ====================


def fix_content_blocks(meta: Dict, logs: list, stats: dict):
    changed = False

    blocks = meta.get("contentBlocks", [])

    if not isinstance(blocks, list):
        meta["contentBlocks"] = []
        logs.append("[ERROR] contentBlocks 非法 -> 重置")
        stats["errors"] += 1
        return True

    for i, block in enumerate(blocks):
        path = f"contentBlocks[{i}]"
        if not isinstance(block, dict):
            blocks[i] = copy.deepcopy(CONTENT_BLOCK_SCHEMA)
            logs.append(f"[ERROR] {path} 非法 -> 重置")
            stats["errors"] += 1
            changed = True
            continue
        # 类型校验（核心新增）
        if block.get("type") not in VALID_BLOCK_TYPES:
            logs.append(f"[WARN] {path}.type 非法: {block.get('type')}")
            stats["warnings"] += 1
        if merge_schema(block, CONTENT_BLOCK_SCHEMA, logs, stats, path):
            changed = True

    return changed


def render_progress(module):
    current = module_stats[module]
    total = module_total[module]

    if total == 0:
        return

    percent = int(current / total * 100)
    bar_len = 20
    filled = int(bar_len * current / total)

    bar = "█" * filled + "░" * (bar_len - filled)

    print(f"\r[{module}] {current}/{total}  {bar} {percent}% ", end="")


# ==================== 单文件处理 ====================


def process_meta(path: str, config: dict, global_stats):
    module_dir = os.path.basename(os.path.dirname(os.path.dirname(path)))
    module_stats[module_dir] += 1
    if os.path.getsize(path) == 0:
        print("SKIP empty:", path)

    try:
        with open(path, "r", encoding="utf8") as f:
            meta = json.load(f)
    except Exception as e:
        print("SKIP invalid json:", path)
        print(e)
        return

    logs = []
    changed = False
    # ==================== 强制修正 module / id ====================
    module, id_ = extract_module_and_id(os.path.dirname(path))
    if not id_:
        logs.append(f"[ERROR] {path} 无法解析 id")
    else:
        id_map[id_].append(path)

    if meta.get("module") != module:
        meta["module"] = module
        logs.append(f"[FIX] module -> {module}")
        changed = True

    if meta.get("id") != id_:
        meta["id"] = id_
        logs.append(f"[FIX] id -> {id_}")
        changed = True

    # 模块精确过滤（核心新增）
    if config["module"]:
        if meta.get("module") != config["module"]:
            return

    stats = {
        "added": 0,
        "removed": 0,
        "warnings": 0,
        "errors": 0,
        "empty": 0,
        "upgraded": 0,
    }

    # 版本升级
    if upgrade_version(meta, META_SCHEMA, logs, stats):
        changed = True

    # 补字段
    if merge_schema(meta, META_SCHEMA, logs, stats):
        changed = True

    if fix_content_blocks(meta, logs, stats):
        changed = True
    # 严格模式删除字段
    if config["mode"] == "strict":
        if remove_extra_fields(meta, META_SCHEMA, logs, stats):
            changed = True

    # 输出日志
    if logs:
        print(f"\n[{path}]")
        for log in logs:
            print("  ", log)

    for k in global_stats:
        global_stats[k] += stats[k]

    # 写入文件
    if changed and not config["dry_run"]:
        with open(path, "w", encoding="utf8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

    render_progress(module_dir)
    if module_stats[module_dir] == module_total[module_dir]:
        print(" ✔")


def extract_module_and_id(dir_path):
    """
    从路径中提取 module 和 id
    """
    # D:\mathnote\03-conic\C001_xxx\
    module_dir = os.path.basename(os.path.dirname(dir_path))
    module = module_dir.split("-")[-1]

    name = os.path.basename(dir_path)

    if "_" in name:
        id_part = name.split("_")[0]
    else:
        id_part = name

    return module, id_part


def ensure_meta_exists(dir_path, config):
    meta_path = os.path.join(dir_path, "meta.json")

    module, id_ = extract_module_and_id(dir_path)

    if not os.path.exists(meta_path):
        meta = copy.deepcopy(META_SCHEMA)
        meta["module"] = module
        meta["id"] = id_

        if not config["dry_run"]:
            with open(meta_path, "w", encoding="utf8") as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)

        print(f"[CREATE] {meta_path}")
        return meta_path

    return meta_path


# ==================== 扫描逻辑 ====================


def scan_files(config):
    # 如果指定了单文件，就只处理这个文件，不再扫描目录
    if config["file"]:
        yield config["file"]
        return

    for module_dir in os.listdir(PROJECT_ROOT):
        # ✅ 只处理白名单模块（核心）
        if module_dir not in ALLOWED_MODULES:
            continue

        module_path = os.path.join(PROJECT_ROOT, module_dir)

        # 只处理目录
        if not os.path.isdir(module_path):
            continue

        for sub_dir in os.listdir(module_path):

            if not is_conclusion_dir(sub_dir):
                continue

            conclusion_path = os.path.join(module_path, sub_dir)

            if not os.path.isdir(conclusion_path):
                continue

            meta_path = ensure_meta_exists(conclusion_path, config)

            yield meta_path


def collect_module_totals():
    for module_dir in os.listdir(PROJECT_ROOT):

        if module_dir not in ALLOWED_MODULES:
            continue

        module_path = os.path.join(PROJECT_ROOT, module_dir)

        if not os.path.isdir(module_path):
            continue

        for sub_dir in os.listdir(module_path):

            if is_conclusion_dir(sub_dir):
                module_total[module_dir] += 1


# ==================== 主函数 ====================


def main():
    collect_module_totals()
    # 检查模块目录是否存在
    for m in ALLOWED_MODULES:
        full_path = os.path.join(PROJECT_ROOT, m)
        if not os.path.exists(full_path):
            print(f"[WARN] 模块目录不存在: {m}")
    config = parse_args()

    print("=" * 60)
    print("META SCHEMA SYNC TOOL (v4.0)")
    print("=" * 60)
    print("Project Root:", PROJECT_ROOT)
    print("Mode:", config["mode"])
    print("Dry Run:", config["dry_run"])
    print("Module:", config["module"])
    print("File:", config["file"])
    print()
    global_stats = {
        "added": 0,
        "removed": 0,
        "warnings": 0,
        "errors": 0,
        "empty": 0,
        "upgraded": 0,
    }
    count = 0

    for path in scan_files(config):
        process_meta(path, config, global_stats)
        count += 1
    print("\n===== SUMMARY =====")
    print("Files:", count)
    print("Added:", global_stats["added"])
    print("Removed:", global_stats["removed"])
    print("Warnings:", global_stats["warnings"])
    print("Errors:", global_stats["errors"])
    print("Empty Fields:", global_stats["empty"])
    print("Upgraded:", global_stats["upgraded"])

    print("\n===== ID CHECK =====")
    # 用在 CI / 发布前
    duplicate_found = False
    for id_, paths in id_map.items():
        if len(paths) > 1:
            duplicate_found = True
            print(f"\n[ERROR] Duplicate ID: {id_}")
            for p in paths:
                print("  ", p)

    if not duplicate_found:
        print("No duplicate IDs ✅")
    print("\n===== MODULE SUMMARY =====")
    for module in sorted(module_total.keys()):
        print(f"{module:<20} : {module_total[module]} files")
    print("DONE")


if __name__ == "__main__":
    main()
