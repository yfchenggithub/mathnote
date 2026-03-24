"""
========================================================
🚀 build_content_json.py（内容构建器 - 最终版）
========================================================

【核心目标】

从 LaTeX 文件结构生成小程序可用的 JSON 数据：

D:\\mathnote
    ↓
content/*.json

--------------------------------------------------------
【支持能力】

✔ 指定模块生成（重点）
✔ 自动解析 meta.json
✔ 自动读取 6 个 tex 内容
✔ 输出标准 JSON 结构

--------------------------------------------------------
【为什么必须做这一步？】

👉 小程序不能解析 tex
👉 必须在构建阶段转为 JSON
👉 保证搜索引擎直接使用

========================================================
"""

import os
import json

# ======================================================
# 🔥 配置区（你只需要改这里）
# ======================================================

ROOT_DIR = r"D:\mathnote"

# ✅ 控制生成哪些模块（核心）
TARGET_MODULES = [
    "07-inequality",
    # "03-vector",
    # "04-trigonometry",
]

OUTPUT_DIR = os.path.join(ROOT_DIR, "data", "content")


# ======================================================
# 工具函数
# ======================================================

def read_tex(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except:
        return ""


def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


# ======================================================
# 处理单个结论
# ======================================================

def process_conclusion(conclusion_path):

    meta_path = os.path.join(conclusion_path, "meta.json")
    meta = read_json(meta_path)

    cid = meta.get("id")
    if not cid:
        print("missing id:", conclusion_path)
        return None

    data = {
        "id": cid,
        "title": meta.get("title", ""),
        "tags": meta.get("tags", []),
        "score": meta.get("score", 0),

        # 内容
        "statement": read_tex(os.path.join(conclusion_path, "01-statement.tex")),
        "explanation": read_tex(os.path.join(conclusion_path, "02-explanation.tex")),
        "proof": read_tex(os.path.join(conclusion_path, "03-proof.tex")),
        "examples": read_tex(os.path.join(conclusion_path, "04-examples.tex")),
        "traps": read_tex(os.path.join(conclusion_path, "05-traps.tex")),
        "summary": read_tex(os.path.join(conclusion_path, "06-summary.tex")),
    }

    return cid, data


# ======================================================
# 处理模块
# ======================================================

def process_module(module_name):

    module_path = os.path.join(ROOT_DIR, module_name)

    if not os.path.exists(module_path):
        print("module not found:", module_name)
        return

    result = {}

    for item in os.listdir(module_path):

        conclusion_path = os.path.join(module_path, item)

        if not os.path.isdir(conclusion_path):
            continue

        res = process_conclusion(conclusion_path)

        if res:
            cid, data = res
            result[cid] = data

    # 输出文件名（去掉前缀）
    name = module_name.split("-")[-1]
    output_file = os.path.join(OUTPUT_DIR, f"{name}.json")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    print(f"Generated: {output_file}  ({len(result)} items)")


# ======================================================
# 主程序
# ======================================================

def main():

    print("====================================")
    print("Building content JSON")
    print("====================================")

    for module in TARGET_MODULES:
        process_module(module)

    print("====================================")
    print("DONE")
    print("====================================")


if __name__ == "__main__":
    main()