"""
========================================================
🚀 build_core_index.py（重构版 - 基于 build_all_indexes.py）
========================================================

【核心目标】

在保留现有 meta.json 数据结构的前提下：

❌ 删除多索引结构（keyword/prefix/pinyin 等）
✅ 合并为一个 core_index（极致搜索）

--------------------------------------------------------
【为什么重构？】

原方案（你当前）：

keyword_index
prefix_index
pinyin_index
pinyin_short_index
formula_index
...

👉 问题：

1）小程序端需要多次查表（慢）
2）JSON 文件过多（加载慢）
3）逻辑分散（不可维护）

--------------------------------------------------------
【新方案】

👉 所有索引统一为：

core_index:
    任意词 → 结论ID列表

--------------------------------------------------------
【支持能力】

✔ 中文关键词
✔ 拼音
✔ 拼音首字母
✔ 前缀匹配
✔ 同义词
✔ 标题拆词
✔ 数学公式（统一处理）

========================================================
"""

from build_search_bundle_js import main as _bundle_main

if __name__ == "__main__":
    raise SystemExit(_bundle_main())

import os
import json
import shutil
from collections import defaultdict

from pypinyin import lazy_pinyin

# ------------------------------------------------------------
# 路径（沿用你的项目结构）
# ------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "search_engine")


# ------------------------------------------------------------
# 初始化
# ------------------------------------------------------------

core_index = defaultdict(set)
rank_index = {}
suggest_set = set()


# ------------------------------------------------------------
# 拼音
# ------------------------------------------------------------

def get_pinyin(word):
    try:
        return "".join(lazy_pinyin(word))
    except:
        return word


def get_pinyin_short(word):
    try:
        return "".join([p[0] for p in lazy_pinyin(word)])
    except:
        return word


# ------------------------------------------------------------
# 前缀拆分（核心能力）
# ------------------------------------------------------------

def add_prefix(word, cid):
    for i in range(1, len(word) + 1):
        prefix = word[:i]
        core_index[prefix].add(cid)


# ------------------------------------------------------------
# 加入词
# ------------------------------------------------------------

def add_word(word, cid):
    if not word:
        return

    word = word.strip().lower()

    if not word:
        return

    # 原词
    core_index[word].add(cid)

    # 前缀
    add_prefix(word, cid)

    # 拼音
    py = get_pinyin(word)
    core_index[py].add(cid)

    # 拼音首字母
    short = get_pinyin_short(word)
    core_index[short].add(cid)

    # suggest
    suggest_set.add(word)


# ------------------------------------------------------------
# 公式标准化
# ------------------------------------------------------------

def normalize_formula(f):
    if not f:
        return None

    f = f.lower()
    f = f.replace(" ", "")
    f = f.replace("²", "^2")
    f = f.replace("³", "^3")

    return f


# ------------------------------------------------------------
# 处理 meta.json（核心复用你的逻辑）
# ------------------------------------------------------------

def process_meta(path):

    try:
        with open(path, "r", encoding="utf8") as f:
            meta = json.load(f)
    except:
        print("Invalid JSON:", path)
        return

    cid = meta.get("id")
    if not cid:
        return

    # 排序权重
    score = meta.get("score", 0)
    rank_index[cid] = score

    # 收集词
    words = []

    words += meta.get("keywords", [])
    words += meta.get("synonyms", [])
    words += meta.get("tags", [])

    # 标题拆词（关键优化）
    title = meta.get("title", "")
    for i in range(len(title)):
        for j in range(i + 2, min(i + 6, len(title)) + 1):
            words.append(title[i:j])

    # 写入索引
    for w in words:
        add_word(w, cid)

    # 公式
    for f in meta.get("formulas", []):
        f = normalize_formula(f)
        if f:
            add_word(f, cid)


# ------------------------------------------------------------
# 扫描（完全复用你结构）
# ------------------------------------------------------------

def scan_meta():

    total = 0

    for root, dirs, files in os.walk(PROJECT_ROOT):

        if "search_engine" in root:
            continue

        if "meta.json" in files:
            process_meta(os.path.join(root, "meta.json"))
            total += 1

    print("Total meta:", total)


# ------------------------------------------------------------
# 输出
# ------------------------------------------------------------

def save_json(name, data):
    path = os.path.join(OUTPUT_DIR, name)
    with open(path, "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False)


# ------------------------------------------------------------
# 主函数
# ------------------------------------------------------------

def main():

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    os.makedirs(OUTPUT_DIR)

    print("Building CORE index...")

    scan_meta()

    print("Saving...")

    save_json("core_index.json", {k: list(v) for k, v in core_index.items()})
    save_json("rank_index.json", rank_index)
    save_json("suggest_index.json", sorted(list(suggest_set)))

    print("====================================")
    print("Core index size:", len(core_index))
    print("Suggest size:", len(suggest_set))
    print("====================================")
    print("Done")


if __name__ == "__main__":
    main()
