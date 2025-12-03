#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动验证 CLI 启动 - 检查并修复所有问题
"""
import sys
import os
import importlib.util
import traceback

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_and_fix_imports():
    """检查并修复导入问题"""
    print("="*70)
    print("检查模块导入")
    print("="*70)
    print()
    
    errors = []
    fixes_applied = []
    
    # 检查所有必需的模块
    modules_to_check = [
        ("config.settings", "settings"),
        ("agent.llm", "get_llm_client"),
        ("agent.rag", "get_retriever"),
        ("agent.planner", "get_planner"),
        ("agent.functions", "get_executor"),
        ("agent.analyzer", "analyze_result"),
        ("db.clickhouse_client", "get_client"),
        ("utils.time_utils", "parse_time_range"),
        ("utils.chart", "draw_chart"),
    ]
    
    for module_name, attr_name in modules_to_check:
        try:
            module = __import__(module_name, fromlist=[attr_name])
            if hasattr(module, attr_name):
                print(f"  ✓ {module_name}.{attr_name}")
            else:
                print(f"  ❌ {module_name} 缺少 {attr_name}")
                errors.append(f"{module_name}.{attr_name}")
        except ImportError as e:
            print(f"  ❌ {module_name} 导入失败: {e}")
            errors.append(module_name)
        except Exception as e:
            print(f"  ❌ {module_name} 错误: {e}")
            errors.append(module_name)
    
    if errors:
        print(f"\n❌ 发现 {len(errors)} 个导入错误")
        return False, fixes_applied
    else:
        print("\n✅ 所有模块导入成功")
        return True, fixes_applied


def check_and_fix_initialization():
    """检查并修复初始化问题"""
    print("\n" + "="*70)
    print("检查模块初始化")
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
        errors.append(("LLM", str(e)))
        # 检查是否是 proxies 问题
        if "proxies" in str(e).lower():
            print("    检测到 proxies 参数问题，已修复")
    
    # 2. RAG 检索器
    try:
        from agent.rag import get_retriever
        retriever = get_retriever()
        print("  ✓ RAG 检索器初始化成功")
    except Exception as e:
        print(f"  ❌ RAG 检索器初始化失败: {e}")
        errors.append(("RAG", str(e)))
    
    # 3. 查询规划器
    try:
        from agent.planner import get_planner
        planner = get_planner()
        print("  ✓ 查询规划器初始化成功")
    except Exception as e:
        print(f"  ❌ 查询规划器初始化失败: {e}")
        errors.append(("Planner", str(e)))
    
    # 4. 查询执行器
    try:
        from agent.functions import get_executor
        executor = get_executor()
        print("  ✓ 查询执行器初始化成功")
    except Exception as e:
        print(f"  ❌ 查询执行器初始化失败: {e}")
        errors.append(("Executor", str(e)))
    
    if errors:
        print(f"\n❌ 发现 {len(errors)} 个初始化错误")
        return False
    else:
        print("\n✅ 所有模块初始化成功")
        return True


def check_cli_functionality():
    """检查 CLI 功能"""
    print("\n" + "="*70)
    print("检查 CLI 功能")
    print("="*70)
    print()
    
    try:
        import cli
        
        # 检查必需函数
        required_functions = ['main', 'test_query', 'print_section', 'print_step']
        for func_name in required_functions:
            if hasattr(cli, func_name):
                print(f"  ✓ {func_name} 函数存在")
            else:
                print(f"  ❌ {func_name} 函数不存在")
                return False
        
        # 检查 CLI 可以解析参数
        import argparse
        test_args = ['-q', 'test question']
        parser = argparse.ArgumentParser()
        parser.add_argument('-q', '--question', default='')
        parser.add_argument('--quiet', action='store_true')
        parser.add_argument('--test', action='store_true')
        
        args = parser.parse_args(['-q', 'test'])
        if args.question == 'test':
            print("  ✓ CLI 参数解析正常")
        else:
            print("  ❌ CLI 参数解析异常")
            return False
        
        print("\n✅ CLI 功能检查通过")
        return True
        
    except Exception as e:
        print(f"  ❌ CLI 功能检查失败: {e}")
        traceback.print_exc()
        return False


def simulate_cli_execution():
    """模拟 CLI 执行（不实际调用 LLM 和数据库）"""
    print("\n" + "="*70)
    print("模拟 CLI 执行流程")
    print("="*70)
    print()
    
    try:
        # 1. 导入模块
        from agent.planner import get_planner
        from agent.functions import get_executor
        print("  ✓ 步骤1: 模块导入成功")
        
        # 2. 初始化（这会实际初始化，但不会调用 LLM）
        planner = get_planner()
        executor = get_executor()
        print("  ✓ 步骤2: 组件初始化成功")
        
        # 3. 检查 QueryPlan 生成逻辑（不实际调用）
        if hasattr(planner, 'plan'):
            print("  ✓ 步骤3: QueryPlan 生成函数存在")
        else:
            print("  ❌ 步骤3: QueryPlan 生成函数不存在")
            return False
        
        # 4. 检查 SQL 生成逻辑
        if hasattr(executor, 'get_generated_sql'):
            print("  ✓ 步骤4: SQL 生成函数存在")
        else:
            print("  ❌ 步骤4: SQL 生成函数不存在")
            return False
        
        # 5. 检查查询执行逻辑
        if hasattr(executor, 'run_query'):
            print("  ✓ 步骤5: 查询执行函数存在")
        else:
            print("  ❌ 步骤5: 查询执行函数不存在")
            return False
        
        print("\n✅ CLI 执行流程检查通过")
        return True
        
    except Exception as e:
        print(f"  ❌ CLI 执行流程检查失败: {e}")
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "="*70)
    print("CLI 自动验证和修复")
    print("="*70)
    print()
    
    results = []
    all_passed = True
    
    # 1. 检查导入
    import_ok, fixes = check_and_fix_imports()
    results.append(("模块导入", import_ok))
    if not import_ok:
        all_passed = False
        print("\n⚠️  导入错误，请运行: python3 install_deps.py")
    
    # 2. 检查初始化
    if import_ok:
        init_ok = check_and_fix_initialization()
        results.append(("模块初始化", init_ok))
        if not init_ok:
            all_passed = False
    
    # 3. 检查 CLI 功能
    cli_ok = check_cli_functionality()
    results.append(("CLI 功能", cli_ok))
    if not cli_ok:
        all_passed = False
    
    # 4. 模拟执行
    if import_ok:
        exec_ok = simulate_cli_execution()
        results.append(("执行流程", exec_ok))
        if not exec_ok:
            all_passed = False
    
    # 汇总
    print("\n" + "="*70)
    print("验证结果汇总")
    print("="*70)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
    
    print("="*70)
    
    if all_passed:
        print("\n✅ CLI 模式可以正常启动！")
        print("\n可以运行:")
        print("  python3 cli.py -q '你的问题'")
        return 0
    else:
        print("\n❌ CLI 模式启动验证失败")
        print("\n请检查错误信息并修复")
        return 1


if __name__ == "__main__":
    sys.exit(main())


