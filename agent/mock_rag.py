#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock RAG 模块 - 用于测试时绕过 sentence-transformers 依赖问题
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class MockRAGRetriever:
    """Mock RAG 检索器"""
    
    def __init__(self, schema_path: str = None):
        """初始化 Mock RAG"""
        logger.info("使用 Mock RAG 检索器")
        self.schema_docs = [
            "detect_ping_log 表包含字段: hostname, task_name, timestamp, avg_rtt, avg_lost, src_isp, src_province",
            "hostname: 探测设备主机名",
            "task_name: 任务名称",
            "timestamp: Unix时间戳",
            "avg_rtt: 平均RTT延迟",
            "avg_lost: 丢包率",
            "src_isp: 源ISP运营商",
            "src_province: 源省份"
        ]
    
    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """Mock 检索，返回固定的schema信息"""
        logger.info(f"Mock检索查询: {query}")
        return self.schema_docs[:top_k]
    
    def get_context(self, query: str) -> str:
        """获取上下文，返回schema信息"""
        logger.info(f"Mock获取上下文: {query}")
        return "\n".join(self.schema_docs)

def get_retriever(schema_path: str = None) -> MockRAGRetriever:
    """获取Mock检索器"""
    return MockRAGRetriever(schema_path)