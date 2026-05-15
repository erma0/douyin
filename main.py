"""
DouyinCrawler GUI 启动器

使用 PyWebView 创建桌面窗口，加载 FastAPI 后端服务。
启动流程：
1. 创建窗口（url="about:blank"）
2. 使用 webview.start(func) 启动后端服务
3. 等待服务就绪后加载实际页面
"""

import os
import socket
import sys
import threading
import time

import webview
from loguru import logger

# 移除默认日志配置
logger.remove()

from backend.constants import (
    PROJECT_ROOT,
    RESOURCE_ROOT,
    SERVER_DEFAULTS,
    WEBVIEW_STORAGE_DIR,
    WINDOW_MIN_SIZE,
)
from backend.settings import settings
from backend.state import state

# 判断是否为打包环境
IS_PACKAGED = getattr(sys, "frozen", False)
if not IS_PACKAGED:
    # 开发环境：保留控制台输出
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO",
    )
# 打包环境：不保存日志文件


# 服务配置（从常量读取）
SERVER_HOST = SERVER_DEFAULTS["HOST"]
SERVER_PORT = SERVER_DEFAULTS["PORT"]


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except OSError:
            return True


def wait_for_server_ready(host: str, port: int, timeout: int = 10) -> bool:
    """等待服务器就绪"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((host, port))
                return True
        except (socket.error, socket.timeout):
            time.sleep(0.2)
    return False


def get_icon_path():
    """获取应用图标路径"""
    dist_icon = os.path.join(RESOURCE_ROOT, "frontend", "dist", "favicon.ico")
    if os.path.exists(dist_icon):
        return dist_icon
    public_icon = os.path.join(RESOURCE_ROOT, "frontend", "public", "favicon.ico")
    if os.path.exists(public_icon):
        return public_icon
    return None


def start_backend(window: webview.Window):
    """
    启动后端服务（在 webview.start 的单独线程中执行）

    Args:
        window: PyWebView 窗口实例
    """
    from backend.server import run_server

    logger.info("🚀 正在启动后端服务...")

    # 启动 FastAPI 服务（守护线程）
    server_thread = threading.Thread(
        target=run_server,
        kwargs={"host": SERVER_HOST, "port": SERVER_PORT},
        daemon=True,
    )
    server_thread.start()

    # 等待服务就绪
    if wait_for_server_ready(SERVER_HOST, SERVER_PORT, timeout=10):
        logger.info(f"✓ 后端服务已就绪: http://{SERVER_HOST}:{SERVER_PORT}")
        window.load_url(f"http://{SERVER_HOST}:{SERVER_PORT}")
    else:
        logger.error("❌ 后端服务启动超时")
        window.load_html(
            """
            <html>
            <head><meta charset="utf-8"><title>错误</title></head>
            <body style="font-family: sans-serif; padding: 40px; text-align: center;">
                <h1>😢 服务启动失败</h1>
                <p>后端服务未能在规定时间内启动，请检查日志或重启应用。</p>
            </body>
            </html>
        """
        )


def on_closing(window: webview.Window) -> bool:
    """窗口关闭事件处理"""
    result = window.create_confirmation_dialog(
        title="确认退出", message="确定要退出吗？"
    )

    if result:
        logger.info("🔄 正在关闭应用...")

        def _cleanup():
            try:
                state.cleanup()
            except Exception as e:
                logger.warning(f"清理资源时出错: {e}")

        threading.Thread(target=_cleanup, daemon=True).start()

        return True

    return False


def main():
    """主程序入口"""
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("🎉 DouyinCrawler 客户端启动中...")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info(f"📍 运行环境信息:")
    logger.info(f"  - 应用根目录: {PROJECT_ROOT}")
    logger.info(f"  - 资源根目录: {RESOURCE_ROOT}")

    # 检查端口是否被占用
    if is_port_in_use(SERVER_PORT, SERVER_HOST):
        logger.error(f"❌ 端口 {SERVER_PORT} 已被占用")
        logger.error("💡 请关闭占用该端口的程序后重试")

        # 显示错误窗口
        window = webview.create_window(
            title="DouyinCrawler - 错误",
            html=f"""
                <html>
                <head><meta charset="utf-8"><title>错误</title></head>
                <body style="font-family: sans-serif; padding: 40px; text-align: center;">
                    <h1>😢 端口被占用</h1>
                    <p>端口 {SERVER_PORT} 已被其他程序占用。</p>
                    <p>请关闭占用该端口的程序后重试。</p>
                </body>
                </html>
            """,
            width=500,
            height=300,
        )
        webview.start()
        return

    # 加载窗口配置
    window_width = settings.get("windowWidth")
    window_height = settings.get("windowHeight")

    # 计算居中位置
    try:
        screen_width = webview.screens[0].width
        screen_height = webview.screens[0].height
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
    except Exception:
        x, y = None, None

    # 创建窗口（初始加载空白页）
    window = webview.create_window(
        title="DouyinCrawler",
        url="about:blank",
        width=window_width,
        height=window_height,
        x=x,
        y=y,
        resizable=True,
        min_size=WINDOW_MIN_SIZE,
        text_select=False,
        easy_drag=False,
    )

    # 注册关闭事件
    window.events.closing += lambda: on_closing(window)

    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info(f"✓ 窗口已创建: {window_width}x{window_height}")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # 启动 GUI（start_backend 在单独线程中执行）
    webview.start(
        func=start_backend,
        args=(window,),
        icon=get_icon_path(),
        storage_path=WEBVIEW_STORAGE_DIR,
        private_mode=False,
    )

    logger.info("👋 应用已正常退出")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"💥 应用崩溃: {e}", exc_info=True)
        sys.exit(1)
