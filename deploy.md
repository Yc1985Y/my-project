# AI Assistant 部署文档

完整的云平台/服务器部署指南，支持本地运行、服务器部署、云平台一键部署。

---

## 📁 项目结构

```
my-project/
├── app.py              # Flask Web 应用主程序
├── wsgi.py             # Gunicorn 入口文件
├── ai_assistant.py     # AI 助手核心模块
├── qwen_api.py         # Qwen API 调用模块
├── requirements.txt    # Python 依赖
├── start.sh            # 一键启动脚本
├── .env.example        # 环境变量模板
├── .env                # 环境变量配置 (需自行创建，已加入 .gitignore)
├── .gitignore          # Git 忽略规则
└── deploy.md           # 本部署文档
```

---

## 🔧 环境要求

- Python 3.8+
- pip 包管理器
- 通义千问 API Key

---

## 📦 快速开始

### 1. 克隆项目

```bash
cd /home/yc/my-project
```

### 2. 创建虚拟环境 (推荐)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
# QWEN_API_KEY=sk-your-actual-api-key
```

### 5. 启动服务

```bash
# 开发模式
./start.sh

# 生产模式
./start.sh -m prod

# 自定义端口和进程数
./start.sh -m prod -p 8080 -w 4
```

---

## 🌐 API 接口

### 基础信息

| 接口 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 首页，显示 API 信息 |
| `/health` | GET | 健康检查 |

### 聊天接口

#### POST /api/chat

多轮对话接口

**请求示例:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，请介绍一下自己", "session_id": "user123"}'
```

**响应示例:**
```json
{
  "success": true,
  "message": "你好！我是 AI 助手...",
  "session_id": "user123",
  "timestamp": "2024-01-01T12:00:00"
}
```

### 代码生成接口

#### POST /api/code/generate

根据描述生成代码

**请求示例:**
```bash
curl -X POST http://localhost:5000/api/code/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "快速排序算法", "language": "python"}'
```

### 代码修复接口

#### POST /api/code/fix

修复代码错误

**请求示例:**
```bash
curl -X POST http://localhost:5000/api/code/fix \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello(): print(\"Hello\"",
    "error": "SyntaxError: unexpected EOF",
    "language": "python"
  }'
```

### 会话管理

```bash
# 获取会话历史
curl http://localhost:5000/api/sessions/user123

# 删除会话
curl -X DELETE http://localhost:5000/api/sessions/user123
```

---

## 🖥️ 服务器部署

### Ubuntu/CentOS 部署

#### 1. 安装系统依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx supervisor

# CentOS/RHEL
sudo yum install -y python3 python3-pip nginx supervisor
```

#### 2. 创建系统用户

```bash
sudo useradd -r -s /bin/false ai-assistant
```

#### 3. 配置 Supervisor

创建 `/etc/supervisor/conf.d/ai-assistant.conf`:

```ini
[program:ai-assistant]
command=/path/to/venv/bin/gunicorn \
    --bind 127.0.0.1:5000 \
    --workers 2 \
    --timeout 120 \
    wsgi:application
directory=/home/yc/my-project
user=ai-assistant
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/ai-assistant/out.log
stderr_logfile=/var/log/ai-assistant/err.log
environment=PATH="/path/to/venv/bin"
```

启动服务:
```bash
sudo mkdir -p /var/log/ai-assistant
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ai-assistant
```

#### 4. 配置 Nginx

创建 `/etc/nginx/sites-available/ai-assistant`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 120s;
        proxy_read_timeout 120s;
    }

    # 静态文件缓存
    location /static {
        alias /home/yc/my-project/static;
        expires 30d;
    }
}
```

启用配置:
```bash
sudo ln -s /etc/nginx/sites-available/ai-assistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## ☁️ 云平台部署

### Render 部署

1. 在 [Render](https://render.com) 创建账户

2. 创建 Web Service:
   - 连接 GitHub 仓库
   - 选择 `Python` 环境
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn wsgi:application`

3. 添加环境变量 (Settings → Environment Variables):
   ```
   QWEN_API_KEY=your-api-key
   QWEN_MODEL=qwen-turbo
   ```

4. 部署完成，获取公网 URL

### 阿里云部署

#### 方案一：ECS 服务器

参考上方「服务器部署」章节

#### 方案二：函数计算 FC

1. 创建 `fc_config.yml`:
```yaml
edition: 1.0.0
service:
  name: ai-assistant
functions:
  - name: api
    runtime: python3.9
    handler: wsgi.application
    codeDir: ./
    environmentVariables:
      QWEN_API_KEY: ${QWEN_API_KEY}
triggers:
  - name: httpTrigger
    type: http
    config:
      authType: anonymous
      methods: [GET, POST, PUT, DELETE]
```

2. 部署:
```bash
npm install -g @alicloud/fun
fun deploy
```

### 腾讯云部署

#### 云函数 SCF

1. 创建 `scf_config.json`:
```json
{
  "FunctionName": "ai-assistant",
  "Runtime": "Python3.9",
  "Handler": "wsgi.application",
  "Environment": {
    "Variables": {
      "QWEN_API_KEY": "your-api-key"
    }
  }
}
```

2. 部署:
```bash
npm install -g serverless
serverless deploy
```

### Vercel 部署

1. 创建 `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "wsgi.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "wsgi.py"
    }
  ],
  "env": {
    "QWEN_API_KEY": "@qwen-api-key"
  }
}
```

2. 添加 Secret:
```bash
vercel secrets add qwen-api-key your-api-key
```

3. 部署:
```bash
vercel --prod
```

---

## 🔒 安全配置

### 1. API Key 保护

- ✅ 使用环境变量，不硬编码
- ✅ `.env` 文件已加入 `.gitignore`
- ✅ 云平台使用 Secret 管理

### 2. 生产环境配置

```bash
# .env 生产配置示例
DEBUG=false
WORKERS=4
LOG_LEVEL=WARNING
```

### 3. Nginx 安全配置

```nginx
# 限制请求频率
limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;

server {
    location / {
        limit_req zone=one burst=20;
        # ...
    }
}
```

### 4. HTTPS 配置 (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 🧪 测试方法

### 健康检查

```bash
curl http://localhost:5000/health
```

### 聊天测试

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "测试", "session_id": "test"}'
```

### 使用 Python 测试

```python
import requests

# 聊天测试
response = requests.post(
    'http://localhost:5000/api/chat',
    json={'message': '你好', 'session_id': 'test123'}
)
print(response.json())
```

---

## 📊 监控与日志

### 查看日志

```bash
# Supervisor
sudo supervisorctl tail ai-assistant

# Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Systemd (如使用)
journalctl -u ai-assistant -f
```

### 性能监控

```bash
# 查看进程状态
ps aux | grep gunicorn

# 查看端口占用
netstat -tlnp | grep 5000

# 查看资源使用
top -p $(pgrep -d',' gunicorn)
```

---

## 🐛 故障排查

### 常见问题

#### 1. API Key 未配置

```
错误：API_KEY 未配置
解决：检查 .env 文件，确保 QWEN_API_KEY 已设置
```

#### 2. 端口被占用

```
错误：Address already in use
解决：更换端口或杀死占用进程
      lsof -i :5000
      kill -9 <PID>
```

#### 3. 依赖安装失败

```bash
# 升级 pip
pip install --upgrade pip

# 清理缓存重装
pip cache purge
pip install -r requirements.txt --force-reinstall
```

#### 4. Gunicorn 启动失败

```bash
# 检查配置
gunicorn --check-config wsgi:application

# 查看错误日志
tail -f /var/log/ai-assistant/err.log
```

---

## 📝 环境变量说明

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `QWEN_API_KEY` | 通义千问 API Key | - | ✅ |
| `QWEN_BASE_URL` | API 基础 URL | https://dashscope.aliyuncs.com/compatible-mode/v1 | ❌ |
| `QWEN_MODEL` | 模型名称 | qwen-turbo | ❌ |
| `QWEN_TIMEOUT` | 请求超时 (秒) | 15 | ❌ |
| `QWEN_MAX_TOKENS` | 最大 Token 数 | 1024 | ❌ |
| `HOST` | 绑定地址 | 0.0.0.0 | ❌ |
| `PORT` | 端口号 | 5000 | ❌ |
| `DEBUG` | 调试模式 | false | ❌ |
| `WORKERS` | Gunicorn 进程数 | 2 | ❌ |

---

## 📄 License

MIT License

---

## 🤝 支持

如有问题，请查看日志文件或提交 Issue。
