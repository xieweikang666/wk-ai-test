"""
数据分析模块
使用 LLM 对查询结果进行自然语言分析
"""
import logging
import pandas as pd
from typing import Dict, Any, Optional

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
    准备结构化数据摘要
    
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
    summary_parts.append(f"=== 数据概览 ===")
    summary_parts.append(f"总行数: {row_count}, 列数: {col_count}")
    summary_parts.append(f"列名: {', '.join(df.columns.tolist())}")

    # 关键指标分析
    summary_parts.append(f"\n=== 关键指标分析 ===")
    
    # 分析不同列的重要性
    if 'device_count' in df.columns and 'src_isp' in df.columns:
        # 设备数量统计分析
        summary_parts.append(f"📊 探测设备数量统计:")
        total_devices = df['device_count'].sum()
        summary_parts.append(f"总设备数: {total_devices} 台")
        
        # 各运营商设备分布
        device_dist = df[['src_isp', 'device_count']].to_string(index=False)
        summary_parts.append(f"\n各运营商设备分布:\n{device_dist}")
        
        # 设备占比分析
        max_isp = df.loc[df['device_count'].idxmax()]
        min_isp = df.loc[df['device_count'].idxmin()]
        
        summary_parts.append(f"\n📈 设备分布分析:")
        summary_parts.append(f"设备最多: {max_isp['src_isp']} ({max_isp['device_count']} 台)")
        summary_parts.append(f"设备最少: {min_isp['src_isp']} ({min_isp['device_count']} 台)")
        
        # 计算设备占比
        summary_parts.append(f"\n设备占比:")
        for _, row in df.iterrows():
            isp = row['src_isp']
            count = row['device_count']
            percentage = (count / total_devices) * 100
            summary_parts.append(f"- {isp}: {count} 台 ({percentage:.1f}%)")
        
    elif 'hostname' in df.columns and 'avg_lost' in df.columns:
        # 探测设备分析
        summary_parts.append(f"📊 探测设备质量数据:")
        best_devices = df.nsmallest(3, 'avg_lost')[['hostname', 'avg_lost', 'avg_rtt']].to_string(index=False)
        worst_devices = df.nlargest(3, 'avg_lost')[['hostname', 'avg_lost', 'avg_rtt']].to_string(index=False)
        summary_parts.append(f"质量最好TOP3:\n{best_devices}")
        summary_parts.append(f"质量最差TOP3:\n{worst_devices}")
        
    elif 'target_node' in df.columns and 'avg_lost' in df.columns:
        # 目标节点分析
        summary_parts.append(f"🎯 目标节点性能数据:")
        best_nodes = df.nsmallest(3, 'avg_lost')[['target_node', 'avg_lost', 'avg_rtt']].to_string(index=False)
        worst_nodes = df.nlargest(3, 'avg_lost')[['target_node', 'avg_lost', 'avg_rtt']].to_string(index=False)
        summary_parts.append(f"性能最佳TOP3:\n{best_nodes}")
        summary_parts.append(f"性能最差TOP3:\n{worst_nodes}")
        
        if 'src_isp' in df.columns:
            # 按ISP分组统计
            isp_stats = df.groupby('src_isp')['avg_lost'].agg(['mean', 'count']).round(2)
            summary_parts.append(f"\n运营商平均丢包率:\n{isp_stats.to_string()}")
            
    elif 'src_province' in df.columns and 'src_isp' in df.columns:
        # 地区覆盖分析
        summary_parts.append(f"🌍 地区覆盖数据:")
        province_stats = df.groupby(['src_province', 'src_isp'])['avg_lost'].mean().round(2)
        summary_parts.append(f"各省运营商平均丢包率:\n{province_stats.to_string()}")

    # 数值列统计摘要
    summary_parts.append(f"\n=== 数值统计 ===")
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    for col in ['avg_lost', 'avg_rtt', 'count']:
        if col in df.columns:
            mean_val = df[col].mean()
            max_val = df[col].max()
            min_val = df[col].min()
            median_val = df[col].median()
            summary_parts.append(f"{col}: 平均={mean_val:.2f}, 中位数={median_val:.2f}, 最大={max_val:.2f}, 最小={min_val:.2f}")

    # 数据质量提示
    summary_parts.append(f"\n=== 数据质量提示 ===")
    if row_count < 10:
        summary_parts.append("⚠️  数据量较少，分析结果可能不够全面")
    elif row_count > 1000:
        summary_parts.append("📈 数据量充足，分析结果可信度较高")
    else:
        summary_parts.append("✅ 数据量适中，分析结果具有参考价值")

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
    system_prompt = """你是专业的网络探测数据分析师，擅长将原始数据转化为可操作的业务洞察。请根据用户问题和查询结果，提供精准、有价值的分析报告。

核心原则：
1. **直接回答**：开门见山回答用户核心问题，不要绕弯子
2. **数据驱动**：基于具体数据得出结论，引用准确数值
3. **可操作性**：提供明确的建议和决策支持
4. **结构清晰**：使用排名、对比等结构化呈现

分析要点：
- **探测设备数量分析**：按运营商统计设备数量，识别设备分布情况
- **探测设备质量分析**：识别质量最好/最差的具体设备，给出hostname和性能指标
- **目标节点分析**：按丢包率排序，推荐优质节点，区分任务类型
- **地区覆盖评估**：明确推荐top3目标节点，提供具体覆盖质量数据

输出要求：
1. **核心结论**：用1-2句话直接回答用户问题
2. **关键数据**：列出前3名最好和最差的设备/节点（含具体数值）
3. **对比分析**：横向比较不同维度的性能差异
4. **行动建议**：提供2-3条具体、可执行的建议

禁止事项：
- 不说"某些主机""有些节点"等模糊表述
- 不编造数据，所有结论必须基于查询结果
- 避免空话套话，每句话都要有信息价值

回复控制在400-600字，确保信息密集且可操作。"""

    # 提取用户原始问题
    original_query = query_plan.get("original_query", "")
    if not original_query:
        original_query = "分析查询结果"
    
    user_prompt = f"""用户原始问题：{original_query}

📋 查询计划：
{query_plan}

📊 结构化数据摘要：
{data_summary}

🎯 分析要求：
根据用户问题的类型，请按以下格式输出分析报告：

**如果是探测设备数量分析：**
1. 核心结论：直接回答各运营商的设备数量分布
2. 数量统计：列出各运营商的设备数量和占比
3. 分布分析：分析设备数量的分布特征
4. 趋势建议：基于设备数量给出运维建议

**如果是探测设备质量分析：**
1. 核心结论：直接回答哪些设备质量最好/最差
2. 设备排名：列出hostname + 具体丢包率和RTT数值
3. 性能分布：分析整体设备质量分布情况
4. 优化建议：针对质量差的设备提出具体改进措施

**如果是目标节点丢包分析：**
1. 核心结论：直接回答哪些目标节点性能最优
2. 节点排名：按丢包率排序，区分task_name
3. 任务对比：不同探测任务的性能差异
4. 选择建议：推荐具体的目标节点选择方案

**如果是地区覆盖质量评估：**
1. 核心结论：直接回答哪些目标节点覆盖浙江电信质量最好
2. 覆盖分析：各目标节点在浙江电信的丢包率排名
3. 质量评估：具体的网络质量指标和表现
4. 推荐清单：TOP3优质目标节点及使用建议

⚠️  注意事项：
- 必须使用数据摘要中的具体数值，不要编造
- 避免模糊表述，要明确指出具体的设备/节点名称
- 提供可操作的建议，让用户能够直接决策
- 回复控制在500字以内，信息要密集有价值
"""

    if chart_path:
        user_prompt += f"\n图表路径: {chart_path}"

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
