"""
RAG 向量检索模块
基于 schema.md 文档构建向量库
"""
import os
import logging
from typing import List, Optional
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

from config.settings import settings

logger = logging.getLogger(__name__)


class RAGRetriever:
    """RAG 检索器，基于 schema.md 文档"""
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        初始化 RAG 检索器
        
        Args:
            schema_path: schema.md 文件路径，默认使用 db/schema.md
        """
        if schema_path is None:
            schema_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "db",
                "schema.md"
            )
        
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema 文件不存在: {schema_path}")
        
        self.schema_path = schema_path
        self.model = None
        self.index = None
        self.texts = []
        self._load_model()
        self._build_index()
    
    def _load_model(self) -> None:
        """加载嵌入模型"""
        try:
            # 使用轻量级中文模型
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logger.info("嵌入模型加载成功")
        except Exception as e:
            logger.error(f"嵌入模型加载失败: {e}")
            raise
    
    def _load_schema(self) -> str:
        """
        加载 schema 文档
        
        Returns:
            schema 文档内容
        """
        if not os.path.exists(self.schema_path):
            raise FileNotFoundError(f"Schema 文件不存在: {self.schema_path}")
        
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content:
            raise ValueError("Schema 文件为空")
        
        return content
    
    def _split_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """
        将文本分割成块
        
        Args:
            text: 原始文本
            chunk_size: 块大小（字符数）
            
        Returns:
            文本块列表
        """
        if not text:
            return []
        
        # 按段落分割
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) <= chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _build_index(self) -> None:
        """构建向量索引"""
        if self.model is None:
            raise ValueError("模型未加载")
        
        # 加载 schema 文档
        schema_content = self._load_schema()
        
        # 分割文本
        self.texts = self._split_text(schema_content)
        
        if not self.texts:
            raise ValueError("Schema 文本块为空")
        
        logger.info(f"加载了 {len(self.texts)} 个文本块")
        
        # 生成嵌入向量
        embeddings = self.model.encode(self.texts, show_progress_bar=False)
        
        if embeddings is None or len(embeddings) == 0:
            raise ValueError("嵌入向量生成失败")
        
        # 构建 FAISS 索引
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        
        # 转换为 float32
        embeddings = embeddings.astype('float32')
        self.index.add(embeddings)
        
        logger.info(f"向量索引构建完成，维度: {dimension}, 向量数: {len(embeddings)}")
    
    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """
        检索相关文档片段
        
        Args:
            query: 查询文本
            top_k: 返回前 k 个结果
            
        Returns:
            相关文档片段列表
        """
        if not query:
            return []
        
        if self.model is None or self.index is None:
            logger.warning("索引未构建，返回空结果")
            return []
        
        if not self.texts:
            logger.warning("文本库为空，返回空结果")
            return []
        
        # 生成查询向量
        query_embedding = self.model.encode([query])
        query_embedding = query_embedding.astype('float32')
        
        # 搜索
        k = min(top_k, len(self.texts))
        distances, indices = self.index.search(query_embedding, k)
        
        # 提取相关文本
        results = []
        for idx in indices[0]:
            if 0 <= idx < len(self.texts):
                results.append(self.texts[idx])
        
        logger.info(f"检索到 {len(results)} 个相关片段")
        return results
    
    def get_context(self, query: str, top_k: int = 3) -> str:
        """
        获取检索上下文（合并为字符串）
        
        Args:
            query: 查询文本
            top_k: 返回前 k 个结果
            
        Returns:
            合并后的上下文字符串
        """
        chunks = self.retrieve(query, top_k)
        
        if not chunks:
            return ""
        
        return "\n\n".join(chunks)


# 全局检索器实例（懒加载）
_retriever: Optional[RAGRetriever] = None


def get_retriever() -> RAGRetriever:
    """
    获取 RAG 检索器实例（单例模式）
    
    Returns:
        RAGRetriever 实例
    """
    global _retriever
    
    if _retriever is not None:
        return _retriever
    
    _retriever = RAGRetriever()
    return _retriever


