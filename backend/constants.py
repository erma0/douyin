# -*- encoding: utf-8 -*-
"""
应用常量配置
统一管理项目中使用的常量，避免重复定义
"""

import os

# 兼容独立脚本运行和模块导入两种方式
try:
    from .utils.paths import get_app_root, get_resource_root
except ImportError:
    from utils.paths import get_app_root, get_resource_root

# 项目根目录（应用目录）
PROJECT_ROOT = get_app_root()
# 资源根目录（包含前端静态文件）
RESOURCE_ROOT = get_resource_root()

# 完整路径
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
DOWNLOAD_DIR = os.path.join(PROJECT_ROOT, "download")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")
ARIA2_CONF_FILE = os.path.join(CONFIG_DIR, "aria2.conf")
WEBVIEW_STORAGE_DIR = os.path.join(CONFIG_DIR, "webview_storage")

# Aria2 默认配置
ARIA2_DEFAULTS = {
    "HOST": "localhost",
    "PORT": 6800,
    "SECRET": "douyin_crawler_default_secret",
}

# 下载配置默认值
DOWNLOAD_DEFAULTS = {
    "MAX_RETRIES": 3,
    "MAX_CONCURRENCY": 5,
}

# 默认设置（用于首次运行创建配置文件）
DEFAULT_SETTINGS = {
    "cookie": "",
    "downloadPath": DOWNLOAD_DIR,
    "maxRetries": DOWNLOAD_DEFAULTS["MAX_RETRIES"],
    "maxConcurrency": DOWNLOAD_DEFAULTS["MAX_CONCURRENCY"],
    "windowWidth": 1200,
    "windowHeight": 800,
    "enableIncrementalFetch": True,
    "aria2Host": ARIA2_DEFAULTS["HOST"],
    "aria2Port": ARIA2_DEFAULTS["PORT"],
    "aria2Secret": ARIA2_DEFAULTS["SECRET"],
}

# 窗口最小尺寸
WINDOW_MIN_SIZE = (900, 800)

# 服务器默认配置
SERVER_DEFAULTS = {
    "HOST": "127.0.0.1",
    "PORT": 8000,
    "DEV": False,
    "LOG_LEVEL": "info",
}
