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
- ✅ 关注用户（仅cli模式，需目标开放权限）
- ✅ 粉丝用户（仅cli模式，需目标开放权限）

### 🎯 应用特性
- 🔄 **增量采集**：智能增量采集用户主页作品
- ⬇️ **批量下载**：集成 Aria2，支持视频/图片批量下载
- 📄 **标题下载**：可选同时下载作品标题文本文件
- 🖼️ **封面下载**：可选同时下载作品封面图片
- 🎨 **多种模式**：GUI 桌面应用 / Web 服务 / cli命令行
- 🌐 **RESTful API**：v2.0 提供完整的 HTTP API
- 🔧 **跨平台支持**：Windows / macOS / Linux

## 📸 界面展示

![软件界面](./docs/images/main.png)

## 🚀快速开始

### 环境要求

> 📍测试环境：`Win10 x64` + `Python 3.12` + `Node.js 22.13.0` + `uv 0.9+`

### Windows 用户

从 [Releases](https://github.com/erma0/douyin/releases) 下载，解压后运行 `DouyinCrawler.exe`

### Web 服务（Docker / 全平台）

```bash
# Docker（推荐）
docker compose up -d

# 或手动启动
uv sync 
cd frontend && pnpm install && pnpm build && cd ..
python -m backend.server
```

浏览器访问 `http://localhost:8000`

### 命令行（cli模式）

```bash
python -m backend.cli -u https://www.douyin.com/user/xxx -l 20
```

📖 详细使用说明请查看 [USAGE.md](USAGE.md)

## 🔨构建和打包

```powershell
# 交互式菜单
.\quick-start.ps1

# 或直接打包
.\scripts\build\pyinstaller.ps1
```

脚本目录结构：
```
scripts/
├── build/          # 打包脚本 (PyInstaller / Nuitka)
├── setup/          # 环境配置 (uv / aria2)
└── dev.ps1         # 开发环境构建
```

## 📊 技术栈

- **后端**: Python 3.12, FastAPI, PyWebView
- **前端**: React 18, TypeScript, Vite
- **下载**: Aria2
- **打包**: PyInstaller / Nuitka

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=erma0/douyin&type=Date)](https://star-history.com/#erma0/douyin&Date)