# -*- coding: utf-8 -*-
"""抖音爬虫核心功能测试"""

import pytest

from backend.lib.douyin import Douyin


@pytest.mark.network
def test_init_with_url():
    """测试URL初始化"""
    d = Douyin(target="https://v.douyin.com/UhYnoMS/")
    d.get_target_id()
    assert d.id == "7235055125771898149"


@pytest.mark.network
def test_init_with_id():
    """测试ID初始化"""
    d = Douyin(target="7235055125771898149",
               type="aweme")
    d.get_target_id()
    assert d.id == "7235055125771898149"


@pytest.mark.network
@pytest.mark.cookie
def test_video_by_url(settings_cookie):
    """测试视频链接采集"""
    d = Douyin(target="https://v.douyin.com/UhYnoMS/", cookie=settings_cookie)
    d.run()
    assert len(d.results) > 0


@pytest.mark.network
@pytest.mark.cookie
def test_video_by_id(settings_cookie):
    """测试视频ID采集"""
    d = Douyin(target="7235055125771898149",
               type="aweme", cookie=settings_cookie)
    d.run()
    assert len(d.results) > 0


@pytest.mark.network
@pytest.mark.cookie
def test_user_post(settings_cookie):
    """测试用户作品采集"""
    d = Douyin(target="https://v.douyin.com/iSNbMea7/",
               limit=18, cookie=settings_cookie)
    d.run()
    assert len(d.results) > 0


@pytest.mark.network
@pytest.mark.cookie
def test_user_like(settings_cookie):
    """测试用户喜欢采集"""
    d = Douyin(target="https://v.douyin.com/e2BkGS7/",
               type="favorite",
               limit=18, cookie=settings_cookie)
    d.run()
    assert len(d.results) > 0


@pytest.mark.network
@pytest.mark.cookie
def test_user_collection(settings_cookie):
    """测试用户收藏采集"""
    d = Douyin(type="collection", limit=18, cookie=settings_cookie)
    d.run()
    assert len(d.results) > 0


@pytest.mark.network
@pytest.mark.cookie
def test_mix(settings_cookie):
    """测试合集采集"""
    d = Douyin(
        target="https://www.douyin.com/collection/7018087406876231711",
        limit=18,
        cookie=settings_cookie
    )
    d.run()
    assert len(d.results) > 0


@pytest.mark.network
@pytest.mark.cookie
def test_music(settings_cookie):
    """测试音乐采集"""
    d = Douyin(
        target="https://www.douyin.com/music/6958014354780359461",
        type="music",
        limit=18,
        cookie=settings_cookie
    )
    d.run()
    assert len(d.results) > 0


@pytest.mark.network
@pytest.mark.cookie
def test_challenge(settings_cookie):
    """测试话题挑战采集"""
    d = Douyin(
        target="https://v.douyin.com/eOsR0vbqrp0/",
        type="hashtag",
        limit=18,
        cookie=settings_cookie
    )
    d.run()
    assert len(d.results) > 0


@pytest.mark.network
@pytest.mark.cookie
def test_search(settings_cookie):
    """测试搜索采集"""
    d = Douyin(
        target="美食",
        type="search",
        limit=18,
        cookie=settings_cookie
    )
    d.run()
    assert len(d.results) > 0


@pytest.mark.network
@pytest.mark.cookie
def test_user_following(settings_cookie):
    """测试用户关注列表采集"""
    d = Douyin(
        type="following",
        limit=60,
        cookie=settings_cookie
    )
    d.run()
    assert len(d.results) > 0


@pytest.mark.network
@pytest.mark.cookie
def test_user_follower(settings_cookie):
    """测试用户粉丝列表采集"""
    d = Douyin(
        target="MS4wLjABAAAAGa0vp7T68ZdsevlrlBuZ3hXxhcbF2PRemtcT_mrmQLA",
        type="follower",
        limit=40,
        cookie=settings_cookie
    )
    d.run()
    assert len(d.results) > 0
