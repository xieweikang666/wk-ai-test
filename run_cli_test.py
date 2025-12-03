#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接运行 CLI 测试
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 模拟命令行参数
sys.argv = ['cli.py', '-q', '统计近1h，发起探测的探测设备(hostname)区分不同的任务(task_name）统计，分析这些设备的平均丢包和rtt情况']

# 导入并运行 CLI
try:
    from cli import main
    main()
except Exception as e:
    print(f"\n❌ CLI 运行失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


