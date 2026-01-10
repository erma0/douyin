"""
FastAPI Server - 后端 HTTP API 服务

提供 RESTful API 接口，将 API 类的方法映射为 HTTP 路由。
适用于 Web 模式或需要通过 HTTP 访问后端的场景。

运行方式:
    python -m backend.server              # 使用默认配置
    python -m backend.server --port 9000  # 指定端口
    python -m backend.server --dev        # 开发模式（启用热重载）

环境变量（前缀 DOUYIN_）:
    DOUYIN_PORT          监听端口（默认: 8000）
    DOUYIN_HOST          监听地址（默认: 127.0.0.1）
    DOUYIN_DEV           开发模式（默认: false）
    DOUYIN_LOG_LEVEL     日志级别（默认: info）
"""

import argparse
import asyncio
import json
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from .api import API


# ============================================================================
# 请求/响应模型
# ============================================================================

class StartTaskRequest(BaseModel):
    """启动采集任务的请求模型"""
    type: str
    target: str
    limit: int = 0
    filters: Optional[Dict[str, str]] = None


class SaveSettingsRequest(BaseModel):
    """保存设置的请求模型"""
    cookie: Optional[str] = None
    downloadPath: Optional[str] = None
    maxRetries: Optional[int] = None
    maxConcurrency: Optional[int] = None
    windowWidth: Optional[int] = None
    windowHeight: Optional[int] = None
    enableIncrementalFetch: Optional[bool] = None
    aria2Host: Optional[str] = None
    aria2Port: Optional[int] = None
    aria2Secret: Optional[str] = None


class OpenUrlRequest(BaseModel):
    """打开URL的请求模型"""
    url: str


class ReadConfigFileRequest(BaseModel):
    """读取配置文件的请求模型"""
    file_path: str


class CheckFileExistsRequest(BaseModel):
    """检查文件存在的请求模型"""
    file_path: str


class OpenFolderRequest(BaseModel):
    """打开文件夹的请求模型"""
    folder_path: str


# ============================================================================
# SSE 事件发射器
# ============================================================================

class SSEEmitter:
    """
    SSE 事件发射器

    管理所有 SSE 客户端连接，并广播 JavaScript 代码到前端。
    用于在 HTTP 模式下模拟 PyWebView 的 evaluate_js 功能。
    """

    def __init__(self):
        self._queues: List[asyncio.Queue] = []

    async def emit(self, js_code: str) -> None:
        """
        发送 JS 代码到所有连接的客户端

        Args:
            js_code: 要执行的 JavaScript 代码
        """
        message = {"type": "evaluate_js", "code": js_code}
        data = f"data: {json.dumps(message, ensure_ascii=False)}\n\n"

        # 广播到所有客户端
        for queue in self._queues:
            await queue.put(data)

    async def create_generator(self):
        """
        为每个客户端创建 SSE 生成器

        Yields:
            SSE 格式的消息字符串
        """
        queue: asyncio.Queue = asyncio.Queue()
        self._queues.append(queue)

        try:
            # 连接建立时的 ping
            yield ": ping\n\n"
            while True:
                message = await queue.get()
                yield message
        finally:
            # 客户端断开时清理
            self._queues.remove(queue)


# 全局 SSE 发射器
sse_emitter = SSEEmitter()


# ============================================================================
# Fake Window 对象
# ============================================================================

class FakeWindow:
    """
    模拟 PyWebView 的 window 对象

    提供与 PyWebView window 兼容的接口，
    但实际上通过 SSE 发送 JS 代码到前端执行。

    这使得 API 类无需修改即可在 HTTP 模式下工作。
    """

    def __init__(self, sse_emitter: SSEEmitter):
        self._sse_emitter = sse_emitter

    def evaluate_js(self, js_code: str) -> None:
        """
        执行 JavaScript 代码

        在 PyWebView 模式下，这会直接在 WebView 中执行
        在 HTTP 模式下，我们通过 SSE 发送到前端执行

        Args:
            js_code: 要执行的 JavaScript 代码
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # 如果没有运行中的事件循环（在后台线程中），获取主循环
            loop = asyncio.get_event_loop()

        # 在后台线程中异步发送
        asyncio.run_coroutine_threadsafe(
            self._sse_emitter.emit(js_code),
            loop
        )


# ============================================================================
# 配置管理
# ============================================================================

def get_config() -> Dict[str, Any]:
    """
    获取配置，优先级：环境变量 > 命令行参数 > 默认值

    Returns:
        配置字典
    """
    # 默认配置
    defaults = {
        "host": "127.0.0.1",
        "port": 8000,
        "dev": False,
        "log_level": "info",
    }

    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Douyin Collector FastAPI Server")
    parser.add_argument(
        "--host",
        type=str,
        default=defaults["host"],
        help=f"监听地址 (默认: {defaults['host']})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=defaults["port"],
        help=f"监听端口 (默认: {defaults['port']})"
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        default=defaults["dev"],
        help="开发模式，启用热重载"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=defaults["log_level"],
        choices=["critical", "error", "warning", "info", "debug"],
        help=f"日志级别 (默认: {defaults['log_level']})"
    )

    args = parser.parse_args()

    # 环境变量覆盖命令行参数（DOUYIN_ 前缀）
    config = {
        "host": os.getenv("DOUYIN_HOST", args.host),
        "port": int(os.getenv("DOUYIN_PORT", str(args.port))),
        "dev": os.getenv("DOUYIN_DEV", "").lower() in ("true", "1", "yes", "on") or args.dev,
        "log_level": os.getenv("DOUYIN_LOG_LEVEL", args.log_level),
    }

    return config


# ============================================================================
# 应用生命周期
# ============================================================================

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 FastAPI Server 启动中...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    yield
    # 关闭时执行
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧹 正在清理资源...")
    api_instance.cleanup()
    print("✓ 资源已清理")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


# ============================================================================
# 应用初始化
# ============================================================================

app = FastAPI(
    title="Douyin Collector API",
    description="抖音采集工具后端 HTTP API",
    version="1.0.0",
    lifespan=lifespan,
)

# 创建 API 实例
api_instance = API()

# 注入 FakeWindow 到 API 实例
# 这使得 API 类在 HTTP 模式下也能使用 evaluate_js
# 实际上会通过 SSE 将 JS 代码发送到前端执行
fake_window = FakeWindow(sse_emitter)
api_instance.set_webview_window(fake_window)


# ============================================================================
# 处理所有来自 API 的路由
# ============================================================================

def register_api_routes(router: APIRouter, api: API) -> None:
    """
    注册所有来自 API 类的路由

    Args:
        router: APIRouter 实例
        api: API 类实例
    """

    # ========================================================================
    # 任务管理接口
    # ========================================================================

    @router.post("/api/task/start")
    def start_task(request: StartTaskRequest) -> Dict[str, Any]:
        """
        开始采集任务

        - type: 任务类型（user/post/search/music等）
        - target: 目标链接或关键词
        - limit: 采集数量限制（0表示不限制）
        - filters: 筛选条件（可选）
        """
        try:
            result = api.start_task(
                type=request.type,
                target=request.target,
                limit=request.limit,
                filters=request.filters
            )
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/api/task/status")
    def get_task_status(task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取任务状态

        - task_id: 任务ID（可选，不提供则返回所有任务状态）
        """
        try:
            return api.get_task_status(task_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/api/task/results")
    def get_task_results(task_id: str) -> List[Dict[str, Any]]:
        """
        获取任务的采集结果

        - task_id: 任务ID
        """
        try:
            return api.get_task_results(task_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ========================================================================
    # 设置管理接口
    # ========================================================================

    @router.get("/api/settings")
    def get_settings() -> Dict[str, Any]:
        """获取当前应用设置"""
        try:
            return api.get_settings()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/api/settings")
    def save_settings(request: SaveSettingsRequest) -> Dict[str, str]:
        """
        保存应用设置（支持部分更新）

        只需要提供要更新的字段，未提供的字段保持不变。
        """
        try:
            # 过滤掉 None 值，只传递需要更新的字段
            settings_update = request.model_dump(exclude_none=True)
            api.save_settings(settings_update)
            return {"status": "success", "message": "设置已保存"}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/api/settings/first-run")
    def is_first_run_check() -> Dict[str, bool]:
        """检查是否首次运行"""
        try:
            is_first_run = api.is_first_run_check()
            return {"is_first_run": is_first_run}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ========================================================================
    # Aria2 接口
    # ========================================================================

    @router.get("/api/aria2/config")
    def get_aria2_config() -> Dict[str, Any]:
        """
        获取 Aria2 配置信息

        返回 Aria2 RPC 服务的连接配置。
        """
        try:
            return api.get_aria2_config()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/api/aria2/check")
    def check_aria2_connection() -> Dict[str, bool]:
        """
        检查 Aria2 连接状态

        快速检查 Aria2 端口是否开放。
        """
        try:
            return api.check_aria2_connection()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/api/aria2/start")
    def start_aria2() -> Dict[str, str]:
        """
        启动 Aria2 服务

        在前端页面加载完成后启动 Aria2 服务。
        """
        try:
            api.start_aria2_after_loaded()
            return {"status": "success", "message": "Aria2 服务启动中"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/api/aria2/config-path")
    def get_aria2_config_path(task_id: Optional[str] = None) -> Dict[str, str]:
        """
        获取已完成任务的 aria2 配置文件路径

        - task_id: 任务ID（可选，不提供则使用最新的任务）
        """
        try:
            config_path = api.get_aria2_config_path(task_id)
            return {"config_path": config_path}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ========================================================================
    # 文件操作接口
    # ========================================================================

    @router.post("/api/file/select-folder")
    def select_folder() -> Dict[str, str]:
        """
        选择文件夹

        打开系统文件夹选择对话框（仅 PyWebView 模式支持）。
        HTTP 模式下返回默认下载路径。
        """
        try:
            folder_path = api.select_folder()
            return {"folder_path": folder_path}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/api/file/open-folder")
    def open_folder(request: OpenFolderRequest) -> Dict[str, Any]:
        """
        打开文件夹

        在系统文件管理器中打开指定的文件夹。
        """
        try:
            success = api.open_folder(request.folder_path)
            return {"success": success}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/api/file/read-config")
    def read_config_file(request: ReadConfigFileRequest) -> Dict[str, str]:
        """
        读取配置文件内容

        - file_path: 配置文件路径
        """
        try:
            content = api.read_config_file(request.file_path)
            return {"content": content}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/api/file/check-exists")
    def check_file_exists(request: CheckFileExistsRequest) -> Dict[str, bool]:
        """
        检查文件是否存在

        - file_path: 文件路径
        """
        try:
            exists = api.check_file_exists(request.file_path)
            return {"exists": exists}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ========================================================================
    # 系统工具接口
    # ========================================================================

    @router.post("/api/system/open-url")
    def open_url(request: OpenUrlRequest) -> Dict[str, str]:
        """
        打开外部链接

        使用系统默认浏览器打开指定的 URL。
        """
        try:
            api.open_url(request.url)
            return {"status": "success", "message": "URL已打开"}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/api/system/clipboard")
    def get_clipboard_text() -> Dict[str, str]:
        """
        获取系统剪贴板内容

        返回剪贴板中的文本内容。
        """
        try:
            text = api.get_clipboard_text()
            return {"text": text}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# 注册所有 API 路由
api_router = APIRouter()
register_api_routes(api_router, api_instance)
app.include_router(api_router)


# ============================================================================
# 基础路由
# ============================================================================

@app.get("/api")
def read_root():
    """根路径，返回 API 信息"""
    return {
        "name": "Douyin Collector API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/events")
async def events_stream():
    """
    SSE 端点，向前端推送 JavaScript 代码

    用于在 HTTP 模式下模拟 PyWebView 的 evaluate_js 功能。
    前端通过监听此端点接收后端发送的 JS 代码并执行。
    """
    return StreamingResponse(
        sse_emitter.create_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ============================================================================
# 日志接口 (注意: HTTP 模式下需要使用 WebSocket 或轮询)
# ============================================================================

@app.get("/api/logs/subscription")
def subscribe_to_logs_info() -> Dict[str, str]:
    """
    订阅日志信息（说明接口）

    注意：在 HTTP 模式下，无法使用回调函数订阅日志。
    推荐方案：
    1. 使用 WebSocket 进行实时日志推送
    2. 使用轮询方式定期获取日志
    3. 直接查看日志文件：{config_dir}/app.log
    """
    return {
        "message": "HTTP 模式不支持回调订阅，请使用 WebSocket 或查看日志文件",
        "log_file": f"{api_instance.config_dir}/app.log"
    }


# ============================================================================
# 静态文件挂载
# ============================================================================

# 计算 frontend/dist 路径
_frontend_dist_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")

# 检查 dist 目录是否存在
if os.path.exists(_frontend_dist_dir):
    # 挂载静态文件到根路径
    # 注意：必须在 API 路由之后挂载，否则 /api/* 会被静态文件拦截
    app.mount("/", StaticFiles(directory=_frontend_dist_dir, html=True), name="static")
    print(f"✓ 前端静态文件已挂载: {_frontend_dist_dir}")
else:
    print(f"⚠ 警告: 前端 dist 目录不存在: {_frontend_dist_dir}")
    print("  请先运行: cd frontend && npm run build")


# ============================================================================
# 主程序入口
# ============================================================================

def main():
    """主程序入口"""
    config = get_config()

    print("\n" + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📡 配置信息")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  监听地址: {config['host']}")
    print(f"  监听端口: {config['port']}")
    print(f"  开发模式: {'启用' if config['dev'] else '禁用'}")
    print(f"  日志级别: {config['log_level']}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    uvicorn.run(
        "backend.server:app",
        host=config["host"],
        port=config["port"],
        reload=config["dev"],
        log_level=config["log_level"],
    )


if __name__ == "__main__":
    main()
