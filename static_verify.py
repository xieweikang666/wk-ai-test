#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
静态验证 CLI 启动 - 不实际运行，只检查代码逻辑
"""
import sys
import os
import ast
import re

def check_file_syntax(filepath):
    """检查文件语法"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def check_imports_in_file(filepath):
    """检查文件中的导入"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查导入语句
        imports = re.findall(r'^from\s+(\S+)\s+import|^import\s+(\S+)', content, re.MULTILINE)
        return [imp[0] or imp[1] for imp in imports]
    except Exception as e:
        return []

def verify_cli_structure():
    """验证 CLI 结构"""
    print("="*70)
    print("静态验证 CLI 代码结构")
    print("="*70)
    print()
    
    issues = []
    
    # 1. 检查 CLI 文件语法
    cli_file = "cli.py"
    if os.path.exists(cli_file):
        ok, error = check_file_syntax(cli_file)
        if ok:
            print(f"  ✓ {cli_file} 语法正确")
        else:
            print(f"  ❌ {cli_file} 语法错误: {error}")
            issues.append(f"{cli_file} 语法错误")
    else:
        print(f"  ❌ {cli_file} 文件不存在")
        issues.append(f"{cli_file} 文件不存在")
    
    # 2. 检查关键模块文件
    key_files = [
        "agent/llm.py",
        "agent/rag.py",
        "agent/planner.py",
        "agent/functions.py",
        "agent/analyzer.py",
        "db/clickhouse_client.py",
        "utils/time_utils.py",
        "utils/chart.py",
        "config/settings.py"
    ]
    
    print("\n检查关键模块文件:")
    for filepath in key_files:
        if os.path.exists(filepath):
            ok, error = check_file_syntax(filepath)
            if ok:
                print(f"  ✓ {filepath}")
            else:
                print(f"  ❌ {filepath} 语法错误: {error}")
                issues.append(f"{filepath} 语法错误: {error}")
        else:
            print(f"  ❌ {filepath} 文件不存在")
            issues.append(f"{filepath} 文件不存在")
    
    # 3. 检查 CLI 必需函数
    if os.path.exists(cli_file):
        with open(cli_file, 'r', encoding='utf-8') as f:
            cli_content = f.read()
        
        required_functions = ['main', 'test_query', 'print_section', 'print_step']
        print("\n检查 CLI 必需函数:")
        for func in required_functions:
            if f"def {func}" in cli_content:
                print(f"  ✓ {func} 函数存在")
            else:
                print(f"  ❌ {func} 函数不存在")
                issues.append(f"CLI 缺少 {func} 函数")
    
    # 4. 检查关键类和方法
    print("\n检查关键类和方法:")
    
    # agent/planner.py
    if os.path.exists("agent/planner.py"):
        with open("agent/planner.py", 'r', encoding='utf-8') as f:
            planner_content = f.read()
        if "class QueryPlanner" in planner_content and "def plan" in planner_content:
            print("  ✓ QueryPlanner.plan 存在")
        else:
            print("  ❌ QueryPlanner.plan 不存在")
            issues.append("QueryPlanner.plan 不存在")
    
    # agent/functions.py
    if os.path.exists("agent/functions.py"):
        with open("agent/functions.py", 'r', encoding='utf-8') as f:
            functions_content = f.read()
        required_methods = ['run_query', 'get_generated_sql', 'draw_chart_wrapper', 'explain_result']
        for method in required_methods:
            if f"def {method}" in functions_content:
                print(f"  ✓ QueryPlanExecutor.{method} 存在")
            else:
                print(f"  ❌ QueryPlanExecutor.{method} 不存在")
                issues.append(f"QueryPlanExecutor.{method} 不存在")
    
    # 5. 检查 group_by_hostname_task 支持
    print("\n检查 group_by_hostname_task 支持:")
    if os.path.exists("agent/planner.py"):
        with open("agent/planner.py", 'r', encoding='utf-8') as f:
            planner_content = f.read()
        if "group_by_hostname_task" in planner_content:
            print("  ✓ planner.py 包含 group_by_hostname_task")
        else:
            print("  ❌ planner.py 缺少 group_by_hostname_task")
            issues.append("planner.py 缺少 group_by_hostname_task")
    
    if os.path.exists("agent/functions.py"):
        with open("agent/functions.py", 'r', encoding='utf-8') as f:
            functions_content = f.read()
        if "group_by_hostname_task" in functions_content:
            print("  ✓ functions.py 包含 group_by_hostname_task 处理")
        else:
            print("  ❌ functions.py 缺少 group_by_hostname_task 处理")
            issues.append("functions.py 缺少 group_by_hostname_task 处理")
    
    # 6. 检查 LLM 客户端 proxies 修复
    print("\n检查 LLM 客户端修复:")
    if os.path.exists("agent/llm.py"):
        with open("agent/llm.py", 'r', encoding='utf-8') as f:
            llm_content = f.read()
        if "HTTP_PROXY" in llm_content or "proxies" in llm_content.lower():
            if "os.environ.pop" in llm_content or "saved_proxy_vars" in llm_content:
                print("  ✓ LLM 客户端已修复 proxies 问题")
            else:
                print("  ⚠ LLM 客户端可能仍有 proxies 问题")
        else:
            print("  ✓ LLM 客户端代码正常")
    
    if issues:
        print(f"\n❌ 发现 {len(issues)} 个问题:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("\n✅ 所有静态检查通过")
        return True

def main():
    """主函数"""
    print("\n" + "="*70)
    print("CLI 静态验证")
    print("="*70)
    print()
    
    result = verify_cli_structure()
    
    print("\n" + "="*70)
    if result:
        print("✅ CLI 代码结构验证通过")
        print("\nCLI 模式应该可以正常启动")
        print("可以运行: python3 cli.py -q '你的问题'")
        return 0
    else:
        print("❌ CLI 代码结构验证失败")
        print("请修复上述问题后重试")
        return 1

if __name__ == "__main__":
    sys.exit(main())


