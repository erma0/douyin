import os
from concurrent.futures import ThreadPoolExecutor

from playwright.sync_api import BrowserContext, sync_playwright


class Browser(object):

    def __init__(self, channel: str = 'msedge', need_login: bool = True, headless: bool = True, ua: str = 'pc'):
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
        self.start(channel, need_login, headless, ua)

    def start(self, channel, need_login, headless, ua) -> BrowserContext:
        """
        启动浏览器
        """
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(channel=channel,
                                                       headless=headless,
                                                       args=['--disable-blink-features=AutomationControlled'])
        if ua == 'pc':
            self._ua: dict = self.playwright.devices['Desktop Edge']
            self._ua.pop('user_agent')
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

    def stop(self):
        """
        关闭浏览器
        """
        self.context.close()
        self.browser.close()
        self.playwright.stop()

    def anti_js(self):
        """
        注入js反检测，没用到
        """
        js = """
        window.chrome = {"app":{"isInstalled":false,"InstallState":{"DISABLED":"disabled","INSTALLED":"installed","NOT_INSTALLED":"not_installed"},"RunningState":{"CANNOT_RUN":"cannot_run","READY_TO_RUN":"ready_to_run","RUNNING":"running"}},"runtime":{"OnInstalledReason":{"CHROME_UPDATE":"chrome_update","INSTALL":"install","SHARED_MODULE_UPDATE":"shared_module_update","UPDATE":"update"},"OnRestartRequiredReason":{"APP_UPDATE":"app_update","OS_UPDATE":"os_update","PERIODIC":"periodic"},"PlatformArch":{"ARM":"arm","ARM64":"arm64","MIPS":"mips","MIPS64":"mips64","X86_32":"x86-32","X86_64":"x86-64"},"PlatformNaclArch":{"ARM":"arm","MIPS":"mips","MIPS64":"mips64","X86_32":"x86-32","X86_64":"x86-64"},"PlatformOs":{"ANDROID":"android","CROS":"cros","LINUX":"linux","MAC":"mac","OPENBSD":"openbsd","WIN":"win"},"RequestUpdateCheckStatus":{"NO_UPDATE":"no_update","THROTTLED":"throttled","UPDATE_AVAILABLE":"update_available"}}};
        Object.defineProperty(navigator,'plugins',{get:()=>[{0:{type:"application/x-google-chrome-pdf",suffixes:"pdf",description:"Portable Document Format",enabledPlugin:Plugin},description:"Portable Document Format",filename:"internal-pdf-viewer",length:1,name:"Chrome PDF Plugin"},{0:{type:"application/pdf",suffixes:"pdf",description:"",enabledPlugin:Plugin},description:"",filename:"mhjfbmdgcfjbbpaeojofohoefgiehjai",length:1,name:"Chrome PDF Viewer"}]});
        """
        self.context.add_init_script(js)


if __name__ == "__main__":
    edge = Browser(headless=False)
    p = edge.context.new_page()
    p.goto('http://baidu.com')
    input()
    edge.stop()
