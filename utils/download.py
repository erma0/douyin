import os
import subprocess

from loguru import logger


def download(path, aria2_conf):
    """
    命令行调用aria2c下载
    """
    if os.path.exists(aria2_conf):
        logger.info('开始下载')
        command = [
            os.path.join(os.path.dirname(__file__), '../aria2c'),
            '-c', '--console-log-level', 'warn', '-d', path, '-i', aria2_conf
        ]
        subprocess.run(command)
    else:
        logger.error('没有发现可下载的配置文件')
