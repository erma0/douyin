# -*- encoding: utf-8 -*-
"""
应用常量配置
统一管理项目中使用的常量，避免重复定义
"""

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
    "COOKIE_FILE": "cookie.txt",
    "ARIA2_CONF": "aria2.conf",
}
