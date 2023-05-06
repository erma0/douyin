# 抖音采集

> [开源不易，若能帮助到您，可以请作者喝奶茶](#请作者喝奶茶)

`playwright`爬虫 + `Aria2`下载
（基于EDGE浏览器）

根据抖音各种链接采集作品并下载（支持图集作品）。

支持输入账号主页、音乐原声、作品的链接或文件路径。

支持下载账号的喜欢列表（需账号打开权限或登录本人账号）

## 声明

> 此程序为学习playwright爬虫及Python中调用Aria2的案例，仅供参考，请勿用于非法用途。

测试环境：`Win10/11 x64` + `Python3.9/11`

功能未全部测试，有问题请提交issue。


## 使用

1. 下载`dist`目录下两个文件
```
douyin.exe
aria2c.exe
```
2. 在程序所在目录打开命令行输入命令，或者直接双击打开douyin.exe后根据提示输入目标地址

- 使用帮助

```
PS > .\douyin.exe --help
Usage: douyin.exe [OPTIONS]

  命令行

Options:
  -t, --targets TEXT   必填。账号/话题/音乐的URL或文件路径（文件格式为一行一个URL），支持多次输入
  -l, --limit INTEGER  选填。最大采集数量，默认不限制
  -g, --grab           选填。只采集信息，不下载作品
  -d, --download       选填。直接下载采集完成的配置文件，用于采集时下载失败后重试
  -np, --notpost       选填。采集除了账号主页作品之外的链接（喜欢/音乐/搜索）不需要登录
  -like, --like        选填。采集账号喜欢作品，输入短链接时需指定，长链接时可指定或在长链接最后加[?showTab=like]
  -login, --login      选填。指定 是否需要登录，默认不登录，可以指定需用登录用于采集自己私密账号的信息
  --help               Show this message and exit.
```

- 使用例子（在程序所在目录打开命令行）
```
# 采集目标地址（主页）的全部作品
douyin.exe -t https://*/ 

# 采集目标地址（喜欢/音乐/搜索）的全部作品
douyin.exe -np -t https://*/ 

# 只采集目标作品信息，不下载作品
douyin.exe -g -t https://*/ 

# 直接下载采集过的目标地址（用于采集时下载出现报错的情况）
douyin.exe -d -t https://*/ 

# 限制数量采集，只采集目标地址的5个作品
douyin.exe -l 5 -t https://*/ 

# 采集目标用户的全部喜欢作品
douyin.exe -np -t https://*/ 长链接后带有[?showTab=like]
douyin.exe -np -like -t https://*/ 短链接

# 采集多个目标地址作品
douyin.exe -t https://*1/ -t https://*2/ 

# 采集文件[user.txt]中的多个目标地址的作品
douyin.exe -t ./user.txt

# 指定需登录采集目标地址的全部作品
douyin.exe -login -t https://*/ 

# 采集私密账号的喜欢（需登录本账号）
douyin.exe -t https://*/ -login -like -np
```


---

## 编译
先安装pyinstaller
```
pip install pyinstaller
```
然后直接打包EXE，图标可自行更换
```
pyinstaller -F .\douyin.py -i .\ico.ico 
```

## 请作者喝奶茶

![支付宝微信收款][1]

  [1]: https://erma0.gitee.io/images/qrcode/shouqianma.png

