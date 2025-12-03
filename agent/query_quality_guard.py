"""
查询质量保障系统
确保SQL生成和分析结果的质量
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import json
import time

from agent.intelligent_sql_generator import IntelligentSQLGenerator
from agent.intelligent_analyzer import IntelligentAnalyzer
from agent.llm import get_llm_client
from db.clickhouse_client import get_client

logger = logging.getLogger(__name__)


class QueryQualityGuard:
    """查询质量保障系统"""
    
    def __init__(self):
        """初始化质量保障系统"""
        self.sql_generator = IntelligentSQLGenerator()
        self.analyzer = IntelligentAnalyzer()
        self.llm = get_llm_client()
        self.client = get_client()
    
    def execute_query_with_quality_check(self, 
                                       user_query: str, 
                                       query_plan: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        执行带质量检查的查询
        
        Returns:
            (查询结果DataFrame, 质量报告)
        """
        quality_report = {
            "sql_generation": {"status": "pending", "issues": [], "score": 0},
            "execution": {"status": "pending", "issues": [], "execution_time": 0},
            "result_quality": {"status": "pending", "issues": [], "score": 0},
            "overall_score": 0
        }
        
        try:
            # 第一步：SQL生成质量检查
            sql, sql_quality = self._generate_and_validate_sql(user_query, query_plan)
            quality_report["sql_generation"] = sql_quality
            
            if sql_quality["status"] == "failed":
                return pd.DataFrame(), quality_report
            
            # 第二步：执行查询并监控
            start_time = time.time()
            df, execution_quality = self._execute_with_monitoring(sql)
            execution_time = time.time() - start_time
            
            quality_report["execution"] = execution_quality
            quality_report["execution"]["execution_time"] = execution_time
            
            if execution_quality["status"] == "failed":
                return pd.DataFrame(), quality_report
            
            # 第三步：结果质量评估
            result_quality = self._evaluate_result_quality(df, query_plan)
            quality_report["result_quality"] = result_quality
            
            # 第四步：计算总体质量分数
            quality_report["overall_score"] = self._calculate_overall_score(quality_report)
            
            return df, quality_report
            
        except Exception as e:
            logger.error(f"查询质量检查失败: {e}")
            quality_report["sql_generation"]["status"] = "failed"
            quality_report["sql_generation"]["issues"].append(f"系统异常: {str(e)}")
            return pd.DataFrame(), quality_report
    
    def _generate_and_validate_sql(self, user_query: str, query_plan: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """生成并验证SQL质量"""
        
        try:
            # 生成SQL
            sql = self.sql_generator.generate_sql(user_query, query_plan)
            
            # 质量检查
            issues = []
            score = 100
            
            # 1. 语法和安全性检查
            validation_result = self.sql_generator.validate_sql_execution(sql)
            if not validation_result["valid"]:
                return "", {"status": "failed", "issues": [validation_result["message"]], "score": 0}
            
            # 2. 复杂度检查
            complexity_score = self._check_sql_complexity(sql)
            score = min(score, complexity_score["score"])
            issues.extend(complexity_score["issues"])
            
            # 3. 性能检查
            performance_score = self._estimate_sql_performance(sql)
            score = min(score, performance_score["score"])
            issues.extend(performance_score["issues"])
            
            # 4. 语义匹配度检查
            semantic_score = self._check_semantic_alignment(sql, user_query)
            score = min(score, semantic_score["score"])
            issues.extend(semantic_score["issues"])
            
            status = "passed" if score >= 70 else "warning"
            
            return sql, {"status": status, "issues": issues, "score": score}
            
        except Exception as e:
            return "", {"status": "failed", "issues": [f"SQL生成异常: {str(e)}"], "score": 0}
    
    def _check_sql_complexity(self, sql: str) -> Dict[str, Any]:
        """检查SQL复杂度"""
        issues = []
        score = 100
        
        sql_lower = sql.lower()
        
        # 检查JOIN数量
        join_count = sql_lower.count(' join ')
        if join_count > 3:
            score -= 20
            issues.append(f"JOIN数量过多({join_count})，可能影响性能")
        
        # 检查子查询深度
        subquery_depth = sql_lower.count('(select')
        if subquery_depth > 2:
            score -= 15
            issues.append(f"子查询过深({subquery_depth}层)，建议简化")
        
        # 检查聚合函数复杂度
        aggregate_functions = ['count(', 'avg(', 'sum(', 'max(', 'min(']
        aggregate_count = sum(sql_lower.count(func) for func in aggregate_functions)
        if aggregate_count > 10:
            score -= 10
            issues.append(f"聚合函数过多({aggregate_count})，查询可能过于复杂")
        
        return {"score": max(0, score), "issues": issues}
    
    def _estimate_sql_performance(self, sql: str) -> Dict[str, Any]:
        """估算SQL性能"""
        issues = []
        score = 100
        
        sql_lower = sql.lower()
        
        # 检查是否有时间过滤
        if 'timestamp' not in sql_lower:
            score -= 30
            issues.append("缺少时间过滤条件，可能导致全表扫描")
        
        # 检查LIMIT
        if 'limit' not in sql_lower:
            score -= 20
            issues.append("缺少LIMIT限制，可能返回大量数据")
        else:
            # 检查LIMIT值
            import re
            limit_match = re.search(r'limit\s+(\d+)', sql_lower)
            if limit_match:
                limit_value = int(limit_match.group(1))
                if limit_value > 1000000:
                    score -= 15
                    issues.append(f"LIMIT值过大({limit_value})，建议分页查询")
        
        # 检查SELECT *
        if 'select *' in sql_lower:
            score -= 10
            issues.append("使用SELECT *可能影响性能，建议指定具体字段")
        
        return {"score": max(0, score), "issues": issues}
    
    def _check_semantic_alignment(self, sql: str, user_query: str) -> Dict[str, Any]:
        """检查SQL与查询意图的匹配度"""
        issues = []
        
        prompt = f"""
请评估以下SQL是否能够准确回答用户的问题。

用户问题：{user_query}

生成的SQL：
{sql}

请从以下角度评估：
1. 字段选择是否合理
2. 聚合方式是否恰当  
3. 过滤条件是否完整
4. 结果是否能回答用户问题

请返回JSON格式：
{{
    "alignment_score": 0-100的匹配度分数,
    "field_appropriateness": "字段选择评估",
    "aggregation_appropriateness": "聚合方式评估", 
    "filter_completeness": "过滤条件评估",
    "result_relevance": "结果相关性评估",
    "suggestions": ["改进建议"]
}}
"""
        
        try:
            response = self.llm.chat([{"role": "user", "content": prompt}], temperature=0.1)
            if response and response.get("content"):
                evaluation = json.loads(response["content"].strip())
                score = evaluation.get("alignment_score", 50)
                
                if score < 70:
                    issues.extend(evaluation.get("suggestions", ["SQL与查询意图匹配度较低"]))
                
                return {"score": score, "issues": issues}
                
        except Exception as e:
            logger.warning(f"语义匹配度检查失败: {e}")
        
        return {"score": 75, "issues": []}
    
    def _execute_with_monitoring(self, sql: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """执行查询并监控"""
        issues = []
        
        try:
            # 执行查询
            df = self.client.execute_query(sql)
            
            if df is None:
                return pd.DataFrame(), {"status": "failed", "issues": ["查询返回空结果"], "score": 0}
            
            # 检查结果大小
            row_count = len(df)
            if row_count == 0:
                issues.append("查询结果为空")
                return df, {"status": "warning", "issues": issues, "score": 60}
            elif row_count < 10:
                issues.append(f"查询结果较少({row_count}行)，分析可能不够全面")
            elif row_count > 100000:
                issues.append(f"查询结果较多({row_count}行)，可能需要进一步聚合")
            
            # 检查列完整性
            if df.columns.empty:
                issues.append("查询结果缺少列信息")
                return df, {"status": "failed", "issues": issues, "score": 0}
            
            score = 100 - len(issues) * 10
            status = "passed" if score >= 70 else "warning"
            
            return df, {"status": status, "issues": issues, "score": max(0, score)}
            
        except Exception as e:
            return pd.DataFrame(), {"status": "failed", "issues": [f"查询执行失败: {str(e)}"], "score": 0}
    
    def _evaluate_result_quality(self, df: pd.DataFrame, query_plan: Dict[str, Any]) -> Dict[str, Any]:
        """评估结果数据质量"""
        issues = []
        score = 100
        
        # 1. 数据完整性检查
        completeness_score = self._check_data_completeness(df)
        score = min(score, completeness_score["score"])
        issues.extend(completeness_score["issues"])
        
        # 2. 数据一致性检查
        consistency_score = self._check_data_consistency(df)
        score = min(score, consistency_score["score"])
        issues.extend(consistency_score["issues"])
        
        # 3. 数据分布合理性检查
        distribution_score = self._check_data_distribution(df)
        score = min(score, distribution_score["score"])
        issues.extend(distribution_score["issues"])
        
        # 4. 查询计划匹配度检查
        plan_alignment = self._check_plan_alignment(df, query_plan)
        score = min(score, plan_alignment["score"])
        issues.extend(plan_alignment["issues"])
        
        status = "passed" if score >= 70 else "warning"
        
        return {"status": status, "issues": issues, "score": max(0, score)}
    
    def _check_data_completeness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """检查数据完整性"""
        issues = []
        score = 100
        
        # 缺失值检查
        missing_analysis = {}
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                missing_rate = missing_count / len(df)
                missing_analysis[col] = missing_rate
                
                if missing_rate > 0.5:
                    score -= 20
                    issues.append(f"列{col}缺失值过多({missing_rate:.1%})")
                elif missing_rate > 0.1:
                    score -= 10
                    issues.append(f"列{col}存在较多缺失值({missing_rate:.1%})")
        
        # 关键字段检查
        key_fields = ['avg_rtt', 'avg_lost', 'hostname', 'target_node']
        for field in key_fields:
            if field in df.columns:
                missing_rate = df[field].isnull().sum() / len(df)
                if missing_rate > 0.2:
                    score -= 15
                    issues.append(f"关键字段{field}缺失率过高({missing_rate:.1%})")
        
        return {"score": max(0, score), "issues": issues}
    
    def _check_data_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """检查数据一致性"""
        issues = []
        score = 100
        
        # 数值范围检查
        if 'avg_lost' in df.columns:
            # 丢包率应该在0-1之间
            invalid_loss = ((df['avg_lost'] < 0) | (df['avg_lost'] > 1)).sum()
            if invalid_loss > 0:
                invalid_rate = invalid_loss / len(df)
                score -= min(30, invalid_rate * 100)
                issues.append(f"丢包率数据异常({invalid_rate:.1%}的数据超出0-1范围)")
        
        if 'avg_rtt' in df.columns:
            # RTT应该为正数
            invalid_rtt = (df['avg_rtt'] < 0).sum()
            if invalid_rtt > 0:
                invalid_rate = invalid_rtt / len(df)
                score -= min(25, invalid_rate * 100)
                issues.append(f"RTT数据异常({invalid_rate:.1%}的数据为负数)")
        
        return {"score": max(0, score), "issues": issues}
    
    def _check_data_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """检查数据分布合理性"""
        issues = []
        score = 100
        
        # 检查数据分布是否过于集中
        for col in ['avg_rtt', 'avg_lost']:
            if col in df.columns:
                data = df[col].dropna()
                if len(data) > 1:
                    # 检查标准差
                    std_val = data.std()
                    mean_val = data.mean()
                    
                    if mean_val > 0:
                        cv = std_val / mean_val  # 变异系数
                        
                        if cv < 0.01:  # 数据过于集中
                            score -= 15
                            issues.append(f"{col}数据分布过于集中，可能缺乏代表性")
                        elif cv > 5:  # 数据过于分散
                            score -= 10
                            issues.append(f"{col}数据变异系数较大({cv:.2f})，可能存在异常值")
        
        return {"score": max(0, score), "issues": issues}
    
    def _check_plan_alignment(self, df: pd.DataFrame, query_plan: Dict[str, Any]) -> Dict[str, Any]:
        """检查结果与查询计划的一致性"""
        issues = []
        score = 100
        
        # 检查预期的指标是否存在
        expected_metrics = query_plan.get("metrics", [])
        for metric in expected_metrics:
            if metric not in df.columns:
                score -= 20
                issues.append(f"缺少预期指标{metric}")
        
        # 检查聚合维度
        aggregation = query_plan.get("aggregation", "none")
        if aggregation != "none":
            # 解析预期应该有的分组字段
            expected_group_fields = []
            if "hostname" in aggregation:
                expected_group_fields.append("hostname")
            if "target_node" in aggregation:
                expected_group_fields.append("target_node")
            if "src_isp" in aggregation:
                expected_group_fields.append("src_isp")
            if "src_province" in aggregation:
                expected_group_fields.append("src_province")
            
            for field in expected_group_fields:
                if field not in df.columns:
                    score -= 15
                    issues.append(f"缺少预期分组字段{field}")
        
        return {"score": max(0, score), "issues": issues}
    
    def _calculate_overall_score(self, quality_report: Dict[str, Any]) -> float:
        """计算总体质量分数"""
        weights = {
            "sql_generation": 0.3,
            "execution": 0.2,
            "result_quality": 0.5
        }
        
        total_score = 0
        total_weight = 0
        
        for component, weight in weights.items():
            component_score = quality_report.get(component, {}).get("score", 0)
            total_score += component_score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0
    
    def generate_quality_report(self, quality_report: Dict[str, Any]) -> str:
        """生成用户友好的质量报告"""
        report_lines = []
        
        overall_score = quality_report.get("overall_score", 0)
        
        if overall_score >= 80:
            report_lines.append("🟢 **查询质量评估：优秀**")
        elif overall_score >= 60:
            report_lines.append("🟡 **查询质量评估：良好**")
        else:
            report_lines.append("🔴 **查询质量评估：需要改进**")
        
        report_lines.append(f"总体评分：{overall_score:.1f}/100")
        
        # 各组件详细报告
        components = {
            "sql_generation": "SQL生成",
            "execution": "查询执行", 
            "result_quality": "结果质量"
        }
        
        for comp_key, comp_name in components.items():
            comp_data = quality_report.get(comp_key, {})
            score = comp_data.get("score", 0)
            status = comp_data.get("status", "unknown")
            issues = comp_data.get("issues", [])
            
            if status == "passed":
                status_emoji = "✅"
            elif status == "warning":
                status_emoji = "⚠️"
            else:
                status_emoji = "❌"
            
            report_lines.append(f"\n{status_emoji} **{comp_name}**：{score:.1f}/100")
            
            if issues:
                for issue in issues[:2]:  # 最多显示2个问题
                    report_lines.append(f"   • {issue}")
        
        return "\n".join(report_lines)