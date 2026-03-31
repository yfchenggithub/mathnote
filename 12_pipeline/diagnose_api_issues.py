from openai import OpenAI
import requests
import time
import openai
import os
from config.config_loader import (
    get_api_config,
)

api_config = get_api_config()
api_key = api_config["api_key"]


def diagnose_api_issues():
    """诊断 API 配置问题"""
    print("🔍 开始诊断 API 配置...")

    # 检查密钥格式
    if not api_key.startswith("sk-"):
        print("❌ API 密钥格式错误，应以 'sk-' 开头")
        return
    # 官网过时的内容，35应该是正确的长度，因为可以获取到两个模型
    # if len(api_key) != 51:
    #     print(f"❌ API 密钥长度错误，当前长度: {len(api_key)}，应为 51")
    #     return

    print("✅ API 密钥格式正确")

    # 测试 API 连接
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

        # 测试模型列表
        # deepseek-chat: DeepSeek-V3.2-Exp 的非思考模式
        # deepseek-reasoner: DeepSeek-V3.2-Exp 的思考模式
        # 目前好像就只提供这两个model
        models = client.models.list()
        print("✅ API 连接正常")
        print(f"✅ 可用模型数量: {len(models.data)}")
        for model in models.data:
            print(f"模型ID: {model.id}")
            print(f"创建时间: {model.created}")
            print(f"所有者: {model.owned_by}")
            print("---")

        # 测试简单请求
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1,
        )
        print("✅ API 调用成功")

    except Exception as e:
        print(f"❌ API 调用失败: {e}")


def test_network_connectivity():
    """测试网络连接"""
    endpoints = ["https://api.deepseek.com", "https://api.deepseek.com/v1/models"]

    for endpoint in endpoints:
        try:
            start_time = time.time()
            response = requests.get(endpoint, timeout=10)
            end_time = time.time()
            # API 密钥无效或缺失
            print(
                f"✅测试网络连接成功  {endpoint}: {response.status_code} ({end_time - start_time:.2f}s)"
            )
        except Exception as e:
            print(f"❌ {endpoint}: {e}")


def test_api_key():
    try:
        client = openai.OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="http://ai.sankotrade.com"
        )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1,
        )

        print("✅ API 密钥有效")
        return True

    except openai.AuthenticationError:
        print("❌ API 密钥无效")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False


def check_model_status():
    """检查模型可用性"""
    models = [
        "deepseek-chat",
        "deepseek-reasoner",
        "deepseek-coder",
        "deepseek-v2",
        "deepseek-yfcheng",
        "invalid_model",
    ]
    # deepseek-yfcheng 日志显示可用，明显是错的
    client = openai.OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="http://ai.sankotrade.com"
    )
    for model in models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
            )
            print(f"✅ {model}: 可用")
        except Exception as e:
            print(f"❌ {model}: 不可用 - {e}")


if __name__ == "__main__":
    diagnose_api_issues()
    test_network_connectivity()
    test_api_key()
    check_model_status()
