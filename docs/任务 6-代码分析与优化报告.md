# Qwen API 代码分析与优化报告

**任务编号**: 任务 6  
**日期**: 2026-03-14  
**文件**: `qwen_api.py`

---

## 一、原始代码问题

### 1. API Key 硬编码（严重安全风险）
```python
API_KEY = "sk-028d2bfdea2b401fa163415258361972"  # 直接暴露在代码中
```

### 2. 错误处理不足
- 未处理 API 返回的错误格式
- 没有重试机制
- 异常信息不清晰

### 3. 历史列表副作用
```python
messages = history or []  # 浅拷贝，可能修改原始列表
messages.append(...)
```

### 4. 缺少类型提示
- 函数无参数类型注解
- 无返回值类型注解

---

## 二、优化方案

### 1. 自定义异常体系
```python
class QwenAPIError(Exception)          # 基类
class QwenTimeoutError(QwenAPIError)   # 超时异常
class QwenConnectionError(QwenAPIError) # 网络异常
class QwenResponseError(QwenAPIError)  # 响应异常
```

### 2. 深拷贝历史列表
```python
messages = []
if history:
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
```

### 3. 重试机制
```python
for attempt in range(max_retries):
    try:
        # 请求代码
    except requests.exceptions.Timeout:
        if attempt < max_retries - 1:
            print(f"\n[重试 {attempt + 1}/{max_retries}] 正在重试...")
            continue
        raise
```

### 4. 分类错误提示
```python
except QwenTimeoutError as e:
    print(f"\r⏱️ 超时：{e}")
except QwenConnectionError as e:
    print(f"\r🌐 网络：{e}")
except QwenResponseError as e:
    print(f"\r❌ 响应：{e}")
```

---

## 三、Git 提交记录

```bash
# 第一次重构提交
a1b27d5 refactor(qwen_api.py): 改进异常处理、深拷贝和错误提示（AI 协助）

# 修复换行符问题
a2ae536 fix(qwen_api.py): 修复换行符转义问题（AI 协助）
```

---

## 四、API Key 安全修复

### ⚠️ 当前状态
- 原 API Key `sk-028d2bfdea2b401fa163415258361972` 已暴露在 Git 历史中
- 需要立即轮换

### 修复步骤

1. **生成新 API Key**
   - 登录阿里云百炼控制台
   - 禁用旧 Key，生成新 Key

2. **创建 .env 文件**
   ```bash
   cd /home/yc/my-project
   cat > .env << 'EOF'
   QWEN_API_KEY=你的新_API_Key
   EOF
   ```

3. **确保 .gitignore 包含 .env**
   ```bash
   echo ".env" >> .gitignore
   ```

4. **清理 Git 历史（可选，如需彻底清理）**
   ```bash
   # 方式 A - 重新初始化（最简单）
   rm -rf .git && git init && git add . && git commit -m "init"
   git push -f origin master
   
   # 方式 B - 使用 BFG
   java -jar bfg.jar --replace-text passwords.txt repo.git
   ```

---

## 五、配套文件

### .env
```bash
QWEN_API_KEY=你的 API_Key
```

### requirements.txt
```txt
requests>=2.28.0
python-dotenv>=1.0.0
```

### .gitignore
```gitignore
.env
__pycache__/
*.pyc
*.pyo
```

---

## 六、运行测试

```bash
cd /home/yc/my-project

# 安装依赖
pip install -r requirements.txt

# 运行
python3 qwen_api.py
```

---

**备注**: 本报告由 AI 协助生成，记录了代码重构的完整过程和安全注意事项。
