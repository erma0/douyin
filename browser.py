import os

from playwright.sync_api import BrowserContext, sync_playwright


class Browser(object):

    def __init__(self, channel: str = 'msedge', need_login: bool = True, headless: bool = True):
        """
        根据给定参数启动浏览器，返回对象包括：
        self.context
        self.browser
        self.playwright
        """
        self.start(channel, need_login, headless)

    def check_login(self):
        url = 'https://sso.douyin.com/passport/sso/check_login/'
        res = self.context.request.get(url).json()
        _login: bool = res.get("has_login", False)
        return _login

    def start(self, channel, need_login, headless) -> BrowserContext:
        """
        启动浏览器
        """
        self.playwright = sync_playwright().start()
        edge = self.playwright.devices['Desktop Edge']
        self.browser = self.playwright.chromium.launch(channel=channel,
                                                       headless=headless,
                                                       args=['--disable-blink-features=AutomationControlled'])
        if need_login:
            # 重用登录状态
            storage_state = "./auth.json" if os.path.exists("./auth.json") else None
            self.context = self.browser.new_context(storage_state=storage_state, permissions=['notifications'], **edge)
            if not self.check_login():
                from login import login
                cookies = login()
                self.context.add_cookies(cookies)
        else:
            self.context = self.browser.new_context(**edge, permissions=['notifications'])
        # self.anti_js()
        return self.context

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
    edge.context.new_page().goto('http://baidu.com')
    edge.stop()
