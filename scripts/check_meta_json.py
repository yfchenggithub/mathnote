"""
===============================================================
Script Name : check_meta.py
Project     : 高中数学二级结论知识库 (Mathnote)

功能说明
---------------------------------------------------------------
检查整个项目中的 meta.json 文件是否存在结构或数据问题。

该脚本只进行检查，不会修改任何文件。

主要检查内容：

1. meta.json 是否为空文件
2. JSON 格式是否正确
3. 是否缺少 id 字段
4. 是否存在重复 id
5. 是否缺少 title
6. 是否缺少 keywords

使用方法
---------------------------------------------------------------
在项目根目录运行：

    check_meta.bat

或手动执行：

    py scripts/check_meta.py

脚本会扫描整个项目并输出检查结果。

设计思路
---------------------------------------------------------------
随着结论数量增加（目标 500+），meta.json 文件会越来越多。

常见问题：

    忘记填写 id
    title 为空
    keywords 未填写
    JSON 格式错误
    不小心复制导致 id 重复

这些问题如果不及时发现，会导致：

    搜索索引生成失败
    小程序搜索异常
    数据结构混乱

因此需要一个自动检测工具。

处理逻辑
---------------------------------------------------------------
1. 扫描整个项目目录
2. 查找所有 meta.json
3. 对每个文件执行：

   - 判断是否为空文件
   - 尝试解析 JSON
   - 检查 id 是否存在
   - 检查 id 是否重复
   - 检查 title
   - 检查 keywords

4. 输出问题报告

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

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

ids = set()
duplicate_ids = set()

total_files = 0


def check_meta(path):

    global total_files

    total_files += 1

    # 空文件
    if os.path.getsize(path) == 0:
        print("ERROR (empty meta):", path)
        return

    try:
        with open(path, "r", encoding="utf8") as f:
            meta = json.load(f)

    except json.JSONDecodeError:
        print("ERROR (invalid json):", path)
        return

    # ID检查
    if "id" not in meta or not meta["id"]:
        print("ERROR (missing id):", path)
    else:

        id_value = meta["id"]

        if id_value in ids:
            duplicate_ids.add(id_value)
            print("ERROR (duplicate id):", id_value, path)

        ids.add(id_value)

    # title
    if "title" not in meta or meta["title"] == "":
        print("WARNING (missing title):", path)

    # keywords
    if "keywords" not in meta or len(meta["keywords"]) == 0:
        print("WARNING (missing keywords):", path)


def main():

    print("Checking project:", PROJECT_ROOT)
    print()

    for root, dirs, files in os.walk(PROJECT_ROOT):

        if "meta.json" in files:

            path = os.path.join(root, "meta.json")
            check_meta(path)

    print()
    print("Total meta files:", total_files)

    if duplicate_ids:
        print("Duplicate IDs:", duplicate_ids)


if __name__ == "__main__":
    main()