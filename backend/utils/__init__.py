# -*- encoding: utf-8 -*-
"""
基础工具模块

提供与应用运行环境相关的基础工具，不依赖业务逻辑。

模块：
    - paths.py: 路径管理
        处理开发环境和打包环境的路径差异
        提供 APP_ROOT（应用根目录）和 RESOURCE_ROOT（资源根目录）
    
    - text.py: 文本处理工具
        提供字符串清理、文件名安全化、URL提取等功能
    
    - execjs_fix.py: execjs库补丁
        修复Windows环境下execjs的兼容性问题

使用示例：
    from backend.utils.paths import get_app_root, get_resource_root
    from backend.utils.text import sanitize_filename
    
    app_root = get_app_root()
    safe_name = sanitize_filename("文件名:包含/特殊*字符")
"""

from .paths import get_app_root, get_resource_root

__all__ = ["get_app_root", "get_resource_root"]
