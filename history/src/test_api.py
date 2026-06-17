"""
API 连接测试脚本
运行这个脚本来验证你的 DeepSeek API Key 是否配置正确。
用法：在项目目录下打开 PowerShell，输入 python src/test_api.py
"""

import json
import sys
from pathlib import Path


def main():
    print("=" * 50)
    print("  公文校对助手 — API 连接测试")
    print("=" * 50)
    print()

    # 1. 读取配置文件
    config_path = Path(__file__).parent.parent / "config.json"
    print(f"📂 读取配置文件: {config_path}")

    if not config_path.exists():
        print("❌ 找不到 config.json 文件！")
        print(f"   请确认文件存在于: {config_path}")
        sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        print("✅ 配置文件读取成功")
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件格式错误: {e}")
        print("   请检查 config.json 中的 JSON 格式是否正确")
        sys.exit(1)

    # 2. 检查 API Key
    api_key = config.get("api_key", "")
    if not api_key or api_key == "在此填入你的DeepSeek-API-Key":
        print()
        print("⚠️  尚未配置 API Key！")
        print()
        print("   请按以下步骤操作：")
        print("   1. 打开浏览器，访问 https://platform.deepseek.com/")
        print("   2. 注册并登录账号")
        print("   3. 进入「API Keys」页面，创建一个新的 API Key")
        print("   4. 复制生成的密钥（以 sk- 开头）")
        print("   5. 用记事本打开 config.json，将密钥粘贴到 api_key 字段")
        print("   6. 保存 config.json 后重新运行本脚本")
        sys.exit(1)

    print(f"✅ API Key 已配置 ({api_key[:10]}...)")

    # 3. 测试网络连接
    api_url = config.get("api_url", "https://api.deepseek.com/v1/chat/completions")
    model = config.get("model", "deepseek-chat")

    print()
    print(f"🌐 测试连接: {api_url}")
    print(f"🧠 使用模型: {model}")
    print()
    print("⏳ 正在发送测试请求...")

    try:
        import requests
    except ImportError:
        print()
        print("❌ 缺少 requests 库！")
        print()
        print("   请在 PowerShell 中运行以下命令安装：")
        print("   pip install requests")
        sys.exit(1)

    try:
        response = requests.post(
            api_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个测试助手，请用中文回答。"
                    },
                    {
                        "role": "user",
                        "content": "请回复：'连接成功！API 测试通过。'"
                    }
                ],
                "max_tokens": 50,
                "temperature": 0.0,
            },
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            reply = data["choices"][0]["message"]["content"].strip()
            print()
            print(f"🤖 AI 回复: {reply}")
            print()
            print("=" * 50)
            print("  ✅ 测试全部通过！环境搭建完成！")
            print("=" * 50)
            print()
            print("👉 下一步：运行 python src/app.py 启动应用")
        elif response.status_code == 401:
            print()
            print("❌ API Key 认证失败 (HTTP 401)")
            print()
            print("   可能的原因：")
            print("   1. API Key 填写错误（请检查是否有多余空格）")
            print("   2. API Key 已被删除或过期")
            print("   3. 账号余额不足")
            print()
            print("   请重新获取 API Key 并更新 config.json")
        elif response.status_code == 429:
            print()
            print("❌ 请求频率超限 (HTTP 429)")
            print("   请稍等片刻后重试")
        else:
            print()
            print(f"❌ API 返回错误 (HTTP {response.status_code})")
            print(f"   详细信息: {response.text[:500]}")

    except requests.exceptions.ConnectionError:
        print()
        print("❌ 网络连接失败！")
        print("   请检查：")
        print("   1. 电脑是否已连接互联网")
        print("   2. 是否需要配置代理/VPN")
        print("   3. 防火墙是否阻止了连接")
    except requests.exceptions.Timeout:
        print()
        print("❌ 请求超时（超过 30 秒）")
        print("   请检查网络连接后重试")
    except Exception as e:
        print()
        print(f"❌ 未知错误: {e}")


if __name__ == "__main__":
    main()
