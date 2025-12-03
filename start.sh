#!/bin/bash
# 启动脚本

echo "启动网络探测数据 AI 分析 Agent..."
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 检查依赖
echo "检查依赖..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "安装依赖..."
    pip3 install -r requirements.txt
fi

# 启动服务
echo "启动服务..."
python3 app.py


