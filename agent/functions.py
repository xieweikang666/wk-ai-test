"""
Function Calling 实现
包含 run_query, draw_chart, explain_result 等函数
"""
import logging
from typing import Dict, Any, Optional
import pandas as pd

from db.clickhouse_client import get_client
from utils.time_utils import parse_time_range
from utils.chart import draw_chart
from agent.simple_analyzer import analyze_result
from config.settings import settings

logger = logging.getLogger(__name__)


class QueryPlanExecutor:
    """QueryPlan 执行器"""
    
    def __init__(self):
        """初始化执行器"""
        self.client = get_client()
    
    def run_query(self, query_plan: Dict[str, Any]) -> pd.DataFrame:
        """
        根据 QueryPlan 生成 SQL 并执行查询
        
        Args:
            query_plan: QueryPlan 字典
            
        Returns:
            查询结果 DataFrame
        """
        if not query_plan:
            raise ValueError("QueryPlan 不能为空")
        
        # 生成 SQL
        sql = self._generate_sql(query_plan)
        
        # 执行查询
        df = self.client.execute_query(sql)
        
        return df
    
    def get_generated_sql(self, plan: Dict[str, Any]) -> str:
        """
        获取生成的 SQL（公开方法，用于展示）
        
        Args:
            plan: QueryPlan 字典
            
        Returns:
            SQL 语句
        """
        return self._generate_sql(plan)
    
    def _generate_sql(self, plan: Dict[str, Any]) -> str:
        """
        根据 QueryPlan 生成 SQL（卫语句设计）
        
        Args:
            plan: QueryPlan 字典
            
        Returns:
            SQL 语句
        """
        if not plan:
            raise ValueError("QueryPlan 不能为空")
        
        # 解析 QueryPlan
        metrics = plan.get("metrics", [])
        if not metrics:
            raise ValueError("metrics 不能为空")
        
        filters = plan.get("filters", {})
        if not filters:
            raise ValueError("filters 不能为空")
        
        time_range = filters.get("time_range")
        if not time_range:
            raise ValueError("filters 必须包含 time_range")
        
        # 解析时间范围
        start_ts, end_ts = parse_time_range(time_range)
        
        # 构建 SELECT 子句
        select_parts = []
        for metric in metrics:
            if metric == "avg_rtt":
                select_parts.append("AVG(avg_rtt) as avg_rtt")
            elif metric == "avg_lost":
                select_parts.append("AVG(avg_lost) as avg_lost")
            elif metric == "max_rtt":
                select_parts.append("MAX(avg_rtt) as max_rtt")
            elif metric == "min_rtt":
                select_parts.append("MIN(avg_rtt) as min_rtt")
            elif metric == "device_count":
                select_parts.append("COUNT(DISTINCT hostname) as device_count")
            else:
                select_parts.append(f"AVG({metric}) as {metric}")
        
        # 添加计数
        select_parts.append("COUNT(*) as count")
        
        # 构建 GROUP BY 子句
        group_by_parts = []
        aggregation = plan.get("aggregation", "none")
        
        if aggregation == "group_by_province":
            group_by_parts.append("src_province")
            select_parts.insert(0, "src_province")
        elif aggregation == "group_by_isp":
            group_by_parts.append("src_isp")
            select_parts.insert(0, "src_isp")
        elif aggregation == "group_by_task":
            group_by_parts.append("task_name")
            select_parts.insert(0, "task_name")
        elif aggregation == "group_by_target_node":
            group_by_parts.append("target_node")
            select_parts.insert(0, "target_node")
        elif aggregation == "group_by_time_hour":
            group_by_parts.append("toStartOfHour(toDateTime(timestamp)) as hour")
            select_parts.insert(0, "toStartOfHour(toDateTime(timestamp)) as hour")
        elif aggregation == "group_by_province_isp":
            group_by_parts.extend(["src_province", "src_isp"])
            select_parts.insert(0, "src_province")
            select_parts.insert(1, "src_isp")
        elif aggregation == "group_by_hostname_task":
            group_by_parts.extend(["hostname", "task_name"])
            select_parts.insert(0, "hostname")
            select_parts.insert(1, "task_name")
        
        # 构建 WHERE 子句
        where_parts = [
            f"timestamp >= {start_ts}",
            f"timestamp <= {end_ts}"
        ]
        
        # 添加过滤条件
        task_name = plan.get("task_name")
        if task_name:
            where_parts.append(f"task_name = '{task_name}'")
        
        src_isp_list = filters.get("src_isp", [])
        if src_isp_list:
            isp_values = "', '".join(src_isp_list)
            where_parts.append(f"src_isp IN ('{isp_values}')")
        
        src_province_list = filters.get("src_province", [])
        if src_province_list:
            province_values = "', '".join(src_province_list)
            where_parts.append(f"src_province IN ('{province_values}')")
        
        target_node_list = filters.get("target_node", [])
        if target_node_list:
            node_values = "', '".join(target_node_list)
            where_parts.append(f"target_node IN ('{node_values}')")
        
        # 组装 SQL
        sql = f"SELECT {', '.join(select_parts)}\n"
        sql += f"FROM {settings.CLICKHOUSE_DATABASE}.{settings.CLICKHOUSE_TABLE_PING}\n"
        sql += f"WHERE {' AND '.join(where_parts)}\n"
        
        if group_by_parts:
            sql += f"GROUP BY {', '.join(group_by_parts)}\n"
        
        # ORDER BY（如果有时间聚合，按时间排序）
        if aggregation == "group_by_time_hour":
            sql += "ORDER BY hour\n"
        elif group_by_parts:
            # 按第一个聚合字段排序
            sql += f"ORDER BY {group_by_parts[0]}\n"
        
        # LIMIT 会在 clickhouse_client 中自动添加
        
        logger.info(f"生成的 SQL:\n{sql}")
        return sql
    
    def draw_chart_wrapper(
        self,
        df: pd.DataFrame,
        chart_type: str = "line",
        title: Optional[str] = None
    ) -> Optional[str]:
        """
        生成图表（包装函数）
        
        Args:
            df: 数据 DataFrame
            chart_type: 图表类型
            title: 图表标题
            
        Returns:
            图表路径，失败返回 None
        """
        if df is None or df.empty:
            logger.warning("数据为空，无法生成图表")
            return None
        
        try:
            chart_path = draw_chart(
                df=df,
                chart_type=chart_type,
                title=title
            )
            logger.info(f"图表生成成功: {chart_path}")
            return chart_path
        except Exception as e:
            logger.error(f"图表生成失败: {e}")
            return None
    
    def explain_result(
        self,
        df: pd.DataFrame,
        query_plan: Dict[str, Any],
        chart_path: Optional[str] = None
    ) -> str:
        """
        使用 LLM 分析查询结果
        
        Args:
            df: 查询结果 DataFrame
            query_plan: 原始 QueryPlan
            chart_path: 图表路径（可选）
            
        Returns:
            分析结果文本
        """
        if df is None or df.empty:
            return "查询结果为空，无法进行分析。"
        
        try:
            analysis = analyze_result(df, query_plan, chart_path)
            return analysis
        except Exception as e:
            logger.error(f"结果分析失败: {e}")
            return f"结果分析失败: {str(e)}"


# 全局执行器实例（懒加载）
_executor: Optional[QueryPlanExecutor] = None


def get_executor() -> QueryPlanExecutor:
    """
    获取 QueryPlan 执行器实例（单例模式）
    
    Returns:
        QueryPlanExecutor 实例
    """
    global _executor
    
    if _executor is not None:
        return _executor
    
    _executor = QueryPlanExecutor()
    return _executor

