# -*- encoding: utf-8 -*-
"""
Cookie管理模块

统一管理Cookie的读取、保存、验证和浏览器获取功能。
"""

import os
from typing import Dict, Optional

import requests
import ujson as json
from loguru import logger

# 修复相对导入问题
try:
    from ..constants import PATHS
except ImportError:
    # 命令行模式下的导入
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from constants import PATHS


class CookieManager:
    """
    Cookie管理器

    负责Cookie的统一管理，包括加载、保存、验证、清除和浏览器获取。
    支持从多个位置读取Cookie，并提供优先级机制。

    Attributes:
        config_dir: 配置文件目录
        cookie_txt_path: cookie.txt文件路径
        cookie_json_path: cookie.json文件路径
    """

    def __init__(self, config_dir: str):
        """
        初始化Cookie管理器

        Args:
            config_dir: 配置文件目录路径

        Note:
            会自动创建配置目录（如果不存在）
        """
        self.config_dir = config_dir
        self.cookie_txt_path = os.path.join(config_dir, PATHS["COOKIE_FILE"])
        self.cookie_json_path = os.path.join(config_dir, "cookie.json")

        # 确保配置目录存在
        os.makedirs(config_dir, exist_ok=True)

    def load_cookie(self, settings_cookie: str = "") -> str:
        """
        加载Cookie

        直接从settings中读取Cookie。

        Args:
            settings_cookie: 设置中的cookie字符串

        Returns:
            Cookie字符串，如果为空则返回空字符串

        Note:
            - Cookie统一保存在settings.json中
            - 返回的Cookie已去除首尾空白
        """
        # 使用settings中的cookie
        if settings_cookie and settings_cookie.strip():
            logger.debug("从配置中加载Cookie")
            return settings_cookie.strip()

        logger.debug("未配置Cookie")
        return ""

    def save_cookie(self, cookie: str) -> bool:
        """
        保存Cookie（已废弃）

        Cookie现在统一保存在settings.json中，此方法保留仅用于兼容性。

        Args:
            cookie: Cookie字符串

        Returns:
            True: 始终返回True（实际不执行保存）

        Note:
            - Cookie由API模块统一保存到settings.json
            - 此方法不再执行实际保存操作
        """
        logger.debug("Cookie由settings.json统一管理，无需单独保存")
        return True

    def validate_cookie(self, cookie: str) -> bool:
        """
        验证Cookie是否有效

        执行基本的Cookie格式和内容验证，确保Cookie包含必要的字段。

        Args:
            cookie: Cookie字符串

        Returns:
            True: Cookie有效
            False: Cookie无效

        验证规则：
        1. Cookie不能为空
        2. 必须包含必要的字段（sessionid或ttwid中的至少一个）
        3. 必须包含'='字符（键值对格式）

        Note:
            - 这是基本验证，不保证Cookie未过期
            - 真正的有效性需要通过API请求验证
            - 字段名不区分大小写
        """
        if not cookie or not cookie.strip():
            return False

        # 基本验证：检查是否包含必要的字段
        # sessionid: 用户会话标识
        # ttwid: 抖音设备标识
        required_fields = ["sessionid", "ttwid"]
        cookie_lower = cookie.lower()

        # 至少包含一个必要字段
        has_required_field = any(field in cookie_lower for field in required_fields)
        if not has_required_field:
            logger.warning(
                f"Cookie缺少必要字段，至少需要包含: {', '.join(required_fields)}"
            )
            return False

        # 检查Cookie格式（必须包含键值对）
        if "=" not in cookie:
            logger.warning("Cookie格式不正确")
            return False

        return True

    def clear_cookie(self) -> bool:
        """
        清除所有Cookie文件

        删除所有Cookie相关文件，用于重置Cookie或退出登录。

        Returns:
            True: 所有文件清除成功
            False: 至少有一个文件清除失败

        Note:
            - 会尝试删除所有Cookie文件
            - 即使某个文件删除失败，也会继续删除其他文件
            - 文件不存在不算失败
            - 删除失败会记录错误日志
        """
        success = True

        # 删除cookie.txt
        if os.path.exists(self.cookie_txt_path):
            try:
                os.remove(self.cookie_txt_path)
                logger.info("已删除cookie.txt")
            except Exception as e:
                logger.error(f"删除cookie.txt失败: {e}")
                success = False

        # 删除cookie.json
        if os.path.exists(self.cookie_json_path):
            try:
                os.remove(self.cookie_json_path)
                logger.info("已删除cookie.json")
            except Exception as e:
                logger.error(f"删除cookie.json失败: {e}")
                success = False

        return success

    @staticmethod
    def cookies_str_to_dict(cookie_string: str) -> Dict[str, str]:
        """
        将Cookie字符串转换为字典格式

        Args:
            cookie_string: Cookie字符串，格式如 "key1=value1; key2=value2"

        Returns:
            Cookie字典
        """
        if not cookie_string or not cookie_string.strip():
            return {}

        cookies = cookie_string.strip().split("; ")
        cookie_dict = {}

        for cookie in cookies:
            if not cookie or cookie == "douyin.com":
                continue
            if "=" not in cookie:
                continue

            try:
                key, value = cookie.split("=", 1)
                cookie_dict[key.strip()] = value.strip()
            except ValueError:
                continue

        return cookie_dict

    @staticmethod
    def cookies_dict_to_str(cookie_dict: Dict[str, str]) -> str:
        """
        将Cookie字典转换为字符串格式

        Args:
            cookie_dict: Cookie字典

        Returns:
            Cookie字符串
        """
        if not cookie_dict:
            return ""

        return "; ".join([f"{key}={value}" for key, value in cookie_dict.items()])

    def test_cookie_validity(self, cookie: str) -> bool:
        """
        通过API测试Cookie是否真正有效

        Args:
            cookie: Cookie字符串

        Returns:
            True: Cookie有效且已登录
            False: Cookie无效或未登录
        """
        if not cookie:
            return False

        try:
            url = "https://sso.douyin.com/check_login/"
            cookie_dict = self.cookies_str_to_dict(cookie)

            response = requests.get(url, cookies=cookie_dict, timeout=10)
            result = response.json()

            if result.get("has_login") is True:
                logger.success("Cookie验证成功，用户已登录")
                return True
            else:
                logger.warning("Cookie验证失败，用户未登录")
                return False

        except Exception as e:
            logger.error(f"Cookie验证请求失败: {e}")
            return False

    @staticmethod
    def get_browser_cookie(browser="edge") -> Dict[str, str]:
        """
        从浏览器获取Cookie (需要rookiepy库)

        Args:
            browser: 浏览器类型 ('chrome', 'edge', 'firefox')

        Returns:
            Cookie字典
        """
        try:
            import rookiepy

            return eval(f"rookiepy.{browser}(['douyin.com'])[0]")
        except ImportError:
            logger.error("需要安装rookiepy库: pip install rookiepy")
            return {}
        except Exception as e:
            logger.error(f"从浏览器获取Cookie失败: {e}")
            return {}


# 全局Cookie管理器实例
_cookie_manager = None


def _get_cookie_manager():
    """获取Cookie管理器实例"""
    global _cookie_manager
    if _cookie_manager is None:
        config_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config"
        )
        _cookie_manager = CookieManager(config_dir)
    return _cookie_manager


# 兼容性接口 - 保持向后兼容
def get_browser_cookie(browser="chrome") -> Dict[str, str]:
    """从浏览器获取Cookie (兼容接口)"""
    return CookieManager.get_browser_cookie(browser)


def get_cookie_dict(cookie="") -> Dict[str, str]:
    """
    获取Cookie字典 (兼容旧接口)

    Args:
        cookie: Cookie字符串或浏览器名称

    Returns:
        Cookie字典
    """
    manager = _get_cookie_manager()

    if cookie:
        # 如果是浏览器名称，从浏览器获取
        if cookie in ["edge", "chrome", "firefox"]:
            return get_browser_cookie(cookie)
        else:
            # 否则作为Cookie字符串处理
            return manager.cookies_str_to_dict(cookie)
    else:
        logger.warning("未提供Cookie，返回空字典")
        return {}


def test_cookie(cookie) -> bool:
    """
    测试Cookie有效性 (兼容旧接口)

    Args:
        cookie: Cookie字符串或字典

    Returns:
        True: Cookie有效
        False: Cookie无效
    """
    manager = _get_cookie_manager()

    if isinstance(cookie, dict):
        cookie_str = manager.cookies_dict_to_str(cookie)
    elif isinstance(cookie, str):
        cookie_str = cookie
    else:
        return False

    return manager.test_cookie_validity(cookie_str)


def cookies_str_to_dict(cookie_string: str) -> Dict[str, str]:
    """Cookie字符串转字典 (兼容旧接口)"""
    return CookieManager.cookies_str_to_dict(cookie_string)


def cookies_dict_to_str(cookie_dict: Dict[str, str]) -> str:
    """Cookie字典转字符串 (兼容旧接口)"""
    return CookieManager.cookies_dict_to_str(cookie_dict)
