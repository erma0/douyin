import os
import subprocess

from loguru import logger


def download(path, aria2_conf):
    """
    命令行调用aria2c下载
    """
    if os.path.exists(aria2_conf):
        logger.info("开始下载")

        # 查找aria2c可执行文件
        import platform
        import shutil

        # 优先查找系统中的 aria2c
        aria2_path = shutil.which("aria2c")

        if not aria2_path:
            # 如果系统中没有，使用项目内置的
            try:
                from ..constants import RESOURCE_ROOT
            except ImportError:
                # 命令行模式下的导入
                import sys

                sys.path.insert(
                    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
                from constants import RESOURCE_ROOT

            if platform.system() == "Windows":
                aria2_path = os.path.join(RESOURCE_ROOT, "aria2", "aria2c.exe")
            else:
                aria2_path = os.path.join(RESOURCE_ROOT, "aria2", "aria2c")

            if not os.path.exists(aria2_path):
                logger.error(f"未找到 aria2c 可执行文件: {aria2_path}")
                logger.error("请运行: .\\scripts\\setup\\aria2.ps1 安装 aria2")
                return

        logger.info(f"使用 aria2c: {aria2_path}")

        command = [
            aria2_path,
            "-c",
            "--console-log-level",
            "warn",
            "-d",
            path,
            "-i",
            aria2_conf,
        ]
        subprocess.run(command)
    else:
        logger.error(f"没有发现可下载的配置文件: {aria2_conf}")
