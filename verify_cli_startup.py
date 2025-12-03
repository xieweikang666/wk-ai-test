#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 CLI 模式是否可以正常启动
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cli_imports():
    """测试 CLI 所需的所有导入"""
    print("="*70)
    print("测试 CLI 模块导入")
    print("="*70)
    print()
    
    errors = []
    
    # 1. 基础模块
    try:
        import json
        import argparse
        print("  ✓ 基础模块 (json, argparse)")
    except ImportError as e:
        print(f"  ❌ 基础模块导入失败: {e}")
        errors.append("基础模块")
    
    # 2. 配置模块
    try:
        from config.settings import settings
        print("  ✓ config.settings")
    except Exception as e:
        print(f"  ❌ config.settings: {e}")
        errors.append("config.settings")
    
    # 3. LLM 模块
    try:
        from agent.llm import get_llm_client
        print("  ✓ agent.llm")
    except Exception as e:
        print(f"  ❌ agent.llm: {e}")
        errors.append("agent.llm")
    
    # 4. RAG 模块
    try:
        from agent.rag import get_retriever
        print("  ✓ agent.rag")
    except Exception as e:
        print(f"  ❌ agent.rag: {e}")
        errors.append("agent.rag")
    
    # 5. Planner 模块
    try:
        from agent.planner import get_planner
        print("  ✓ agent.planner")
    except Exception as e:
        print(f"  ❌ agent.planner: {e}")
        errors.append("agent.planner")
    
    # 6. Functions 模块
    try:
        from agent.functions import get_executor
        print("  ✓ agent.functions")
    except Exception as e:
        print(f"  ❌ agent.functions: {e}")
        errors.append("agent.functions")
    
    # 7. 数据库模块
    try:
        from db.clickhouse_client import get_client
        print("  ✓ db.clickhouse_client")
    except Exception as e:
        print(f"  ❌ db.clickhouse_client: {e}")
        errors.append("db.clickhouse_client")
    
    # 8. 工具模块
    try:
        from utils.time_utils import parse_time_range
        print("  ✓ utils.time_utils")
    except Exception as e:
        print(f"  ❌ utils.time_utils: {e}")
        errors.append("utils.time_utils")
    
    try:
        from utils.chart import draw_chart
        print("  ✓ utils.chart")
    except Exception as e:
        print(f"  ❌ utils.chart: {e}")
        errors.append("utils.chart")
    
    # 9. 分析器模块
    try:
        from agent.analyzer import analyze_result
        print("  ✓ agent.analyzer")
    except Exception as e:
        print(f"  ❌ agent.analyzer: {e}")
        errors.append("agent.analyzer")
    
    # 10. CLI 模块本身
    try:
        import cli
        print("  ✓ cli 模块")
    except Exception as e:
        print(f"  ❌ cli 模块: {e}")
        errors.append("cli")
    
    if errors:
        print(f"\n❌ 导入失败: {len(errors)} 个模块")
        return False
    else:
        print("\n✅ 所有模块导入成功")
        return True


def test_cli_initialization():
    """测试 CLI 所需的初始化"""
    print("\n" + "="*70)
    print("测试 CLI 模块初始化")
    print("="*70)
    print()
    
    errors = []
    
    # 1. LLM 客户端
    try:
        from agent.llm import get_llm_client
        llm = get_llm_client()
        print("  ✓ LLM 客户端初始化成功")
    except Exception as e:
        print(f"  ❌ LLM 客户端初始化失败: {e}")
        errors.append("LLM")
    
    # 2. RAG 检索器
    try:
        from agent.rag import get_retriever
        retriever = get_retriever()
        print("  ✓ RAG 检索器初始化成功")
    except Exception as e:
        print(f"  ❌ RAG 检索器初始化失败: {e}")
        errors.append("RAG")
    
    # 3. 查询规划器
    try:
        from agent.planner import get_planner
        planner = get_planner()
        print("  ✓ 查询规划器初始化成功")
    except Exception as e:
        print(f"  ❌ 查询规划器初始化失败: {e}")
        errors.append("Planner")
    
    # 4. 查询执行器
    try:
        from agent.functions import get_executor
        executor = get_executor()
        print("  ✓ 查询执行器初始化成功")
    except Exception as e:
        print(f"  ❌ 查询执行器初始化失败: {e}")
        errors.append("Executor")
    
    if errors:
        print(f"\n❌ 初始化失败: {len(errors)} 个模块")
        return False
    else:
        print("\n✅ 所有模块初始化成功")
        return True


def test_cli_main():
    """测试 CLI main 函数是否可以调用"""
    print("\n" + "="*70)
    print("测试 CLI main 函数")
    print("="*70)
    print()
    
    try:
        import cli
        # 检查 main 函数是否存在
        if hasattr(cli, 'main'):
            print("  ✓ CLI main 函数存在")
            
            # 检查 test_query 函数是否存在
            if hasattr(cli, 'test_query'):
                print("  ✓ CLI test_query 函数存在")
                return True
            else:
                print("  ❌ CLI test_query 函数不存在")
                return False
        else:
            print("  ❌ CLI main 函数不存在")
            return False
    except Exception as e:
        print(f"  ❌ CLI 模块检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "="*70)
    print("CLI 启动验证")
    print("="*70)
    print()
    
    results = []
    
    # 测试导入
    results.append(("模块导入", test_cli_imports()))
    
    # 测试初始化
    results.append(("模块初始化", test_cli_initialization()))
    
    # 测试 CLI main
    results.append(("CLI main 函数", test_cli_main()))
    
    # 汇总
    print("\n" + "="*70)
    print("验证结果汇总")
    print("="*70)
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
        if not result:
            all_passed = False
    
    print("="*70)
    
    if all_passed:
        print("\n✅ CLI 模式可以正常启动！")
        print("\n可以运行以下命令:")
        print("  python3 cli.py --help")
        print("  python3 cli.py -q '你的问题'")
        return 0
    else:
        print("\n❌ CLI 模式启动验证失败")
        print("\n请检查错误信息并修复")
        return 1


if __name__ == "__main__":
    sys.exit(main())


