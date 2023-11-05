![douyin](https://socialify.git.ci/erma0/douyin/image?description=1&font=Source%20Code%20Pro&forks=1&issues=1&language=1&name=1&owner=1&pattern=Circuit%20Board&stargazers=1&theme=Auto)

# ✨抖音爬虫

> ❤️[开源不易，欢迎star⭐，若能帮助到您，可以请作者喝杯咖啡☕](#请作者喝杯咖啡)

## 📢声明

> 本仓库为学习`playwright`爬虫、命令行调用`Aria2`及`FastAPI/AMIS/Eel`实现`WEBUI`的案例，仅用于测试和学习研究，禁止用于商业用途或任何非法用途。

> 任何用户直接或间接使用、传播本仓库内容时责任自负，本仓库的贡献者不对该等行为产生的任何后果负责。

> 如果相关方认为该项目的代码可能涉嫌侵犯其权利，请及时通知删除相关代码。
---

## 🏠项目地址

> [https://github.com/erma0/douyin](https://github.com/erma0/douyin)

## 🍬功能

采集账号主页作品、喜欢作品、收藏作品、音乐原声作品、搜索作品、关注列表、粉丝列表、合集作品、单个作品

PS.

- 采集账号主页作品需登录任一个账号
- 采集账号的喜欢列表需账号打开权限或登录本人账号
- 支持输入文件路径批量操作（同一类型，一行一个目标地址）
- 支持增量采集账号主页作品

## ‍🚩待办

> 💡欢迎PR或建议

- [ ] 精简功能，修复一下bug
- [ ] GUI - Eel

## 🌳文件结构

```ps
douyin                           
├─ dist                          # 编译输出目录
│  ├─ aria2c.exe                    # aria2下载器
│  ├─ douyin.exe                    # 主程序
├─ results                       # 网页返回数据样板
├─ browser.py                    # 浏览器启闭
├─ exec.py                       # 命令行解析
├─ ico.ico                       # 图标logo
├─ login.py                      # 登录
├─ README.md                     # 项目说明
├─ requirements.txt              # 依赖库
├─ spider.py                     # 爬虫核心代码
└─ test.py                       # 随手测试代码
```

---

## 🚀使用

> 📍测试环境：`Win10/11 x64` + `Python3.8/11`。

> 📭**功能未全部测试，有问题请提交issue，也可加Q群`738029092`反馈（请提供测试链接以便复现问题）**
>
### 🍔主程序

1. Windows只需下载 [releases](https://github.com/erma0/douyin/releases) 或 `dist`目录中的两个文件

    > ⚠️ Linux或macOS请从[官方地址下载对应的Aria2](https://github.com/aria2/aria2/releases)，然后自行修改源码调试运行

    - douyin.exe
    - aria2c.exe

2. 在程序所在目录打开命令行输入命令，或者Windows系统可以直接双击打开douyin.exe后根据提示输入目标地址

    - 🐔使用帮助

    ```ps
    
    ```

    - 🏀使用例子（在程序所在目录打开命令行）

    ```ps
    # 采集本账号的喜欢
    ./douyin -t like

    # 采集本账号的收藏
    ./douyin -t favorite

    # 采集本账号的关注
    ./douyin -t follow

    # 采集本账号的粉丝
    ./douyin -t fans

    # 查询抖音号信息（可查精确粉丝数）
    ./douyin -t id -u xinhuashe

    # 采集目标地址（主页）的全部作品
    ./douyin -u https://*/ 
    ./douyin -t post -u https://*/ 

    # 采集目标地址（喜欢）的全部作品(需目标地址开放权限)
    ./douyin -u https://*/*?showTab=like
    ./douyin -t like -u https://*/ 

    # 采集目标地址（音乐）的全部作品
    ./douyin -u https://*/ 
    ./douyin -t music -u https://*/ 

    # 采集目标地址（搜索）的全部作品
    ./douyin -u 搜索关键字
    ./douyin -u https://*/ 
    ./douyin -t search -u https://*/ 

    # 采集目标地址（合集）的全部作品
    ./douyin -u https://*/ 
    ./douyin -t collection -u https://*/ 

    # 采集目标地址（关注）的全部信息
    ./douyin -t follow -u https://*/ 

    # 采集目标地址（粉丝）的全部信息
    ./douyin -t fans -u https://*/ 

    # 只采集目标信息，不下载
    ./douyin -g -u https://*/ 

    # 直接下载采集过的目标地址（用于上次下载出错时）
    ./douyin -d -u https://*/ 

    # 限制数量采集，只采集目标地址的5条结果
    ./douyin -n 5 -u https://*/ 

    # 采集多个目标地址
    ./douyin -u https://*1/ -u https://*2/ 

    # 采集文件[user.txt]中的多个目标地址
    ./douyin -u ./user.txt

    # 指定不登录采集目标地址
    ./douyin -l -u https://*/ 

    # 在下载配置文件中使用msToken参数（解决下载0kb问题）
    ./douyin -m -u https://*/ 

    # 指定使用chrome采集
    ./douyin -b chrome -u https://*/ 

    # 采集单个作品
    ./douyin -u id
    ./douyin -u https://*/ 
    ```

    > 💡手动使用aria2c下载

    ```ps
    aria2c -c --console-log-level warn -d ./下载目录 -i 生成的下载配置文件.txt
    ```

## 🔨编译

> ❗**不能upx压缩，否则playwright无法启动**

1. 安装依赖

    ```ps
    pip install -U -r ./requirements.txt
    ```

2. 安装pyinstaller

    ```ps
    pip install pyinstaller
    ```

3. 设置环境变量（powershell）

    ```ps
    $env:PLAYWRIGHT_BROWSERS_PATH="0"
    ```

4. 安装Edge或者Chrome

    ```ps
    playwright install msedge
    playwright install chromium
    ```

5. 打包EXE，图标可自行更换

    - 编译主程序

    ```ps
    pyinstaller -F ./exec.py -i ./ico.ico -n douyin
    ```

> ⚠️截至目前`playwright`最新版，Windows编译时需自行[修改`playwright`源码](https://github.com/microsoft/playwright-python/issues/1778#issuecomment-1565339726)才能隐藏命令行黑窗口，也就是在`playwright/_impl/_transport.py`文件的`create_subprocess_exec` 函数中加上下面这行内容，或者直接使用`1.29.0`版本的`playwright`

```python
creationflags=134217728 if sys.platform == "win32" else 0,
```
<!-- playwright codegen --channel msedge https://v.douyin.com/U3eAtXx/ -->

## ☕请作者喝杯咖啡

![支付宝微信收款][1]

  [1]: https://erma0.cn/images/qrcode/shouqianma.png
