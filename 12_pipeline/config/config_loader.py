import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# 加载配置
# =========================

APP_CONFIG = load_json(os.path.join(BASE_DIR, "config/app_config.json"))
TAXONOMY_NODES = load_json(os.path.join(BASE_DIR, "config/taxonomy_nodes.json"))


# =========================
# 提供快捷访问方法
# =========================


def get_api_config():
    return APP_CONFIG["api"]


def get_model_config():
    return APP_CONFIG["model"]


def get_paths():
    return APP_CONFIG["paths"]


def get_performance():
    return APP_CONFIG["performance"]


def get_prompts_config():
    return APP_CONFIG["prompts"]
