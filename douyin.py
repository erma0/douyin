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
from urllib.parse import unquote, urlparse

import click
from loguru import logger
from playwright.sync_api import Route, TimeoutError, sync_playwright


class Douyin(object):

    def __init__(self, target: str, limit: int = -1, post: bool = True, like: bool = False, need_login: bool = False):
        """
        初始化
        """
        self.limit = limit
        self.url = target.strip()
        if like: self.type = 'like'
        self.down_path = os.path.join('.', '下载')
        if not os.path.exists(self.down_path): os.makedirs(self.down_path)
        self.has_more = True
        self.post = post
        self.need_login = post if post else need_login
        hookURL = '/aweme/v[123]/web/(aweme|music|search)'
        self.hookURL = re.compile(hookURL, re.S)
        self.pageDown = 0
        self.pageDownMax = 5  # 重试次数
        self.results = []  # 保存结果

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
        程序出错，直接退出
        """
        logger.error(str)
        exit()

    @staticmethod
    def filter_emoji(desstr, restr=''):
        # 过滤表情，在处理文件名的时候如果想去除emoji可以调用
        try:
            res = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            res = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
        return res.sub(restr, desstr)

    def _append_results(self, aweme_list: List[dict]):
        """
        数据入库
        """
        if self.limit < 0 or len(self.results) < self.limit:
            for item in aweme_list:
                if self.limit > 0 and len(self.results) >= self.limit:
                    self.has_more = False
                    # 如果给出了限制采集数目，直接退出循环
                    # self.videosL = self.videosL[:self.limit + self.over_num]  # 超出的删除
                    logger.info(f'已达到限制采集数量：{len(self.results)}')
                    return
                # =====下载视频=====
                _type = item.get('aweme_type', item.get('awemeType'))
                desc = self.str2path(item['desc'])
                info = item.get('statistics', item.get('stats', {}))
                for i in [
                        'playCount', 'downloadCount', 'forwardCount', 'collectCount', "digest", "exposure_count",
                        "live_watch_count", "play_count"
                ]:
                    if not info.get(i):
                        info.pop(i, '')
                info['id'] = item.get('aweme_id', item.get('awemeId'))
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
                # if _type in [0, 33, 51, 53, 55, 61, 66]:  # 视频
                if _type <= 66:  # 视频
                    play_addr = item['video'].get('play_addr')
                    if play_addr:
                        download_addr = item['video']['play_addr']['url_list'][-1]
                    else:
                        download_addr = f"https:{ item['video']['playApi']}"
                    info['download_addr'] = download_addr
                elif _type == 68:  # 图文
                    info['download_addr'] = [images.get('url_list', images.get('urlList'))[-1] for images in item['images']]
                else:  # 其他类型作品
                    info['download_addr'] = '其他类型作品'
                    logger.info('type', _type)
                    with open(f'{_type}.json', 'w', encoding='utf-8') as f:  # 保存未区分的类型
                        json.dump(item, f, ensure_ascii=False)  # 中文不用Unicode编码
                self.results.append(info)  # 用于保存信息

            logger.info(f'采集中，已采集到{len(self.results)}条结果')

    def download(self):
        """
        采集完成后，统一下载已采集的结果
        """

        if os.path.exists(self.aria2_conf):
            logger.info('开始下载')
            command = f"aria2c.exe -c --console-log-level warn -d {self.down_path} -i {self.aria2_conf}"
            os.system(command)  # system有输出，阻塞
            # os.popen(command)  # popen无输出，不阻塞
        else:
            logger.error('没有发现可下载的配置文件')

    def save(self):
        if self.results:
            logger.success(f'采集完成，共采集到{len(self.results)}条结果')
            with open(f'{self.down_path}.json', 'w', encoding='utf-8') as f:  # 保存数据到文件
                json.dump(self.results, f, ensure_ascii=False)  # 中文不用Unicode编码
            with open(self.aria2_conf, 'w', encoding='utf-8') as f:  # 保存为Aria下载文件
                _ = []
                for line in self.results:
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
                # f.writelines([f'{line["download_addr"]}\n\tdir={self.down_path}\n\tout={filename}.mp4\n' for line in self.results])
        else:
            logger.error("采集结果为空")

    def handle(self, route: Route):
        if self.has_more:
            if self.pageDown > 0:
                self.pageDown = 0
            response = route.fetch()
            # logger.success(f"<< status  {response.status}")
            try:
                resj = response.json()
                info = resj.get('aweme_list') if resj.get('aweme_list') else [item['aweme_info'] for item in resj.get('data')]
                self.has_more = resj.get('has_more', True)
                self._append_results(info)
            except Exception as err:
                logger.error(f'err  {err}')
                logger.info(f'response  {response.text()}')
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

    def get_down_path(self):
        # 判断链接类型（user/like/music/search） 取目标ID
        *_, self.type, self.id = unquote(urlparse(self.url).path.strip('/')).split('/')
        if self.url.endswith('showTab=like'): self.type = 'like'
        if self.type == 'search':
            self.title = self.id
        else:
            self.title = self.title.split('-')[0].strip()
        self.down_path = os.path.join(self.down_path, self.str2path(f'{self.type}_{self.title}'))
        self.aria2_conf = f'{self.down_path}.txt'

    def run(self):
        """
        开始采集
        """
        with sync_playwright() as playwright:
            edge = playwright.devices['Desktop Edge']
            browser = playwright.chromium.launch(channel="msedge",
                                                 headless=True,
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
            self.page = self.context.new_page()
            self.page.set_default_timeout(0)
            self.page.route("**/*", lambda route: route.abort() if route.request.resource_type == "image" else route.continue_())
            self.page.route(self.hookURL, self.handle)
            self.page.goto(self.url)

            if self.type == 'like' and not self.page.url.endswith('showTab=like'):
                self.url = self.page.url + '?showTab=like'
                self.page.goto(self.url)
            else:
                self.url = self.page.url
            self.title = self.page.title()
            self.get_down_path()
            self.page.locator('[data-e2e="scroll-list"]').last.click()  # 聚焦滚动列表
            if self.post:  # 提取初始页面数据
                render_data = json.loads(unquote(self.page.locator('id=RENDER_DATA').inner_text()))
                self._append_results(render_data['41']['post']['data'])

            while self.has_more and self.pageDown <= self.pageDownMax:
                try:
                    # with self.page.expect_request('https://mcs.zijieapi.com/list', timeout=2000):
                    with self.page.expect_request_finished(lambda request: self.hookURL.search(request.url), timeout=2000):
                        self.page.keyboard.press('End')
                        # logger.info("press('End')")
                except TimeoutError:
                    self.page.keyboard.press('PageUp')
                    self.pageDown += 1
                    logger.error("超时 + 1")
            self.save()
            self.page.wait_for_timeout(1000)
            # self.page.screenshot(path="end.png")
            self.context.close()
            browser.close()


@click.command()
@click.option('-t', '--targets', type=click.STRING, multiple=True, help='必填。账号/话题/音乐的URL或文件路径（文件格式为一行一个URL），支持多次输入')
@click.option('-l', '--limit', default=-1, help='选填。最大采集数量，默认不限制')
@click.option('-g', '--grab', is_flag=True, help='选填。只采集信息，不下载作品')
@click.option('-d', '--download', is_flag=True, help='选填。直接下载采集完成的配置文件，用于采集时下载失败后重试')
@click.option('-np', '--notpost', is_flag=True, help='选填。采集除了账号主页作品之外的链接（喜欢/音乐/搜索）不需要登录')
@click.option('-like', '--like', is_flag=True, help='选填。采集账号喜欢作品，输入短链接时需指定，长链接时可指定或在长链接最后加[?showTab=like]')
@click.option('-login', '--login', is_flag=True, help='选填。指定 是否需要登录，默认不登录，可以指定需用登录用于采集自己私密账号的信息')
def main(targets, limit, notpost, grab, download, like, login):
    """
    命令行
    """
    # print(targets, limit, notpost, grab, download, like, login)
    if not targets:
        targets = (input('目标URL或文件路径：'), )
    for _target in targets:
        if os.path.exists(_target):  # 文件路径
            with open(_target, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if lines:
                for line in lines:
                    start(line, limit, notpost, grab, download, like, login)
            else:
                logger.error(f'[{_target}]中没有发现目标URL')
        else:
            start(_target, limit, notpost, grab, download, like, login)


def start(target, limit, notpost, grab, download, like, login):
    if urlparse(target).netloc.endswith('douyin.com'):  # 单个URL
        a = Douyin(target, limit, not notpost, like, login)  # 作品
        if not download:  # 需要新采集
            a.run()
        if not grab:  # 需要下载
            a.download()
    else:
        logger.error(f'[{target}]不是目标URL格式')


if __name__ == "__main__":
    # a = Douyin('https://m.douyin.com/share/user/MS4wLjABAAAAUe1jo5bYxPJybmnDDMxh2e9A95NAvoNfJiL7JVX5nhQ', limit=5)  # 作品
    # a = Douyin('https://m.douyin.com/share/user/MS4wLjABAAAAUe1jo5bYxPJybmnDDMxh2e9A95NAvoNfJiL7JVX5nhQ')  # 作品
    # a = Douyin('https://v.douyin.com/BGPBena/', post=False)  # 音乐
    # a = Douyin('https://v.douyin.com/BK2VMkG/', post=False)  # 图集
    # a = Douyin('https://www.douyin.com/user/MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4?showTab=like', post=False)  # 长链接+喜欢
    # a = Douyin('https://v.douyin.com/BGf3Wp6/', need_login=True, like=True, post=False)  # 短链接+喜欢+自己的私密账号需登录
    # a.run()
    # a.download()
    # python ./spider.py -t https://v.douyin.com/BGf3Wp6/ -login -like -np
    main()
    # https://v.douyin.com/AvTAgEn/
