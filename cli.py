# -*- encoding: utf-8 -*-
'''
@File    :   cli.py
@Time    :   2024年07月16日 12:05:55 星期二
@Author  :   erma0
@Version :   1.0
@Link    :   https://github.com/erma0
@Desc    :   命令行
'''

import os

import click
from loguru import logger

from lib.douyin import Douyin


version = 'V4.250113'
banner = rf'''
 ____                    _         ____        _     _
|  _ \  ___  _   _ _   _(_)_ __   / ___| _ __ (_) __| | ___ _ __
| | | |/ _ \| | | | | | | | '_ \  \___ \| '_ \| |/ _` |/ _ \ '__|
| |_| | (_) | |_| | |_| | | | | |  ___) | |_) | | (_| |  __/ |
|____/ \___/ \__,_|\__, |_|_| |_| |____/| .__/|_|\__,_|\___|_|
                    |___/                |_|
                            {version}
                Github: https://github.com/erma0/douyin
'''
print(banner)


@click.command()
@click.option('-u', '--urls', type=click.STRING, multiple=True, help='作品/账号/话题/音乐等类型的URL链接/ID或搜索关键词，也可输入文件路径（文件内一行一个），可多次输入。')
@click.option('-l', '--limit', type=click.INT, default=0, help='选填。限制最大采集数量，默认不限制')
@click.option('-d', '--download', is_flag=True, help='选填。不需要下载时使用此参数，默认自动下载')
@click.option('-t', '--type',
              type=click.Choice(['post', 'like', 'music', 'hashtag', 'search', 'follow', 'fans', 'collection', 'favorite', 'video', 'note', 'user', 'live'],
                                case_sensitive=False),
              default='post',
              help='选填。采集类型，默认采集post作品，支持[主页作品/喜欢/音乐/话题/搜索（用户/视频/直播）/关注/粉丝/合集/收藏/视频/图文]，输入URL链接时能够自动识别部分类型。')
@click.option('-p', '--path', type=click.STRING, default='下载', help='选填。下载文件夹，默认为[下载]')
@click.option('-c', '--cookie', type=click.STRING, help='选填。已登录账号的cookie，可以直接填在config/cookie.txt文件中，也可在运行时手动输入，也可输入[edge/chrome]将会自动从本地浏览器读取cookie')
def main(urls, limit, download, type, path, cookie):
    if not urls:  # 未输入目标
        if type in ['like', 'favorite', 'follow', 'fans']:
            # 直接采集本账号
            start(urls, limit, download, type, path, cookie)
            return
        else:
            # 提示输入目标关键词/URL链接/ID或文件路径
            # 未指定类型时，部分链接可根据输入的URL自动识别类型
            urls = (input(f'采集类型：{type}，请输入目标关键词/URL链接/ID或文件路径：'), )
    for url in urls:
        if os.path.exists(url):  # 文件路径
            with open(url, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if lines:
                for line in lines:
                    start(line, limit, download, type, path, cookie)
            else:
                logger.error(f'[{url}]中没有发现目标URL')
        else:
            start(url, limit, download, type, path, cookie)


def start(url, limit, download, type, path, cookie):
    a = Douyin(url, limit, type, path, cookie)
    a.run()

    if download or a.type in ['user', 'follow', 'fans', 'live']:
        logger.info('不需要下载')
        return
    a.download_all()


if __name__ == "__main__":
    main()
