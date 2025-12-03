#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 LLM 客户端修复
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_llm_init():
    """测试 LLM 客户端初始化"""
    print("="*70)
    print("测试 LLM 客户端初始化")
    print("="*70)
    print()
    
    try:
        from agent.llm import get_llm_client
        print("1. 导入 LLM 模块... ✓")
        
        print("2. 初始化 LLM 客户端...")
        llm = get_llm_client()
        print("   ✓ LLM 客户端初始化成功")
        print(f"   ✓ 模型: {llm.model}")
        print(f"   ✓ 客户端类型: {type(llm.client)}")
        
        print("\n✅ LLM 客户端初始化测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ LLM 客户端初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_llm_init()
    sys.exit(0 if success else 1)


