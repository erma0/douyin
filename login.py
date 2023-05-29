import ujson as json

from browser import Browser, BrowserContext


def check_login(context: BrowserContext):
    url = 'https://sso.douyin.com/passport/sso/check_login/'
    res = context.request.get(url).json()
    _login: bool = res.get("has_login", False)
    return _login


def save_cookies(context: BrowserContext):
    cookies = context.cookies()
    cookies.append({"name": "LOGIN_STATUS", "value": "1", "domain": ".douyin.com", "path": "/"})
    cookies.append({"name": "SEARCH_RESULT_LIST_TYPE", "value": "%22multi%22", "domain": ".douyin.com", "path": "/"})
    s = {"cookies": cookies}
    with open("./auth.json", 'w', encoding='utf-8') as f:
        json.dump(s, f, ensure_ascii=False)
    # context.storage_state(path="./auth.json")
    return cookies


def login() -> None:
    edge = Browser(channel="msedge", need_login=False, headless=False)
    page = edge.context.new_page()
    with page.expect_response("https://www.douyin.com/passport/sso/login/**", timeout=0):
        page.goto("https://sso.douyin.com/", wait_until='domcontentloaded')
    print('登录成功')
    cookies = save_cookies(page.context)
    edge.stop()
    return cookies


if __name__ == "__main__":
    login()
