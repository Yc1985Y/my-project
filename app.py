#!/usr/bin/env python3
"""
AI Assistant Flask Web Application
多轮对话 | 代码生成 | 错误修复
"""
import os
import logging
from datetime import datetime
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 启用 CORS 跨域支持
CORS(app, resources={
    r"/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# 从环境变量获取配置
API_KEY = os.getenv("QWEN_API_KEY", "")
BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
MODEL = os.getenv("QWEN_MODEL", "qwen-turbo")
TIMEOUT = int(os.getenv("QWEN_TIMEOUT", "15"))
MAX_TOKENS = int(os.getenv("QWEN_MAX_TOKENS", "1024"))

# 简单的内存会话存储（生产环境建议使用 Redis）
chat_sessions = {}


def chat_with_qwen(prompt: str, history: list) -> str:
    """调用 Qwen API 进行对话"""
    import requests
    
    if not API_KEY:
        logger.error("API_KEY 未配置")
        raise ValueError("API_KEY 未配置，请设置 QWEN_API_KEY 环境变量")
    
    messages = history + [{"role": "user", "content": prompt}]
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "max_tokens": MAX_TOKENS
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=data,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        result = response.json()
        
        if "error" in result:
            error_msg = result["error"].get("message", "未知错误")
            raise ValueError(f"API 错误：{error_msg}")
        
        return result["choices"][0]["message"]["content"]
    
    except requests.exceptions.ReadTimeout:
        logger.warning("请求超时")
        return "⚠️ 请求超时，请重试一次即可~"
    except requests.exceptions.ConnectionError:
        logger.warning("网络连接失败")
        return "⚠️ 网络连接不稳定，请重试"
    except Exception as e:
        logger.error(f"请求失败：{str(e)}")
        return f"⚠️ 出错：{str(e)}"


@app.route('/')
def index():
    """首页"""
    return jsonify({
        "name": "AI Assistant API",
        "version": "1.0.0",
        "description": "多轮对话 | 代码生成 | 错误修复",
        "endpoints": {
            "chat": "/api/chat",
            "health": "/health",
            "sessions": "/api/sessions"
        }
    })


@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "model": MODEL,
        "api_configured": bool(API_KEY)
    })


@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    """
    聊天接口
    POST /api/chat
    Body: {
        "message": "用户消息",
        "session_id": "可选的会话 ID"
    }
    """
    # 处理 OPTIONS 预检请求
    if request.method == 'OPTIONS':
        response = Response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
    
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    session_id = data.get('session_id', 'default')
    
    if not message:
        return jsonify({
            "success": False,
            "error": "消息不能为空"
        }), 400
    
    # 获取或创建会话历史
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    
    history = chat_sessions[session_id]
    
    try:
        reply = chat_with_qwen(message, history)
        
        # 更新会话历史
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": reply})
        
        # 限制历史长度（最多 10 轮对话）
        if len(history) > 20:
            history = history[-20:]
        
        return jsonify({
            "success": True,
            "message": reply,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"聊天失败：{str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/chat/stream', methods=['POST', 'OPTIONS'])
def chat_stream():
    """
    流式聊天接口（SSE）
    POST /api/chat/stream
    Body: {
        "message": "用户消息",
        "session_id": "可选的会话 ID"
    }
    """
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    session_id = data.get('session_id', 'default')
    
    if not message:
        return jsonify({
            "success": False,
            "error": "消息不能为空"
        }), 400
    
    def generate():
        import requests
        
        if not API_KEY:
            yield f"data: {jsonify({'error': 'API_KEY 未配置'})}\n\n"
            return
        
        messages = chat_sessions.get(session_id, []) + [{"role": "user", "content": message}]
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": MODEL,
            "messages": messages,
            "stream": True,
            "max_tokens": MAX_TOKENS
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat/completions",
                headers=headers,
                json=data,
                timeout=TIMEOUT,
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    yield f"data: {line.decode('utf-8')}\n\n"
        
        except Exception as e:
            yield f"data: {jsonify({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/sessions/<session_id>', methods=['GET', 'OPTIONS'])
def get_session(session_id):
    """获取会话历史"""
    history = chat_sessions.get(session_id, [])
    return jsonify({
        "success": True,
        "session_id": session_id,
        "history": history,
        "message_count": len(history) // 2
    })


@app.route('/api/sessions/<session_id>', methods=['DELETE', 'OPTIONS'])
def delete_session(session_id):
    """删除会话"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    return jsonify({
        "success": True,
        "message": f"会话 {session_id} 已删除"
    })


@app.route('/api/code/generate', methods=['POST', 'OPTIONS'])
def generate_code():
    """
    代码生成接口
    POST /api/code/generate
    Body: {
        "description": "代码功能描述",
        "language": "编程语言 (可选)"
    }
    """
    data = request.get_json() or {}
    description = data.get('description', '').strip()
    language = data.get('language', 'python')
    
    if not description:
        return jsonify({
            "success": False,
            "error": "功能描述不能为空"
        }), 400
    
    prompt = f"请用{language}编写代码，实现以下功能：{description}"
    
    try:
        code = chat_with_qwen(prompt, [])
        return jsonify({
            "success": True,
            "code": code,
            "language": language,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/code/fix', methods=['POST', 'OPTIONS'])
def fix_code():
    """
    代码修复接口
    POST /api/code/fix
    Body: {
        "code": "有问题的代码",
        "error": "错误信息 (可选)",
        "language": "编程语言 (可选)"
    }
    """
    data = request.get_json() or {}
    code = data.get('code', '').strip()
    error = data.get('error', '')
    language = data.get('language', 'python')
    
    if not code:
        return jsonify({
            "success": False,
            "error": "代码不能为空"
        }), 400
    
    prompt = f"请修复以下{language}代码的错误：\n\n```{language}\n{code}\n```\n"
    if error:
        prompt += f"\n错误信息：{error}"
    
    try:
        fixed_code = chat_with_qwen(prompt, [])
        return jsonify({
            "success": True,
            "fixed_code": fixed_code,
            "language": language,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "接口不存在"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "服务器内部错误"
    }), 500


if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting AI Assistant on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
