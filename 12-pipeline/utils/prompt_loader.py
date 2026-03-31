import os
from config.config_loader import get_paths, get_prompts_config

paths = get_paths()
prompts_config = get_prompts_config()

PROMPT_DIR = paths["prompt_dir"]
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_prompt(step):
    """
    根据 step 自动加载 prompt
    """
    filename = prompts_config.get(step)

    if not filename:
        raise ValueError(f"❌ 未配置 prompt: {step}")

    path = os.path.join(BASE_DIR, PROMPT_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Prompt 文件不存在: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return f.read()
