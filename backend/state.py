"""
应用状态管理模块
"""

import os
import time
from typing import Any, Dict, List, Optional

import ujson as json
from loguru import logger

from .constants import (
    ARIA2_DEFAULTS,
    CONFIG_DIR,
    DEFAULT_SETTINGS,
    DOWNLOAD_DEFAULTS,
    DOWNLOAD_DIR,
    SETTINGS_FILE,
)
from .lib.aria2_manager import Aria2Manager


class AppState:
    """应用状态管理"""

    # 配置验证规则
    VALIDATORS = {
        "cookie": (lambda x: isinstance(x, str), "必须是字符串"),
        "downloadPath": (
            lambda x: isinstance(x, str) and len(x) > 0,
            "必须是非空字符串",
        ),
        "maxRetries": (
            lambda x: isinstance(x, int) and 0 <= x <= 10,
            "必须是0-10的整数",
        ),
        "maxConcurrency": (
            lambda x: isinstance(x, int) and 1 <= x <= 10,
            "必须是1-10的整数",
        ),
        "aria2Host": (lambda x: isinstance(x, str) and len(x) > 0, "必须是非空字符串"),
        "aria2Port": (
            lambda x: isinstance(x, int) and 1 <= x <= 65535,
            "必须是1-65535的整数",
        ),
        "aria2Secret": (lambda x: isinstance(x, str), "必须是字符串"),
    }

    def __init__(self) -> None:
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("🚀 应用状态初始化中...")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 确保配置目录存在
        os.makedirs(CONFIG_DIR, exist_ok=True)

        # 是否首次运行
        self.is_first_run = not os.path.exists(SETTINGS_FILE)
        if self.is_first_run:
            logger.info("🎉 检测到首次运行")

        # 配置
        self.settings: Dict[str, Any] = self._load_settings()

        # 任务状态
        self.task_status: Dict[str, Dict[str, Any]] = {}
        self.task_results: Dict[str, List[Dict[str, Any]]] = {}
        self.aria2_config_paths: Dict[str, str] = {}

        # Aria2 管理器
        self.aria2_manager: Optional[Aria2Manager] = self._init_aria2()

        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.success("✓ 应用状态初始化完成")
        logger.info(f"  - 配置目录: {CONFIG_DIR}")
        logger.info(f"  - 下载目录: {self.settings.get('downloadPath')}")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # ========== 配置管理 ==========

    def _load_settings(self) -> Dict[str, Any]:
        """加载配置"""
        if not os.path.exists(SETTINGS_FILE):
            settings = DEFAULT_SETTINGS.copy()
            self._save_settings_file(settings)
            logger.info("✓ 默认配置已创建")
            return settings

        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
            logger.info("✓ 配置已加载")
        except json.JSONDecodeError:
            logger.error("✗ 配置文件损坏，备份并重置")
            self._backup_settings_file()
            settings = DEFAULT_SETTINGS.copy()
            self._save_settings_file(settings)
            return settings
        except Exception as e:
            logger.error(f"✗ 加载配置失败: {e}")
            return DEFAULT_SETTINGS.copy()

        # 验证修复 + 补充缺失
        need_save = False

        is_valid, errors = self._validate(settings)
        if not is_valid:
            logger.warning("⚠ 配置包含无效项，自动修复...")
            for err in errors:
                key = err.split(":")[0].strip()
                if key in DEFAULT_SETTINGS:
                    settings[key] = DEFAULT_SETTINGS[key]
                    logger.warning(f"  - 已修复 {key}")
            need_save = True

        for key, default in DEFAULT_SETTINGS.items():
            if key not in settings:
                settings[key] = default
                need_save = True

        if need_save:
            self._save_settings_file(settings)

        return settings

    def _validate(self, settings: Dict[str, Any]) -> tuple[bool, List[str]]:
        """验证配置"""
        errors = []
        for key, value in settings.items():
            if key in self.VALIDATORS:
                check, msg = self.VALIDATORS[key]
                try:
                    if not check(value):
                        errors.append(f"{key}: {msg}")
                except Exception as e:
                    errors.append(f"{key}: 验证出错 - {e}")
        return len(errors) == 0, errors

    def _save_settings_file(self, settings: Dict[str, Any]) -> None:
        """保存配置到文件"""
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)

    def _backup_settings_file(self) -> None:
        """备份配置文件"""
        if os.path.exists(SETTINGS_FILE):
            backup = f"{SETTINGS_FILE}.backup.{int(time.time())}"
            try:
                os.rename(SETTINGS_FILE, backup)
                logger.info(f"  - 已备份到: {backup}")
            except Exception as e:
                logger.warning(f"  - 备份失败: {e}")

    def save_settings(self, updates: Dict[str, Any]) -> None:
        """更新并保存配置"""
        is_valid, errors = self._validate(updates)
        if not is_valid:
            raise ValueError("配置验证失败:\n" + "\n".join(f"  - {e}" for e in errors))

        self.settings.update(updates)
        self._save_settings_file(self.settings)
        logger.success(f"✓ 配置已保存: {', '.join(updates.keys())}")

    # ========== Aria2 管理 ==========

    def _init_aria2(self) -> Optional[Aria2Manager]:
        """初始化 Aria2 管理器"""
        try:
            return Aria2Manager(
                host=self.settings.get("aria2Host", ARIA2_DEFAULTS["HOST"]),
                port=self.settings.get("aria2Port", ARIA2_DEFAULTS["PORT"]),
                secret=self.settings.get("aria2Secret", ARIA2_DEFAULTS["SECRET"]),
                download_dir=self.settings.get(
                    "downloadPath", DOWNLOAD_DIR
                ),
                max_retries=self.settings.get(
                    "maxRetries", DOWNLOAD_DEFAULTS["MAX_RETRIES"]
                ),
                max_concurrency=self.settings.get(
                    "maxConcurrency", DOWNLOAD_DEFAULTS["MAX_CONCURRENCY"]
                ),
            )
        except Exception as e:
            logger.error(f"初始化 Aria2 管理器失败: {e}")
            return None

    # ========== 状态查询 ==========

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
            "config": len(self.settings) > 0,
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
