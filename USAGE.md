# 使用指南

**[English](./USAGE_EN.md) | [Tiếng Việt](./USAGE_VI.md) | 简体中文**

## 📋 目录

- [安装Aria2](#安装aria2)
- [Cookie获取](#cookie获取)
- [功能说明](#功能说明)
- [配置管理](#配置管理)
- [常见问题](#常见问题)
- [故障排除](#故障排除)
- [高级用法](#高级用法)

---

## � 安装开Aria2

批量下载功能需要Aria2支持：

```powershell
# 方式1：使用项目脚本（推荐）
.\scripts\setup\aria2.ps1

# 方式2：手动安装
# 1. 下载 https://github.com/aria2/aria2/releases
# 2. 解压到项目的 aria2 目录或添加到系统PATH
# 3. 验证：aria2c --version
```


## 🍪 Cookie获取

Cookie是获取数据的必要凭证。

### 获取步骤

1. **打开抖音网页版**
   - 访问 https://www.douyin.com
   - 登录你的抖音账号

2. **打开开发者工具**
   - 按 `F12` 键
   - 或右键点击页面 → 选择"检查"

3. **切换到Network标签**
   - 点击顶部的 `Network`（网络）标签
   - 刷新页面（F5）

4. **查找请求**
   - 在过滤器中输入 `aweme`
   - 找到任意一个 `post/?` 或类似的请求

5. **复制Cookie**
   - 点击该请求
   - 在右侧找到 `Request Headers`（请求标头）
   - 找到 `Cookie:` 字段
   - 双击Cookie值全选并复制

6. **保存Cookie**
   - 在应用程序中点击设置图标
   - 粘贴Cookie到输入框
   - 点击保存

![示意图](./docs/images/image.png)

### Cookie验证

有效的Cookie应该包含以下字段：
- `sessionid`
- `ttwid`
- `__ac_nonce`

如果Cookie缺少这些字段，可能无法正常工作。

---

## 🎯 功能说明

### 采集类型

| 类型 | 说明 | 输入示例 | 状态 |
|------|------|----------|------|
| **单个作品** | 获取单个作品信息 | `https://www.douyin.com/video/7xxx` | ✅ 正常 |
| **用户主页** | 获取用户发布的作品 | `https://www.douyin.com/user/MS4wLjABxxx` | ✅ 正常 |
| **用户喜欢** | 获取用户点赞的作品 | 用户主页链接 | ✅ 正常 |
| **用户收藏** | 获取用户收藏的作品 | 用户主页链接 | ✅ 正常 |
| **话题挑战** | 获取话题下的作品 | `https://www.douyin.com/hashtag/xxx` | ✅ 正常 |
| **合集** | 获取合集中的作品 | 合集链接 | ✅ 正常 |
| **音乐原声** | 获取使用该音乐的作品 | `https://www.douyin.com/music/7xxx` | ✅ 正常 |
| **关键词搜索** | 搜索相关作品 | `风景` | ✅ 正常 |

### 采集数量限制

- **全部**：采集所有可用数据（可能很慢）
- **20/50/100条**：快速采集指定数量
- **自定义**：输入任意数量

### 批量下载

点击"一键下载全部"按钮，系统会自动：
1. 读取采集结果的Aria2配置文件
2. 通过JSON-RPC向Aria2提交下载任务
3. 实时显示下载进度和状态
4. 自动处理失败任务和错误

**特性**：
- ✅ 实时进度显示
- ✅ 支持断点续传
- ✅ 自动跳过已存在文件
- ✅ 智能错误处理和重试

### 设置选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| **Cookie** | 抖音登录凭证 | 空 |
| **下载路径** | 文件保存位置 | `./download` |
| **最大重试次数** | 下载失败重试次数 | 3 |
| **最大并发数** | 同时下载任务数 | 5 |
| **Aria2主机** | Aria2服务地址 | localhost |
| **Aria2端口** | Aria2服务端口 | 6800 |
| **Aria2密钥** | Aria2RPC密钥 | douyin_crawler_default_secret |



## ❓ 常见问题

### Q1: 提示"Cookie无效或已过期"

**原因：**
- Cookie已过期
- Cookie格式不正确
- 未登录抖音账号

**解决方法：**
1. 重新获取Cookie（参考上方步骤）
2. 确保Cookie完整复制
3. 检查是否包含必要字段

### Q2: 采集结果为空

**解决方法：**
1. 检查链接是否正确
2. 更新Cookie
3. 检查网络连接

### Q3: 下载失败

**解决方法：**
1. 确认Aria2已安装：`aria2c --version`
2. 查看日志面板中的详细错误信息
3. 检查磁盘空间是否充足
4. 尝试减少并发数（在设置中调整）

### Q4: 应用程序启动失败

**可能原因：**
- 依赖未安装
- 端口被占用
- 前端未构建
- 配置文件损坏

**解决方法：**
```powershell
# 方法1：使用构建脚本（推荐）
.\scripts\dev.ps1 -Clean

# 方法2：手动重新安装
pip install -r requirements.txt
cd frontend
pnpm install  # 或 npm install
pnpm build    # 或 npm run build
```

### Q5: 前端页面空白

**可能原因：**
- 防火墙阻止访问
- 前端未构建
- 构建路径错误
- dist目录缺失文件

**解决方法：**
1. 检查防火墙设置，确保允许应用程序访问网络（通常使用专用网络配置即可）
2. 确认前端已构建
3. 检查构建路径是否正确

### Q5: 某些功能无法使用

**已知问题：**
- 抖音号解析功能暂未实现
- 喜欢、收藏功能需目标开发权限，部分目标无法获取
- 自动获取Cookie功能已被删除

**解决方法：**
1. 使用推荐的稳定功能
2. 手动配置Cookie
3. 使用完整链接

### Q6: 配置丢失或重置

**可能原因：**
- 配置文件被删除
- 配置文件格式错误
- 权限问题

**解决方法：**
```powershell
# 检查配置文件
cat config/settings.json

# 如果文件损坏，删除后重新启动
Remove-Item config/settings.json
python main.py
```

#### 问题5：部分任务失败

**这是正常现象**，可能原因：
- 文件已存在（会自动跳过）
- 下载链接已过期
- 网络临时中断
- Cookie已失效


### 联系支持

如果问题仍未解决：

1. 查看项目Issues：https://github.com/erma0/douyin/issues
2. 提交新Issue时请包含：
   - 目标链接
   - 错误信息
   - 软件版本
   - 系统和环境版本

## 🎓 高级用法

### 命令行模式

除了GUI界面，还支持功能完整的命令行操作：

#### 基础用法

```powershell
# 查看帮助
python backend/cli.py -h

# 采集用户主页作品
python backend/cli.py -u https://www.douyin.com/user/MS4wLjABxxx

# 限制采集数量
python backend/cli.py -u https://www.douyin.com/user/MS4wLjABxxx -l 20

# 仅采集数据，不下载文件
python backend/cli.py -u https://www.douyin.com/user/MS4wLjABxxx --no-download
```

#### 采集类型

```powershell
# 用户主页作品（默认）
python backend/cli.py -u https://www.douyin.com/user/MS4wLjABxxx -t post

# 用户喜欢作品
python backend/cli.py -u https://www.douyin.com/user/MS4wLjABxxx -t favorite

# 用户收藏作品
python backend/cli.py -u https://www.douyin.com/user/MS4wLjABxxx -t collection

# 话题作品
python backend/cli.py -u https://www.douyin.com/hashtag/xxx -t hashtag

# 音乐作品
python backend/cli.py -u https://www.douyin.com/music/7xxx -t music

# 合集作品
python backend/cli.py -u 合集链接 -t mix

# 单个作品
python backend/cli.py -u https://www.douyin.com/video/7xxx -t aweme

# 关键词搜索
python backend/cli.py -u "美食" -t search
```

#### 搜索筛选

```powershell
# 搜索并按最新排序
python backend/cli.py -u "美食" -t search --sort-type 2

# 搜索一周内的视频
python backend/cli.py -u "美食" -t search --publish-time 7

# 搜索1-5分钟的视频
python backend/cli.py -u "美食" -t search --filter-duration "1-5"

# 组合筛选条件
python backend/cli.py -u "美食" -t search --sort-type 2 --publish-time 7 --filter-duration "1-5"
```

**筛选参数说明：**
- `--sort-type`: 0=综合，1=最多点赞，2=最新
- `--publish-time`: 0=不限，1=一天内，7=一周内，180=半年内
- `--filter-duration`: 空=不限，0-1=1分钟以下，1-5=1-5分钟，5-10000=5分钟以上

#### Cookie配置

```powershell
# 方式1：命令行指定
python backend/cli.py -u 目标链接 -c "your_cookie_string"

# 方式2：配置文件（推荐）
# 在 config/settings.json 中设置 cookie 字段
python backend/cli.py -u 目标链接
```

#### 批量采集

创建文本文件（如 `urls.txt`），每行一个链接：

```text
https://www.douyin.com/user/MS4wLjABxxx
https://www.douyin.com/user/MS4wLjAByyy
https://www.douyin.com/hashtag/xxx
https://www.douyin.com/music/7xxx
```

然后运行：

```powershell
python backend/cli.py -u urls.txt -l 50
```

#### 自定义下载路径

```powershell
python backend/cli.py -u 目标链接 -p "D:/Downloads/douyin"
```

---

**祝使用愉快！** 🎉
