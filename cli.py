#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI 命令行工具
用于测试和验证系统功能
"""
import sys
import os
import json
import traceback
import argparse

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_step(step_num: int, description: str):
    """打印步骤"""
    print(f"[步骤 {step_num}] {description}...")


def test_query(question: str, verbose: bool = True):
    """测试查询"""
    print_section("网络探测数据 AI 分析 Agent - 测试")
    print(f"问题: {question}\n")
    
    try:
        # 步骤1: 导入模块
        if verbose:
            print_step(1, "导入模块")
        from agent.planner import get_planner
        from agent.functions import get_executor
        if verbose:
            print("  ✓ 模块导入成功\n")
        
        # 步骤2: 初始化
        if verbose:
            print_step(2, "初始化规划器和执行器")
        planner = get_planner()
        executor = get_executor()
        if verbose:
            print("  ✓ 初始化完成\n")
        
        # 步骤3: 生成 QueryPlan
        if verbose:
            print_step(3, "生成 QueryPlan (调用 LLM)")
            print("  (这可能需要一些时间...)\n")
        query_plan = planner.plan(question)
        if verbose:
            print("  ✓ QueryPlan 生成成功")
            print(f"\n  QueryPlan 内容:")
            print(f"  {json.dumps(query_plan, indent=2, ensure_ascii=False)}\n")
        
        # 步骤4: 生成 SQL
        if verbose:
            print_step(4, "生成 SQL")
        generated_sql = executor.get_generated_sql(query_plan)
        if verbose:
            print("  ✓ SQL 生成成功")
            print(f"\n  生成的 SQL:\n")
            print("  " + "\n  ".join(generated_sql.split("\n")))
            print()
        
        # 步骤5: 执行查询
        if verbose:
            print_step(5, "执行查询 (连接 ClickHouse)")
            print("  (正在查询数据库...)\n")
        df = executor.run_query(query_plan)
        if verbose:
            print(f"  ✓ 查询完成，返回 {len(df)} 行数据\n")
        
        # 步骤6: 显示结果
        if not df.empty:
            if verbose:
                print_step(6, "查询结果预览")
                print(f"\n  前 10 行数据:\n")
                print("  " + "\n  ".join(df.head(10).to_string().split("\n")))
                print()
        else:
            if verbose:
                print_step(6, "查询结果")
                print("  ⚠ 查询结果为空\n")
        
        # 步骤7: 生成图表
        chart_path = None
        if query_plan.get("need_chart", False):
            if verbose:
                print_step(7, "生成图表")
            chart_type = query_plan.get("chart_type", "line")
            chart_path = executor.draw_chart_wrapper(
                df=df,
                chart_type=chart_type,
                title=f"查询结果 - {question[:50]}"
            )
            if chart_path:
                if verbose:
                    print(f"  ✓ 图表已生成: {chart_path}\n")
            else:
                if verbose:
                    print("  ⚠ 图表生成失败\n")
        
        # 步骤8: 分析结果
        if verbose:
            print_step(8, "分析结果 (调用 LLM)")
            print("  (正在分析数据...)\n")
        answer = executor.explain_result(
            df=df,
            query_plan=query_plan,
            chart_path=chart_path
        )
        
        # 输出最终结果
        print_section("最终结果")
        print("生成的 SQL:")
        print("-" * 70)
        print(generated_sql)
        print("-" * 70)
        
        print("\n分析结果:")
        print("-" * 70)
        print(answer)
        print("-" * 70)
        
        if chart_path:
            print(f"\n图表路径: {chart_path}")
        
        return {
            "success": True,
            "sql": generated_sql,
            "rows": len(df),
            "answer": answer,
            "chart_path": chart_path,
            "query_plan": query_plan
        }
        
    except ImportError as e:
        print(f"\n❌ 导入错误: {e}")
        print("\n请确保已安装所有依赖:")
        print("  pip install -r requirements.txt")
        if verbose:
            traceback.print_exc()
        return {"success": False, "error": f"导入错误: {str(e)}"}
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        if verbose:
            print("\n详细错误信息:")
            traceback.print_exc()
        return {"success": False, "error": str(e)}


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="网络探测数据 AI 分析 Agent - CLI 工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认问题测试
  python3 cli.py
  
  # 使用自定义问题
  python3 cli.py -q "统计近1h的RTT情况"
  
  # 静默模式（只显示最终结果）
  python3 cli.py --quiet
        """
    )
    
    parser.add_argument(
        "-q", "--question",
        default="统计近1h，发起探测的探测设备(hostname)区分不同的任务(task_name）统计，分析这些设备的平均丢包和rtt情况",
        help="要查询的问题"
    )
    
    parser.add_argument(
        "--quiet", "-Q",
        action="store_true",
        help="静默模式，只显示最终结果"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="运行测试模式"
    )
    
    args = parser.parse_args()
    
    if args.test:
        # 测试模式：运行多个测试问题
        test_questions = [
            "统计近1h，发起探测的探测设备(hostname)区分不同的任务(task_name）统计，分析这些设备的平均丢包和rtt情况",
            "查询最近30分钟的RTT平均值",
            "统计各省份的丢包率"
        ]
        
        print_section("测试模式")
        results = []
        for i, question in enumerate(test_questions, 1):
            print(f"\n测试 {i}/{len(test_questions)}")
            result = test_query(question, verbose=not args.quiet)
            results.append(result)
            if not result["success"]:
                print(f"❌ 测试 {i} 失败: {result.get('error', 'Unknown error')}")
            else:
                print(f"✅ 测试 {i} 成功")
        
        # 汇总
        success_count = sum(1 for r in results if r["success"])
        print_section(f"测试完成: {success_count}/{len(test_questions)} 成功")
        
        sys.exit(0 if success_count == len(test_questions) else 1)
    else:
        # 单次查询模式
        result = test_query(args.question, verbose=not args.quiet)
        
        if result["success"]:
            print("\n✅ 查询完成")
            sys.exit(0)
        else:
            print(f"\n❌ 查询失败: {result.get('error', 'Unknown error')}")
            sys.exit(1)


if __name__ == "__main__":
    main()

