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
from urllib.parse import quote

import exejs
import requests
from loguru import logger

from ..cookies import CookieManager
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
    # JS 签名脚本
    SIGN = _load_sign_script()

    def __init__(self, cookie="", UA=""):
        """
        初始化请求对象

        Args:
            cookie: Cookie字符串，用于身份验证
            UA: User-Agent字符串，如果需要访问搜索页面等内容需要提供与cookie对应的UA
        """
        self.PARAMS = RequestParams.BASE.copy()
        self.HEADERS = RequestHeaders.DEFAULT.copy()
        self.WEBID = ""

        self.COOKIES = CookieManager.cookies_str_to_dict(cookie) if cookie else {}

        # 如果提供了UA，更新请求头和参数以匹配浏览器版本
        if UA:
            # 从UA中提取Chrome版本号
            version = UA.split(" Chrome/")[1].split(" ")[0]
            _version = version.split(".")[0]
            # 更新请求头中的UA和版本信息
            self.HEADERS.update(
                {
                    "User-Agent": UA,
                    "sec-ch-ua": f'"Chromium";v="{_version}", "Not(A:Brand";v="24", "Google Chrome";v="{_version}"',
                }
            )
            # 更新参数中的浏览器和引擎版本
            self.PARAMS.update(
                {
                    "browser_version": version,
                    "engine_version": version,
                }
            )

    def get_sign(self, uri: str, params: dict) -> dict:
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
        a_bogus = self.SIGN.call(call_name, query, self.HEADERS.get("User-Agent"))
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
        """
        获取网页HTML内容

        Args:
            url: 目标URL

        Returns:
            str: HTML内容，失败返回空字符串
        """
        headers = self.HEADERS.copy()
        # 修改fetch目标为document类型
        headers["sec-fetch-dest"] = "document"
        response = requests.get(url, headers=headers, cookies=self.COOKIES)
        if response.status_code != 200 or response.text == "":
            logger.error(f"HTML请求失败, url: {url}, header: {headers}")
            return ""
        return response.text

    def getJSON(self, uri: str, params: dict, data: dict = None):
        """
        发送JSON API请求

        Args:
            uri: API路径
            params: 请求参数
            data: POST请求的数据，如果提供则使用POST方法，否则使用GET

        Returns:
            dict: 响应的JSON数据，失败返回空字典
        """
        url = f"{self.HOST}{uri}"
        # 合并基础参数
        params.update(self.PARAMS)
        # 注意：单个作品详情/音乐/粉丝接口需要签名
        if uri in [
            APIEndpoint.AWEME_DETAIL,
            APIEndpoint.MUSIC_AWEME,
            APIEndpoint.USER_FOLLOWER,
        ]:
            params["a_bogus"] = self.get_sign(uri, params)
        # 根据是否有data决定使用POST还是GET
        if data:
            response = requests.post(
                url,
                params=params,
                data=data,
                headers=self.HEADERS,
                cookies=self.COOKIES,
            )
        else:
            response = requests.get(
                url, params=params, headers=self.HEADERS, cookies=self.COOKIES
            )

        # 检查响应状态
        if (
            response.status_code != 200
            or response.text == ""
            or response.json().get("status_code", 0) != 0
        ):
            logger.error(
                f"JSON请求失败：url: {url},  params: {params}, code: {response.status_code}, body: {response.text}"
            )
            return {}

        return response.json()


if __name__ == "__main__":
    r = Request()
    print(r.get_webid())
