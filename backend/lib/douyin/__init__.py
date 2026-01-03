# -*- encoding: utf-8 -*-
"""
抖音爬虫模块

提供完整的抖音数据采集功能，支持多种采集类型。

核心类：
    Douyin: 爬虫主类，提供统一的采集接口

支持的采集类型：
    - aweme: 单个作品
    - post: 用户主页作品
    - favorite: 用户喜欢
    - collection: 用户收藏
    - music: 音乐作品
    - hashtag: 话题作品
    - mix: 合集作品
    - search: 关键词搜索
    - following: 关注列表
    - follower: 粉丝列表

使用示例：
    from backend.lib.douyin import Douyin

    # 采集用户作品
    douyin = Douyin(
        target="https://www.douyin.com/user/xxx",
        limit=10,
        type="post",
        cookie="your_cookie"
    )
    douyin.run()

    # 使用回调函数实时处理数据
    def handle_new_items(items, item_type):
        print(f"收到 {len(items)} 条新数据")

    douyin = Douyin(
        target="搜索关键词",
        type="search",
        on_new_items=handle_new_items
    )
    douyin.run()

模块结构：
    - crawler.py: 爬虫主类，协调各模块完成数据采集
    - client.py: API客户端，封装抖音API调用
    - parser.py: 数据解析器，解析API返回的数据
    - target.py: 目标处理器，识别和解析用户输入
    - types.py: 类型定义和常量（作品类型、API端点、请求参数等）
    - request.py: HTTP请求封装，处理签名和Cookie
    - js/: JavaScript脚本（签名生成）
"""

from .crawler import Douyin

__all__ = ["Douyin"]
