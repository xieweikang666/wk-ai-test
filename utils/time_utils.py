"""
时间工具模块
处理时间范围转换（如 last_30_min → 具体时间戳）
"""
from datetime import datetime, timedelta
from typing import Tuple, Optional
import re


def parse_time_range(time_range: str) -> Tuple[int, int]:
    """
    解析时间范围字符串，返回 (start_timestamp, end_timestamp)
    
    支持格式：
    - last_5_min, last_30_min, last_1_hour, last_24_hour
    - between:2024-01-01 00:00:00:2024-01-01 23:59:59
    - timestamp:1609459200:1609545600
    
    Args:
        time_range: 时间范围字符串
        
    Returns:
        (start_timestamp, end_timestamp) 元组，单位：秒
        
    Raises:
        ValueError: 时间格式不支持
    """
    if not time_range:
        raise ValueError("时间范围不能为空")
    
    now = datetime.now()
    end_timestamp = int(now.timestamp())
    
    # 处理相对时间
    if time_range.startswith("last_"):
        match = re.match(r"last_(\d+)_(min|hour|day)", time_range)
        if not match:
            raise ValueError(f"不支持的时间格式: {time_range}")
        
        value = int(match.group(1))
        unit = match.group(2)
        
        if unit == "min":
            delta = timedelta(minutes=value)
        elif unit == "hour":
            delta = timedelta(hours=value)
        elif unit == "day":
            delta = timedelta(days=value)
        else:
            raise ValueError(f"不支持的时间单位: {unit}")
        
        start_time = now - delta
        start_timestamp = int(start_time.timestamp())
        
        return start_timestamp, end_timestamp
    
    # 处理 between 格式
    if time_range.startswith("between:"):
        parts = time_range.replace("between:", "").split(":")
        if len(parts) != 2:
            raise ValueError(f"between 格式错误: {time_range}")
        
        try:
            start_str = parts[0].strip()
            end_str = parts[1].strip()
            
            # 尝试解析为 datetime
            start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
            end_dt = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
            
            return int(start_dt.timestamp()), int(end_dt.timestamp())
        except ValueError as e:
            raise ValueError(f"时间解析失败: {e}")
    
    # 处理 timestamp 格式
    if time_range.startswith("timestamp:"):
        parts = time_range.replace("timestamp:", "").split(":")
        if len(parts) != 2:
            raise ValueError(f"timestamp 格式错误: {time_range}")
        
        try:
            start_ts = int(parts[0].strip())
            end_ts = int(parts[1].strip())
            return start_ts, end_ts
        except ValueError as e:
            raise ValueError(f"时间戳解析失败: {e}")
    
    raise ValueError(f"不支持的时间格式: {time_range}")


def format_timestamp(timestamp: int) -> str:
    """
    格式化时间戳为可读字符串
    
    Args:
        timestamp: 时间戳（秒）
        
    Returns:
        格式化的时间字符串
    """
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


