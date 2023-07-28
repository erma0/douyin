# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Time    :   2023年07月28日 10:30:34 星期六
@Author  :   erma0
@Version :   1.0
@Link    :   https://erma0.cn
@Desc    :   抖音主页作品采集
'''

import os
import subprocess
from sys import exit
from threading import Lock
from typing import List
from urllib.parse import urlparse

import click
import requests
import ujson as json
from loguru import logger


class Douyin(object):

    def __init__(self, target: str, limit: int = -1, sessionid: str = ''):
        """
        初始化信息
        """
        self.num = limit
        self.http = requests.Session()
        self.http.headers.clear()
        self.http.headers.update({
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
        })
        self.down_path = os.path.join('.', '下载')
        if not os.path.exists(self.down_path): os.makedirs(self.down_path)
        self.results_old = []  # 前一次保存结果
        self.has_more = True
        self.msToken = False
        self.results = []
        self.lock = Lock()
        self.cookie = 'sessionid=' + sessionid if sessionid else sessionid
        if not self.test_cookie():
            # self.verify()
            self.quit()

        self.url2uid(target)
        self.get_user_info()

    @staticmethod
    def str2path(str: str):
        """
        把字符串转为Windows合法文件名
        """
        # 非法字符
        lst = ['\r', '\n', '\\', '/', ':', '*', '?', '"', '<', '>', '|']
        # lst = ['\r', '\n', '\\', '/', ':', '*', '?', '"', '<', '>', '|', ' ', '^']
        # 非法字符处理方式1
        for key in lst:
            str = str.replace(key, '_')
        # 非法字符处理方式2
        # str = str.translate(None, ''.join(lst))
        # 文件名+路径长度最大255，汉字*2，取80
        if len(str) > 80:
            str = str[:80]
        return str.strip()

    @staticmethod
    def quit(str: str = ''):
        """
        直接退出程序
        """
        if str:
            logger.error(str)
        exit()

    def url2uid(self, url: str):
        """
        取uid
        """
        url = url.strip()
        hostname = urlparse(url).hostname
        if hostname and hostname.endswith('douyin.com'):  # 链接
            if hostname == 'v.douyin.com':
                r = self.http.head(url, allow_redirects=False)
                self.url = r.headers.get('Location', url)
            else:
                self.url = url
        else:  # uid
            self.url = f'https://www.douyin.com/user/{url}'
        self.uid = urlparse(self.url).path.strip('/').split('/')[-1]
        return self.uid

    def test_cookie(self, cookie=''):
        """
        测试cookie有效性
        """
        if cookie:
            self.cookie = cookie
        elif os.path.isfile('./verify'):
            with open('./verify', 'r', encoding='utf-8') as f:
                self.cookie = f.read()

        if not self.cookie:
            logger.error('cookie为空')
            return False

        cookie_dict = dict([ck.split('=', 1) for ck in self.cookie.replace(' ', '').split(';')])
        self.http.cookies = requests.utils.cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True)
        res = self.http.get('https://www.douyin.com/aweme/v1/web/aweme/post/', stream=True).headers  # 检测cookie是否有效
        if int(res['Content-Length']) > 0:  # cookie未过期
            logger.success('cookie验证成功')
            return True
        else:
            logger.error('cookie验证失败')
            return False

    def verify(self):
        """
        手动取cookie
        """
        pass

    def get_user_info(self):
        """
        取目标信息
        查询结果在 self.info
        """
        url = f'https://www.douyin.com/web/api/v2/user/info/?sec_uid={self.uid}'
        try:
            res = self.http.get(url).json()
            self.info = res['user_info']
            # 下载路径
            self.down_path = os.path.join(self.down_path, self.str2path(f"{self.info['nickname']}_{self.uid}"))
            self.aria2_conf = f'{self.down_path}.txt'
            if os.path.exists(f'{self.down_path}.json') and not self.results_old:
                with open(f'{self.down_path}.json', 'r', encoding='utf-8') as f:
                    self.results_old = json.load(f)
        except:
            self.quit('目标解析失败，程序退出。')

    def crawl(self):
        """
        采集用户作品/喜欢
        """
        cursor = 0
        retry = 0
        max_retry = 10

        # https://www.douyin.com/aweme/v1/web/aweme/post/?aid=6383&sec_user_id=-&count=50&max_cursor=0
        url = 'https://www.douyin.com/aweme/v1/web/aweme/post/'

        while self.has_more:
            params = {'aid': 6383, 'sec_user_id': self.uid, "count": 50, 'max_cursor': cursor}
            try:
                res = self.http.get(url, params=params)
                resj = res.json()
                cursor = resj.get('max_cursor')
                self.has_more = resj.get('has_more')
                aweme_list = resj.get('aweme_list')
            except:
                retry += 1
                logger.error(f'采集请求出错... 进行第{retry}次重试')
                break
            finally:
                # 默认重试max_retry次
                if retry >= max_retry:
                    self.has_more = False

            if aweme_list:
                self._append_awemes(aweme_list)
                if retry: retry = 0  # 请求成功后重置重试次数
            elif self.has_more:
                retry += 1
                # logger.error(f'采集未完成，但请求结果为空... 进行第{retry}次重试')
            else:
                # logger.info('未采集到结果')
                pass

        if self.results:
            logger.success(f'采集完成，本次共采集到{len(self.results)}条结果')
            self.save()
        else:
            logger.info("本次采集结果为空")

    def _append_awemes(self, aweme_list: List[dict]):
        """
        数据入库
        """
        with self.lock:  # 加锁避免意外冲突
            if self.num < 0 or len(self.results) < self.num:
                for item in aweme_list:
                    # =====限制数量=====
                    if self.num > 0 and len(self.results) >= self.num:
                        self.has_more = False
                        logger.info(f'已达到限制采集数量：{len(self.results)}')
                        return
                    # =====增量采集=====
                    _time = item.get('create_time', item.get('createTime'))
                    _is_top = item.get('is_top', item.get('tag', {}).get('isTop'))
                    if self.results_old:
                        old = self.results_old[0]['time']
                        if _time <= old:  # 如果当前作品时间早于上次采集的最新作品时间，且不是置顶作品，直接退出
                            if _is_top:
                                continue
                            if self.has_more:
                                self.has_more = False
                                logger.success(f'增量采集完成，上次运行结果：{old}')
                            return
                    # =====保存结果=====
                    # _type = item.get('media_type', item.get('media_type'))  # 2 图集 4 视频
                    _type = item.get('aweme_type', item.get('awemeType'))
                    info: dict = item.get('statistics', item.get('stats', {}))
                    for i in [
                            'playCount', 'downloadCount', 'forwardCount', 'collectCount', "digest", "exposure_count",
                            "live_watch_count", "play_count", "download_count", "forward_count", "lose_count",
                            "lose_comment_count"
                    ]:
                        if not info.get(i):
                            info.pop(i, '')
                    for i in ['duration', 'authentication_token']:
                        if item.get(i):
                            info[i] = item[i]
                    if _type <= 66 or _type in [69, 107]:  # 视频 77西瓜视频
                        play_addr = item['video'].get('play_addr')
                        if play_addr:
                            download_addr = item['video']['play_addr']['url_list'][-1]
                        else:
                            download_addr = f"https:{ item['video']['playApi']}"
                        info['download_addr'] = download_addr
                    elif _type == 68:  # 图文
                        info['download_addr'] = [images.get('url_list', images.get('urlList'))[-1] for images in item['images']]
                    elif _type == 101:  # 直播
                        continue
                    else:  # 其他类型作品
                        info['download_addr'] = '其他类型作品'
                        logger.info('type', _type)
                        with open(f'{_type}.json', 'w', encoding='utf-8') as f:  # 保存未区分的类型
                            json.dump(item, f, ensure_ascii=False)  # 中文不用Unicode编码
                        continue
                    info.pop('aweme_id', '')
                    info['id'] = item.get('aweme_id', item.get('awemeId'))
                    info['time'] = _time
                    desc = self.str2path(item.get('desc'))
                    info['desc'] = desc
                    music = item.get('music')
                    if music:
                        info['music_title'] = self.str2path(music['title'])
                        info['music_url'] = music.get('play_url', music.get('playUrl'))['uri']
                    cover = item['video'].get('origin_cover')
                    if cover:
                        info['cover'] = item['video']['origin_cover']['url_list'][-1]
                    else:
                        info['cover'] = f"https:{item['video']['originCover']}"
                    text_extra = item.get('text_extra', item.get('textExtra'))
                    if text_extra:
                        info['text_extra'] = [{
                            'tag_id': hashtag.get('hashtag_id', hashtag.get('hashtagId')),
                            'tag_name': hashtag.get('hashtag_name', hashtag.get('hashtagName'))
                        } for hashtag in text_extra]
                    video_tag = item.get('video_tag', item.get('videoTag'))
                    if video_tag:
                        info['video_tag'] = video_tag
                    self.results.append(info)  # 用于保存信息
                logger.info(f'采集中，已采集到{len(self.results)}条结果')
            else:
                self.has_more = False
                logger.info(f'已达到限制采集数量：{len(self.results)}')

    def download(self):
        """
        采集完成后，统一下载已采集的结果
        """
        if os.path.exists(self.aria2_conf):
            logger.info('开始下载')
            command = ['aria2c', '-c', '--console-log-level', 'warn', '-d', self.down_path, '-i', self.aria2_conf]
            subprocess.run(command)  # shell=True时字符串会转义
        else:
            logger.error('没有发现可下载的配置文件')

    def save(self):
        _ = []
        with open(self.aria2_conf, 'w', encoding='utf-8') as f:
            for line in self.results:  # 只保存本次采集结果的下载配置
                filename = f'{line["id"]}_{line["desc"]}'
                if isinstance(line["download_addr"], list):
                    down_path = self.down_path.replace(line["id"], filename) if self.type == 'video' else os.path.join(
                        self.down_path, filename)
                    [
                        _.append(f'{addr}\n\tdir={down_path}\n\tout={line["id"]}_{index + 1}.jpeg\n')
                        for index, addr in enumerate(line["download_addr"])
                    ]
                elif isinstance(line["download_addr"], str):
                    if self.msToken:  # 下载0kb时，使用msToken
                        _.append(
                            f'{line["download_addr"]}\n\tdir={self.down_path}\n\tout={filename}.mp4\n\tuser-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36\n\theader=Cookie:msToken={line["authentication_token"]}\n'
                        )
                    else:
                        _.append(f'{line["download_addr"]}\n\tdir={self.down_path}\n\tout={filename}.mp4\n')  # 能正常下载的
                else:
                    logger.error("下载地址错误")
            f.writelines(_)
        with open(f'{self.down_path}.json', 'w', encoding='utf-8') as f:  # 保存所有数据到文件，包括旧数据
            self.results.sort(key=lambda item: item['id'], reverse=True)
            self.results.extend(self.results_old)
            json.dump(self.results, f, ensure_ascii=False)


@click.command()
@click.option('-t', '--targets', type=click.STRING, multiple=True, help='必填。用户URL/sec_uid或文件路径（文件格式为一行一个），支持多次输入')
@click.option('-l', '--limit', default=-1, help='选填。最大采集数量，默认不限制')
@click.option('-c', '--cookie', default='', help='选填。登录后cookie中sessionid的值')
@click.option('-g', '--grab', is_flag=True, help='选填。只采集信息，不下载作品')
@click.option('-d', '--download', is_flag=True, help='选填。直接下载采集完成的配置文件，用于采集时下载失败后重试')
def main(targets, limit, grab, download, cookie):
    """
    命令行
    """
    if not targets:
        targets = (input('目标URL或文件路径：'), )
    for _target in targets:
        if os.path.isfile(_target):  # 文件路径
            with open(_target, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if lines:
                for line in lines:
                    start(line, limit, grab, download, cookie)
            else:
                logger.error(f'[{_target}]中没有发现目标URL')
        else:
            start(_target, limit, grab, download, cookie)


def start(target, limit, grab, download, cookie):
    a = Douyin(target, limit, cookie)
    if not download:  # 不直接下载
        a.crawl()
    if not grab:  # 不直接下载
        a.download()


if __name__ == "__main__":
    # a = Douyin('https://m.douyin.com/share/user/MS4wLjABAAAAUe1jo5bYxPJybmnDDMxh2e9A95NAvoNfJiL7JVX5nhQ', limit=5)  # 作品
    # a = Douyin('https://v.douyin.com/BK2VMkG/', limit=5)  # 图集
    # a = Douyin('https://www.douyin.com/user/MS4wLjABAAAAUe1jo5bYxPJybmnDDMxh2e9A95NAvoNfJiL7JVX5nhQ')  # 长链接
    # a.crawl()
    # a.download()
    #  python main.py -t https://v.douyin.com/BGf3Wp6/
    main()
