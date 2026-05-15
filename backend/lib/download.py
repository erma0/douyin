import os
import subprocess

from loguru import logger

from ..constants import RESOURCE_ROOT


def download(path: str, aria2_conf: str) -> None:
    if os.path.exists(aria2_conf):
        logger.info("开始下载")

        from .aria2_manager import Aria2Manager
        aria2_path = Aria2Manager._find_aria2_executable()

        if not aria2_path:
            logger.error("未找到 aria2c 可执行文件")
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
        try:
            result = subprocess.run(command, timeout=3600)
            if result.returncode != 0:
                logger.error(f"aria2c 下载失败，退出码: {result.returncode}")
        except subprocess.TimeoutExpired:
            logger.error("aria2c 下载超时（1小时），已终止")
        except Exception as e:
            logger.error(f"aria2c 执行异常: {e}")
    else:
        logger.error(f"没有发现可下载的配置文件: {aria2_conf}")
