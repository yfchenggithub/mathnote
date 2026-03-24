"""
===============================================================
Script Name : upgrade_meta.py
Project     : 高中数学二级结论知识库 (Mathnote)

功能说明
---------------------------------------------------------------
批量升级项目中的 meta.json 文件，使其结构与 meta_schema.json 保持一致。

主要功能：
1. 自动扫描整个项目目录中的所有 meta.json
2. 根据 meta_schema.json 自动补充缺失字段
3. 自动删除 schema 中不存在的字段（保持结构统一）
4. 跳过空文件和 JSON 格式错误文件
5. 输出更新日志和统计信息

使用方法
---------------------------------------------------------------
在项目根目录运行：

    upgrade_meta.bat

或手动执行：

    py scripts/upgrade_meta.py

脚本会自动：

    读取 scripts/meta_schema.json
    扫描整个项目目录
    更新所有 meta.json

设计思路
---------------------------------------------------------------
随着二级结论数量不断增加（目标 500+），meta.json 的结构可能会
不断新增字段或删除字段。

如果手动维护每个 meta.json：

    成本极高
    容易遗漏
    数据结构不统一

因此引入 schema 机制：

    meta_schema.json = 数据结构标准

脚本通过：

    merge_schema()

自动补充字段

通过：

    remove_extra_fields()

删除废弃字段

保证整个项目的 meta.json 结构始终统一。

处理逻辑
---------------------------------------------------------------
1. 读取 meta_schema.json
2. 遍历项目目录
3. 找到所有 meta.json
4. 对每个 meta.json 执行：

   - 判断文件是否为空
   - 判断 JSON 是否合法
   - 自动补充 schema 新字段
   - 删除 schema 中不存在字段
   - 写回文件

作者
---------------------------------------------------------------
Author : 程远锋
Role   : 程序员 / 高中数学教师

创建时间
---------------------------------------------------------------
Created : 2026
===============================================================
"""
import json
import os
import copy

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(SCRIPT_DIR, "meta_schema.json")
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

total_files = 0
updated_files = 0


def merge_schema(meta, schema):
    """
    根据schema补充字段
    """
    changed = False

    for key, value in schema.items():

        if key not in meta:
            meta[key] = copy.deepcopy(value)
            changed = True

        elif isinstance(value, dict) and isinstance(meta[key], dict):
            sub_changed = merge_schema(meta[key], value)
            if sub_changed:
                changed = True

    return changed


def remove_extra_fields(meta, schema):
    """
    删除schema中不存在的字段
    """
    changed = False

    keys = list(meta.keys())

    for key in keys:

        if key not in schema:
            del meta[key]
            changed = True

        elif isinstance(meta[key], dict) and isinstance(schema[key], dict):
            sub_changed = remove_extra_fields(meta[key], schema[key])
            if sub_changed:
                changed = True

    return changed


def process_meta(path, schema):

    global updated_files

    # 空文件
    if os.path.getsize(path) == 0:
        print("SKIP (empty file):", path)
        return

    try:
        with open(path, "r", encoding="utf8") as f:
            meta = json.load(f)

    except json.JSONDecodeError:
        print("SKIP (invalid json):", path)
        return

    # ID 检查
    if "id" not in meta or meta["id"] == "":
        print("WARNING (missing id):", path)

    changed1 = merge_schema(meta, schema)
    changed2 = remove_extra_fields(meta, schema)

    if changed1 or changed2:

        with open(path, "w", encoding="utf8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        print("UPDATED:", path)
        updated_files += 1


def main():

    global total_files

    with open(SCHEMA_PATH, "r", encoding="utf8") as f:
        schema = json.load(f)

    print("Schema:", SCHEMA_PATH)
    print("Project:", PROJECT_ROOT)
    print()

    for root, dirs, files in os.walk(PROJECT_ROOT):

        if "meta.json" in files:

            total_files += 1

            path = os.path.join(root, "meta.json")
            process_meta(path, schema)

    print()
    print("Total meta files:", total_files)
    print("Updated files:", updated_files)


if __name__ == "__main__":
    main()