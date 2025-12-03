"""
简化数据分析器 - 生成精简、高价值的回答
"""
import logging
from typing import Dict, Any, Optional
import pandas as pd

logger = logging.getLogger(__name__)

def analyze_result(
    df: pd.DataFrame,
    query_plan: Dict[str, Any],
    chart_path: Optional[str] = None
) -> str:
    """
    分析查询结果并生成精简的自然语言说明
    
    Args:
        df: 查询结果 DataFrame
        query_plan: 原始 QueryPlan
        chart_path: 图表路径（可选）
        
    Returns:
        精简的分析结果文本
    """
    if df is None or df.empty:
        return "查询结果为空，无法进行分析。"
    
    try:
        # 根据查询类型生成精简分析
        analysis_type = _determine_analysis_type(query_plan)
        
        if analysis_type == "device_count":
            return _analyze_device_count(df)
        elif analysis_type == "network_quality":
            return _analyze_network_quality(df)
        elif analysis_type == "packet_loss":
            return _analyze_packet_loss(df)
        else:
            return _generate_generic_analysis(df)
            
    except Exception as e:
        logger.error(f"结果分析异常: {e}")
        return f"结果分析失败: {str(e)}"


def _determine_analysis_type(query_plan: Dict[str, Any]) -> str:
    """确定分析类型"""
    metrics = query_plan.get("metrics", [])
    aggregation = query_plan.get("aggregation", "")
    
    if "device_count" in metrics:
        return "device_count"
    elif aggregation == "group_by_target_node":
        return "packet_loss"
    elif "avg_rtt" in metrics or "avg_lost" in metrics:
        return "network_quality"
    else:
        return "generic"


def _analyze_device_count(df: pd.DataFrame) -> str:
    """分析设备数量统计"""
    if df.empty or 'device_count' not in df.columns:
        return "无法分析设备数量数据。"
    
    # 找出设备数量最多的运营商
    max_row = df.loc[df['device_count'].idxmax()]
    min_row = df.loc[df['device_count'].idxmin()]
    
    total_devices = df['device_count'].sum()
    isp_name = max_row.get('src_isp', '未知运营商')
    
    return f"""
📊 **设备分布概览**

• **{isp_name}** 设备最多：{max_row['device_count']}台 ({max_row['device_count']/total_devices*100:.1f}%)
• **{min_row.get('src_isp', '未知运营商')}** 设备最少：{min_row['device_count']}台
• 总计：{total_devices}台探测设备

💡 **建议**：关注设备分布均衡性，适当增加设备较少运营商的覆盖。
""".strip()


def _analyze_network_quality(df: pd.DataFrame) -> str:
    """分析网络质量"""
    if df.empty:
        return "无法分析网络质量数据。"
    
    avg_lost = df['avg_lost'].mean() if 'avg_lost' in df.columns else 0
    avg_rtt = df['avg_rtt'].mean() if 'avg_rtt' in df.columns else 0
    
    # 评估网络质量
    if avg_lost < 1 and avg_rtt < 50:
        quality = "优秀"
        emoji = "🟢"
    elif avg_lost < 3 and avg_rtt < 100:
        quality = "良好" 
        emoji = "🟡"
    else:
        quality = "需优化"
        emoji = "🔴"
    
    return f"""
{emoji} **网络质量评估：{quality}**

• **平均丢包率**：{avg_lost:.2f}%
• **平均延迟**：{avg_rtt:.1f}ms

💡 **建议**：{'网络质量良好，继续保持监控' if quality in ['优秀', '良好'] else '建议优化网络配置，重点改善丢包率和延迟问题'}。
""".strip()


def _analyze_packet_loss(df: pd.DataFrame) -> str:
    """分析丢包情况"""
    if df.empty or 'avg_lost_rate' not in df.columns:
        return "无法分析丢包数据。"
    
    worst_node = df.loc[df['avg_lost_rate'].idxmax()]
    best_node = df.loc[df['avg_lost_rate'].idxmin()]
    
    avg_loss = df['avg_lost_rate'].mean()
    
    return f"""
📈 **丢包率分析**

• **整体平均**：{avg_loss:.2f}%
• **最差节点**：{worst_node.get('target_node', '未知')} ({worst_node['avg_lost_rate']:.2f}%)
• **最佳节点**：{best_node.get('target_node', '未知')} ({best_node['avg_lost_rate']:.2f}%)

💡 **重点关注**：丢包率超过3%的节点需要网络优化。
""".strip()


def _generate_generic_analysis(df: pd.DataFrame) -> str:
    """生成通用分析"""
    if df.empty:
        return "无数据可分析。"
    
    row_count = len(df)
    
    # 找出关键数值列
    numeric_cols = df.select_dtypes(include=['number']).columns
    key_insights = []
    
    for col in numeric_cols:
        if 'count' in col.lower() or 'device' in col.lower():
            total = df[col].sum()
            key_insights.append(f"• 总计 {col.replace('_', ' ')}：{total:,.0f}")
        elif 'avg' in col.lower() or 'rate' in col.lower():
            avg_val = df[col].mean()
            key_insights.append(f"• 平均 {col.replace('_', ' ')}：{avg_val:.2f}")
    
    return f"""
📋 **数据概览**

• 共查询到 {row_count} 条记录
{chr(10).join(key_insights[:3])}

💡 更多详细信息可查看具体数据。
""".strip()