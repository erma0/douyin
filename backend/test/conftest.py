# -*- coding: utf-8 -*-
"""测试配置文件，提供共享的fixture"""

import json
import os

import pytest
from backend.constants import SETTINGS_FILE


@pytest.fixture(scope="session")
def settings_cookie():
    """从文件读取Cookie"""
    # 使用统一的路径管理
    
    cookie = ""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
            cookie = settings.get("cookie", "")
    return cookie
