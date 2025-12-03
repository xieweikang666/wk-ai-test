#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试 CLI 功能
"""
import sys
import os
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接调用 CLI 的 test_query 函数
from cli import test_query

if __name__ == "__main__":
    question = "统计近1h，发起探测的探测设备(hostname)区分不同的任务(task_name）统计，分析这些设备的平均丢包和rtt情况"
    
    print("="*70)
    print("CLI 模式测试")
    print("="*70)
    print()
    
    result = test_query(question, verbose=True)
    
    if result["success"]:
        print("\n" + "="*70)
        print("测试结果分析")
        print("="*70)
        
        # 分析 SQL 质量
        sql = result.get("sql", "")
        print("\n1. SQL 质量评估:")
        print("-" * 70)
        
        sql_quality = {
            "时间范围": "✓" if "last_1_hour" in str(result.get("query_plan", {})) or "timestamp >=" in sql else "✗",
            "GROUP BY": "✓" if "GROUP BY" in sql and "hostname" in sql and "task_name" in sql else "✗",
            "聚合函数": "✓" if "AVG" in sql and ("avg_rtt" in sql or "avg_lost" in sql) else "✗",
            "字段选择": "✓" if "hostname" in sql and "task_name" in sql else "✗"
        }
        
        for key, value in sql_quality.items():
            print(f"  {key}: {value}")
        
        # 分析查询结果
        rows = result.get("rows", 0)
        print(f"\n2. 查询结果:")
        print(f"  返回行数: {rows}")
        
        # 分析回答质量
        answer = result.get("answer", "")
        print(f"\n3. 分析结果质量:")
        print(f"  回答长度: {len(answer)} 字符")
        if answer:
            print(f"  是否包含数据洞察: {'✓' if len(answer) > 100 else '✗'}")
        
        print("\n" + "="*70)
        print("✅ 测试完成")
        print("="*70)
    else:
        print(f"\n❌ 测试失败: {result.get('error', 'Unknown error')}")
        sys.exit(1)


