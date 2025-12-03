"""
FastAPI 主入口
提供 /chat API 接口
"""
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

from agent.simple_planner import get_planner
from agent.functions import get_executor
from config.settings import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="网络探测数据 AI 分析 Agent",
    description="基于 ClickHouse + RAG + Function Calling 的数据分析系统",
    version="1.0.0"
)

# 挂载静态文件目录
try:
    import os
    if not os.path.exists(settings.STATIC_DIR):
        os.makedirs(settings.STATIC_DIR)
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
except Exception as e:
    logger.warning(f"静态文件目录挂载失败: {e}")


# 请求模型
class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str


# 响应模型
class ChatResponse(BaseModel):
    """聊天响应模型"""
    answer: str
    chart_url: Optional[str] = None
    sql: Optional[str] = None  # 生成的 SQL（用于评估）


@app.get("/")
async def root():
    """根路径 - 返回ChatGPT风格交互页面"""
    index_path = f"{settings.STATIC_DIR}/index.html"
    try:
        return FileResponse(index_path, media_type="text/html")
    except Exception as e:
        logger.error(f"无法找到index.html: {e}")
        return {
            "message": "网络探测数据 AI 分析 Agent",
            "version": "1.0.0",
            "endpoints": {
                "/chat": "POST - 发送自然语言查询",
                "/health": "GET - 健康检查"
            }
        }


@app.get("/health")
async def health():
    """健康检查"""
    try:
        # 检查 ClickHouse 连接
        from db.clickhouse_client import get_client
        client = get_client()
        if client.test_connection():
            return {"status": "healthy", "clickhouse": "connected"}
        return {"status": "unhealthy", "clickhouse": "disconnected"}
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {"status": "unhealthy", "error": str(e)}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天接口 - 处理自然语言查询
    
    流程：
    1. 用户输入问题
    2. RAG 检索数据库上下文
    3. LLM 生成 QueryPlan
    4. 根据 QueryPlan 生成 SQL 并执行
    5. 可选：生成图表
    6. LLM 分析结果
    7. 返回答案和图表路径
    """
    if not request.message:
        raise HTTPException(status_code=400, detail="消息不能为空")
    
    try:
        logger.info(f"收到用户查询: {request.message}")
        
        # 1. 获取规划器和执行器
        planner = get_planner()
        executor = get_executor()
        
        # 2. 生成 QueryPlan
        query_plan = planner.plan(request.message)
        
        # 3. 生成 SQL（用于展示和评估）
        # 注意：这里需要访问私有方法，为了展示 SQL，我们通过一个公开方法获取
        generated_sql = executor.get_generated_sql(query_plan)
        
        # 4. 执行查询
        df = executor.run_query(query_plan)
        
        # 5. 生成图表（如果需要）
        chart_path = None
        if query_plan.get("need_chart", False):
            chart_type = query_plan.get("chart_type", "line")
            chart_path = executor.draw_chart_wrapper(
                df=df,
                chart_type=chart_type,
                title=f"查询结果 - {request.message[:50]}"
            )
        
        # 6. 分析结果
        answer = executor.explain_result(
            df=df,
            query_plan=query_plan,
            chart_path=chart_path
        )
        
        # 7. 返回结果
        response = ChatResponse(
            answer=answer,
            chart_url=chart_path,
            sql=generated_sql  # 输出 SQL 供评估
        )
        
        logger.info("查询处理完成")
        return response
        
    except ValueError as e:
        logger.error(f"参数错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"处理失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


if __name__ == "__main__":
    import sys
    import argparse
    
    # 先解析所有参数来判断模式
    parser = argparse.ArgumentParser(description="网络探测数据 AI 分析 Agent")
    parser.add_argument("-q", "--question", help="CLI模式：指定问题")
    parser.add_argument("--test", action="store_true", help="CLI模式：运行测试")
    parser.add_argument("--quiet", action="store_true", help="CLI模式：静默运行")
    parser.add_argument("-Q", "--verify", action="store_true", help="CLI模式：验证模式")
    parser.add_argument("--host", default="0.0.0.0", help="Web模式：绑定地址")
    parser.add_argument("--port", type=int, default=8000, help="Web模式：端口号")
    
    args = parser.parse_args()
    
    # 判断是否为CLI模式
    cli_mode = args.question or args.test or args.quiet or args.verify
    
    if cli_mode:
        # CLI模式
        try:
            from cli import main as cli_main
            cli_main()
        except ImportError as e:
            print(f"❌ CLI 模块导入失败: {e}")
            print("请确保 cli.py 文件存在")
            sys.exit(1)
    else:
        # Web服务模式
        import uvicorn
        print(f"🚀 启动Web服务: http://{args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)

