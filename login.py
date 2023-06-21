import ujson as json

from browser import Browser, BrowserContext


class Login(object):

    def __init__(self, context: BrowserContext = None):
        self.context = context

    def _login(self, url_login="https://sso.douyin.com/", url_ok="https://www.douyin.com/passport/sso/login"):
        page = self.context.new_page()
        with page.expect_request_finished(lambda request: url_ok in request.url, timeout=0):
            page.goto(url_login, wait_until='domcontentloaded')
        cookies = self.get_cookies()
        page.close()
        return cookies

    def check_login(self):
        url = 'https://sso.douyin.com/check_login/'
        res = self.context.request.get(url).json()
        is_login: bool = res.get("has_login", False)
        if is_login:  # 重新登录（有些朋友偶尔出现无法采集的情况，重新登陆后就正常，所以加入此功能）
            # self.context.request.get(res.get("redirect_url", url))
            self._login(url_login=res.get("redirect_url", "https://sso.douyin.com/"))
        return is_login

    @staticmethod
    def save_cookies(cookies: list, key: list[str] = None):
        """
        默认保存全部cookie，可选仅保存指定key
        """
        if key:
            session = []
            for i in cookies:
                if i['name'] in key:
                    session.append({"name": i['name'], "value": i['value'], "domain": ".douyin.com", "path": "/"})
        else:
            session = cookies

        s = {"cookies": session}
        with open("./auth.json", 'w', encoding='utf-8') as f:
            json.dump(s, f, ensure_ascii=False)

    def get_cookies(self):
        cookies = self.context.cookies()
        cookies.append({"name": "LOGIN_STATUS", "value": "1", "domain": ".douyin.com", "path": "/"})
        cookies.append({"name": "SEARCH_RESULT_LIST_TYPE", "value": "%22multi%22", "domain": ".douyin.com", "path": "/"})
        self.save_cookies(cookies)
        # self.save_cookies(cookies, key=['toutiao_sso_user_ss'])  # 'sessionid'
        return cookies

    def new_login(self) -> None:
        edge = Browser(channel="msedge", need_login=False, headless=False)
        self.context = edge.context
        cookies = self._login()
        edge.stop()
        return cookies


if __name__ == "__main__":
    Login().new_login()
