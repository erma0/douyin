import os

import requests
import ujson as json
from loguru import logger


def str_to_path(text):
    """
    把字符串转为Windows合法文件名

    Args:
        text: 输入字符串，可以是 str 或 None

    Returns:
        处理后的合法文件名字符串
    """
    # 处理 None 或空值
    if text is None or text == "":
        return ""

    # 确保是字符串类型
    if not isinstance(text, str):
        text = str(text)

    # 只替换 Windows 文件名真正不支持的字符，保留 # 和 emoji
    illegal_chars = ["\r", "\n", "\\", "/", ":", "*", "?", '"', "<", ">", "|"]

    # 替换非法字符
    for char in illegal_chars:
        text = text.replace(char, "_")

    # 文件名+路径长度最大255，汉字*2，取80
    if len(text) > 80:
        text = text[:80]

    return text.strip()


def quit(str: str = ""):
    """
    抛出异常而不是退出程序（适用于GUI应用）
    """
    if str:
        logger.error(str)
    raise Exception(str if str else "程序异常退出")


def url_redirect(url):
    r = requests.head(url, allow_redirects=False)
    u = r.headers.get("Location", url)
    return u


def save_json(filename: str, data):
    path = os.path.dirname(filename)
    if path:
        os.makedirs(path, exist_ok=True)

    with open(f"{filename}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
