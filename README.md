![douyin](https://socialify.git.ci/erma0/douyin/image?description=1&font=Source%20Code%20Pro&forks=1&issues=1&language=1&owner=1&pattern=Circuit%20Board&stargazers=1&theme=Auto)

# ✨DouyinCrawler

**[English](./README_EN.md) | [Tiếng Việt](./README_VI.md) | 简体中文**

> ❤️[开源不易，欢迎star⭐](#star-history)

## 📢声明

> 本项目初衷为学习`python`爬虫、命令行调用`Aria2`及`python`实现`WebUI`的案例，后用于尝试体验AI编程（前端及前后端交互部分纯AI生成），应用程序功能为获取抖音平台上公开的信息，仅用于测试和学习研究，禁止用于商业用途或任何非法用途。
>
> 任何用户直接或间接使用、传播本仓库内容时责任自负，本仓库的贡献者不对该等行为产生的任何后果负责。
>
> **如果相关方认为该项目的代码可能涉嫌侵犯其权利，请及时联系我删除相关代码**。
>
> 使用本仓库的内容即表示您同意本免责声明的所有条款和条件。如果你不接受以上的免责声明，请立即停止使用本项目。

---

## 🏠项目地址

> [https://github.com/erma0/douyin](https://github.com/erma0/douyin)

## 🍬功能特性

### 📊 数据采集
- ✅ 单个作品数据
- ✅ 用户主页作品
- ✅ 用户喜欢作品（需目标开放权限）
- ✅ 用户收藏作品（需目标开放权限）
- ✅ 话题挑战作品
- ✅ 合集作品
- ✅ 音乐原声作品
- ✅ 关键词搜索作品

### 🎯 应用特性
- 🔄 **增量采集**：智能增量采集用户主页作品
- ⬇️ **批量下载**：集成Aria2，支持视频/图片批量下载
- 🎨 **可视化界面**：React桌面应用，实时日志显示
- 🎉 **首次运行向导**：友好的欢迎界面，引导配置

## 📸 界面展示

![软件界面](./docs/images/main.png)

## 🚀快速开始

### 环境要求

> 📍测试环境：`Win10 x64` + `Python 3.12` + `Node.js 22.13.0` + `uv 0.9+`


### 快速启动

- 从 [Releases](https://github.com/erma0/douyin/releases) 下载最新版本
- 解压后双击运行 `DouyinCrawler.exe`

详细使用说明请查看 [USAGE.md](USAGE.md)

## 🔨构建和打包

### 📁 脚本目录

所有构建脚本已整理到 `scripts/` 目录：

```
scripts/
├── build/              # 打包脚本
│   ├── pyinstaller.ps1      # PyInstaller 打包
│   ├── pyinstaller-dir.spec # 目录模式配置
│   ├── pyinstaller-onefile.spec # 单文件配置
│   └── nuitka.ps1           # Nuitka 打包
├── setup/              # 环境配置
│   ├── uv.ps1               # 配置 uv 环境
│   ├── aria2.ps1            # 下载 aria2
│   └── pyinstaller.ps1      # 单独安装 PyInstaller
└── dev.ps1             # 开发环境构建
```

### 🚀 快速开始

#### 方式 1：使用快速启动菜单（推荐）

```powershell
.\quick-start.ps1
```

提供交互式菜单，按数字选择操作。

#### 方式 2：手动执行脚本

详见脚本目录


### 📦 打包说明

#### PyInstaller（推荐）
- ✅ 打包速度快（1-2分钟）
- ✅ 支持目录模式和单文件模式
- ✅ 兼容性好
- 📦 体积：目录模式 ~36MB，单文件 ~17MB

#### Nuitka（高性能）
- ✅ 编译为原生代码，性能更好
- ✅ 启动速度快
- ⚠️ 编译时间长（3-5分钟）
- ⚠️ 需要 MinGW64 编译器（自动下载）
- 📦 体积：目录模式 ~45MB，单文件 ~12MB

#### 打包产物
- **目录模式**：`dist/DouyinCrawler/DouyinCrawler.exe`（启动快）
- **单文件模式**：`dist/DouyinCrawler.exe`（便于分发）
- **发布包**：`release/DouyinCrawler_*.zip`（自动生成）

## 关于linux桌面

linux桌面运行当前项目主要的阻碍在于发行版中未必有开箱即用的webview，需要自己安装。本项目使用pywebview创建窗口，pywebview的官方文档说明了[每个系统如何安装pywebview所需的依赖](https://pywebview.flowrl.com/guide/installation.html#linux)，其中就包括linux。


对于ubuntu desktop，你可以参考下面这段不保证一定能工作的命令，原谅此处文档的含糊不清，我也不是非常清楚gtk，cairo这些东西是如何工作的。

```bash
# 如果没有安装python3-dev 需要安装一下，里面似乎包含pycairo，pywebview会用到。
sudo apt install build-essential python3-dev

# 同样是pywebview的依赖
sudo apt install libcairo2-dev libgirepository1.0-dev


# 构建前端，如果没有node需要先自己安装，这里就不演示安装node了

cd frontend
pnpm run install && pnpm run build
```


## 服务器运行

`python -m backend.server` 启动fastapi服务器，打开 `localhost:8000` 以访问和pywebview相同的界面，但是功能略有些残缺。

命令行参数和环境变量如下，环境变量会覆盖命令行参数，方便容器部署的情况下修改配置。

```text
运行方式:
    python -m backend.server              # 使用默认配置
    python -m backend.server --port 9000  # 指定端口
    python -m backend.server --dev        # 开发模式（启用热重载）
    python -m backend.server --cookie "xxx"  # 设置 Cookie

环境变量（前缀 DOUYIN_）:
    DOUYIN_PORT          监听端口（默认: 8000）
    DOUYIN_HOST          监听地址（默认: 127.0.0.1）
    DOUYIN_DEV           开发模式（默认: false）
    DOUYIN_LOG_LEVEL     日志级别（默认: info）
    DOUYIN_COOKIE        抖音 Cookie
```

### 为什么服务器功能是残缺的

本项目的架构一开始就为webview设计，并且api.py直接依赖pywebview 的 window对象，要实现服务器功能就必须手动在普通的前后端项目中模拟pywebview的通信接口，目前没有完全模拟。

pywebview 通信接口参考：
1. https://pywebview.flowrl.com/api/#window-pywebview
2. https://pywebview.flowrl.com/guide/interdomain.html

当前的服务器工作方式是：
1. fastapi托管前端静态文件
2. 打开界面时，如果`window.pywebview`不可用，则认为当前运行在浏览器环境而不是pywebview环境，根据不同的环境选择相应的bridge
3. 对于浏览器环境，实现了一个新的httpBridge，完全与原bridge保持类型一致，新的httpBridge向fastapi发送请求调用后端api
4. 后端任务完成后需要执行回调向前端发送消息，这部分通过SSE完成，httpBridge与fastapi会建立SSE连接，服务器模块创建了一个FakeWindow并依赖注入`API`，当API执行window.evaluate_js，FakeWindow实际上会通过SSE发送消息给前端，前端的httpBridge执行该jscode。

后续如果需要模拟更多的pywebview接口，在httpBridge和FakeWindow的基础上添加即可。

## 📊 技术栈

- **后端**: Python 3.12, PyWebView
- **前端**: React 18, TypeScript, Vite
- **下载**: Aria2
- **打包**: PyInstaller / Nuitka

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=erma0/douyin&type=Date)](https://star-history.com/#erma0/douyin&Date)