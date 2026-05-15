# API 文档

**[English](#english) | [简体中文](#简体中文)**

---

## 简体中文

基础地址：`http://localhost:8000`

### 任务管理 `/api/task`

#### 启动任务

```
POST /api/task/start
```

请求体：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `type` | `string` | 是 | - | 任务类型：`post`/`favorite`/`collection`/`hashtag`/`music`/`mix`/`aweme`/`search`/`following`/`follower` |
| `target` | `string` | 是 | - | 目标链接或搜索关键词 |
| `limit` | `int` | 否 | `0` | 采集数量限制，0 表示不限制 |
| `filters` | `object` | 否 | `null` | 筛选条件（仅搜索类型） |

响应：

```json
{
  "task_id": "task_xxx",
  "status": "running"
}
```

#### 取消任务

```
POST /api/task/cancel
```

请求体：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | `string` | 是 | 要取消的任务 ID |

响应：

```json
{
  "task_id": "task_xxx",
  "status": "cancelled"
}
```

#### 获取任务状态

```
GET /api/task/status?task_id=task_xxx
```

查询参数：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | `string` | 否 | 任务 ID，不提供则返回所有任务 |

响应：

```json
[
  {
    "id": "task_xxx",
    "type": "post",
    "target": "https://www.douyin.com/user/xxx",
    "status": "running",
    "progress": 10,
    "result_count": 5,
    "error": null,
    "created_at": 1700000000.0,
    "updated_at": 1700000001.0
  }
]
```

任务状态值：`running`、`cancelling`、`cancelled`、`completed`、`error`

#### 获取采集结果

```
GET /api/task/results/{task_id}
```

路径参数：

| 字段 | 类型 | 说明 |
|------|------|------|
| `task_id` | `string` | 任务 ID |

响应：采集结果列表

---

### 设置管理 `/api/settings`

#### 获取设置

```
GET /api/settings
```

响应：

```json
{
  "cookie": "",
  "userAgent": "",
  "downloadPath": "./download",
  "maxRetries": 3,
  "maxConcurrency": 5,
  "windowWidth": 1200,
  "windowHeight": 800,
  "enableIncrementalFetch": true,
  "aria2Host": "localhost",
  "aria2Port": 6800,
  "aria2Secret": "",
  "enableDownloadTitle": false,
  "enableDownloadCover": false,
  "downloadInterval": 0
}
```

#### 保存设置

```
POST /api/settings
```

支持部分更新，仅传需要修改的字段。

请求体：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `cookie` | `string` | - | Cookie |
| `userAgent` | `string` | - | 自定义 UA |
| `downloadPath` | `string` | 非空 | 下载路径 |
| `maxRetries` | `int` | 0-10 | 最大重试次数 |
| `maxConcurrency` | `int` | 1-10 | 最大并发数 |
| `windowWidth` | `int` | 800-3840 | 窗口宽度 |
| `windowHeight` | `int` | 600-2160 | 窗口高度 |
| `enableIncrementalFetch` | `bool` | - | 启用增量采集 |
| `aria2Host` | `string` | - | Aria2 主机地址 |
| `aria2Port` | `int` | 1-65535 | Aria2 端口 |
| `aria2Secret` | `string` | - | Aria2 密钥 |
| `enableDownloadTitle` | `bool` | - | 下载标题文本 |
| `enableDownloadCover` | `bool` | - | 下载封面图片 |
| `downloadInterval` | `float` | 0-60 | 下载间隔（秒） |

响应：

```json
{
  "status": "ok",
  "message": "设置已保存"
}
```

#### 检查首次运行

```
GET /api/settings/first-run
```

响应：

```json
{
  "is_first_run": true
}
```

---

### Aria2 管理 `/api/aria2`

#### 获取 Aria2 配置

```
GET /api/aria2/config
```

响应：

```json
{
  "host": "localhost",
  "port": 6800,
  "secret": "douyin_crawler_default_secret"
}
```

#### 获取 Aria2 连接状态

```
GET /api/aria2/status
```

响应：

```json
{
  "connected": true
}
```

#### 启动 Aria2 服务

```
POST /api/aria2/start
```

响应：

```json
{
  "status": "ok",
  "message": "Aria2 已启动"
}
```

#### 获取配置文件路径

```
GET /api/aria2/config-path?task_id=task_xxx
```

查询参数：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | `string` | 否 | 任务 ID，不提供则返回最新任务 |

响应：

```json
{
  "config_path": "C:\\Users\\xxx\\download\\task_xxx\\aria2.conf"
}
```

---

### 文件操作 `/api/file`

#### 打开文件夹

```
POST /api/file/open-folder
```

请求体：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `folder_path` | `string` | 是 | 文件夹路径 |

响应：

```json
{
  "success": true
}
```

#### 检查文件是否存在

```
POST /api/file/check-exists
```

请求体：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file_path` | `string` | 是 | 文件路径 |

响应：

```json
{
  "exists": true
}
```

#### 读取配置文件

```
POST /api/file/read-config
```

仅支持 `.txt` 文件。

请求体：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file_path` | `string` | 是 | 配置文件路径 |

响应：

```json
{
  "content": "文件内容..."
}
```

#### 查找本地已下载文件

```
GET /api/file/find-local/{work_id}
```

路径参数：

| 字段 | 类型 | 说明 |
|------|------|------|
| `work_id` | `string` | 作品 ID |

响应：

```json
{
  "found": true,
  "video_path": "video/xxx.mp4",
  "images": ["image/xxx_1.jpg", "image/xxx_2.jpg"]
}
```

#### 媒体文件流服务

```
GET /api/file/media/{file_path:path}
```

路径参数：

| 字段 | 类型 | 说明 |
|------|------|------|
| `file_path` | `string` | 相对于下载目录的文件路径 |

支持 Range 请求，用于视频播放。直接返回文件流。

---

### 系统工具 `/api/system`

#### 获取剪贴板内容

```
GET /api/system/clipboard
```

响应：

```json
{
  "text": "剪贴板内容"
}
```

#### 打开 URL

```
POST /api/system/open-url
```

请求体：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | `string` | 是 | 要打开的 URL |

响应：

```json
{
  "status": "ok",
  "message": "已打开"
}
```

#### 登录获取 Cookie

```
POST /api/system/cookie-login
```

仅 GUI 模式可用，弹出登录窗口。

响应：

```json
{
  "success": true,
  "cookie": "sessionid=xxx; ttwid=xxx; ...",
  "user_agent": "Mozilla/5.0 ...",
  "error": ""
}
```

---

### 实时通信 `/api/events`

#### SSE 事件流

```
GET /api/events
```

SSE（Server-Sent Events）实时推送，心跳间隔 30 秒。

事件类型：

| 事件 | 数据字段 | 说明 |
|------|----------|------|
| `task_result` | `task_id`, `data`, `total` | 采集结果 |
| `task_status` | `task_id`, `status`, `progress`, `result_count`, `detected_type`, `is_incremental` | 任务状态变化 |
| `task_error` | `task_id`, `error` | 任务错误 |
| `log` | `id`, `timestamp`, `level`, `message` | 日志消息 |
| `ping` | - | 心跳 |

---

## English

Base URL: `http://localhost:8000`

### Task Management `/api/task`

#### Start Task

```
POST /api/task/start
```

Request body:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `type` | `string` | Yes | - | Task type: `post`/`favorite`/`collection`/`hashtag`/`music`/`mix`/`aweme`/`search`/`following`/`follower` |
| `target` | `string` | Yes | - | Target URL or search keyword |
| `limit` | `int` | No | `0` | Collection limit, 0 = unlimited |
| `filters` | `object` | No | `null` | Filter conditions (search type only) |

Response:

```json
{
  "task_id": "task_xxx",
  "status": "running"
}
```

#### Cancel Task

```
POST /api/task/cancel
```

Request body:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_id` | `string` | Yes | Task ID to cancel |

Response:

```json
{
  "task_id": "task_xxx",
  "status": "cancelled"
}
```

#### Get Task Status

```
GET /api/task/status?task_id=task_xxx
```

Query parameters:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_id` | `string` | No | Task ID, returns all tasks if omitted |

Response:

```json
[
  {
    "id": "task_xxx",
    "type": "post",
    "target": "https://www.douyin.com/user/xxx",
    "status": "running",
    "progress": 10,
    "result_count": 5,
    "error": null,
    "created_at": 1700000000.0,
    "updated_at": 1700000001.0
  }
]
```

Task status values: `running`, `cancelling`, `cancelled`, `completed`, `error`

#### Get Collection Results

```
GET /api/task/results/{task_id}
```

Path parameters:

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | `string` | Task ID |

Response: Collection results list

---

### Settings Management `/api/settings`

#### Get Settings

```
GET /api/settings
```

Response:

```json
{
  "cookie": "",
  "userAgent": "",
  "downloadPath": "./download",
  "maxRetries": 3,
  "maxConcurrency": 5,
  "windowWidth": 1200,
  "windowHeight": 800,
  "enableIncrementalFetch": true,
  "aria2Host": "localhost",
  "aria2Port": 6800,
  "aria2Secret": "",
  "enableDownloadTitle": false,
  "enableDownloadCover": false,
  "downloadInterval": 0
}
```

#### Save Settings

```
POST /api/settings
```

Supports partial updates — only send fields you want to change.

Request body:

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| `cookie` | `string` | - | Cookie |
| `userAgent` | `string` | - | Custom User-Agent |
| `downloadPath` | `string` | non-empty | Download path |
| `maxRetries` | `int` | 0-10 | Max retries |
| `maxConcurrency` | `int` | 1-10 | Max concurrency |
| `windowWidth` | `int` | 800-3840 | Window width |
| `windowHeight` | `int` | 600-2160 | Window height |
| `enableIncrementalFetch` | `bool` | - | Enable incremental fetch |
| `aria2Host` | `string` | - | Aria2 host |
| `aria2Port` | `int` | 1-65535 | Aria2 port |
| `aria2Secret` | `string` | - | Aria2 secret |
| `enableDownloadTitle` | `bool` | - | Download title text |
| `enableDownloadCover` | `bool` | - | Download cover image |
| `downloadInterval` | `float` | 0-60 | Download interval (seconds) |

Response:

```json
{
  "status": "ok",
  "message": "Settings saved"
}
```

#### Check First Run

```
GET /api/settings/first-run
```

Response:

```json
{
  "is_first_run": true
}
```

---

### Aria2 Management `/api/aria2`

#### Get Aria2 Config

```
GET /api/aria2/config
```

Response:

```json
{
  "host": "localhost",
  "port": 6800,
  "secret": "douyin_crawler_default_secret"
}
```

#### Get Aria2 Connection Status

```
GET /api/aria2/status
```

Response:

```json
{
  "connected": true
}
```

#### Start Aria2 Service

```
POST /api/aria2/start
```

Response:

```json
{
  "status": "ok",
  "message": "Aria2 started"
}
```

#### Get Config File Path

```
GET /api/aria2/config-path?task_id=task_xxx
```

Query parameters:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_id` | `string` | No | Task ID, defaults to latest task |

Response:

```json
{
  "config_path": "C:\\Users\\xxx\\download\\task_xxx\\aria2.conf"
}
```

---

### File Operations `/api/file`

#### Open Folder

```
POST /api/file/open-folder
```

Request body:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `folder_path` | `string` | Yes | Folder path |

Response:

```json
{
  "success": true
}
```

#### Check File Exists

```
POST /api/file/check-exists
```

Request body:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file_path` | `string` | Yes | File path |

Response:

```json
{
  "exists": true
}
```

#### Read Config File

```
POST /api/file/read-config
```

Only `.txt` files are supported.

Request body:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file_path` | `string` | Yes | Config file path |

Response:

```json
{
  "content": "file content..."
}
```

#### Find Local Downloaded File

```
GET /api/file/find-local/{work_id}
```

Path parameters:

| Field | Type | Description |
|-------|------|-------------|
| `work_id` | `string` | Work ID |

Response:

```json
{
  "found": true,
  "video_path": "video/xxx.mp4",
  "images": ["image/xxx_1.jpg", "image/xxx_2.jpg"]
}
```

#### Media File Streaming

```
GET /api/file/media/{file_path:path}
```

Path parameters:

| Field | Type | Description |
|-------|------|-------------|
| `file_path` | `string` | File path relative to download directory |

Supports Range requests for video playback. Returns file stream directly.

---

### System Utilities `/api/system`

#### Get Clipboard Content

```
GET /api/system/clipboard
```

Response:

```json
{
  "text": "clipboard content"
}
```

#### Open URL

```
POST /api/system/open-url
```

Request body:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | `string` | Yes | URL to open |

Response:

```json
{
  "status": "ok",
  "message": "Opened"
}
```

#### Login to Get Cookie

```
POST /api/system/cookie-login
```

GUI mode only. Opens a login window.

Response:

```json
{
  "success": true,
  "cookie": "sessionid=xxx; ttwid=xxx; ...",
  "user_agent": "Mozilla/5.0 ...",
  "error": ""
}
```

---

### Real-time Communication `/api/events`

#### SSE Event Stream

```
GET /api/events
```

SSE (Server-Sent Events) real-time push, heartbeat interval 30 seconds.

Event types:

| Event | Data Fields | Description |
|-------|-------------|-------------|
| `task_result` | `task_id`, `data`, `total` | Collection result |
| `task_status` | `task_id`, `status`, `progress`, `result_count`, `detected_type`, `is_incremental` | Task status change |
| `task_error` | `task_id`, `error` | Task error |
| `log` | `id`, `timestamp`, `level`, `message` | Log message |
| `ping` | - | Heartbeat |
