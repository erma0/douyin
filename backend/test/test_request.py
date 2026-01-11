from backend.lib.douyin.request import Request
import pytest


@pytest.fixture
def request_client(settings_cookie):
    """创建请求客户端实例的fixture"""
    return Request(cookie=settings_cookie)


class TestRequest:
    """测试请求功能"""

    def test_get_aweme_detail(self, request_client):
        """测试获取作品详情"""
        params = {"aweme_id": "7235055125771898149"}
        uri = "/aweme/v1/web/aweme/detail/"
        resp = request_client.getJSON(uri, params)
        aweme_detail = resp.get("aweme_detail")
        assert aweme_detail is not None

    def test_get_hash_detail(self, request_client):
        """测试获取话题详情"""
        params = {"ch_id": "1749186610476046", "query_type": 0}
        uri = "/aweme/v1/web/challenge/detail/"
        resp = request_client.getJSON(uri, params)
        ch_info = resp.get("ch_info")
        assert ch_info is not None

    def test_request_search(self, request_client):
        """测试搜索功能"""
        params = {
            "search_id": "",
            "search_channel": "aweme_video_web",
            "search_source": "tab_search",
            "query_correct_type": 1,
            "from_group_id": "",
            "is_filter_search": 1,
            "list_type": "single",
            "need_filter_settings": 1,
            "offset": 0,
            "sort_type": 1,  # 排序 综合 1最多点赞 2最新
            "enable_history": 1,
            "search_range": 0,  # 搜索范围  不限
            "publish_time": 0,  # 发布时间  不限
            "filter_duration": "",  # 时长 不限 0-1  1-5  5-10000
            "count": 18,  # 限制采集数量为18
            "keyword": "抖音",
        }
        resp = request_client.getJSON("/aweme/v1/web/search/item/", params)
        ret = resp.get("data")
        assert ret is not None

    def test_request_search_user(self, request_client):
        """测试搜索用户功能"""
        params = {
            "count": 18,  # 限制采集数量为18
            "from_group_id": "",
            "is_filter_search": 0,
            "keyword": "新华社",
            "list_type": "single",
            "need_filter_settings": 0,
            "offset": 0,
            "query_correct_type": 1,
            "search_channel": "aweme_user_web",
            "search_source": "tab_search",
        }
        resp = request_client.getJSON("/aweme/v1/web/discover/search/", params)
        ret = resp.get("user_list")
        assert ret is not None

    def test_getHTML(self, request_client):
        """测试获取HTML内容"""
        html = request_client.getHTML("https://v.douyin.com/UhYnoMS/")
        assert html is not None
        assert len(html) > 0
