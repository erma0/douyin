# -*- encoding: utf-8 -*-
'''
@File    :   download.py
@Time    :   2021年03月16日 17:27:19 星期二
@Author  :   erma0
@Version :   1.0
@Link    :   https://erma0.cn
@Desc    :   调用Aria2下载
'''
import os
import threading
import time

from aria2p import Client, Stats


class Download(Client):
    """
    Aria2下载类
    同级目录下需存在aria2c_64.exe及aria2c_32.exe
    直接投递任务，不用手动控制线程队列等
    参数dir为Aria2指定下载路径，可为相对路径或绝对路径
    为空时默认为 ./下载/
    参数类型str，需自行处理路径中的非法字符串（如|*等）
    非法字符串可通过Download.title2path()方法处理
    """
    def __init__(self, dir: str = None):
        # 初始化Aria2服务
        self.dir = dir if dir else '下载'  # 提供title2path方法，非法字符串由来源自行处理
        self.__server()
        super().__init__()  # 父类构造方法
        # 默认连接参数aria2p.Client(host="http://localhost", port=6800, secret="")

    def __server(self):
        """
        启动Aria2服务
        固定参数此时设置
        参考：https://aria2.github.io/manual/en/html/aria2c.html#options
        """
        if 'PROGRAMFILES(X86)' in os.environ:
            exe = "aria2c_64"
        else:
            exe = "aria2c_32"
        # 文件已存在则跳过下载的方法：
        # --auto-file-renaming=false 可行，但控制台使用会报错，不过报错不影响
        # -c 可行，且控制台不报错
        command = f"{exe} --dir={self.dir} -c --quiet --enable-rpc=true"
        os.popen(command)  # popen实现子进程打开程序，无DOS界面，不阻塞

    @staticmethod
    def title2path(title: str):
        """
        转为Windows合法文件名
        """
        # 非法字符
        lst = ['\r', '\n', '\\', '/', ':', '*', '?', '"', '<', '>', '|']
        # 非法字符处理方式1
        for key in lst:
            title = title.replace(key, '-')
        # 非法字符处理方式2
        # title = title.translate(None, ''.join(lst))
        # 文件名+路径长度最大255，汉字*2，取60
        if len(title) > 60:
            title = title[:60]
        return title.strip()

    def download(self, url: str, filename: str = None, options={}):
        """
        添加下载任务
        单个任务特有参数此时设置
        格式为 options = {'out': filename}
        参考：https://pawamoy.github.io/aria2p/reference/options/
        """
        if filename:
            options['out'] = filename  # 提供title2path方法，非法字符串由来源自行处理，因为此处传入文件名是带有路径的，无法一键处理
        return self.add_uri([url], options=options)

    def get_stat(self):
        """
        返回Aria2服务统计信息
        downloadSpeed: 下载速度 (byte/s)
        uploadSpeed: 上传速度(byte/s)
        numActive: 活动下载任务
        numWaiting: 等待队列任务
        numStopped: 已停止的任务（不超过--max-download-result 默认限制1000）
        numStoppedTotal: 已停止的任务（可超过--max-download-result 默认限制1000）
        """
        return Stats(self.get_global_stat())

    def start_listening(self,
                        on_start=None,
                        on_pause=None,
                        on_stop=None,
                        on_complete=None,
                        on_error=None,
                        on_bt_complete=None,
                        timeout: int = 5):
        """
        一键注册回调函数，不阻塞
        停止监听：self.stop_listening()
        不停止会阻塞进程，导致程序无法关闭
        """
        # 下载任务动态事件监听
        if on_complete is None:
            on_complete = self.__on_complete
        kwargs = {
            "on_download_start": on_start,
            "on_download_pause": on_pause,
            "on_download_stop": on_stop,
            "on_download_complete": on_complete,
            "on_download_error": on_error,
            "on_bt_download_complete": on_bt_complete,
            "timeout": timeout,
            "handle_signals": False
        }
        self.listener = threading.Thread(target=self.listen_to_notifications, kwargs=kwargs)
        self.listener.start()

    def start_loop(self, on_loop=None, timeout: int = 2):
        """
        循环监听进行中任务的状态
        每2秒一次
        回调函数接收当前下载List
            'gid': str,
            '文件名称': /下载/文件名.mp4,
            '下载速度': 1.25MB/s,
            '下载进度': 12.25%
        """
        threading.Thread(target=self.__on_loop, kwargs={'on_loop': on_loop, "timeout": timeout}).start()

    def stop_loop(self):
        self.loop = False

    def __on_loop(self, on_loop, timeout):
        self.loop = True
        while self.loop:
            if callable(on_loop):
                status = []
                info = self.tell_active(
                    keys=['gid', 'files', 'totalLength', 'completedLength', 'downloadSpeed'])

                for task in info:
                    length = int(task['totalLength'])
                    if length:
                        speed = int(task['downloadSpeed']) / 1024  # KB/s
                        unit = 'KB/s'
                        if speed >= 1000:
                            speed = speed / 1024  # MB/s
                            unit = 'MB/s'
                        speed = '{:.2f}{}'.format(speed, unit)
                        s = {
                            'gid': task['gid'],
                            '文件名称': task['files'][0]['path'],
                            '下载速度': speed,
                            '下载进度': '{:.2%}'.format(int(task['completedLength']) / length)
                        }
                        status.append(s)
                if status:
                    on_loop(status)  # 回传给回调函数
            time.sleep(timeout)

    def __on_complete(self, gid):
        """
        任务完成时的回调函数
        任务全部完成时结束监听
        """
        print(self.get_files(gid)[0]['path'], '下载完成')
        stat = self.get_stat()
        print('当前下载信息：', stat.__dict__['_struct'])
        if stat.num_active + stat.num_waiting == 0:  # 正在进行任务数=0，任务全部完成
            # 当前任务由此结束
            self.stop_listening()
            self.stop_loop()
            print('当前任务队列已完成，已退出监听')