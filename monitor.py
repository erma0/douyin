import time
from typing import List

import schedule

from browser import Browser
from spider import Douyin

edge = Browser()


def start() -> None:
    print('开始一轮')
    with open('url.txt', 'r', encoding='utf-8') as f:
        lines: List[str] = f.readlines()
    for url in lines:
        a = Douyin(edge.context, url)
        a.run()
        if a.results:
            a.download()
    print('结束一轮')


def main():
    print('监控启动')
    schedule.every(10).minutes.do(start)
    # schedule.every().hour.do(start)
    # schedule.every().day.at("10:30").do(start)
    # schedule.every().monday.do(start)
    # schedule.every().wednesday.at("13:15").do(start)
    # schedule.every().day.at("12:42", "Europe/Amsterdam").do(start)
    # schedule.every().minute.at(":17").do(start)
    schedule.run_all()
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
