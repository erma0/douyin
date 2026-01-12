# -*- encoding: utf-8 -*-
"""
抖音API客户端模块

负责构建API请求参数并调用抖音API接口
"""

from typing import List, Tuple
from urllib.parse import quote, unquote

from ...utils.text import quit
from .request import Request
from .types import APIConfig, APIEndpoint


class DouyinClient:
    """API客户端：负责调用抖音各类API接口"""

    def __init__(self, request: Request):
        """
        初始化API客户端

        Args:
            request: Request实例
        """
        self.request = request

    def fetch_aweme_detail(self, aweme_id: str) -> dict:
        """
        获取单个作品详情

        Args:
            aweme_id: 作品ID

        Returns:
            dict: 作品详情数据
        """
        params = {"aweme_id": aweme_id}
        uri = APIEndpoint.AWEME_DETAIL

        resp = self.request.getJSON(uri, params)
        aweme_detail = resp.get("aweme_detail", {})

        if not aweme_detail:
            quit("作品详情获取失败")

        return aweme_detail

    def fetch_awemes_list(
        self, type: str, target_id: str, max_cursor: int, logid: str, filters: dict
    ) -> Tuple[List[dict], int, str, bool]:
        """
        获取作品/用户列表

        Args:
            type: 采集类型
            target_id: 目标ID
            max_cursor: 游标位置
            logid: 日志ID
            filters: 过滤条件

        Returns:
            tuple: (作品列表, 新游标, 日志ID, 是否还有更多)
        """
        uri, params, data = self._build_awemes_params(
            type, target_id, max_cursor, logid, filters
        )

        resp = self.request.getJSON(uri, params, data)

        # 提取游标
        new_cursor = max_cursor
        for name in ["max_cursor", "cursor", "min_time"]:
            new_cursor = resp.get(name, 0)
            if new_cursor:
                break

        # 提取日志ID
        if not logid:
            logid = resp.get("log_pb", {}).get("impr_id", "")

        # 提取数据列表
        items_list = []
        for name in ["aweme_list", "user_list", "data", "followings", "followers"]:
            items_list = resp.get(name, [])
            if items_list:
                break

        has_more = resp.get("has_more", 0)

        return items_list, new_cursor, logid, has_more

    def _build_common_params(self, max_cursor: int, count: int = None) -> dict:
        """构建通用参数"""
        return {
            "cursor": max_cursor,
            "count": count or APIConfig.DEFAULT_COUNT,
        }

    def _build_awemes_params(
        self, type: str, target_id: str, max_cursor: int, logid: str, filters: dict
    ) -> Tuple[str, dict, dict]:
        """
        构建作品列表请求参数

        Args:
            type: 采集类型
            target_id: 目标ID
            max_cursor: 游标位置
            logid: 日志ID
            filters: 过滤条件

        Returns:
            tuple: (uri, params, data)
        """
        data = {}

        if type == "post":
            uri = APIEndpoint.AWEME_POST
            params = {
                "publish_video_strategy_type": 2,
                "max_cursor": max_cursor,
                "locate_query": False,
                "show_live_replay_strategy": 1,
                "need_time_list": 0,
                "time_list_query": 0,
                "whale_cut_token": "",
                "count": APIConfig.DEFAULT_COUNT,
                "sec_user_id": target_id,
            }
        elif type == "favorite":
            uri = APIEndpoint.AWEME_FAVORITE
            params = {
                "sec_user_id": target_id,
                "max_cursor": max_cursor,
                "min_cursor": "0",
                "whale_cut_token": "",
                "cut_version": "1",
                "count": APIConfig.DEFAULT_COUNT,
                "publish_video_strategy_type": "2",
            }
        elif type == "collection":
            uri = APIEndpoint.AWEME_COLLECTION
            params = {
                "sec_user_id": target_id,
                "publish_video_strategy_type": 2,
            }
            data = self._build_common_params(max_cursor)
        elif type == "music":
            uri = APIEndpoint.MUSIC_AWEME
            params = {**self._build_common_params(max_cursor), "music_id": target_id}
        elif type == "hashtag":
            uri = APIEndpoint.CHALLENGE_AWEME
            params = {
                **self._build_common_params(max_cursor),
                "sort_type": 1,  # 0综合 1最热 2最新
                "ch_id": target_id,
            }
        elif type == "mix":
            uri = APIEndpoint.MIX_AWEME
            params = {**self._build_common_params(max_cursor), "mix_id": target_id}
        elif type == "search":
            uri = APIEndpoint.SEARCH_ITEM
            params = {
                "search_id": logid,
                "search_channel": "aweme_video_web",
                "search_source": "tab_search",
                "query_correct_type": 1,
                "from_group_id": "",
                "is_filter_search": 1,
                "list_type": "single",
                "need_filter_settings": 1,
                "offset": max_cursor,
                "sort_type": int(filters.get("sort_type", "0")),
                "enable_history": 1,
                "search_range": int(filters.get("search_range", "0")),
                "publish_time": int(filters.get("publish_time", "0")),
                "filter_duration": filters.get("filter_duration", ""),
                "count": APIConfig.DEFAULT_COUNT,
                "keyword": unquote(target_id),
            }
        elif type == "following":
            uri = APIEndpoint.USER_FOLLOWING
            params = {
                "sec_user_id": target_id,
                "offset": 0,
                "min_time": 0,
                "max_time": max_cursor,
                "count": APIConfig.FOLLOW_COUNT,
                "gps_access": 0,
                "is_top": 1,
            }
        elif type == "follower":
            uri = APIEndpoint.USER_FOLLOWER
            params = {
                "sec_user_id": target_id,
                "offset": 0,
                "min_time": 0,
                "max_time": max_cursor,
                "count": APIConfig.FOLLOW_COUNT,
                "gps_access": 0,
                "is_top": 1,
                "source_type": 3,  # 网页端默认排序 3最早/1最近/4综合
            }
        else:
            quit(f"不支持的采集类型: {type}")

        return uri, params, data
