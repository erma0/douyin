import os
import sys
import threading
import time

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
    with open('url.txt', 'r', encoding='utf-8') as f:
        lines: list[str] = f.readlines()
    for url in lines:
        a = API(edge.context, url)
        a.run()
        if a.results:
            icon.notify(f"发现{len(a.results)}条新内容，开始下载。", "发现新内容")
            a.download()
    print('任务结束')


def click_menu(icon: Icon, item: MenuItem):
    global state
    state = not item.checked
    set_schedule(icon)


def on_exit(icon: Icon, item: MenuItem):
    global state, run
    state = False
    run = False
    schedule.clear()
    icon.stop()


def set_schedule(icon: Icon):
    if state:
        schedule.every(10).minutes.do(start)
        global first
        first = True
        if icon.HAS_NOTIFICATION:
            icon.title = '监控中'
            icon.notify(f'{int(schedule.idle_seconds())}秒后执行下一次任务', '抖音监控')
    else:
        if icon.HAS_NOTIFICATION:
            icon.title = '未启动'
            icon.notify("停止监控", '抖音监控')
        schedule.clear()


edge = Browser()
state = True
first = True
run = True

menu = (MenuItem(text='开始', action=click_menu, checked=lambda item: state, default=True), MenuItem(text='退出', action=on_exit))
image: Image = Image.open(get_path("ico.ico"))
icon: Icon = Icon("监控", image, "监控中" if state else "未启动", menu)
threading.Thread(target=icon.run).start()
time.sleep(1)

set_schedule(icon)

while run:
    if first:
        first = False
        schedule.run_all()
    else:
        schedule.run_pending()
    time.sleep(1)
