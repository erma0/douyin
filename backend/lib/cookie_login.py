# -*- encoding: utf-8 -*-
"""
Cookie 登录获取模块

通过 pywebview 打开抖音登录页面，拦截请求获取 Cookie。
仅在 GUI 模式下可用。
"""

import threading
from dataclasses import dataclass
from typing import Optional

import webview
from loguru import logger

# 目标 API 路径（登录后会请求这些接口）
TARGET_API_PATHS = [
    "/aweme/v1/web/search/item",
]

# 登录页面 URL
LOGIN_URL = "https://www.douyin.com/search/deepseek?type=video"


@dataclass
class CookieResult:
    """Cookie 获取结果"""

    success: bool
    cookie: str = ""
    user_agent: str = ""
    error: str = ""


def get_cookie_by_login() -> CookieResult:
    """
    通过登录获取 Cookie

    在主 GUI 事件循环中创建新窗口，共享 storage_path。

    Returns:
        CookieResult: 获取结果
    """
    logger.info("🔐 正在打开抖音登录窗口...")

    captured = False
    result: Optional[CookieResult] = None
    result_event = threading.Event()
    window: Optional[webview.Window] = None

    def on_request_sent(request) -> None:
        nonlocal captured, result

        if captured:
            return

        # 检查是否为目标 API
        url = request.url
        is_target = any(path in url for path in TARGET_API_PATHS)

        if not is_target:
            return

        logger.info(f"🎯 捕获到目标请求: {url}")

        # 提取 Cookie 和 User-Agent
        headers = request.headers or {}
        cookie = headers.get("Cookie", "")
        user_agent = headers.get("User-Agent", "")

        if not cookie:
            logger.debug("请求中未包含 Cookie")
            return

        # 验证 Cookie 是否包含必要字段
        cookie_lower = cookie.lower()
        if "sessionid" not in cookie_lower and "ttwid" not in cookie_lower:
            logger.debug("Cookie 缺少必要字段")
            return

        # 标记已捕获
        captured = True
        logger.success("✓ Cookie 获取成功")

        result = CookieResult(
            success=True,
            cookie=cookie,
            user_agent=user_agent,
        )

        # 关闭窗口
        try:
            window.destroy()
        except Exception as e:
            logger.warning(f"关闭窗口时出错: {e}")

    def on_closing() -> bool:
        nonlocal result

        if not captured:
            logger.info("用户关闭了登录窗口")
            result = CookieResult(
                success=False,
                error="用户取消登录",
            )

        # 设置事件，通知等待线程
        if result is None:
            result = CookieResult(success=False, error="未知错误")
        result_event.set()

        return True

    def on_loaded() -> None:
        logger.info("📄 登录页面已加载，请完成登录...")

    # 在已有的 GUI 事件循环中创建新窗口
    window = webview.create_window(
        title="登录抖音获取Cookie",
        url=LOGIN_URL,
        width=900,
        height=700,
        resizable=True,
        on_top=True,
    )

    # 绑定事件
    window.events.request_sent += on_request_sent
    window.events.closing += on_closing
    window.events.loaded += on_loaded

    # 等待窗口关闭
    result_event.wait()

    return result
