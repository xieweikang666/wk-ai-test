"""
智能数据分析器
基于LLM的高质量、个性化数据洞察生成
"""
import logging
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import json

from agent.llm import get_llm_client

logger = logging.getLogger(__name__)


class IntelligentAnalyzer:
    """智能数据分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.llm = get_llm_client()
    
    def analyze_with_intelligence(self, 
                                df: pd.DataFrame, 
                                user_query: str, 
                                query_plan: Dict[str, Any],
                                chart_path: Optional[str] = None) -> str:
        """
        智能数据分析
        
        Args:
            df: 查询结果数据
            user_query: 用户原始问题
            query_plan: 查询计划
            chart_path: 图表路径
            
        Returns:
            智能分析结果
        """
        if df is None or df.empty:
            return "查询结果为空，无法进行分析。"
        
        try:
            # 第一步：深度理解用户意图
            intent = self._deep_understand_intent(user_query)
            
            # 第二步：多维度数据洞察
            insights = self._extract_data_insights(df, query_plan)
            
            # 第三步：生成个性化分析
            analysis = self._generate_personalized_analysis(
                user_query, intent, insights, query_plan, chart_path
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"智能分析失败: {e}")
            return f"分析生成失败: {str(e)}"
    
    def _deep_understand_intent(self, user_query: str) -> Dict[str, Any]:
        """深度理解用户查询意图"""
        
        prompt = f"""
你是资深的网络质量分析专家。请深入分析用户查询的真实意图和需求。

用户问题：{user_query}

请返回JSON格式的意图分析：
{{
    "explicit_goal": "明确目标（用户直接表达的需求）",
    "implicit_needs": ["隐含需求（用户可能关心但未明说的方面）"],
    "analysis_depth": "分析深度要求（概览/详细/深度分析）",
    "decision_context": "决策场景（运维规划/故障排查/性能优化/日常监控）",
    "key_concerns": ["核心关注点（成本/性能/可用性/体验等）"],
    "preferred_format": "偏好的回答格式（数据驱动/对比分析/排名推荐/问题诊断）"
}}

分析要点：
1. 透过表面问题理解深层需求
2. 考虑用户的实际工作场景
3. 识别可能的相关关注点
4. 推断最合适的分析角度
"""
        
        try:
            response = self.llm.chat([{"role": "user", "content": prompt}], temperature=0.3)
            if response and response.get("content"):
                content = response["content"].strip()
                return json.loads(content)
        except Exception as e:
            logger.warning(f"深度意图理解失败: {e}")
        
        # 默认意图
        return {
            "explicit_goal": "数据查询",
            "implicit_needs": ["质量评估", "异常识别"],
            "analysis_depth": "详细分析",
            "decision_context": "日常监控",
            "key_concerns": ["性能", "可用性"],
            "preferred_format": "数据驱动"
        }
    
    def _extract_data_insights(self, df: pd.DataFrame, query_plan: Dict[str, Any]) -> Dict[str, Any]:
        """多维度数据洞察提取"""
        
        insights = {
            "basic_stats": self._get_basic_statistics(df),
            "quality_analysis": self._analyze_quality_characteristics(df),
            "performance_patterns": self._identify_performance_patterns(df),
            "anomalies": self._detect_anomalies(df),
            "key_findings": self._extract_key_findings(df),
            "data_quality": self._assess_data_quality(df)
        }
        
        # 根据查询计划调整洞察重点
        metrics = query_plan.get("metrics", [])
        if "avg_lost" in metrics:
            insights["loss_analysis"] = self._analyze_packet_loss(df)
        if "avg_rtt" in metrics:
            insights["latency_analysis"] = self._analyze_latency(df)
        
        return insights
    
    def _get_basic_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """基础统计信息"""
        stats = {
            "total_records": len(df),
            "columns": df.columns.tolist(),
            "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
            "categorical_columns": df.select_dtypes(include=['object']).columns.tolist()
        }
        
        # 数值列统计
        numeric_cols = ['avg_rtt', 'avg_lost', 'count']
        for col in numeric_cols:
            if col in df.columns:
                stats[col] = {
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "q25": float(df[col].quantile(0.25)),
                    "q75": float(df[col].quantile(0.75))
                }
        
        return stats
    
    def _analyze_quality_characteristics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """质量特征分析"""
        quality_analysis = {}
        
        if 'avg_lost' in df.columns:
            loss_data = df['avg_lost'].dropna()
            if len(loss_data) > 0:
                # 质量分级
                excellent = len(loss_data[loss_data < 0.01])  # <1%
                good = len(loss_data[(loss_data >= 0.01) & (loss_data < 0.03)])  # 1-3%
                fair = len(loss_data[(loss_data >= 0.03) & (loss_data < 0.05)])  # 3-5%
                poor = len(loss_data[loss_data >= 0.05])  # >5%
                
                quality_analysis["packet_loss_distribution"] = {
                    "excellent_count": excellent,
                    "good_count": good, 
                    "fair_count": fair,
                    "poor_count": poor,
                    "excellent_rate": excellent / len(loss_data),
                    "poor_rate": poor / len(loss_data)
                }
        
        if 'avg_rtt' in df.columns:
            rtt_data = df['avg_rtt'].dropna()
            if len(rtt_data) > 0:
                # 延迟分级
                excellent = len(rtt_data[rtt_data < 50])  # <50ms
                good = len(rtt_data[(rtt_data >= 50) & (rtt_data < 100)])  # 50-100ms
                fair = len(rtt_data[(rtt_data >= 100) & (rtt_data < 200)])  # 100-200ms
                poor = len(rtt_data[rtt_data >= 200])  # >200ms
                
                quality_analysis["latency_distribution"] = {
                    "excellent_count": excellent,
                    "good_count": good,
                    "fair_count": fair, 
                    "poor_count": poor,
                    "excellent_rate": excellent / len(rtt_data),
                    "poor_rate": poor / len(rtt_data)
                }
        
        return quality_analysis
    
    def _identify_performance_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """识别性能模式"""
        patterns = {}
        
        # 维度分析
        dimension_columns = ['src_isp', 'src_province', 'hostname', 'target_node', 'task_name']
        
        for col in dimension_columns:
            if col in df.columns and 'avg_lost' in df.columns:
                # 按维度分组的性能分析
                group_stats = df.groupby(col)['avg_lost'].agg(['mean', 'count', 'std']).reset_index()
                
                if len(group_stats) > 0:
                    # 找出最好和最差的
                    best = group_stats.loc[group_stats['mean'].idxmin()]
                    worst = group_stats.loc[group_stats['mean'].idxmax()]
                    
                    patterns[f"{col}_performance"] = {
                        "best_entity": best[col],
                        "best_performance": float(best['mean']),
                        "worst_entity": worst[col], 
                        "worst_performance": float(worst['mean']),
                        "performance_gap": float(worst['mean'] - best['mean']),
                        "total_entities": len(group_stats)
                    }
        
        return patterns
    
    def _detect_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """异常检测"""
        anomalies = {}
        
        if 'avg_lost' in df.columns:
            loss_data = df['avg_lost'].dropna()
            if len(loss_data) > 5:
                # 使用IQR方法检测异常
                Q1 = loss_data.quantile(0.25)
                Q3 = loss_data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                anomaly_mask = (loss_data < lower_bound) | (loss_data > upper_bound)
                anomaly_count = anomaly_mask.sum()
                
                anomalies["packet_loss_anomalies"] = {
                    "count": int(anomaly_count),
                    "rate": float(anomaly_count / len(loss_data)),
                    "threshold_upper": float(upper_bound),
                    "threshold_lower": float(lower_bound)
                }
        
        if 'avg_rtt' in df.columns:
            rtt_data = df['avg_rtt'].dropna()
            if len(rtt_data) > 5:
                Q1 = rtt_data.quantile(0.25)
                Q3 = rtt_data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                anomaly_mask = (rtt_data < lower_bound) | (rtt_data > upper_bound)
                anomaly_count = anomaly_mask.sum()
                
                anomalies["latency_anomalies"] = {
                    "count": int(anomaly_count),
                    "rate": float(anomaly_count / len(rtt_data)),
                    "threshold_upper": float(upper_bound),
                    "threshold_lower": float(lower_bound)
                }
        
        return anomalies
    
    def _extract_key_findings(self, df: pd.DataFrame) -> list:
        """提取关键发现"""
        findings = []
        
        if len(df) > 0:
            findings.append(f"数据集包含{len(df)}条记录")
            
            if 'avg_lost' in df.columns:
                avg_loss = df['avg_lost'].mean()
                if avg_loss < 0.02:
                    findings.append(f"整体网络质量良好，平均丢包率为{avg_loss:.3%}")
                elif avg_loss > 0.05:
                    findings.append(f"网络质量问题较为严重，平均丢包率达到{avg_loss:.3%}")
                else:
                    findings.append(f"网络质量一般，平均丢包率为{avg_loss:.3%}")
            
            if 'avg_rtt' in df.columns:
                avg_rtt = df['avg_rtt'].mean()
                if avg_rtt < 50:
                    findings.append(f"网络延迟表现优秀，平均RTT为{avg_rtt:.1f}ms")
                elif avg_rtt > 150:
                    findings.append(f"网络延迟较高，平均RTT达到{avg_rtt:.1f}ms")
                else:
                    findings.append(f"网络延迟适中，平均RTT为{avg_rtt:.1f}ms")
        
        return findings
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """评估数据质量"""
        quality_assessment = {}
        
        # 缺失值检查
        missing_analysis = {}
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                missing_analysis[col] = {
                    "missing_count": int(missing_count),
                    "missing_rate": float(missing_count / len(df))
                }
        
        quality_assessment["missing_values"] = missing_analysis
        
        # 数据一致性检查
        if 'avg_lost' in df.columns:
            # 检查丢包率是否在合理范围
            invalid_loss = ((df['avg_lost'] < 0) | (df['avg_lost'] > 1)).sum()
            if invalid_loss > 0:
                quality_assessment["invalid_packet_loss"] = {
                    "count": int(invalid_loss),
                    "rate": float(invalid_loss / len(df))
                }
        
        if 'avg_rtt' in df.columns:
            # 检查RTT是否为正数
            invalid_rtt = (df['avg_rtt'] < 0).sum()
            if invalid_rtt > 0:
                quality_assessment["invalid_rtt"] = {
                    "count": int(invalid_rtt),
                    "rate": float(invalid_rtt / len(df))
                }
        
        quality_assessment["overall_quality_score"] = self._calculate_quality_score(quality_assessment, len(df))
        
        return quality_assessment
    
    def _calculate_quality_score(self, quality_assessment: Dict[str, Any], total_records: int) -> float:
        """计算数据质量分数"""
        score = 1.0
        
        # 缺失值扣分
        for col, missing_info in quality_assessment.get("missing_values", {}).items():
            score -= missing_info["missing_rate"] * 0.1
        
        # 异常值扣分
        for issue_type, issue_info in quality_assessment.items():
            if "rate" in issue_info and issue_type != "missing_values":
                score -= issue_info["rate"] * 0.2
        
        return max(0.0, min(1.0, score))
    
    def _analyze_packet_loss(self, df: pd.DataFrame) -> Dict[str, Any]:
        """专门的丢包分析"""
        if 'avg_lost' not in df.columns:
            return {}
        
        loss_data = df['avg_lost'].dropna()
        
        return {
            "mean_loss": float(loss_data.mean()),
            "median_loss": float(loss_data.median()),
            "max_loss": float(loss_data.max()),
            "min_loss": float(loss_data.min()),
            "loss_volatility": float(loss_data.std() / loss_data.mean()) if loss_data.mean() > 0 else 0,
            "high_loss_rate": float((loss_data > 0.05).sum() / len(loss_data))
        }
    
    def _analyze_latency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """专门的延迟分析"""
        if 'avg_rtt' not in df.columns:
            return {}
        
        rtt_data = df['avg_rtt'].dropna()
        
        return {
            "mean_rtt": float(rtt_data.mean()),
            "median_rtt": float(rtt_data.median()),
            "max_rtt": float(rtt_data.max()),
            "min_rtt": float(rtt_data.min()),
            "rtt_volatility": float(rtt_data.std() / rtt_data.mean()) if rtt_data.mean() > 0 else 0,
            "high_latency_rate": float((rtt_data > 200).sum() / len(rtt_data))
        }
    
    def _generate_personalized_analysis(self, 
                                      user_query: str,
                                      intent: Dict[str, Any],
                                      insights: Dict[str, Any],
                                      query_plan: Dict[str, Any],
                                      chart_path: Optional[str] = None) -> str:
        """生成个性化分析报告"""
        
        # 构建个性化提示词
        system_prompt = """你是顶尖的网络质量分析专家，能够将复杂的数据转化为深刻的商业洞察。

分析原则：
1. **洞察深度**：超越表面数据，发现隐藏的问题和机会
2. **个性化定制**：根据用户意图和场景调整分析角度
3. **实用导向**：提供可操作的建议和决策支持
4. **数据诚信**：严格基于数据，避免主观臆测

回答要求：
- 开门见山，直接回答用户核心关切
- 用具体数据支撑观点，避免模糊表述
- 提供层次化的分析（核心发现→深入分析→行动建议）
- 语言专业但不晦涩，让技术和业务人员都能理解
- 控制在500-700字，确保信息密度"""
        
        user_prompt = f"""
## 用户查询意图
{json.dumps(intent, ensure_ascii=False, indent=2)}

## 数据洞察结果
{json.dumps(insights, ensure_ascii=False, indent=2)}

## 原始查询：{user_query}

## 查询计划
{json.dumps(query_plan, ensure_ascii=False, indent=2)}

## 分析要求
请基于以上信息，生成一份高质量的网络质量分析报告。重点包括：

1. **核心结论**（2-3句话）：
   - 直接回应用户最关心的问题
   - 突出最重要的发现
   
2. **深度分析**（3-4点）：
   - 基于数据洞察进行多角度分析
   - 对比不同维度的表现差异
   - 识别潜在的问题和优势
   
3. **关键数据支撑**：
   - 引用具体的数值和排名
   - 展示数据背后的趋势和模式
   
4. **行动建议**（2-3条）：
   - 基于分析结果提出具体建议
   - 考虑用户的决策场景和关注点
   - 提供可执行的改进措施

## 注意事项
- 严格使用insights中的数据，不要编造
- 根据用户意图调整分析重点和表达方式
- 避免模板化表述，体现个性化洞察
- 如果存在数据质量问题，需要说明影响
"""

        if chart_path:
            user_prompt += f"\n\n## 图表参考\n分析时可以参考生成的图表：{chart_path}"
        
        try:
            response = self.llm.chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ], temperature=0.7)
            
            if response and response.get("content"):
                analysis = response["content"].strip()
                logger.info("个性化分析生成成功")
                return analysis
            
        except Exception as e:
            logger.error(f"个性化分析生成失败: {e}")
        
        # 回退分析
        return self._fallback_analysis(insights, user_query)
    
    def _fallback_analysis(self, insights: Dict[str, Any], user_query: str) -> str:
        """回退分析"""
        basic_stats = insights.get("basic_stats", {})
        key_findings = insights.get("key_findings", [])
        
        analysis = f"基于{basic_stats.get('total_records', 0)}条数据的分析结果：\n\n"
        
        for finding in key_findings:
            analysis += f"• {finding}\n"
        
        analysis += f"\n建议进一步扩大查询范围或调整查询条件以获得更详细的分析。"
        
        return analysis