# -*- encoding: utf-8 -*-
'''
@File    :   request.py
@Time    :   2024年07月08日 17:46:37 星期一
@Author  :   ShilongLee
@Version :   1.0
@Link    :   https://github.com/ShilongLee/Crawler
@Desc    :   抖音sign
'''
import os
import re
from urllib.parse import quote

import requests
from loguru import logger

from utils.cookies import cookies_to_dict, get_cookie
from utils.execjs_fix import execjs


class Request(object):

    def __init__(self, cookie=''):
        if cookie:
            cookie = cookies_to_dict(cookie)
        else:
            cookie = get_cookie()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "sec-ch-ua-platform": "Windows",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            "referer": "https://www.douyin.com/?recommend=1",
            "priority": "u=1, i",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "accept": "application/json, text/plain, */*",
            "dnt": "1",
        }

        self.http = requests.Session()
        self.http.headers.clear()
        self.http.cookies.clear()
        self.http.headers.update(headers)
        self.http.cookies.update(cookie)

    def request(self, uri: str, params: dict, data: dict = None):
        HOST = 'https://www.douyin.com'
        url = f'{HOST}{uri}'

        params = self.get_params(params)
        params["a_bogus"] = self.get_sign(uri, params)

        # logger.info(f'url: {url}, params={params}')
        if data:
            response = self.http.post(url, params=params, data=data)
        else:
            response = self.http.get(url, params=params)

        if response.status_code != 200 or response.text == '' or response.json().get('status_code', 0) != 0:
            logger.error(
                f'请求失败：url: {url},  params: {params}, code: {response.status_code}, body: {response.text}')
            if os.path.exists('cookie.json'):
                os.remove('cookie.json')
            return {}, False

        return response.json(), True

    def get_sign(self, uri: str, params: dict) -> dict:
        query = '&'.join([f'{k}={quote(str(v))}' for k, v in params.items()])
        file = os.path.join(os.path.dirname(__file__), '../lib/douyin.js')
        DOUYIN_SIGN = execjs.compile(
            open(file, 'r', encoding='utf-8').read())

        call_name = 'sign_datail'
        if 'reply' in uri:
            call_name = 'sign_reply'
        a_bogus = DOUYIN_SIGN.call(
            call_name, query, self.http.headers.get("User-Agent"))
        return a_bogus

    def get_params(self, params: dict) -> dict:
        COMMON_PARAMS = {
            'device_platform': 'webapp',
            'aid': '6383',
            'channel': 'channel_pc_web',
            'update_version_code': '170400',
            'pc_client_type': '1',  # Windows
            'version_code': '190500',
            'version_name': '19.5.0',
            'cookie_enabled': 'true',
            'screen_width': '2560',  # from cookie dy_swidth
            'screen_height': '1440',  # from cookie dy_sheight
            'browser_language': 'zh-CN',
            'browser_platform': 'Win32',
            'browser_name': 'Chrome',
            'browser_version': '126.0.0.0',
            'browser_online': 'true',
            'engine_name': 'Blink',
            'engine_version': '126.0.0.0',
            'os_name': 'Windows',
            'os_version': '10',
            'cpu_core_num': '24',   # device_web_cpu_core
            'device_memory': '8',   # device_web_memory_size
            'platform': 'PC',
            'downlink': '10',
            'effective_type': '4g',
            'round_trip_time': '50',
            # 'webid': '',   # from doc
            # 'verifyFp': '',   # from cookie s_v_web_id
            # 'fp': '', # from cookie s_v_web_id
            # 'msToken': '',  # from cookie msToken
            # 'a_bogus': '' # sign
        }
        params.update(COMMON_PARAMS)

        cookie = self.http.cookies.get_dict()
        params['msToken'] = cookie.get('msToken', None)
        params['screen_width'] = cookie.get('dy_swidth', 2560)
        params['screen_height'] = cookie.get('dy_sheight', 1440)
        params['cpu_core_num'] = cookie.get('device_web_cpu_core', 24)
        params['device_memory'] = cookie.get('device_web_memory_size', 8)
        params['verifyFp'] = cookie.get('s_v_web_id', None)
        params['fp'] = cookie.get('s_v_web_id', None)
        params['webid'] = self.get_webid()
        return params

    def get_webid(self):
        url = 'https://www.douyin.com/?recommend=1'
        response = self.http.get(url)
        if response.status_code != 200 or response.text == '':
            logger.error(f'请求失败, url: {url}')
            return None
        pattern = r'"user_unique_id\\":\\"(\d+)\\"'
        match = re.search(pattern, response.text)
        if match:
            return match.group(1)
        return None


if __name__ == "__main__":
    r = Request()
    print(r.get_webid())
