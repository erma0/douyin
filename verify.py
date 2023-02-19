import time
import requests
import webview
from webview import Window


def webview_start(window: Window):
    window.hide()
    web_id = ''
    while not web_id:
        for c in window.get_cookies():
            if c.get('s_v_web_id'):
                web_id = c.get('s_v_web_id').value
                print('已取回验证码', web_id)
                break
        time.sleep(0.5)

    window.show()
    window.restore()

    while True:
        res = requests.get(
            'https://m.douyin.com/web/api/v2/aweme/post/',
            headers={
                'User-Agent':
                'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
                'Cookie': 's_v_web_id=' + web_id
            })
        if res.content:
            print('通过验证', web_id)
            break
        else:
            print('需要手动过验证码', web_id)
            time.sleep(0.5)
    window.destroy()


def verify():
    """
    手动过验证码
    """

    window = webview.create_window(
        # hidden=True,# 有bug，隐藏窗口不能恢复，使用最小化代替
        minimized=True,  # 最小化
        frameless=True,  # 无边框
        width=255,
        height=255,  # 1080p 315，2160p 255
        title='Test Douyin',
        url='https://m.douyin.com/share/user/MS4wLjABAAAA58dutoFIvpxGtw-0QXJ4AI5OKtd_-KHt-HZDtfFnvy4')

    webview.start(
        func=webview_start,
        args=window,
        # private_mode=False,
        user_agent=
        'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
    )


verify()
