"""
12_pipeline/run_pipeline.py

功能介绍
--------
该脚本用于将 `input/<ID>/source.*` 里的 LaTeX/文本输入，批量加工为 5 个阶段的结构化结果：
- L1: raw 文本清洗与结构提取 -> output/<ID>/l1_raw.json
- L2: 结论重构 -> output/<ID>/l2_statement.json
- L3: 教学价值评估 -> output/<ID>/l3_eval.json
- L4: 讲义模块生成 -> output/<ID>/l4_lecture.json
- L5: 检索与推荐 meta 生成 -> output/<ID>/l5_meta.json
- 讲义片段导出 -> output/<ID>/01_statement.tex ~ 06_summary.tex

新增能力
--------
1. `--ids`: 仅处理指定 ID（支持一个或多个，如 `--ids I001 I002`）。
2. `--force`: 强制全量重跑，忽略并覆盖所有阶段缓存（默认关闭）。

缓存策略
--------
1. 默认模式（不传 `--force`）:
   - 若阶段输出文件已存在，则直接复用缓存；
   - 仅补齐缺失阶段。
2. 强制模式（传 `--force`）:
   - L1~L5 全部重新生成；
   - 已有输出会被新结果覆盖。

处理流程
--------
0. 截图在deepseek中进行识别成latex文本后，放在 `input/<ID>/source.*` 中，支持多种扩展名（如 .tex/.txt/.json），这一步是手工完成的，脚本不涉及 OCR 识别。因为脚本不识别图片，所以输入必须是文本格式，推荐使用 `.tex` 或 `.txt`，也支持 `.json`（会优先从 `raw_latex_text` 等字段提取文本），目前只支持letex格式的文本输入，后续可根据需求增加对纯文本的支持。
1. 扫描输入目录中的 ID 子目录（如 `I001/`），读取其中 `source.*` 或首个可识别文件。
2. 若传入 `--ids`，先按 ID 过滤待处理项。
3. 每个 ID 执行 L1 -> L5；L3 与 L4 会并行执行以降低耗时。
4. 每个阶段统一走 LLM 调用封装，带有重试和并发闸门控制。
5. 批处理结束后输出 success/error/skipped 统计。

脚本用法
--------
1) 默认批量处理全部 ID（优先复用缓存）
   python run_pipeline.py

2) 仅处理指定 ID
   python run_pipeline.py --ids I001

3) 处理多个 ID，并强制全量重跑
   python run_pipeline.py --ids I001 I002 --force

4) 自定义输入输出目录、并发、扩展名与单文件超时
   python run_pipeline.py --input-dir ./input --output-dir ./output --max-workers 3 --extensions .txt .tex --timeout 120
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
API_TIMEOUT_SECONDS = int(perf.get("api_timeout_seconds", 180))
L4_RETRY_TIMES = int(perf.get("l4_retry_times", 1))
PROGRESS_LOG_START_SECONDS = max(1, int(perf.get("progress_log_start_seconds", 120)))
PROGRESS_LOG_INTERVAL_SECONDS = max(
    1, int(perf.get("progress_log_interval_seconds", 30))
)
PROGRESS_POLL_SECONDS = max(1, int(perf.get("progress_poll_seconds", 5)))

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
    "l4": "reasoning",
    "l5": "default",
    "l6": "default",
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

ID_DIR_PATTERN = re.compile(r"^[A-Za-z]\d{3}$")
L6_DIRNAME_FILE_PATTERN_TEMPLATE = r"^{item_id}_[a-z0-9]+(?:_[a-z0-9]+)*$"
L6_FALLBACK_SLUG = "generated_conclusion"


def parse_args() -> argparse.Namespace:
    """
    解析命令行参数。

    Returns:
        argparse.Namespace: 运行参数集合。
    """
    parser = argparse.ArgumentParser(
        description=(
            "批量运行 LaTeX -> statement/eval/lecture/meta/dirname 的六阶段流水线。"
            " 输入目录需包含 ID 子目录（如 input/I001/source.tex）。"
        ),
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
            "输入文件扩展名列表（空格分隔）。\n" "示例: --extensions .txt .tex .json"
        ),
    )
    parser.add_argument(
        "--ids",
        nargs="+",
        default=None,
        help=(
            "仅处理指定 ID（支持空格或逗号分隔，大小写不敏感）。\n"
            "示例: --ids I001 I002 或 --ids i001,i002"
        ),
    )
    parser.add_argument(
        "positional_ids",
        nargs="*",
        help=(
            "位置参数 ID，等价于 --ids，支持空格或逗号分隔。\n"
            "示例: I001 I002 或 i001,i002"
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制全量重跑并覆盖缓存（默认: 关闭，优先复用缓存）",
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


def normalize_ids(ids: list[str] | None) -> list[str]:
    """
    标准化并校验 `--ids` 参数。

    支持两种输入形式：
    1) 空格分隔：`--ids I001 I002`
    2) 逗号分隔：`--ids I001,I002`

    Args:
        ids: 命令行读取到的原始 ID 列表。

    Returns:
        list[str]: 去重后的规范化 ID 列表（统一为大写）。

    Raises:
        ValueError: 出现非法 ID（非 `字母 + 3 位数字`）时抛出。
    """
    if not ids:
        return []

    normalized: list[str] = []
    for raw in ids:
        for piece in raw.replace("，", ",").split(","):
            item_id = piece.strip().upper()
            if not item_id:
                continue
            if not ID_DIR_PATTERN.match(item_id):
                raise ValueError(f"ID 参数包含非法值: {piece!r}（期望格式如 I001）")
            normalized.append(item_id)

    return list(dict.fromkeys(normalized))


def find_source_file_in_id_dir(
    id_dir: str, input_extensions: tuple[str, ...]
) -> str | None:
    """
    在单个 ID 子目录中定位输入源文件。

    优先级：
    1) `source.<ext>`（按扩展名顺序）
    2) 目录中首个匹配扩展名的文件（按文件名字典序）

    Args:
        id_dir: ID 子目录绝对路径（例如 input/I001）。
        input_extensions: 支持的扩展名。

    Returns:
        str | None: 命中的文件绝对路径；找不到返回 None。
    """
    for ext in input_extensions:
        candidate = os.path.join(id_dir, f"source{ext}")
        if os.path.isfile(candidate):
            return candidate

    files = []
    for name in os.listdir(id_dir):
        full_path = os.path.join(id_dir, name)
        if os.path.isfile(full_path) and name.lower().endswith(input_extensions):
            files.append(full_path)

    if not files:
        return None

    files.sort()
    return files[0]


def discover_input_items(
    input_dir: str, input_extensions: tuple[str, ...]
) -> list[tuple[str, str]]:
    """
    扫描输入目录并发现待处理 ID 项。

    约定：
    - 输入目录下每个一级子目录名是 ID（如 I001）。
    - 每个 ID 子目录内放源文件（推荐 `source.tex` / `source.txt`）。

    Args:
        input_dir: 输入根目录。
        input_extensions: 支持扩展名。

    Returns:
        list[tuple[str, str]]: [(item_id, source_file_path), ...]
    """
    items: list[tuple[str, str]] = []

    for name in sorted(os.listdir(input_dir)):
        id_dir = os.path.join(input_dir, name)
        if not os.path.isdir(id_dir):
            continue
        if not ID_DIR_PATTERN.match(name):
            continue

        source_path = find_source_file_in_id_dir(id_dir, input_extensions)
        if not source_path:
            logging.warning(
                f"{name} 未找到可用源文件（支持: {', '.join(input_extensions)}），已跳过"
            )
            continue
        items.append((name, source_path))

    return items


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


def wait_future_with_progress(
    future: Any,
    step_label: str,
    *,
    start_time: float | None = None,
    log_start_seconds: int = PROGRESS_LOG_START_SECONDS,
    log_interval_seconds: int = PROGRESS_LOG_INTERVAL_SECONDS,
    poll_seconds: int = PROGRESS_POLL_SECONDS,
) -> Any:
    """
    等待 future 结果，并在长耗时场景周期打印“仍在执行”日志。
    """
    t0 = start_time if start_time is not None else time.perf_counter()
    next_log_at = float(log_start_seconds)

    while True:
        try:
            return future.result(timeout=poll_seconds)
        except TimeoutError:
            elapsed = time.perf_counter() - t0
            if elapsed >= next_log_at:
                logging.info(f"{step_label} 仍在执行，已耗时: {elapsed:.2f}s")
                next_log_at += float(log_interval_seconds)


def run_step_with_progress(
    step_label: str,
    func: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> Any:
    """
    在线程中执行单步任务，并输出长耗时心跳日志。
    """
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=1) as local_executor:
        future = local_executor.submit(func, *args, **kwargs)
        return wait_future_with_progress(future, step_label, start_time=t0)


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
        retries = L4_RETRY_TIMES if step == "l4" else RETRY_TIMES

        def _request() -> Any:
            local_client = OpenAI(
                api_key=api_config["api_key"],
                base_url=api_config["base_url"],
            )
            return local_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=TEMPERATURE,
                timeout=API_TIMEOUT_SECONDS,
            )

        response = retry_call(_request, retries=retries)
        return response.choices[0].message.content


def render_prompt(step: str, input_data: Any) -> str:
    """
    将输入数据注入到 prompt 模板中。

    优先替换 `{{input}}` 占位符；若模板未使用占位符，则在末尾附加输入数据。

    Args:
        step: 阶段名（l1~l6）。
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
                if len(hex_part) == 4 and all(
                    c in "0123456789abcdefABCDEF" for c in hex_part
                ):
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


def step_dirname_generate(all_data: dict[str, Any]) -> str:
    """
    L6: 生成目录名（文件名格式）字符串。

    Args:
        all_data: 提供给 L6 的输入载荷。

    Returns:
        str: LLM 原始文本输出。
    """
    prompt = render_prompt("l6", all_data)
    result = call_llm(prompt, step="l6")
    return result if isinstance(result, str) else str(result)


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


def build_l6_payload(
    item_id: str,
    l2: dict[str, Any],
    l5: dict[str, Any],
) -> dict[str, Any]:
    """
    构建 L6 输入载荷。

    Args:
        item_id: 当前条目 ID（如 C017）。
        l2: L2 输出。
        l5: L5 输出。

    Returns:
        dict[str, Any]: 供 L6 使用的精简字段。
    """
    l5_core = l5.get("core", {}) if isinstance(l5.get("core"), dict) else {}
    l5_search = l5.get("search", {}) if isinstance(l5.get("search"), dict) else {}
    l2_meta = l2.get("meta", {}) if isinstance(l2.get("meta"), dict) else {}
    keywords = l5_search.get("keywords", [])
    if not isinstance(keywords, list):
        keywords = []

    return {
        "id": item_id,
        "module": l5.get("module", ""),
        "title": l5_core.get("title") or l2_meta.get("title", ""),
        "summary": l5_core.get("summary", ""),
        "statement": clip_text(l2.get("statement", ""), 900),
        "latex": clip_text(l2.get("latex", ""), 1200),
        "keywords": keywords[:8],
    }


def pick_first_nonempty_line(text: str) -> str:
    """
    从文本中提取首个非空行，并清理常见包裹符号。
    """
    clean = text.replace("```", "").strip()
    for line in clean.splitlines():
        candidate = line.strip().strip("`").strip('"').strip("'")
        if candidate:
            return candidate
    return ""


def normalize_l6_dirname(item_id: str, raw_output: str) -> str:
    """
    将 L6 原始输出标准化为 `<ID>_<snake_case_slug>`。
    """
    canonical_id = item_id.upper()
    line = pick_first_nonempty_line(raw_output)
    line = line.replace("\\", "/").split("/")[-1].strip()

    if not line:
        return f"{canonical_id}_{L6_FALLBACK_SLUG}"

    full_pattern = re.compile(r"^[A-Za-z]\d{3}_(.+)$")
    match = full_pattern.match(line)
    slug_source = match.group(1) if match else line

    slug = re.sub(r"[^A-Za-z0-9]+", "_", slug_source).strip("_").lower()
    slug = re.sub(r"_+", "_", slug)
    if len(slug) > 64:
        slug = slug[:64].rstrip("_")
    if not slug:
        slug = L6_FALLBACK_SLUG

    return f"{canonical_id}_{slug}"


def list_l6_dirname_files(item_dir: str, item_id: str) -> list[str]:
    """
    列出 output/<ID>/ 下所有形如 `<ID>_<slug>` 的文件（L6 产物）。
    """
    if not os.path.isdir(item_dir):
        return []

    pattern = re.compile(
        L6_DIRNAME_FILE_PATTERN_TEMPLATE.format(item_id=re.escape(item_id)),
        re.IGNORECASE,
    )

    result: list[str] = []
    for name in os.listdir(item_dir):
        full_path = os.path.join(item_dir, name)
        if os.path.isfile(full_path) and pattern.match(name):
            result.append(full_path)

    result.sort()
    return result


def get_cached_l6_dirname(item_dir: str, item_id: str) -> str | None:
    """
    返回已缓存的 L6 文件名；若存在多个，返回字典序第一个并记录告警。
    """
    files = list_l6_dirname_files(item_dir, item_id)
    if not files:
        return None
    if len(files) > 1:
        names = ", ".join(os.path.basename(path) for path in files)
        logging.warning(f"{item_id} 检测到多个 L6 文件名缓存，将使用第一个: {names}")
    return os.path.basename(files[0])


def save_l6_dirname_file(item_dir: str, item_id: str, dirname_file: str) -> str:
    """
    保存 L6 产物：创建一个“文件名即目录名”的空文件，并清理旧缓存。

    Returns:
        str: 实际保存的绝对路径。
    """
    os.makedirs(item_dir, exist_ok=True)

    pattern = re.compile(
        L6_DIRNAME_FILE_PATTERN_TEMPLATE.format(item_id=re.escape(item_id)),
        re.IGNORECASE,
    )
    if not pattern.match(dirname_file):
        raise ValueError(f"无效 L6 文件名格式: {dirname_file}")

    for path in list_l6_dirname_files(item_dir, item_id):
        if os.path.basename(path) != dirname_file:
            os.remove(path)

    target_path = os.path.join(item_dir, dirname_file)
    with open(target_path, "w", encoding="utf-8", newline="\n") as f:
        # 文件内容不参与业务，仅使用文件名作为目录名载体。
        f.write("")

    return target_path


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

    # 关键约束：meta.id 必须与当前处理的题目 ID 一致，避免模型幻觉写错 ID。
    original_id = meta_json.get("id")
    if isinstance(original_id, str) and original_id and original_id != fallback_id:
        logging.warning(
            f"{fallback_id} L5 id 已纠正: {original_id!r} -> {fallback_id!r}"
        )
    meta_json["id"] = fallback_id
    meta_json.setdefault("module", "")
    meta_json.setdefault("core", {})
    meta_json.setdefault("search", {})
    meta_json.setdefault("searchmeta", META_DEFAULT_SEARCHMETA.copy())
    meta_json.setdefault("ranking", {})
    meta_json.setdefault("math", {})
    meta_json.setdefault("content", {})
    meta_json.setdefault("usage", {})
    meta_json.setdefault(
        "interactive", {"has_diagram": False, "geogebra_id": "", "param_demo": {}}
    )
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
        # 若 svg 正好是“旧 id 命名”，同步修正，避免出现 id 与 svg 文件名不一致。
        if (
            isinstance(original_id, str)
            and original_id
            and meta_json["assets"].get("svg") == f"{original_id}.svg"
        ):
            meta_json["assets"]["svg"] = f"{meta_json['id']}.svg"
        else:
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
        dict[str, str]: l1~l5 到目标文件路径的映射（L6 为动态文件名，不在此映射中）。
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
        f.write(
            raw
            if isinstance(raw, str)
            else json.dumps(raw, ensure_ascii=False, indent=2)
        )


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


def process_file(
    item_id: str,
    input_path: str,
    output_dir: str,
    force: bool = False,
) -> str:
    """
    Process one input item through L1~L6.

    Returns:
        str: success / error / skipped
    """
    filename = item_id

    try:
        paths_map = build_output_paths(filename, output_dir)
        item_output_dir = os.path.join(output_dir, filename)
        if force:
            logging.info(f"{filename} 启用 --force，忽略缓存并全量重跑")

        # ========= L1 =========
        if not force and file_exists(paths_map["l1"]):
            l1 = load_json_file(paths_map["l1"])
        else:
            raw_text = read_input_text(input_path)
            if not raw_text:
                logging.error(f"{filename} 输入为空或读取失败")
                return "error"
            t0 = time.perf_counter()
            l1 = run_step_with_progress(f"{filename} L1", step_latex_extract, raw_text)
            logging.info(f"{filename} L1 耗时: {time.perf_counter() - t0:.2f}s")
            if not is_step_success(l1):
                save_parse_debug(output_dir, filename, "l1", l1)
                logging.error(f"{filename} L1 失败: {get_step_error(l1)}")
                return "error"
            save_json(l1, paths_map["l1"])

        # ========= L2 =========
        if not force and file_exists(paths_map["l2"]):
            l2 = load_json_file(paths_map["l2"])
        else:
            t0 = time.perf_counter()
            l2 = run_step_with_progress(f"{filename} L2", step_statement_rewrite, l1)
            logging.info(f"{filename} L2 耗时: {time.perf_counter() - t0:.2f}s")
            if not is_step_success(l2):
                save_parse_debug(output_dir, filename, "l2", l2)
                logging.error(f"{filename} L2 失败: {get_step_error(l2)}")
                return "error"
            save_json(l2, paths_map["l2"])

        # ========= L3/L4 (parallel) =========
        l3 = None
        l4 = None

        if not force and file_exists(paths_map["l3"]):
            l3 = load_json_file(paths_map["l3"])
        if not force and file_exists(paths_map["l4"]):
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
                    result = wait_future_with_progress(
                        future,
                        f"{filename} {step_name.upper()}",
                        start_time=step_start[step_name],
                    )
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
            if l3 is None:
                l3 = load_json_file(paths_map["l3"])
            if l4 is None:
                l4 = load_json_file(paths_map["l4"])

        # Always export tex snippets from L4
        export_lecture_tex_snippets(l4, filename, output_dir)

        # ========= L5 =========
        l5: dict[str, Any] | None = None
        l5_from_cache = False
        if not force and file_exists(paths_map["l5"]):
            try:
                l5_cached = load_json_file(paths_map["l5"])
                cached_id = l5_cached.get("id")
                patched = False
                if cached_id != filename:
                    l5_cached["id"] = filename
                    patched = True
                    if (
                        isinstance(cached_id, str)
                        and isinstance(l5_cached.get("assets"), dict)
                        and l5_cached["assets"].get("svg") == f"{cached_id}.svg"
                    ):
                        l5_cached["assets"]["svg"] = f"{filename}.svg"
                if patched:
                    save_json(l5_cached, paths_map["l5"])
                    logging.warning(
                        f"{filename} 检测到历史 L5 id 异常，已自动修正: "
                        f"{cached_id!r} -> {filename!r}"
                    )
                l5 = l5_cached
                l5_from_cache = True
            except Exception as e:
                logging.warning(f"{filename} L5 缓存校正失败，转为重跑 L5: {e}")

        if l5 is None:
            merged = build_l5_payload(l2, l3, l4)
            t0 = time.perf_counter()
            l5 = run_step_with_progress(f"{filename} L5", step_meta_generate, merged)
            logging.info(f"{filename} L5 耗时: {time.perf_counter() - t0:.2f}s")
            if not is_step_success(l5):
                save_parse_debug(output_dir, filename, "l5", l5)
                logging.error(f"{filename} L5 失败: {get_step_error(l5)}")
                return "error"
            l5 = apply_meta_defaults(l5, filename)
            save_json(l5, paths_map["l5"])
        else:
            logging.info(f"{filename} 已处理，跳过 L5")

        # ========= L6 =========
        cached_l6 = None if force else get_cached_l6_dirname(item_output_dir, filename)
        if cached_l6 and l5_from_cache:
            logging.info(f"{filename} 已处理，跳过 L6")
            return "skipped"

        if cached_l6:
            logging.info(f"{filename} L6 将更新缓存: {cached_l6}")

        l6_payload = build_l6_payload(filename, l2, l5)
        t0 = time.perf_counter()
        l6_raw = run_step_with_progress(f"{filename} L6", step_dirname_generate, l6_payload)
        l6_dirname = normalize_l6_dirname(filename, l6_raw)
        l6_path = save_l6_dirname_file(item_output_dir, filename, l6_dirname)
        logging.info(f"{filename} L6 耗时: {time.perf_counter() - t0:.2f}s")
        logging.info(f"{filename} L6 目录名: {os.path.basename(l6_path)}")

        return "success"

    except Exception as e:
        logging.error(f"Error processing {filename}: {e}")
        return "error"

def run_batch(
    input_dir: str = INPUT_DIR,
    output_dir: str = OUTPUT_DIR,
    max_workers: int = MAX_WORKERS,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    input_extensions: tuple[str, ...] = DEFAULT_INPUT_EXTENSIONS,
    target_ids: list[str] | None = None,
    force: bool = False,
) -> dict[str, int]:
    """
    批量处理输入目录中的 ID 子目录。

    Args:
        input_dir: 输入目录（例如包含 I001/I002 子目录）。
        output_dir: 输出目录。
        max_workers: 线程池并发数。
        timeout_seconds: 单文件 future 结果等待超时。
        input_extensions: 支持的输入扩展名元组。
        target_ids: 可选；仅处理这些 ID。
        force: 是否强制全量重跑并覆盖缓存。

    Returns:
        dict[str, int]: 处理统计（success/error/skipped）。
    """
    if not os.path.exists(input_dir):
        logging.error(f"输入目录不存在: {input_dir}")
        return {"success": 0, "error": 1, "skipped": 0}

    items = discover_input_items(input_dir, input_extensions)
    requested_ids = target_ids or []
    requested_id_set = set(requested_ids)

    # 若指定了 --ids，仅保留命中的 ID 项，并提示未命中的 ID。
    if requested_id_set:
        items = [item for item in items if item[0] in requested_id_set]
        found_id_set = {item[0] for item in items}
        missing_ids = sorted(requested_id_set - found_id_set)
        if missing_ids:
            logging.warning(
                "--ids 中以下 ID 未找到可用输入源文件，已跳过: "
                + ", ".join(missing_ids)
            )

    if not items:
        if requested_id_set:
            logging.warning("按 --ids 过滤后没有可处理项。")
        else:
            logging.warning(
                "未找到待处理 ID 子目录或源文件。"
                f" 支持扩展名: {', '.join(input_extensions)}"
            )
        return {"success": 0, "error": 0, "skipped": 0}

    mode = "force（全量重跑）" if force else "cache（优先复用）"
    logging.info(
        f"开始批处理，共 {len(items)} 个条目，并发数 {max_workers}，模式: {mode}"
    )
    if requested_ids:
        logging.info(f"指定 ID: {', '.join(requested_ids)}")
    batch_start = time.perf_counter()

    stats = {"success": 0, "error": 0, "skipped": 0}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_item = {
            executor.submit(process_file, item_id, source_path, output_dir, force): (
                item_id,
                source_path,
            )
            for item_id, source_path in items
        }

        with tqdm(total=len(items), desc="Processing Pipeline") as pbar:
            for future in as_completed(future_to_item):
                item_id, source_path = future_to_item[future]
                try:
                    result = future.result(timeout=timeout_seconds)
                    stats[result] += 1
                except TimeoutError:
                    logging.error(
                        f"{item_id} 超时（>{timeout_seconds}s），源文件: {source_path}"
                    )
                    stats["error"] += 1
                except Exception as e:
                    logging.error(f"{item_id} 任务异常: {e}")
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

    raw_ids: list[str] = []
    if args.ids:
        raw_ids.extend(args.ids)
    if args.positional_ids:
        raw_ids.extend(args.positional_ids)

    target_ids = normalize_ids(raw_ids)
    if (args.ids is not None or args.positional_ids) and not target_ids:
        raise ValueError("ID 参数不能为空")

    run_batch(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        max_workers=args.max_workers,
        timeout_seconds=args.timeout,
        input_extensions=extensions,
        target_ids=target_ids,
        force=args.force,
    )


if __name__ == "__main__":
    main()

