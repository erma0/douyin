# -*- encoding: utf-8 -*-
"""
数据解析模块

负责解析抖音API返回的数据，提取作品和用户信息
"""

import os
from typing import List

from loguru import logger

from ...utils.text import sanitize_filename, save_json
from .types import AwemeType


class DataParser:
    """数据解析器：负责解析作品和用户数据"""

    @staticmethod
    def parse_awemes(
        awemes_list: List[dict],
        results: list,
        results_old: list,
        limit: int,
        has_more: bool,
        type: str,
        down_path: str,
    ) -> tuple[List[dict], bool]:
        """
        解析作品列表

        Args:
            awemes_list: 原始作品数据列表
            results: 当前结果列表
            results_old: 旧结果列表（用于增量采集）
            limit: 限制数量
            has_more: 是否还有更多数据
            type: 采集类型
            down_path: 下载路径

        Returns:
            tuple: (新增的作品列表, 是否还有更多数据)
        """
        new_items = []

        if limit == 0 or len(results) < limit:
            for item in awemes_list:
                # 兼容搜索
                if item.get("aweme_info"):
                    item = item["aweme_info"]

                # 限制数量
                if limit > 0 and len(results) >= limit:
                    has_more = False
                    logger.info(f"已达到限制采集数量： {len(results)}")
                    return new_items, has_more

                # 增量采集
                _time = item.get("create_time", item.get("createTime"))
                if results_old:
                    old = results_old[0]["time"]
                    if _time <= old:
                        _is_top = item.get("is_top", item.get("tag", {}).get("isTop"))
                        if _is_top:  # 置顶作品，不重复保存
                            continue
                        if has_more:
                            has_more = False
                        logger.success(f"增量采集完成，上次运行结果：{old}")
                        results.extend(results_old)
                        return new_items, has_more

                # 解析作品数据
                aweme = DataParser._parse_single_aweme(item, type)
                if aweme:
                    results.append(aweme)
                    new_items.append(aweme)

            logger.info(f"采集中，已采集到 {len(results)} 条结果")
        else:
            has_more = False
            logger.info(f"已达到限制采集数量： {len(results)}")

        return new_items, has_more

    @staticmethod
    def _parse_single_aweme(item: dict, type: str) -> dict:
        """
        解析单个作品数据

        Args:
            item: 原始作品数据
            type: 采集类型

        Returns:
            dict: 解析后的作品数据，如果是不支持的类型则返回None
        """
        _type = item.get("aweme_type", item.get("awemeType"))
        aweme = item.get("statistics", item.get("stats", {}))

        # 清理不需要的字段
        unnecessary_fields = [
            "playCount",
            "downloadCount",
            "forwardCount",
            "collectCount",
            "digest",
            "exposure_count",
            "live_watch_count",
            "play_count",
            "download_count",
            "forward_count",
            "lose_count",
            "lose_comment_count",
        ]
        for field in unnecessary_fields:
            aweme.pop(field, None)

        # 根据作品类型处理下载地址
        if _type <= AwemeType.VIDEO_MAX or _type in AwemeType.VIDEO_SPECIAL:  # 视频
            play_addr = item["video"].get("play_addr")
            if play_addr:
                download_addr = play_addr["url_list"][-1]
            else:
                download_addr = item["download"]["urlList"][-1]
                download_addr = download_addr.replace("watermark=1", "watermark=0")
            aweme["download_addr"] = download_addr
        elif _type == AwemeType.IMAGE:  # 图文
            aweme["download_addr"] = [
                images.get("url_list", images.get("urlList"))[-1]
                for images in item["images"]
            ]
        elif _type == AwemeType.LIVE:  # 直播
            return None
        else:  # 其他类型作品
            aweme["download_addr"] = "其他类型作品"
            logger.info(f"其他类型作品：type {_type}")
            save_json(f"type_{_type}", item)
            return None

        # 基本信息
        aweme.pop("aweme_id", None)
        aweme["id"] = item.get("aweme_id", item.get("awemeId"))
        aweme["time"] = item.get("create_time", item.get("createTime"))
        aweme["type"] = _type
        aweme["desc"] = sanitize_filename(item.get("desc"))
        aweme["duration"] = item.get("duration", item["video"].get("duration"))

        # 音乐信息
        music = item.get("music")
        if music:
            aweme["music_title"] = sanitize_filename(music["title"])
            aweme["music_url"] = music.get("play_url", music.get("playUrl"))["uri"]

        # 封面
        cover = item["video"].get("cover")
        if isinstance(cover, dict):
            aweme["cover"] = cover["url_list"][-1]
        else:
            aweme["cover"] = f"https:{item['video']['dynamicCover']}"

        # 作者信息
        author = item.get("author", item.get("authorInfo"))
        if author:
            avatarThumb = author.get("avatar_thumb", author.get("avatarThumb"))
            aweme["author_avatar"] = avatarThumb.get(
                "url_list", avatarThumb.get("urlList")
            )[-1]
            aweme["author_nickname"] = author.get("nickname")
            aweme["author_uid"] = author.get("sec_uid", author.get("secUid"))
            aweme["author_unique_id"] = author.get("unique_id", author.get("uniqueId"))
            aweme["author_short_id"] = author.get("short_id", author.get("shortId"))
            aweme["author_signature"] = sanitize_filename(author.get("signature"))

        # 话题标签
        text_extra = item.get("text_extra", item.get("textExtra"))
        if text_extra:
            aweme["text_extra"] = [
                {
                    "tag_id": hashtag.get("hashtag_id", hashtag.get("hashtagId")),
                    "tag_name": hashtag.get("hashtag_name", hashtag.get("hashtagName")),
                }
                for hashtag in text_extra
            ]

        # 合集信息
        if type == "mix":
            aweme["no"] = item["mix_info"]["statis"]["current_episode"]

        return aweme

    @staticmethod
    def parse_users(
        user_list: List[dict], results: list, limit: int, has_more: bool
    ) -> bool:
        """
        解析用户列表

        Args:
            user_list: 原始用户数据列表
            results: 当前结果列表
            limit: 限制数量
            has_more: 是否还有更多数据

        Returns:
            bool: 是否还有更多数据
        """
        if limit == 0 or len(results) < limit:
            for item in user_list:
                # 兼容搜索
                if item.get("user_info"):
                    item = item["user_info"]

                # 限制数量
                if limit > 0 and len(results) >= limit:
                    has_more = False
                    logger.info(f"已达到限制采集数量： {len(results)}")
                    return has_more

                # 解析用户数据
                user_info = DataParser._parse_single_user(item)
                results.append(user_info)

            logger.info(f"采集中，已采集到 {len(results)} 条结果")
        else:
            has_more = False
            logger.info(f"已达到限制采集数量： {len(results)}")

        return has_more

    @staticmethod
    def _parse_single_user(item: dict) -> dict:
        """
        解析单个用户数据

        Args:
            item: 原始用户数据

        Returns:
            dict: 解析后的用户数据
        """
        user_info = {}
        user_info["nickname"] = sanitize_filename(item["nickname"])
        user_info["signature"] = sanitize_filename(item["signature"])
        user_info["avatar"] = item["avatar_thumb"]["url_list"][0]

        # 基本字段
        basic_fields = [
            "sec_uid",
            "uid",
            "short_id",
            "unique_id",
            "unique_id_modify_time",
            "aweme_count",
            "favoriting_count",
            "follower_count",
            "following_count",
            "constellation",
            "create_time",
            "enterprise_verify_reason",
            "is_gov_media_vip",
            "live_status",
            "total_favorited",
            "share_qrcode_uri",
        ]
        for field in basic_fields:
            if item.get(field):
                user_info[field] = item[field]

        # 直播间信息
        room_id = item.get("room_id")
        if room_id:
            user_info["live_room_id"] = room_id
            user_info["live_room_url"] = [
                f"http://pull-flv-f26.douyincdn.com/media/stream-{room_id}.flv",
                f"http://pull-hls-f26.douyincdn.com/media/stream-{room_id}.m3u8",
            ]

        # 原创音乐人
        musician = item.get("original_musician")
        if musician and musician.get("music_count"):
            user_info["original_musician"] = item["original_musician"]

        return user_info
