#!/bin/bash

# React前端启动脚本

echo "🚀 启动React前端..."

# 检查是否在frontend目录
if [ ! -f "package.json" ]; then
    echo "❌ 错误：请在frontend目录下运行此脚本"
    exit 1
fi

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "❌ 错误：Node.js未安装，请先安装Node.js 14+"
    exit 1
fi

# 检查npm是否安装
if ! command -v npm &> /dev/null; then
    echo "❌ 错误：npm未安装"
    exit 1
fi

# 检查是否已安装依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖中..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
fi

# 启动开发服务器
echo "🌐 启动开发服务器..."
echo "前端将在 http://localhost:3000 启动"
echo "请确保后端服务在 http://localhost:8000 运行"
echo "按 Ctrl+C 停止服务"
echo ""

npm start