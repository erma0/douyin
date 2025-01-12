from lib.request import Request
import pytest
# cookie = 'store-region=cn-sh; store-region-src=uid; LOGIN_STATUS=1; xgplayer_user_id=367931046110; bd_ticket_guard_client_web_domain=2; passport_assist_user=CjygedsOLgo0uHwp8as6-2i2l99KqLbwfwPiRJsCk8KmMY64vbjlYv7zvuqoxQlUtqRCeNMakE7O476AgpcaSgo8u4_8ftLvOMImhuqVwZO3JfN5mgZgvCfWibx0vBDNnIB0gpODa2rodH05QS23LrSpt7ibCE2lFMEnMD8tEJ2izg0Yia_WVCABIgEDcgJqiw%3D%3D; n_mh=1DH3rVcAItOwveDvL_n0OEgb207LQhJciUYaX6qd_lU; sso_uid_tt=5c92641c6f0d64f095211e1a46650309; sso_uid_tt_ss=5c92641c6f0d64f095211e1a46650309; toutiao_sso_user=a255c1c532b35ff242a02893eaf27ea6; toutiao_sso_user_ss=a255c1c532b35ff242a02893eaf27ea6; uid_tt=33577f9b341ec0acf09abdb39ba34c67; uid_tt_ss=33577f9b341ec0acf09abdb39ba34c67; sid_tt=f15f8f87871d5aa9b68dd7eb2f5e1d9d; sessionid=f15f8f87871d5aa9b68dd7eb2f5e1d9d; sessionid_ss=f15f8f87871d5aa9b68dd7eb2f5e1d9d; _bd_ticket_crypt_cookie=70476d7d16ef72b902b328f9a6ae0caf; my_rd=2; s_v_web_id=verify_lwbqdj6d_RCGjYjsX_kcNz_478q_AwHc_mXYxrJqpdSL3; sid_ucp_sso_v1=1.0.0-KDZiZmUyODY4N2IyYjVlNjhhZGRkM2QyMDJjNTIxYjEzNTU5MDRmNmIKHQihxs3k7wIQ2JahsgYY7zEgDDD9xfnXBTgGQPQHGgJobCIgYTI1NWMxYzUzMmIzNWZmMjQyYTAyODkzZWFmMjdlYTY; ssid_ucp_sso_v1=1.0.0-KDZiZmUyODY4N2IyYjVlNjhhZGRkM2QyMDJjNTIxYjEzNTU5MDRmNmIKHQihxs3k7wIQ2JahsgYY7zEgDDD9xfnXBTgGQPQHGgJobCIgYTI1NWMxYzUzMmIzNWZmMjQyYTAyODkzZWFmMjdlYTY; SEARCH_RESULT_LIST_TYPE=%22single%22; UIFID_TEMP=92637177d23c7380dffedc31a6ba68e4c4b48989c830706ec28d8dc2a6180493d4f8f912861b28b668e8364696defadac55e955b57487ade95982de4661c64cbbfd29b95e31a0c84c4f4025fa269dd7c; fpk1=U2FsdGVkX1+xDNr2uE+qoC55sTKoQ2i2xnHGBpAsNDEVZsugqByQ73Yk1fUtlrDtEbdC7pz0yhOQbBx1StJbzg==; fpk2=2c7cfdf77b39d40c83bf9879746da885; UIFID=92637177d23c7380dffedc31a6ba68e4c4b48989c830706ec28d8dc2a618049302647ab75eb956f915b078c50d10fb6abc0b5d1843b01eccbec99d2387250c01f850db1ccf7fb60a208be1c116bb726389febe6c7c291ebf63cc35aeb45811ea1ed683adbd0b838567ded29edbbe55b8a65806deec138cf1830e76adeac2dd40e1645452fd8fb8b38725c30c4449ba540371ce6433d63a7d122a779fb5d6d898; passport_csrf_token=8a609aa823113643ad802a9833e8bf49; passport_csrf_token_default=8a609aa823113643ad802a9833e8bf49; ttwid=1%7C-exW172RboiVv9sOto_GaDoGvc92RU459ApQbJXTogM%7C1719991220%7Cf6b802c5036fae7e93e4f4419552220b9b13f33af716109ab459427f0e0d2ba7; sid_guard=f15f8f87871d5aa9b68dd7eb2f5e1d9d%7C1720084395%7C5184000%7CMon%2C+02-Sep-2024+09%3A13%3A15+GMT; sid_ucp_v1=1.0.0-KDg1ZGNhYTA0N2IyNWY4OTM2Njk3MTY1YzA5OTNmNmI3YTYyNWNjYzMKGQihxs3k7wIQq8-ZtAYY7zEgDDgGQPQHSAQaAmhsIiBmMTVmOGY4Nzg3MWQ1YWE5YjY4ZGQ3ZWIyZjVlMWQ5ZA; ssid_ucp_v1=1.0.0-KDg1ZGNhYTA0N2IyNWY4OTM2Njk3MTY1YzA5OTNmNmI3YTYyNWNjYzMKGQihxs3k7wIQq8-ZtAYY7zEgDDgGQPQHSAQaAmhsIiBmMTVmOGY4Nzg3MWQ1YWE5YjY4ZGQ3ZWIyZjVlMWQ5ZA; MONITOR_WEB_ID=0f81696b-2d23-4460-b5f9-aa9110fec8f9; dy_swidth=1536; dy_sheight=864; __live_version__=%221.1.2.1533%22; live_use_vvc=%22false%22; pwa2=%220%7C0%7C3%7C0%22; download_guide=%223%2F20240710%2F0%22; publish_badge_show_info=%221%2C0%2C0%2C1720600417369%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Afalse%2C%22volume%22%3A0.995%7D; WallpaperGuide=%7B%22showTime%22%3A1721029294626%2C%22closeTime%22%3A0%2C%22showCount%22%3A4%2C%22cursor1%22%3A63%2C%22cursor2%22%3A0%2C%22hoverTime%22%3A1720167694867%7D; strategyABtestKey=%221721088679.595%22; odin_tt=08715f263a7cd241d5b53ec99becde78617d57726332bbb6f0f030208b9ff96e57a19d3fcc45271f20925982017e9488; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAAl7TJWjJJrnu11IlllB6Mi5V9VbAsQo1N987guPjctc8%2F1721145600000%2F0%2F0%2F1721092627181%22; __ac_nonce=06695cd0200a47fdb3031; __ac_signature=_02B4Z6wo00f01oS6GVgAAIDBuRMDxa6xpQaEmh3AAMfHBlAUY9Kj9s8vgsHlo86YMwE-Il3VwfP4laBMD7o.4lmpmdWcxghE1RExcAeNd9Zc.aJQZHeZO59Y8ElX7-0ch0m951oUuwpKi7Ea2f; douyin.com; xg_device_score=6.905294117647059; device_web_cpu_core=4; device_web_memory_size=8; architecture=amd64; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1536%2C%5C%22screen_height%5C%22%3A864%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A4%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A3.75%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; csrf_session_id=b545fa6fb038cbe46156f4e264502c0b; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAAl7TJWjJJrnu11IlllB6Mi5V9VbAsQo1N987guPjctc8%2F1721145600000%2F0%2F1721093380947%2F0%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCSlcyRi9qYmJldExTNTlSQ2ZxdUwyL0RpQUE3eFdvQ3NlTnN4clJndVlLL1BmTVAvN2JTaWRTMEpQWnBwbGdVTWhLdVEzRHd3eU1NSHlpZXMzQzNjOVk9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A0%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A1%7D%22; home_can_add_dy_2_desktop=%221%22; biz_trace_id=04467289; IsDouyinActive=false; passport_fe_beating_status=false'
# ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36'
# r = Request(cookie, UA=ua)
r = Request()


def get_aweme_detail(id='7379453318386437428') -> tuple[dict, bool]:
    params = {"aweme_id": id}
    uri = '/aweme/v1/web/aweme/detail/'
    resp = r.getJSON(uri, params)
    aweme_detail = resp.get('aweme_detail')
    return aweme_detail


def get_hash_detail(id='1749186610476046'):
    params = {"ch_id": id, "query_type": 0}
    uri = '/aweme/v1/web/challenge/detail/'
    resp = r.getJSON(uri, params)
    ch_info = resp.get('ch_info')
    return ch_info


def request_search(keyword: str = '抖音', max_cursor: int = 0, limit: int = 10) -> tuple[dict, bool]:
    """
    请求抖音获取搜索信息
    """
    params = {
        "search_id": '',
        "search_channel": "aweme_video_web",
        "search_source": "tab_search",
        "query_correct_type": 1,
        "from_group_id": "",
        "is_filter_search": 1,
        "list_type": "single",
        "need_filter_settings": 1,
        "offset": max_cursor,
        "sort_type": 1,  # 排序 综合 1最多点赞 2最新
        "enable_history": 1,
        "search_range": 0,  # 搜索范围  不限
        "publish_time": 0,  # 发布时间  不限
        "filter_duration": '',  # 时长 不限 0-1  1-5  5-10000
        'count': 18,
        "keyword": keyword
    }
    resp = r.getJSON('/aweme/v1/web/search/item/', params)
    ret = resp.get('data')
    return ret


def request_search_user(keyword: str = '新华社', max_cursor: int = 0, limit: int = 10) -> tuple[dict, bool]:
    """
    请求抖音获取搜索信息
    """
    params = {
        'count': 10,
        "from_group_id": "",
        "is_filter_search": 0,
        "keyword": keyword,
        "list_type": "single",
        "need_filter_settings": 0,
        "offset": max_cursor,
        # "search_id": '',
        "query_correct_type": 1,
        "search_channel": "aweme_user_web",
        "search_source": "tab_search"
    }
    resp = r.getJSON('/aweme/v1/web/discover/search/', params)
    ret = resp.get('user_list')
    return ret


@pytest.mark.parametrize('function', [get_aweme_detail, get_hash_detail, request_search, request_search_user])
def test_request(function):
    assert function()


def test_getHTML():
    assert r.getHTML('https://v.douyin.com/UhYnoMS/')
