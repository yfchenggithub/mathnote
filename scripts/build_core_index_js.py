"""
========================================================
🚀 build_core_index_js.py（小程序 JS 输出终极版）
========================================================

【核心目标】

将 meta.json → 构建为：

✅ core_index.js     （搜索核心）
✅ rank_index.js     （排序权重）
✅ suggest_index.js  （自动补全）

--------------------------------------------------------
【为什么必须输出 JS 而不是 JSON？】

❌ 微信小程序不支持直接 import JSON
❌ require JSON 会报错 / 不稳定
❌ resolveJsonModule 不可用

✅ JS 模块 = 唯一稳定方案

--------------------------------------------------------
【核心设计（极致搜索架构）】

👉 一个核心索引：

core_index:
    任意词 → [cid, cid, cid...]

支持：

✔ 中文关键词
✔ 拼音（quanpin）
✔ 拼音首字母（缩写）
✔ 前缀匹配（极致补全）
✔ 标题拆词（模糊搜索）
✔ 同义词
✔ 公式

--------------------------------------------------------
【模块控制（重要）】

你可以只生成某些模块：

ENABLED_MODULES = [
    "inequality",
    "vector",
]

👉 自动只扫描这些目录

--------------------------------------------------------
【项目结构要求】

D:/mathnote/
    inequality/
        I01-xxx/
            meta.json
    vector/
        V01-xxx/
            meta.json

--------------------------------------------------------
【输出位置】

miniprogram/data/index_js/

--------------------------------------------------------
"""

import os
import json
import shutil
from collections import defaultdict
from pypinyin import lazy_pinyin

# ========================================================
# 🔧 可配置区域（你只需要改这里）
# ========================================================

# 根目录
ROOT_DIR = r"D:\mathnote"

# 输出目录（小程序用）
OUTPUT_DIR = r"D:\mathnote\search_engine"

# 启用模块（只生成这些）
ENABLED_MODULES = [
    "07-inequality",
    # "vector",
    # "triangle",
]

# 是否压缩 JSON（建议开启）
MINIFY = True


# ========================================================
# 初始化
# ========================================================

core_index = defaultdict(set)
rank_index = {}
suggest_set = set()


# ========================================================
# 拼音工具
# ========================================================

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


# ========================================================
# 前缀（核心性能点）
# ========================================================

def add_prefix(word, cid):
    """
    输入：极值
    输出：
        极
        极值
    """
    for i in range(1, len(word) + 1):
        prefix = word[:i]
        core_index[prefix].add(cid)


# ========================================================
# 核心：加入词
# ========================================================

def add_word(word, cid):

    if not word:
        return

    word = word.strip().lower()

    if not word:
        return

    # 1️⃣ 原词
    core_index[word].add(cid)

    # 2️⃣ 前缀
    add_prefix(word, cid)

    # 3️⃣ 拼音
    py = get_pinyin(word)
    core_index[py].add(cid)

    # 4️⃣ 拼音缩写
    short = get_pinyin_short(word)
    core_index[short].add(cid)

    # 5️⃣ suggest
    suggest_set.add(word)


# ========================================================
# 公式处理
# ========================================================

def normalize_formula(f):

    if not f:
        return None

    f = f.lower()
    f = f.replace(" ", "")
    f = f.replace("²", "^2")
    f = f.replace("³", "^3")

    return f


# ========================================================
# 处理 meta.json
# ========================================================

def process_meta(meta_path):

    try:
        with open(meta_path, "r", encoding="utf8") as f:
            meta = json.load(f)
    except Exception as e:
        print("JSON错误:", meta_path, e)
        return

    cid = meta.get("id")
    if not cid:
        return

    # 排序权重
    rank_index[cid] = meta.get("score", 0)

    words = []

    # 关键词
    words += meta.get("keywords", [])
    words += meta.get("synonyms", [])
    words += meta.get("tags", [])

    # 标题拆词（非常关键）
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


# ========================================================
# 扫描模块
# ========================================================

def scan():

    total = 0

    for module in ENABLED_MODULES:

        module_path = os.path.join(ROOT_DIR, module)

        if not os.path.exists(module_path):
            print("模块不存在:", module)
            continue

        print(f"扫描模块: {module}")

        for root, dirs, files in os.walk(module_path):

            if "meta.json" in files:
                process_meta(os.path.join(root, "meta.json"))
                total += 1

    print("总 meta 数量:", total)


# ========================================================
# 输出 JS 模块
# ========================================================

def write_js(name, data, var_name):

    path = os.path.join(OUTPUT_DIR, name)

    try:
        with open(path, "w", encoding="utf8") as f:

            f.write("// Auto-generated file. DO NOT EDIT\n\n")

            f.write(f"const {var_name} = ")

            if MINIFY:
                json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            else:
                json_str = json.dumps(data, ensure_ascii=False, indent=2)

            f.write(json_str)

            f.write("\n\nmodule.exports = " + var_name + ";")

        print("已生成:", name)

    except Exception as e:
        print("写入失败:", name, e)


# ========================================================
# 主函数
# ========================================================

def main():

    # 清空旧目录
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("开始构建索引...")

    scan()

    print("写入 JS...")

    write_js(
        "core_index.js",
        {k: list(v) for k, v in core_index.items()},
        "coreIndex"
    )

    write_js(
        "rank_index.js",
        rank_index,
        "rankIndex"
    )

    write_js(
        "suggest_index.js",
        sorted(list(suggest_set)),
        "suggestIndex"
    )

    print("====================================")
    print("core_index:", len(core_index))
    print("suggest:", len(suggest_set))
    print("====================================")
    print("构建完成")


if __name__ == "__main__":
    main()