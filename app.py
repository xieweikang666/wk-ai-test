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
import os
import sys

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
    if not os.path.exists(settings.STATIC_DIR):
        os.makedirs(settings.STATIC_DIR)
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
except Exception as e:
    logger.warning(f"静态文件目录挂载失败: {e}")

# 检查是否为生产模式（--prod 参数）
PROD_MODE = "--prod" in sys.argv

# 生产模式下挂载React构建文件
if PROD_MODE:
    try:
        react_build_dir = "frontend/build"
        if os.path.exists(react_build_dir) and os.path.exists(f"{react_build_dir}/index.html"):
            # 挂载React静态文件
            app.mount("/static", StaticFiles(directory=f"{react_build_dir}/static"), name="react_static")
            logger.info(f"生产模式：已挂载React构建文件从 {react_build_dir}")
        else:
            logger.warning(f"生产模式：未找到React构建文件 {react_build_dir}")
    except Exception as e:
        logger.warning(f"React构建文件挂载失败: {e}")


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
    quality_summary: Optional[str] = None  # 质量摘要（智能引擎）


@app.get("/")
async def root():
    """根路径 - 根据模式返回不同页面"""
    if PROD_MODE:
        # 生产模式：返回React构建的index.html
        react_index = "frontend/build/index.html"
        try:
            if os.path.exists(react_index):
                return FileResponse(react_index, media_type="text/html")
        except Exception as e:
            logger.error(f"无法找到React构建文件: {e}")
    
    # 开发模式或React构建文件不存在：返回原始HTML页面
    index_path = f"{settings.STATIC_DIR}/index.html"
    try:
        return FileResponse(index_path, media_type="text/html")
    except Exception as e:
        logger.error(f"无法找到index.html: {e}")
        return {
            "message": "网络探测数据 AI 分析 Agent",
            "version": "1.0.0",
            "mode": "production" if PROD_MODE else "development",
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
    2. 生成 QueryPlan
    3. 根据配置选择执行器（原始/智能）
    4. 执行查询并分析结果
    5. 可选：生成图表和质量报告
    6. 返回答案和相关信息
    """
    if not request.message:
        raise HTTPException(status_code=400, detail="消息不能为空")
    
    try:
        logger.info(f"收到用户查询: {request.message}")
        
        # 1. 获取规划器
        planner = get_planner()
        
        # 2. 生成 QueryPlan
        query_plan = planner.plan(request.message)
        query_plan["original_query"] = request.message  # 确保原始查询被保存
        
        # 3. 获取执行器（自动选择智能引擎或原始引擎）
        executor = get_executor()
        
        # 4. 检查是否使用了智能引擎
        is_intelligent = settings.ENABLE_INTELLIGENT_ENGINE and hasattr(executor, 'engine')
        
        if is_intelligent:
            # 使用智能引擎执行
            logger.info("使用智能查询引擎执行")
            
            # 直接通过智能引擎执行
            query_result = executor.engine.execute_intelligent_query(
                user_query=request.message,
                query_plan=query_plan,
                enable_quality_check=settings.ENABLE_QUALITY_CHECK
            )
            
            if not query_result["success"]:
                raise Exception(query_result.get("error", "智能查询执行失败"))
            
            # 生成响应
            response_data = executor.engine.generate_response_format(query_result)
            
            response = ChatResponse(
                answer=response_data["answer"],
                chart_url=response_data["chart_url"],
                sql=response_data["sql"],
                quality_summary=response_data.get("quality_summary")
            )
            
        else:
            # 使用原始引擎执行
            logger.info("使用原始查询引擎执行")
            
            # 生成 SQL（用于展示和评估）
            generated_sql = executor.get_generated_sql(query_plan)
            
            # 执行查询
            df = executor.run_query(query_plan)
            
            # 生成图表（如果需要）
            chart_path = None
            if query_plan.get("need_chart", False):
                chart_type = query_plan.get("chart_type", "line")
                chart_path = executor.draw_chart_wrapper(
                    df=df,
                    chart_type=chart_type,
                    title=f"查询结果 - {request.message[:50]}"
                )
            
            # 分析结果
            answer = executor.explain_result(
                df=df,
                query_plan=query_plan,
                chart_path=chart_path
            )
            
            # 返回结果
            response = ChatResponse(
                answer=answer,
                chart_url=chart_path,
                sql=generated_sql,
                quality_summary=None
            )
        
        logger.info("查询处理完成")
        return response
        
    except ValueError as e:
        logger.error(f"参数错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"处理失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@app.get("/engine/status")
async def engine_status():
    """获取当前引擎状态"""
    try:
        return {
            "intelligent_engine_enabled": settings.ENABLE_INTELLIGENT_ENGINE,
            "quality_check_enabled": settings.ENABLE_QUALITY_CHECK,
            "fallback_enabled": settings.INTELLIGENT_ENGINE_FALLBACK,
            "current_engine": "intelligent" if settings.ENABLE_INTELLIGENT_ENGINE else "original"
        }
    except Exception as e:
        logger.error(f"获取引擎状态失败: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/engine/switch")
async def switch_engine(enable_intelligent: bool = None):
    """切换查询引擎（仅用于开发测试）"""
    try:
        if enable_intelligent is None:
            raise HTTPException(status_code=400, detail="请指定是否启用智能引擎")
        
        # 更新配置（临时，重启后恢复）
        settings.ENABLE_INTELLIGENT_ENGINE = enable_intelligent
        
        # 清除执行器缓存以应用新配置
        global _executor
        from agent.functions import _executor as func_executor
        func_executor = None
        
        status = "intelligent" if enable_intelligent else "original"
        logger.info(f"引擎已切换为: {status}")
        
        return {
            "message": f"已切换到{status}引擎",
            "current_engine": status,
            "intelligent_engine_enabled": settings.ENABLE_INTELLIGENT_ENGINE
        }
        
    except Exception as e:
        logger.error(f"引擎切换失败: {e}")
        raise HTTPException(status_code=500, detail=f"引擎切换失败: {str(e)}")


@app.get("/engine/quality")
async def get_quality_metrics():
    """获取智能引擎质量指标（如果启用）"""
    if not settings.ENABLE_INTELLIGENT_ENGINE:
        return {"message": "智能引擎未启用"}
    
    try:
        # 这里可以添加更多质量指标收集逻辑
        return {
            "status": "intelligent_engine_active",
            "quality_check_enabled": settings.ENABLE_QUALITY_CHECK,
            "metrics": {
                "sql_generation_quality": "enabled",
                "result_analysis_quality": "enabled", 
                "anomaly_detection": "enabled",
                "semantic_understanding": "enabled"
            }
        }
    except Exception as e:
        logger.error(f"获取质量指标失败: {e}")
        return {"status": "error", "message": str(e)}


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
    parser.add_argument("--prod", action="store_true", help="生产模式：服务React构建文件")
    
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
        
        # 根据模式显示不同信息
        if args.prod:
            print(f"🚀 启动生产模式服务: http://{args.host}:{args.port}")
            print("📦 生产模式：服务React构建文件")
        else:
            print(f"🚀 启动开发模式服务: http://{args.host}:{args.port}")
            print("🛠️  开发模式：需要单独启动React前端")
        
        uvicorn.run(app, host=args.host, port=args.port)

