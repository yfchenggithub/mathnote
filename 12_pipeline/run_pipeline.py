"""
12_pipeline/run_pipeline.py

功能介绍
--------
该脚本用于将 `input/<ID>/source.*` 里的 LaTeX/文本输入，批量加工为 5 个阶段的结构化结果：
- L1: raw 文本清洗与结构提取 -> output/<ID>/l1_raw.json
- L2: 结论重构 -> output/<ID>/l2_statement.json
- L3: 教学价值评估 -> output/<ID>/l3_eval.json
- L4: 讲义模块生成 -> output/<ID>/l4_lecture.json
- L4_check: 讲义终审修复 -> output/<ID>/l4_lecture_checked.json
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
   - 若对应阶段 prompt 指纹发生变化，则该阶段缓存自动失效并重跑（与 `--force` 无关）；
   - 若任一 prompt 变化导致“全局 prompt 快照”不一致，则该条目所有阶段缓存本轮全部失效；
   - 仅补齐缺失阶段。
2. 强制模式（传 `--force`）:
   - L1~L5 全部重新生成；
   - 已有输出会被新结果覆盖。

处理流程
--------
0. 截图在deepseek中进行识别成latex文本后，放在 `input/<ID>/source.*` 中，支持多种扩展名（如 .tex/.txt/.json），这一步是手工完成的，脚本不涉及 OCR 识别。因为脚本不识别图片，所以输入必须是文本格式，推荐使用 `.tex` 或 `.txt`，也支持 `.json`（会优先从 `raw_latex_text` 等字段提取文本），目前只支持letex格式的文本输入，后续可根据需求增加对纯文本的支持。
1. 扫描输入目录中的 ID 子目录（如 `I001/`），读取其中 `source.*` 或首个可识别文件。
2. 若传入 `--ids`，先按 ID 过滤待处理项。
3. 每个 ID 串行执行 L1 -> L6。
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

4) 自定义输入输出目录与扩展名
   python run_pipeline.py --input-dir ./input --output-dir ./output --extensions .txt .tex
"""

import argparse
from contextvars import ContextVar
import hashlib
import json
import logging
import os
import random
import re
import time
from datetime import date, datetime
from threading import Semaphore, Thread
from typing import Any, Callable

from openai import OpenAI
from tqdm import tqdm

from config.config_loader import (
    get_api_config,
    get_model_config,
    get_pipeline_config,
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
semaphore: Semaphore

# =========================
# 配置加载
# =========================

api_config = get_api_config()
model_config = get_model_config()
pipeline_config = get_pipeline_config()
paths = get_paths()
perf = get_performance()


def coerce_bool_config(value: Any, default: bool) -> bool:
    """
    将配置值稳健转换为布尔值；非法值回退默认值。

    支持:
    - bool
    - "true"/"false" 等常见字符串
    - 0/1
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        token = value.strip().lower()
        if token in {"1", "true", "yes", "on"}:
            return True
        if token in {"0", "false", "no", "off"}:
            return False
    return default


def coerce_int_config(value: Any, default: int, *, minimum: int = 0) -> int:
    """
    Coerce int-like configuration values with a lower bound.
    """
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, parsed)


ENABLE_L3 = coerce_bool_config(pipeline_config.get("enable_l3", True), True)
ENABLE_L4 = coerce_bool_config(pipeline_config.get("enable_l4", True), True)
ENABLE_L4_CHECK = coerce_bool_config(
    pipeline_config.get("enable_l4_check", True), True
)
ENABLE_L5 = coerce_bool_config(pipeline_config.get("enable_l5", True), True)

if not ENABLE_L4 and ENABLE_L4_CHECK:
    logging.warning("配置冲突: enable_l4=false 时将自动忽略 enable_l4_check。")
    ENABLE_L4_CHECK = False

TEMPERATURE = perf["temperature"]
RETRY_TIMES = perf["retry_times"]
API_TIMEOUT_SECONDS = int(perf.get("api_timeout_seconds", 180))
L4_RETRY_TIMES = int(perf.get("l4_retry_times", 1))
API_CONCURRENCY = max(1, int(perf.get("api_concurrency", 3)))

raw_step_max_tokens = perf.get("step_max_tokens", {})
STEP_MAX_TOKENS: dict[str, int] = {}
if isinstance(raw_step_max_tokens, dict):
    for step_name, value in raw_step_max_tokens.items():
        if isinstance(step_name, str) and isinstance(value, int) and value > 0:
            STEP_MAX_TOKENS[step_name] = value

LOG_PROMPT_STATS = bool(perf.get("log_prompt_stats", False))
PROGRESS_LOG_START_SECONDS = coerce_int_config(
    perf.get("progress_log_start_seconds", 120), 120, minimum=0
)
PROGRESS_LOG_INTERVAL_SECONDS = coerce_int_config(
    perf.get("progress_log_interval_seconds", 30), 30, minimum=1
)
PROGRESS_POLL_SECONDS = coerce_int_config(
    perf.get("progress_poll_seconds", 5), 5, minimum=1
)
# Keep first heartbeat responsive even when configured start is very large.
FIRST_PROGRESS_LOG_SECONDS = (
    PROGRESS_LOG_INTERVAL_SECONDS
    if PROGRESS_LOG_START_SECONDS <= 0
    else min(PROGRESS_LOG_START_SECONDS, PROGRESS_LOG_INTERVAL_SECONDS)
)

INPUT_DIR = os.path.join(BASE_DIR, paths["input_dir"])
OUTPUT_DIR = os.path.join(BASE_DIR, paths["output_dir"])

DEFAULT_INPUT_EXTENSIONS = (".tex", ".txt", ".md", ".latex", ".json")
L5_MAX_TEXT_CHARS = 2400

STEP_SUCCESS_STATUS = ("success", None)
NON_RETRY_ERROR_CODES = {
    "invalid_api_key",
    "model_not_found",
    "insufficient_quota",
}

# pipeline 各阶段模型映射由配置文件统一控制。
PIPELINE_MODEL_STEPS = ("l1", "l2", "l3", "l4", "l4_check", "l5", "l6")

# 模型类型名到 app_config.model 键名的映射（兼容旧命名）
MODEL_CONFIG_KEY_BY_TYPE = {
    "flash": "flash",
    "pro": "pro",
    "default": "flash",
    "reasoning": "pro",
}


def normalize_model_type_name(model_type: str) -> str | None:
    """
    统一模型类型命名为 flash/pro；无法识别时返回 None。
    """
    mapped = MODEL_CONFIG_KEY_BY_TYPE.get(model_type)
    if mapped is None:
        return None
    return "flash" if mapped == "flash" else "pro"


def resolve_model_config_key(model_type: str) -> str | None:
    """
    将模型类型名解析为 app_config.model 的键名。
    """
    return MODEL_CONFIG_KEY_BY_TYPE.get(model_type)


def build_step_model_map() -> dict[str, str]:
    """
    从 pipeline.step_models 构建阶段模型映射。

    约束：
    - 每个阶段必须显式配置；
    - 每个阶段的值必须是 flash/pro（兼容 default/reasoning）；
    - 映射到 app_config.model 后必须存在。
    """
    raw_step_models = pipeline_config.get("step_models")
    if not isinstance(raw_step_models, dict):
        raise ValueError(
            "配置错误: pipeline.step_models 必须是对象，且需覆盖阶段: "
            + ", ".join(PIPELINE_MODEL_STEPS)
        )

    extra_steps = sorted(
        step_name for step_name in raw_step_models if step_name not in PIPELINE_MODEL_STEPS
    )
    if extra_steps:
        logging.warning(f"pipeline.step_models 存在未知阶段，将忽略: {extra_steps}")

    resolved_map: dict[str, str] = {}
    missing_steps: list[str] = []

    for step_name in PIPELINE_MODEL_STEPS:
        raw_model_type = raw_step_models.get(step_name)
        if not isinstance(raw_model_type, str):
            missing_steps.append(step_name)
            continue

        normalized_model_type = normalize_model_type_name(raw_model_type.strip().lower())
        if normalized_model_type is None:
            raise ValueError(
                f"配置错误: pipeline.step_models[{step_name!r}]={raw_model_type!r} 非法，支持值: flash/pro"
            )

        config_key = resolve_model_config_key(normalized_model_type)
        if config_key is None or config_key not in model_config:
            raise ValueError(
                f"配置错误: pipeline.step_models[{step_name!r}]={raw_model_type!r} 未命中 model 配置"
            )
        resolved_map[step_name] = normalized_model_type

    if missing_steps:
        raise ValueError(
            "配置错误: pipeline.step_models 缺少阶段配置: "
            + ", ".join(missing_steps)
        )

    return resolved_map


MODEL_MAP = build_step_model_map()
logging.info(f"阶段模型映射已生效: {MODEL_MAP}")

client = OpenAI(
    api_key=api_config["api_key"],
    base_url=api_config["base_url"],
)
semaphore = Semaphore(API_CONCURRENCY)

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

L4_REQUIRED_KEYS = tuple(LECTURE_TEX_FILE_MAP.keys())
CACHE_STATE_FILENAME = "_pipeline_cache_state.json"
PROMPT_MANAGED_STEPS = ("l1", "l2", "l3", "l4", "l4_check", "l5", "l6")

ID_DIR_PATTERN = re.compile(r"^[A-Za-z]\d{3}$")
L6_DIRNAME_FILE_PATTERN_TEMPLATE = r"^{item_id}_[a-z0-9]+(?:_[a-z0-9]+)*$"
L6_FALLBACK_SLUG = "generated_conclusion"
CURRENT_ITEM_ID: ContextVar[str] = ContextVar("CURRENT_ITEM_ID", default="-")


def normalize_reason_text(reason: Any) -> str:
    """
    Normalize error text for concise one-line logs.
    """
    text = str(reason) if reason is not None else "unknown"
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 240:
        return f"{text[:237]}..."
    return text


def log_stage_start(item_id: str, stage: str, mode: str) -> float:
    """
    Emit standardized stage start log and return a timer anchor.
    """
    logging.info("[stage/start] item=%s stage=%s mode=%s", item_id, stage, mode)
    return time.perf_counter()


def log_stage_done(
    item_id: str,
    stage: str,
    mode: str,
    started_at: float,
    note: str | None = None,
) -> None:
    """
    Emit standardized stage completion log with elapsed time.
    """
    elapsed = time.perf_counter() - started_at
    if note:
        logging.info(
            "[stage/done] item=%s stage=%s mode=%s elapsed=%.2fs note=%s",
            item_id,
            stage,
            mode,
            elapsed,
            note,
        )
        return
    logging.info(
        "[stage/done] item=%s stage=%s mode=%s elapsed=%.2fs",
        item_id,
        stage,
        mode,
        elapsed,
    )


def log_stage_fail(
    item_id: str,
    stage: str,
    mode: str,
    started_at: float,
    reason: Any,
) -> None:
    """
    Emit standardized stage failure log with elapsed time and reason.
    """
    elapsed = time.perf_counter() - started_at
    logging.error(
        "[stage/fail] item=%s stage=%s mode=%s elapsed=%.2fs reason=%s",
        item_id,
        stage,
        mode,
        elapsed,
        normalize_reason_text(reason),
    )


def compute_prompt_hash(text: str) -> str:
    """
    计算 prompt 文本指纹（SHA1）。
    """
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def build_prompt_hash_snapshot() -> dict[str, str]:
    """
    构建当前进程的 prompt 指纹快照。

    说明：
    - 每次 pipeline 启动时计算一次；
    - 任一受管阶段 prompt 变更，会导致对应缓存失效；
    - 与 --force 无关：即使不传 --force，指纹不一致也必须重跑。
    """
    snapshot: dict[str, str] = {}
    for step in PROMPT_MANAGED_STEPS:
        # 统一复用 load_prompt，避免路径解析逻辑分叉。
        text = load_prompt(step)
        snapshot[step] = compute_prompt_hash(text)
    return snapshot


PROMPT_HASH_SNAPSHOT = build_prompt_hash_snapshot()


def compute_prompt_snapshot_hash(snapshot: dict[str, str]) -> str:
    """
    计算“全量 prompt 快照”的稳定指纹。

    作用：
    - 任一阶段 prompt 发生变化时，快照指纹都会变化；
    - 可用于整条目缓存的总开关失效判定，防止下游继续复用旧结果。
    """
    payload = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return compute_prompt_hash(payload)


PROMPT_SNAPSHOT_HASH = compute_prompt_snapshot_hash(PROMPT_HASH_SNAPSHOT)


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
    retry_meta: dict[str, Any] | None = None,
    on_attempt_start: Callable[[int, int], None] | None = None,
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
        attempts_used = attempt + 1
        if on_attempt_start is not None:
            on_attempt_start(attempts_used, retries)
        try:
            result = func(*args, **kwargs)
            if retry_meta is not None:
                retry_meta["attempts"] = attempts_used
                retry_meta["retry_count"] = max(0, attempts_used - 1)
                retry_meta["retries_limit"] = retries
                retry_meta["succeeded"] = True
            return result
        except Exception as e:
            error_code = getattr(e, "code", None)
            if error_code in NON_RETRY_ERROR_CODES:
                if retry_meta is not None:
                    retry_meta["attempts"] = attempts_used
                    retry_meta["retry_count"] = max(0, attempts_used - 1)
                    retry_meta["retries_limit"] = retries
                    retry_meta["succeeded"] = False
                raise
            if attempt == retries - 1:
                if retry_meta is not None:
                    retry_meta["attempts"] = attempts_used
                    retry_meta["retry_count"] = max(0, attempts_used - 1)
                    retry_meta["retries_limit"] = retries
                    retry_meta["succeeded"] = False
                raise

            sleep_time = delay * (2**attempt) + random.random()
            logging.info(f"⚠️ Retry {attempt + 1}/{retries} after {sleep_time:.2f}s")
            time.sleep(sleep_time)


def get_model(step: str = "default") -> str:
    """
    根据阶段名返回模型名。

    Args:
        step: pipeline 阶段（l1/l2/l3/l4/l4_check/l5/l6）。

    Returns:
        str: 模型名称。
    """
    model_type = MODEL_MAP.get(step)
    if model_type is None:
        raise KeyError(
            f"未找到阶段模型配置: step={step!r}，请在 pipeline.step_models 中显式配置"
        )
    config_key = resolve_model_config_key(model_type)
    if config_key is None or config_key not in model_config:
        raise KeyError(
            f"未找到可用模型映射: step={step!r}, model_type={model_type!r}, config_key={config_key!r}"
        )
    return model_config[config_key]



def get_step_max_tokens(step: str) -> int | None:
    """
    返回阶段专用 max_tokens（未配置时返回 None）。
    """
    value = STEP_MAX_TOKENS.get(step)
    if isinstance(value, int) and value > 0:
        return value
    return None


def extract_llm_text(response: Any) -> str:
    """
    兼容不同 SDK 返回结构，提取文本内容。
    """
    choices = getattr(response, "choices", None)
    if not choices:
        return ""

    first = choices[0]
    message = getattr(first, "message", None)
    if message is None:
        return ""

    content = getattr(message, "content", None)
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for chunk in content:
            if isinstance(chunk, dict):
                text_part = chunk.get("text")
            else:
                text_part = getattr(chunk, "text", None)
            if isinstance(text_part, str) and text_part:
                parts.append(text_part)
        if parts:
            return "".join(parts)

    return ""


def now_iso_millis() -> str:
    """
    返回本地时间毫秒级 ISO 时间戳，用于请求链路打点。
    """
    return datetime.now().isoformat(timespec="milliseconds")


def serialize_prompt_payload(input_data: Any) -> str:
    """
    将 prompt 输入统一序列化为字符串。
    """
    if isinstance(input_data, str):
        return input_data
    return json.dumps(input_data, ensure_ascii=False, indent=2)


def get_payload_chars(input_data: Any) -> int:
    """
    统计输入负载字符数（非 token），用于阶段间相对对比。
    """
    return len(serialize_prompt_payload(input_data))


def log_perf_trace(step: str, metrics: dict[str, Any]) -> None:
    """
    输出统一性能追踪日志，便于后续聚合分析。
    """
    record = {
        "event": "perf_trace",
        "step": step,
        "model": metrics.get("model"),
        "prompt_chars": metrics.get("prompt_chars"),
        "payload_chars": metrics.get("payload_chars"),
        "response_chars": metrics.get("response_chars"),
        "request_start_ts": metrics.get("request_start_ts"),
        "request_end_ts": metrics.get("request_end_ts"),
        # 新主字段：LLM 往返总耗时（包含服务端推理时间）。
        "llm_roundtrip_ms": metrics.get("llm_roundtrip_ms"),
        # 兼容旧字段，避免历史分析脚本失效。
        "network_wait_ms": metrics.get("network_wait_ms"),
        "prompt_tokens": metrics.get("prompt_tokens"),
        "completion_tokens": metrics.get("completion_tokens"),
        "total_tokens": metrics.get("total_tokens"),
        "json_parse_ms": metrics.get("json_parse_ms"),
        "validate_ms": metrics.get("validate_ms"),
        "retry_count": metrics.get("retry_count"),
        "timeout_value": metrics.get("timeout_value"),
    }
    logging.info("[PERF_TRACE] %s", json.dumps(record, ensure_ascii=False))


def extract_usage_tokens(response: Any) -> dict[str, int | None]:
    """
    从响应中提取 token 使用量；SDK 对象/字典两种结构都兼容。
    """
    usage = getattr(response, "usage", None)
    if usage is None and isinstance(response, dict):
        usage = response.get("usage")

    def _pick_int(name: str) -> int | None:
        value = None
        if usage is None:
            return None
        if isinstance(usage, dict):
            value = usage.get(name)
        else:
            value = getattr(usage, name, None)
        return value if isinstance(value, int) else None

    return {
        "prompt_tokens": _pick_int("prompt_tokens"),
        "completion_tokens": _pick_int("completion_tokens"),
        "total_tokens": _pick_int("total_tokens"),
    }


def request_llm_with_progress(
    request_kwargs: dict[str, Any],
    *,
    step: str,
    model_name: str,
    attempt: int,
    retries: int,
) -> Any:
    """
    Execute one LLM request with heartbeat progress logs while waiting.
    """
    response_holder: dict[str, Any] = {}
    error_holder: dict[str, Exception] = {}

    def _request_worker() -> None:
        try:
            response_holder["response"] = client.chat.completions.create(**request_kwargs)
        except Exception as exc:
            error_holder["error"] = exc

    worker = Thread(target=_request_worker, daemon=True)
    worker.start()

    started = time.perf_counter()
    next_log_at = FIRST_PROGRESS_LOG_SECONDS
    while worker.is_alive():
        worker.join(timeout=PROGRESS_POLL_SECONDS)
        if not worker.is_alive():
            break

        elapsed = time.perf_counter() - started
        if elapsed < next_log_at:
            continue

        logging.info(
            (
                "[progress] item=%s stage=%s model=%s attempt=%d/%d "
                "retry_count=%d waited=%.1fs timeout=%ss"
            ),
            CURRENT_ITEM_ID.get(),
            step.upper(),
            model_name,
            attempt,
            retries,
            max(0, attempt - 1),
            elapsed,
            API_TIMEOUT_SECONDS,
        )
        next_log_at += PROGRESS_LOG_INTERVAL_SECONDS

    if "error" in error_holder:
        raise error_holder["error"]
    if "response" not in response_holder:
        raise RuntimeError(
            f"LLM request returned without response (step={step}, model={model_name})"
        )
    return response_holder["response"]


def call_llm(
    prompt: str,
    step: str = "default",
    payload_chars: int | None = None,
    metrics: dict[str, Any] | None = None,
) -> str:
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
        max_tokens = get_step_max_tokens(step)

        if LOG_PROMPT_STATS:
            logging.info(
                f"{step.upper()} request: model={model}, prompt_chars={len(prompt)}, max_tokens={max_tokens}"
            )

        total_llm_roundtrip_ms = 0.0
        total_retry_count = 0
        request_start_ts: str | None = None
        request_end_ts: str | None = None
        effective_model = model
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_tokens = 0
        has_usage = False

        def _run_request(
            request_model: str,
            request_max_tokens: int | None,
            request_retries: int,
        ) -> Any:
            nonlocal total_llm_roundtrip_ms, total_retry_count
            nonlocal request_start_ts, request_end_ts, effective_model
            nonlocal total_prompt_tokens, total_completion_tokens, total_tokens, has_usage

            retry_meta: dict[str, Any] = {}
            current_attempt = 1

            def _on_attempt_start(attempt_used: int, retries_limit: int) -> None:
                nonlocal current_attempt
                current_attempt = attempt_used
                if attempt_used > 1:
                    logging.info(
                        "[llm/retry] item=%s stage=%s model=%s attempt=%d/%d",
                        CURRENT_ITEM_ID.get(),
                        step.upper(),
                        request_model,
                        attempt_used,
                        retries_limit,
                    )

            def _request(request_model_name: str, request_max_tokens_inner: int | None) -> Any:
                request_kwargs: dict[str, Any] = {
                    "model": request_model_name,
                    "messages": messages,
                    "temperature": TEMPERATURE,
                    "timeout": API_TIMEOUT_SECONDS,
                }
                if request_max_tokens_inner is not None:
                    request_kwargs["max_tokens"] = request_max_tokens_inner
                return request_llm_with_progress(
                    request_kwargs,
                    step=step,
                    model_name=request_model_name,
                    attempt=current_attempt,
                    retries=request_retries,
                )

            started_iso = now_iso_millis()
            started = time.perf_counter()
            response_obj = retry_call(
                _request,
                request_model,
                request_max_tokens,
                retries=request_retries,
                retry_meta=retry_meta,
                on_attempt_start=_on_attempt_start,
            )
            elapsed_ms = (time.perf_counter() - started) * 1000
            ended_iso = now_iso_millis()

            total_llm_roundtrip_ms += elapsed_ms
            total_retry_count += int(retry_meta.get("retry_count", 0))
            if request_start_ts is None:
                request_start_ts = started_iso
            request_end_ts = ended_iso
            effective_model = request_model
            usage_tokens = extract_usage_tokens(response_obj)
            if usage_tokens["prompt_tokens"] is not None:
                has_usage = True
                total_prompt_tokens += usage_tokens["prompt_tokens"] or 0
            if usage_tokens["completion_tokens"] is not None:
                has_usage = True
                total_completion_tokens += usage_tokens["completion_tokens"] or 0
            if usage_tokens["total_tokens"] is not None:
                has_usage = True
                total_tokens += usage_tokens["total_tokens"] or 0
            return response_obj

        response = _run_request(model, max_tokens, retries)
        text = extract_llm_text(response)

        # 部分模型在 max_tokens 偏小时可能先输出 reasoning 后无正文，补一次不带 max_tokens 的重试
        if not text.strip() and max_tokens is not None:
            logging.warning(
                f"{step.upper()} empty response with max_tokens={max_tokens}, retry without max_tokens"
            )
            response = _run_request(model, None, max(1, retries))
            text = extract_llm_text(response)

        # L4 使用快模型时，少量场景可能返回空内容，自动回退 reasoning
        if step == "l4" and not text.strip():
            fallback_model = model_config.get("pro") or model_config.get("reasoning")
            if isinstance(fallback_model, str) and fallback_model and fallback_model != model:
                logging.warning(
                    f"{step.upper()} empty response with {model}, fallback to {fallback_model}"
                )
                response = _run_request(fallback_model, None, max(1, L4_RETRY_TIMES))
                text = extract_llm_text(response)

        if metrics is not None:
            metrics.update(
                {
                    "step": step,
                    "model": effective_model,
                    "prompt_chars": len(prompt),
                    "payload_chars": payload_chars,
                    "response_chars": len(text),
                    "request_start_ts": request_start_ts or now_iso_millis(),
                    "request_end_ts": request_end_ts or now_iso_millis(),
                    "llm_roundtrip_ms": round(total_llm_roundtrip_ms, 2),
                    "network_wait_ms": round(total_llm_roundtrip_ms, 2),
                    "prompt_tokens": total_prompt_tokens if has_usage else None,
                    "completion_tokens": total_completion_tokens if has_usage else None,
                    "total_tokens": total_tokens if has_usage else None,
                    "retry_count": total_retry_count,
                    "timeout_value": API_TIMEOUT_SECONDS,
                }
            )

        return text


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

    payload = serialize_prompt_payload(input_data)

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


def load_item_cache_state(state_path: str) -> dict[str, Any]:
    """
    读取单条目缓存状态文件。

    状态文件用于记录“每个阶段最后一次成功产出对应的 prompt 指纹”，
    以便在 prompt 变更后自动使缓存失效。

    Args:
        state_path: `output/<ID>/_pipeline_cache_state.json` 绝对路径。

    Returns:
        dict[str, Any]: 标准化缓存状态。
    """
    default_state = {"version": 2, "prompt_hashes": {}, "prompt_snapshot_hash": ""}
    if not os.path.isfile(state_path):
        return default_state
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return default_state
        prompt_hashes = data.get("prompt_hashes")
        if not isinstance(prompt_hashes, dict):
            prompt_hashes = {}
        clean_hashes = {
            str(k): str(v)
            for k, v in prompt_hashes.items()
            if isinstance(k, str) and isinstance(v, str)
        }
        return {
            "version": int(data.get("version", 2)),
            "prompt_hashes": clean_hashes,
            "prompt_snapshot_hash": (
                str(data.get("prompt_snapshot_hash"))
                if isinstance(data.get("prompt_snapshot_hash"), str)
                else ""
            ),
        }
    except Exception as exc:
        logging.warning(f"缓存状态文件读取失败，将忽略并重建: {state_path}, error={exc}")
        return default_state


def save_item_cache_state(state_path: str, state: dict[str, Any]) -> None:
    """
    持久化单条目缓存状态文件。
    """
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def mark_step_prompt_hash(
    cache_state: dict[str, Any],
    step: str,
) -> bool:
    """
    将当前阶段 prompt 指纹写入缓存状态。

    Returns:
        bool: 状态是否发生变化（用于决定是否落盘）。
    """
    expected = PROMPT_HASH_SNAPSHOT.get(step)
    if not expected:
        return False
    prompt_hashes = cache_state.setdefault("prompt_hashes", {})
    if not isinstance(prompt_hashes, dict):
        cache_state["prompt_hashes"] = {}
        prompt_hashes = cache_state["prompt_hashes"]
    current = prompt_hashes.get(step)
    if current == expected:
        return False
    prompt_hashes[step] = expected
    return True


def is_prompt_snapshot_fresh(
    *,
    item_id: str,
    cache_state: dict[str, Any],
) -> bool:
    """
    检查条目级 prompt 快照是否与当前运行一致。

    规则：
    - 缺失快照记录 => 视为过期（保守重跑）；
    - 快照不一致 => 视为过期（任一 prompt 已变更）；
    - 一致 => 允许按阶段级策略复用缓存。
    """
    cached = cache_state.get("prompt_snapshot_hash", "")
    if not isinstance(cached, str) or not cached:
        logging.info("%s 检测到缺失 prompt 快照记录，判定全部阶段缓存失效。", item_id)
        return False

    if cached != PROMPT_SNAPSHOT_HASH:
        logging.info(
            (
                "%s 检测到 prompt 快照变更，判定全部阶段缓存失效。"
                " cached=%s current=%s"
            ),
            item_id,
            cached[:12],
            PROMPT_SNAPSHOT_HASH[:12],
        )
        return False

    return True


def mark_prompt_snapshot_hash(cache_state: dict[str, Any]) -> bool:
    """
    将当前全量 prompt 快照指纹写入缓存状态。

    Returns:
        bool: 状态是否发生变化。
    """
    current = cache_state.get("prompt_snapshot_hash")
    if current == PROMPT_SNAPSHOT_HASH:
        return False
    cache_state["prompt_snapshot_hash"] = PROMPT_SNAPSHOT_HASH
    return True


def is_step_cache_prompt_fresh(
    *,
    item_id: str,
    step: str,
    cache_state: dict[str, Any],
) -> bool:
    """
    检查阶段缓存是否与当前 prompt 指纹一致。

    规则：
    - 无状态记录 => 视为过期（保守重跑）；
    - 指纹不一致 => 视为过期（prompt 已变更）；
    - 一致 => 允许复用缓存。
    """
    expected = PROMPT_HASH_SNAPSHOT.get(step)
    if not expected:
        # 非 prompt 管理阶段，默认视为新鲜。
        return True

    prompt_hashes = cache_state.get("prompt_hashes", {})
    if not isinstance(prompt_hashes, dict):
        prompt_hashes = {}
    cached = prompt_hashes.get(step)

    if not cached:
        logging.info(
            "%s %s 缓存无 prompt 指纹记录，判定缓存失效并重跑。",
            item_id,
            step.upper(),
        )
        return False

    if cached != expected:
        logging.info(
            (
                "%s %s prompt 已变更，缓存失效并重跑。"
                " cached=%s current=%s"
            ),
            item_id,
            step.upper(),
            cached[:12],
            expected[:12],
        )
        return False

    return True


def safe_json_parse(
    text: str | None, parse_metrics: dict[str, Any] | None = None
) -> dict[str, Any]:
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
    started = time.perf_counter()

    def _finalize(result: dict[str, Any], parse_status: str) -> dict[str, Any]:
        if parse_metrics is not None:
            parse_metrics["json_parse_ms"] = round((time.perf_counter() - started) * 1000, 2)
            parse_metrics["parse_status"] = parse_status
        return result

    if not text:
        return _finalize({"status": "empty_response"}, "empty_response")

    clean_text = text.replace("```json", "").replace("```", "").strip()
    json_candidate = extract_first_json_object(clean_text) or clean_text

    try:
        parsed = json.loads(json_candidate)
        return _finalize(normalize_control_chars(parsed), "parsed")
    except Exception as e:
        # 常见失败场景：LaTeX 反斜杠未转义，导致 Invalid \escape
        repaired = repair_invalid_json_escapes(json_candidate)
        repaired = remove_trailing_commas(repaired)
        try:
            parsed = json.loads(repaired)
            return _finalize(normalize_control_chars(parsed), "parsed_repaired")
        except Exception as e2:
            logging.warning(f"JSON 解析失败，返回原始文本。Error: {e2}")
            return _finalize(
                {"status": "parse_error", "raw": text, "error": str(e2)},
                "parse_error",
            )


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
    payload_chars = get_payload_chars(raw_json)
    prompt = render_prompt("l2", raw_json)
    perf_metrics: dict[str, Any] = {}
    result = call_llm(prompt, step="l2", payload_chars=payload_chars, metrics=perf_metrics)
    parsed = safe_json_parse(result, parse_metrics=perf_metrics)
    perf_metrics["validate_ms"] = None
    log_perf_trace("l2", perf_metrics)
    return parsed


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
    payload_chars = get_payload_chars(payload)
    prompt = render_prompt("l4", payload)
    perf_metrics: dict[str, Any] = {}
    result = call_llm(prompt, step="l4", payload_chars=payload_chars, metrics=perf_metrics)
    parsed = safe_json_parse(result, parse_metrics=perf_metrics)
    validate_started = time.perf_counter()
    validated = validate_l4_lecture_result(parsed, "l4")
    perf_metrics["validate_ms"] = round((time.perf_counter() - validate_started) * 1000, 2)
    log_perf_trace("l4", perf_metrics)
    return validated


def validate_l4_lecture_result(
    result: dict[str, Any], step_name: str
) -> dict[str, Any]:
    """
    校验 L4/L4_check 产物是否具备完整六段结构。

    Args:
        result: 当前阶段解析后的 JSON 结果。
        step_name: 阶段名（用于日志与错误定位）。

    Returns:
        dict[str, Any]:
            - 合法时原样返回；
            - 不合法时返回 invalid_output 结构。
    """
    if not isinstance(result, dict):
        return {
            "status": "invalid_output",
            "error": f"{step_name} output is not a JSON object",
            "raw": result,
        }

    missing_keys = [key for key in L4_REQUIRED_KEYS if key not in result]
    invalid_type_keys = [
        key for key in L4_REQUIRED_KEYS if key in result and not isinstance(result[key], str)
    ]

    if missing_keys or invalid_type_keys:
        details = {
            "missing_keys": missing_keys,
            "non_string_keys": invalid_type_keys,
        }
        return {
            "status": "invalid_output",
            "error": f"{step_name} output schema invalid",
            "details": details,
            "raw": result,
        }

    return result


def step_lecture_repair(
    l2_json: dict[str, Any], l3_json: dict[str, Any], l4_json: dict[str, Any]
) -> dict[str, Any]:
    """
    L4_check: 在 L4 基础上做最小修改修复。

    Args:
        l2_json: L2 输出（结论核心）。
        l3_json: L3 输出（教学评估）。
        l4_json: L4 输出（六段讲义）。

    Returns:
        dict[str, Any]: L4_check 修复后的六段讲义 JSON。
    """
    payload = build_l4_check_payload(l2_json, l3_json, l4_json)
    payload_chars = get_payload_chars(payload)
    prompt = render_prompt("l4_check", payload)
    perf_metrics: dict[str, Any] = {}
    result = call_llm(
        prompt,
        step="l4_check",
        payload_chars=payload_chars,
        metrics=perf_metrics,
    )
    parsed = safe_json_parse(result, parse_metrics=perf_metrics)
    validate_started = time.perf_counter()
    validated = validate_l4_lecture_result(parsed, "l4_check")
    perf_metrics["validate_ms"] = round((time.perf_counter() - validate_started) * 1000, 2)
    log_perf_trace("l4_check", perf_metrics)
    return validated


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


def build_l4_check_payload(
    l2: dict[str, Any], l3: dict[str, Any], l4: dict[str, Any]
) -> dict[str, Any]:
    """
    构建 L4_check 输入载荷。

    L4_check 只做“终审修复”，因此输入聚焦在：
    - L2: 原始结论与条件
    - L3: 教学价值评估
    - L4: 已生成讲义六段内容

    Args:
        l2: L2 输出。
        l3: L3 输出。
        l4: L4 输出。

    Returns:
        dict[str, Any]: 传给 L4_check 的结构化输入。
    """
    l4_blocks = {key: clip_text(l4.get(key, ""), 6000) for key in L4_REQUIRED_KEYS}

    return {
        "l2": {
            "statement": clip_text(l2.get("statement", ""), 2000),
            "latex": clip_text(l2.get("latex", ""), 3000),
            "meta": l2.get("meta", {}),
        },
        "l3": {
            "scores": l3.get("scores", {}),
            "final_score": l3.get("final_score"),
            "decision": l3.get("decision"),
            "tags": l3.get("tags", []),
            "analysis": clip_text(l3.get("analysis", ""), 1200),
        },
        "l4": l4_blocks,
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
        dict[str, str]:
            - `cache_state`: prompt 指纹缓存状态文件；
            - `l1`~`l5`/`l4_check`: 各阶段结果文件路径。
            （L6 为动态文件名，不在此映射中）
    """
    item_dir = os.path.join(output_dir, filename)
    return {
        "cache_state": os.path.join(item_dir, CACHE_STATE_FILENAME),
        "l1": os.path.join(item_dir, "l1_raw.json"),
        "l2": os.path.join(item_dir, "l2_statement.json"),
        "l3": os.path.join(item_dir, "l3_eval.json"),
        "l4": os.path.join(item_dir, "l4_lecture.json"),
        "l4_check": os.path.join(item_dir, "l4_lecture_checked.json"),
        "l5": os.path.join(item_dir, "l5_meta.json"),
    }


def save_parse_debug(
    output_dir: str,
    filename: str,
    step_name: str,
    result: dict[str, Any],
) -> None:
    """
    记录阶段异常原始内容，便于回溯模型输出问题。

    Args:
        output_dir: 输出根目录。
        filename: 输入文件名（无扩展名）。
        step_name: 阶段名（l1/l2/l3/l4/l4_check/l5）。
        result: 当前阶段返回 JSON。
    """
    status = result.get("status")
    if status not in {"parse_error", "invalid_output"}:
        return

    debug_dir = os.path.join(output_dir, filename, "debug")
    os.makedirs(debug_dir, exist_ok=True)
    debug_path = os.path.join(debug_dir, f"{step_name}_{status}.txt")
    raw = result.get("raw", "")
    err = result.get("error", "")
    details = result.get("details")
    with open(debug_path, "w", encoding="utf-8") as f:
        f.write(f"[{step_name}] {status}: {err}\n\n")
        if details is not None:
            f.write("[details]\n")
            f.write(json.dumps(details, ensure_ascii=False, indent=2))
            f.write("\n\n")
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


def build_disabled_l3_result() -> dict[str, Any]:
    """
    当 L3 被配置关闭时，提供一个稳定的占位结果，供下游流程读取。
    """
    return {
        "status": "success",
        "scores": {},
        "final_score": None,
        "decision": "disabled",
        "tags": [],
        "analysis": "L3 disabled by pipeline config",
        "confidence_score": 0.0,
    }


def build_l5_fallback_for_l6(l2: dict[str, Any], item_id: str) -> dict[str, Any]:
    """
    当 L5 被配置关闭时，为 L6 提供最小可用输入。
    """
    l2_meta = l2.get("meta", {}) if isinstance(l2.get("meta"), dict) else {}
    title = l2_meta.get("title", "")
    if not isinstance(title, str):
        title = ""
    summary = l2.get("statement", "")
    if not isinstance(summary, str):
        summary = ""
    return {
        "id": item_id,
        "module": "",
        "core": {
            "title": title,
            "summary": clip_text(summary, 160),
        },
        "search": {"keywords": []},
    }


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
    item_token = CURRENT_ITEM_ID.set(filename)

    try:
        paths_map = build_output_paths(filename, output_dir)
        item_output_dir = os.path.join(output_dir, filename)
        cache_state_path = paths_map["cache_state"]
        cache_state = load_item_cache_state(cache_state_path)
        prompt_snapshot_fresh = is_prompt_snapshot_fresh(
            item_id=filename,
            cache_state=cache_state,
        )

        def persist_step_prompt_hash(step: str) -> None:
            if mark_step_prompt_hash(cache_state, step):
                save_item_cache_state(cache_state_path, cache_state)

        def persist_prompt_snapshot_hash() -> None:
            if mark_prompt_snapshot_hash(cache_state):
                save_item_cache_state(cache_state_path, cache_state)

        def can_use_step_cache(step: str, cache_path: str) -> bool:
            if force:
                return False
            if not prompt_snapshot_fresh:
                return False
            if not file_exists(cache_path):
                return False
            return is_step_cache_prompt_fresh(
                item_id=filename,
                step=step,
                cache_state=cache_state,
            )

        if force:
            logging.info(f"{filename} 启用 --force，忽略缓存并全量重跑")

        # ========= L1 =========
        l1_mode = "cache" if can_use_step_cache("l1", paths_map["l1"]) else "run"
        l1_started = log_stage_start(filename, "L1", l1_mode)
        if l1_mode == "cache":
            l1 = load_json_file(paths_map["l1"])
            log_stage_done(filename, "L1", l1_mode, l1_started)
        else:
            raw_text = read_input_text(input_path)
            if not raw_text:
                log_stage_fail(
                    filename,
                    "L1",
                    l1_mode,
                    l1_started,
                    "input is empty or cannot be read",
                )
                return "error"
            l1 = step_latex_extract(raw_text)
            if not is_step_success(l1):
                save_parse_debug(output_dir, filename, "l1", l1)
                log_stage_fail(filename, "L1", l1_mode, l1_started, get_step_error(l1))
                return "error"
            save_json(l1, paths_map["l1"])
            persist_step_prompt_hash("l1")
            log_stage_done(filename, "L1", l1_mode, l1_started)

        # ========= L2 =========
        l2_mode = "cache" if can_use_step_cache("l2", paths_map["l2"]) else "run"
        l2_started = log_stage_start(filename, "L2", l2_mode)
        if l2_mode == "cache":
            l2 = load_json_file(paths_map["l2"])
            log_stage_done(filename, "L2", l2_mode, l2_started)
        else:
            l2 = step_statement_rewrite(l1)
            if not is_step_success(l2):
                save_parse_debug(output_dir, filename, "l2", l2)
                log_stage_fail(filename, "L2", l2_mode, l2_started, get_step_error(l2))
                return "error"
            save_json(l2, paths_map["l2"])
            persist_step_prompt_hash("l2")
            log_stage_done(filename, "L2", l2_mode, l2_started)

        # ========= L3 / L4 =========
        l3: dict[str, Any] | None = None
        l4_raw: dict[str, Any] | None = None
        l4_from_cache = False

        if ENABLE_L3:
            l3_mode = "cache" if can_use_step_cache("l3", paths_map["l3"]) else "run"
            l3_started = log_stage_start(filename, "L3", l3_mode)
            if l3_mode == "cache":
                l3 = load_json_file(paths_map["l3"])
                log_stage_done(filename, "L3", l3_mode, l3_started)
            else:
                l3 = step_quality_eval(l2)
                if not is_step_success(l3):
                    save_parse_debug(output_dir, filename, "l3", l3)
                    log_stage_fail(
                        filename,
                        "L3",
                        l3_mode,
                        l3_started,
                        get_step_error(l3),
                    )
                    return "error"
                save_json(l3, paths_map["l3"])
                persist_step_prompt_hash("l3")
                log_stage_done(filename, "L3", l3_mode, l3_started)
        else:
            l3_disabled_started = log_stage_start(filename, "L3", "disabled")
            l3 = build_disabled_l3_result()
            log_stage_done(filename, "L3", "disabled", l3_disabled_started)

        if ENABLE_L4:
            if can_use_step_cache("l4", paths_map["l4"]):
                l4_cache_started = log_stage_start(filename, "L4", "cache")
                l4_raw_cached = load_json_file(paths_map["l4"])
                l4_raw_checked = validate_l4_lecture_result(l4_raw_cached, "l4_cache")
                if is_step_success(l4_raw_checked):
                    l4_raw = l4_raw_checked
                    l4_from_cache = True
                    log_stage_done(filename, "L4", "cache", l4_cache_started)
                else:
                    log_stage_done(
                        filename,
                        "L4",
                        "cache",
                        l4_cache_started,
                        note=f"invalid_cache={get_step_error(l4_raw_checked)}",
                    )
                    logging.warning(
                        f"{filename} 检测到历史 L4 缓存结构异常，将重跑 L4: "
                        f"{get_step_error(l4_raw_checked)}"
                    )

            if l4_raw is None:
                l4_run_started = log_stage_start(filename, "L4", "run")
                l4_raw = step_lecture_generate(l2)
                if not is_step_success(l4_raw):
                    save_parse_debug(output_dir, filename, "l4", l4_raw)
                    log_stage_fail(
                        filename,
                        "L4",
                        "run",
                        l4_run_started,
                        get_step_error(l4_raw),
                    )
                    return "error"
                l4_from_cache = False
                save_json(l4_raw, paths_map["l4"])
                persist_step_prompt_hash("l4")
                log_stage_done(filename, "L4", "run", l4_run_started)
        else:
            l4_disabled_started = log_stage_start(filename, "L4", "disabled")
            log_stage_done(filename, "L4", "disabled", l4_disabled_started)

        if ENABLE_L4 and l4_raw is None:
            l4_fallback_started = log_stage_start(filename, "L4", "cache-fallback")
            l4_raw_loaded = load_json_file(paths_map["l4"])
            l4_raw = validate_l4_lecture_result(l4_raw_loaded, "l4")
            if not is_step_success(l4_raw):
                save_parse_debug(output_dir, filename, "l4", l4_raw)
                log_stage_fail(
                    filename,
                    "L4",
                    "cache-fallback",
                    l4_fallback_started,
                    get_step_error(l4_raw),
                )
                return "error"
            log_stage_done(filename, "L4", "cache-fallback", l4_fallback_started)

        # ========= L4_check =========
        l4: dict[str, Any] | None = None
        l4_check_from_cache = False
        if ENABLE_L4:
            if ENABLE_L4_CHECK:
                if can_use_step_cache("l4_check", paths_map["l4_check"]):
                    l4_check_cache_started = log_stage_start(filename, "L4_CHECK", "cache")
                    l4_cached = load_json_file(paths_map["l4_check"])
                    l4_cached_checked = validate_l4_lecture_result(
                        l4_cached, "l4_check_cache"
                    )
                    if is_step_success(l4_cached_checked):
                        l4 = l4_cached_checked
                        l4_check_from_cache = True
                        log_stage_done(
                            filename,
                            "L4_CHECK",
                            "cache",
                            l4_check_cache_started,
                        )
                    else:
                        log_stage_done(
                            filename,
                            "L4_CHECK",
                            "cache",
                            l4_check_cache_started,
                            note=f"invalid_cache={get_step_error(l4_cached_checked)}",
                        )
                        logging.warning(
                            f"{filename} 检测到历史 L4_CHECK 缓存结构异常，将重跑 L4_CHECK: "
                            f"{get_step_error(l4_cached_checked)}"
                        )

                if l4 is None:
                    l4_check_run_started = log_stage_start(filename, "L4_CHECK", "run")
                    l4 = step_lecture_repair(l2, l3, l4_raw)
                    if not is_step_success(l4):
                        save_parse_debug(output_dir, filename, "l4_check", l4)
                        log_stage_fail(
                            filename,
                            "L4_CHECK",
                            "run",
                            l4_check_run_started,
                            get_step_error(l4),
                        )
                        return "error"
                    save_json(l4, paths_map["l4_check"])
                    persist_step_prompt_hash("l4_check")
                    log_stage_done(filename, "L4_CHECK", "run", l4_check_run_started)
            else:
                l4_check_disabled_started = log_stage_start(
                    filename,
                    "L4_CHECK",
                    "disabled-use-l4",
                )
                l4 = l4_raw
                l4_check_from_cache = l4_from_cache
                log_stage_done(
                    filename,
                    "L4_CHECK",
                    "disabled-use-l4",
                    l4_check_disabled_started,
                )

            if l4 is None:
                l4_guard_started = log_stage_start(filename, "L4_CHECK", "guard")
                log_stage_fail(
                    filename,
                    "L4_CHECK",
                    "guard",
                    l4_guard_started,
                    "L4 result missing, cannot export lecture snippets",
                )
                return "error"

            l4_export_started = log_stage_start(filename, "L4_EXPORT", "run")
            export_lecture_tex_snippets(l4, filename, output_dir)
            log_stage_done(filename, "L4_EXPORT", "run", l4_export_started)
        else:
            l4_check_disabled_started = log_stage_start(filename, "L4_CHECK", "disabled")
            l4 = {}
            log_stage_done(filename, "L4_CHECK", "disabled", l4_check_disabled_started)

        # ========= L5 =========
        l5: dict[str, Any] | None = None
        l5_from_cache = False
        if ENABLE_L5:
            l5_cache_reusable = l4_check_from_cache or (not ENABLE_L4)
            if can_use_step_cache("l5", paths_map["l5"]) and l5_cache_reusable:
                l5_cache_started = log_stage_start(filename, "L5", "cache")
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
                    log_stage_done(filename, "L5", "cache", l5_cache_started)
                except Exception as e:
                    log_stage_done(
                        filename,
                        "L5",
                        "cache",
                        l5_cache_started,
                        note=f"cache_repair_failed={normalize_reason_text(e)}",
                    )
                    logging.warning(f"{filename} L5 缓存校正失败，转为重跑 L5: {e}")
            elif not force and file_exists(paths_map["l5"]) and not l5_cache_reusable:
                logging.info(f"{filename} 检测到上游变更，L5 缓存失效，转为重跑 L5")

            if l5 is None:
                l5_run_started = log_stage_start(filename, "L5", "run")
                merged = build_l5_payload(l2, l3, l4)
                l5 = step_meta_generate(merged)
                if not is_step_success(l5):
                    save_parse_debug(output_dir, filename, "l5", l5)
                    log_stage_fail(
                        filename,
                        "L5",
                        "run",
                        l5_run_started,
                        get_step_error(l5),
                    )
                    return "error"
                l5 = apply_meta_defaults(l5, filename)
                save_json(l5, paths_map["l5"])
                persist_step_prompt_hash("l5")
                log_stage_done(filename, "L5", "run", l5_run_started)
        else:
            l5_disabled_started = log_stage_start(filename, "L5", "disabled")
            l5 = build_l5_fallback_for_l6(l2, filename)
            log_stage_done(filename, "L5", "disabled", l5_disabled_started)

        # ========= L6 =========
        cached_l6 = None if force else get_cached_l6_dirname(item_output_dir, filename)
        l6_prompt_fresh = is_step_cache_prompt_fresh(
            item_id=filename,
            step="l6",
            cache_state=cache_state,
        )
        if (
            cached_l6
            and (l5_from_cache or not ENABLE_L5)
            and prompt_snapshot_fresh
            and l6_prompt_fresh
        ):
            l6_cache_skip_started = log_stage_start(filename, "L6", "cache-skip")
            log_stage_done(
                filename,
                "L6",
                "cache-skip",
                l6_cache_skip_started,
                note=f"cached={cached_l6}",
            )
            persist_prompt_snapshot_hash()
            return "skipped"

        if cached_l6:
            logging.info(f"{filename} L6 将更新缓存: {cached_l6}")

        l6_started = log_stage_start(filename, "L6", "run")
        l6_payload = build_l6_payload(filename, l2, l5)
        try:
            l6_raw = step_dirname_generate(l6_payload)
            l6_dirname = normalize_l6_dirname(filename, l6_raw)
            l6_path = save_l6_dirname_file(item_output_dir, filename, l6_dirname)
            persist_step_prompt_hash("l6")
        except Exception as exc:
            log_stage_fail(filename, "L6", "run", l6_started, exc)
            raise
        log_stage_done(
            filename,
            "L6",
            "run",
            l6_started,
            note=f"dirname={os.path.basename(l6_path)}",
        )

        persist_prompt_snapshot_hash()
        return "success"

    except Exception as e:
        logging.error(f"Error processing {filename}: {e}")
        return "error"
    finally:
        CURRENT_ITEM_ID.reset(item_token)

def run_batch(
    input_dir: str = INPUT_DIR,
    output_dir: str = OUTPUT_DIR,
    input_extensions: tuple[str, ...] = DEFAULT_INPUT_EXTENSIONS,
    target_ids: list[str] | None = None,
    force: bool = False,
) -> dict[str, int]:
    """
    批量处理输入目录中的 ID 子目录。

    Args:
        input_dir: 输入目录（例如包含 I001/I002 子目录）。
        output_dir: 输出目录。
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
    logging.info(f"开始批处理，共 {len(items)} 个条目，模式: {mode}")
    if requested_ids:
        logging.info(f"指定 ID: {', '.join(requested_ids)}")
    batch_start = time.perf_counter()

    stats = {"success": 0, "error": 0, "skipped": 0}

    with tqdm(total=len(items), desc="Processing Pipeline") as pbar:
        for item_id, source_path in items:
            try:
                result = process_file(item_id, source_path, output_dir, force)
                stats[result] += 1
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

    logging.info(
        "Pipeline 开关: enable_l3=%s, enable_l4=%s, enable_l4_check=%s, enable_l5=%s",
        ENABLE_L3,
        ENABLE_L4,
        ENABLE_L4_CHECK,
        ENABLE_L5,
    )
    prompt_hash_preview = {
        step: digest[:12] for step, digest in PROMPT_HASH_SNAPSHOT.items()
    }
    logging.info(
        "Prompt 指纹快照(前12位): %s",
        json.dumps(prompt_hash_preview, ensure_ascii=False, sort_keys=True),
    )
    logging.info("Prompt 全局快照(前12位): %s", PROMPT_SNAPSHOT_HASH[:12])
    logging.info(
        (
            "Pipeline 心跳: progress_log_start_seconds=%s, "
            "progress_log_interval_seconds=%s, progress_poll_seconds=%s, "
            "effective_first_heartbeat_seconds=%s"
        ),
        PROGRESS_LOG_START_SECONDS,
        PROGRESS_LOG_INTERVAL_SECONDS,
        PROGRESS_POLL_SECONDS,
        FIRST_PROGRESS_LOG_SECONDS,
    )

    run_batch(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        input_extensions=extensions,
        target_ids=target_ids,
        force=args.force,
    )


if __name__ == "__main__":
    main()

