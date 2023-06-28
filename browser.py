import os
from concurrent.futures import ThreadPoolExecutor

from playwright.sync_api import BrowserContext, sync_playwright


class Browser(object):

    def __init__(self,
                 channel: str = 'msedge',
                 need_login: bool = True,
                 headless: bool = True,
                 ua: str = 'pc',
                 image: bool = False):
        """
        可用对象包括：
        self.context
        self.browser
        self.playwright
        [注意]
        playwright非线程安全
        不能在同一线程内多次创建playwright实例，不能在不同线程调用同一个全局playwright对象
        若需要在线程内调用，则需要在每个线程内创建playwright实例，可参考do_login写法
        """
        self.start(channel, need_login, headless, ua, image)

    def anti_js(self):
        """
        注入js反检测，没用
        """
        # js ="./js/anti.js"
        js = "./js/stealth.min.js"
        self.context.add_init_script(path=js)

    def do_login(self):
        """
        登录
        """
        from login import Login

        storage_state = "./auth.json" if os.path.exists("./auth.json") else None
        self.context = self.browser.new_context(
            **self._ua,
            storage_state=storage_state,
            permissions=['notifications'],
            ignore_https_errors=True,
        )

        _login = Login(self.context)
        if not _login.check_login():
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_login.new_login)
                cookies = future.result()
            self.context.clear_cookies()
            self.context.add_cookies(cookies)

    def start(self, channel, need_login, headless, ua, image) -> BrowserContext:
        """
        启动浏览器
        """
        _args = [
            '--disable-blink-features=AutomationControlled',
        ]
        if not image:  # 不显示图片
            _args.append("--blink-settings=imagesEnabled=false")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            channel=channel,
            headless=headless,
            ignore_default_args=['--enable-automation'],
            args=_args,
        )
        if ua == 'pc':
            self._ua: dict = self.playwright.devices['Desktop Edge']
            self._ua['user_agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50'
        else:
            self._ua = self.playwright.devices['iPhone 12']
        if need_login:  # 重用登录状态
            self.do_login()
        else:
            self.context = self.browser.new_context(
                **self._ua,
                permissions=['notifications'],
                ignore_https_errors=True,
            )
        # self.anti_js()

    def stop(self):
        """
        关闭浏览器
        """
        self.context.close()
        self.browser.close()
        self.playwright.stop()


if __name__ == "__main__":
    edge = Browser()
    # edge = Browser(headless=False)
    p = edge.context.new_page()
    # p.goto('https://antispider1.scrape.center/')
    # p.goto('https://antoinevastel.com/bots/')
    # p.keyboard.press('End')
    p.goto('https://antoinevastel.com/bots/datadome')  # 过不去
    # p.goto('https://www.douyin.com/search/xinhuashe?&type=user')
    # p.screenshot(path="end.png")
    edge.stop()
