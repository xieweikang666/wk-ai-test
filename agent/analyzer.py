"""
数据分析模块
使用 LLM 对查询结果进行自然语言分析
"""
import logging
from typing import Dict, Any, Optional
import pandas as pd
from agent.llm import get_llm_client

logger = logging.getLogger(__name__)


def analyze_result(
    df: pd.DataFrame,
    query_plan: Dict[str, Any],
    chart_path: Optional[str] = None
) -> str:
    """
    分析查询结果并生成自然语言说明
    
    Args:
        df: 查询结果 DataFrame
        query_plan: 原始 QueryPlan
        chart_path: 图表路径（可选）
        
    Returns:
        分析结果文本
    """
    if df is None or df.empty:
        return "查询结果为空，无法进行分析。"
    
    if not query_plan:
        return "缺少查询计划信息，无法进行分析。"
    
    try:
        llm = get_llm_client()
        
        # 准备数据摘要
        data_summary = _prepare_data_summary(df)
        
        # 构建分析提示词
        messages = _build_analysis_messages(data_summary, query_plan, chart_path)
        
        # 调用 LLM 进行分析
        response = llm.chat(messages=messages, temperature=0.7)
        
        if not response or not response.get("content"):
            return "分析结果生成失败。"
        
        analysis = response["content"]
        logger.info("结果分析完成")
        return analysis
        
    except Exception as e:
        logger.error(f"结果分析异常: {e}")
        return f"结果分析失败: {str(e)}"


def _prepare_data_summary(df: pd.DataFrame) -> str:
    """
    准备数据摘要（卫语句）
    
    Args:
        df: 数据 DataFrame
        
    Returns:
        数据摘要字符串
    """
    if df is None or df.empty:
        return "数据为空"
    
    summary_parts = []
    
    # 基本信息
    row_count = len(df)
    col_count = len(df.columns)
    summary_parts.append(f"数据行数: {row_count}, 列数: {col_count}")
    
    # 列名
    summary_parts.append(f"列名: {', '.join(df.columns.tolist())}")
    
    # 数值列统计
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if numeric_cols:
        summary_parts.append("\n数值列统计:")
        for col in numeric_cols[:5]:  # 最多显示5列
            if col in df.columns:
                mean_val = df[col].mean()
                max_val = df[col].max()
                min_val = df[col].min()
                summary_parts.append(
                    f"  {col}: 平均值={mean_val:.2f}, 最大值={max_val:.2f}, 最小值={min_val:.2f}"
                )
    
    # 前几行数据（用于示例）
    if row_count > 0:
        summary_parts.append(f"\n前 {min(5, row_count)} 行数据:")
        summary_parts.append(df.head(min(5, row_count)).to_string())
    
    return "\n".join(summary_parts)


def _build_analysis_messages(
    data_summary: str,
    query_plan: Dict[str, Any],
    chart_path: Optional[str]
) -> list:
    """
    构建分析提示词
    
    Args:
        data_summary: 数据摘要
        query_plan: 查询计划
        chart_path: 图表路径
        
    Returns:
        消息列表
    """
    system_prompt = """你是一个专业的数据分析师。你的任务是根据查询结果数据，生成清晰、专业的自然语言分析报告。

要求：
1. 用中文回答
2. 分析数据的主要趋势和特征
3. 指出异常值或值得关注的点
4. 如果数据量较大，进行合理的概括
5. 语言简洁、专业、易懂

如果提供了图表路径，可以在分析中提及图表。"""
    
    user_prompt = f"""请分析以下查询结果：

查询计划：
{query_plan}

数据摘要：
{data_summary}
"""
    
    if chart_path:
        user_prompt += f"\n图表路径: {chart_path}"
    
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]


