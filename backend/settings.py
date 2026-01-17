# -*- encoding: utf-8 -*-
"""
配置管理模块

统一管理应用配置的加载、验证、保存功能。
提供全局 settings 实例供其他模块使用。
"""

import os
import time
from typing import Any, Callable, Dict, List, Tuple

import ujson as json
from loguru import logger

from .constants import CONFIG_DIR, DEFAULT_SETTINGS, SETTINGS_FILE


class SettingsManager:
    """
    配置管理器

    负责配置文件的加载、验证、保存和备份。
    支持配置项的自动补全和损坏修复。
    """

    # 配置验证规则: key -> (validator, error_message)
    VALIDATORS: Dict[str, Tuple[Callable[[Any], bool], str]] = {
        "cookie": (lambda x: isinstance(x, str), "必须是字符串"),
        "userAgent": (lambda x: isinstance(x, str), "必须是字符串"),
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

    def __init__(self, auto_load: bool = True) -> None:
        """
        初始化配置管理器

        Args:
            auto_load: 是否自动加载配置，默认 True
        """
        self._settings: Dict[str, Any] = {}
        self._is_first_run: bool = not os.path.exists(SETTINGS_FILE)

        # 确保配置目录存在
        os.makedirs(CONFIG_DIR, exist_ok=True)

        if auto_load:
            self.load()

    @property
    def is_first_run(self) -> bool:
        """是否首次运行"""
        return self._is_first_run

    @property
    def data(self) -> Dict[str, Any]:
        """获取完整配置字典（只读副本）"""
        return self._settings.copy()

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项

        Args:
            key: 配置键名
            default: 默认值，如果未指定则从 DEFAULT_SETTINGS 获取

        Returns:
            配置值
        """
        if default is None:
            default = DEFAULT_SETTINGS.get(key)
        return self._settings.get(key, default)

    def load(self) -> Dict[str, Any]:
        """
        加载配置文件

        Returns:
            加载后的配置字典
        """
        if not os.path.exists(SETTINGS_FILE):
            self._settings = DEFAULT_SETTINGS.copy()
            self._save_file()
            logger.info("✓ 默认配置已创建")
            return self._settings

        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                self._settings = json.load(f)
            logger.info("✓ 配置已加载")
        except json.JSONDecodeError:
            logger.error("✗ 配置文件损坏，备份并重置")
            self._backup_file()
            self._settings = DEFAULT_SETTINGS.copy()
            self._save_file()
            return self._settings
        except Exception as e:
            logger.error(f"✗ 加载配置失败: {e}")
            self._settings = DEFAULT_SETTINGS.copy()
            return self._settings

        # 验证修复 + 补充缺失
        self._repair_and_complete()

        return self._settings

    def save(self, updates: Dict[str, Any]) -> None:
        """
        更新并保存配置

        Args:
            updates: 要更新的配置项

        Raises:
            ValueError: 配置验证失败
        """
        is_valid, errors = self._validate(updates)
        if not is_valid:
            raise ValueError("配置验证失败:\n" + "\n".join(f"  - {e}" for e in errors))

        self._settings.update(updates)
        self._save_file()
        logger.success(f"✓ 配置已保存: {', '.join(updates.keys())}")

    def _validate(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证配置项"""
        errors = []
        for key, value in data.items():
            if key in self.VALIDATORS:
                check, msg = self.VALIDATORS[key]
                try:
                    if not check(value):
                        errors.append(f"{key}: {msg}")
                except Exception as e:
                    errors.append(f"{key}: 验证出错 - {e}")
        return len(errors) == 0, errors

    def _repair_and_complete(self) -> None:
        """修复无效配置项并补充缺失项"""
        need_save = False

        # 验证并修复无效项
        is_valid, errors = self._validate(self._settings)
        if not is_valid:
            logger.warning("⚠ 配置包含无效项，自动修复...")
            for err in errors:
                key = err.split(":")[0].strip()
                if key in DEFAULT_SETTINGS:
                    self._settings[key] = DEFAULT_SETTINGS[key]
                    logger.warning(f"  - 已修复 {key}")
            need_save = True

        # 补充缺失项
        for key, default in DEFAULT_SETTINGS.items():
            if key not in self._settings:
                self._settings[key] = default
                need_save = True

        if need_save:
            self._save_file()

    def _save_file(self) -> None:
        """保存配置到文件"""
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, ensure_ascii=False, indent=2)

    def _backup_file(self) -> None:
        """备份配置文件"""
        if os.path.exists(SETTINGS_FILE):
            backup = f"{SETTINGS_FILE}.backup.{int(time.time())}"
            try:
                os.rename(SETTINGS_FILE, backup)
                logger.info(f"  - 已备份到: {backup}")
            except Exception as e:
                logger.warning(f"  - 备份失败: {e}")


# 全局实例
settings = SettingsManager()
