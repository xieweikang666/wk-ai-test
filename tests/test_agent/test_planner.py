"""
查询规划器测试模块
"""
import pytest
from agent.simple_planner import SimpleQueryPlanner


class TestSimpleQueryPlanner:
    """查询规划器测试类"""
    
    def test_plan_device_quality_analysis(self, query_planner):
        """测试探测设备质量分析查询规划"""
        query = "统计近1h，发起探测的探测设备(hostname)区分不同的任务(task_name）统计，分析这些设备的平均丢包和rtt情况"
        
        plan = query_planner.plan(query)
        
        assert plan["action"] == "query"
        assert "avg_lost" in plan["metrics"]
        assert "avg_rtt" in plan["metrics"]
        assert plan["aggregation"] == "group_by_hostname_task"
        assert plan["filters"]["time_range"] == "last_1_hour"
        assert plan["original_query"] == query
    
    def test_plan_target_node_analysis(self, query_planner):
        """测试目标节点丢包分析查询规划"""
        query = "统计近1h的探测目标节点(target_node)丢包情况，区分不同的任务(task_name）统计"
        
        plan = query_planner.plan(query)
        
        assert plan["action"] == "query"
        assert "avg_lost" in plan["metrics"]
        assert "avg_rtt" in plan["metrics"
        assert plan["aggregation"] == "group_by_target_node_task"
        assert plan["filters"]["time_range"] == "last_1_hour"
    
    def test_plan_region_coverage_analysis(self, query_planner):
        """测试地区覆盖质量评估查询规划"""
        query = "统计近1h，各个目标节点(target_node)覆盖浙江电信(chinatelecom)浙江(zhejiang)的丢包情况"
        
        plan = query_planner.plan(query)
        
        assert plan["action"] == "query"
        assert "avg_lost" in plan["metrics"]
        assert "avg_rtt" in plan["metrics"
        assert plan["aggregation"] == "group_by_target_node"
        assert "chinatelecom" in plan["filters"]["src_isp"]
        assert "zhejiang" in plan["filters"]["src_province"]
    
    def test_time_range_parsing(self, query_planner):
        """测试时间范围解析"""
        # 测试1小时
        plan = query_planner.plan("查看近1h的网络质量")
        assert plan["filters"]["time_range"] == "last_1_hour"
        
        # 测试3小时
        plan = query_planner.plan("查看近3h的网络质量")
        assert plan["filters"]["time_range"] == "last_3_hour"
        
        # 测试24小时
        plan = query_planner.plan("查看近24h的网络质量")
        assert plan["filters"]["time_range"] == "last_24_hour"
    
    def test_empty_query(self, query_planner):
        """测试空查询处理"""
        with pytest.raises(ValueError, match="用户问题不能为空"):
            query_planner.plan("")
    
    def test_isp_parsing(self, query_planner):
        """测试运营商解析"""
        plan = query_planner.plan("分析电信和移动的网络质量")
        assert "chinatelecom" in plan["filters"]["src_isp"]
        assert "chinamobile" in plan["filters"]["src_isp"]
    
    def test_province_parsing(self, query_planner):
        """测试省份解析"""
        plan = query_planner.plan("分析浙江和江苏的网络质量")
        assert "zhejiang" in plan["filters"]["src_province"]
        assert "jiangsu" in plan["filters"]["src_province"]