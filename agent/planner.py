"""
用户意图规划器
将用户问题转换为 QueryPlan（结构化查询计划）
"""
import json
import logging
from typing import Dict, Any, Optional, List
from agent.llm import get_llm_client

logger = logging.getLogger(__name__)

try:
    from agent.rag import get_retriever
except ImportError:
    from agent.mock_rag import get_retriever
    logger.warning("使用 Mock RAG 模块")


class QueryPlanner:
    """查询规划器"""
    
    # Function Calling 定义：生成 QueryPlan
    QUERY_PLAN_FUNCTION = {
        "name": "generate_query_plan",
        "description": "根据用户问题生成结构化查询计划（QueryPlan）",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["query"],
                    "description": "操作类型，目前只支持 query"
                },
                "metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "需要查询的指标列表，如：avg_rtt, avg_lost"
                },
                "task_name": {
                    "type": "string",
                    "description": "任务名称过滤，如：edge_l1_detect，如果不需要过滤则设为 null"
                },
                "filters": {
                    "type": "object",
                    "description": "过滤条件",
                    "properties": {
                        "src_isp": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "源运营商列表，如：['chinatelecom', 'chinamobile']"
                        },
                        "src_province": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "源省份列表，如：['liaoning', 'beijing']"
                        },
                        "target_node": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "目标节点列表"
                        },
                        "time_range": {
                            "type": "string",
                            "description": "时间范围，格式：last_30_min, last_1_hour, last_24_hour, 或 between:start:end"
                        }
                    }
                },
                "aggregation": {
                    "type": "string",
                    "enum": [
                        "none",
                        "group_by_province",
                        "group_by_isp",
                        "group_by_task",
                        "group_by_target_node",
                        "group_by_time_hour",
                        "group_by_province_isp",
                        "group_by_hostname_task"
                    ],
                    "description": "聚合方式"
                },
                "need_chart": {
                    "type": "boolean",
                    "description": "是否需要生成图表"
                },
                "chart_type": {
                    "type": "string",
                    "enum": ["line", "bar", "scatter", "histogram"],
                    "description": "图表类型，仅在 need_chart=true 时有效"
                }
            },
            "required": ["action", "metrics", "filters", "aggregation", "need_chart"]
        }
    }
    
    def __init__(self):
        """初始化规划器"""
        self.llm = get_llm_client()
        self.rag = get_retriever()
    
    def plan(self, user_query: str) -> Dict[str, Any]:
        """
        将用户问题转换为 QueryPlan
        
        Args:
            user_query: 用户问题
            
        Returns:
            QueryPlan 字典
        """
        if not user_query:
            raise ValueError("用户问题不能为空")
        
        # 通过 RAG 获取数据库上下文
        context = self._get_database_context(user_query)
        
        # 构建提示词
        messages = self._build_messages(user_query, context)
        
        # 调用 LLM 生成 QueryPlan
        response = self.llm.chat(
            messages=messages,
            functions=[self.QUERY_PLAN_FUNCTION],
            function_call="auto"
        )
        
        # 解析 Function Calling 结果
        query_plan = self._parse_function_call(response)
        
        # 验证 QueryPlan
        self._validate_plan(query_plan)
        
        logger.info(f"QueryPlan 生成成功: {json.dumps(query_plan, ensure_ascii=False, indent=2)}")
        return query_plan
    
    def _get_database_context(self, query: str) -> str:
        """
        通过 RAG 获取数据库上下文
        
        Args:
            query: 用户查询
            
        Returns:
            数据库上下文字符串
        """
        if not query:
            return ""
        
        try:
            context = self.rag.get_context(query, top_k=3)
            if context:
                logger.info("RAG 检索到数据库上下文")
            return context
        except Exception as e:
            logger.warning(f"RAG 检索失败: {e}")
            return ""
    
    def _build_messages(self, user_query: str, context: str) -> List[Dict[str, str]]:
        """
        构建 LLM 消息列表
        
        Args:
            user_query: 用户问题
            context: 数据库上下文
            
        Returns:
            消息列表
        """
        system_prompt = """你是一个专业的数据库查询规划助手。你的任务是根据用户的问题，生成结构化的查询计划（QueryPlan）。

关键要求：
1. 必须包含时间范围（time_range），格式：last_30_min, last_1_hour, last_24_hour 等
2. 根据用户问题选择合适的指标（metrics）：avg_rtt（平均延迟）、avg_lost（丢包率）
3. 根据用户问题选择合适的过滤条件（filters）：src_isp（运营商）、src_province（省份）、target_node（目标节点）
4. 根据用户问题选择合适的聚合方式（aggregation）
5. 如果用户要求画图或查看趋势，设置 need_chart=true 并选择合适的 chart_type

使用以下数据库上下文信息来帮助生成准确的查询计划："""
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        if context:
            messages.append({
                "role": "system",
                "content": f"\n\n数据库上下文：\n{context}"
            })
        
        messages.append({
            "role": "user",
            "content": user_query
        })
        
        return messages
    
    def _parse_function_call(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析 Function Calling 响应
        
        Args:
            response: LLM 响应
            
        Returns:
            QueryPlan 字典
        """
        if not response:
            raise ValueError("LLM 响应为空")
        
        function_call = response.get("function_call")
        if not function_call:
            raise ValueError("LLM 未返回 Function Calling 结果")
        
        function_name = function_call.get("name")
        if function_name != "generate_query_plan":
            raise ValueError(f"Function 名称不匹配: {function_name}")
        
        arguments_str = function_call.get("arguments")
        if not arguments_str:
            raise ValueError("Function 参数为空")
        
        try:
            query_plan = json.loads(arguments_str)
            return query_plan
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}, 原始内容: {arguments_str}")
            raise ValueError(f"QueryPlan JSON 解析失败: {e}")
    
    def _validate_plan(self, plan: Dict[str, Any]) -> None:
        """
        验证 QueryPlan（卫语句）
        
        Args:
            plan: QueryPlan 字典
            
        Raises:
            ValueError: QueryPlan 验证失败
        """
        if not plan:
            raise ValueError("QueryPlan 不能为空")
        
        # 检查必需字段
        required_fields = ["action", "metrics", "filters", "aggregation", "need_chart"]
        for field in required_fields:
            if field not in plan:
                raise ValueError(f"QueryPlan 缺少必需字段: {field}")
        
        # 检查 action
        if plan["action"] != "query":
            raise ValueError(f"不支持的 action: {plan['action']}")
        
        # 检查 metrics
        if not plan["metrics"] or not isinstance(plan["metrics"], list):
            raise ValueError("metrics 必须是非空列表")
        
        # 检查 filters 和时间范围
        filters = plan.get("filters", {})
        if not isinstance(filters, dict):
            raise ValueError("filters 必须是字典")
        
        time_range = filters.get("time_range")
        if not time_range:
            raise ValueError("filters 必须包含 time_range（时间范围）")
        
        # 检查 aggregation
        valid_aggregations = [
            "none", "group_by_province", "group_by_isp", "group_by_task",
            "group_by_target_node", "group_by_time_hour", "group_by_province_isp",
            "group_by_hostname_task"
        ]
        if plan["aggregation"] not in valid_aggregations:
            raise ValueError(f"不支持的 aggregation: {plan['aggregation']}")


# 全局规划器实例（懒加载）
_planner: Optional[QueryPlanner] = None


def get_planner() -> QueryPlanner:
    """
    获取查询规划器实例（单例模式）
    
    Returns:
        QueryPlanner 实例
    """
    global _planner
    
    if _planner is not None:
        return _planner
    
    _planner = QueryPlanner()
    return _planner

