# 抖音采集

> [请作者喝奶茶](#请作者喝奶茶)

`Python`爬虫 + `Aria2`下载

根据抖音各种链接采集作品并下载（支持图集作品）。

支持输入用户主页、话题挑战、音乐原声、作品的链接或文件路径。

支持下载用户的喜欢列表（需用户打开权限且并非所有用户可用）

## 声明

> 此程序为学习Python中调用Aria2的案例，仅供参考，请勿用于非法用途。

测试环境：`Win10/11 x64` + `Python3.11`

功能未全部测试，有问题请提交issue。


## 使用

1. 下载以下两个文件
```
main.exe
aria2c.exe
```
2. 打开命令行输入命令，或者直接双击打开main.exe后根据提示输入目标地址

- 使用帮助

```
PS > .\main.exe --help
Usage: main.exe [OPTIONS]

  命令行

Options:
  -t, --targets TEXT   必填。用户/话题/音乐/视频的URL或文件路径（文件格式为一行一个URL），支持多次输入
  -l, --limit INTEGER  选填。最大采集数量，默认不限制
  -c, --cookie TEXT    选填。网页cookie中s_v_web_id的值[verify_***]，默认不指定，从程序中重新获取
  -d, --download       选填。直接下载采集完成的配置文件，用于采集时下载失败后重试
  -like, --like        选填。只采集用户喜欢作品
  --help               Show this message and exit.
```

- 例子
```
# 采集目标地址的全部作品
main.exe -t https://*/ 

# 直接下载采集过的目标地址（用于采集时下载出现报错的情况）
main.exe -d -t https://*/ 

# 采集目标地址的5个新作品
main.exe -l 5 -t https://*/ 

# 采集目标用户的5个新喜欢作品
main.exe -like -l 5 -t https://*/ 

# 采集多个目标地址各自的5个新作品
main.exe -l 5 -t https://*1/ -t https://*2/ 

# 采集文件[user.txt]中的多个目标地址各自的5个新作品
main.exe -l 5 -t ./user.txt

# 指定cookie采集目标地址的全部作品
main.exe -c verify_*** -t https://*/ 
```


---

## 请作者喝奶茶

![支付宝微信收款][1]

  [1]: https://erma0.gitee.io/images/qrcode/shouqianma.png

