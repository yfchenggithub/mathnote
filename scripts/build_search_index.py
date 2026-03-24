"""
===============================================================
Script Name : build_search_index.py
Project     : 高中数学二级结论知识库 (Mathnote)

功能说明
---------------------------------------------------------------
从项目中的所有 meta.json 文件生成搜索索引 search_index.json。

该索引用于微信小程序实现"极速搜索"，避免每次搜索都遍历
全部 meta.json 文件。

索引结构：

    keyword -> [结论ID]

例如：

{
  "连不等式": ["I01"],
  "夹逼": ["I01"],
  "数量积": ["V03","V05"]
}

搜索时只需要：

    index[keyword]

即可快速得到对应结论。

主要索引来源字段：

    title
    keywords
    synonyms
    searchBoost

使用方法
---------------------------------------------------------------

在项目根目录运行：

    build_search_index.bat

或手动运行：

    py scripts/build_search_index.py

生成文件：

    search_index.json

设计思路
---------------------------------------------------------------

随着结论数量增加（目标 500+），如果每次搜索都遍历所有
meta.json，性能会明显下降。

因此提前生成倒排索引：

    keyword -> id list

搜索复杂度从：

    O(N)

降低到：

    O(1)

极大提升小程序搜索体验。

异常处理
---------------------------------------------------------------

脚本会自动处理：

    空 meta.json
    JSON 格式错误
    缺少 id
    缺少关键词

并输出警告信息。

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
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

OUTPUT_FILE = os.path.join(PROJECT_ROOT, "search_index.json")

index = defaultdict(set)

total_meta = 0
total_keywords = 0


def add_word(word, cid):

    global total_keywords

    if not word:
        return

    word = word.strip()

    if word == "":
        return

    index[word].add(cid)
    total_keywords += 1


def process_meta(path):

    global total_meta

    total_meta += 1

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

    cid = meta.get("id")

    if not cid:
        print("WARNING (missing id):", path)
        return

    words = []

    words.append(meta.get("title", ""))

    words += meta.get("keywords", [])
    words += meta.get("synonyms", [])
    words += meta.get("searchBoost", [])

    for w in words:
        add_word(w, cid)


def main():

    print("Building search index...")
    print("Project:", PROJECT_ROOT)
    print()

    for root, dirs, files in os.walk(PROJECT_ROOT):

        if "meta.json" in files:

            path = os.path.join(root, "meta.json")
            process_meta(path)

    result = {k: list(v) for k, v in index.items()}

    with open(OUTPUT_FILE, "w", encoding="utf8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print()
    print("Search index generated:", OUTPUT_FILE)
    print("Meta files scanned:", total_meta)
    print("Total keywords:", len(result))


if __name__ == "__main__":
    main()