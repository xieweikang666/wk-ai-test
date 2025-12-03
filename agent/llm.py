"""
LLM 模型调用封装
"""
import logging
from typing import Optional, List, Dict, Any
from openai import OpenAI

from config.settings import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM 客户端封装"""
    
    def __init__(self):
        """初始化 LLM 客户端"""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY 未配置")
        
        if not settings.OPENAI_API_BASE:
            raise ValueError("OPENAI_API_BASE 未配置")
        
        # 临时清除可能影响初始化的环境变量
        import os
        import httpx
        
        saved_proxy_vars = {}
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy', 'NO_PROXY', 'no_proxy']
        for var in proxy_vars:
            if var in os.environ:
                saved_proxy_vars[var] = os.environ.pop(var)
        
        try:
            # 创建不使用代理的 httpx 客户端
            http_client = httpx.Client(
                timeout=60.0,
                follow_redirects=True
            )
            
            # 使用自定义 http_client 初始化 OpenAI
            self.client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_API_BASE,
                http_client=http_client
            )
            
            self.model = settings.OPENAI_MODEL
            logger.info(f"LLM 客户端初始化完成，模型: {self.model}")
            
            # 初始化成功，不恢复代理环境变量（避免影响 API 调用）
            
        except Exception as e:
            # 初始化失败，恢复环境变量
            os.environ.update(saved_proxy_vars)
            logger.error(f"LLM 客户端初始化失败: {e}")
            raise
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        调用 LLM 进行对话
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            functions: Function Calling 定义列表
            function_call: Function Calling 模式（"auto", "none", 或函数名）
            
        Returns:
            LLM 响应字典
        """
        if not messages:
            raise ValueError("消息列表不能为空")
        
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature
            }
            
            # 添加 Function Calling 参数
            if functions:
                kwargs["functions"] = functions
                if function_call:
                    kwargs["function_call"] = function_call
                else:
                    kwargs["function_call"] = "auto"
            
            response = self.client.chat.completions.create(**kwargs)
            
            if not response:
                raise ValueError("LLM 响应为空")
            
            result = {
                "content": response.choices[0].message.content,
                "role": response.choices[0].message.role,
                "function_call": None
            }
            
            # 处理 Function Calling
            if response.choices[0].message.function_call:
                result["function_call"] = {
                    "name": response.choices[0].message.function_call.name,
                    "arguments": response.choices[0].message.function_call.arguments
                }
            
            logger.info("LLM 调用成功")
            return result
            
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise


# 全局客户端实例（懒加载）
_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    获取 LLM 客户端实例（单例模式）
    
    Returns:
        LLMClient 实例
    """
    global _client
    
    if _client is not None:
        return _client
    
    _client = LLMClient()
    return _client

