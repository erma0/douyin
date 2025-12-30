# -*- encoding: utf-8 -*-
"""

路径工具模块

提供应用根目录和资源根目录的获取功能
"""


import os
import sys


def get_app_root():
    """

    获取应用根目录（用于配置文件、下载目录等用户数据）


    Returns:

        str: 应用根目录路径


    规则:

        - 如果 sys.argv[0] 是 .exe 文件，返回其所在目录

        - 否则返回项目根目录（开发环境）
    """

    # 获取启动脚本/可执行文件的路径

    if sys.argv and sys.argv[0]:

        entry_path = os.path.abspath(sys.argv[0])

        # 如果是 .exe 文件，返回其所在目录

        if entry_path.lower().endswith(".exe"):

            return os.path.dirname(entry_path)

    # 开发环境：返回项目根目录（backend/utils -> backend -> 项目根）

    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_resource_root():
    """

    获取资源根目录（用于读取打包的静态资源）


    Returns:

        str: 资源根目录路径


    规则:

        - Nuitka/PyInstaller 打包: 使用 __compiled__.containing_dir 或临时解压目录

        - 开发环境: 项目根目录
    """

    # 尝试获取 Nuitka 的临时解压目录

    try:

        import __compiled__

        if hasattr(__compiled__, "containing_dir"):

            return __compiled__.containing_dir

    except ImportError:
        pass

    # 尝试获取 PyInstaller 的临时解压目录

    if hasattr(sys, "_MEIPASS"):

        return sys._MEIPASS

    # 开发环境：返回项目根目录（backend/utils -> backend -> 项目根）

    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
