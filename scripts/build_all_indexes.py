"""
====================================================================
Script Name : build_all_indexes.py
Project     : Mathnote 高中数学二级结论搜索引擎
Author      : 程远锋
Created     : 2026

====================================================================
一、项目背景
====================================================================

本项目用于构建"高中数学二级结论搜索引擎"的离线索引。

由于微信小程序运行环境存在以下限制：

1）JSON 解析速度有限
2）JS 遍历大量对象性能下降
3）包体大小有限
4）网络请求不稳定

因此必须在 **构建阶段（Build Time）** 完成大部分计算，
生成适合小程序端直接使用的索引。

最终目标：

    小程序端搜索延迟 < 3ms

====================================================================
二、系统架构
====================================================================

            meta.json
               │
               ▼
        build_all_indexes.py
               │
               ▼
        search_engine/*.json
               │
               ▼
        微信小程序加载 JSON
               │
               ▼
           毫秒级搜索

====================================================================
三、生成索引文件
====================================================================

search_engine/

keyword_index.json
    关键词 → 结论ID列表

prefix_index.json
    前缀 → 关键词列表

pinyin_index.json
    拼音 → 结论ID列表

pinyin_short_index.json
    拼音首字母 → 结论ID列表

formula_index.json
    数学表达式 → 结论ID列表

ranking_index.json
    结论ID → 排序权重

meta_compact.json
    结论ID → 精简信息

suggestion_index.json
    自动补全词库

====================================================================
四、设计原则
====================================================================

1 轻量 JSON
避免大型嵌套结构

2 两级索引
prefix → keyword → cid

3 构建阶段完成复杂计算

4 拼音搜索支持

5 数学表达式搜索支持

====================================================================
五、数学表达式搜索
====================================================================

支持用户输入：

    ab+bc+ca
    a^2+b^2+c^2
    sin2x
    |AB|^2

搜索对应结论。

实现方式：

在构建阶段：

1 提取 meta.json 中 formula 字段
2 进行表达式标准化
3 建立 formula_index

====================================================================
"""

import os
import json
import shutil
import re
from collections import defaultdict

# ------------------------------------------------------------
# 依赖检测
# ------------------------------------------------------------

try:
    from pypinyin import lazy_pinyin
except ImportError:
    raise RuntimeError(
        "Missing dependency: pypinyin\n"
        "Please run: pip install pypinyin"
    )

# ------------------------------------------------------------
# 路径配置
# ------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "search_engine")

# ------------------------------------------------------------
# 清理旧索引
# ------------------------------------------------------------

def prepare_output():

    try:

        if os.path.exists(OUTPUT_DIR):

            print("Removing old search_engine directory...")

            shutil.rmtree(OUTPUT_DIR)

        os.makedirs(OUTPUT_DIR)

    except Exception as e:

        print("Failed to prepare output directory")

        raise e


# ------------------------------------------------------------
# 索引结构
# ------------------------------------------------------------

keyword_index = defaultdict(set)
prefix_index = defaultdict(set)

pinyin_index = defaultdict(set)
pinyin_short_index = defaultdict(set)

formula_index = defaultdict(set)

ranking_index = {}

meta_compact = {}

suggestions = set()


# ------------------------------------------------------------
# 拼音
# ------------------------------------------------------------

def get_pinyin(word):

    try:

        return "".join(lazy_pinyin(word))

    except Exception:

        return word


def get_pinyin_short(word):

    try:

        return "".join([p[0] for p in lazy_pinyin(word)])

    except Exception:

        return word


# ------------------------------------------------------------
# 中文拆词
# ------------------------------------------------------------

def split_words(text):

    words = []

    length = len(text)

    for i in range(length):

        for j in range(i + 2, min(i + 6, length) + 1):

            words.append(text[i:j])

    return words


# ------------------------------------------------------------
# 数学表达式标准化
# ------------------------------------------------------------

def normalize_formula(formula):

    if not formula:

        return None

    formula = formula.lower()

    formula = formula.replace(" ", "")

    formula = formula.replace("²", "^2")

    formula = formula.replace("³", "^3")

    return formula


# ------------------------------------------------------------
# 加入关键词索引
# ------------------------------------------------------------

def add_keyword(word, cid):

    word = word.strip()

    if not word:

        return

    keyword_index[word].add(cid)

    suggestions.add(word)

    # prefix

    for i in range(1, len(word) + 1):

        prefix = word[:i]

        prefix_index[prefix].add(word)

    # pinyin

    py = get_pinyin(word)

    pinyin_index[py].add(cid)

    short = get_pinyin_short(word)

    pinyin_short_index[short].add(cid)


# ------------------------------------------------------------
# 加入公式索引
# ------------------------------------------------------------

def add_formula(formula, cid):

    f = normalize_formula(formula)

    if not f:

        return

    formula_index[f].add(cid)


# ------------------------------------------------------------
# 处理 meta.json
# ------------------------------------------------------------

def process_meta(path):

    try:

        with open(path, "r", encoding="utf8") as f:

            meta = json.load(f)

    except Exception:

        print("Invalid JSON:", path)

        return

    cid = meta.get("id")

    if not cid:

        print("Missing id:", path)

        return

    if cid in meta_compact:

        print("Duplicate id:", cid)

        return

    title = meta.get("title", "")

    summary = meta.get("summary", "")

    keywords = meta.get("keywords", [])

    synonyms = meta.get("synonyms", [])

    formulas = meta.get("formulas", [])

    score = meta.get("score", 0)

    # compact meta

    meta_compact[cid] = {

        "title": title,

        "summary": summary

    }

    ranking_index[cid] = score

    # 关键词集合

    words = []

    words += keywords

    words += synonyms

    words += split_words(title)

    for w in words:

        add_keyword(w, cid)

    # 数学公式

    for f in formulas:

        add_formula(f, cid)


# ------------------------------------------------------------
# 扫描 meta.json
# ------------------------------------------------------------

def scan_meta():

    total = 0

    for root, dirs, files in os.walk(PROJECT_ROOT):

        if "search_engine" in root:

            continue

        if "meta.json" in files:

            path = os.path.join(root, "meta.json")

            process_meta(path)

            total += 1

    print("Total meta scanned:", total)


# ------------------------------------------------------------
# 保存 JSON
# ------------------------------------------------------------

def save_json(name, data):

    try:

        path = os.path.join(OUTPUT_DIR, name)

        with open(path, "w", encoding="utf8") as f:

            json.dump(data, f, ensure_ascii=False)

        print("Generated:", name)

    except Exception as e:

        print("Failed to save", name)

        raise e


# ------------------------------------------------------------
# 主程序
# ------------------------------------------------------------

def main():

    print()
    print("====================================")
    print("Building Mathnote Search Engine")
    print("====================================")

    prepare_output()

    scan_meta()

    print()

    save_json(
        "keyword_index.json",
        {k: list(v) for k, v in keyword_index.items()}
    )

    save_json(
        "prefix_index.json",
        {k: list(v) for k, v in prefix_index.items()}
    )

    save_json(
        "pinyin_index.json",
        {k: list(v) for k, v in pinyin_index.items()}
    )

    save_json(
        "pinyin_short_index.json",
        {k: list(v) for k, v in pinyin_short_index.items()}
    )

    save_json(
        "formula_index.json",
        {k: list(v) for k, v in formula_index.items()}
    )

    save_json("ranking_index.json", ranking_index)

    save_json("meta_compact.json", meta_compact)

    save_json("suggestion_index.json", sorted(list(suggestions)))

    print()
    print("====================================")
    print("Build Statistics")
    print("====================================")

    print("Total conclusions:", len(meta_compact))
    print("Keyword index:", len(keyword_index))
    print("Prefix index:", len(prefix_index))
    print("Formula index:", len(formula_index))
    print("Suggestion size:", len(suggestions))

    print()
    print("Search engine build complete.")
    print()


if __name__ == "__main__":

    main()