import os
import sys
import threading
import time
from typing import List

import schedule
from PIL import Image
from pystray import Icon, MenuItem

from browser import Browser
from spider import Douyin


class API(Douyin):

    def download(self):
        """
        采集完成后，统一下载已采集的结果
        """
        if os.path.exists(self.aria2_conf):
            command = f"aria2c -c --console-log-level warn -d {self.down_path} -i {self.aria2_conf}"
            # os.system(command)  # system有输出，阻塞
            os.popen(command)  # popen无输出，不阻塞


def get_path(relative_path):
    try:
        # PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def start() -> None:
    print('任务开始')
    edge = Browser()
    with open('url.txt', 'r', encoding='utf-8') as f:
        lines: List[str] = f.readlines()
    for url in lines:
        a = API(edge.context, url)
        a.run()
        if a.results:
            if download:
                icon.notify(f"发现{len(a.results)}条新内容，开始下载", "发现新内容")
                a.download()
            else:
                icon.notify(f"发现{len(a.results)}条新内容", "发现新内容")
        else:
            # icon.notify("未发现新内容")
            pass
    edge.stop()
    print('任务结束')


def click_download(icon: Icon, item: MenuItem):
    global download
    download = not item.checked


def click_start(icon: Icon, item: MenuItem):
    global running
    running = not item.checked
    set_schedule(icon)


def click_exit(icon: Icon, item: MenuItem):
    global state
    state = False
    schedule.clear()
    icon.stop()


def set_schedule(icon: Icon):
    if running:
        schedule.every(10).minutes.do(start)
        schedule.run_all()
        if icon.HAS_NOTIFICATION:
            icon.title = '监控中'
            icon.notify(f'{int(schedule.idle_seconds())}秒后执行下一次任务', '抖音监控')
    else:
        schedule.clear()
        if icon.HAS_NOTIFICATION:
            icon.title = '未启动'
            icon.notify("停止监控", '抖音监控')


def on_start():
    set_schedule(icon)
    while state:
        schedule.run_pending()
        time.sleep(1)


state = True
running = True
download = False

menu = (
    MenuItem(text='开始', action=click_start, checked=lambda item: running, default=True),
    MenuItem(text='下载', action=click_download, checked=lambda item: download, default=False),
    MenuItem(text='退出', action=click_exit),
)
image: Image = Image.open(get_path("ico.ico"))
icon: Icon = Icon("监控", image, "监控中" if running else "未启动", menu)

# 使用icon.run(setup=on_start)时无法创建图标，只能单独跑一个线程
threading.Thread(target=on_start, daemon=True).start()

icon.run()
