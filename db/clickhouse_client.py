"""
ClickHouse 数据库客户端
实现安全查询和限制逻辑
"""
import logging
from typing import Optional, List, Dict, Any
import pandas as pd
from clickhouse_driver import Client
from clickhouse_driver.errors import Error as ClickHouseError

from config.settings import settings

logger = logging.getLogger(__name__)


class ClickHouseClient:
    """ClickHouse 客户端，包含安全限制"""
    
    # 危险 SQL 关键字（禁止执行）
    DANGEROUS_KEYWORDS = [
        'insert', 'update', 'delete', 'drop', 'alter', 
        'create', 'truncate', 'grant', 'revoke', 'exec'
    ]
    
    def __init__(self):
        """初始化 ClickHouse 客户端"""
        if not settings.CLICKHOUSE_ENABLE:
            raise ValueError("ClickHouse 未启用")
        
        if not settings.CLICKHOUSE_ADDRESSES:
            raise ValueError("ClickHouse 地址未配置")
        
        # 解析地址
        host, port = self._parse_address(settings.CLICKHOUSE_ADDRESSES[0])
        
        try:
            self.client = Client(
                host=host,
                port=port,
                database=settings.CLICKHOUSE_DATABASE,
                user=settings.CLICKHOUSE_USERNAME,
                password=settings.CLICKHOUSE_PASSWORD,
                connect_timeout=10,
                send_receive_timeout=300
            )
            logger.info(f"ClickHouse 连接成功: {host}:{port}")
        except Exception as e:
            logger.error(f"ClickHouse 连接失败: {e}")
            raise
    
    @staticmethod
    def _parse_address(address: str) -> tuple:
        """
        解析地址字符串
        
        Args:
            address: 地址字符串，格式 "host:port"
            
        Returns:
            (host, port) 元组
        """
        if ':' not in address:
            raise ValueError(f"地址格式错误: {address}")
        
        parts = address.split(':')
        if len(parts) != 2:
            raise ValueError(f"地址格式错误: {address}")
        
        host = parts[0].strip()
        try:
            port = int(parts[1].strip())
        except ValueError:
            raise ValueError(f"端口格式错误: {address}")
        
        return host, port
    
    def _validate_sql(self, sql: str) -> None:
        """
        验证 SQL 安全性（卫语句）
        
        Args:
            sql: SQL 语句
            
        Raises:
            ValueError: SQL 不安全
        """
        if not sql:
            raise ValueError("SQL 语句不能为空")
        
        sql_lower = sql.lower().strip()
        
        # 检查是否只允许 SELECT
        if not sql_lower.startswith('select'):
            raise ValueError("只允许执行 SELECT 查询")
        
        # 检查危险关键字
        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword in sql_lower:
                raise ValueError(f"SQL 包含危险关键字: {keyword}")
        
        # 检查是否包含时间范围（必须）
        if 'timestamp' not in sql_lower:
            logger.warning("SQL 未包含 timestamp 字段，可能导致全表扫描")
        
        # 检查是否包含 LIMIT（建议）
        if 'limit' not in sql_lower:
            logger.warning("SQL 未包含 LIMIT，建议添加以限制返回行数")
    
    def _ensure_limit(self, sql: str) -> str:
        """
        确保 SQL 包含 LIMIT（卫语句）
        
        Args:
            sql: SQL 语句
            
        Returns:
            添加了 LIMIT 的 SQL
        """
        sql_lower = sql.lower().strip()
        
        # 如果已有 LIMIT，检查是否超过最大值
        if 'limit' in sql_lower:
            # 提取现有 LIMIT 值（简单处理）
            import re
            limit_match = re.search(r'limit\s+(\d+)', sql_lower, re.IGNORECASE)
            if limit_match:
                existing_limit = int(limit_match.group(1))
                if existing_limit > settings.MAX_QUERY_ROWS:
                    # 替换为最大限制
                    sql = re.sub(
                        r'limit\s+\d+',
                        f'LIMIT {settings.MAX_QUERY_ROWS}',
                        sql,
                        flags=re.IGNORECASE
                    )
                    logger.warning(f"LIMIT 值超过最大值，已调整为 {settings.MAX_QUERY_ROWS}")
            return sql
        
        # 如果没有 LIMIT，添加
        max_limit = settings.MAX_QUERY_ROWS
        if sql.rstrip().endswith(';'):
            sql = sql.rstrip()[:-1]
        
        sql = f"{sql} LIMIT {max_limit}"
        logger.info(f"自动添加 LIMIT {max_limit}")
        return sql
    
    def execute_query(self, sql: str) -> pd.DataFrame:
        """
        执行安全查询
        
        Args:
            sql: SQL 语句
            
        Returns:
            查询结果 DataFrame
            
        Raises:
            ValueError: SQL 验证失败
            ClickHouseError: 查询执行失败
        """
        # 验证 SQL 安全性
        self._validate_sql(sql)
        
        # 确保包含 LIMIT
        sql = self._ensure_limit(sql)
        
        logger.info(f"执行查询: {sql}")
        
        try:
            # 执行查询
            result = self.client.query_dataframe(sql)
            
            if result is None:
                logger.warning("查询返回空结果")
                return pd.DataFrame()
            
            row_count = len(result)
            logger.info(f"查询成功，返回 {row_count} 行")
            
            # 检查结果大小
            if row_count >= settings.MAX_QUERY_ROWS:
                logger.warning(f"返回行数达到限制上限 {settings.MAX_QUERY_ROWS}，可能需要聚合查询")
            
            return result
            
        except ClickHouseError as e:
            logger.error(f"ClickHouse 查询失败: {e}")
            raise
        except Exception as e:
            logger.error(f"查询执行异常: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        测试连接
        
        Returns:
            连接是否成功
        """
        if not self.client:
            return False
        
        try:
            result = self.client.execute("SELECT 1")
            return result is not None
        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return False


# 全局客户端实例（懒加载）
_client: Optional[ClickHouseClient] = None


def get_client() -> ClickHouseClient:
    """
    获取 ClickHouse 客户端实例（单例模式）
    
    Returns:
        ClickHouseClient 实例
    """
    global _client
    
    if _client is not None:
        return _client
    
    if not settings.CLICKHOUSE_ENABLE:
        raise ValueError("ClickHouse 未启用")
    
    _client = ClickHouseClient()
    return _client

