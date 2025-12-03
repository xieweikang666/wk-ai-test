"""
配置管理模块
"""
import os
import logging
from typing import List
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
    OPENAI_API_KEY: str = "sk-Yle3nSp72pPw66kaHy4goZmjPdz5oHTrwUdcY29ITTWWNtHq"
    OPENAI_API_BASE: str = "https://geekai.co/api/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # ClickHouse 配置（阿里云）
    CLICKHOUSE_ENABLE: bool = True
    CLICKHOUSE_ADDRESSES: List[str] = ["cc-2zet16rb5415n61g4-ck-l5.clickhouseserver.rds.aliyuncs.com:9000"]
    CLICKHOUSE_DATABASE: str = "detect"
    CLICKHOUSE_USERNAME: str = "zcdn"
    CLICKHOUSE_PASSWORD: str = "0b6e38A0b3c0cf"
    CLICKHOUSE_TABLE_PING: str = "detect_ping_log"
    
    # 查询限制
    MAX_QUERY_ROWS: int = 1000000
    
    # 静态文件目录
    STATIC_DIR: str = "static"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


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
