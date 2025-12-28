# -*- coding: utf-8 -*-
"""测试配置文件，提供共享的fixture"""

import json
import os

import pytest


@pytest.fixture(scope="session")
def settings_cookie():
    """从文件读取Cookie"""
    # 直接读取settings.json文件 - 修正路径：从项目根目录查找config
    config_dir = os.path.join(
        os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))), 'config'
    )
    settings_path = os.path.join(config_dir, "settings.json")
    cookie = ""
    if os.path.exists(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
            cookie = settings.get("cookie", "")
    return cookie
