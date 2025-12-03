#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目启动测试脚本
验证项目是否能正常启动和运行
"""
import sys
import os
import traceback

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试模块导入"""
    print("="*70)
    print("测试 1: 模块导入")
    print("="*70)
    
    errors = []
    
    try:
        from config.settings import settings
        print("  ✓ config.settings")
    except Exception as e:
        print(f"  ❌ config.settings: {e}")
        errors.append(f"config.settings: {e}")
    
    try:
        from agent.llm import get_llm_client
        print("  ✓ agent.llm")
    except Exception as e:
        print(f"  ❌ agent.llm: {e}")
        errors.append(f"agent.llm: {e}")
    
    try:
        from agent.rag import get_retriever
        print("  ✓ agent.rag")
    except Exception as e:
        print(f"  ❌ agent.rag: {e}")
        errors.append(f"agent.rag: {e}")
    
    try:
        from agent.planner import get_planner
        print("  ✓ agent.planner")
    except Exception as e:
        print(f"  ❌ agent.planner: {e}")
        errors.append(f"agent.planner: {e}")
    
    try:
        from agent.functions import get_executor
        print("  ✓ agent.functions")
    except Exception as e:
        print(f"  ❌ agent.functions: {e}")
        errors.append(f"agent.functions: {e}")
    
    try:
        from db.clickhouse_client import get_client
        print("  ✓ db.clickhouse_client")
    except Exception as e:
        print(f"  ❌ db.clickhouse_client: {e}")
        errors.append(f"db.clickhouse_client: {e}")
    
    try:
        from utils.time_utils import parse_time_range
        print("  ✓ utils.time_utils")
    except Exception as e:
        print(f"  ❌ utils.time_utils: {e}")
        errors.append(f"utils.time_utils: {e}")
    
    try:
        from utils.chart import draw_chart
        print("  ✓ utils.chart")
    except Exception as e:
        print(f"  ❌ utils.chart: {e}")
        errors.append(f"utils.chart: {e}")
    
    if errors:
        print(f"\n❌ 导入失败: {len(errors)} 个错误")
        return False
    else:
        print("\n✅ 所有模块导入成功")
        return True


def test_initialization():
    """测试初始化"""
    print("\n" + "="*70)
    print("测试 2: 模块初始化")
    print("="*70)
    
    errors = []
    
    try:
        from config.settings import settings
        print(f"  ✓ Settings 初始化成功 (模型: {settings.OPENAI_MODEL})")
    except Exception as e:
        print(f"  ❌ Settings 初始化失败: {e}")
        errors.append(f"Settings: {e}")
        traceback.print_exc()
    
    try:
        from agent.llm import get_llm_client
        llm = get_llm_client()
        print("  ✓ LLM 客户端初始化成功")
    except Exception as e:
        print(f"  ❌ LLM 客户端初始化失败: {e}")
        errors.append(f"LLM: {e}")
        # 不打印完整 traceback，因为可能是依赖问题
    
    try:
        from agent.rag import get_retriever
        retriever = get_retriever()
        print("  ✓ RAG 检索器初始化成功")
    except Exception as e:
        print(f"  ❌ RAG 检索器初始化失败: {e}")
        errors.append(f"RAG: {e}")
        # 不打印完整 traceback，因为可能是依赖问题
    
    try:
        from agent.planner import get_planner
        planner = get_planner()
        print("  ✓ 查询规划器初始化成功")
    except Exception as e:
        print(f"  ❌ 查询规划器初始化失败: {e}")
        errors.append(f"Planner: {e}")
        traceback.print_exc()
    
    try:
        from agent.functions import get_executor
        executor = get_executor()
        print("  ✓ 查询执行器初始化成功")
    except Exception as e:
        print(f"  ❌ 查询执行器初始化失败: {e}")
        errors.append(f"Executor: {e}")
        traceback.print_exc()
    
    if errors:
        print(f"\n❌ 初始化失败: {len(errors)} 个错误")
        return False
    else:
        print("\n✅ 所有模块初始化成功")
        return True


def test_app_import():
    """测试 FastAPI 应用导入"""
    print("\n" + "="*70)
    print("测试 3: FastAPI 应用导入")
    print("="*70)
    
    try:
        from app import app
        print("  ✓ FastAPI 应用导入成功")
        print(f"  ✓ 应用标题: {app.title}")
        return True
    except Exception as e:
        print(f"  ❌ FastAPI 应用导入失败: {e}")
        traceback.print_exc()
        return False


def test_cli_import():
    """测试 CLI 工具导入"""
    print("\n" + "="*70)
    print("测试 4: CLI 工具导入")
    print("="*70)
    
    try:
        import cli
        print("  ✓ CLI 工具导入成功")
        return True
    except Exception as e:
        print(f"  ❌ CLI 工具导入失败: {e}")
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "="*70)
    print("项目启动测试")
    print("="*70)
    print()
    
    results = []
    
    # 测试导入
    results.append(("模块导入", test_imports()))
    
    # 测试初始化
    results.append(("模块初始化", test_initialization()))
    
    # 测试应用导入
    results.append(("FastAPI 应用", test_app_import()))
    
    # 测试 CLI 导入
    results.append(("CLI 工具", test_cli_import()))
    
    # 汇总
    print("\n" + "="*70)
    print("测试结果汇总")
    print("="*70)
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
        if not result:
            all_passed = False
    
    print("="*70)
    
    if all_passed:
        print("\n✅ 所有测试通过！项目可以正常启动")
        print("\n可以运行以下命令:")
        print("  python3 cli.py -q '你的问题'  # CLI 模式")
        print("  python3 app.py                # 启动服务")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查错误信息并修复")
        return 1


if __name__ == "__main__":
    sys.exit(main())


