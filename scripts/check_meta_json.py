# -*- coding: utf-8 -*-
"""
=============================================================
File: check_meta_json.py
用途：校验所有 meta.json 是否符合 META_SCHEMA 规范（只检查，不修改）

【核心目标】
-------------------------------------------------------------
1. 校验 meta.json 结构是否完整（字段缺失 / 类型错误）
2. 校验 module / id 是否正确（防止路径篡改）
3. 校验 contentBlocks 结构是否合法（核心渲染数据）
4. 校验是否存在非法字段（schema 之外）
5. 提供清晰日志，便于修复

⚠️ 注意：
- 本脚本只做“检查”，不做修改
- 自动修复请使用：meta_schema_sync.py

=============================================================
"""

import os
import json
import re
import datetime
from typing import Dict, Any

from meta_schema import META_SCHEMA

# ==================== 项目路径 ====================
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# ==================== contentBlocks 校验规则 ====================
VALID_BLOCK_TYPES = {
    "statement",
    "explanation",
    "proof",
    "example",
    "trap",
    "summary",
}

REPORT = {
    "summary": {
        "totalFiles": 0,
        "errorFiles": 0,
        "totalErrors": 0,
        "status": "",
        "generatedAt": "",
    },
    "files": [],
}
# ==================== 目录规则 ====================
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


def is_module_dir(name: str) -> bool:
    return re.match(r"^\d{2}-[a-z]+$", name) is not None


def is_conclusion_dir(name: str) -> bool:
    return re.match(r"^[A-Z]\d{3}_", name) is not None


# ==================== 工具函数 ====================


def extract_module_and_id(dir_path: str):
    """
    从目录路径提取 module 和 id

    示例：
    03-inequality/C001_xxx → module=inequality, id=C001
    """
    module_dir = os.path.basename(os.path.dirname(dir_path))
    module = module_dir.split("-")[-1]

    name = os.path.basename(dir_path)
    id_ = name.split("_")[0]

    return module, id_


# ==================== 核心校验 ====================


def check_schema(meta: Dict, schema: Dict, path="") -> list:
    """
    递归检查 schema 结构

    返回：
    - errors: 所有错误列表
    """
    errors = []

    # 1️⃣ 检查缺失字段
    for key in schema:
        full_key = f"{path}.{key}" if path else key

        if key not in meta:
            errors.append(f"[MISSING] {full_key}")
        else:
            # 如果是 dict，递归检查
            if isinstance(schema[key], dict) and isinstance(meta[key], dict):
                errors.extend(check_schema(meta[key], schema[key], full_key))

    # 2️⃣ 检查多余字段
    for key in meta:
        full_key = f"{path}.{key}" if path else key

        if key not in schema:
            errors.append(f"[EXTRA] {full_key}")

    return errors


def check_content_blocks(meta: Dict) -> list:
    """
    校验 contentBlocks（核心结构）

    检查：
    - 是否为 list
    - 每个 block 是否为 dict
    - type 是否合法
    """
    errors = []

    blocks = meta.get("contentBlocks", [])

    if not isinstance(blocks, list):
        return ["[ERROR] contentBlocks 不是数组"]

    for i, block in enumerate(blocks):
        path = f"contentBlocks[{i}]"

        if not isinstance(block, dict):
            errors.append(f"[ERROR] {path} 不是对象")
            continue

        # type 校验
        if block.get("type") not in VALID_BLOCK_TYPES:
            errors.append(f"[ERROR] {path}.type 非法: {block.get('type')}")

    return errors


# ==================== 单文件处理 ====================


def check_meta_file(path: str):
    """
    校验单个 meta.json
    """
    global REPORT
    try:
        with open(path, "r", encoding="utf8") as f:
            meta = json.load(f)
    except Exception:
        print(f"[ERROR] 无法解析 JSON: {path}")
        return

    errors = []

    # ==================== 路径校验 ====================
    module, id_ = extract_module_and_id(os.path.dirname(path))

    if meta.get("module") != module:
        errors.append(f"[ERROR] module 不匹配: {meta.get('module')} != {module}")

    if meta.get("id") != id_:
        errors.append(f"[ERROR] id 不匹配: {meta.get('id')} != {id_}")

    # ==================== schema 校验 ====================
    errors.extend(check_schema(meta, META_SCHEMA))

    # ==================== contentBlocks 校验 ====================
    errors.extend(check_content_blocks(meta))

    # ==================== 输出 ====================
    if errors:
        # ===== 收集 JSON 报告 =====
        REPORT["summary"]["errorFiles"] += 1
        REPORT["summary"]["totalErrors"] += len(errors)

        REPORT["files"].append(
            {
                "path": path.replace(PROJECT_ROOT + os.sep, ""),
                "module": module,
                "id": id_,
                "errors": errors,
            }
        )
        # 控制台输出（保留）
        print(f"\n[{path}]")
        for e in errors:
            print(" ", e)


# ==================== 扫描 ====================


def scan_all():
    """
    扫描所有模块 & 结论
    """
    for module_dir in os.listdir(PROJECT_ROOT):
        # ✅ 只处理白名单模块（核心）
        if module_dir not in ALLOWED_MODULES:
            continue

        module_path = os.path.join(PROJECT_ROOT, module_dir)

        for sub_dir in os.listdir(module_path):
            if not is_conclusion_dir(sub_dir):
                continue

            conclusion_path = os.path.join(module_path, sub_dir)
            meta_path = os.path.join(conclusion_path, "meta.json")

            if os.path.exists(meta_path):
                REPORT["summary"]["totalFiles"] += 1
                check_meta_file(meta_path)
            else:
                REPORT["summary"]["totalFiles"] += 1

                REPORT["summary"]["errorFiles"] += 1
                REPORT["summary"]["totalErrors"] += 1

                REPORT["files"].append(
                    {
                        "path": meta_path.replace(PROJECT_ROOT + os.sep, ""),
                        "module": module_dir,
                        "id": sub_dir,
                        "errors": ["[MISSING FILE] meta.json 不存在"],
                    }
                )
                print(f"[MISSING FILE] {meta_path}")


# ==================== 主入口 ====================


def main():
    print("=" * 50)
    print("META JSON CHECK TOOL")
    print("=" * 50)

    scan_all()
    # ===== 输出 JSON 报告 =====
    report_path = os.path.join(PROJECT_ROOT, "meta_check_report.json")
    if REPORT["summary"]["errorFiles"] > 0:
        REPORT["summary"]["status"] = "FAIL"
    else:
        REPORT["summary"]["status"] = "PASS"
    REPORT["summary"]["generatedAt"] = datetime.datetime.now().isoformat()
    with open(report_path, "w", encoding="utf8") as f:
        json.dump(REPORT, f, indent=2, ensure_ascii=False)

    print("\n===== SUMMARY =====")
    print("Total Files:", REPORT["summary"]["totalFiles"])
    print("Error Files:", REPORT["summary"]["errorFiles"])
    print("Total Errors:", REPORT["summary"]["totalErrors"])
    print("status:", REPORT["summary"]["status"])
    print("generatedAt:", REPORT["summary"]["generatedAt"])

    print(f"\nJSON Report: {report_path}")
    print("\nDONE")


if __name__ == "__main__":
    main()
