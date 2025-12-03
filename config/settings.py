"""
配置管理模块
"""
import os
import logging
from typing import List
from pydantic import Field
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """应用配置"""
    
    # LLM 配置（GPT-4o mini - 国内 API）
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    OPENAI_API_BASE: str = Field(default="https://geekai.co/api/v1", env="OPENAI_API_BASE")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    
  # ClickHouse 配置（阿里云）
    CLICKHOUSE_ENABLE: bool = Field(default=True, env="CLICKHOUSE_ENABLE")
    CLICKHOUSE_DATABASE: str = Field(default="detect", env="CLICKHOUSE_DATABASE")
    CLICKHOUSE_USERNAME: str = Field(default="zcdn", env="CLICKHOUSE_USERNAME")
    CLICKHOUSE_PASSWORD: str = Field(default="", env="CLICKHOUSE_PASSWORD")
    CLICKHOUSE_TABLE_PING: str = Field(default="detect_ping_log", env="CLICKHOUSE_TABLE_PING")
    
    # 查询限制
    MAX_QUERY_ROWS: int = Field(default=1000000, env="MAX_QUERY_ROWS")
    
    # 静态文件目录
    STATIC_DIR: str = Field(default="static", env="STATIC_DIR")
    
    # 智能引擎配置
    ENABLE_INTELLIGENT_ENGINE: bool = Field(default=False, env="ENABLE_INTELLIGENT_ENGINE")
    ENABLE_QUALITY_CHECK: bool = Field(default=True, env="ENABLE_QUALITY_CHECK")
    INTELLIGENT_ENGINE_FALLBACK: bool = Field(default=True, env="INTELLIGENT_ENGINE_FALLBACK")
    
    @property
    def CLICKHOUSE_ADDRESSES(self) -> List[str]:
        """从环境变量解析地址列表"""
        addresses_str = os.getenv("CLICKHOUSE_ADDRESSES", "cc-2zet16rb5415n61g4-ck-l5.clickhouseserver.rds.aliyuncs.com:9000")
        return [addr.strip() for addr in addresses_str.split(",") if addr.strip()]


def init_settings() -> Settings:
    """
    初始化配置并设置环境变量
    
    Returns:
        Settings 实例
    """
    settings = Settings()
    
    # 设置环境变量（用于 OpenAI SDK）
    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY 未设置")
        return settings
    
    if not settings.OPENAI_API_BASE:
        logger.warning("OPENAI_API_BASE 未设置")
        return settings
    
    os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
    os.environ["OPENAI_API_BASE"] = settings.OPENAI_API_BASE
    
    logger.info(f"配置初始化完成，模型: {settings.OPENAI_MODEL}")
    return settings


# 全局配置实例
settings = init_settings()
