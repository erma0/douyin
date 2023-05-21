# -*- encoding: utf-8 -*-
'''
@File    :   exec.py
@Time    :   2023年05月18日 19:33:32 星期四
@Author  :   erma0
@Version :   1.0
@Link    :   https://erma0.cn
@Desc    :   命令行
'''

import os

import click
from loguru import logger

from browser import Browser
from spider import Douyin


@click.command()
@click.option('-u', '--urls', type=click.STRING, multiple=True, help='必填。账号/话题/音乐的URL或文件路径（文件格式为一行一个URL），支持多次输入')
@click.option('-n', '--num', default=-1, help='选填。最大采集数量，默认不限制')
@click.option('-g', '--grab', is_flag=True, help='选填。只采集信息，不下载作品')
@click.option('-d', '--download', is_flag=True, help='选填。直接下载采集完成的配置文件，用于采集时下载失败后重试')
@click.option('-l', '--login', default=True, is_flag=True, help='选填。指定是否需要登录，默认要登录，用于采集主页作品、关注粉丝列表以及本人私密账号的信息，也可避免一些莫名其妙的风控')
@click.option('-t',
              '--type',
              type=click.Choice(['post', 'like', 'music', 'search', 'follow', 'fans', 'collection', 'video'],
                                case_sensitive=False),
              default='post',
              help='选填。采集类型，支持[主页作品/喜欢/音乐/搜索/关注/粉丝/合集/单作品]，默认采集post作品，能够自动识别搜索/音乐/合集/单作品。采集账号主页作品或私密账号喜欢作品必须登录。')
@click.option('-b',
              '--browser',
              type=click.Choice(["chrome", "msedge", "chrome-beta", "msedge-beta", "msedge-dev"], case_sensitive=False),
              default='msedge',
              help='选填。浏览器类型，默认使用稳定版EDGE，可选[chrome/msedge]，如需使用Firefox或WebKit请自行修改Browser')
def main(urls, num, grab, download, login, type, browser):
    """
    命令行
    """
    edge = Browser(channel=browser, need_login=login)

    if not urls:
        urls = (input('目标URL或文件路径：'), )
    for url in urls:
        if os.path.exists(url):  # 文件路径
            with open(url, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if lines:
                for line in lines:
                    start(line, num, grab, download, type)
            else:
                logger.error(f'[{url}]中没有发现目标URL')
        else:
            start(url, num, grab, download, type)
    edge.stop()


def start(url, num, grab, download, type):
    a = Douyin(url, num, type)
    if not download:  # 需要新采集
        a.run()
    if grab or type in ['follow', 'fans']:  # 不需要下载
        return
    else:
        a.download()


if __name__ == "__main__":
    main()
