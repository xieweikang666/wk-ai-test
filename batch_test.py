#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络探测数据查询分析 - MVP版本
"""
import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.clickhouse_client import ClickHouseClient

class NetworkAnalyzer:
    """网络探测数据分析器"""
    
    def __init__(self):
        self.ch_client = ClickHouseClient()
        
    def _get_time_range(self, time_desc: str) -> tuple:
        """获取时间范围戳"""
        now = datetime.now()
        
        if "近1h" in time_desc or "近1小时" in time_desc:
            start = int((now - timedelta(hours=1)).timestamp())
        elif "近3h" in time_desc or "近3小时" in time_desc:
            start = int((now - timedelta(hours=3)).timestamp())
        elif "昨天晚高峰" in time_desc:
            yesterday = now - timedelta(days=1)
            start_time = yesterday.replace(hour=19, minute=0, second=0, microsecond=0)
            end_time = yesterday.replace(hour=23, minute=0, second=0, microsecond=0)
            return int(start_time.timestamp()), int(end_time.timestamp())
        else:
            start = int((now - timedelta(hours=1)).timestamp())
            
        return start, int(now.timestamp())
    
    def _execute_and_analyze(self, sql: str) -> pd.DataFrame:
        """执行SQL并返回结果"""
        try:
            return self.ch_client.execute_query(sql)
        except Exception as e:
            print(f"查询失败: {e}")
            return pd.DataFrame()
    
    # 核心查询方法
    def query_device_performance(self, time_range: str = "近1h") -> pd.DataFrame:
        """查询设备性能指标"""
        start_ts, end_ts = self._get_time_range(time_range)
        
        sql = f"""
        SELECT hostname, task_name, 
               AVG(avg_rtt) as avg_rtt, 
               AVG(avg_lost) as avg_lost, 
               COUNT(*) as sample_count
        FROM detect_ping_log
        WHERE timestamp >= {start_ts} AND timestamp <= {end_ts}
        GROUP BY hostname, task_name
        ORDER BY hostname, task_name
        """
        
        return self._execute_and_analyze(sql)
    
    def query_node_packet_loss(self, time_range: str = "近1h") -> pd.DataFrame:
        """查询节点丢包情况"""
        start_ts, end_ts = self._get_time_range(time_range)
        
        sql = f"""
        SELECT target_node, task_name,
               AVG(avg_lost) as avg_lost_rate,
               MAX(avg_lost) as max_lost_rate,
               MIN(avg_lost) as min_lost_rate,
               COUNT(*) as sample_count,
               COUNT(DISTINCT hostname) as device_count
        FROM detect_ping_log
        WHERE timestamp >= {start_ts} AND timestamp <= {end_ts}
        GROUP BY target_node, task_name
        ORDER BY target_node, avg_lost_rate
        """
        
        return self._execute_and_analyze(sql)
    
    def query_regional_coverage(self, time_range: str = "近1h") -> pd.DataFrame:
        """查询地区覆盖情况"""
        start_ts, end_ts = self._get_time_range(time_range)
        
        sql = f"""
        SELECT target_node, src_isp, src_province,
               AVG(avg_lost) as avg_lost_rate,
               COUNT(*) as sample_count,
               COUNT(DISTINCT hostname) as device_count
        FROM detect_ping_log
        WHERE timestamp >= {start_ts} AND timestamp <= {end_ts}
        GROUP BY target_node, src_isp, src_province
        ORDER BY target_node, avg_lost_rate
        """
        
        return self._execute_and_analyze(sql)
    
    def query_isp_devices(self, time_range: str = "近1h") -> pd.DataFrame:
        """查询运营商设备分布"""
        start_ts, end_ts = self._get_time_range(time_range)
        
        sql = f"""
        SELECT src_isp,
               COUNT(DISTINCT hostname) as device_count,
               COUNT(*) as total_samples,
               COUNT(DISTINCT task_name) as task_count
        FROM detect_ping_log
        WHERE timestamp >= {start_ts} AND timestamp <= {end_ts}
        GROUP BY src_isp
        ORDER BY device_count DESC
        """
        
        return self._execute_and_analyze(sql)

if __name__ == "__main__":
    # 使用示例
    analyzer = NetworkAnalyzer()
    
    # 查询各运营商设备分布
    print("各运营商设备分布:")
    df = analyzer.query_isp_devices()
    print(df.head())