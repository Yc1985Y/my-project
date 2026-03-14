#!/usr/bin/env python3
"""Qwen API 调用示例 - 对话机器人（AI 协助优化）"""

import os
import json
from typing import Optional, List, Dict

import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置
API_KEY = os.getenv("QWEN_API_KEY", "sk-028d2bfdea2b401fa163415258361972")
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
    """调用 Qwen API 进行对话（AI 协助优化）

    Args:
        message: 用户消息
        history: 对话历史列表，格式：[{"role": "user/assistant", "content": "..."}]
        max_retries: 最大重试次数

    Returns:
        AI 回复内容

    Raises:
        QwenAPIError: 当 API 调用失败时
        QwenTimeoutError: 请求超时
        QwenConnectionError: 网络连接失败
        QwenResponseError: 响应解析失败或 API 返回错误
    """
    if not API_KEY:
        raise QwenAPIError("API_KEY 未配置，请设置 QWEN_API_KEY 环境变量")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # 创建历史消息的深拷贝，避免修改原始列表（AI 协助）
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

    # 重试机制（AI 协助）
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

            # 检查 API 错误响应（AI 协助）
            if "error" in result:
                error_msg = result["error"].get("message", "未知错误")
                error_code = result["error"].get("code", "unknown")
                raise QwenResponseError(
                    f"API 错误 [{error_code}]: {error_msg}",
                    original_error=result["error"]
                )

            # 检查响应结构（AI 协助）
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
                print(f"
[重试 {attempt + 1}/{max_retries}] 请求超时，正在重试...")
                continue
            raise QwenTimeoutError("请求超时，请检查网络连接", original_error=e)

        except requests.exceptions.ConnectionError as e:
            last_error = e
            if attempt < max_retries - 1:
                print(f"
[重试 {attempt + 1}/{max_retries}] 连接失败，正在重试...")
                continue
            raise QwenConnectionError("网络连接失败，请检查网络", original_error=e)

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "未知"
            raise QwenResponseError(f"HTTP 错误 {status_code}", original_error=e)

        except json.JSONDecodeError as e:
            raise QwenResponseError(f"响应 JSON 解析失败", original_error=e)

        except KeyError as e:
            raise QwenResponseError(f"响应格式异常，缺少字段：{e}", original_error=e)

    # 所有重试都失败（AI 协助）
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
            user_input = input("
你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("
再见！")
            break

        if user_input.lower() in ["quit", "exit", "退出"]:
            print("再见！")
            break

        if not user_input:
            continue

        print("
Qwen 正在思考...", end="", flush=True)
        try:
            reply = chat_with_qwen(user_input, history)
            print(f"Qwen：{reply}")

            # 更新历史（AI 协助）
            history.extend([
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": reply}
            ])

        except QwenTimeoutError as e:
            print(f"⏱️ 超时：{e}")
        except QwenConnectionError as e:
            print(f"🌐 网络：{e}")
        except QwenResponseError as e:
            print(f"❌ 响应：{e}")
        except QwenAPIError as e:
            print(f"⚠️ 错误：{e}")


if __name__ == "__main__":
    main()
