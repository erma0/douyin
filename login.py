import json
from playwright.sync_api import Playwright, sync_playwright, BrowserContext


def save_cookies(context: BrowserContext):
    cookies = context.cookies()
    cookies.append({"name": "LOGIN_STATUS", "value": "1", "domain": ".douyin.com", "path": "/"})
    cookies.append({"name": "SEARCH_RESULT_LIST_TYPE", "value": "%22multi%22", "domain": ".douyin.com", "path": "/"})
    s = {"cookies": cookies}
    with open("./auth.json", 'w', encoding='utf-8') as f:
        json.dump(s, f, ensure_ascii=False)
    # context.storage_state(path="./auth.json")
    return cookies


def login(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(channel="msedge", headless=False)
    page = browser.new_page()
    with page.expect_response("https://www.douyin.com/passport/sso/login/**", timeout=0):
        page.goto("https://sso.douyin.com/", wait_until='domcontentloaded')
    print('登录成功')
    cookies = save_cookies(page.context)
    browser.close()
    return cookies


if __name__ == "__main__":
    with sync_playwright() as playwright:
        login(playwright)
