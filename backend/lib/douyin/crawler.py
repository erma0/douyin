# -*- encoding: utf-8 -*-
"""
抖音爬虫核心模块

主要功能：
- 协调各个模块完成数据采集
- 管理采集流程和状态
- 保存采集结果
"""

import os
import threading
from collections.abc import Callable
from threading import Lock

import ujson as json
from loguru import logger

from ...utils.text import abort, generate_filename, save_json
from ..exceptions import CookieExpiredError, VerifyCheckError
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
        user_agent: str = "",
        filters: dict | None = None,
        on_new_items: Callable | None = None,
        enable_download_title: bool = False,
        enable_download_cover: bool = False,
        cancel_event: threading.Event | None = None,
        filename_fields: list[str] | None = None,
        filename_separator: str = "_",
    ):
        """
        初始化爬虫

        Args:
            target: 目标URL或ID
            limit: 限制采集数量（0表示不限制）
            type: 采集类型
            down_path: 下载路径
            cookie: Cookie字符串
            user_agent: User-Agent字符串，留空使用内置默认值
            filters: 过滤条件
            on_new_items: 新数据回调函数，接收(new_items, type)参数
            enable_download_title: 是否下载标题文本文件
            enable_download_cover: 是否下载封面图
            cancel_event: 取消信号
            filename_fields: 文件名字段列表
            filename_separator: 文件名字段分隔符
        """
        self.target = target
        self.limit = limit
        self.type = type
        self.filters = filters or {}
        self.on_new_items = on_new_items
        self.enable_download_title = enable_download_title
        self.enable_download_cover = enable_download_cover
        self.cancel_event = cancel_event
        self.filename_fields = filename_fields or ["id", "title"]
        self.filename_separator = filename_separator

        # 初始化下载路径
        self.down_path = os.path.join(".", down_path)
        if not os.path.exists(self.down_path):
            os.makedirs(self.down_path)

        # 初始化状态
        self.has_more = True
        self.results_old = []
        self.results = []
        self.lock = Lock()
        self._has_received_data = False

        # 初始化请求客户端
        self.request = Request(cookie, user_agent)
        self.client = DouyinClient(self.request)

        # 目标信息（将在run时初始化）
        self.id = ""
        self.url = ""
        self.title = ""
        self.info = {}
        self.render_data = {}
        self.aria2_conf = ""

    def close(self) -> None:
        if hasattr(self, "request") and self.request:
            self.request.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def run(self):
        """运行爬虫"""
        self._get_target_info()

        if self.cancel_event and self.cancel_event.is_set():
            logger.info("⏹ 采集任务已取消")
            return

        if self.type in ["following", "follower", "post", "favorite", "collection", "search", "music", "hashtag", "mix"]:
            self.get_awemes_list()
        elif self.type == "aweme":
            self.get_aweme_detail()
        else:
            abort(f"获取目标类型错误, type: {self.type}")

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
        try:
            if self.render_data.get("aweme"):
                aweme_detail = self.render_data["aweme"]["detail"]
                self._has_received_data = True
            else:
                aweme_detail = self.client.fetch_aweme_detail(self.id)
                if aweme_detail:
                    self._has_received_data = True
        except CookieExpiredError as e:
            logger.error(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            logger.error(f"✗ Cookie已失效: {e}")
            logger.error(f"  请在设置中更新Cookie后再继续")
            logger.error(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            raise
        except VerifyCheckError as e:
            logger.error(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            logger.error(f"✗ 检测到验证码: {e}")
            logger.error(f"  请在浏览器中打开抖音完成验证后再继续")
            logger.error(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            raise

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
            if self.cancel_event and self.cancel_event.is_set():
                logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                logger.info(f"⏹ 采集任务已取消")
                logger.info(f"  当前已采集: {len(self.results)} 条数据")
                logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                self.has_more = False
                break

            try:
                # 调用API获取数据
                items_list, max_cursor, logid, self.has_more = (
                    self.client.fetch_awemes_list(
                        self.type, self.id, max_cursor, logid, self.filters
                    )
                )

                if items_list:
                    self._has_received_data = True
                    retry = 0

            except CookieExpiredError as e:
                logger.error(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                logger.error(f"✗ Cookie已失效: {e}")
                logger.error(f"  请在设置中更新Cookie后再继续")
                logger.error(f"  当前已采集: {len(self.results)} 条数据")
                logger.error(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                self.has_more = False
                raise
            except VerifyCheckError as e:
                # 验证码异常，直接停止任务，不重试
                logger.error(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                logger.error(f"✗ 检测到验证码: {e}")
                logger.error(f"  请在浏览器中打开抖音完成验证后再继续")
                logger.error(f"  当前已采集: {len(self.results)} 条数据")
                logger.error(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                self.has_more = False
                raise
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
                        prev_count = len(self.results)
                        self.has_more = DataParser.parse_users(
                            items_list, self.results, self.limit, self.has_more
                        )
                        new_user_count = len(self.results) - prev_count
                        if new_user_count > 0 and self.on_new_items:
                            new_users = self.results[prev_count:]
                            self.on_new_items(new_users, self.type)
                    else:
                        abort(f"类型错误，type：{self.type}")
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
                filename = generate_filename(
                    line, self.filename_fields, self.filename_separator
                )

                if self.type == "mix":
                    no_val = line.get("no")
                    if no_val:
                        filename = f"第{no_val}集{self.filename_separator}{filename}"

                # 确定当前作品的下载目录
                item_down_path = self.down_path
                
                # 图文作品使用子目录
                if isinstance(line["download_addr"], list):
                    if self.type == "aweme":
                        parent = os.path.dirname(self.down_path)
                        item_down_path = os.path.join(parent, filename)
                    else:
                        item_down_path = os.path.join(self.down_path, filename)

                    for index, addr in enumerate(line["download_addr"]):
                        lines.append(
                            f'{addr}\n dir={item_down_path}\n out={line["id"]}_{index + 1}.jpeg\n'
                        )
                # 视频作品使用根目录
                elif isinstance(line["download_addr"], str):
                    lines.append(
                        f'{line["download_addr"]}\n dir={self.down_path}\n out={filename}.mp4\n'
                    )
                else:
                    logger.error("下载地址错误")
                
                # 添加封面图下载（如果启用）
                if self.enable_download_cover and line.get("cover"):
                    lines.append(
                        f'{line["cover"]}\n dir={item_down_path}\n out={line["id"]}_cover.jpg\n'
                    )
                
                # 保存标题文本文件（如果启用）
                if self.enable_download_title:
                    try:
                        title_file_path = os.path.join(item_down_path, f'{line["id"]}_title.txt')
                        with open(title_file_path, "w", encoding="utf-8") as f:
                            f.write(desc)
                    except Exception as e:
                        logger.error(f"保存标题文件失败: {e}")

        if lines:
            with open(self.aria2_conf, "w", encoding="utf-8") as f:
                f.writelines(lines)
