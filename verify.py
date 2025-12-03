#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码验证脚本 - 检查代码逻辑是否正确
"""
import sys
import os
import ast
import importlib.util

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_imports():
    """检查导入是否正常"""
    print("检查模块导入...")
    try:
        from config.settings import settings
        print("  ✓ config.settings")
        
        from agent.llm import get_llm_client
        print("  ✓ agent.llm")
        
        from agent.rag import get_retriever
        print("  ✓ agent.rag")
        
        from agent.planner import get_planner
        print("  ✓ agent.planner")
        
        from agent.functions import get_executor
        print("  ✓ agent.functions")
        
        from db.clickhouse_client import get_client
        print("  ✓ db.clickhouse_client")
        
        from utils.time_utils import parse_time_range
        print("  ✓ utils.time_utils")
        
        from utils.chart import draw_chart
        print("  ✓ utils.chart")
        
        print("\n✅ 所有模块导入成功\n")
        return True
    except Exception as e:
        print(f"\n❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_code_logic():
    """检查代码逻辑"""
    print("检查代码逻辑...")
    issues = []
    
    # 检查 planner.py 中的 aggregation 枚举
    try:
        with open('agent/planner.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'group_by_hostname_task' not in content:
                issues.append("❌ planner.py 中缺少 group_by_hostname_task")
            else:
                print("  ✓ planner.py 包含 group_by_hostname_task")
    except Exception as e:
        issues.append(f"❌ 无法读取 planner.py: {e}")
    
    # 检查 functions.py 中的 SQL 生成逻辑
    try:
        with open('agent/functions.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'group_by_hostname_task' not in content:
                issues.append("❌ functions.py 中缺少 group_by_hostname_task 处理")
            else:
                print("  ✓ functions.py 包含 group_by_hostname_task 处理")
    except Exception as e:
        issues.append(f"❌ 无法读取 functions.py: {e}")
    
    # 检查时间工具
    try:
        from utils.time_utils import parse_time_range
        start, end = parse_time_range("last_1_hour")
        if start >= end:
            issues.append("❌ 时间范围解析错误")
        else:
            print("  ✓ 时间工具正常工作")
    except Exception as e:
        issues.append(f"❌ 时间工具测试失败: {e}")
    
    if issues:
        print("\n发现的问题:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("\n✅ 代码逻辑检查通过\n")
        return True


def check_config():
    """检查配置"""
    print("检查配置...")
    try:
        from config.settings import settings
        
        if not settings.OPENAI_API_KEY:
            print("  ⚠ OPENAI_API_KEY 未设置")
        else:
            print("  ✓ OPENAI_API_KEY 已设置")
        
        if not settings.OPENAI_API_BASE:
            print("  ⚠ OPENAI_API_BASE 未设置")
        else:
            print("  ✓ OPENAI_API_BASE 已设置")
        
        if not settings.CLICKHOUSE_ADDRESSES:
            print("  ⚠ CLICKHOUSE_ADDRESSES 未设置")
        else:
            print("  ✓ CLICKHOUSE_ADDRESSES 已设置")
        
        print("\n✅ 配置检查完成\n")
        return True
    except Exception as e:
        print(f"\n❌ 配置检查失败: {e}")
        return False


def main():
    """主函数"""
    print("="*70)
    print("代码验证脚本")
    print("="*70)
    print()
    
    results = []
    
    # 检查导入
    import_result = check_imports()
    results.append(("模块导入", import_result))
    
    # 如果导入失败，提示安装依赖
    if not import_result:
        print("\n⚠️  检测到依赖缺失，请运行以下命令安装:")
        print("  python3 install_deps.py")
        print("  或")
        print("  pip install -r requirements.txt")
        print()
    
    # 检查配置
    results.append(("配置检查", check_config()))
    
    # 检查代码逻辑
    results.append(("代码逻辑", check_code_logic()))
    
    # 汇总
    print("="*70)
    print("验证结果汇总")
    print("="*70)
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    print()
    if all_passed:
        print("✅ 所有检查通过！")
        print("\n可以运行以下命令进行测试:")
        print("  python3 cli.py")
        print("  python3 cli.py -q '你的问题'")
        return 0
    else:
        print("❌ 部分检查失败")
        if not import_result:
            print("\n💡 提示: 运行 'python3 install_deps.py' 自动安装依赖")
        return 1


if __name__ == "__main__":
    sys.exit(main())

