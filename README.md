![douyin](https://socialify.git.ci/erma0/douyin/image?description=1&font=Source%20Code%20Pro&forks=1&issues=1&language=1&owner=1&pattern=Circuit%20Board&stargazers=1&theme=Auto)

# ✨DouyinCrawler

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
- ✅ 指定作品数据
- ✅ 用户资料信息
- ✅ 用户主页作品
- ⚠️ 用户喜欢作品（功能异常）
- ⚠️ 用户收藏作品（仅能获取自己的收藏）
- ⚠️ 音乐原声作品（功能异常）
- ✅ 挑战话题作品
- ✅ 合集作品
- ✅ 用户关注列表
- ✅ 用户粉丝列表
- ⚠️ 关键词搜索作品（功能无效）
- ❌ 抖音号解析功能（暂无）

### 🎯 应用特性
- 🚀 **一键构建**：自动化构建脚本，智能检查依赖
- 📦 **批量操作**：支持文件路径输入，一行一个目标
- 🔄 **增量采集**：智能增量采集用户主页作品
- ⬇️ **批量下载**：集成Aria2，支持视频/图片批量下载
- 🎨 **可视化界面**：React桌面应用，实时日志显示
- ⚙️ **统一配置**：集中管理所有配置，自动同步
- ⚠️ **自动获取Cookie**：功能基本无效，需手动配置
- 🎉 **首次运行向导**：友好的欢迎界面，引导配置

## 🚀快速开始

> 📍测试环境：`Win10 x64` + `Python 3.12` + `Node.js 22.13.0`

### 环境要求

| 软件 | 版本要求 | 用途 |
|------|---------|------|
| Python | 3.8+ | 后端运行环境 |
| Node.js | 16+ | 前端构建工具 |
| Aria2 | 最新版 | 下载功能（可选） |

### 快速启动

- 从 [Releases](https://github.com/erma0/douyin/releases) 下载最新版本
- 解压后双击运行 `DouyinCrawler.exe`


详细使用说明请查看 [USAGE.md](USAGE.md)

## ⚠️ 已知问题

当前版本存在以下功能问题，计划在后续版本中修复：

1. **抖音号解析功能暂无** - 目前仅支持链接解析，不支持直接输入抖音号
2. **音乐功能异常** - 音乐原声作品采集可能失败
3. **收藏功能限制** - 仅能获取自己的收藏，无法获取他人收藏
4. **喜欢功能无效** - 用户喜欢作品采集可能失败
5. **自动获取Cookie无效** - 需要手动从浏览器复制Cookie
6. **搜索功能无效** - 关键词搜索功能可能无法正常工作

### 命令行模式

支持命令行方式采集数据，当前版本不一定兼容，请前往v4分支查看

## 🔨构建和打包

### 开发环境
```powershell
.\build.ps1           # 构建开发环境
.\build.ps1 -Clean    # 清理后重新构建
python main.py        # 运行
```

### 打包发布
```powershell
.\build-all.ps1                # 目录模式（推荐）
.\build-all.ps1 -Mode onefile  # 单文件模式
.\build-all.ps1 -Clean         # 清理后打包
```

**打包产物：**
- 单文件模式：`dist/DouyinCrawler.exe`
- 目录模式：`dist/DouyinCrawler/DouyinCrawler.exe`

## 📊 项目状态

### 开发进度
- ✅ 基础UI界面完成
- ✅ 用户主页作品采集
- ✅ 批量下载功能
- ✅ 自动化构建流程
- ⚠️ 部分功能存在问题（见上方已知问题）
- 🔄 持续优化中

### 技术栈
- **后端**: Python 3.8+, PyWebView, Loguru
- **前端**: React 18, TypeScript, Vite（纯AI生成）
- **下载**: Aria2
- **打包**: PyInstaller

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=erma0/douyin&type=Date)](https://star-history.com/#erma0/douyin&Date)