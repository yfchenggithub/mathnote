"""
12_pipeline/run_pipeline.py

功能介绍
--------
该脚本负责把 `input/` 目录中的 LaTeX 文本输入批量加工为 5 个阶段的结构化结果：
- L1: raw 文本清洗与结构提取 -> output/<ID>/raw_l1.json
- L2: 结论重构 -> output/<ID>/statement_l2.json
- L3: 教学价值评估 -> output/<ID>/eval_l3.json
- L4: 讲义模块生成 -> output/<ID>/lecture_l4.json
- L5: 检索与推荐 meta 生成 -> output/<ID>/meta_l5.json
- 讲义片段导出 -> output/<ID>/01_statement.tex ~ 06_summary.tex

流程介绍
--------
1. 扫描输入目录，读取 .tex/.txt/.md/.latex/.json 文件。
2. 每个文件按 L1 -> L5 依次执行；若某阶段输出已存在则自动复用。
3. 所有阶段调用统一的 LLM 接口，并带有重试与并发控制。
4. 批处理结束后输出 success/error/skipped 统计。

脚本用法
--------
1) 默认使用配置文件中的路径与并发:
   python run_pipeline.py

2) 指定输入/输出目录与并发:
   python run_pipeline.py --input-dir ./input --output-dir ./output --max-workers 3

3) 指定扩展名与单文件超时:
   python run_pipeline.py --extensions .txt .tex .json --timeout 120
"""

import argparse
import json
import logging
import os
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
from datetime import date
from threading import Semaphore
from typing import Any, Callable

from openai import OpenAI
from tqdm import tqdm

from config.config_loader import (
    get_api_config,
    get_model_config,
    get_paths,
    get_performance,
)
from utils.prompt_loader import load_prompt

# =========================
# 基础常量与日志
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "pipeline.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

# 额外 API 并发闸门，防止瞬时请求过高造成限流。
semaphore = Semaphore(3)

# =========================
# 配置加载
# =========================

api_config = get_api_config()
model_config = get_model_config()
paths = get_paths()
perf = get_performance()

TEMPERATURE = perf["temperature"]
MAX_WORKERS = perf["max_workers"]
RETRY_TIMES = perf["retry_times"]

INPUT_DIR = os.path.join(BASE_DIR, paths["input_dir"])
OUTPUT_DIR = os.path.join(BASE_DIR, paths["output_dir"])

DEFAULT_TIMEOUT_SECONDS = 60
DEFAULT_INPUT_EXTENSIONS = (".tex", ".txt", ".md", ".latex", ".json")
L5_MAX_TEXT_CHARS = 2400

STEP_SUCCESS_STATUS = ("success", None)
NON_RETRY_ERROR_CODES = {
    "invalid_api_key",
    "model_not_found",
    "insufficient_quota",
}

# Pipeline 阶段到模型类型的映射（具体模型名在 app_config.json 中配置）。
MODEL_MAP = {
    "l1": "default",
    "l2": "reasoning",
    "l3": "default",
    # L4 生成内容较长，优先使用 chat 模型以降低延迟。
    "l4": "default",
    "l5": "default",
}

META_DEFAULT_SEARCHMETA = {
    "titleWeight": 10,
    "keywordWeight": 8,
    "synonymWeight": 6,
    "formulaWeight": 7,
}

LECTURE_TEX_FILE_MAP = {
    "01_statement": "01_statement.tex",
    "02_explanation": "02_explanation.tex",
    "03_proof": "03_proof.tex",
    "04_examples": "04_examples.tex",
    "05_traps": "05_traps.tex",
    "06_summary": "06_summary.tex",
}


def parse_args() -> argparse.Namespace:
    """
    解析命令行参数。

    Returns:
        argparse.Namespace: 运行参数集合。
    """
    parser = argparse.ArgumentParser(
        description="批量运行 LaTeX -> statement/eval/lecture/meta 的五阶段流水线。",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--input-dir",
        default=INPUT_DIR,
        help=f"输入目录（默认: {INPUT_DIR}）",
    )
    parser.add_argument(
        "--output-dir",
        default=OUTPUT_DIR,
        help=f"输出目录（默认: {OUTPUT_DIR}）",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=MAX_WORKERS,
        help=f"批处理并发数（默认: {MAX_WORKERS}）",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"单文件 future.result 超时秒数（默认: {DEFAULT_TIMEOUT_SECONDS}）",
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=list(DEFAULT_INPUT_EXTENSIONS),
        help=(
            "输入文件扩展名列表（空格分隔）。\n"
            "示例: --extensions .txt .tex .json"
        ),
    )
    return parser.parse_args()


def normalize_extensions(extensions: list[str]) -> tuple[str, ...]:
    """
    标准化扩展名为小写且以点号开头。

    Args:
        extensions: 原始扩展名列表。

    Returns:
        tuple[str, ...]: 可用于 endswith 的标准扩展名元组。
    """
    normalized = []
    for ext in extensions:
        ext = ext.strip().lower()
        if not ext:
            continue
        if not ext.startswith("."):
            ext = f".{ext}"
        normalized.append(ext)

    # 去重并保持顺序
    unique = list(dict.fromkeys(normalized))
    return tuple(unique)


def retry_call(
    func: Callable[..., Any],
    *args: Any,
    retries: int = 3,
    delay: float = 1,
    **kwargs: Any,
) -> Any:
    """
    通用重试封装，采用指数退避。

    Args:
        func: 待执行函数。
        *args: 位置参数。
        retries: 最大重试次数。
        delay: 初始重试延迟秒数。
        **kwargs: 关键字参数。

    Returns:
        Any: 函数返回值。

    Raises:
        Exception: 达到最大重试次数后，抛出最后一次异常。
    """
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_code = getattr(e, "code", None)
            if error_code in NON_RETRY_ERROR_CODES:
                raise
            if attempt == retries - 1:
                raise

            sleep_time = delay * (2**attempt) + random.random()
            logging.info(f"⚠️ Retry {attempt + 1}/{retries} after {sleep_time:.2f}s")
            time.sleep(sleep_time)


def get_model(step: str = "default") -> str:
    """
    根据阶段名返回模型名。

    Args:
        step: pipeline 阶段（l1/l2/l3/l4/l5）。

    Returns:
        str: 模型名称。
    """
    model_type = MODEL_MAP.get(step, "default")
    return model_config[model_type]


def call_llm(prompt: str, step: str = "default") -> str:
    """
    调用 LLM，返回纯文本响应。

    Args:
        prompt: 已渲染好的提示词。
        step: 当前阶段，用于动态选择模型。

    Returns:
        str: LLM 返回文本。
    """
    with semaphore:
        model = get_model(step)
        messages = [{"role": "user", "content": prompt}]

        def _request() -> Any:
            local_client = OpenAI(
                api_key=api_config["api_key"],
                base_url=api_config["base_url"],
            )
            return local_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=TEMPERATURE,
            )

        response = retry_call(_request, retries=RETRY_TIMES)
        return response.choices[0].message.content


def render_prompt(step: str, input_data: Any) -> str:
    """
    将输入数据注入到 prompt 模板中。

    优先替换 `{{input}}` 占位符；若模板未使用占位符，则在末尾附加输入数据。

    Args:
        step: 阶段名（l1~l5）。
        input_data: 注入数据（字符串或可 JSON 序列化对象）。

    Returns:
        str: 渲染后的 prompt。
    """
    template = load_prompt(step)

    if isinstance(input_data, str):
        payload = input_data
    else:
        payload = json.dumps(input_data, ensure_ascii=False, indent=2)

    if "{{input}}" in template:
        return template.replace("{{input}}", payload)
    return f"{template}\n\n【输入数据】\n{payload}"


def save_json(data: dict[str, Any], path: str) -> None:
    """
    保存 JSON 文件并自动创建目录。

    Args:
        data: 待保存的数据。
        path: 目标路径。
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json_file(path: str) -> dict[str, Any]:
    """
    读取 JSON 文件，自动兼容 UTF-8 BOM。

    Args:
        path: JSON 文件路径。

    Returns:
        dict[str, Any]: 解析后的对象。

    Raises:
        ValueError: 内容不是 JSON 对象。
        Exception: 文件读取/解析失败时抛出最后一次异常。
    """
    last_error: Exception | None = None
    for encoding in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            with open(path, "r", encoding=encoding) as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError(f"{path} 不是 JSON 对象")
            return data
        except Exception as e:
            last_error = e
    raise last_error if last_error else ValueError(f"读取 JSON 失败: {path}")


def safe_json_parse(text: str | None) -> dict[str, Any]:
    """
    尽量从 LLM 文本中提取 JSON。

    支持场景:
    - 纯 JSON
    - ```json 代码块包裹
    - 文本中夹带一个 JSON 对象

    Args:
        text: LLM 原始输出。

    Returns:
        dict[str, Any]: 解析后的 JSON；失败时返回 parse_error 结构。
    """
    if not text:
        return {"status": "empty_response"}

    clean_text = text.replace("```json", "").replace("```", "").strip()
    json_candidate = extract_first_json_object(clean_text) or clean_text

    try:
        parsed = json.loads(json_candidate)
        return normalize_control_chars(parsed)
    except Exception as e:
        # 常见失败场景：LaTeX 反斜杠未转义，导致 Invalid \escape
        repaired = repair_invalid_json_escapes(json_candidate)
        repaired = remove_trailing_commas(repaired)
        try:
            parsed = json.loads(repaired)
            return normalize_control_chars(parsed)
        except Exception as e2:
            logging.warning(f"JSON 解析失败，返回原始文本。Error: {e2}")
            return {"status": "parse_error", "raw": text, "error": str(e2)}


def extract_first_json_object(text: str) -> str | None:
    """
    从文本中提取第一个“括号平衡”的 JSON 对象字符串。

    Args:
        text: 包含 JSON 的原始文本。

    Returns:
        str | None: JSON 对象文本；找不到则返回 None。
    """
    start = text.find("{")
    if start < 0:
        return None

    depth = 0
    in_string = False
    escape = False

    for i in range(start, len(text)):
        ch = text[i]

        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]

    return None


def repair_invalid_json_escapes(text: str) -> str:
    """
    修复 JSON 字符串内部无效反斜杠转义。

    例如将 `\\begin`（在 JSON 中是无效转义 `\\b`?）之外的非法 `\\x` 修复为 `\\\\x`。

    Args:
        text: 可能包含无效转义的 JSON 文本。

    Returns:
        str: 修复后的 JSON 文本。
    """
    # 对本项目而言，\b \f \n \r \t 大多来自 LaTeX 命令的误转义，统一转为字面量更安全。
    valid_escapes = {'"', "\\", "/", "u"}
    out: list[str] = []
    in_string = False
    i = 0

    while i < len(text):
        ch = text[i]

        if not in_string:
            out.append(ch)
            if ch == '"':
                in_string = True
            i += 1
            continue

        # in_string == True
        if ch == '"':
            out.append(ch)
            in_string = False
            i += 1
            continue

        if ch != "\\":
            out.append(ch)
            i += 1
            continue

        # ch == "\" inside string
        if i + 1 >= len(text):
            out.append("\\\\")
            i += 1
            continue

        nxt = text[i + 1]
        if nxt in valid_escapes:
            if nxt == "u":
                # \u 后需 4 位十六进制，否则当作非法转义修复
                hex_part = text[i + 2 : i + 6]
                if len(hex_part) == 4 and all(c in "0123456789abcdefABCDEF" for c in hex_part):
                    out.append("\\")
                    out.append("u")
                    out.append(hex_part)
                    i += 6
                    continue
                out.append("\\\\")
                i += 1
                continue

            out.append("\\")
            out.append(nxt)
            i += 2
            continue

        # 非法转义：补一个反斜杠变成字面量
        out.append("\\\\")
        i += 1

    return "".join(out)


def remove_trailing_commas(text: str) -> str:
    """
    删除 JSON 对象/数组在闭括号前的尾逗号。

    Args:
        text: JSON 文本。

    Returns:
        str: 去除尾逗号后的 JSON 文本。
    """
    return re.sub(r",\s*([}\]])", r"\1", text)


def normalize_control_chars(value: Any) -> Any:
    """
    递归修复字符串中的控制字符，避免 `\\begin` 被解析成退格字符等问题。

    Args:
        value: 任意 JSON 值。

    Returns:
        Any: 修复后的值。
    """
    if isinstance(value, dict):
        return {k: normalize_control_chars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize_control_chars(v) for v in value]
    if isinstance(value, str):
        return (
            value.replace("\x08", "\\b")
            .replace("\x0c", "\\f")
            .replace("\r", "\\r")
            .replace("\t", "\\t")
        )
    return value


def read_input_text(input_path: str) -> str | None:
    """
    读取输入文件文本，自动兼容常见编码。

    对于 `.json` 输入，优先从以下键提取文本:
    - raw_latex_text
    - raw_text
    - latex
    - text

    Args:
        input_path: 输入文件路径。

    Returns:
        str | None: 读取到的文本；失败返回 None。
    """
    encodings = ("utf-8", "utf-8-sig", "gb18030")
    for encoding in encodings:
        try:
            with open(input_path, "r", encoding=encoding) as f:
                text = f.read().strip()

            if input_path.lower().endswith(".json") and text:
                data = json.loads(text)
                if isinstance(data, dict):
                    for key in ("raw_latex_text", "raw_text", "latex", "text"):
                        value = data.get(key)
                        if isinstance(value, str) and value.strip():
                            return value.strip()

            if text:
                return text
        except UnicodeDecodeError:
            continue
        except json.JSONDecodeError:
            logging.error(f"JSON 输入解析失败: {input_path}")
            return None
        except Exception as e:
            logging.error(f"读取输入文件失败: {input_path}, Error: {e}")
            return None

    logging.error(f"输入文件编码无法识别或内容为空: {input_path}")
    return None


def step_latex_extract(raw_latex_text: str) -> dict[str, Any]:
    """
    L1: 原始 LaTeX 清洗 + 结构化提取。

    Args:
        raw_latex_text: 输入原文。

    Returns:
        dict[str, Any]: L1 解析结果。
    """
    prompt = render_prompt("l1", {"raw_latex_text": raw_latex_text})
    result = call_llm(prompt, step="l1")
    return safe_json_parse(result)


def step_statement_rewrite(raw_json: dict[str, Any]) -> dict[str, Any]:
    """
    L2: 结论重构。

    Args:
        raw_json: L1 输出。

    Returns:
        dict[str, Any]: L2 输出。
    """
    prompt = render_prompt("l2", raw_json)
    result = call_llm(prompt, step="l2")
    return safe_json_parse(result)


def step_quality_eval(l2_json: dict[str, Any]) -> dict[str, Any]:
    """
    L3: 教学价值评估。

    Args:
        l2_json: L2 输出。

    Returns:
        dict[str, Any]: L3 输出。
    """
    prompt = render_prompt("l3", l2_json)
    result = call_llm(prompt, step="l3")
    return safe_json_parse(result)


def step_lecture_generate(l2_json: dict[str, Any]) -> dict[str, Any]:
    """
    L4: 讲义模块生成。

    Args:
        l2_json: L2 输出。

    Returns:
        dict[str, Any]: L4 输出。
    """
    payload = build_l4_payload(l2_json)
    prompt = render_prompt("l4", payload)
    result = call_llm(prompt, step="l4")
    return safe_json_parse(result)


def step_meta_generate(all_data: dict[str, Any]) -> dict[str, Any]:
    """
    L5: meta.json 生成。

    Args:
        all_data: 聚合输入（通常包含 l2/l3/l4）。

    Returns:
        dict[str, Any]: L5 输出。
    """
    prompt = render_prompt("l5", all_data)
    result = call_llm(prompt, step="l5")
    return safe_json_parse(result)


def file_exists(path: str) -> bool:
    """
    判断文件是否存在且非空。

    Args:
        path: 文件路径。

    Returns:
        bool: True 表示可视为已有有效缓存。
    """
    return os.path.exists(path) and os.path.getsize(path) > 10


def get_step_error(result: dict[str, Any] | Any) -> str:
    """
    统一抽取阶段失败原因。

    Args:
        result: 阶段返回对象。

    Returns:
        str: 优先返回 error/reason/status。
    """
    if not isinstance(result, dict):
        return "invalid_response"
    return result.get("error") or result.get("reason") or str(result.get("status"))


def clip_text(value: Any, max_chars: int = L5_MAX_TEXT_CHARS) -> Any:
    """
    裁剪超长文本，降低 L5 输入 token 体积。

    Args:
        value: 待裁剪内容。
        max_chars: 最大字符数。

    Returns:
        Any: 若为字符串则返回裁剪后文本，否则原样返回。
    """
    if not isinstance(value, str):
        return value
    if len(value) <= max_chars:
        return value
    return value[:max_chars]


def build_l5_payload(
    l2: dict[str, Any], l3: dict[str, Any], l4: dict[str, Any]
) -> dict[str, Any]:
    """
    构建 L5 输入的精简载荷，减少冗余长文本。

    Args:
        l2: 结论重构结果。
        l3: 评估结果。
        l4: 讲义结果。

    Returns:
        dict[str, Any]: 传给 L5 的精简输入。
    """
    files = {
        "01_statement": clip_text(l4.get("01_statement", "")),
        "04_examples": clip_text(l4.get("04_examples", "")),
        "06_summary": clip_text(l4.get("06_summary", "")),
    }

    evaluation = {
        "scores": l3.get("scores", {}),
        "final_score": l3.get("final_score"),
        "decision": l3.get("decision"),
        "tags": l3.get("tags", []),
        "analysis": clip_text(l3.get("analysis", ""), 600),
    }

    return {
        "statement": clip_text(l2.get("statement", "")),
        "latex": clip_text(l2.get("latex", "")),
        "meta": l2.get("meta", {}),
        "evaluation": evaluation,
        "files": files,
    }


def build_l4_payload(l2: dict[str, Any]) -> dict[str, Any]:
    """
    构建 L4 输入的精简载荷。

    L4 只依赖结论本身，传入过多附加字段会增加 prompt token，
    对结果帮助有限但会拉高时延。

    Args:
        l2: L2 输出。

    Returns:
        dict[str, Any]: L4 需要的最小输入。
    """
    return {
        "statement": clip_text(l2.get("statement", ""), 1600),
        "latex": clip_text(l2.get("latex", ""), 2200),
        "meta": l2.get("meta", {}),
    }


def apply_meta_defaults(meta_json: dict[str, Any], fallback_id: str) -> dict[str, Any]:
    """
    对 L5 结果做默认字段补全，减少 prompt 对固定字段生成的负担。

    Args:
        meta_json: L5 输出 JSON。
        fallback_id: 回退 id（通常为文件名）。

    Returns:
        dict[str, Any]: 补全后的 meta JSON。
    """
    if not isinstance(meta_json, dict):
        return {"status": "invalid_output", "raw": meta_json}

    meta_json.setdefault("id", fallback_id)
    meta_json.setdefault("module", "")
    meta_json.setdefault("core", {})
    meta_json.setdefault("search", {})
    meta_json.setdefault("searchmeta", META_DEFAULT_SEARCHMETA.copy())
    meta_json.setdefault("ranking", {})
    meta_json.setdefault("math", {})
    meta_json.setdefault("content", {})
    meta_json.setdefault("usage", {})
    meta_json.setdefault("interactive", {"has_diagram": False, "geogebra_id": "", "param_demo": {}})
    meta_json.setdefault("assets", {})
    meta_json.setdefault("shareConfig", {})
    meta_json.setdefault("relations", {})
    meta_json.setdefault("meta", {})
    meta_json.setdefault("isPro", 0)
    meta_json.setdefault("remarks", "")
    meta_json.setdefault("knowledgeNode", "")
    meta_json.setdefault("altNodes", "")

    if isinstance(meta_json["searchmeta"], dict):
        for key, value in META_DEFAULT_SEARCHMETA.items():
            meta_json["searchmeta"].setdefault(key, value)

    if isinstance(meta_json["ranking"], dict):
        meta_json["ranking"].setdefault("search_boost", 0)
        meta_json["ranking"].setdefault("hot_score", 50)
        meta_json["ranking"].setdefault("click_rate", 0)
        meta_json["ranking"].setdefault("success_rate", 0)

    if isinstance(meta_json["assets"], dict):
        meta_json["assets"].setdefault("svg", f"{meta_json['id']}.svg")

    if isinstance(meta_json["meta"], dict):
        meta_json["meta"].setdefault("version", 1)
        meta_json["meta"].setdefault("source", "AI生成")
        meta_json["meta"]["created_at"] = date.today().isoformat()

    return meta_json


def build_output_paths(filename: str, output_dir: str) -> dict[str, str]:
    """
    构建单文件各阶段输出路径（按题目聚合到 output/<filename>/）。

    Args:
        filename: 不含扩展名的文件名。
        output_dir: 输出根目录。

    Returns:
        dict[str, str]: l1~l5 到目标文件路径的映射。
    """
    item_dir = os.path.join(output_dir, filename)
    return {
        "l1": os.path.join(item_dir, "l1_raw.json"),
        "l2": os.path.join(item_dir, "l2_statement.json"),
        "l3": os.path.join(item_dir, "l3_eval.json"),
        "l4": os.path.join(item_dir, "l4_lecture.json"),
        "l5": os.path.join(item_dir, "l5_meta.json"),
    }


def save_parse_debug(
    output_dir: str,
    filename: str,
    step_name: str,
    result: dict[str, Any],
) -> None:
    """
    记录 parse_error 原始文本，便于回溯模型输出问题。

    Args:
        output_dir: 输出根目录。
        filename: 输入文件名（无扩展名）。
        step_name: 阶段名（l1/l2/l3/l4/l5）。
        result: 当前阶段返回 JSON。
    """
    if result.get("status") != "parse_error":
        return

    debug_dir = os.path.join(output_dir, filename, "debug")
    os.makedirs(debug_dir, exist_ok=True)
    debug_path = os.path.join(debug_dir, f"{step_name}_parse_error.txt")
    raw = result.get("raw", "")
    err = result.get("error", "")
    with open(debug_path, "w", encoding="utf-8") as f:
        f.write(f"[{step_name}] parse_error: {err}\n\n")
        f.write(raw if isinstance(raw, str) else json.dumps(raw, ensure_ascii=False, indent=2))


def export_lecture_tex_snippets(
    lecture_json: dict[str, Any], filename: str, output_dir: str
) -> None:
    """
    将 L4 的 JSON 字段导出为可直接使用的 .tex 片段文件。

    说明：
    - `lecture/*.json` 中是 JSON 字符串，展示时会出现 `\\` 与 `\\n` 转义。
    - 本函数会把“解码后的真实 LaTeX 内容”写入单独 `.tex` 文件，
      避免手工复制时带入 JSON 转义字符。

    Args:
        lecture_json: L4 输出 JSON。
        filename: 输入文件名（无扩展名）。
        output_dir: 输出根目录。
    """
    if not isinstance(lecture_json, dict):
        return

    target_dir = os.path.join(output_dir, filename)
    os.makedirs(target_dir, exist_ok=True)

    exported = 0
    for key, tex_name in LECTURE_TEX_FILE_MAP.items():
        content = lecture_json.get(key)
        if not isinstance(content, str) or not content.strip():
            continue

        tex_path = os.path.join(target_dir, tex_name)
        with open(tex_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content.strip())
            f.write("\n")
        exported += 1

    if exported:
        logging.info(f"{filename} L4 导出 tex 片段: {exported} 个")


def is_step_success(result: dict[str, Any]) -> bool:
    """
    判断阶段返回是否为成功状态。

    Args:
        result: 阶段返回 JSON。

    Returns:
        bool: 成功返回 True。
    """
    return result.get("status") in STEP_SUCCESS_STATUS


def process_file(input_path: str, output_dir: str) -> str:
    """
    处理单个输入文件。

    规则:
    - 若某阶段输出已存在，则跳过该阶段并复用缓存。
    - 若最终 L5 已存在，直接返回 skipped。

    Args:
        input_path: 输入文件绝对路径。
        output_dir: 输出根目录。

    Returns:
        str: success / error / skipped
    """
    filename = os.path.splitext(os.path.basename(input_path))[0]

    try:
        paths_map = build_output_paths(filename, output_dir)

        # ========= L1 =========
        if file_exists(paths_map["l1"]):
            l1 = load_json_file(paths_map["l1"])
        else:
            raw_text = read_input_text(input_path)
            if not raw_text:
                logging.error(f"{filename} 输入为空或读取失败")
                return "error"
            t0 = time.perf_counter()
            l1 = step_latex_extract(raw_text)
            logging.info(f"{filename} L1 耗时: {time.perf_counter() - t0:.2f}s")
            if not is_step_success(l1):
                save_parse_debug(output_dir, filename, "l1", l1)
                logging.error(f"{filename} L1 失败: {get_step_error(l1)}")
                return "error"
            save_json(l1, paths_map["l1"])

        # ========= L2 =========
        if file_exists(paths_map["l2"]):
            l2 = load_json_file(paths_map["l2"])
        else:
            t0 = time.perf_counter()
            l2 = step_statement_rewrite(l1)
            logging.info(f"{filename} L2 耗时: {time.perf_counter() - t0:.2f}s")
            if not is_step_success(l2):
                save_parse_debug(output_dir, filename, "l2", l2)
                logging.error(f"{filename} L2 失败: {get_step_error(l2)}")
                return "error"
            save_json(l2, paths_map["l2"])

        # ========= L3/L4（并行） =========
        l3 = None
        l4 = None

        if file_exists(paths_map["l3"]):
            l3 = load_json_file(paths_map["l3"])
        if file_exists(paths_map["l4"]):
            l4 = load_json_file(paths_map["l4"])

        future_map: dict[str, Any] = {}
        if l3 is None or l4 is None:
            with ThreadPoolExecutor(max_workers=2) as local_executor:
                if l3 is None:
                    future_map["l3"] = local_executor.submit(step_quality_eval, l2)
                if l4 is None:
                    future_map["l4"] = local_executor.submit(step_lecture_generate, l2)

                step_start = {
                    "l3": time.perf_counter() if "l3" in future_map else None,
                    "l4": time.perf_counter() if "l4" in future_map else None,
                }

                for step_name, future in future_map.items():
                    result = future.result()
                    elapsed = time.perf_counter() - step_start[step_name]
                    logging.info(f"{filename} {step_name.upper()} 耗时: {elapsed:.2f}s")

                    if not is_step_success(result):
                        save_parse_debug(output_dir, filename, step_name, result)
                        logging.error(
                            f"{filename} {step_name.upper()} 失败: {get_step_error(result)}"
                        )
                        return "error"

                    if step_name == "l3":
                        l3 = result
                        save_json(l3, paths_map["l3"])
                    else:
                        l4 = result
                        save_json(l4, paths_map["l4"])
        else:
            # 双缓存命中时，确保变量存在
            if l3 is None:
                l3 = load_json_file(paths_map["l3"])
            if l4 is None:
                l4 = load_json_file(paths_map["l4"])

        # 无论 L4 是新生成还是缓存复用，都导出一份真实 tex 片段文件。
        export_lecture_tex_snippets(l4, filename, output_dir)

        # ========= L5 =========
        if file_exists(paths_map["l5"]):
            logging.info(f"{filename} 已处理，跳过 L5")
            return "skipped"

        merged = build_l5_payload(l2, l3, l4)
        t0 = time.perf_counter()
        l5 = step_meta_generate(merged)
        logging.info(f"{filename} L5 耗时: {time.perf_counter() - t0:.2f}s")
        if not is_step_success(l5):
            save_parse_debug(output_dir, filename, "l5", l5)
            logging.error(f"{filename} L5 失败: {get_step_error(l5)}")
            return "error"
        save_json(apply_meta_defaults(l5, filename), paths_map["l5"])

        return "success"

    except Exception as e:
        logging.error(f"❌ Error processing {filename}: {e}")
        return "error"


def run_batch(
    input_dir: str = INPUT_DIR,
    output_dir: str = OUTPUT_DIR,
    max_workers: int = MAX_WORKERS,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    input_extensions: tuple[str, ...] = DEFAULT_INPUT_EXTENSIONS,
) -> dict[str, int]:
    """
    批量处理输入目录中的文本文件。

    Args:
        input_dir: 输入目录。
        output_dir: 输出目录。
        max_workers: 线程池并发数。
        timeout_seconds: 单文件 future 结果等待超时。
        input_extensions: 支持的输入扩展名元组。

    Returns:
        dict[str, int]: 处理统计（success/error/skipped）。
    """
    if not os.path.exists(input_dir):
        logging.error(f"输入目录不存在: {input_dir}")
        return {"success": 0, "error": 1, "skipped": 0}

    files = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.lower().endswith(input_extensions)
    ]

    if not files:
        logging.warning(
            f"未找到待处理文本文件，支持扩展名: {', '.join(input_extensions)}"
        )
        return {"success": 0, "error": 0, "skipped": 0}

    files.sort()
    logging.info(f"开始批处理，共 {len(files)} 个文件，并发数 {max_workers}")
    batch_start = time.perf_counter()

    stats = {"success": 0, "error": 0, "skipped": 0}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(process_file, file_path, output_dir): file_path
            for file_path in files
        }

        with tqdm(total=len(files), desc="Processing Pipeline") as pbar:
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result(timeout=timeout_seconds)
                    stats[result] += 1
                except TimeoutError:
                    logging.error(f"{file_path} 超时（>{timeout_seconds}s）")
                    stats["error"] += 1
                except Exception as e:
                    logging.error(f"{file_path} 任务异常: {e}")
                    stats["error"] += 1

                pbar.set_postfix(stats)
                pbar.update(1)

    total_elapsed = time.perf_counter() - batch_start
    logging.info(f"\n✅ 任务结束: {stats}")
    logging.info(f"⏱ 总耗时: {total_elapsed:.2f}s")
    return stats


def main() -> None:
    """脚本入口：解析参数并启动批处理。"""
    args = parse_args()

    if args.max_workers <= 0:
        raise ValueError("--max-workers 必须是正整数")
    if args.timeout <= 0:
        raise ValueError("--timeout 必须是正整数")

    extensions = normalize_extensions(args.extensions)
    if not extensions:
        raise ValueError("--extensions 不能为空")

    run_batch(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        max_workers=args.max_workers,
        timeout_seconds=args.timeout,
        input_extensions=extensions,
    )


if __name__ == "__main__":
    main()
