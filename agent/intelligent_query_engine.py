"""
智能分析执行引擎
整合SQL生成、质量保障和分析结果生成
"""
import logging
from typing import Dict, Any, Optional
import pandas as pd

from agent.query_quality_guard import QueryQualityGuard
from agent.intelligent_analyzer import IntelligentAnalyzer
from utils.chart import draw_chart

logger = logging.getLogger(__name__)


class IntelligentQueryEngine:
    """智能查询执行引擎"""
    
    def __init__(self):
        """初始化查询引擎"""
        self.quality_guard = QueryQualityGuard()
        self.analyzer = IntelligentAnalyzer()
    
    def execute_intelligent_query(self, 
                                user_query: str, 
                                query_plan: Dict[str, Any],
                                enable_quality_check: bool = True) -> Dict[str, Any]:
        """
        执行智能查询
        
        Args:
            user_query: 用户原始查询
            query_plan: 查询计划
            enable_quality_check: 是否启用质量检查
            
        Returns:
            完整的查询结果
        """
        result = {
            "success": False,
            "data": None,
            "analysis": None,
            "chart_path": None,
            "sql": None,
            "quality_report": None,
            "error": None
        }
        
        try:
            logger.info(f"开始执行智能查询: {user_query}")
            
            if enable_quality_check:
                # 带质量检查的执行
                df, quality_report = self.quality_guard.execute_query_with_quality_check(
                    user_query, query_plan
                )
                result["quality_report"] = quality_report
                
                if df.empty:
                    result["error"] = "查询结果为空或执行失败"
                    result["sql"] = "执行失败"
                    return result
                
                # 如果质量分数过低，提供警告
                if quality_report["overall_score"] < 60:
                    logger.warning(f"查询质量分数较低: {quality_report['overall_score']:.1f}")
            else:
                # 直接执行（原有逻辑）
                from agent.intelligent_sql_generator import IntelligentSQLGenerator
                from db.clickhouse_client import get_client
                
                sql_generator = IntelligentSQLGenerator()
                client = get_client()
                
                sql = sql_generator.generate_sql(user_query, query_plan)
                df = client.execute_query(sql)
                result["sql"] = sql
                
                if df is None or df.empty:
                    result["error"] = "查询结果为空"
                    return result
            
            result["data"] = df
            
            # 生成智能分析
            logger.info("开始生成智能分析...")
            analysis = self.analyzer.analyze_with_intelligence(
                df=df,
                user_query=user_query,
                query_plan=query_plan
            )
            result["analysis"] = analysis
            
            # 生成图表（如果需要）
            if query_plan.get("need_chart", False):
                chart_type = query_plan.get("chart_type", "bar")
                try:
                    chart_path = draw_chart(
                        df=df,
                        chart_type=chart_type,
                        title=f"网络质量分析 - {user_query[:30]}"
                    )
                    result["chart_path"] = chart_path
                    logger.info(f"图表生成成功: {chart_path}")
                except Exception as e:
                    logger.warning(f"图表生成失败: {e}")
            
            result["success"] = True
            logger.info("智能查询执行完成")
            
            return result
            
        except Exception as e:
            logger.error(f"智能查询执行失败: {e}", exc_info=True)
            result["error"] = f"查询执行失败: {str(e)}"
            return result
    
    def get_query_explanation(self, user_query: str, query_plan: Dict[str, Any]) -> str:
        """生成查询解释说明"""
        
        explanation_parts = [
            f"**查询理解**：{user_query}",
            "",
            "**执行计划**："
        ]
        
        # 解析查询计划的关键信息
        metrics = query_plan.get("metrics", [])
        if metrics:
            metric_names = []
            for metric in metrics:
                if metric == "avg_rtt":
                    metric_names.append("平均延迟(RTT)")
                elif metric == "avg_lost":
                    metric_names.append("平均丢包率")
                else:
                    metric_names.append(metric)
            explanation_parts.append(f"- 分析指标：{', '.join(metric_names)}")
        
        filters = query_plan.get("filters", {})
        time_range = filters.get("time_range", "")
        if time_range:
            explanation_parts.append(f"- 时间范围：{time_range}")
        
        src_isp = filters.get("src_isp", [])
        if src_isp:
            isp_names = []
            for isp in src_isp:
                if isp == "chinatelecom":
                    isp_names.append("电信")
                elif isp == "chinamobile":
                    isp_names.append("移动")
                elif isp == "chinaunicom":
                    isp_names.append("联通")
                else:
                    isp_names.append(isp)
            explanation_parts.append(f"- 运营商筛选：{', '.join(isp_names)}")
        
        aggregation = query_plan.get("aggregation", "none")
        if aggregation != "none":
            aggregation_desc = self._get_aggregation_description(aggregation)
            explanation_parts.append(f"- 数据聚合：{aggregation_desc}")
        
        explanation_parts.extend([
            "",
            "**查询特点**：",
            "- 使用智能SQL生成，确保查询准确性和性能",
            "- 多维度数据质量检查，保障分析可靠性",
            "- 基于LLM的深度分析，提供个性化洞察",
            "- 自动识别异常和趋势，生成可操作建议"
        ])
        
        return "\n".join(explanation_parts)
    
    def _get_aggregation_description(self, aggregation: str) -> str:
        """获取聚合方式描述"""
        descriptions = {
            "group_by_province": "按省份分组统计",
            "group_by_isp": "按运营商分组统计", 
            "group_by_task": "按任务类型分组统计",
            "group_by_target_node": "按目标节点分组统计",
            "group_by_time_hour": "按时间(小时)趋势分析",
            "group_by_province_isp": "按省份和运营商交叉分析",
            "group_by_hostname_task": "按探测设备和任务类型分析",
            "group_by_target_node_task": "按目标节点和任务类型分析",
            "group_by_target_node_province_isp": "按目标节点、省份和运营商综合分析"
        }
        
        return descriptions.get(aggregation, "自定义聚合方式")
    
    def generate_response_format(self, query_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成标准化的响应格式"""
        
        if not query_result["success"]:
            return {
                "answer": f"❌ 查询执行失败：{query_result['error']}",
                "chart_url": None,
                "sql": query_result.get("sql"),
                "quality_summary": None
            }
        
        response = {
            "answer": query_result["analysis"],
            "chart_url": query_result.get("chart_path"),
            "sql": query_result.get("sql"),
            "quality_summary": None
        }
        
        # 添加质量摘要
        quality_report = query_result.get("quality_report")
        if quality_report:
            quality_score = quality_report.get("overall_score", 0)
            if quality_score >= 80:
                quality_emoji = "🟢"
                quality_text = "优秀"
            elif quality_score >= 60:
                quality_emoji = "🟡"
                quality_text = "良好"
            else:
                quality_emoji = "🔴"
                quality_text = "需改进"
            
            response["quality_summary"] = f"{quality_emoji} 查询质量：{quality_text} ({quality_score:.1f}/100)"
        
        return response


# 向后兼容的包装器
def create_enhanced_functions_executor():
    """创建增强版函数执行器，保持与原有代码的兼容性"""
    
    class EnhancedQueryExecutor:
        """增强版查询执行器"""
        
        def __init__(self):
            self.engine = IntelligentQueryEngine()
        
        def run_query(self, query_plan: Dict[str, Any]) -> pd.DataFrame:
            """执行查询（兼容原接口）"""
            original_query = query_plan.get("original_query", "")
            
            # 使用智能引擎执行查询
            result = self.engine.execute_intelligent_query(
                user_query=original_query,
                query_plan=query_plan,
                enable_quality_check=True  # 默认启用质量检查
            )
            
            if result["success"]:
                # 缓存结果供其他方法使用
                self._last_result = result
                return result["data"]
            else:
                raise Exception(f"查询执行失败: {result['error']}")
        
        def get_generated_sql(self, query_plan: Dict[str, Any]) -> str:
            """获取生成的SQL（兼容原接口）"""
            if hasattr(self, '_last_result') and self._last_result:
                return self._last_result.get("sql", "")
            
            # 如果没有缓存的查询结果，重新生成SQL
            from agent.intelligent_sql_generator import IntelligentSQLGenerator
            generator = IntelligentSQLGenerator()
            original_query = query_plan.get("original_query", "")
            return generator.generate_sql(original_query, query_plan)
        
        def explain_result(self, 
                          df: pd.DataFrame,
                          query_plan: Dict[str, Any], 
                          chart_path: Optional[str] = None) -> str:
            """解释结果（兼容原接口）"""
            if hasattr(self, '_last_result') and self._last_result:
                return self._last_result.get("analysis", "")
            
            # 如果没有缓存的分析结果，重新生成分析
            original_query = query_plan.get("original_query", "")
            analysis = self.engine.analyzer.analyze_with_intelligence(
                df=df,
                user_query=original_query,
                query_plan=query_plan,
                chart_path=chart_path
            )
            return analysis
        
        def draw_chart_wrapper(self, 
                             df: pd.DataFrame,
                             chart_type: str = "line",
                             title: Optional[str] = None) -> Optional[str]:
            """生成图表（兼容原接口）"""
            try:
                return draw_chart(df=df, chart_type=chart_type, title=title)
            except Exception as e:
                logger.error(f"图表生成失败: {e}")
                return None
    
    return EnhancedQueryExecutor()


# 全局执行器实例
_enhanced_executor = None

def get_enhanced_executor():
    """获取增强版执行器实例（单例模式）"""
    global _enhanced_executor
    
    if _enhanced_executor is not None:
        return _enhanced_executor
    
    _enhanced_executor = create_enhanced_functions_executor()
    return _enhanced_executor