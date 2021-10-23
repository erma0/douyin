# -*- encoding: utf-8 -*-
'''
@File    :   ui.py
@Time    :   2021年04月02日 21:19:56 星期五
@Author  :   erma0
@Version :   1.0
@Link    :   https://erma0.cn
@Desc    :   UI界面
'''
from douyin import Task
import webview


class API(Task):
    """
    前后端交互接口
    """
    def __init__(self):
        """
        初始化
        """

    def init(self, type='user', limit=0):
        """
        在UI中，类的初始化无法传参，所以需要重新定义初始化
        """
        super().__init__(type=type, limit=limit)

    def download(self, target):
        window.evaluate_js('app.loading=true;')
        super().download(target)
        window.evaluate_js('app.setData();app.openInfo();app.loading=false;')
        # print('开始下载')

    def videos(self):
        return self.douyin.videosL

    # def status(self):
    #     """
    #     任务状态
    #     是否采集完成：has_more
    #     是否下载完成：finish
    #     """
    #     status = {'has_more': self.douyin.has_more, 'finish': self.douyin.finish}
    #     return status

    def _on_loop(self, info: list):
        """
        重写监听回调函数
        UI显示实时下载进度
        """
        for i in info:
            gid = i['gid']
            video = self.douyin.videosL[self.douyin.gids[gid]]
            video['status'] = float(i['下载进度'][:-1]) / 100  # 12.34% => 0.1214
        window.evaluate_js('app.setData();')
        # UI不用频繁刷新来显示正在下载列表，等某任务下载完成时再显示就行了
        # window.evaluate_js('app.setData();app.pagingScrollTopLeft({});'.format(self.douyin.gids[gid] - 5))

    def _on_finish(self, gid):
        """
        重写下载完成事件
        用于UI提示当前任务[下载完成]
        任务完成时结束监听
        """
        self.num += 1
        print(self.num)

        self.douyin.videosL[self.douyin.gids[gid]]['status'] = 1
        # 任务下载完成时显示到UI中就行了[pagingScrollTopLeft无效，无法切换]
        window.evaluate_js('app.setData();')
        # window.evaluate_js('app.setData();app.pagingScrollTopLeft({});'.format(self.douyin.gids[gid]))

        # print(self.douyin.aria2.get_files(gid)[0]['path'], '任务完成（成功/停止/失败）')
        stat = self.douyin.aria2.get_stat()
        # print('当前下载信息：', stat.__dict__['_struct'])

        if stat.num_active + stat.num_waiting == 0:  # 正在进行任务数=0，任务全部完成
            # 当前任务由此结束
            self.douyin.finish = True
            print('当前任务队列下载完成')
            window.evaluate_js('app.openSuccess()')
            self.douyin.aria2.stop_listening()
            self.douyin.aria2.stop_loop()

    def openFile(self):
        # print('py', "打开文件")
        file_types = ('文本文件 (*.txt)', '全部文件 (*.*)')
        result = window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types)
        print('py 打开文件', result)
        return result[0]


if __name__ == "__main__":
    api = API()
    window = webview.create_window(
        title='标题',  # 标题
        url='ui/index.html',  # 本地文件或网络URL
        js_api=api,  # 暴露api对象，或使用flask等服务创建的对象
        width=735,  # 窗口宽；好像和网页中大小不一样，网页中大小为620*470px
        height=510,  # 窗口高
        resizable=True,  # 是否可以缩放窗口
        frameless=False)  # 窗口无边框
    webview.start(debug=True)
