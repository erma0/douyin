import os
import sys

import webview
from loguru import logger

from backend.api import API
from backend.constants import PROJECT_ROOT, RESOURCE_ROOT

# 判断是否为打包环境
IS_PACKAGED = getattr(sys, "frozen", False)

# 配置日志：打包后禁用控制台输出
logger.remove()  # 移除默认handler

if not IS_PACKAGED:
    # 开发环境：保留控制台输出
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO",
    )
# 打包环境：不添加handler，避免控制台编码问题
# 日志会在API初始化后自动配置（文件+前端面板）


def get_entrypoint():
    """获取前端入口文件路径（从资源目录读取）"""
    index_path = os.path.join(RESOURCE_ROOT, "frontend", "dist", "index.html")

    if os.path.exists(index_path):
        logger.info(f"🔄 加载前端: {index_path}")
        return index_path
    else:
        logger.error(f"❌ 未找到前端文件: {index_path}")
        logger.error("💡 请先构建前端: cd frontend && pnpm build")
        sys.exit(1)


def get_icon_path():
    """获取应用图标路径（从资源目录读取）"""

    # 优先使用构建后的图标
    dist_icon = os.path.join(RESOURCE_ROOT, "frontend", "dist", "favicon.ico")
    if os.path.exists(dist_icon):
        return dist_icon

    # 备用：开发环境的图标
    public_icon = os.path.join(RESOURCE_ROOT, "frontend", "public", "favicon.ico")
    if os.path.exists(public_icon):
        return public_icon

    return None


if __name__ == "__main__":
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("🎉 DouyinCrawler客户端启动中...")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # 调试信息：打印关键路径
    logger.info(f"📍 运行环境信息:")
    # logger.info(f"  - sys.frozen: {getattr(sys, 'frozen', False)}")
    # logger.info(f"  - sys.executable: {sys.executable}")
    # logger.info(f"  - sys.argv[0]: {sys.argv[0] if sys.argv else 'N/A'}")
    logger.info(f"  - 应用根目录: {PROJECT_ROOT}")
    logger.info(f"  - 资源根目录: {RESOURCE_ROOT}")

    try:
        entry = get_entrypoint()
        api = API()

        # 加载窗口配置
        window_width = api.settings.get("windowWidth", 1200)
        window_height = api.settings.get("windowHeight", 800)

        # 计算居中位置
        screen_width = webview.screens[0].width
        screen_height = webview.screens[0].height
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # 创建窗口
        window = webview.create_window(
            title="DouyinCrawler",
            url=entry,
            js_api=api,
            width=window_width,
            height=window_height,
            x=x,
            y=y,
            resizable=True,
            min_size=(900, 800),
            text_select=False,
            # 允许跨域访问，解决视频预览问题
            easy_drag=False,
        )

        api.set_webview_window(window)

        # 页面加载完成回调
        def on_loaded():
            logger.info("✓ 前端页面加载完成")
            # 注意：不在这里启动 Aria2
            # Aria2 将在前端 API 就绪后由前端主动调用启动

        window.events.loaded += on_loaded

        # 窗口关闭事件
        def on_closing():
            result = window.create_confirmation_dialog(
                title="确认退出", message="确定要退出吗？"
            )

            if result:
                logger.info("🔄 正在关闭应用...")

                # 清理后端资源
                api.cleanup()

                # 给足够时间让所有资源释放
                # 包括：日志文件、aria2进程、WebView缓存等
                import time

                time.sleep(1.0)

                return True
            return False

        window.events.closing += on_closing

        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info(f"✓ 窗口已创建: {window_width}x{window_height}")
        logger.info("✓ 应用启动成功")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 启动应用
        # 注意：生产环境不要使用 debug=True，会导致性能问题和卡顿
        # http_server=True 允许加载外部资源（解决视频跨域问题）
        # storage_path 使用独立目录，避免与config冲突
        storage_path = os.path.join(api.config_dir, "webview_storage")
        os.makedirs(storage_path, exist_ok=True)

        webview.start(
            debug=False,
            # gui='edgechromium',
            icon=get_icon_path(),
            http_server=True,  # 启用HTTP服务器模式，允许跨域访问外部资源
            storage_path=storage_path,
        )

        # webview.start()返回后，窗口已关闭
        # 再次确保所有资源已释放
        logger.info("👋 应用已正常退出")

        # 最终清理：确保所有文件句柄都已关闭
        import time

        time.sleep(0.5)
    except Exception as e:
        logger.error(f"💥 应用崩溃: {e}", exc_info=True)
        sys.exit(1)
