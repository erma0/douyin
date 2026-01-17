# -*- encoding: utf-8 -*-
"""
Cookie工具模块

提供Cookie的格式转换和验证功能。
"""

from typing import Dict

import requests
from loguru import logger


class CookieManager:
    """
    Cookie工具类

    提供Cookie的格式转换和验证功能。
    所有方法都是静态方法，不需要实例化。
    """

    @staticmethod
    def validate_cookie(cookie: str) -> bool:
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
            logger.debug("Cookie为空")
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
            logger.warning("Cookie格式不正确，缺少键值对分隔符")
            return False

        return True

    @staticmethod
    def cookies_str_to_dict(cookie_string: str) -> Dict[str, str]:
        """
        将Cookie字符串转换为字典格式

        Args:
            cookie_string: Cookie字符串，格式如 "key1=value1; key2=value2"

        Returns:
            Cookie字典，如果输入为空或格式错误则返回空字典
        """
        if not cookie_string or not cookie_string.strip():
            return {}

        # 支持多种分隔符："; " 或 ";"
        cookies = cookie_string.strip().replace("; ", ";").split(";")
        cookie_dict = {}

        for cookie in cookies:
            cookie = cookie.strip()
            # 跳过空字符串和域名标识
            if not cookie or cookie == "douyin.com":
                continue
            if "=" not in cookie:
                logger.debug(f"跳过无效的Cookie片段: {cookie}")
                continue

            try:
                key, value = cookie.split("=", 1)
                key = key.strip()
                value = value.strip().rstrip(";")

                # 跳过空键或空值
                if key and value:
                    cookie_dict[key] = value
            except ValueError as e:
                logger.debug(f"解析Cookie片段失败: {cookie}, 错误: {e}")
                continue

        return cookie_dict

    @staticmethod
    def cookies_dict_to_str(cookie_dict: Dict[str, str]) -> str:
        """
        将Cookie字典转换为字符串格式

        Args:
            cookie_dict: Cookie字典

        Returns:
            Cookie字符串，格式为 "key1=value1; key2=value2"
        """
        if not cookie_dict:
            return ""

        # 过滤掉空键或空值
        valid_items = [(k, v) for k, v in cookie_dict.items() if k and v]
        return "; ".join([f"{key}={value}" for key, value in valid_items])

    @staticmethod
    def test_cookie_validity(cookie: str) -> bool:
        """
        通过API测试Cookie是否真正有效

        Args:
            cookie: Cookie字符串

        Returns:
            True: Cookie有效且已登录
            False: Cookie无效或未登录
        """
        if not cookie or not cookie.strip():
            logger.debug("Cookie为空，无法验证")
            return False

        try:
            url = "https://sso.douyin.com/check_login/"
            cookie_dict = CookieManager.cookies_str_to_dict(cookie)

            if not cookie_dict:
                logger.warning("Cookie解析失败，无法验证")
                return False

            response = requests.get(url, cookies=cookie_dict, timeout=10)

            # 检查HTTP状态码
            if response.status_code != 200:
                logger.warning(f"Cookie验证请求失败，状态码: {response.status_code}")
                return False

            result = response.json()

            if result.get("has_login") is True:
                logger.success("Cookie验证成功，用户已登录")
                return True
            else:
                logger.warning("Cookie验证失败，用户未登录")
                return False

        except requests.exceptions.Timeout:
            logger.error("Cookie验证请求超时")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Cookie验证网络请求失败: {e}")
            return False
        except ValueError as e:
            logger.error(f"Cookie验证响应解析失败: {e}")
            return False
        except Exception as e:
            logger.error(f"Cookie验证失败，未知错误: {e}")
            return False

    # 浏览器 Cookie 获取功能已移除
    # 原因：不同浏览器适配复杂，建议手动从浏览器复制 Cookie
