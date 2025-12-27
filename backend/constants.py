# -*- encoding: utf-8 -*-
"""
应用常量配置
统一管理项目中使用的常量，避免重复定义
"""

import os
import sys

# 获取项目根目录
if getattr(sys, 'frozen', False):
    # 打包后：使用exe所在目录
    PROJECT_ROOT = os.path.dirname(sys.executable)
else:
    # 开发环境：使用项目根目录
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

# 路径相关常量
PATHS = {
    "CONFIG_DIR": "config",
    "DOWNLOAD_DIR": "download",
    "SETTINGS_FILE": "settings.json",
    "ARIA2_CONF": "aria2.conf",
}

# 默认设置（用于首次运行创建配置文件）
DEFAULT_SETTINGS = {
    "cookie": "",
    "downloadPath": os.path.join(PROJECT_ROOT, PATHS["DOWNLOAD_DIR"]),
    "maxRetries": DOWNLOAD_DEFAULTS["MAX_RETRIES"],
    "maxConcurrency": DOWNLOAD_DEFAULTS["MAX_CONCURRENCY"],
    "windowWidth": 1200,
    "windowHeight": 800,
    "enableIncrementalFetch": True,
    "aria2Host": ARIA2_DEFAULTS["HOST"],
    "aria2Port": ARIA2_DEFAULTS["PORT"],
    "aria2Secret": ARIA2_DEFAULTS["SECRET"],
}
