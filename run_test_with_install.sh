#!/bin/bash
# 自动安装依赖并运行测试

echo "=========================================="
echo "自动安装依赖并运行测试"
echo "=========================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 安装依赖
echo "步骤 1: 安装依赖..."
python3 install_deps.py

if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi

echo ""
echo "步骤 2: 验证代码..."
python3 verify.py

if [ $? -ne 0 ]; then
    echo "❌ 代码验证失败"
    exit 1
fi

echo ""
echo "步骤 3: 运行测试..."
python3 cli.py -q "统计近1h，发起探测的探测设备(hostname)区分不同的任务(task_name）统计，分析这些设备的平均丢包和rtt情况"

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="


