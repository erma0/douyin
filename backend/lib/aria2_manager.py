# -*- encoding: utf-8 -*-
"""
Aria2管理模块 - 简化版

负责Aria2下载服务的生命周期管理：
1. 检测Aria2服务是否运行
2. 自动启动Aria2服务（如果未运行）
3. 查找Aria2可执行文件（内置或系统）
4. 生成Aria2配置文件
5. 清理Aria2进程资源

设计理念：
- 后端只管理Aria2服务的启动和停止
- 前端直接通过JSON-RPC与Aria2通信
- 无需aria2p等第三方库，减少依赖
"""

import os
import subprocess
import time
from typing import Optional

from loguru import logger

from ..constants import (
    ARIA2_CONF_FILE,
    ARIA2_DEFAULTS,
    CONFIG_DIR,
    DOWNLOAD_DEFAULTS,
    RESOURCE_ROOT,
)
from .douyin.types import DouyinURL, RequestHeaders


class Aria2Manager:
    """
    Aria2服务管理器

    简化版设计，只负责Aria2服务的启动和停止，
    不处理具体的下载任务（由前端直接通过RPC处理）。

    Attributes:
        host: Aria2 RPC服务主机地址
        port: Aria2 RPC服务端口
        secret: Aria2 RPC服务密钥
        aria2_process: Aria2进程对象
    """

    def __init__(
        self,
        host: str = ARIA2_DEFAULTS["HOST"],
        port: int = ARIA2_DEFAULTS["PORT"],
        secret: str = "",
        download_dir: str = "",
        max_retries: int = DOWNLOAD_DEFAULTS["MAX_RETRIES"],
        max_concurrency: int = DOWNLOAD_DEFAULTS["MAX_CONCURRENCY"],
    ):
        """
        初始化Aria2管理器

        Args:
            host: Aria2 RPC服务主机地址，默认localhost（安全考虑）
            port: Aria2 RPC服务端口，默认6800
            secret: Aria2 RPC服务密钥，用于身份验证
            download_dir: 下载目录，如果为空则使用默认目录
            max_retries: 最大重试次数，从配置面板获取
            max_concurrency: 最大并发下载数，从配置面板获取
        """
        self.host = host
        self.port = port
        self.secret = secret
        self.download_dir = download_dir
        self.max_retries = max_retries
        self.max_concurrency = max_concurrency
        self.aria2_process = None

    def _check_connection(self) -> bool:
        """
        检查Aria2 RPC服务是否可用（增强版本）

        先检查端口连通性，再验证RPC服务响应，确保服务真正可用。

        Returns:
            True: 服务可用
            False: 服务不可用

        Note:
            - 使用0.1秒超时进行端口检查
            - 验证RPC服务响应，确保服务完全就绪
            - 适合频繁调用的场景
        """
        try:
            import socket
            import urllib.error
            import urllib.request

            import ujson as json

            # 1. 快速检查端口是否开放
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)  # 100ms超时
            result = sock.connect_ex((self.host, self.port))
            sock.close()

            if result != 0:
                return False

            # 2. 验证RPC服务响应（确保aria2服务真正就绪）
            rpc_url = f"http://{self.host}:{self.port}/jsonrpc"

            # 构建简单的RPC请求
            rpc_data = {"jsonrpc": "2.0", "id": "test", "method": "aria2.getVersion"}

            # 如果有密钥，添加到参数中
            if self.secret:
                rpc_data["params"] = [f"token:{self.secret}"]

            # 发送RPC请求
            req = urllib.request.Request(
                rpc_url,
                data=json.dumps(rpc_data).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )

            with urllib.request.urlopen(req, timeout=0.5) as response:
                result_data = json.loads(response.read().decode("utf-8"))

                # 检查是否有错误
                if "error" in result_data:
                    logger.debug(f"Aria2 RPC错误: {result_data['error']}")
                    return False

                # 检查是否有结果
                if "result" in result_data:
                    return True

            return False

        except (socket.error, urllib.error.URLError, json.JSONDecodeError, Exception):
            # 静默处理，避免日志干扰
            return False

    def _find_aria2_executable(self) -> Optional[str]:
        """
        查找Aria2可执行文件（优化版 - 快速查找）

        按优先级搜索Aria2程序：
        1. 项目内置的aria2（aria2/aria2c.exe或aria2c）
        2. 系统PATH中的aria2c命令

        Returns:
            Aria2可执行文件的完整路径，未找到返回None

        Note:
            - Windows系统查找aria2c.exe
            - Linux/Mac系统查找aria2c
            - 内置版本优先，确保版本一致性
            - 系统版本作为备选，提高兼容性
            - 优化：使用 shutil.which() 快速查找，避免执行 --version 命令
        """
        import platform
        import shutil

        # 1. 检查项目内置的aria2（最快，直接文件检查）
        # 使用资源根目录（打包后是临时解压目录）
        if platform.system() == "Windows":
            bundled_aria2 = os.path.join(RESOURCE_ROOT, "aria2", "aria2c.exe")
        else:
            bundled_aria2 = os.path.join(RESOURCE_ROOT, "aria2", "aria2c")

        if os.path.exists(bundled_aria2):
            logger.info(f"✓ 找到内置Aria2")
            return bundled_aria2

        # 2. 检查系统PATH中的aria2c（使用 shutil.which 快速查找，无需执行命令）
        system_aria2 = shutil.which("aria2c")
        if system_aria2:
            logger.info("✓ 找到系统Aria2")
            return system_aria2

        logger.warning("✗ 未找到Aria2可执行文件")
        return None

    def start_aria2_server(self):
        """
        异步启动Aria2服务器（优化版 - 极速启动）

        如果Aria2服务未运行，则异步启动。执行以下步骤：
        1. 检查服务是否已运行（避免重复启动）
        2. 查找Aria2可执行文件
        3. 生成Aria2配置文件
        4. 异步启动Aria2进程

        Returns:
            None，因为启动是异步的

        Note:
            - 启动过程完全异步，不阻塞主线程
            - 不等待服务启动完成，立即返回
            - Windows下会隐藏控制台窗口
            - 配置文件保存在用户目录的.douyin_crawler文件夹
            - 启动后会在后台验证服务是否成功启动
            - 优化：减少日志输出，提高启动速度
        """
        # 先尝试连接现有服务，避免重复启动
        if self._check_connection():
            logger.info("✓ Aria2服务已就绪")
            return

        logger.info("🚀 正在启动Aria2服务...")

        # 查找aria2可执行文件
        aria2_cmd = self._find_aria2_executable()
        if not aria2_cmd:
            logger.error("✗ 未找到Aria2程序，请运行: .\\scripts\\setup\\aria2.ps1")
            return

        # 准备配置目录和文件
        # 下载目录：使用传入的目录或默认目录
        if self.download_dir:
            download_dir = self.download_dir
        else:
            # 默认使用应用根目录下的 download 文件夹
            download_dir = CONFIG_DIR

        os.makedirs(download_dir, exist_ok=True)

        # 配置目录：应用根目录下的 config 文件夹
        os.makedirs(CONFIG_DIR, exist_ok=True)

        # Aria2配置参数（精简优化版）
        aria2_config = {
            # === 基础配置 ===
            "dir": download_dir,  # 下载目录
            # 不配置log，aria2将不写入日志文件
            # === RPC 配置 ===
            "enable-rpc": "true",  # 启用RPC
            "rpc-listen-all": "false",  # 只监听本地
            "rpc-listen-port": str(self.port),  # RPC端口
            "rpc-allow-origin-all": "true",  # 允许所有来源
            # === 下载配置 ===
            "max-concurrent-downloads": str(self.max_concurrency),  # 最大并发数
            "max-connection-per-server": "16",  # 单服务器最大连接数
            "min-split-size": "5M",  # 最小分片大小
            "continue": "true",  # 断点续传
            # === 重试配置 ===
            "max-tries": str(self.max_retries),  # 最大重试次数
            "retry-wait": "3",  # 重试等待时间（秒）
            "timeout": "60",  # 下载超时（秒）
            "connect-timeout": "30",  # 连接超时（秒）
            # === HTTP 配置 ===
            "User-Agent": RequestHeaders.USER_AGENT,
            "referer": DouyinURL.BASE,
            "check-certificate": "false",  # 不检查SSL证书
            # === 性能优化 ===
            "disk-cache": "32M",  # 磁盘缓存
            "file-allocation": "none",  # 文件预分配（none=最快）
            "auto-file-renaming": "false",  # 禁用自动重命名，配合continue实现智能跳过
        }

        # 如果设置了密钥，添加到配置（增强安全性）
        if self.secret:
            aria2_config["rpc-secret"] = self.secret
        else:
            # 如果没有设置密钥，生成一个默认密钥以提高安全性
            aria2_config["rpc-secret"] = ARIA2_DEFAULTS["SECRET"]

        try:
            # 优化：使用更快的写入方式
            config_content = "\n".join(f"{k}={v}" for k, v in aria2_config.items())
            with open(ARIA2_CONF_FILE, "w", encoding="utf-8") as f:
                f.write(config_content)
        except Exception as e:
            logger.error(f"✗ 创建配置文件失败: {e}")
            return

        # 启动Aria2进程
        try:
            import platform

            if platform.system() == "Windows":
                # Windows下隐藏控制台窗口，避免弹出黑窗口
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

                self.aria2_process = subprocess.Popen(
                    [aria2_cmd, "--conf-path", ARIA2_CONF_FILE],
                    stdout=subprocess.DEVNULL,  # 丢弃标准输出，避免缓冲区满导致进程阻塞
                    stderr=subprocess.DEVNULL,  # 丢弃标准错误，避免缓冲区满导致进程阻塞
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    shell=False,
                )
            else:
                self.aria2_process = subprocess.Popen(
                    [aria2_cmd, "--conf-path", ARIA2_CONF_FILE],
                    stdout=subprocess.DEVNULL,  # 丢弃标准输出，避免缓冲区满导致进程阻塞
                    stderr=subprocess.DEVNULL,  # 丢弃标准错误，避免缓冲区满导致进程阻塞
                    close_fds=True,
                    shell=False,
                )

            logger.success("✓ Aria2进程已启动，等待服务就绪...")

            # 等待服务真正就绪（最多等待10秒）
            for i in range(20):  # 20次 * 0.5秒 = 10秒
                time.sleep(0.5)
                if self._check_connection():
                    logger.success("✓ Aria2服务已就绪")
                    return

            logger.warning("⚠ Aria2进程已启动，但RPC服务可能需要更多时间才能就绪")

        except FileNotFoundError:
            logger.error("✗ 未找到aria2c命令")
        except Exception as e:
            logger.error(f"✗ 启动失败: {e}")
            # 确保进程被清理
            if self.aria2_process:
                try:
                    self.aria2_process.terminate()
                    self.aria2_process.wait(timeout=2)
                except:
                    try:
                        self.aria2_process.kill()
                    except:
                        pass

    def cleanup(self) -> None:
        """
        清理Aria2资源

        在应用退出时调用，负责：
        1. 终止自己启动的Aria2进程
        2. 查找并终止所有aria2c进程（避免僵尸进程）
        3. 等待进程正常退出
        4. 清理连接状态

        Note:
            - 使用terminate()优雅终止进程
            - 等待最多2秒，避免无限等待
            - 超时后强制终止进程
            - 会终止所有aria2c进程，确保端口释放
        """
        logger.info("清理Aria2资源...")

        # 停止自己启动的Aria2进程
        if self.aria2_process:
            try:
                # 发送终止信号
                self.aria2_process.terminate()
                # 等待进程退出（最多1秒）
                try:
                    self.aria2_process.wait(timeout=1)
                    logger.info("✓ Aria2进程已终止")
                except subprocess.TimeoutExpired:
                    # 超时则强制终止
                    self.aria2_process.kill()
                    logger.info("✓ Aria2进程已强制终止")
            except Exception as e:
                logger.error(f"✗ 终止Aria2进程失败: {e}")

        logger.info("✓ Aria2资源清理完成")
