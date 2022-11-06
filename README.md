# 抖音采集

> [花几秒钟领个支付宝红包吧~](#支持作者)

`Python`取数据 + `Aria2`下载

根据抖音各种**链接**或各种**ID**，通过网页接口采集视频作品，并下载作品到本地。

支持用户主页链接或sec_uid、话题挑战和音乐原声链接或ID。

## 使用须知

> 此程序为学习Python中调用Aria2的案例，仅供参考，请勿用于非法用途。

2021.10.22测试仍能正常运行。

测试环境：`Win10_x64` + `Python3.8`

~~支持采集喜欢列表~~（只有部分用户可用，原因不明）

有问题请提交issue，在下面评论看不到。

## TODO

- [x] 采集用户作品
- [x] 调用Aria2下载
- [x] 话题/原声作品采集
- [x] 喜欢作品采集
- [x] 导入文件批量采集
- [x] 命令行调用
- [x] ~~用pywebview写界面~~ 界面写了个大概，后来没时间弄了，放弃了
- [x] ~~打包exe~~ 直接装个[Python](https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe)吧

## 使用

### 安装依赖

在程序目录打开命令行，输入
```
pip install -r requirements.txt
```

### 使用命令行：`exec.py`

1. 直接运行可查看命令列表，或使用`-h`参数查看帮助
    ```
    python exec.py
    python exec.py download -h
    ```
2. 可选参数
    ```
    --type  指定下载类型，默认值：--type=user（采集用户作品）
    --limit 指定采集数量，默认值：--limit=0（采集全部）
    ```
3. 命令行例子
    - 采集某用户全部作品：
    ```
    python exec.py download 用户主页链接或secuid
    ```
    - 采集某用户喜欢的前10个作品：
    ```
    python exec.py download 用户主页链接或secuid --type=like --limit=10
    ```
    - 采集某音乐原声前10个作品：
    ```
    python exec.py download 音乐链接或ID --type=music --limit=10
    ```
    - 采集某话题挑战全部作品：
    ```
    python exec.py download 话题挑战链接或ID --type=challenge
    ```
    - 批量采集某文件内全部用户作品：
    ```
    python exec.py download_batch 文件路径（文件内一行一个链接或id） --type=user
    ```

---

## 支持作者

### 扫码领支付宝红包

![红包码][2]

### 赞助支持

![支付宝微信收款][1]

  [1]: https://erma0.gitee.io/images/qrcode/shouqianma.png
  [2]: https://erma0.gitee.io/images/qrcode/hongbao.jpg

