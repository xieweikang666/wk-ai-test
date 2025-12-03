"""
pytest 配置文件
定义测试夹具和通用配置
"""
import pytest
import asyncio
import pandas as pd
from unittest.mock import Mock, patch
from agent.simple_planner import SimpleQueryPlanner
from agent.functions import QueryPlanExecutor
from config.settings import Settings


@pytest.fixture
def sample_dataframe():
    """提供示例 DataFrame 用于测试"""
    return pd.DataFrame({
        'hostname': ['host1', 'host2', 'host3'],
        'target_node': ['node1', 'node2', 'node3'],
        'avg_lost': [0.5, 1.2, 2.1],
        'avg_rtt': [30.5, 45.2, 60.8],
        'count': [1000, 2000, 1500],
        'src_isp': ['chinatelecom', 'chinamobile', 'chinaunicom'],
        'src_province': ['zhejiang', 'jiangsu', 'beijing'],
        'task_name': ['task1', 'task2', 'task3']
    })


@pytest.fixture
def mock_settings():
    """提供模拟配置"""
    return Settings(
        OPENAI_API_KEY="test_key",
        CLICKHOUSE_PASSWORD="test_password",
        CLICKHOUSE_ENABLE=False  # 测试时禁用数据库连接
    )


@pytest.fixture
def query_planner():
    """提供查询规划器实例"""
    return SimpleQueryPlanner()


@pytest.fixture
def query_executor():
    """提供查询执行器实例"""
    return QueryPlanExecutor()


@pytest.fixture
def mock_llm_response():
    """提供模拟的 LLM 响应"""
    return {
        "content": "这是一个测试分析结果，包含具体的设备名称和性能数据。"
    }


# 异步测试支持
@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于异步测试"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Mock 配置
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """模拟环境变量"""
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")
    monkeypatch.setenv("CLICKHOUSE_PASSWORD", "test_password")
    monkeypatch.setenv("LOG_LEVEL", "ERROR")  # 测试时减少日志输出