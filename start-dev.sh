#!/bin/bash

# 一键启动脚本 - 开发模式
# 同时启动后端FastAPI服务和React前端开发服务器

set -e

echo "🚀 启动网络探测数据AI分析平台..."
echo "📋 模式：开发模式（热重载）"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查Python和Node.js
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 错误：Python3未安装${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ 错误：Node.js未安装${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ 错误：npm未安装${NC}"
    exit 1
fi

# 检查Python依赖
echo "🐍 检查Python依赖..."
if ! python3 -c "import fastapi, clickhouse_driver" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python依赖缺失，正在安装...${NC}"
    pip3 install -r requirements.txt
fi

# 检查前端依赖
echo "📦 检查前端依赖..."
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}⚠️  前端依赖缺失，正在安装...${NC}"
    cd frontend
    npm install
    cd ..
fi

# 创建日志目录
mkdir -p logs

echo ""
echo -e "${GREEN}✅ 环境检查完成${NC}"
echo ""

# 启动服务函数
start_backend() {
    echo -e "${GREEN}🔧 启动后端服务 (端口:8000)...${NC}"
    python3 app.py --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "后端进程 PID: $BACKEND_PID"
    
    # 等待后端启动
    sleep 3
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${GREEN}✅ 后端服务启动成功${NC}"
    else
        echo -e "${RED}❌ 后端服务启动失败，请检查日志 logs/backend.log${NC}"
        exit 1
    fi
}

start_frontend() {
    echo -e "${GREEN}🎨 启动前端服务 (端口:3000)...${NC}"
    cd frontend
    npm start > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    echo "前端进程 PID: $FRONTEND_PID"
    
    # 等待前端启动
    sleep 5
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${GREEN}✅ 前端服务启动成功${NC}"
    else
        echo -e "${RED}❌ 前端服务启动失败，请检查日志 logs/frontend.log${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
}

# 停止服务函数
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 正在停止服务...${NC}"
    
    if [ ! -z "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        echo "后端服务已停止"
    fi
    
    if [ ! -z "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        echo "前端服务已停止"
    fi
    
    # 清理可能残留的进程
    pkill -f "python3 app.py" 2>/dev/null || true
    pkill -f "react-scripts start" 2>/dev/null || true
    
    echo -e "${GREEN}✅ 服务已停止${NC}"
    exit 0
}

# 捕获中断信号
trap cleanup SIGINT SIGTERM

# 启动服务
start_backend
start_frontend

echo ""
echo -e "${GREEN}🎉 启动完成！${NC}"
echo "📱 前端地址: http://localhost:3000"
echo "🔧 后端地址: http://localhost:8000"
echo "📊 API文档: http://localhost:8000/docs"
echo ""
echo "📋 服务状态:"
echo "   后端 PID: $BACKEND_PID"
echo "   前端 PID: $FRONTEND_PID"
echo ""
echo "📝 日志文件:"
echo "   后端日志: logs/backend.log"
echo "   前端日志: logs/frontend.log"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}"

# 保持脚本运行，等待中断
while true; do
    sleep 1
    # 检查进程是否还在运行
    if ! kill -0 $BACKEND_PID 2>/dev/null || ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}❌ 检测到服务异常退出${NC}"
        cleanup
    fi
done