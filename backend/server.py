"""
FastAPI Server - 后端 HTTP API 服务

提供 RESTful API 接口和 SSE 实时通信。
支持 GUI 模式（PyWebView）和本地 Web 模式（浏览器）。

运行方式:
    python -m backend.server              # 使用默认配置
    python -m backend.server --port 9000  # 指定端口
    python -m backend.server --dev        # 开发模式（启用热重载）

环境变量（前缀 DOUYIN_）:
    DOUYIN_PORT          监听端口
    DOUYIN_HOST          监听地址
    DOUYIN_DEV           开发模式
    DOUYIN_LOG_LEVEL     日志级别
"""

import os
from contextlib import asynccontextmanager
from typing import Any

import click
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from pydantic import BaseModel

from .constants import APP_VERSION, RESOURCE_ROOT, SERVER_DEFAULTS
from .routers import (
    aria2_router,
    file_router,
    settings_router,
    system_router,
    task_router,
)
from .sse import sse
from .state import state

_VERSION = APP_VERSION

# ============================================================================
# 响应模型
# ============================================================================


class HealthResponse(BaseModel):
    """健康检查响应"""

    ready: bool
    aria2: bool
    config: bool
    error: str | None


class APIInfoResponse(BaseModel):
    """API 信息响应"""

    name: str
    version: str
    status: str


# ============================================================================
# 应用生命周期
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("🚀 FastAPI Server 启动中...")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # state 在模块导入时已初始化
    logger.info("✓ 应用状态已初始化")

    yield

    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("🧹 正在清理资源...")
    state.cleanup()
    logger.info("✓ 资源已清理")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


# ============================================================================
# 应用初始化
# ============================================================================

app = FastAPI(
    title="Douyin Collector API",
    description="抖音采集工具后端 HTTP API",
    version=_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(task_router)
app.include_router(settings_router)
app.include_router(aria2_router)
app.include_router(file_router)
app.include_router(system_router)


# ============================================================================
# 基础路由
# ============================================================================


@app.get("/api", response_model=APIInfoResponse)
def read_root() -> dict[str, str]:
    """根路径，返回 API 信息"""
    return {
        "name": "Douyin Collector API",
        "version": _VERSION,
        "status": "running",
    }


@app.get("/api/health", response_model=HealthResponse)
def health_check() -> dict[str, Any]:
    """健康检查接口"""
    return state.health_check()


@app.get("/api/events")
async def events_stream():
    """SSE 端点，向前端推送实时事件"""
    return StreamingResponse(
        sse.connect(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ============================================================================
# 静态文件挂载
# ============================================================================

_frontend_dist_dir = os.path.join(RESOURCE_ROOT, "frontend", "dist")

if os.path.exists(_frontend_dist_dir):
    app.mount("/", StaticFiles(directory=_frontend_dist_dir, html=True), name="static")
    logger.info(f"✓ 前端静态文件已挂载: {_frontend_dist_dir}")
else:
    logger.warning(f"前端 dist 目录不存在: {_frontend_dist_dir}")
    logger.warning("请先运行: cd frontend && pnpm build")


# ============================================================================
# 主程序入口
# ============================================================================


def run_server(
    host: str = SERVER_DEFAULTS["HOST"],
    port: int = SERVER_DEFAULTS["PORT"],
    dev: bool = SERVER_DEFAULTS["DEV"],
):
    """启动服务器（供外部调用，如 main.py）"""
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info" if dev else "warning",
    )


@click.command()
@click.option(
    "-h",
    "--host",
    type=str,
    default=SERVER_DEFAULTS["HOST"],
    envvar="DOUYIN_HOST",
    help=f"监听地址，默认 {SERVER_DEFAULTS['HOST']}",
)
@click.option(
    "-p",
    "--port",
    type=int,
    default=SERVER_DEFAULTS["PORT"],
    envvar="DOUYIN_PORT",
    help=f"监听端口，默认 {SERVER_DEFAULTS['PORT']}",
)
@click.option(
    "--dev",
    is_flag=True,
    default=SERVER_DEFAULTS["DEV"],
    envvar="DOUYIN_DEV",
    help="开发模式（启用热重载）",
)
@click.option(
    "--log-level",
    type=click.Choice(
        ["critical", "error", "warning", "info", "debug"], case_sensitive=False
    ),
    default=SERVER_DEFAULTS["LOG_LEVEL"],
    envvar="DOUYIN_LOG_LEVEL",
    help=f"日志级别，默认 {SERVER_DEFAULTS['LOG_LEVEL']}",
)
def main(host: str, port: int, dev: bool, log_level: str):
    """抖音采集工具 FastAPI 服务"""
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("📡 配置信息")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info(f"  监听地址: {host}")
    logger.info(f"  监听端口: {port}")
    logger.info(f"  开发模式: {'启用' if dev else '禁用'}")
    logger.info(f"  日志级别: {log_level}")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    uvicorn.run(
        "backend.server:app",
        host=host,
        port=port,
        reload=dev,
        log_level=log_level,
    )


if __name__ == "__main__":
    main()
