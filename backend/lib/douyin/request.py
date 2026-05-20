# -*- encoding: utf-8 -*-
"""
@File    :   request.py
@Time    :   2024年07月15日
@Author  :   erma0
@Version :   1.1
@Link    :   https://github.com/ShilongLee/Crawler
@Desc    :   抖音sign
"""
import os
import random
import threading
from urllib.parse import quote

import exejs
import niquests as requests
from loguru import logger

from ..cookies import CookieManager
from ..exceptions import CookieExpiredError, VerifyCheckError
from .types import (
    APIEndpoint,
    CookieField,
    DouyinURL,
    RequestHeaders,
    RequestParams,
    SignMethod,
    TokenConfig,
)

# 指定JS运行时为Node.js
# exejs.reset_runtime("Node")


def _load_sign_script():
    """加载 JS 签名脚本"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    js_file = os.path.join(current_dir, "js", "douyin.js")
    with open(js_file, "r", encoding="utf-8") as f:
        return exejs.compile(f.read())


class Request(object):
    """
    抖音请求处理类

    用于处理抖音网页端的HTTP请求，包括签名生成、参数构建等功能
    """

    HOST = DouyinURL.BASE
    _SIGN = None
    _sign_lock = threading.Lock()

    @classmethod
    def _get_sign(cls):
        if cls._SIGN is None:
            with cls._sign_lock:
                if cls._SIGN is None:
                    try:
                        cls._SIGN = _load_sign_script()
                    except Exception as e:
                        logger.error(f"加载JS签名脚本失败: {e}")
                        raise
        return cls._SIGN

    def __init__(self, cookie="", UA=""):
        self.PARAMS = RequestParams.BASE.copy()
        self.HEADERS = RequestHeaders.DEFAULT.copy()
        self.WEBID = ""

        self.COOKIES = CookieManager.cookies_str_to_dict(cookie) if cookie else {}

        self._session = self._create_session()

        if UA:
            try:
                version = UA.split(" Chrome/")[1].split(" ")[0]
                _version = version.split(".")[0]
                self.HEADERS.update(
                    {
                        "User-Agent": UA,
                        "sec-ch-ua": f'"Chromium";v="{_version}", "Not(A:Brand";v="24", "Google Chrome";v="{_version}"',
                    }
                )
                self.PARAMS.update(
                    {
                        "browser_version": version,
                        "engine_version": version,
                    }
                )
            except (IndexError, ValueError):
                logger.warning(f"无法解析 User-Agent 中的 Chrome 版本: {UA}")

    def close(self) -> None:
        if self._session:
            self._session.close()
            self._session = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    @staticmethod
    def _create_session() -> requests.Session:
        session = requests.Session()
        session.max_redirects = 5
        return session

    def get_sign(self, uri: str, params: dict) -> str:
        """
        生成请求签名(a_bogus)

        Args:
            uri: 请求的URI路径
            params: 请求参数字典

        Returns:
            str: 生成的a_bogus签名
        """
        # 构建查询字符串
        query = "&".join([f"{k}={quote(str(v))}" for k, v in params.items()])
        # 根据URI类型选择不同的签名方法
        call_name = SignMethod.DETAIL
        if "reply" in uri:
            call_name = SignMethod.REPLY
        # 调用JS脚本生成签名
        a_bogus = self._get_sign().call(call_name, query, self.HEADERS.get("User-Agent"))
        return a_bogus

    def get_params(self, params: dict) -> dict:
        """
        构建完整的请求参数

        从Cookie中提取必要的参数并添加到请求参数中
        主要用于单个作品详情请求，其他类型不需要

        Args:
            params: 基础参数字典

        Returns:
            dict: 完整的请求参数字典
        """
        # 从Cookie中提取设备和浏览器信息
        params[CookieField.MS_TOKEN] = self.get_ms_token()
        params["screen_width"] = self.COOKIES.get(CookieField.DY_SWIDTH, 2560)
        params["screen_height"] = self.COOKIES.get(CookieField.DY_SHEIGHT, 1440)
        params["cpu_core_num"] = self.COOKIES.get(CookieField.DEVICE_WEB_CPU_CORE, 24)
        params["device_memory"] = self.COOKIES.get(
            CookieField.DEVICE_WEB_MEMORY_SIZE, 8
        )
        params["verifyFp"] = self.COOKIES.get(CookieField.S_V_WEB_ID, None)
        params["fp"] = self.COOKIES.get(CookieField.S_V_WEB_ID, None)
        params["webid"] = self.get_webid()
        return params

    def get_webid(self):
        """
        获取或生成Web ID

        Returns:
            str: 19位随机数字字符串
        """
        if not self.WEBID:
            # 生成一个随机的webid，避免循环调用
            self.WEBID = str(
                random.randint(TokenConfig.WEBID_MIN, TokenConfig.WEBID_MAX)
            )
        return self.WEBID

    def get_ms_token(self, randomlength=None):
        """
        获取或生成msToken

        Args:
            randomlength: 随机字符串长度，默认使用TokenConfig.MS_TOKEN_LENGTH

        Returns:
            str: Cookie中的msToken或随机生成的字符串
        """
        ms_token = self.COOKIES.get(CookieField.MS_TOKEN, None)
        if not ms_token:
            # 生成随机msToken
            if randomlength is None:
                randomlength = TokenConfig.MS_TOKEN_LENGTH
            ms_token = ""
            base_str = TokenConfig.MS_TOKEN_CHARS
            length = len(base_str) - 1
            for _ in range(randomlength):
                ms_token += base_str[random.randint(0, length)]
        return ms_token

    def getHTML(self, url) -> str:
        headers = self.HEADERS.copy()
        headers["sec-fetch-dest"] = "document"
        response = self._session.get(
            url, headers=headers, cookies=self.COOKIES, timeout=(10, 30)
        )
        if response.status_code != 200 or response.text == "":
            logger.error(f"HTML请求失败, url: {url}, header: {headers}")
            return ""
        return response.text

    def getJSON(self, uri: str, params: dict, data: dict = None):
        url = f"{self.HOST}{uri}"
        params.update(self.PARAMS)
        if uri in [
            APIEndpoint.AWEME_DETAIL,
            APIEndpoint.MUSIC_AWEME,
            APIEndpoint.USER_FOLLOWER,
        ]:
            params["a_bogus"] = self.get_sign(uri, params)
        if data:
            response = self._session.post(
                url,
                params=params,
                data=data,
                headers=self.HEADERS,
                cookies=self.COOKIES,
                timeout=(10, 30),
            )
        else:
            response = self._session.get(
                url,
                params=params,
                headers=self.HEADERS,
                cookies=self.COOKIES,
                timeout=(10, 30),
            )

        if response.status_code != 200:
            logger.error(
                f"JSON请求失败：url: {url},  params: {params}, code: {response.status_code}, body: {response.text}"
            )
            return {}

        if response.text == "":
            logger.error(
                f"响应体为空（Cookie可能已失效）：url: {url},  params: {params}, code: {response.status_code}"
            )
            raise CookieExpiredError("Cookie可能已失效，响应体为空，请在设置中更新Cookie")

        try:
            json_data = response.json()
        except Exception as e:
            logger.error(
                f"JSON解析失败：url: {url},  params: {params}, body: {response.text}, error: {e}"
            )
            return {}

        # 检查是否触发验证码
        if CookieManager.check_verify_check(json_data):
            logger.error(
                f"检测到验证码：url: {url},  params: {params}, body: {response.text}"
            )
            raise VerifyCheckError("触发验证码，请完成验证后再继续")

        # 检查状态码
        if json_data.get("status_code", 0) != 0:
            logger.error(
                f"JSON请求失败：url: {url},  params: {params}, code: {response.status_code}, body: {response.text}"
            )
            return {}

        return json_data


if __name__ == "__main__":
    r = Request()
    print(r.get_webid())
