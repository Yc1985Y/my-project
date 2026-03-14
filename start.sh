#!/bin/bash
#===============================================================================
# AI Assistant 一键启动脚本
# 支持本地开发、服务器部署、云平台部署
#===============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# 默认配置
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-5000}"
WORKERS="${WORKERS:-2}"
DEBUG="${DEBUG:-false}"
MODE="${MODE:-dev}"  # dev | prod

#-------------------------------------------------------------------------------
# 帮助信息
#-------------------------------------------------------------------------------
show_help() {
    cat << HELP
${BLUE}AI Assistant 启动脚本${NC}

用法：$0 [选项]

选项:
    -m, --mode      运行模式 (dev|prod), 默认：dev
    -p, --port      端口号，默认：5000
    -w, --workers   Gunicorn 工作进程数，默认：2
    -d, --debug     开启调试模式
    -h, --help      显示帮助信息

示例:
    $0                      # 开发模式启动
    $0 -m prod              # 生产模式启动 (Gunicorn)
    $0 -p 8080 -w 4         # 指定端口和进程数
    $0 --debug              # 调试模式启动

环境变量:
    QWEN_API_KEY           # 通义千问 API Key (必需)
    QWEN_BASE_URL          # API 基础 URL
    QWEN_MODEL             # 模型名称
    HOST                   # 绑定地址
    PORT                   # 端口号
    WORKERS                # Gunicorn 进程数
    DEBUG                  # 调试模式

HELP
}

#-------------------------------------------------------------------------------
# 检查环境
#-------------------------------------------------------------------------------
check_environment() {
    echo -e "${BLUE}检查运行环境...${NC}"
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}错误：未找到 Python3${NC}"
        exit 1
    fi
    
    # 检查虚拟环境
    if [ ! -d "venv" ] && [ ! -d ".venv" ] && [ -z "$VIRTUAL_ENV" ]; then
        echo -e "${YELLOW}警告：未检测到虚拟环境${NC}"
        echo -e "${YELLOW}建议创建：python3 -m venv venv${NC}"
    fi
    
    # 检查 .env 文件
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}警告：未找到 .env 文件${NC}"
        if [ -f ".env.example" ]; then
            echo -e "${YELLOW}建议复制配置：cp .env.example .env${NC}"
        fi
    fi
    
    # 检查 API Key
    if [ -z "$QWEN_API_KEY" ]; then
        echo -e "${YELLOW}警告：QWEN_API_KEY 未设置${NC}"
    fi
}

#-------------------------------------------------------------------------------
# 安装依赖
#-------------------------------------------------------------------------------
install_dependencies() {
    echo -e "${BLUE}检查并安装依赖...${NC}"
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt -q
    fi
}

#-------------------------------------------------------------------------------
# 开发模式启动 (Flask)
#-------------------------------------------------------------------------------
start_dev() {
    echo -e "${GREEN}==================================${NC}"
    echo -e "${GREEN}  AI Assistant - 开发模式${NC}"
    echo -e "${GREEN}==================================${NC}"
    echo -e "地址：${BLUE}http://${HOST}:${PORT}${NC}"
    echo -e "调试：${YELLOW}已开启${NC}"
    echo ""
    
    export DEBUG=true
    export HOST="${HOST:-0.0.0.0}"
    export PORT="${PORT:-5000}"
    
    python3 app.py
}

#-------------------------------------------------------------------------------
# 生产模式启动 (Gunicorn)
#-------------------------------------------------------------------------------
start_prod() {
    echo -e "${GREEN}==================================${NC}"
    echo -e "${GREEN}  AI Assistant - 生产模式${NC}"
    echo -e "${GREEN}==================================${NC}"
    echo -e "地址：${BLUE}http://${HOST}:${PORT}${NC}"
    echo -e "进程：${WORKERS}"
    echo ""
    
    export DEBUG=false
    export HOST="${HOST:-0.0.0.0}"
    export PORT="${PORT:-5000}"
    export WORKERS="${WORKERS:-2}"
    
    # 检查 Gunicorn
    if ! command -v gunicorn &> /dev/null; then
        echo -e "${YELLOW}安装 Gunicorn...${NC}"
        pip3 install gunicorn -q
    fi
    
    gunicorn \
        --bind "${HOST}:${PORT}" \
        --workers "${WORKERS}" \
        --worker-class sync \
        --timeout 120 \
        --keep-alive 5 \
        --access-logfile - \
        --error-logfile - \
        --capture-output \
        wsgi:application
}

#-------------------------------------------------------------------------------
# 主函数
#-------------------------------------------------------------------------------
main() {
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -m|--mode)
                MODE="$2"
                shift 2
                ;;
            -p|--port)
                PORT="$2"
                shift 2
                ;;
            -w|--workers)
                WORKERS="$2"
                shift 2
                ;;
            -d|--debug)
                DEBUG=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo -e "${RED}未知选项：$1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 检查环境
    check_environment
    
    # 启动服务
    case $MODE in
        dev|development)
            start_dev
            ;;
        prod|production)
            start_prod
            ;;
        *)
            echo -e "${RED}未知模式：$MODE${NC}"
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
