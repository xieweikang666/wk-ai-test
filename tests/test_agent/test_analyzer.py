"""
数据分析器测试模块
"""
import pytest
from unittest.mock import patch, Mock
import pandas as pd
from agent.analyzer import analyze_result, _prepare_data_summary


class TestAnalyzer:
    """数据分析器测试类"""
    
    def test_prepare_data_summary_empty(self):
        """测试空数据处理"""
        result = _prepare_data_summary(pd.DataFrame())
        assert result == "数据为空"
    
    def test_prepare_data_summary_none(self):
        """测试None数据处理"""
        result = _prepare_data_summary(None)
        assert result == "数据为空"
    
    def test_prepare_device_summary(self, sample_dataframe):
        """测试设备数据摘要"""
        result = _prepare_data_summary(sample_dataframe)
        
        assert "数据概览" in result
        assert "关键指标分析" in result
        assert "探测设备质量数据" in result
        assert "AMCDN1YZ1P6001156" in result or "host1" in result
    
    def test_prepare_target_node_summary(self, sample_dataframe):
        """测试目标节点数据摘要"""
        # 重命名列以模拟目标节点数据
        node_df = sample_dataframe.rename(columns={'hostname': 'target_node'})
        result = _prepare_data_summary(node_df)
        
        assert "目标节点性能数据" in result
        assert "性能最佳TOP3" in result
        assert "性能最差TOP3" in result
    
    def test_analyze_result_empty_dataframe(self):
        """测试空DataFrame分析"""
        result = analyze_result(pd.DataFrame(), {})
        assert result == "查询结果为空，无法进行分析。"
    
    def test_analyze_result_none_dataframe(self):
        """测试None DataFrame分析"""
        result = analyze_result(None, {})
        assert result == "查询结果为空，无法进行分析。"
    
    def test_analyze_result_empty_query_plan(self, sample_dataframe):
        """测试空查询计划分析"""
        result = analyze_result(sample_dataframe, {})
        assert result == "缺少查询计划信息，无法进行分析。"
    
    @patch('agent.analyzer.get_llm_client')
    def test_analyze_result_success(self, mock_llm, sample_dataframe, mock_llm_response):
        """测试成功分析结果"""
        # 设置mock
        mock_client = Mock()
        mock_client.chat.return_value = mock_llm_response
        mock_llm.return_value = mock_client
        
        query_plan = {
            "original_query": "测试查询",
            "metrics": ["avg_lost", "avg_rtt"],
            "aggregation": "group_by_hostname_task"
        }
        
        result = analyze_result(sample_dataframe, query_plan)
        
        assert result == mock_llm_response["content"]
        mock_client.chat.assert_called_once()
    
    @patch('agent.analyzer.get_llm_client')
    def test_analyze_result_llm_failure(self, mock_llm, sample_dataframe):
        """测试LLM调用失败处理"""
        # 设置mock抛出异常
        mock_llm.side_effect = Exception("LLM调用失败")
        
        query_plan = {
            "original_query": "测试查询",
            "metrics": ["avg_lost", "avg_rtt"],
            "aggregation": "group_by_hostname_task"
        }
        
        result = analyze_result(sample_dataframe, query_plan)
        
        assert "结果分析失败" in result
        assert "LLM调用失败" in result