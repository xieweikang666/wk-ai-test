"""
智能SQL生成器
基于LLM动态生成高质量SQL查询
"""
import logging
import time
from typing import Dict, Any, List, Optional
import json
import re

from agent.llm import get_llm_client
from db.clickhouse_client import get_client
from config.settings import settings
from utils.time_utils import parse_time_range

logger = logging.getLogger(__name__)


class IntelligentSQLGenerator:
    """智能SQL生成器"""
    
    def __init__(self):
        """初始化SQL生成器"""
        self.llm = get_llm_client()
        self.client = get_client()
        self.schema_context = self._load_schema_context()
    
    def _load_schema_context(self) -> str:
        """加载数据库schema上下文"""
        return """
## 数据库表结构
- 表名: detect.detect_ping_log
- 主键: (timestamp, task_name) 
- 排序键: (timestamp, task_name, src_isp, src_province)

## 字段说明
### 时间字段
- timestamp (Int64): Unix时间戳(秒)，必须用于时间过滤

### 维度字段
- task_name (String): 探测任务名称，如 edge_l1_detect, edge_l2_detect
- src_isp (String): 源运营商 (chinatelecom/chinamobile/chinaunicom/chinatietong)
- src_province (String): 源省份 (zhejiang/jiangsu/beijing等)
- hostname (String): 探测设备主机名
- target_node (String): 目标节点标识

### 指标字段
- avg_rtt (Float64): 平均延迟(ms)，核心性能指标
- avg_lost (Float64): 平均丢包率(0-1)，核心质量指标
- packet_loss (Int64): 丢包数量
- packet_total (Int64): 总包数量

## 查询要求
1. 必须包含时间范围过滤: timestamp >= X AND timestamp <= Y
2. 必须包含LIMIT限制(最大100万行)
3. 优先使用聚合函数避免返回大量数据
4. 注意字段大小写(全部小写)
"""
    
    def generate_sql(self, user_query: str, query_plan: Dict[str, Any]) -> str:
        """
        基于用户问题和查询计划生成SQL
        
        Args:
            user_query: 用户原始问题
            query_plan: 查询计划
            
        Returns:
            生成的SQL语句
        """
        try:
            # 第一步：理解查询意图
            intent = self._analyze_query_intent(user_query)
            
            # 第二步：生成基础SQL
            sql = self._generate_base_sql(user_query, query_plan, intent)
            
            # 第三步：SQL优化和验证
            optimized_sql = self._optimize_and_validate_sql(sql)
            
            logger.info(f"生成SQL: {optimized_sql}")
            return optimized_sql
            
        except Exception as e:
            logger.error(f"SQL生成失败: {e}")
            # 回退到规则生成
            return self._fallback_sql_generation(query_plan)
    
    def _analyze_query_intent(self, user_query: str) -> Dict[str, Any]:
        """使用LLM分析查询意图"""
        
        prompt = f"""
你是网络探测数据查询专家。请分析用户问题的查询意图。

用户问题：{user_query}

请返回JSON格式的意图分析：
{{
    "primary_goal": "主要目标（如：质量分析/性能排名/趋势分析/对比分析）",
    "time_preference": "时间偏好（如：最新数据/历史趋势/特定时段）",
    "aggregation_need": "聚合需求（如：详细数据/统计摘要/排名分析）",
    "key_dimensions": ["关键分析维度"],
    "output_priority": "输出优先级（如：准确性/性能/详细程度）"
}}

要求：
1. 简洁明确，避免冗余描述
2. 基于问题本身推断意图
3. 考虑网络探测数据的特性
"""
        
        try:
            response = self.llm.chat([{"role": "user", "content": prompt}], temperature=0.3)
            if response and response.get("content"):
                content = response["content"].strip()
                # 尝试解析JSON
                return json.loads(content)
        except Exception as e:
            logger.warning(f"意图分析失败: {e}")
        
        # 默认意图
        return {
            "primary_goal": "质量分析",
            "time_preference": "最新数据", 
            "aggregation_need": "统计摘要",
            "key_dimensions": ["src_isp", "src_province"],
            "output_priority": "准确性"
        }
    
    def _generate_base_sql(self, user_query: str, query_plan: Dict[str, Any], intent: Dict[str, Any]) -> str:
        """生成基础SQL语句"""
        
        # 时间范围解析
        time_range = query_plan.get("filters", {}).get("time_range", "last_1_hour")
        start_ts, end_ts = parse_time_range(time_range)
        
        # 构建提示词
        prompt = f"""
基于以下信息生成ClickHouse SQL查询：

## 用户问题
{user_query}

## 查询意图
{json.dumps(intent, ensure_ascii=False, indent=2)}

## 查询计划
{json.dumps(query_plan, ensure_ascii=False, indent=2)}

## 时间范围
{time_range} -> {start_ts} 到 {end_ts}

## 数据库Schema
{self.schema_context}

## 生成要求
1. 根据查询意图选择合适的字段和聚合方式
2. 时间范围: timestamp >= {start_ts} AND timestamp <= {end_ts}
3. 添加 LIMIT 1000000
4. 优先使用聚合函数提高查询性能
5. 确保字段名正确(全部小写)

请生成完整的SQL查询语句（仅返回SQL，不要解释）：
"""
        
        try:
            response = self.llm.chat([{"role": "user", "content": prompt}], temperature=0.1)
            if response and response.get("content"):
                sql = response["content"].strip()
                # 清理可能的代码块标记
                sql = re.sub(r'```sql\s*', '', sql)
                sql = re.sub(r'```\s*$', '', sql)
                return sql
        except Exception as e:
            logger.error(f"LLM SQL生成失败: {e}")
            raise
        
        raise ValueError("无法生成SQL")
    
    def _optimize_and_validate_sql(self, sql: str) -> str:
        """优化和验证SQL"""
        if not sql:
            raise ValueError("SQL不能为空")
        
        sql_lower = sql.lower().strip()
        
        # 安全检查
        if not sql_lower.startswith('select'):
            raise ValueError("只允许SELECT查询")
        
        dangerous_keywords = ['insert', 'update', 'delete', 'drop', 'alter', 'create']
        for keyword in dangerous_keywords:
            if keyword in sql_lower:
                raise ValueError(f"SQL包含危险关键字: {keyword}")
        
        # 性能检查
        if 'timestamp' not in sql_lower:
            logger.warning("SQL未包含时间过滤，可能导致性能问题")
            # 强制添加时间范围
            current_time = int(time.time())
            one_hour_ago = current_time - 3600
            if 'where' in sql_lower:
                sql = sql.replace('WHERE', f'WHERE timestamp >= {one_hour_ago} AND timestamp <= {current_time} AND')
            else:
                sql = sql.replace('FROM detect.detect_ping_log', f'FROM detect.detect_ping_log WHERE timestamp >= {one_hour_ago} AND timestamp <= {current_time}')
        
        # LIMIT检查
        if 'limit' not in sql_lower:
            sql += "\nLIMIT 1000000"
            logger.info("自动添加LIMIT限制")
        
        return sql
    
    def _fallback_sql_generation(self, query_plan: Dict[str, Any]) -> str:
        """回退到规则生成SQL"""
        logger.info("使用回退SQL生成策略")
        
        # 基于查询计划生成简单SQL
        metrics = query_plan.get("metrics", ["avg_lost"])
        time_range = query_plan.get("filters", {}).get("time_range", "last_1_hour")
        start_ts, end_ts = parse_time_range(time_range)
        
        # 构建SELECT
        select_parts = []
        for metric in metrics:
            if metric == "avg_rtt":
                select_parts.append("AVG(avg_rtt) as avg_rtt")
            elif metric == "avg_lost":
                select_parts.append("AVG(avg_lost) as avg_lost")
            else:
                select_parts.append(f"AVG({metric}) as {metric}")
        
        select_parts.append("COUNT(*) as count")
        
        # 构建SQL
        sql = f"""
SELECT {', '.join(select_parts)}
FROM {settings.CLICKHOUSE_DATABASE}.{settings.CLICKHOUSE_TABLE_PING}
WHERE timestamp >= {start_ts} AND timestamp <= {end_ts}
LIMIT 1000000
""".strip()
        
        return sql
    
    def validate_sql_execution(self, sql: str) -> Dict[str, Any]:
        """验证SQL执行并返回诊断信息"""
        try:
            # 检查SQL是否已经包含LIMIT
            sql_lower = sql.lower()
            if 'limit' not in sql_lower:
                test_sql = sql + " LIMIT 1"
            else:
                test_sql = sql
                
            # 测试执行并获取执行计划
            test_result = self.client.execute_query(test_sql)
            
            return {
                "valid": True,
                "message": "SQL执行成功",
                "sample_data": test_result.head(3).to_dict() if not test_result.empty else None
            }
        except Exception as e:
            return {
                "valid": False,
                "message": f"SQL执行失败: {str(e)}",
                "suggestion": self._get_error_suggestion(str(e))
            }
    
    def _get_error_suggestion(self, error_msg: str) -> str:
        """根据错误信息提供修复建议"""
        if "Unknown column" in error_msg:
            return "检查字段名是否正确，参考schema文档"
        elif "Missing columns" in error_msg:
            return "确保SELECT和GROUP BY字段匹配"
        elif "too large" in error_msg.lower() or "memory" in error_msg.lower():
            return "数据量过大，建议增加聚合或缩小时间范围"
        else:
            return "请检查SQL语法是否符合ClickHouse规范"