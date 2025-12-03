"""
简化版查询规划器 - 不使用Function Calling
"""
import json
import logging
import re
from typing import Dict, Any
from agent.llm import get_llm_client

logger = logging.getLogger(__name__)

class SimpleQueryPlanner:
    """简化的查询规划器"""
    
    def __init__(self):
        """初始化规划器"""
        self.llm = get_llm_client()
    
    def plan(self, user_query: str) -> Dict[str, Any]:
        """
        将用户问题转换为 QueryPlan（简化版本）
        
        Args:
            user_query: 用户问题，如："查看浙江电信的网络覆盖质量"
            
        Returns:
            QueryPlan 字典
        """
        if not user_query:
            raise ValueError("用户问题不能为空")
        
        # 简化版本：使用规则匹配
        query_plan = {
            "action": "query",
            "metrics": [],
            "filters": {
                "time_range": "last_1_hour"  # 默认近1小时
            },
            "aggregation": "none",
            "need_chart": False,
            "original_query": user_query  # 保存原始问题
        }
        
        # 解析时间范围
        if "近1h" in user_query or "近1小时" in user_query:
            query_plan["filters"]["time_range"] = "last_1_hour"
        elif "近3h" in user_query or "近3小时" in user_query:
            query_plan["filters"]["time_range"] = "last_3_hour"
        elif "近24h" in user_query or "近24小时" in user_query:
            query_plan["filters"]["time_range"] = "last_24_hour"
        
        # 解析指标
        if "丢包" in user_query or "packet_loss" in user_query.lower():
            query_plan["metrics"].append("avg_lost")
        if "延迟" in user_query or "rtt" in user_query.lower() or "响应时间" in user_query:
            query_plan["metrics"].append("avg_rtt")
        if "质量" in user_query or "覆盖" in user_query or "性能" in user_query:
            # 质量分析需要丢包和延迟两个指标
            if "avg_lost" not in query_plan["metrics"]:
                query_plan["metrics"].append("avg_lost")
            if "avg_rtt" not in query_plan["metrics"]:
                query_plan["metrics"].append("avg_rtt")
        
        # 如果没有明确指定指标，默认使用丢包率
        if not query_plan["metrics"]:
            query_plan["metrics"] = ["avg_lost"]
        
        # 解析运营商
        isps = ["chinatelecom", "chinamobile", "chinaunicom", "chinatietong"]
        isp_names = ["电信", "移动", "联通", "铁通"]
        for isp, name in zip(isps, isp_names):
            if name in user_query or isp in user_query.lower():
                if "src_isp" not in query_plan["filters"]:
                    query_plan["filters"]["src_isp"] = []
                query_plan["filters"]["src_isp"].append(isp)
        
        # 解析省份
        provinces = ["zhejiang", "jiangsu", "beijing", "shanghai", "guangdong", "liaoning"]
        province_names = ["浙江", "江苏", "北京", "上海", "广东", "辽宁"]
        for province, name in zip(provinces, province_names):
            if name in user_query:
                if "src_province" not in query_plan["filters"]:
                    query_plan["filters"]["src_province"] = []
                query_plan["filters"]["src_province"].append(province)
        
        # 解析目标节点相关查询 - 优先处理
        if "目标节点" in user_query or "target_node" in user_query:
            query_plan["metrics"] = ["avg_lost", "avg_rtt"]
            if "地区" in user_query or "src_isp" in user_query or "src_province" in user_query:
                # 目标节点覆盖地区分析
                query_plan["aggregation"] = "group_by_target_node_province_isp"
            else:
                # 目标节点丢包分析（按task_name分组，但查询target_node）
                query_plan["aggregation"] = "group_by_target_node_task"
        # 解析设备相关查询 - 需要更精确的匹配
        elif ("探测设备" in user_query and "hostname" in user_query) or ("发起探测" in user_query and "hostname" in user_query):
            if "各运营商" in user_query or "运营商" in user_query:
                # 按运营商统计设备数量
                query_plan["aggregation"] = "group_by_isp"
                query_plan["metrics"] = ["device_count"]
            else:
                # 分析设备质量
                query_plan["aggregation"] = "group_by_hostname_task"
                query_plan["metrics"] = ["avg_lost", "avg_rtt"]
        
        # 解析地区覆盖查询 - 但不要覆盖已有的aggregation
        if "覆盖" in user_query and ("地区" in user_query or "省份" in user_query):
            if query_plan["aggregation"] == "none":  # 只有在未设置时才设置
                query_plan["aggregation"] = "group_by_province_isp"
        
        # 解析任务相关查询 - 但不要覆盖已有的aggregation
        if "任务" in user_query or "task_name" in user_query:
            if query_plan["aggregation"] == "none":  # 只有在未设置时才设置
                query_plan["aggregation"] = "group_by_hostname_task"
        
        # 解析是否需要图表
        if "图" in user_query or "趋势" in user_query or "对比" in user_query:
            query_plan["need_chart"] = True
            query_plan["chart_type"] = "bar" if "对比" in user_query else "line"
        
        logger.info(f"生成QueryPlan: {json.dumps(query_plan, ensure_ascii=False, indent=2)}")
        return query_plan


# 全局规划器实例（懒加载）
_planner: SimpleQueryPlanner = None

def get_planner():
    """
    获取查询规划器实例（单例模式）
    
    Returns:
        SimpleQueryPlanner 实例
    """
    global _planner
    
    if _planner is not None:
        return _planner
    
    _planner = SimpleQueryPlanner()
    return _planner