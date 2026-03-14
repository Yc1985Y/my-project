#!/usr/bin/env python3
"""
WSGI Entry Point for Gunicorn
AI Assistant Web Application
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

# 暴露 application 对象供 Gunicorn 使用
application = app

if __name__ == "__main__":
    # 本地开发时使用 Flask 内置服务器
    from app import app
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    print(f"Starting development server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
