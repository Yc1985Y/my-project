#!/usr/bin/env python3
"""AI 项目单元测试 - 测试 qwen_api.py 和 ai_assistant.py（AI 协助）"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestQwenAPI(unittest.TestCase):
    """测试 qwen_api.py 中的函数和异常处理"""

    def test_imports(self):
        """测试模块能否正常导入"""
        from qwen_api import (
            QwenAPIError, QwenTimeoutError, QwenConnectionError,
            QwenResponseError, chat_with_qwen
        )
        self.assertTrue(True)

    def test_custom_exceptions(self):
        """测试自定义异常类"""
        from qwen_api import QwenAPIError, QwenTimeoutError, QwenConnectionError, QwenResponseError

        err = QwenAPIError("测试错误")
        self.assertEqual(str(err), "测试错误")
        self.assertIsNone(err.original_error)

        original = ValueError("原始错误")
        err = QwenAPIError("包装错误", original_error=original)
        self.assertEqual(str(err), "包装错误")
        self.assertEqual(err.original_error, original)

        self.assertIsInstance(QwenTimeoutError("超时"), QwenAPIError)
        self.assertIsInstance(QwenConnectionError("连接失败"), QwenAPIError)
        self.assertIsInstance(QwenResponseError("响应错误"), QwenAPIError)

    @patch('qwen_api.API_KEY', 'test-key')
    @patch('qwen_api.requests.post')
    def test_chat_with_qwen_success(self, mock_post):
        """测试正常 API 调用"""
        from qwen_api import chat_with_qwen

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "这是 AI 的回答"}}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = chat_with_qwen("你好")
        
        self.assertEqual(result, "这是 AI 的回答")
        mock_post.assert_called_once()

    @patch('qwen_api.API_KEY', 'test-key')
    @patch('qwen_api.requests.post')
    def test_chat_with_qwen_with_history(self, mock_post):
        """测试带历史记录的对话"""
        from qwen_api import chat_with_qwen

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "基于历史的回答"}}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        history = [
            {"role": "user", "content": "之前的对话"},
            {"role": "assistant", "content": "之前的回答"}
        ]
        
        result = chat_with_qwen("新问题", history)
        
        self.assertEqual(result, "基于历史的回答")
        call_args = mock_post.call_args
        messages = call_args[1]['json']['messages']
        self.assertEqual(len(messages), 3)

    @patch('qwen_api.API_KEY', None)
    def test_chat_without_api_key(self):
        """测试未配置 API_KEY 时抛出异常"""
        from qwen_api import chat_with_qwen, QwenAPIError
        
        with self.assertRaises(QwenAPIError) as context:
            chat_with_qwen("你好")
        
        self.assertIn("API_KEY 未配置", str(context.exception))

    @patch('qwen_api.API_KEY', 'test-key')
    @patch('qwen_api.requests.post')
    def test_chat_timeout_error(self, mock_post):
        """测试超时异常处理"""
        from qwen_api import chat_with_qwen, QwenTimeoutError
        import requests

        mock_post.side_effect = requests.exceptions.Timeout()

        with self.assertRaises(QwenTimeoutError):
            chat_with_qwen("你好", max_retries=1)

    @patch('qwen_api.API_KEY', 'test-key')
    @patch('qwen_api.requests.post')
    def test_chat_connection_error(self, mock_post):
        """测试连接异常处理"""
        from qwen_api import chat_with_qwen, QwenConnectionError
        import requests

        mock_post.side_effect = requests.exceptions.ConnectionError()

        with self.assertRaises(QwenConnectionError):
            chat_with_qwen("你好", max_retries=1)

    @patch('qwen_api.API_KEY', 'test-key')
    @patch('qwen_api.requests.post')
    def test_chat_http_error(self, mock_post):
        """测试 HTTP 错误处理"""
        from qwen_api import chat_with_qwen, QwenResponseError
        import requests

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.side_effect = requests.exceptions.HTTPError(response=mock_response)

        with self.assertRaises(QwenResponseError):
            chat_with_qwen("你好", max_retries=1)

    @patch('qwen_api.API_KEY', 'test-key')
    @patch('qwen_api.requests.post')
    def test_chat_api_error_response(self, mock_post):
        """测试 API 返回错误时的处理"""
        from qwen_api import chat_with_qwen, QwenResponseError

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": {"code": "invalid_request", "message": "无效请求"}
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        with self.assertRaises(QwenResponseError) as context:
            chat_with_qwen("你好", max_retries=1)
        
        self.assertIn("API 错误", str(context.exception))

    @patch('qwen_api.API_KEY', 'test-key')
    @patch('qwen_api.requests.post')
    def test_chat_empty_choices(self, mock_post):
        """测试 API 返回空 choices 时的处理"""
        from qwen_api import chat_with_qwen, QwenResponseError

        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": []}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        with self.assertRaises(QwenResponseError):
            chat_with_qwen("你好", max_retries=1)

    @patch('qwen_api.API_KEY', 'test-key')
    @patch('qwen_api.requests.post')
    def test_chat_empty_content(self, mock_post):
        """测试 API 返回空内容时的处理"""
        from qwen_api import chat_with_qwen, QwenResponseError

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": ""}}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        with self.assertRaises(QwenResponseError):
            chat_with_qwen("你好", max_retries=1)


class TestAIAssistant(unittest.TestCase):
    """测试 ai_assistant.py 中的对话函数"""

    def test_imports(self):
        """测试模块能否正常导入"""
        from ai_assistant import chat, main
        self.assertTrue(True)

    @patch('ai_assistant.API_KEY', 'test-key')
    @patch('ai_assistant.requests.post')
    def test_chat_success(self, mock_post):
        """测试正常对话"""
        from ai_assistant import chat

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "AI 助手的回答"}}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        history = [{"role": "user", "content": "你好"}]
        result = chat("你好", history)
        
        self.assertEqual(result, "AI 助手的回答")
        mock_post.assert_called_once()

    @patch('ai_assistant.API_KEY', 'test-key')
    @patch('ai_assistant.requests.post')
    def test_chat_with_empty_history(self, mock_post):
        """测试空历史记录"""
        from ai_assistant import chat

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "回答"}}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = chat("第一个问题", [])
        
        self.assertEqual(result, "回答")
        call_args = mock_post.call_args
        messages = call_args[1]['json']['messages']
        self.assertEqual(len(messages), 1)

    @patch('ai_assistant.API_KEY', 'test-key')
    @patch('ai_assistant.requests.post')
    def test_chat_timeout_returns_message(self, mock_post):
        """测试超时返回友好提示"""
        from ai_assistant import chat
        import requests

        mock_post.side_effect = requests.exceptions.ReadTimeout()

        result = chat("你好", [])
        
        self.assertIn("超时", result)
        self.assertIn("⚠️", result)

    @patch('ai_assistant.API_KEY', 'test-key')
    @patch('ai_assistant.requests.post')
    def test_chat_connection_error_returns_message(self, mock_post):
        """测试连接错误返回友好提示"""
        from ai_assistant import chat
        import requests

        mock_post.side_effect = requests.exceptions.ConnectionError()

        result = chat("你好", [])
        
        self.assertIn("网络", result)
        self.assertIn("⚠️", result)

    @patch('ai_assistant.API_KEY', 'test-key')
    @patch('ai_assistant.requests.post')
    def test_chat_generic_error_returns_message(self, mock_post):
        """测试通用错误返回错误信息"""
        from ai_assistant import chat

        mock_post.side_effect = Exception("未知错误")

        result = chat("你好", [])
        
        self.assertIn("出错", result)
        self.assertIn("未知错误", result)

    @patch('ai_assistant.API_KEY', 'test-key')
    @patch('ai_assistant.requests.post')
    def test_chat_request_payload(self, mock_post):
        """测试请求参数正确"""
        from ai_assistant import chat

        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "ok"}}]}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        history = [{"role": "user", "content": "历史"}]
        chat("新问题", history)

        call_args = mock_post.call_args
        data = call_args[1]['json']
        
        self.assertEqual(data['model'], 'qwen-turbo')
        self.assertEqual(data['stream'], False)
        self.assertEqual(data['max_tokens'], 1024)
        self.assertEqual(len(data['messages']), 2)

    @patch('ai_assistant.API_KEY', None)
    @patch('ai_assistant.requests.post')
    def test_chat_without_api_key(self, mock_post):
        """测试未配置 API_KEY 时的错误处理"""
        from ai_assistant import chat

        mock_post.side_effect = Exception("Authorization failed")

        result = chat("你好", [])
        
        self.assertIn("出错", result)


class TestIntegration(unittest.TestCase):
    """集成测试 - 测试模块间协作"""

    @patch('qwen_api.API_KEY', 'test-key')
    @patch('qwen_api.requests.post')
    def test_multi_turn_conversation_simulation(self, mock_post):
        """模拟多轮对话场景"""
        from qwen_api import chat_with_qwen

        responses = [
            {"choices": [{"message": {"content": "回答 1"}}]},
            {"choices": [{"message": {"content": "回答 2"}}]},
            {"choices": [{"message": {"content": "回答 3"}}]},
        ]
        
        mock_response = MagicMock()
        mock_response.json.side_effect = responses
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        history = []
        
        reply1 = chat_with_qwen("问题 1", history)
        self.assertEqual(reply1, "回答 1")
        history.extend([
            {"role": "user", "content": "问题 1"},
            {"role": "assistant", "content": reply1}
        ])

        reply2 = chat_with_qwen("问题 2", history)
        self.assertEqual(reply2, "回答 2")
        
        reply3 = chat_with_qwen("问题 3", history)
        self.assertEqual(reply3, "回答 3")

        self.assertEqual(mock_post.call_count, 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
