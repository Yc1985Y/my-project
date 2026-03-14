#!/usr/bin/env python3
"""Qwen API 调用示例 - 对话机器人（AI 协助优化）"""

import os
import json
from typing import Optional, List, Dict

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("QWEN_API_KEY")
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL = "qwen3.5-plus"
TIMEOUT = 30
MAX_TOKENS = 2048
MAX_RETRIES = 3


class QwenAPIError(Exception):
    """自定义 API 异常基类（AI 协助）"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error


class QwenTimeoutError(QwenAPIError):
    """请求超时异常（AI 协助）"""
    pass


class QwenConnectionError(QwenAPIError):
    """网络连接异常（AI 协助）"""
    pass


class QwenResponseError(QwenAPIError):
    """API 响应异常（AI 协助）"""
    pass


def chat_with_qwen(
    message: str,
    history: Optional[List[Dict[str, str]]] = None,
    max_retries: int = MAX_RETRIES
) -> str:
    """调用 Qwen API 进行对话（AI 协助优化）"""
    if not API_KEY:
        raise QwenAPIError("API_KEY 未配置，请设置 QWEN_API_KEY 环境变量")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    messages = []
    if history:
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "max_tokens": MAX_TOKENS
    }

    last_error: Optional[Exception] = None
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=TIMEOUT
            )
            response.raise_for_status()
            result = response.json()

            if "error" in result:
                error_msg = result["error"].get("message", "未知错误")
                error_code = result["error"].get("code", "unknown")
                raise QwenResponseError(
                    f"API 错误 [{error_code}]: {error_msg}",
                    original_error=result["error"]
                )

            if not result.get("choices"):
                raise QwenResponseError("API 返回空响应，无 choices 字段")

            if not result["choices"][0].get("message"):
                raise QwenResponseError("API 返回的消息格式不正确")

            content = result["choices"][0]["message"].get("content", "")
            if not content:
                raise QwenResponseError("API 返回空内容")

            return content

        except requests.exceptions.Timeout as e:
            last_error = e
            if attempt < max_retries - 1:
                print(f"\n[重试 {attempt + 1}/{max_retries}] 请求超时，正在重试...")
                continue
            raise QwenTimeoutError("请求超时，请检查网络连接", original_error=e)

        except requests.exceptions.ConnectionError as e:
            last_error = e
            if attempt < max_retries - 1:
                print(f"\n[重试 {attempt + 1}/{max_retries}] 连接失败，正在重试...")
                continue
            raise QwenConnectionError("网络连接失败，请检查网络", original_error=e)

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "未知"
            raise QwenResponseError(f"HTTP 错误 {status_code}", original_error=e)

        except json.JSONDecodeError as e:
            raise QwenResponseError(f"响应 JSON 解析失败", original_error=e)

        except KeyError as e:
            raise QwenResponseError(f"响应格式异常，缺少字段：{e}", original_error=e)

    raise QwenAPIError(
        f"请求失败，已重试 {max_retries} 次",
        original_error=last_error
    )


def main():
    """主函数 - 交互式对话（AI 协助）"""
    print("=" * 50)
    print("Qwen 对话机器人（输入 'quit' 退出）")
    print("=" * 50)

    history: List[Dict[str, str]] = []

    while True:
        try:
            user_input = input("\n你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if user_input.lower() in ["quit", "exit", "退出"]:
            print("再见！")
            break

        if not user_input:
            continue

        print("\nQwen 正在思考...", end="", flush=True)
        try:
            reply = chat_with_qwen(user_input, history)
            print(f"\rQwen：{reply}")

            history.extend([
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": reply}
            ])

        except QwenTimeoutError as e:
            print(f"\r⏱️ 超时：{e}")
        except QwenConnectionError as e:
            print(f"\r🌐 网络：{e}")
        except QwenResponseError as e:
            print(f"\r❌ 响应：{e}")
        except QwenAPIError as e:
            print(f"\r⚠️ 错误：{e}")


if __name__ == "__main__":
    main()
