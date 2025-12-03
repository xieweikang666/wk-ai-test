"""
图表生成模块
使用 Matplotlib 生成各种类型的图表
"""
import os
from datetime import datetime
from typing import Optional, List
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from config.settings import settings


# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def ensure_static_dir():
    """确保 static 目录存在"""
    if not os.path.exists(settings.STATIC_DIR):
        os.makedirs(settings.STATIC_DIR)


def draw_chart(
    df: pd.DataFrame,
    chart_type: str = "line",
    x_column: Optional[str] = None,
    y_columns: Optional[List[str]] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None
) -> str:
    """
    生成图表并保存到 static 目录
    
    Args:
        df: 数据 DataFrame
        chart_type: 图表类型 (line, bar, scatter, histogram)
        x_column: X 轴列名
        y_columns: Y 轴列名列表（支持多列）
        title: 图表标题
        xlabel: X 轴标签
        ylabel: Y 轴标签
        
    Returns:
        图表文件路径（相对于根目录）
    """
    if df.empty:
        raise ValueError("数据框为空，无法生成图表")
    
    ensure_static_dir()
    
    # 自动选择列
    if x_column is None:
        # 尝试找到时间列
        time_cols = ['timestamp', 'time', 'date', 'datetime']
        for col in time_cols:
            if col in df.columns:
                x_column = col
                break
        
        # 如果没有时间列，使用索引
        if x_column is None:
            x_column = df.index.name if df.index.name else "index"
            df = df.reset_index()
    
    if y_columns is None:
        # 自动选择数值列
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if x_column in numeric_cols:
            numeric_cols.remove(x_column)
        y_columns = numeric_cols[:3]  # 最多显示3列
    
    if not y_columns:
        raise ValueError("没有可用的数值列用于绘图")
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 处理时间列
    x_data = df[x_column]
    if x_column in ['timestamp'] and df[x_column].dtype in ['int64', 'int32']:
        # 转换时间戳为 datetime
        x_data = pd.to_datetime(df[x_column], unit='s')
    
    # 绘制不同类型的图表
    if chart_type == "line":
        for y_col in y_columns:
            ax.plot(x_data, df[y_col], marker='o', label=y_col, linewidth=2, markersize=4)
        ax.legend()
        
    elif chart_type == "bar":
        x_pos = range(len(df))
        width = 0.8 / len(y_columns)
        for i, y_col in enumerate(y_columns):
            offset = (i - len(y_columns) / 2) * width
            ax.bar([p + offset for p in x_pos], df[y_col], width, label=y_col)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(x_data, rotation=45, ha='right')
        ax.legend()
        
    elif chart_type == "scatter":
        if len(y_columns) == 1:
            ax.scatter(x_data, df[y_columns[0]], alpha=0.6, s=50)
        else:
            # 多列散点图
            for y_col in y_columns:
                ax.scatter(x_data, df[y_col], alpha=0.6, s=50, label=y_col)
            ax.legend()
        
    elif chart_type == "histogram":
        for y_col in y_columns:
            ax.hist(df[y_col], bins=30, alpha=0.6, label=y_col)
        ax.legend()
        
    else:
        raise ValueError(f"不支持的图表类型: {chart_type}")
    
    # 设置标签和标题
    if xlabel:
        ax.set_xlabel(xlabel)
    else:
        ax.set_xlabel(x_column)
    
    if ylabel:
        ax.set_ylabel(ylabel)
    else:
        if len(y_columns) == 1:
            ax.set_ylabel(y_columns[0])
        else:
            ax.set_ylabel("数值")
    
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    
    # 格式化时间轴
    if x_column in ['timestamp'] or 'time' in x_column.lower():
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    
    # 保存文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chart_{timestamp}.png"
    filepath = os.path.join(settings.STATIC_DIR, filename)
    
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    return f"/static/{filename}"


