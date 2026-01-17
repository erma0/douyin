## 项目概述

抖音爬虫（DouyinCrawler）是一个基于 Python 的桌面/web/api应用，用于采集抖音平台的视频、用户信息等数据。项目采用前后端分离架构，前端使用 Web 技术，后端使用 FastAPI 框架，通过 PyWebView 打包成桌面应用，或提供api服务供web或其他应用调用。

## 技术栈

### 后端

- **Python 3.12**
- **FastAPI** - Web 框架
- **PyWebView** - 桌面窗口
- **Aria2** - 下载管理器
- **Loguru** - 日志管理
- **ujson** - 替代json库

### 前端

- **React** - UI 框架
- **TypeScript** - 类型系统
- **Vite** - 构建工具
- **pnpm** - 包管理工具

### 测试

- **pytest** - 测试框架

## 项目结构规范

- **lib/**：核心业务逻辑，与框架无关
- **routers/**：API 路由，仅处理 HTTP 请求
- **utils/**：通用工具函数
- **test/**：单元测试

- 后端代码位于 `backend/` 目录
- 前端代码位于 `frontend/` 目录
- 测试文件放在对应模块的 `test/` 目录下
- 全局配置文件 `config/settings.json`
- 前端请求统一封装在 `frontend/services/api.ts` 中，再在 `frontend/services/bridge.ts` 中二次封装，提供类型检查和错误处理

## 资源链接

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [PyWebView 文档](https://pywebview.flowrl.com/)
- [Aria2 文档](https://aria2.github.io/)
