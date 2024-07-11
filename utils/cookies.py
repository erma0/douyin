import os

import requests
import ujson as json
from loguru import logger

from utils.util import save_json


def get_cookie() -> dict:
    if os.path.exists('config/cookie.json'):
        with open('config/cookie.json', 'r', encoding='utf-8') as f:
            cookie = json.load(f)
    elif os.path.exists('config/cookie.txt'):
        with open('config/cookie.txt', 'r', encoding='utf-8') as f:
            cookie = cookies_to_dict(f.read())
    else:
        cookie = cookies_to_dict(input('请输入cookie:'))
        save_cookie(cookie)
    return cookie


def save_cookie(cookie: dict):
    save_json('config/cookie', cookie)


def test_cookie(cookie):
    url = 'https://sso.douyin.com/check_login/'
    if type(cookie) is dict:
        cookie_dict = cookie
    elif type(cookie) is str:
        cookie_dict = cookies_to_dict(cookie)

    res = requests.get(url, cookies=cookie_dict).json()
    if res['has_login'] is True:
        logger.success('cookie已登录')
        return True
    else:
        logger.error('cookie未登录')
        return False


def cookies_to_dict(cookie_string: str) -> dict:
    cookies = cookie_string.strip().split('; ')
    cookie_dict = {}
    for cookie in cookies:
        if cookie == '' or cookie == 'douyin.com':
            continue
        key, value = cookie.split('=', 1)
        cookie_dict[key] = value
    return cookie_dict


if __name__ == "__main__":
    save_json('edge_cookie', get_cookie())
    # save_json('dict_cookie', cookies_to_dict(x))
