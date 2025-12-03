#!/usr/bin/env python3
"""
API 测试脚本
"""
import requests
import json
import sys

def test_chat_api(question: str, base_url: str = "http://localhost:8000"):
    """测试 /chat API"""
    url = f"{base_url}/chat"
    
    print(f"\n{'='*60}")
    print(f"测试问题: {question}")
    print(f"{'='*60}\n")
    
    try:
        response = requests.post(
            url,
            json={"message": question},
            timeout=300  # 5分钟超时
        )
        
        if response.status_code != 200:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
        
        result = response.json()
        
        print("✅ 请求成功\n")
        print(f"{'='*60}")
        print("生成的 SQL:")
        print(f"{'='*60}")
        print(result.get("sql", "N/A"))
        print()
        
        print(f"{'='*60}")
        print("分析结果:")
        print(f"{'='*60}")
        print(result.get("answer", "N/A"))
        print()
        
        if result.get("chart_url"):
            print(f"{'='*60}")
            print(f"图表路径: {result['chart_url']}")
            print(f"访问地址: {base_url}{result['chart_url']}")
            print(f"{'='*60}\n")
        
        return result
        
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保服务已启动 (python3 app.py)")
        return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "统计近1h，发起探测的探测设备(hostname)区分不同的任务(task_name）统计，分析这些设备的平均丢包和rtt情况"
    
    result = test_chat_api(question)
    
    if result:
        print("✅ 测试完成")
    else:
        print("❌ 测试失败")
        sys.exit(1)

