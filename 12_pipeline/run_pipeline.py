"""
12_pipeline/run_pipeline.py

功能介绍
--------
该脚本负责把 `input/` 目录中的 LaTeX 文本输入批量加工为 5 个阶段的结构化结果：
- L1: raw 文本清洗与结构提取 -> output/raw/*.json
- L2: 结论重构 -> output/statement/*.json
- L3: 教学价值评估 -> output/eval/*.json
- L4: 讲义模块生成 -> output/lecture/*.json
- L5: 检索与推荐 meta 生成 -> output/meta/*.json

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
    "l4": "reasoning",
    "l5": "default",
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

    try:
        match = re.search(r"\{.*\}", clean_text, re.S)
        if match:
            return json.loads(match.group())
        return json.loads(clean_text)
    except Exception as e:
        logging.warning(f"JSON 解析失败，返回原始文本。Error: {e}")
        return {"status": "parse_error", "raw": text}


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
    prompt = render_prompt("l4", l2_json)
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


def build_output_paths(filename: str, output_dir: str) -> dict[str, str]:
    """
    构建单文件各阶段输出路径。

    Args:
        filename: 不含扩展名的文件名。
        output_dir: 输出根目录。

    Returns:
        dict[str, str]: l1~l5 到目标文件路径的映射。
    """
    return {
        "l1": os.path.join(output_dir, "raw", f"{filename}.json"),
        "l2": os.path.join(output_dir, "statement", f"{filename}.json"),
        "l3": os.path.join(output_dir, "eval", f"{filename}.json"),
        "l4": os.path.join(output_dir, "lecture", f"{filename}.json"),
        "l5": os.path.join(output_dir, "meta", f"{filename}.json"),
    }


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
            with open(paths_map["l1"], "r", encoding="utf-8") as f:
                l1 = json.load(f)
        else:
            raw_text = read_input_text(input_path)
            if not raw_text:
                logging.error(f"{filename} 输入为空或读取失败")
                return "error"
            l1 = step_latex_extract(raw_text)
            if not is_step_success(l1):
                logging.error(f"{filename} L1 失败: {get_step_error(l1)}")
                return "error"
            save_json(l1, paths_map["l1"])

        # ========= L2 =========
        if file_exists(paths_map["l2"]):
            with open(paths_map["l2"], "r", encoding="utf-8") as f:
                l2 = json.load(f)
        else:
            l2 = step_statement_rewrite(l1)
            if not is_step_success(l2):
                logging.error(f"{filename} L2 失败: {get_step_error(l2)}")
                return "error"
            save_json(l2, paths_map["l2"])

        # ========= L3 =========
        if file_exists(paths_map["l3"]):
            with open(paths_map["l3"], "r", encoding="utf-8") as f:
                l3 = json.load(f)
        else:
            l3 = step_quality_eval(l2)
            if not is_step_success(l3):
                logging.error(f"{filename} L3 失败: {get_step_error(l3)}")
                return "error"
            save_json(l3, paths_map["l3"])

        # ========= L4 =========
        if file_exists(paths_map["l4"]):
            with open(paths_map["l4"], "r", encoding="utf-8") as f:
                l4 = json.load(f)
        else:
            l4 = step_lecture_generate(l2)
            if not is_step_success(l4):
                logging.error(f"{filename} L4 失败: {get_step_error(l4)}")
                return "error"
            save_json(l4, paths_map["l4"])

        # ========= L5 =========
        if file_exists(paths_map["l5"]):
            logging.info(f"{filename} 已处理，跳过 L5")
            return "skipped"

        merged = {"l2": l2, "l3": l3, "l4": l4}
        l5 = step_meta_generate(merged)
        if not is_step_success(l5):
            logging.error(f"{filename} L5 失败: {get_step_error(l5)}")
            return "error"
        save_json(l5, paths_map["l5"])

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

    logging.info(f"\n✅ 任务结束: {stats}")
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
