# -*- encoding: utf-8 -*-
"""
应用运行时状态管理模块

管理任务状态、Aria2 连接等运行时资源。
"""

import threading
import time
from typing import Any

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

    线程安全：所有共享状态的读写操作通过 _lock 保护
    """

    MAX_COMPLETED_TASKS = 20

    def __init__(self) -> None:
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("🚀 应用状态初始化中...")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        self._lock = threading.Lock()

        self._task_status: dict[str, dict[str, Any]] = {}
        self._task_results: dict[str, list[dict[str, Any]]] = {}
        self._aria2_config_paths: dict[str, str] = {}
        self.task_cancel_events: dict[str, threading.Event] = {}

        self.aria2_manager: Aria2Manager | None = self._init_aria2()

        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.success("✓ 应用状态初始化完成")
        logger.info(f"  - 下载目录: {settings.get('downloadPath')}")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def _init_aria2(self) -> Aria2Manager | None:
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

    def register_cancel_event(self, task_id: str) -> threading.Event:
        event = threading.Event()
        with self._lock:
            self.task_cancel_events[task_id] = event
        return event

    def request_cancel(self, task_id: str) -> bool:
        with self._lock:
            event = self.task_cancel_events.get(task_id)
        if event is None:
            return False
        event.set()
        return True

    def is_cancelled(self, task_id: str) -> bool:
        with self._lock:
            event = self.task_cancel_events.get(task_id)
        return event is not None and event.is_set()

    def cleanup_cancel_event(self, task_id: str) -> None:
        with self._lock:
            self.task_cancel_events.pop(task_id, None)

    def task_exists(self, task_id: str) -> bool:
        with self._lock:
            return task_id in self._task_status

    def get_task_status(self, task_id: str | None = None) -> list[dict[str, Any]]:
        with self._lock:
            if task_id:
                return [self._task_status[task_id]] if task_id in self._task_status else []
            return list(self._task_status.values())

    def get_task_results(self, task_id: str) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._task_results.get(task_id, []))

    def set_task_status(self, task_id: str, **kwargs) -> None:
        with self._lock:
            if task_id in self._task_status:
                self._task_status[task_id].update(kwargs)

    def add_results(self, task_id: str, items: list[dict[str, Any]]) -> int:
        with self._lock:
            self._task_results[task_id].extend(items)
            count = len(self._task_results[task_id])
            self._task_status[task_id]["result_count"] = count
            self._task_status[task_id]["updated_at"] = time.time()
        return count

    def init_task(self, task_id: str, status: dict[str, Any]) -> None:
        with self._lock:
            status["created_at"] = time.time()
            self._task_status[task_id] = status
            self._task_results[task_id] = []
            self._cleanup_old_tasks()

    def health_check(self) -> dict[str, Any]:
        aria2_ok = False
        if self.aria2_manager:
            try:
                aria2_ok = self.aria2_manager.is_connected()
            except Exception:
                pass

        return {
            "ready": True,
            "aria2": aria2_ok,
            "config": len(settings.get("cookie", "").strip()) > 0,
            "error": None,
        }

    def get_aria2_config_path_for_task(self, task_id: str | None = None) -> str | None:
        with self._lock:
            if task_id is None:
                if self._aria2_config_paths:
                    latest_task_id = max(
                        self._aria2_config_paths.keys(),
                        key=lambda tid: self._task_status.get(tid, {}).get("created_at", 0),
                    )
                    return self._aria2_config_paths[latest_task_id]

                completed_tasks = [
                    tid
                    for tid, info in self._task_status.items()
                    if info.get("status") == "completed" and "aria2_conf" in info
                ]

                if completed_tasks:
                    latest_task_id = max(
                        completed_tasks,
                        key=lambda tid: self._task_status[tid].get("created_at", 0),
                    )
                    config_path = self._task_status[latest_task_id]["aria2_conf"]
                    self._aria2_config_paths[latest_task_id] = config_path
                    return config_path

                return None

            if task_id in self._aria2_config_paths:
                return self._aria2_config_paths[task_id]

            if task_id in self._task_status:
                task_info = self._task_status[task_id]
                if task_info.get("status") != "completed":
                    return None
                config_path = task_info.get("aria2_conf")
                if config_path:
                    self._aria2_config_paths[task_id] = config_path
                return config_path

            return None

    def set_aria2_config(self, task_id: str, config_path: str) -> None:
        with self._lock:
            self._aria2_config_paths[task_id] = config_path
            if task_id in self._task_status:
                self._task_status[task_id]["aria2_conf"] = config_path

    def _cleanup_old_tasks(self) -> None:
        completed = [
            (tid, info.get("created_at", 0))
            for tid, info in self._task_status.items()
            if info.get("status") in ("completed", "cancelled", "failed")
        ]
        if len(completed) <= self.MAX_COMPLETED_TASKS:
            return

        completed.sort(key=lambda x: x[1])
        to_remove = completed[: len(completed) - self.MAX_COMPLETED_TASKS]
        for tid, _ in to_remove:
            self._task_status.pop(tid, None)
            self._task_results.pop(tid, None)
            self._aria2_config_paths.pop(tid, None)
        logger.debug(f"清理了 {len(to_remove)} 个旧任务记录")

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
