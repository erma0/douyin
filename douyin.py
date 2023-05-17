# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Time    :   2023年02月19日 17:12:04 星期天
@Author  :   erma0
@Version :   3.0
@Link    :   https://erma0.cn
@Desc    :   抖音爬虫2023.05.06更新
'''
import json
import os
import re
from typing import List
from urllib.parse import unquote, urlparse, quote

import click
from loguru import logger
from playwright.sync_api import Route, TimeoutError, sync_playwright


class Douyin(object):

    def __init__(self, url: str, num: int = -1, need_login: bool = True, type: str = 'post', channel: str = 'msedge'):
        """
        初始化
        type=['post', 'like', 'music', 'search', 'follow', 'fans', 'collection']
        """
        self.url = url.strip()
        self.num = num
        self.need_login = need_login
        self.type = type
        self.channel = channel
        self.has_more = True
        self.down_path = os.path.join('.', '下载')
        if not os.path.exists(self.down_path): os.makedirs(self.down_path)
        self.pageDown = 0
        self.pageDownMax = 5  # 重试次数
        self.results = []  # 保存结果
        self.results_old = []  # 前一次保存结果

    @staticmethod
    def str2path(str: str):
        """
        把字符串转为Windows合法文件名
        """
        # 非法字符
        lst = ['\r', '\n', '\\', '/', ':', '*', '?', '"', '<', '>', '|', ' ']
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
    def quit(str):
        """
        直接退出程序
        """
        logger.error(str)
        exit()

    def url2redirect(self, url):
        """
        取302跳转地址
        """

        # a = self.context.request.head(url)
        r = self.context.new_page()
        r.route("**/*", lambda route: route.abort() if route.request.resource_type != "document" else route.continue_())
        r.goto(url, wait_until='domcontentloaded')
        url = r.url
        r.close()
        return url

    @staticmethod
    def filter_emoji(desstr, restr=''):
        # 过滤表情，在处理文件名的时候如果想去除emoji可以调用
        try:
            res = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            res = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
        return res.sub(restr, desstr)

    def _append_users(self, user_list: List[dict]):
        if not user_list:
            logger.error("本次请求结果为空")
            return
        if self.num < 0 or len(self.results) < self.num:
            for item in user_list:
                if self.num > 0 and len(self.results) >= self.num:
                    self.has_more = False
                    logger.info(f'已达到限制采集数量：{len(self.results)}')
                    return
                info = {}
                info['nickname'] = self.str2path(item['nickname'])
                info['signature'] = self.str2path(item['signature'])
                info['avatar'] = item['avatar_larger']['url_list'][0]
                for i in [
                        'sec_uid', 'uid', 'short_id', 'unique_id', 'unique_id_modify_time', 'aweme_count', 'favoriting_count',
                        'follower_count', 'following_count', 'constellation', 'create_time', 'enterprise_verify_reason',
                        'is_gov_media_vip', 'live_status', 'total_favorited', 'share_qrcode_uri'
                ]:
                    if item.get(i):
                        info[i] = item[i]
                room_id = item.get('room_id')
                if room_id:  # 直播间
                    info['live_room_id'] = room_id
                    info['live_room_url'] = [
                        f'http://pull-flv-f26.douyincdn.com/media/stream-{room_id}.flv',
                        f'http://pull-hls-f26.douyincdn.com/media/stream-{room_id}.m3u8'
                    ]
                music_count = item['original_musician']['music_count']
                if music_count:  # 原创音乐人
                    info['original_musician'] = item['original_musician']

                self.results.append(info)  # 用于保存信息
            logger.info(f'采集中，已采集到{len(self.results)}条结果')
        else:
            self.has_more = False
            logger.info(f'已达到限制采集数量：{len(self.results)}')

    def _append_awemes(self, aweme_list: List[dict]):
        """
        数据入库
        """
        if not aweme_list:
            logger.error("本次请求结果为空")
            return
        if self.num < 0 or len(self.results) < self.num:
            for item in aweme_list:
                if self.num > 0 and len(self.results) >= self.num:
                    self.has_more = False
                    logger.info(f'已达到限制采集数量：{len(self.results)}')
                    return
                # =====下载视频=====
                _time = item.get('create_time', item.get('createTime'))
                _is_top = item.get('is_top', item.get('tag', {}).get('isTop'))
                if self.results_old:
                    old = self.results_old[0]['time']
                    if _time <= old:  # 如果当前作品时间早于上次采集的最新作品时间，且不是置顶作品，直接退出
                        if _is_top:
                            continue
                        self.has_more = False
                        logger.success(f'增量采集完成，上次运行结果：{old}')
                        return
                _type = item.get('aweme_type', item.get('awemeType'))
                info = item.get('statistics', item.get('stats', {}))
                for i in [
                        'playCount', 'downloadCount', 'forwardCount', 'collectCount', "digest", "exposure_count",
                        "live_watch_count", "play_count", "download_count", "forward_count", "lose_count", "lose_comment_count"
                ]:
                    if not info.get(i):
                        info.pop(i, '')
                info.pop('aweme_id', '')
                if _type <= 66 or _type == 107:  # 视频 77西瓜视频
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
                tags = item.get('text_extra', item.get('textExtra'))
                if tags:
                    info['tags'] = [{
                        'tag_id': hashtag.get('hashtag_id', hashtag.get('hashtagId')),
                        'tag_name': hashtag.get('hashtag_name', hashtag.get('hashtagName'))
                    } for hashtag in tags]
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
            command = f"aria2c -c --console-log-level warn -d {self.down_path} -i {self.aria2_conf}"
            os.system(command)  # system有输出，阻塞
            # os.popen(command)  # popen无输出，不阻塞
        else:
            logger.error('没有发现可下载的配置文件')

    def save(self):
        if self.results:
            logger.success(f'采集完成，本次共采集到{len(self.results)}条结果')
            if self.type in ['post', 'like', 'music', 'search', 'collection']:  # 视频列表保存为Aria下载文件
                with open(self.aria2_conf, 'w', encoding='utf-8') as f:
                    _ = []
                    for line in self.results:  # 只保存本次采集结果的下载配置
                        filename = f'{line["id"]}_{line["desc"]}'
                        if isinstance(line["download_addr"], list):
                            down_path = os.path.join(self.down_path, filename)
                            [
                                _.append(f'{addr}\n\tdir={down_path}\n\tout={line["id"]}_{index + 1}.jpeg\n')
                                for index, addr in enumerate(line["download_addr"])
                            ]
                        elif isinstance(line["download_addr"], str):
                            _.append(f'{line["download_addr"]}\n\tdir={self.down_path}\n\tout={filename}.mp4\n')
                        else:
                            logger.error("下载地址错误")
                    f.writelines(_)
            with open(f'{self.down_path}.json', 'w', encoding='utf-8') as f:  # 保存所有数据到文件，包括旧数据
                if type == 'post':  # 除主页作品外都不需要按时间排序
                    self.results.sort(key=lambda item: item['id'], reverse=True)
                    self.results.extend(self.results_old)
                json.dump(self.results, f, ensure_ascii=False)
        else:
            logger.error("本次采集结果为空")

    def handle(self, route: Route):
        if self.has_more:
            if self.pageDown > 0:
                self.pageDown = 0
            response = route.fetch()
            try:
                resj = response.json()
                self.has_more = resj.get('has_more', True)
                if self.type == 'follow':
                    info = resj.get('followings')
                    self._append_users(info)
                elif self.type == 'fans':
                    info = resj.get('followers')
                    self._append_users(info)
                elif self.type == 'search':
                    info = []
                    for item in resj.get('data'):
                        if item['type'] == 1:  # 1作品 16合集 76百科 77头条文章 996热榜 997微头条
                            _info = item['aweme_info']
                            info.append(_info)
                        elif item['type'] == 16:
                            _info = item['aweme_mix_info']['mix_items']
                            info.extend(_info)
                        elif item['type'] == 996:
                            _info = item['sub_card_list'][0]['hotspot_info']['hotspot_items']
                            info.extend(_info)
                        else:
                            pass
                    self._append_awemes(info)
                else:
                    info = resj.get('aweme_list')
                    self._append_awemes(info)
            except Exception as err:
                logger.error(f'err：  {err}')
                with open('error.json', 'w', encoding='utf-8') as f:  # 保存未区分的类型
                    json.dump(response.json(), f, ensure_ascii=False)  # 中文不用Unicode编码
        route.fulfill(response=response)

    def anti_js(self):
        """
        注入js反检测，没用到
        """
        js = """
        window.chrome = {"app":{"isInstalled":false,"InstallState":{"DISABLED":"disabled","INSTALLED":"installed","NOT_INSTALLED":"not_installed"},"RunningState":{"CANNOT_RUN":"cannot_run","READY_TO_RUN":"ready_to_run","RUNNING":"running"}},"runtime":{"OnInstalledReason":{"CHROME_UPDATE":"chrome_update","INSTALL":"install","SHARED_MODULE_UPDATE":"shared_module_update","UPDATE":"update"},"OnRestartRequiredReason":{"APP_UPDATE":"app_update","OS_UPDATE":"os_update","PERIODIC":"periodic"},"PlatformArch":{"ARM":"arm","ARM64":"arm64","MIPS":"mips","MIPS64":"mips64","X86_32":"x86-32","X86_64":"x86-64"},"PlatformNaclArch":{"ARM":"arm","MIPS":"mips","MIPS64":"mips64","X86_32":"x86-32","X86_64":"x86-64"},"PlatformOs":{"ANDROID":"android","CROS":"cros","LINUX":"linux","MAC":"mac","OPENBSD":"openbsd","WIN":"win"},"RequestUpdateCheckStatus":{"NO_UPDATE":"no_update","THROTTLED":"throttled","UPDATE_AVAILABLE":"update_available"}}};
        Object.defineProperty(navigator,'plugins',{get:()=>[{0:{type:"application/x-google-chrome-pdf",suffixes:"pdf",description:"Portable Document Format",enabledPlugin:Plugin},description:"Portable Document Format",filename:"internal-pdf-viewer",length:1,name:"Chrome PDF Plugin"},{0:{type:"application/pdf",suffixes:"pdf",description:"",enabledPlugin:Plugin},description:"",filename:"mhjfbmdgcfjbbpaeojofohoefgiehjai",length:1,name:"Chrome PDF Viewer"}]});
        """
        self.context.add_init_script(js)

    def check_login(self):
        url = 'https://sso.douyin.com/passport/sso/check_login/'
        res = self.context.request.get(url).json()
        _login: bool = res.get("has_login", False)
        logger.info(f'已登录：{_login}')
        return _login

    def page_init(self):
        if urlparse(self.url).netloc.endswith('douyin.com'):  # 链接
            if self.url.endswith('?showTab=like'): self.type = 'like'
            self.url = self.url2redirect(self.url)
        else:  # 关键字
            self.url = f'https://www.douyin.com/search/{quote(self.url)}'
        *_, _type, self.id = unquote(urlparse(self.url).path.strip('/')).split('/')
        hookURL = '/aweme/v[123]/web/'
        if _type == 'search':  # 自动识别 搜索
            self.type = 'search'
            hookURL += 'general/search'
        elif _type == 'music':  # 自动识别 音乐
            self.type = 'music'
            hookURL += 'music'
        elif _type == 'collection':  # 自动识别 合集
            self.type = 'collection'
            hookURL += 'mix/aweme'
        elif self.type == 'post':
            hookURL += 'aweme/post'
        elif self.type == 'like':
            hookURL += 'aweme/favorit'
            if not self.url.endswith('showTab=like'):
                self.url = self.url.split('?')[0] + '?showTab=like'
        elif self.type == 'follow':
            hookURL += 'user/following'
        elif self.type == 'fans':
            hookURL += 'user/follower'
        else:  # 备用
            pass
        self.hookURL = re.compile(hookURL, re.S)

    def page_options(self):
        render_data = json.loads(unquote(self.page.locator('id=RENDER_DATA').inner_text()))
        info = render_data[sorted(render_data.keys())[1]]
        if self.type in ['post', 'like', 'follow', 'fans']:
            self.info = info['user']  # 备用
            self.title = self.info['user']['nickname']
            if self.type == 'follow':  # 点击关注列表
                self.page.locator('[data-e2e="user-info-follow"]').click()
                self.page.locator('[data-e2e="user-fans-container"]').click()
            elif self.type == 'fans':  # 点击粉丝列表
                self.page.locator('[data-e2e="user-info-fans"]').click()
                self.page.locator('[data-e2e="user-fans-container"]').click()
        elif self.type == 'search':
            self.title = self.id
            self.info = info['defaultSearchParams']
            # self.title = self.info['keyword']
        elif self.type == 'collection':
            self.info = info['aweme']['detail']['mixInfo']
            self.title = self.info['mixName']
        elif self.type == 'music':  # 聚焦滚动列表
            self.info = info['musicDetail']
            self.title = self.info['title']
            self.page.locator('[data-e2e="scroll-list"]').last.click()
        else:  # 备用
            pass

        self.down_path = os.path.join(self.down_path, self.str2path(f'{self.type}_{self.title}'))
        self.aria2_conf = f'{self.down_path}.txt'
        if self.type == 'post' and os.path.exists(f'{self.down_path}.json'):  # 主页作品可以增量采集，其他类型难以实现
            with open(f'{self.down_path}.json', 'r', encoding='utf-8') as f:
                self.results_old = json.load(f)
        if self.type == 'post':  # post页面需提取初始页面数据，先得到下载目录后再提取
            render_data_ls = info['post']['data']
            # 从新到旧排序,无视置顶作品（此需求一般用来采集最新作品）
            render_data_ls.sort(key=lambda item: item.get('aweme_id', item.get('awemeId')), reverse=True)
            self._append_awemes(render_data_ls)

    def page_next(self):  # 加载数据
        if self.type == 'collection':
            self.page.get_by_role("button", name="点击加载更多").click()
        else:
            self.page.keyboard.press('End')
        # logger.info("加载中")

    def run(self):
        """
        开始采集
        """
        with sync_playwright() as playwright:
            edge = playwright.devices['Desktop Edge']
            browser = playwright.chromium.launch(
                channel=self.channel,
                #  headless=False,
                args=['--disable-blink-features=AutomationControlled'])
            if self.need_login:
                # 重用登录状态
                storage_state = "./auth.json" if os.path.exists("./auth.json") else None
                self.context = browser.new_context(storage_state=storage_state, permissions=['notifications'], **edge)
                if not self.check_login():
                    from login import login
                    cookies = login(playwright)
                    self.context.add_cookies(cookies)
            else:
                self.context = browser.new_context(**edge, permissions=['notifications'])
            # self.anti_js()
            self.page_init()  # 初始化参数
            self.page = self.context.new_page()
            self.page.set_default_timeout(0)
            self.page.route("**/*", lambda route: route.abort() if route.request.resource_type == "image" else route.continue_())
            self.page.route(self.hookURL, self.handle)
            self.page.goto(self.url)
            self.page_options()  # 打开页面后的操作
            while self.has_more and self.pageDown <= self.pageDownMax:
                try:
                    with self.page.expect_request_finished(lambda request: self.hookURL.search(request.url), timeout=2000):
                        self.page_next()  # 加载下一批数据
                except TimeoutError:  # 重试
                    self.pageDown += 1
                    logger.error("重试 + 1")
            self.save()  # 保存结果
            self.page.unroute(self.hookURL, self.handle)
            self.page.wait_for_timeout(1000)
            # self.page.screenshot(path="end.png")
            self.context.close()
            browser.close()


@click.command()
@click.option('-u', '--urls', type=click.STRING, multiple=True, help='必填。账号/话题/音乐的URL或文件路径（文件格式为一行一个URL），支持多次输入')
@click.option('-n', '--num', default=-1, help='选填。最大采集数量，默认不限制')
@click.option('-g', '--grab', is_flag=True, help='选填。只采集信息，不下载作品')
@click.option('-d', '--download', is_flag=True, help='选填。直接下载采集完成的配置文件，用于采集时下载失败后重试')
@click.option('-l', '--login', default=True, is_flag=True, help='选填。指定是否需要登录，默认要登录，用于采集主页作品、关注粉丝列表以及本人私密账号的信息，也可避免一些莫名其妙的风控')
@click.option('-t',
              '--type',
              type=click.Choice(['post', 'like', 'music', 'search', 'follow', 'fans', 'collection'], case_sensitive=False),
              default='post',
              help='选填。采集类型，支持[作品/喜欢/音乐/搜索/关注/粉丝/合集]，默认采集post作品，能够自动识别搜索/音乐/合集。采集账号主页作品或私密账号喜欢作品必须登录。')
@click.option('-b',
              '--browser',
              type=click.Choice(["chrome", "msedge", "chrome-beta", "msedge-beta", "msedge-dev"], case_sensitive=False),
              default='msedge',
              help='选填。浏览器类型，默认使用稳定版EDGE，可选[chrome/msedge]，如需使用Firefox或WebKit请自行修改run函数。')
def main(urls, num, grab, download, login, type, browser):
    """
    命令行
    """
    # print()
    if not urls:
        urls = (input('目标URL或文件路径：'), )
    for url in urls:
        if os.path.exists(url):  # 文件路径
            with open(url, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if lines:
                for line in lines:
                    start(line, num, grab, download, login, type, browser)
            else:
                logger.error(f'[{url}]中没有发现目标URL')
        else:
            start(url, num, grab, download, login, type, browser)


def start(url, num, grab, download, login, type, browser):
    a = Douyin(url, num, login, type, browser)
    if not download:  # 需要新采集
        a.run()
    if grab or type in ['follow', 'fans']:  # 不需要下载
        return
    else:
        a.download()


def test():
    # a = Douyin('https://www.douyin.com/user/MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4', num=11)  # 作品
    # a = Douyin('https://www.douyin.com/user/MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4')  # 作品
    # a = Douyin('https://v.douyin.com/ULdJdxS/')  # 作品
    # a = Douyin('https://v.douyin.com/BK2VMkG/')  # 图集作品
    # a = Douyin('https://v.douyin.com/BGPBena/', type='music')  # 音乐
    # a = Douyin('https://v.douyin.com/BGPBena/', num=11)  # 音乐
    # a = Douyin('https://www.douyin.com/search/%E4%B8%8D%E8%89%AF%E4%BA%BA', 30)  # 搜索
    # a = Douyin('https://www.douyin.com/search/%E4%B8%8D%E8%89%AF%E4%BA%BA', type='search')  # 搜索
    # a = Douyin('不良人', num=11)  # 关键字搜索
    # a = Douyin('不良人', type='search', num=11)  # 关键字搜索
    # a = Douyin('https://www.douyin.com/user/MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4?showTab=like')  # 长链接+喜欢
    # a = Douyin('https://www.douyin.com/user/MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4', type='like')  # 长链接+喜欢
    # a = Douyin('https://v.douyin.com/BGf3Wp6/', type='like')  # 短链接+喜欢+自己的私密账号需登录
    # a = Douyin('https://www.douyin.com/user/MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4', type='fans')  # 粉丝
    a = Douyin('https://www.douyin.com/user/MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4', type='follow')  # 关注
    # a = Douyin('https://www.douyin.com/collection/7018087406876231711')  # 合集
    # a = Douyin('https://www.douyin.com/collection/7018087406876231711', type='collect')  # 合集
    a.run()
    # a.download()
    # python ./douyin.py -u https://v.douyin.com/BGf3Wp6/ -t like
    # https://v.douyin.com/AvTAgEn/


if __name__ == "__main__":
    banner = '''
     ____                    _         ____        _     _           
    |  _ \  ___  _   _ _   _(_)_ __   / ___| _ __ (_) __| | ___ _ __ 
    | | | |/ _ \| | | | | | | | '_ \  \___ \| '_ \| |/ _` |/ _ \ '__|
    | |_| | (_) | |_| | |_| | | | | |  ___) | |_) | | (_| |  __/ |   
    |____/ \___/ \__,_|\__, |_|_| |_| |____/| .__/|_|\__,_|\___|_|   
                        |___/                |_|                      
                                  V3.1.3
                  Github: https://github.com/erma0/douyin
'''
    print(banner)
    main()
    # test()
