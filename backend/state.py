# -*- encoding: utf-8 -*-
"""
应用运行时状态管理模块

管理任务状态、Aria2 连接等运行时资源。
"""

from typing import Any, Dict, List, Optional

from loguru import logger

from .constants import ARIA2_DEFAULTS, DOWNLOAD_DEFAULTS, DOWNLOAD_DIR
from .lib.aria2_manager import Aria2Manager
from .settings import settings


class AppState:
    """
    应用运行时状态管理

    负责管理：
    - 任务状态和结果
    - Aria2 管理器
    - 运行时资源清理
    """

    def __init__(self) -> None:
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("🚀 应用状态初始化中...")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 任务状态
        self.task_status: Dict[str, Dict[str, Any]] = {}
        self.task_results: Dict[str, List[Dict[str, Any]]] = {}
        self.aria2_config_paths: Dict[str, str] = {}

        # Aria2 管理器
        self.aria2_manager: Optional[Aria2Manager] = self._init_aria2()

        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.success("✓ 应用状态初始化完成")
        logger.info(f"  - 下载目录: {settings.get('downloadPath')}")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def _init_aria2(self) -> Optional[Aria2Manager]:
        """初始化 Aria2 管理器"""
        try:
            return Aria2Manager(
                host=settings.get("aria2Host", ARIA2_DEFAULTS["HOST"]),
                port=settings.get("aria2Port", ARIA2_DEFAULTS["PORT"]),
                secret=settings.get("aria2Secret", ARIA2_DEFAULTS["SECRET"]),
                download_dir=settings.get("downloadPath", DOWNLOAD_DIR),
                max_retries=settings.get(
                    "maxRetries", DOWNLOAD_DEFAULTS["MAX_RETRIES"]
                ),
                max_concurrency=settings.get(
                    "maxConcurrency", DOWNLOAD_DEFAULTS["MAX_CONCURRENCY"]
                ),
            )
        except Exception as e:
            logger.error(f"初始化 Aria2 管理器失败: {e}")
            return None

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        aria2_ok = False
        if self.aria2_manager:
            try:
                aria2_ok = self.aria2_manager._check_connection()
            except Exception:
                pass

        return {
            "ready": True,
            "aria2": aria2_ok,
            # "config": len(settings.get("cookie", "")) > 0,
            "error": None,
        }

    def cleanup(self) -> None:
        """清理资源"""
        logger.info("🧹 开始清理资源...")
        if self.aria2_manager:
            try:
                self.aria2_manager.cleanup()
                logger.info("✓ Aria2资源已清理")
            except Exception as e:
                logger.error(f"✗ 清理Aria2资源失败: {e}")
        logger.info("✓ 资源清理完成")


# 全局实例，直接导入使用
state = AppState()
