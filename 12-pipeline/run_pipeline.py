import os
import json
import base64
import time
import random
import logging
import re
from tqdm import tqdm
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from threading import Semaphore

# 配置日志（同时输出到文件和控制台）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

# 并发控制（防止 API 限流）
semaphore = Semaphore(3)
# =========================
# 🔑 配置
# =========================

from config.config_loader import (
    get_api_config,
    get_model_config,
    get_paths,
    get_performance,
)

api_config = get_api_config()
model_config = get_model_config()
paths = get_paths()
perf = get_performance()

# client = OpenAI(api_key=api_config["api_key"], base_url=api_config["base_url"])

MODEL = model_config["default"]

TEMPERATURE = perf["temperature"]
MAX_WORKERS = perf["max_workers"]
RETRY_TIMES = perf["retry_times"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, paths["input_dir"])
OUTPUT_DIR = os.path.join(BASE_DIR, paths["output_dir"])
logging.FileHandler(os.path.join(BASE_DIR, "pipeline.log"))

# =========================
# 🧠 工具函数
# =========================
# 步骤与模型映射
MODEL_MAP = {
    "l1": "default",
    "l2": "reasoning",
    "l3": "default",
    "l4": "reasoning",
    "l5": "default",
}


def retry_call(func, *args, retries=3, delay=1, **kwargs):
    """带指数退避的重试装饰器"""
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 最后一次尝试失败
            error_code = getattr(e, "code", None)
            # 对于某些错误类型不进行重试
            if error_code in [
                "invalid_api_key",
                "model_not_found",
                "insufficient_quota",
            ]:
                raise e
            if attempt == retries - 1:
                raise e
            sleep_time = delay * (2**attempt) + random.random()
            logging.info(f"⚠️ Retry {attempt+1}/{retries} after {sleep_time:.2f}s")
            time.sleep(sleep_time)


def get_model(step="default"):
    """根据步骤返回模型名称"""
    model_type = MODEL_MAP.get(step, "default")
    return model_config[model_type]


def encode_image(image_path):
    """将图片编码为 base64"""
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        logging.error(f"图片编码失败: {image_path}, Error: {e}")
        return None


def call_llm(prompt, step="default", image_base64=None):
    """
    通用调用函数（支持图像 + 动态模型）

    :param prompt: 输入prompt
    :param step: pipeline阶段（l1/l2/l3/l4/l5）
    :param image_base64: 可选图片
    """
    with semaphore:
        # ✅ 动态选择模型
        model = get_model(step)

        messages = []

        if image_base64:
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}",
                            },
                        },
                    ],
                }
            )
        else:
            messages.append({"role": "user", "content": prompt})

        def _request():
            local_client = OpenAI(
                api_key=api_config["api_key"], base_url=api_config["base_url"]
            )
            return local_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=TEMPERATURE,
            )

        response = retry_call(_request, retries=RETRY_TIMES)
        return response.choices[0].message.content


def save_json(data, path):
    """保存 JSON 文件，自动创建目录"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def safe_json_parse(text):
    """
    增强版 JSON 解析，处理 Markdown 代码块和脏数据
    """
    if not text:
        return {"status": "empty_response"}

    # 尝试去除 Markdown 格式
    clean_text = text.replace("```json", "").replace("```", "").strip()

    try:
        # 寻找第一个 { 和最后一个 }
        start = clean_text.find("{")
        end = clean_text.rfind("}") + 1
        match = re.search(r"\{.*\}", clean_text, re.S)
        if match:
            return json.loads(match.group())
        return json.loads(clean_text)
    except Exception as e:
        logging.warning(f"JSON 解析失败，返回原始文本。Error: {e}")
        return {"status": "parse_error", "raw": text}


# =========================
# 🧱 Pipeline步骤
# =========================

from utils.prompt_loader import load_prompt


def step_ocr_extract(image_path):
    """L1: OCR + 结构化修复"""
    prompt = load_prompt("l1")
    img = encode_image(image_path)
    if img is None:
        return {"status": "image_encode_error", "error": "无法编码图片"}
    result = call_llm(prompt, step="l1", image_base64=img)
    return safe_json_parse(result)


def step_statement_rewrite(raw_json):
    """L2: 结论重构"""
    prompt = load_prompt("l2")
    prompt = prompt.replace("{{input}}", json.dumps(raw_json, ensure_ascii=False))

    result = call_llm(prompt, step="l2")
    return safe_json_parse(result)


def step_quality_eval(l2_json):
    """L3: 教学评估"""
    prompt = load_prompt("l3")
    prompt = prompt.replace("{{input}}", json.dumps(l2_json, ensure_ascii=False))

    result = call_llm(prompt, step="l3")
    return safe_json_parse(result)


def step_lecture_generate(l2_json):
    """L4: 讲义生成"""
    prompt = load_prompt("l4")
    prompt = prompt.replace("{{input}}", json.dumps(l2_json, ensure_ascii=False))

    result = call_llm(prompt, step="l4")
    return safe_json_parse(result)


def step_meta_generate(all_data):
    """L5: 最终 meta.json 生成"""
    prompt = load_prompt("l5")
    prompt = prompt.replace("{{input}}", json.dumps(all_data, ensure_ascii=False))

    result = call_llm(prompt, step="l5")
    return safe_json_parse(result)


# =========================
# 🔄 单文件处理
# =========================


def file_exists(path):
    """检查文件是否存在且非空"""
    return os.path.exists(path) and os.path.getsize(path) > 10


def process_file(image_path):
    """处理单个图片文件，返回状态字符串: 'success', 'error', 'skipped'"""
    filename = os.path.splitext(os.path.basename(image_path))[0]

    try:
        paths_map = {
            "l1": f"{OUTPUT_DIR}/raw/{filename}.json",
            "l2": f"{OUTPUT_DIR}/statement/{filename}.json",
            "l3": f"{OUTPUT_DIR}/eval/{filename}.json",
            "l4": f"{OUTPUT_DIR}/lecture/{filename}.json",
            "l5": f"{OUTPUT_DIR}/meta/{filename}.json",
        }

        # ========= L1 =========
        if file_exists(paths_map["l1"]):
            l1 = json.load(open(paths_map["l1"], encoding="utf-8"))
        else:
            l1 = step_ocr_extract(image_path)
            if l1.get("status") not in ("success", None):
                logging.error(f"{filename} L1 失败: {l1.get('error')}")
                return "error"
            save_json(l1, paths_map["l1"])

        # ========= L2 =========
        if file_exists(paths_map["l2"]):
            l2 = json.load(open(paths_map["l2"], encoding="utf-8"))
        else:
            l2 = step_statement_rewrite(l1)
            if l2.get("status") not in ("success", None):
                logging.error(f"{filename} L2 失败: {l2.get('error')}")
                return "error"
            save_json(l2, paths_map["l2"])

        # ========= L3 =========
        if file_exists(paths_map["l3"]):
            l3 = json.load(open(paths_map["l3"], encoding="utf-8"))
        else:
            l3 = step_quality_eval(l2)
            if l3.get("status") not in ("success", None):
                logging.error(f"{filename} L3 失败: {l3.get('error')}")
                return "error"
            save_json(l3, paths_map["l3"])

        # ========= L4 =========
        if file_exists(paths_map["l4"]):
            l4 = json.load(open(paths_map["l4"], encoding="utf-8"))
        else:
            l4 = step_lecture_generate(l2)
            if l4.get("status") not in ("success", None):
                logging.error(f"{filename} L4 失败: {l4.get('error')}")
                return "error"
            save_json(l4, paths_map["l4"])

        # ========= L5 =========
        if file_exists(paths_map["l5"]):
            logging.info(f"{filename} 已处理，跳过 L5")
            return "skipped"

        merged = {"l2": l2, "l3": l3, "l4": l4}
        l5 = step_meta_generate(merged)
        if l5.get("status") not in ("success", None):
            logging.error(f"{filename} L5 失败: {l5.get('error')}")
            return "error"
        save_json(l5, paths_map["l5"])

        return "success"

    except Exception as e:
        logging.error(f"❌ Error processing {filename}: {e}")
        return "error"


# =========================
# 🚀 批处理入口
# =========================


def run_batch():
    """批量处理输入目录中的所有图片"""
    if not os.path.exists(INPUT_DIR):
        logging.error(f"输入目录不存在: {INPUT_DIR}")
        return
    files = [
        os.path.join(INPUT_DIR, f)
        for f in os.listdir(INPUT_DIR)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]
    if not files:
        logging.warning("未找到待处理文件。")
        return
    logging.info(f"开始批处理，共 {len(files)} 个文件，并发数 {MAX_WORKERS}")
    stats = {"success": 0, "error": 0, "skipped": 0}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 提交任务
        future_to_file = {executor.submit(process_file, f): f for f in files}

        # 使用 tqdm 显示进度条
        with tqdm(total=len(files), desc="Processing Pipeline") as pbar:
            TIMEOUT = 60
            for future in as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    # 超时控制, 阻塞等待线程结果的地方
                    result = future.result(timeout=TIMEOUT)
                    stats[result] += 1
                except TimeoutError:
                    logging.error(f"{file} 超时（>{TIMEOUT}s）")
                    stats["error"] += 1
                except Exception as e:
                    logging.error(f"{file} 任务异常: {e}")
                    stats["error"] += 1
                pbar.set_postfix(stats)
                pbar.update(1)

    logging.info(f"\n✅ 任务结束: {stats}")


if __name__ == "__main__":
    run_batch()
