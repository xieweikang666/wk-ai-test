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
    - 自然语言：昨天、今天、前天、昨晚、今天上午、昨天晚高峰19-23点等
    
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
    
    # 处理自然语言时间表达
    if "昨天" in time_range or "昨天" in time_range:
        return _parse_yesterday_time(time_range, now)
    elif "今天" in time_range or "今天" in time_range:
        return _parse_today_time(time_range, now)
    elif "前天" in time_range or "前天" in time_range:
        return _parse_day_before_yesterday_time(time_range, now)
    
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
        end_timestamp = int(now.timestamp())
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


def _parse_yesterday_time(time_range: str, now: datetime) -> Tuple[int, int]:
    """解析昨天的时间范围"""
    yesterday = now - timedelta(days=1)
    yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # 解析具体时间段
    if "晚高峰" in time_range:
        # 查找时间范围，如 19-23点
        time_match = re.search(r'(\d{1,2})[-~到至](\d{1,2})点', time_range)
        if time_match:
            start_hour = int(time_match.group(1))
            end_hour = int(time_match.group(2))
            yesterday_start = yesterday.replace(hour=start_hour, minute=0, second=0, microsecond=0)
            yesterday_end = yesterday.replace(hour=end_hour, minute=59, second=59, microsecond=999999)
        else:
            # 默认晚高峰 19-23点
            yesterday_start = yesterday.replace(hour=19, minute=0, second=0, microsecond=0)
            yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif "晚上" in time_range:
        time_match = re.search(r'(\d{1,2})[-~到至](\d{1,2})点', time_range)
        if time_match:
            start_hour = int(time_match.group(1))
            end_hour = int(time_match.group(2))
            yesterday_start = yesterday.replace(hour=start_hour, minute=0, second=0, microsecond=0)
            yesterday_end = yesterday.replace(hour=end_hour, minute=59, second=59, microsecond=999999)
        else:
            # 默认晚上 19-23点
            yesterday_start = yesterday.replace(hour=19, minute=0, second=0, microsecond=0)
            yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        # 整个昨天
        pass
    
    return int(yesterday_start.timestamp()), int(yesterday_end.timestamp())


def _parse_today_time(time_range: str, now: datetime) -> Tuple[int, int]:
    """解析今天的时间范围"""
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    if "上午" in time_range:
        time_match = re.search(r'(\d{1,2})[-~到至](\d{1,2})点', time_range)
        if time_match:
            start_hour = int(time_match.group(1))
            end_hour = int(time_match.group(2))
            start_time = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
            end_time = now.replace(hour=end_hour, minute=59, second=59, microsecond=999999)
            return int(start_time.timestamp()), int(end_time.timestamp())
        else:
            # 默认上午 8-12点
            start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
            end_time = now.replace(hour=12, minute=0, second=0, microsecond=0)
            return int(start_time.timestamp()), int(end_time.timestamp())
    elif "下午" in time_range:
        time_match = re.search(r'(\d{1,2})[-~到至](\d{1,2})点', time_range)
        if time_match:
            start_hour = int(time_match.group(1))
            end_hour = int(time_match.group(2))
            start_time = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
            end_time = now.replace(hour=end_hour, minute=59, second=59, microsecond=999999)
            return int(start_time.timestamp()), int(end_time.timestamp())
        else:
            # 默认下午 12-18点
            start_time = now.replace(hour=12, minute=0, second=0, microsecond=0)
            end_time = now.replace(hour=18, minute=0, second=0, microsecond=0)
            return int(start_time.timestamp()), int(end_time.timestamp())
    
    # 默认今天到现在
    return int(today_start.timestamp()), int(now.timestamp())


def _parse_day_before_yesterday_time(time_range: str, now: datetime) -> Tuple[int, int]:
    """解析前天的时间范围"""
    day_before_yesterday = now - timedelta(days=2)
    day_before_yesterday_start = day_before_yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    day_before_yesterday_end = day_before_yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return int(day_before_yesterday_start.timestamp()), int(day_before_yesterday_end.timestamp())


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


