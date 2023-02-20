# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Time    :   2023年02月19日 17:12:04 星期天
@Author  :   erma0
@Version :   1.0
@Link    :   https://erma0.cn
@Desc    :   抖音爬虫2023.02.19更新
'''

import os
import click
import json
import time
import requests
from urllib.parse import urlparse
import webview
from loguru import logger

# logger.add("log_{time}.log")


class Douyin(object):

    def __init__(self, target: str, limit: int = 0, v_web_id: str = ''):
        """
        初始化用户信息
        """
        self.http = requests.Session()
        self.http.headers.clear()
        self.http.headers.update({
            'User-Agent':
            'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36 Edg/110.0.1587.46'
        })

        self.limit = limit
        self.verify_web_id = v_web_id
        self.url = self.url2redirect(target.strip())
        # 判断链接类型（user/video/challenge/music），取目标ID
        *_, self.type, self.id = urlparse(self.url).path.strip('/').split('/')
        self.down_path = os.path.join('.', '下载')
        if not os.path.exists(self.down_path): os.makedirs(self.down_path)
        self.has_more = True
        self.videosL = []  # 采集结果采用列表格式

        if not self.test_cookie():
            self.get_verify()
        self.get_target_info()

    def quit(self, str):
        """
        程序出错，直接退出
        """
        logger.error(str)
        exit()

    def url2redirect(self, url):
        """
        取302跳转地址
        短连接转长链接
        """
        r = self.http.head(url, allow_redirects=False)
        return r.headers.get('Location', url)

    @staticmethod
    def str2path(str: str):
        """
        把字符串转为Windows合法文件名
        """
        # 非法字符
        lst = ['\r', '\n', '\\', '/', ':', '*', '?', '"', '<', '>', '|']
        # 非法字符处理方式1
        for key in lst:
            str = str.replace(key, '_')
        # 非法字符处理方式2
        # str = str.translate(None, ''.join(lst))
        # 文件名+路径长度最大255，汉字*2，取80
        if len(str) > 80:
            str = str[:80]
        return str.strip()

    def download(self):
        """
        作品抓取完成后，统一下载已采集的结果
        """
        if self.videosL:
            logger.info('开始下载')
            filename = f'{self.down_path}.txt'
            if self.type == 'like':
                self.down_path = os.path.join(self.down_path, self.type)
            command = f"aria2c.exe -c --console-log-level warn -d {self.down_path} -i {filename}"
            os.system(command)  # system有输出，阻塞
            # os.popen(command)  # popen无输出，不阻塞

    def test_cookie(self, v_web_id=''):
        """
        测试cookie有效性
        """
        if self.verify_web_id:
            pass
        elif v_web_id:
            self.verify_web_id = v_web_id
        elif os.path.exists('./verify'):
            with open('./verify', 'r', encoding='utf-8') as f:
                self.verify_web_id = f.read()
        else:
            return False

        self.http.headers.update({'Cookie': 's_v_web_id=' + self.verify_web_id})
        res = self.http.get('https://www.douyin.com/web/api/v2/aweme/post/').content  # 检测cookie是否有效
        if res:  # 有返回结果，证明cookie未过期，直接销毁窗口，进入主程序
            logger.success(f'验证成功：{self.verify_web_id}')
            with open('./verify', 'w', encoding='utf-8') as f:
                f.write(self.verify_web_id)
            return True
        else:
            return False

    def __webview_start(self):
        """
        webview窗口启动程序
        """
        logger.info('验证码加载中...')
        self.window.hide()
        self.verify_web_id = ''
        while not self.verify_web_id:
            for c in self.window.get_cookies():
                if c.get('s_v_web_id'):
                    self.verify_web_id = c.get('s_v_web_id').value
                    break
            time.sleep(0.5)
        if self.test_cookie():
            self.window.destroy()  # 销毁验证码窗口
            return

        self.window.show()  # 显示验证码窗口
        self.window.restore()  # 显示验证码窗口，从最小化恢复
        for i in range(60 * 2):
            if self.test_cookie():
                self.window.destroy()  # 销毁验证码窗口
                return
            else:
                if i % 2 == 0: logger.info(f'请在 {60-i//2}秒 之内通过验证')
                time.sleep(0.5)
        self.window.destroy()  # 销毁验证码窗口
        self.quit('验证失败，程序退出。')

    def get_verify(self):
        """
        手动过验证码
        """
        import ctypes
        user32 = ctypes.windll.user32
        w, h = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        side = 1080 * 255 // h  # 窗口大小自适应系统缩放
        self.window = webview.create_window(
            # hidden=True,# 有bug，隐藏窗口不能恢复，使用最小化代替
            minimized=True,  # 最小化
            frameless=True,  # 无边框
            width=side,
            height=side,  # 1080p：无框高255；125%：无框高315，框高40
            title='请手动过验证码',
            # url='https://www.douyin.com/share/user/MS4wLjABAAAA-Hb-4F9Y2cX_D0VZapSrRQ71BarAcaE1AUDI5gkZBEY'  # 指定一处验证码可以通用
            url=self.url  # 每次使用目标URL获取验证码，会出现两个域名，短期可能需要两次验证
        )

        webview.start(
            func=self.__webview_start,
            private_mode=False,
            user_agent=
            'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36 Edg/110.0.1587.46'
            # 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        )

    def get_target_info(self):
        """
        取目标信息
        查询结果在 self.info
        """
        if self.type == 'video':
            self.down_path = os.path.join(self.down_path, '未分类作品')
            # url = f'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={self.id}'
            return
        else:
            dic = {'user': ('sec_uid', 'nickname'), 'challenge': ('ch_id', 'cha_name'), 'music': ('music_id', 'title')}
            url = f'https://www.iesdouyin.com/web/api/v2/{self.type}/info/?{dic[self.type][0]}={self.id}'
        res = self.http.get(url).json()
        for key, value in res.items():
            if key.endswith('_info'):
                self.info = value
                # 下载路径
                self.down_path = os.path.join(self.down_path, self.str2path(f'{self.type}_{value[dic[self.type][1]]}_{self.id}'))

    def parse(self):
        """
        单个作品解析
        """
        url = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/'
        params = {'item_ids': self.id}
        res = self.http.get(url, params=params).json()
        if res:
            aweme_list = res.get('item_list')
            if aweme_list:
                self.__append_videos(aweme_list)
                logger.success(f'解析完成')
                if self.videosL:
                    with open(f'{self.down_path}.txt', 'w', encoding='utf-8') as f:  # 保存为Aria下载文件
                        f.writelines(self.videosL)
                    # with open(f'{self.down_path}.json', 'w', encoding='utf-8') as f:  # 保存数据到文件
                    #     json.dump(self.videosL, f, ensure_ascii=False)  # 中文不用Unicode编码
                return
        self.quit('解析失败')

    def crawl(self):
        """
        采集用户作品/喜欢
        """
        if self.type == 'video':
            return self.parse()
        cursor = 0
        retry = 0
        max_retry = 10
        dic = {
            'user': ('max_cursor', 'sec_uid', 'aweme/post'),
            'like': ('max_cursor', 'sec_uid', 'aweme/like'),
            'challenge': ('cursor', 'ch_id', 'challenge/aweme'),
            'music': ('cursor', 'music_id', 'music/list/aweme')
        }
        # https://www.iesdouyin.com/web/api/v2/aweme/post/  max_cursor
        # https://www.iesdouyin.com/web/api/v2/aweme/like/  max_cursor
        # https://www.iesdouyin.com/web/api/v2/challenge/aweme/  cursor
        # https://www.iesdouyin.com/web/api/v2/music/list/aweme/  cursor
        url = f'https://www.iesdouyin.com/web/api/v2/{dic[self.type][2]}/'

        while self.has_more:
            params = {dic[self.type][1]: self.id, "count": "20", dic[self.type][0]: cursor}
            res = self.http.get(url, params=params).json()
            if res:
                cursor = res.get(dic[self.type][0])
                self.has_more = res.get('has_more')
                aweme_list = res.get('aweme_list')
                if aweme_list:
                    self.__append_videos(aweme_list)
                    if retry: retry = 0  # 请求成功后重置重试次数
                else:
                    logger.error(f'采集未完成，但请求结果为空... 进行第{retry}次重试')
                    retry += 1
            else:
                retry += 1
                logger.error(f'采集请求出错... 进行第{retry}次重试')

            # 默认重试max_retry次
            if retry >= max_retry:
                self.has_more = False
        if self.videosL:
            logger.success(f'采集完成，共采集到{len(self.videosL)}条结果')
            with open(f'{self.down_path}.txt', 'w', encoding='utf-8') as f:  # 保存为Aria下载文件
                f.writelines(self.videosL)
            # with open(f'{self.down_path}.json', 'w', encoding='utf-8') as f:  # 保存数据到文件
            #     json.dump(self.videosL, f, ensure_ascii=False)  # 中文不用Unicode编码

    def __append_videos(self, aweme_list):
        """
        数据入库
        """
        for item in aweme_list:
            # =====采集数据=====
            # info = item.get('statistics', {})
            # if info:
            #     info.pop('play_count', '')
            # else:
            #     info['aweme_id'] = item['aweme_id']
            # info['desc'] = self.str2path(item['desc'])  # 需提前处理非法字符串
            # info['uri'] = item['video']['play_addr']['uri']
            # info['duration'] = item['video']['duration']
            # download_addr = item['video'].get('download_addr')
            # if download_addr:
            #     download_addr = item['video']['download_addr']['url_list'][0].replace('ratio=540p', 'ratio=1080p').replace(
            #         'ratio=720p', 'ratio=1080p').replace('watermark=1', 'watermark=0')  # 去水印+高清
            # else:
            #     download_addr = item['video']['play_addr']['url_list'][0].replace('/playwm/', '/play/')  # 高清
            # info['origin_cover'] = item['video']['origin_cover']['url_list'][0]
            # info['dynamic_cover'] = item['video']['dynamic_cover']['url_list'][0]
            # self.videosL.append(info)# 保存数据

            # =====下载视频=====
            id = item['aweme_id']
            filename = self.str2path(item['desc'])
            download_addr = item['video'].get('download_addr')
            if download_addr:
                download_addr = item['video']['download_addr']['url_list'][0].replace('ratio=540p', 'ratio=1080p').replace(
                    'ratio=720p', 'ratio=1080p').replace('watermark=1', 'watermark=0')  # 去水印+高清
            else:
                download_addr = item['video']['play_addr']['url_list'][0].replace('/playwm/', '/play/')  # 高清
            self.videosL.append(f'{download_addr}\n\tdir={self.down_path}\n\tout={id}_{filename}.mp4\n')  # 用于下载

        if self.limit:
            more = len(self.videosL) - self.limit
            if more >= 0:
                # 如果给出了限制采集数目，超出的删除后直接返回
                self.videosL = self.videosL[:self.limit]
                self.has_more = False
        logger.info(f'采集中，已采集到{len(self.videosL)}条结果')


@click.command()
@click.option('-u', '--url', prompt='目标URL', help='必填。用户/话题/音乐/视频的URL')
@click.option('-l', '--limit', default=0, help='选填。最大采集数量，默认不限制')
@click.option('-c', '--cookie', default='', help='选填。网页cookie中s_v_web_id的值[verify_*]，默认不指定，从程序中重新获取')
@click.option('--like', is_flag=True, help='选填。只采集用户喜欢作品')
def start(url, limit, like, cookie):
    """
    命令行
    """
    a = Douyin(url, limit, cookie)  # 作品
    if like:
        a.type = 'like'
    a.crawl()
    a.download()


if __name__ == "__main__":
    # a = Douyin('https://v.douyin.com/BGfGunr/', limit=5)  # 作品
    # a = Douyin('https://v.douyin.com/BGPS8D7/', limit=5)  # 话题
    # a = Douyin('https://v.douyin.com/BGPBena/', limit=5)  # 音乐
    # a = Douyin('https://v.douyin.com/BnKHFA4/')  # 单个视频
    a = Douyin('https://v.douyin.com/BnmDr51/', limit=5)  # 喜欢
    # a = Douyin('https://www.douyin.com/user/MS4wLjABAAAABPp-cYQw6UzgBj-3sq-a9P2weMfqCLf6FVNmmT_kdkw', limit=5)  # 长链接+喜欢
    a.type = 'like'  # 喜欢
    a.crawl()
    a.download()

    # start()
