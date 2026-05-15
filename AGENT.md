# AGENT.md — DouyinCrawler AI Agent 指南

为 AI 编程助手提供项目上下文，兼容 Claude (CLAUDE.md)、Cursor、Trae、OpenCode 等工具。

## 语言

对话和代码注释使用**中文**。

## 环境

- 操作系统：Windows 10/11，终端 PowerShell
- 后端包管理：**`uv`**（`uv sync` / `uv run` / `uv add`），禁止使用 pip
- 前端包管理：**`pnpm`**（`pnpm install` / `pnpm add` / `pnpm build`），禁止使用 npm / yarn

## 项目概述

抖音数据采集工具，支持 GUI（PyWebView）/ Web 服务 / CLI 三种模式。前后端分离架构。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python >=3.12, FastAPI, Uvicorn, PyWebView, Click |
| 前端 | React 18, TypeScript, Vite 6, Tailwind CSS 4 |
| 下载 | Aria2 (JSON-RPC) |
| 日志 | Loguru（替代 logging） |
| JSON | ujson（替代 json） |
| 测试 | pytest（后端）/ vitest（前端） |
| 打包 | PyInstaller / Nuitka |

## 项目结构

```
douyin/
├── main.py                    # GUI 入口（PyWebView）
├── pyproject.toml             # Python 依赖（uv 管理）
├── backend/
│   ├── server.py              # FastAPI 应用 & 入口
│   ├── cli.py                 # CLI 入口（Click）
│   ├── constants.py           # 全局常量
│   ├── settings.py            # 配置管理（单例）
│   ├── state.py               # 运行时状态（单例）
│   ├── sse.py                 # SSE 事件管理器
│   ├── lib/                   # 核心业务逻辑（与框架无关）
│   │   ├── douyin/            #   爬虫核心（crawler/client/parser/target/request/types）
│   │   ├── aria2_manager.py   #   Aria2 管理器
│   │   ├── cookies.py         #   Cookie 管理 & 验证
│   │   └── download.py        #   下载模块
│   ├── routers/               # API 路由（仅 HTTP 请求/响应）
│   ├── utils/                 # 通用工具函数
│   └── test/                  # 测试
├── frontend/
│   ├── types.ts               # 全局类型定义
│   ├── components/            # UI 组件
│   ├── hooks/                 # 自定义 Hooks
│   ├── services/
│   │   ├── api.ts             #   HTTP API 封装（底层）
│   │   ├── bridge.ts          #   前后端通信桥接（上层，带错误处理）
│   │   └── sseClient.ts       #   SSE 客户端
│   └── utils/                 # 工具函数
├── scripts/                   # 构建 & 部署脚本
└── config/                    # 运行时配置（gitignore）
```

## 架构

### 后端分层

| 层 | 目录 | 职责 | 约束 |
|----|------|------|------|
| 路由层 | `routers/` | HTTP 请求/响应 | 不含业务逻辑，调用 `lib/` 和 `state` |
| 业务层 | `lib/` | 核心业务逻辑 | 与框架无关，不依赖 FastAPI |
| 状态层 | `state.py` | 运行时状态 | 单例模式 |
| 配置层 | `settings.py` | 配置管理 | 单例模式，自动修复损坏配置 |
| 工具层 | `utils/` | 工具函数 | 纯函数优先 |

### 前端分层

| 层 | 目录 | 职责 |
|----|------|------|
| API 层 | `services/api.ts` | HTTP 请求封装 |
| 桥接层 | `services/bridge.ts` | 统一通信，错误处理，SSE 管理 |
| 组件层 | `components/` | UI 组件，通过 bridge 调用后端 |
| 类型层 | `types.ts` | 全局 TypeScript 类型 |

### 通信

- 前端通过 `bridge.ts` 调用后端，**禁止组件直接使用 `api.ts`**
- 实时数据通过 SSE 推送，后端任务在独立线程执行

## 编码规范

### Python

- `import ujson as json`、`from loguru import logger`
- 全局单例：`settings = SettingsManager()`、`state = AppState()`、`sse = SSEManager()`
- 常量集中在 `constants.py` 和 `types.py`，使用类分组（如 `APIEndpoint`、`FieldName`）
- 路由用 `APIRouter`，请求/响应用 Pydantic `BaseModel`
- 类型注解用 3.12+ 语法（`str | None` 而非 `Optional[str]`）

### TypeScript / React

- 函数式组件 + Hooks，不用 class 组件
- 类型集中在 `types.ts`，使用 Tailwind CSS
- API 调用统一通过 `bridge.ts`

### 通用

- 遵循现有代码风格，不引入未使用的依赖
- 优先选用成熟热门的第三方库
- 不添加不必要的注释

## 常用命令

```bash
# 后端
uv sync                                    # 安装依赖
uv run pytest backend/test/                # 测试
python -m backend.server                   # Web 服务
python -m backend.cli -u <URL> -l 10       # CLI
python main.py                             # GUI

# 前端（在 frontend/ 目录下）
pnpm install && pnpm dev                   # 安装 & 开发
pnpm build                                 # 构建
pnpm test                                  # 测试

# 完整启动
uv sync && cd frontend && pnpm install && pnpm build && cd .. && python -m backend.server
```

## 注意事项

- Cookie 是采集必要条件，通过 `config/settings.json` 或 CLI `-c` 提供
- 增量采集仅对 `post` 类型生效，需 `results_old` 非空且 `_has_received_data` 为真
- 验证码异常 (`VerifyCheckError`) 终止任务，需人工处理
- Aria2 需独立启动，默认端口 6800，密钥 `douyin_crawler_default_secret`
- 下载间隔 `downloadInterval`（0-60秒）可避免触发频率限制
- SSE 事件循环引用在首次连接时缓存，确保跨线程消息发送可靠
- 应用关闭时资源清理在后台线程执行，避免阻塞主线程
- 环境变量前缀 `DOUYIN_`（端口、主机、日志级别等）
