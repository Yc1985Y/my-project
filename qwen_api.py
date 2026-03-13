# 修复API版本兼容问题
#!/usr/bin/env python3
...
#!/usr/bin/env python3
"""Qwen API 调用示例 - 对话机器人"""
import requests
import json

# 配置（已填入你的API Key）
API_KEY = "sk-028d2bfdea2b401fa163415258361972"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL = "qwen3.5-plus"

def chat_with_qwen(message, history=None):
    """调用 Qwen API 进行对话   
    Args:       
        message: 用户消息       
        history: 对话历史列表   
    Returns:       
        AI 回复内容   
    """
    # 构建请求头
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # 构建消息列表
    messages = history or []
    messages.append({"role": "user", "content": message})
    
    # 构建请求体
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "max_tokens": 2048
    }

    try:
        # 发送请求
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        assistant_message = result["choices"][0]["message"]["content"]
        return assistant_message
    
    except requests.exceptions.RequestException as e:
        return f"请求失败：{e}"

def main():
    """主函数 - 交互式对话"""
    print("="*50)
    print("Qwen 对话机器人（输入 'quit' 退出）")
    print("="*50)
    history = []
    
    while True:
        # 获取用户输入
        user_input = input("\n你：").strip()
        if user_input.lower() in ["quit", "exit", "退出"]:
            print("再见！")
            break
        if not user_input:
            continue
        
        # 调用 API
        print("\nQwen 正在思考...", end="")
        reply = chat_with_qwen(user_input, history.copy())
        
        # 显示回复
        print(f"\n\nQwen：{reply}")
        
        # 更新对话历史
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()
# AI协助修复：兼容Python3.8 + requests库
