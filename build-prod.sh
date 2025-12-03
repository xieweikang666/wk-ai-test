#!/bin/bash

# 一键构建脚本 - 生产模式
# 构建React前端并配置后端提供静态文件服务

set -e

echo "🏗️  构建网络探测数据AI分析平台..."
echo "📋 模式：生产构建"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查必要工具
check_requirements() {
    echo "🔍 检查构建环境..."
    
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
    
    echo -e "${GREEN}✅ 构建环境检查通过${NC}"
}

# 清理旧的构建文件
clean_old_build() {
    echo "🧹 清理旧的构建文件..."
    
    # 清理前端构建文件
    if [ -d "frontend/build" ]; then
        rm -rf frontend/build
        echo "已清理 frontend/build"
    fi
    
    # 清理前端安装缓存（可选）
    if [ "$1" = "--deep" ]; then
        if [ -d "frontend/node_modules" ]; then
            rm -rf frontend/node_modules
            echo "已清理 frontend/node_modules"
        fi
    fi
    
    echo -e "${GREEN}✅ 清理完成${NC}"
}

# 安装依赖
install_dependencies() {
    echo "📦 安装依赖..."
    
    # 安装Python依赖
    echo "安装Python依赖..."
    pip3 install -r requirements.txt
    
    # 安装前端依赖
    echo "安装前端依赖..."
    cd frontend
    npm install
    cd ..
    
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
}

# 构建前端
build_frontend() {
    echo "🎨 构建React前端..."
    
    cd frontend
    
    # 设置生产环境变量
    export NODE_ENV=production
    export GENERATE_SOURCEMAP=false
    
    # 执行构建
    npm run build
    
    # 检查构建结果
    if [ ! -d "build" ] || [ ! -f "build/index.html" ]; then
        echo -e "${RED}❌ 前端构建失败${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 前端构建成功${NC}"
    
    # 显示构建信息
    BUILD_SIZE=$(du -sh build | cut -f1)
    echo "构建大小: $BUILD_SIZE"
    
    cd ..
}

# 验证构建结果
verify_build() {
    echo "🔍 验证构建结果..."
    
    # 检查关键文件
    REQUIRED_FILES=(
        "frontend/build/index.html"
        "frontend/build/static/js/main.*.js"
        "frontend/build/static/css/main.*.css"
    )
    
    for file in "${REQUIRED_FILES[@]}"; do
        if ! ls $file &> /dev/null; then
            echo -e "${RED}❌ 缺少关键文件: $file${NC}"
            exit 1
        fi
    done
    
    echo -e "${GREEN}✅ 构建验证通过${NC}"
}

# 创建启动脚本
create_prod_start_script() {
    echo "📝 创建生产启动脚本..."
    
    cat > start-prod.sh << 'EOF'
#!/bin/bash

# 生产环境启动脚本
# 启动后端服务，同时提供React静态文件

set -e

echo "🚀 启动生产环境服务..."

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查构建文件
if [ ! -f "frontend/build/index.html" ]; then
    echo -e "${RED}❌ 错误：未找到构建文件，请先运行 ./build-prod.sh${NC}"
    exit 1
fi

# 检查Python依赖
if ! python3 -c "import fastapi, clickhouse_driver" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python依赖缺失，正在安装...${NC}"
    pip3 install -r requirements.txt
fi

# 创建日志目录
mkdir -p logs

# 启动服务
echo -e "${GREEN}🔧 启动生产服务...${NC}"
python3 app.py --host 0.0.0.0 --port 8000 --prod > logs/prod.log 2>&1 &
PROD_PID=$!

echo "生产服务 PID: $PROD_PID"

# 等待服务启动
sleep 3
if kill -0 $PROD_PID 2>/dev/null; then
    echo -e "${GREEN}✅ 生产服务启动成功${NC}"
else
    echo -e "${RED}❌ 生产服务启动失败，请检查日志 logs/prod.log${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 生产服务启动完成！${NC}"
echo "🌐 访问地址: http://localhost:8000"
echo "📊 API文档: http://localhost:8000/docs"
echo "📝 日志文件: logs/prod.log"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"

# 捕获中断信号
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 正在停止生产服务...${NC}"
    if kill -0 $PROD_PID 2>/dev/null; then
        kill $PROD_PID
        echo "生产服务已停止"
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

# 保持脚本运行
while true; do
    sleep 1
    if ! kill -0 $PROD_PID 2>/dev/null; then
        echo -e "${RED}❌ 生产服务异常退出${NC}"
        exit 1
    fi
done
EOF

    chmod +x start-prod.sh
    echo -e "${GREEN}✅ 生产启动脚本创建完成${NC}"
}

# 生成构建信息
generate_build_info() {
    echo "📋 生成构建信息..."
    
    cat > build-info.json << EOF
{
  "build_time": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "build_mode": "production",
  "node_version": "$(node --version)",
  "npm_version": "$(npm --version)",
  "python_version": "$(python3 --version)",
  "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "git_branch": "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
}
EOF
    
    echo -e "${GREEN}✅ 构建信息已生成${NC}"
}

# 主流程
main() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}  网络探测数据AI分析平台 - 构建工具${NC}"
    echo -e "${BLUE}======================================${NC}"
    echo ""
    
    # 解析参数
    CLEAN_TYPE=""
    if [ "$1" = "--clean" ]; then
        CLEAN_TYPE="normal"
    elif [ "$1" = "--deep-clean" ]; then
        CLEAN_TYPE="deep"
    fi
    
    # 执行构建流程
    check_requirements
    
    if [ ! -z "$CLEAN_TYPE" ]; then
        clean_old_build $CLEAN_TYPE
    fi
    
    install_dependencies
    build_frontend
    verify_build
    create_prod_start_script
    generate_build_info
    
    echo ""
    echo -e "${GREEN}🎉 构建完成！${NC}"
    echo ""
    echo -e "${BLUE}📋 构建结果:${NC}"
    echo "  前端构建: frontend/build/"
    echo "  构建大小: $(du -sh frontend/build | cut -f1)"
    echo "  启动脚本: start-prod.sh"
    echo "  构建信息: build-info.json"
    echo ""
    echo -e "${BLUE}🚀 下一步:${NC}"
    echo "  开发模式: ./start-dev.sh"
    echo "  生产模式: ./start-prod.sh"
    echo ""
    echo -e "${YELLOW}💡 提示:${NC}"
    echo "  使用 --clean 参数清理构建缓存"
    echo "  使用 --deep-clean 参数完全重新构建"
}

# 执行主流程
main "$@"