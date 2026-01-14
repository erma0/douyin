# -*- encoding: utf-8 -*-
"""
抖音爬虫核心模块

主要功能：
- 协调各个模块完成数据采集
- 管理采集流程和状态
- 保存采集结果
"""

import os
from threading import Lock

import ujson as json
from loguru import logger

from ...utils.text import quit, save_json
from .client import DouyinClient
from .parser import DataParser
from .request import Request
from .target import TargetHandler
from .types import DouyinURL, FieldName


class Douyin:
    """抖音爬虫主类"""

    def __init__(
            self,
            target: str = "",
            limit: int = 0,
            type: str = "post",
            down_path: str = "下载",
            cookie: str = "",
            filters: dict = None,
            on_new_items: callable = None,
    ):
        """
        初始化爬虫

        Args:
            target: 目标URL或ID
            limit: 限制采集数量（0表示不限制）
            type: 采集类型
            down_path: 下载路径
            cookie: Cookie字符串
            filters: 过滤条件
            on_new_items: 新数据回调函数，接收(new_items, type)参数
        """
        self.target = target
        self.limit = limit
        self.type = type
        self.filters = filters or {}
        self.on_new_items = on_new_items  # 新增回调函数

        # 初始化下载路径
        self.down_path = os.path.join(".", down_path)
        if not os.path.exists(self.down_path):
            os.makedirs(self.down_path)

        # 初始化状态
        self.has_more = True
        self.results_old = []
        self.results = []
        self.lock = Lock()

        # 初始化请求客户端
        self.request = Request(cookie)
        self.client = DouyinClient(self.request)

        # 目标信息（将在run时初始化）
        self.id = ""
        self.url = ""
        self.title = ""
        self.info = {}
        self.render_data = {}
        self.aria2_conf = ""

    def run(self):
        """运行爬虫"""
        # 获取目标信息
        self._get_target_info()

        # 根据类型执行不同的采集逻辑
        if self.type == "follower":
            # 修改：粉丝类型仅获取数量，不爬取列表
            self.get_follower_count()
        elif self.type == "following":
            self.get_awemes_list()
        elif self.type in [
            "post",
            "favorite",
            "collection",
            "search",
            "music",
            "hashtag",
            "mix",
        ]:
            self.get_awemes_list()
        elif self.type == "aweme":
            self.get_aweme_detail()
        else:
            quit(f"获取目标类型错误, type: {self.type}")

    def get_follower_count(self):
        """获取粉丝数量"""
        if not self.info:
            logger.error("未获取到目标用户信息")
            return

        # self.info 使用驼峰命名法 (camelCase)
        nickname = self.info.get("nickname", "未知")

        # 1. 获取粉丝数 (尝试 followerCount 和 mplatformFollowersCount)
        follower_count = self.info.get("followerCount", 0)
        if not follower_count:
            follower_count = self.info.get("mplatformFollowersCount", 0)

        logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info(f"目标用户: {nickname}")
        logger.info(f"粉丝数量: {follower_count}")
        logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 2. 构造结果数据 (修正了所有字段的 key)
        self.results = [{
            "nickname": nickname,
            "uid": self.info.get("uid"),
            "sec_uid": self.info.get("secUid"),  # 对应 secUid
            "follower_count": follower_count,
            "unique_id": self.info.get("uniqueId"),  # 对应 uniqueId
            "short_id": self.info.get("shortId"),  # 对应 shortId
            "signature": self.info.get("desc"),  # 对应 desc
            "avatar": self.info.get("avatarUrl"),  # 对应 avatarUrl
            "aweme_count": self.info.get("awemeCount"),  # 对应 awemeCount
            "following_count": self.info.get("followingCount"),  # 对应 followingCount
            "total_favorited": self.info.get("totalFavorited"),  # 对应 totalFavorited
        }]

        # 保存结果
        self.save()

    def get_target_id(self):
        """
        解析目标ID（向后兼容的公共方法）

        注意：此方法仅用于向后兼容，建议使用 run() 方法
        """
        handler = TargetHandler(self.request, self.target, self.type, self.down_path)
        handler.parse_target_id()

        # 更新目标信息
        self.id = handler.id
        self.url = handler.url
        self.type = handler.type

    def _get_target_info(self):
        """获取目标信息"""
        # 使用TargetHandler处理目标
        handler = TargetHandler(self.request, self.target, self.type, self.down_path)
        handler.parse_target_id()

        # 更新目标信息
        self.id = handler.id
        self.url = handler.url
        self.type = handler.type

        # 获取详细信息
        self.title, self.down_path, self.aria2_conf, self.info, self.render_data = (
            handler.fetch_target_info()
        )

        # 增量采集：加载旧数据
        if self.type == "post":
            json_path = f"{self.down_path}.json"
            if os.path.exists(json_path) and not self.results_old:
                with open(json_path, "r", encoding="utf-8") as f:
                    self.results_old = json.load(f)

    def get_aweme_detail(self):
        """获取单个作品详情"""
        # 优先从render_data获取
        if self.render_data.get("aweme"):
            aweme_detail = self.render_data["aweme"]["detail"]
        else:
            # 通过API获取
            aweme_detail = self.client.fetch_aweme_detail(self.id)

        # 解析数据
        with self.lock:
            new_items, self.has_more = DataParser.parse_awemes(
                [aweme_detail],
                self.results,
                self.results_old,
                self.limit,
                self.has_more,
                self.type,
                self.down_path,
            )
            # 触发回调
            if new_items and self.on_new_items:
                self.on_new_items(new_items, self.type)

        self.save()

    def get_awemes_list(self):
        """获取作品/用户列表"""
        max_cursor = 0
        logid = ""
        retry = 0
        max_retry = 10

        while self.has_more:
            try:
                # 调用API获取数据
                items_list, max_cursor, logid, self.has_more = (
                    self.client.fetch_awemes_list(
                        self.type, self.id, max_cursor, logid, self.filters
                    )
                )

                # 重置重试计数
                if items_list:
                    retry = 0

            except Exception as e:
                retry += 1
                logger.error(f"采集请求出错: {e}... 进行第{retry}次重试")
                if retry >= max_retry:
                    logger.error(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    logger.error(f"✗ 已达到最大重试次数({max_retry}次)，停止任务")
                    logger.error(f"  当前已采集: {len(self.results)} 条数据")
                    logger.error(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    self.has_more = False
                continue

            # 解析数据
            if items_list:
                with self.lock:
                    if self.type in [
                        "post",
                        "favorite",
                        "collection",
                        "search",
                        "music",
                        "hashtag",
                        "mix",
                    ]:
                        new_items, self.has_more = DataParser.parse_awemes(
                            items_list,
                            self.results,
                            self.results_old,
                            self.limit,
                            self.has_more,
                            self.type,
                            self.down_path,
                        )
                        # 触发回调
                        if new_items and self.on_new_items:
                            self.on_new_items(new_items, self.type)
                    elif self.type in ["following", "follower"]:
                        self.has_more = DataParser.parse_users(
                            items_list, self.results, self.limit, self.has_more
                        )
                    else:
                        quit(f"类型错误，type：{self.type}")
            elif self.has_more:
                retry += 1
                logger.error(f"采集未完成，但请求结果为空... 进行第{retry}次重试")
                if retry >= max_retry:
                    logger.error(f"已达到最大重试次数({max_retry}次)，停止任务")
                    self.has_more = False

        self.save()

    def save(self):
        """保存采集结果（JSON数据和aria2配置）"""
        if not self.results:
            logger.info("本次采集结果为空")
            return

        logger.success(f"采集完成，本次共采集到 {len(self.results)} 条结果")

        # 保存JSON数据
        if self.type == "post":
            self.results.sort(key=lambda item: item["id"], reverse=True)
        save_json(self.down_path, self.results)

        # 保存aria2下载配置
        self._save_aria2_config()

    def _save_aria2_config(self):
        """保存aria2下载配置文件"""
        lines = []

        # 保存主页链接
        if self.type in ["following", "follower"]:
            lines = [
                f"{DouyinURL.USER}/{line.get(FieldName.SEC_UID, 'None')}\n"
                for line in self.results
                if line.get(FieldName.SEC_UID)
            ]
        # 保存作品下载配置
        else:
            for line in self.results:
                desc = line.get("desc") or "无标题"
                filename = f'{line["id"]}_{desc}'

                if self.type == "mix":
                    filename = f"第{line['no']}集_{filename}"

                # 图文作品
                if isinstance(line["download_addr"], list):
                    if self.type == "aweme":
                        down_path = self.down_path.replace(line["id"], filename)
                    else:
                        down_path = os.path.join(self.down_path, filename)

                    for index, addr in enumerate(line["download_addr"]):
                        lines.append(
                            f'{addr}\n dir={down_path}\n out={line["id"]}_{index + 1}.jpeg\n'
                        )
                # 视频作品
                elif isinstance(line["download_addr"], str):
                    lines.append(
                        f'{line["download_addr"]}\n dir={self.down_path}\n out={filename}.mp4\n'
                    )
                else:
                    logger.error("下载地址错误")

        if lines:
            with open(self.aria2_conf, "w", encoding="utf-8") as f:
                f.writelines(lines)