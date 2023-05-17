# 抖音采集

> [开源不易，若能帮助到您，可以请作者喝杯咖啡](#请作者喝杯咖啡)

`playwright`爬虫（基于EDGE/Chrome浏览器） + `Aria2`下载

根据抖音各种链接采集信息并下载。

---

支持采集账号主页作品、喜欢作品、音乐原声作品、搜索作品、关注列表、粉丝列表、合集作品

采集账号的喜欢列表需账号打开权限或登录本人账号、采集账号主页作品需登录任一个账号

为防止意外错误，默认采集任何类型链接都预先登录一个账号

支持输入文件路径批量操作（同一类型，一行一个目标地址）

账号主页作品支持增量采集

## 项目地址
[https://github.com/erma0/douyin](https://github.com/erma0/douyin)

## 声明
> 此程序为学习playwright爬虫及Python中调用Aria2的案例，仅供参考，请勿用于非法用途。

测试环境：`Win10/11 x64` + `Python3.8/11`

**功能未全部测试，有问题请提交issue，也可加Q群`738029092`反馈**


## 使用
1. Windows只需下载 [releases](https://github.com/erma0/douyin/releases) 或 `dist`目录中的两个文件
```
douyin.exe
aria2c.exe
```
Linux或macOS请从[官方地址下载对应的Aria2](https://github.com/aria2/aria2/releases)，然后运行源码或自行编译

2. 在程序所在目录打开命令行输入命令，或者Windows系统可以直接双击打开douyin.exe后根据提示输入目标地址

- 使用帮助

```
PS > ./douyin --help
Usage: douyin [OPTIONS]

  命令行

Options:
  -u, --urls TEXT                 必填。账号/话题/音乐的URL或文件路径（文件格式为一行一个URL），支持多次输入
  -n, --num INTEGER               选填。最大采集数量，默认不限制
  -g, --grab                      选填。只采集信息，不下载作品
  -d, --download                  选填。直接下载采集完成的配置文件，用于采集时下载失败后重试
  -l, --login                     选填。指定是否需要登录，默认要登录，用于采集主页作品、关注粉丝列表以及本人私密账号的信息
                                  ，也可避免一些莫名其妙的风控
  -t, --type [post|like|music|search|follow|fans|collection]
                                  选填。采集类型，支持[作品/喜欢/音乐/搜索/关注/粉丝/合集]，默认采集post作品，
                                  能够自动识别搜索/音乐/合集。采集账号主页作品或私密账号喜欢作品必须登录。
  -b, --browser [chrome|msedge|chrome-beta|msedge-beta|msedge-dev]
                                  选填。浏览器类型，默认使用稳定版EDGE，可选[chrome/msedge]，如需使用F
                                  irefox或WebKit请自行修改run函数。
  --help                          Show this message and exit.
```

- 使用例子（在程序所在目录打开命令行）
```
# 采集目标地址（主页）的全部作品（私密账号需登录本账号）
./douyin -u https://*/ 
./douyin -t post -u https://*/ 

# 采集目标地址（喜欢）的全部作品（私密账号需登录本账号）
./douyin -t like -u https://*/ 

# 采集目标地址（音乐）的全部作品
./douyin -u https://*/ 
./douyin -t music -u https://*/ 

# 采集目标地址（搜索）的全部作品
./douyin -u https://*/ 
./douyin -t search -u https://*/ 

# 采集目标地址（合集）的全部作品
./douyin -u https://*/ 
./douyin -t collect -u https://*/ 

# 采集目标地址（关注）的全部信息
./douyin -t follow -u https://*/ 

# 采集目标地址（粉丝）的全部信息
./douyin -t fans -u https://*/ 

# 只采集目标信息，不下载
./douyin -g -u https://*/ 

# 直接下载采集过的目标地址（用于采集时下载出现报错的情况）
./douyin -d -u https://*/ 

# 限制数量采集，只采集目标地址的5条结果
./douyin -n 5 -u https://*/ 

# 采集多个目标地址
./douyin -u https://*1/ -u https://*2/ 

# 采集文件[user.txt]中的多个目标地址
./douyin -u ./user.txt

# 指定不登录采集目标地址
./douyin -l -u https://*/ 

# 指定使用chrome采集
./douyin -b chrome -u https://*/ 
```

## 编译

1. 安装依赖
```
pip install -r .\requirements.txt
```
2. 安装pyinstaller
```
pip install pyinstaller
```
3. 设置环境变量（powershell）
```
$env:PLAYWRIGHT_BROWSERS_PATH="0"
```
4. 安装Edge或者Chrome
```
playwright install msedge
playwright install chromium
```
5. 打包EXE，图标可自行更换
```
pyinstaller -F ./douyin.py -i ./ico.ico 
```

**不能upx压缩，否则playwright无法启动**


## 请作者喝杯咖啡
---

![支付宝微信收款][1]

  [1]: https://erma0.gitee.io/images/qrcode/shouqianma.png

