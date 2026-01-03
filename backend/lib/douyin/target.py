# -*- encoding: utf-8 -*-
"""
目标识别和信息获取模块

负责解析用户输入的目标（URL或ID），识别目标类型，并获取目标的基本信息
"""

import os
import re
from urllib.parse import parse_qs, quote, unquote, urlparse

import ujson as json
from loguru import logger

from ...utils.text import quit, sanitize_filename, url_redirect
from .request import Request
from .types import USER_ID_PREFIX, DouyinURL


class TargetHandler:
    """目标处理器：负责目标识别和信息获取"""

    def __init__(self, request: Request, target: str, type: str, down_path: str):
        """
        初始化目标处理器

        Args:
            request: Request实例
            target: 目标URL或ID
            type: 目标类型
            down_path: 下载路径
        """
        self.request = request
        self.target = target
        self.type = type
        self.down_path = down_path
        self.id = ""
        self.url = ""
        self.title = ""
        self.info = {}
        self.render_data = {}

    def parse_target_id(self):
        """解析目标ID和URL"""
        if self.target:
            target = self.target.strip()
            hostname = urlparse(target).hostname

            # 输入链接
            if hostname and hostname.endswith("douyin.com"):
                self._parse_url(target, hostname)
            # 输入非链接
            else:
                self._parse_non_url(target)
        else:
            # 未输入目标，直接采集本账号数据
            self.id = self._get_self_uid()
            self.url = DouyinURL.USER_SELF

    def _parse_url(self, target: str, hostname: str):
        """解析URL类型的目标"""
        if hostname == "v.douyin.com":
            target = url_redirect(target)

        path = unquote(urlparse(target).path.strip("/"))
        path_parts = path.split("/")

        # 确保路径至少有两个部分
        if len(path_parts) < 2:
            self.type = "post"
            self.id = path_parts[-1] if path_parts else ""
            self.url = target
        else:
            _type = path_parts[-2]
            self.id = path_parts[-1]
            self.url = target

            # 自动识别：单个作品、搜索、音乐、合集
            if _type in ["video", "note", "music", "hashtag", "collection"]:
                self.type = _type
                if self.type in ["video", "note"]:
                    self.url = f"{DouyinURL.NOTE}/{self.id}"
            elif _type == "search":
                self.id = unquote(self.id)
                search_type = parse_qs(urlparse(target).query).get("type")
                if search_type is None or search_type[0] in ["video", "general"]:
                    self.type = "search"
                else:
                    self.type = search_type[0]

    def _parse_non_url(self, target: str):
        """解析非URL类型的目标"""
        self.id = target

        if self.type in ["search", "user", "live"]:
            self.url = f"{DouyinURL.SEARCH}/{quote(self.id)}"
        elif (
            self.type in ["video", "note", "music", "hashtag", "collection"]
            and self.id.isdigit()
        ):
            if self.type in ["video", "note"]:
                self.url = f"{DouyinURL.NOTE}/{self.id}"
            else:
                self.url = f"{DouyinURL.BASE}/{self.type}/{self.id}"
        elif self.type in [
            "post",
            "like",
            "favorite",
            "follow",
            "fans",
        ] and self.id.startswith(USER_ID_PREFIX):
            self.url = f"{DouyinURL.USER}/{self.id}"
        else:
            quit(f"[{self.id}]目标输入错误，请检查参数")

    def _get_self_uid(self) -> str:
        """获取当前登录用户的UID"""
        url = DouyinURL.USER_SELF
        text = self.request.getHTML(url)
        if text == "":
            quit(f"获取UID请求失败, url: {url}")

        pattern = r'secUid\\":\\"([-\w]+)\\"'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            quit(f"获取UID请求失败, url: {url}")

    def fetch_target_info(self) -> tuple[str, str]:
        """
        获取目标信息

        Returns:
            tuple: (title, aria2_conf_path)
        """
        # 目标信息
        if self.type in ["search", "user", "live"]:
            self.title = self.id
        elif self.type in ["video", "note"]:
            # 通过API获取，暂时使用ID作为标题
            self.title = self.id
        else:
            self._fetch_from_html()

        # 构建下载路径
        down_path = os.path.join(
            self.down_path, sanitize_filename(f"{self.type}_{self.title}")
        )
        aria2_conf = f"{down_path}.txt"

        return self.title, down_path, aria2_conf, self.info, self.render_data

    def _fetch_from_html(self):
        """从HTML页面获取目标信息"""
        text = self.request.getHTML(self.url)
        pattern = r'self\.__pace_f\.push\(\[1,"\d:\[\S+?({[\s\S]*?)\]\\n"\]\)</script>'
        render_data_list = re.findall(pattern, text)

        if not render_data_list:
            quit(f"提取目标信息失败，可能是cookie无效。url: {self.url}")

        render_data = render_data_list[-1].replace('\\"', '"').replace("\\\\", "\\")
        self.render_data = json.loads(render_data)

        # 根据类型提取信息
        if self.type == "collection":
            self.info = self.render_data["aweme"]["detail"]["mixInfo"]
            self.title = self.info["mixName"]
        elif self.type == "music":
            self.info = self.render_data["musicDetail"]
            self.title = self.info["title"]
        elif self.type == "hashtag":
            self.info = self.render_data["topicDetail"]
            self.title = self.info["chaName"]
        elif self.type in ["video", "note"]:
            self.info = self.render_data["aweme"]["detail"]
            self.title = self.id
        elif self.type in ["post", "like", "favorite", "follow", "fans"]:
            self.info = self.render_data["user"]["user"]
            self.title = self.info["nickname"]
        else:
            quit(f"获取目标信息请求失败, type: {self.type}")
