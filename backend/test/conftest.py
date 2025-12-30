# -*- coding: utf-8 -*-
"""测试配置文件，提供共享的fixture"""

import json
import os

import pytest
from backend.constants import PROJECT_ROOT, PATHS


@pytest.fixture(scope="session")
def settings_cookie():
    """从文件读取Cookie"""
    # 使用统一的路径管理
    config_dir = os.path.join(PROJECT_ROOT, PATHS["CONFIG_DIR"])
    settings_path = os.path.join(config_dir, PATHS["SETTINGS_FILE"])
    
    cookie = ""
    if os.path.exists(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
            cookie = settings.get("cookie", "")
    return cookie
