
import os
import requests
import ujson as json
from loguru import logger


def str_to_path(str: str):
    """
    把字符串转为Windows合法文件名
    """
    # 非法字符
    lst = ['\r', '\n', '\\', '/', ':', '*', '?', '"', '<', '>', '|']
    # lst.extend([' ', '^'])
    # 字符处理方式1
    for key in lst:
        str = str.replace(key, '_')
    # 字符处理方式2
    # str = str.translate(None, ''.join(lst))
    # 文件名+路径长度最大255，汉字*2，取80
    if len(str) > 80:
        str = str[:80]
    return str.strip()


def quit(str: str = ''):
    """
    直接退出程序
    """
    if str:
        logger.error(str)
    exit()


def url_redirect(url):
    r = requests.head(url, allow_redirects=False)
    u = r.headers.get('Location', url)
    return u


def save_json(filename: str, data):
    path = os.path.dirname(filename)
    if path:
        os.makedirs(path, exist_ok=True)

    with open(f'{filename}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
