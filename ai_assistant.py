#!/usr/bin/env python3
# 任务9：AI助手应用（已修复超时）
# 多轮对话 | 代码生成 | 错误修复
from dotenv import load_dotenv
import os
import requests

load_dotenv()

API_KEY = os.getenv("QWEN_API_KEY")
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL = "qwen-turbo"  # 改用更快更稳的模型

def chat(prompt, history):
    messages = history + [{"role": "user", "content": prompt}]
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "max_tokens": 1024
    }

    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=data,
            timeout=15
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    
    except requests.exceptions.ReadTimeout:
        return "⚠️ 请求超时，请重试一次即可~"
    except requests.exceptions.ConnectionError:
        return "⚠️ 网络连接不稳定，请重试"
    except Exception as e:
        return f"⚠️ 出错：{str(e)}"

def main():
    print("=" * 60)
    print("🤖 任务9：AI助手（多轮对话 | 代码生成 | 错误修复）")
    print("=" * 60)
    history = []
    
    while True:
        user = input("\n你：").strip()
        if user.lower() in ["quit", "exit", "q"]:
            print("👋 再见！")
            break
        
        print("AI助手正在思考...")
        reply = chat(user, history)
        print(f"AI助手：{reply}")
        
        history.append({"role": "user", "content": user})
        history.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()
