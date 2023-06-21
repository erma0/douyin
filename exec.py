# -*- encoding: utf-8 -*-
'''
@File    :   exec.py
@Time    :   2023年06月19日 20:29:33 星期一
@Author  :   erma0
@Version :   1.0
@Link    :   https://erma0.cn
@Desc    :   抖音爬虫命令行
'''

import os

import click
from loguru import logger

from browser import Browser
from spider import Douyin


@click.command()
@click.option('-u', '--urls', type=click.STRING, multiple=True, help='账号/话题/音乐等URL或文件路径（文件格式为一行一个URL），支持多次输入。采集本账号喜欢/收藏时无需输入')
@click.option('-n', '--num', default=-1, help='选填。最大采集数量，默认不限制')
@click.option('-g', '--grab', is_flag=True, help='选填。只采集信息，不下载作品')
@click.option('-d', '--download', is_flag=True, help='选填。不采集，直接下载之前采集过的配置文件，用于下载失败时重试')
@click.option('-l', '--login', default=True, is_flag=True, help='选填。指定是否登录，默认要登录，可避免一些风控，采集关注粉丝等信息时必须登录')
@click.option('-m', '--mstoken', default=False, is_flag=True, help='选填。指定是否在下载配置文件中设置UA及mstoken，默认不需要，出现下载0kb时尝试使用此参数')
@click.option('-h', '--headless', default=True, is_flag=True, help='选填。指定是否使用headless模式（不显示浏览器界面），默认为True，出现问题时使用此参数以便观察')
@click.option('-t',
              '--type',
              type=click.Choice(['post', 'like', 'music', 'search', 'follow', 'fans', 'collection', 'video', 'favorite'],
                                case_sensitive=False),
              default='post',
              help='选填。采集类型，支持[主页作品/喜欢/音乐/搜索/关注/粉丝/合集/单作品/收藏]，默认采集post作品，能够自动识别搜索/音乐/合集/单作品以及本账号的喜欢/收藏。')
@click.option('-b',
              '--browser',
              type=click.Choice(["chrome", "msedge", "chrome-beta", "msedge-beta", "msedge-dev"], case_sensitive=False),
              default='msedge',
              help='选填。浏览器类型，默认使用稳定版EDGE，可选[chrome/msedge]以及beta或dev版本，如需使用Firefox或WebKit请自行修改browser文件')
@click.option('-p', '--path', type=click.STRING, default='下载', help='选填。下载文件夹，默认为[下载]')
@click.option('-pt',
              '--pathtype',
              type=click.Choice(["id", "title"], case_sensitive=False),
              default='id',
              help='选填。文件夹命名格式，默认为[type]_[id]，可选[title]（不需要主页作品增量采集时建议填title，即使用[标题/昵称/关键词]来命名）')
def main(urls, num, grab, download, login, mstoken, headless, type, browser, path, pathtype):
    """
    命令行
    """

    if not urls:  # 未输入目标地址
        if type in ['like', 'favorite', 'follow', 'fans']:  # 采集本账号
            edge = Browser(channel=browser, headless=headless)
            start(edge.context, urls, num, grab, download, type, path, pathtype, mstoken)
            edge.stop()
            return
        elif type in ['post', 'music', 'search', 'collection', 'video']:  # 自动识别类型
            urls = (input('目标URL或文件路径：'), )
        else:
            print('请输入目标URL或文件路径')
            return

    edge = Browser(channel=browser, need_login=login, headless=headless)

    for url in urls:
        if os.path.exists(url):  # 文件路径
            with open(url, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if lines:
                for line in lines:
                    start(edge.context, line, num, grab, download, type, path, pathtype, mstoken)
            else:
                logger.error(f'[{url}]中没有发现目标URL')
        else:
            start(edge.context, url, num, grab, download, type, path, pathtype, mstoken)
    edge.stop()


def start(context, url, num, grab, download, type, path, pathtype, mstoken):
    a = Douyin(context, url, num, type, path, pathtype, mstoken)

    if download:  # 不需要新采集
        a.has_more = False
    a.run()

    if grab or type in ['follow', 'fans']:  # 不需要下载
        return
    a.download()


if __name__ == "__main__":
    main()
