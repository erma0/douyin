# 使用指南

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

## ⚠️ 功能限制说明

### 当前版本限制
1. **抖音号解析** - 暂不支持直接输入抖音号，请使用完整链接
2. **音乐功能** - 音乐原声作品采集可能失败，建议使用其他功能
3. **收藏功能** - 只能获取自己账号的收藏，无法获取他人收藏
4. **喜欢功能** - 用户喜欢作品采集不稳定，可能返回空结果
5. **搜索功能** - 关键词搜索暂时无效，建议使用链接采集
6. **自动Cookie** - 自动获取Cookie功能无效，需手动配置

### 推荐使用功能
- ✅ **用户主页作品** - 功能稳定，推荐使用
- ✅ **指定作品** - 单个作品采集正常
- ✅ **挑战话题** - 话题作品采集正常
- ✅ **合集作品** - 合集采集功能正常

---

## 🍪 Cookie获取

Cookie是访问抖音数据的必要凭证，有效期约为60天。

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
| **指定作品** | 获取单个作品信息 | `https://www.douyin.com/video/7xxx` | ✅ 正常 |
| **用户主页** | 获取用户发布的作品 | `https://www.douyin.com/user/MS4wLjABxxx` | ✅ 正常 |
| **用户喜欢** | 获取用户点赞的作品 | 用户主页链接 | ⚠️ 功能异常 |
| **用户收藏** | 获取用户收藏的作品 | 用户主页链接 | ⚠️ 仅能获取自己的 |
| **音乐原声** | 获取使用该音乐的作品 | `https://www.douyin.com/music/7xxx` | ⚠️ 功能异常 |
| **挑战话题** | 获取话题下的作品 | `https://www.douyin.com/hashtag/xxx` | ✅ 正常 |
| **合集** | 获取合集中的作品 | 合集链接 | ✅ 正常 |
| **关键词搜索** | 搜索相关作品 | `风景` | ⚠️ 功能无效 |

### 采集数量限制

- **全部**：采集所有可用数据（可能很慢）
- **20/50/100条**：快速采集指定数量
- **自定义**：输入任意数量

### 批量操作

1. **全选/多选**
   - 点击"全选"勾选所有作品
   - 或单独勾选需要的作品

2. **导出数据**
   - 选中作品后点击"导出数据"
   - 将保存为JSON格式

3. **批量下载**
   - 选中作品后点击"批量下载"
   - 视频和图片将自动下载到指定目录
   
   **批量下载工作流程**：
   1. 采集完成后，系统会生成Aria2配置文件（保存在 `download` 目录）
   2. 点击"批量下载"按钮
   3. 前端读取配置文件并解析下载任务
   4. 通过JSON-RPC直接向Aria2提交任务
   5. 实时监控下载进度和状态
   6. 自动处理失败任务和错误情况
   
   **特性**：
   - ✅ 实时进度显示（每秒更新）
   - ✅ 支持断点续传
   - ✅ 自动跳过已存在文件
   - ✅ 智能错误处理和重试
   - ✅ 批量状态查询优化
   - ✅ 任务完成自动清理

### 设置选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| **Cookie** | 抖音登录凭证 | 空 |
| **下载路径** | 文件保存位置 | `~/Downloads/Douyin` |
| **最大重试次数** | 下载失败重试次数 | 3 |
| **最大并发数** | 同时下载任务数 | 3 |
| **Aria2主机** | Aria2服务地址 | localhost |
| **Aria2端口** | Aria2服务端口 | 6800 |
| **Aria2密钥** | Aria2RPC密钥 | 空 |

---

## ⚙️ 配置管理

### 配置文件位置

所有配置统一存储在 `config/` 目录：

```
config/
├── settings.json    # 主配置文件（所有设置）
├── cookie.txt       # Cookie备份（自动同步）
└── app.log          # 应用日志
```

### 配置加载机制

**优先级顺序**：
1. `settings.json` 中的配置（最高优先级）
2. `cookie.txt` 文本格式备份
3. 默认配置值

**自动处理**：
- 配置文件不存在 → 使用默认值并创建文件
- 配置文件损坏 → 使用默认值并记录错误
- 配置项缺失 → 自动补充默认值
- Cookie更新 → 自动同步到 `cookie.txt`

### 配置验证

应用会自动验证配置的有效性：

| 配置项 | 验证规则 |
|--------|---------|
| Cookie | 字符串类型 |
| 下载路径 | 有效的目录路径 |
| 重试次数 | 1-10之间的整数 |
| 并发数 | 1-10之间的整数 |
| 窗口尺寸 | 800-2000之间的整数 |
| Aria2端口 | 1-65535之间的整数 |

**无效配置处理**：
- 显示友好的错误提示
- 自动替换为默认值
- 记录到日志文件

### 手动编辑配置

可以直接编辑 `config/settings.json`：

```json
{
  "cookie": "你的Cookie",
  "downloadPath": "D:/Downloads/Douyin",
  "maxRetries": 5,
  "maxConcurrency": 5,
  "windowWidth": 1200,
  "windowHeight": 800,
  "aria2Host": "localhost",
  "aria2Port": 6800,
  "aria2Secret": "douyin_crawler_default_secret"
}
```

**注意**：
- 使用UTF-8编码
- 保持JSON格式正确
- 重启应用后生效

---

## ❓ 常见问题

### Q1: 提示"Cookie无效或已过期"

**原因：**
- Cookie已过期（约60天有效期）
- Cookie格式不正确
- 未登录抖音账号

**解决方法：**
1. 重新获取Cookie（参考上方步骤）
2. 确保Cookie完整复制
3. 检查是否包含必要字段

### Q2: 采集结果为空

**可能原因：**
- 目标链接错误
- Cookie无效
- 网络连接问题
- 目标账号设置了隐私保护

**解决方法：**
1. 检查链接是否正确
2. 更新Cookie
3. 检查网络连接
4. 尝试其他公开账号

### Q3: 下载失败

**可能原因：**
- 未安装Aria2
- Aria2服务未启动
- 网络问题
- 磁盘空间不足
- Cookie已过期
- 配置文件读取失败

**解决方法：**
1. 确认Aria2已安装：`aria2c --version`
2. 检查应用是否自动启动了Aria2服务（查看日志）
3. 验证Cookie是否有效（在设置中重新保存）
4. 检查配置文件是否存在：`download/collection_*.txt` 或 `download/user_*.txt`
5. 查看日志面板中的详细错误信息
6. 检查磁盘空间是否充足
7. 尝试减少并发数（在设置中调整）

**批量下载特定问题**：
- **Aria2连接失败**：应用会自动尝试启动Aria2，等待几秒后重试
- **配置文件不存在**：确保先完成采集任务，系统会自动生成配置文件
- **部分任务失败**：系统会继续处理其他任务，最后显示成功/失败统计
- **进度不更新**：等待1-2秒（轮询间隔），或检查浏览器控制台错误

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
- 前端未构建
- 构建路径错误
- dist目录缺失文件

**解决方法：**
```powershell
# 重新构建前端
cd frontend
pnpm build  # 或 npm run build

# 验证构建产物
ls dist/index.html
ls dist/assets/
```

### Q5: 某些功能无法使用

**已知问题：**
- 抖音号解析功能暂未实现
- 音乐、喜欢、搜索功能可能异常
- 收藏功能仅支持自己的账号
- 自动获取Cookie功能无效

**解决方法：**
1. 使用推荐的稳定功能（用户主页、指定作品、话题、合集）
2. 手动配置Cookie而非使用自动获取
3. 使用完整链接而非抖音号
4. 等待后续版本修复

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

---

## 🔧 故障排除

### 批量下载故障排查

#### 问题1：提示"Aria2服务连接失败"

**诊断步骤**：
1. 检查Aria2是否已安装
   ```powershell
   aria2c --version
   ```

2. 查看应用日志，确认Aria2启动状态
   ```powershell
   Get-Content config/app.log -Tail 50
   ```

3. 手动测试Aria2连接
   ```powershell
   # 检查端口是否开放
   Test-NetConnection -ComputerName localhost -Port 6800
   ```

**解决方案**：
- 如果未安装：运行 `.\scripts\setup\aria2.ps1` 或手动下载
- 如果端口被占用：在设置中更改Aria2端口
- 如果启动失败：查看 `config/app.log` 了解详情

#### 问题2：配置文件读取失败

**可能原因**：
- 采集任务未完成
- 配置文件被删除或移动
- 文件路径权限问题

**解决方案**：
1. 确认采集任务已完成（状态显示"完成"）
2. 检查 `download` 目录是否存在配置文件
   ```powershell
   ls download/*.txt
   ```
3. 如果文件不存在，重新运行采集任务

#### 问题3：任务提交失败

**诊断步骤**：
1. 打开浏览器开发者工具（F12）
2. 切换到Console标签
3. 查看错误信息

**常见错误**：
- `Unauthorized`：检查Aria2密钥设置是否正确
- `Network Error`：检查Aria2服务是否运行
- `Invalid URL`：配置文件格式可能有问题

**解决方案**：
- 验证设置中的Aria2配置（主机、端口、密钥）
- 重启应用重新初始化Aria2连接
- 检查配置文件格式是否正确

#### 问题4：下载进度不更新

**可能原因**：
- 轮询机制未启动
- 浏览器标签页被挂起
- JavaScript错误

**解决方案**：
1. 等待1-2秒（正常轮询间隔）
2. 确保浏览器标签页处于活动状态
3. 检查浏览器控制台是否有错误
4. 刷新页面重试

#### 问题5：部分任务失败

**这是正常现象**，可能原因：
- 文件已存在（会自动跳过）
- 下载链接已过期
- 网络临时中断
- Cookie已失效

**查看详情**：
1. 查看应用日志了解具体失败原因（`config/app.log`）
2. 对于失败的任务，可以：
   - 更新Cookie后重试
   - 手动下载失败的文件
   - 重新采集该作品

### 查看日志

应用程序运行时会生成详细日志：

1. **界面日志**
   - 点击左侧"日志"按钮
   - 查看实时运行日志
   - 支持按级别过滤（INFO/DEBUG/ERROR）

2. **文件日志**
   - 应用日志：`config/app.log`
   - 包含完整的运行记录和错误堆栈
   - 注：Aria2 不记录日志文件以节省磁盘空间

3. **浏览器控制台**
   - 按F12打开开发者工具
   - 查看前端JavaScript错误
   - 查看网络请求详情

### 调试模式

开启调试模式获取更多信息：

```powershell
python main.py debug
```

在浏览器中按 `F12` 查看控制台输出。

### 重置配置

如果设置出现问题，可以删除配置文件重置：

```powershell
# 删除配置文件
Remove-Item config/settings.json
Remove-Item config/cookie.txt

# 重新启动应用程序
python main.py
```

### 清理缓存

清理临时文件和缓存：

```powershell
# 使用构建脚本清理（推荐）
.\scripts\dev.ps1 -Clean

# 或手动清理
cd frontend
Remove-Item -Recurse -Force node_modules
Remove-Item -Recurse -Force dist
pnpm install  # 或 npm install
pnpm build    # 或 npm run build

# 清理Python缓存
cd ..
Remove-Item -Recurse -Force __pycache__
Remove-Item -Recurse -Force backend/__pycache__
Remove-Item -Recurse -Force backend/lib/__pycache__
```

### 联系支持

如果问题仍未解决：

1. 查看项目Issues：https://github.com/erma0/douyin/issues
2. 提交新Issue时请包含：
   - 错误信息截图
   - 日志文件内容
   - 操作系统版本
   - Python和Node.js版本

---

## 📝 注意事项

1. **合法使用**
   - 仅用于学习和研究
   - 不得用于商业用途
   - 尊重他人隐私和版权

2. **Cookie安全**
   - 不要分享你的Cookie
   - 定期更新Cookie
   - 退出登录后Cookie会失效

3. **下载限制**
   - 建议设置合理的并发数（3-5）
   - 避免短时间大量下载
   - 注意磁盘空间

4. **性能优化**
   - 采集大量数据时建议分批进行
   - 定期清理下载目录
   - 关闭不必要的后台程序

---

## 🎓 高级用法

### 命令行模式

除了GUI界面，还支持命令行操作：

```powershell
# 查看帮助
python backend/cli.py -h

# 采集用户主页作品
python backend/cli.py -u https://v.douyin.com/iybvCom1/

# 限制数量
python backend/cli.py -l 5 -u https://v.douyin.com/iybvCom1/

# 指定类型
python backend/cli.py -t like -u https://v.douyin.com/iybvCom1/
```

### 批量采集

创建文本文件，每行一个链接：

```text
https://www.douyin.com/user/MS4wLjABxxx
https://www.douyin.com/user/MS4wLjAByyy
https://www.douyin.com/user/MS4wLjABzzz
```

然后运行：

```powershell
python backend/cli.py -u urls.txt
```

### 自定义配置路径

可以指定自定义的配置目录：

```powershell
# 设置环境变量
$env:DOUYIN_CONFIG_DIR = "D:/MyConfig"

# 启动应用
python main.py
```

### 调试和日志

**启用调试模式**：
```powershell
python main.py debug
```

调试模式特性：
- 前端热更新（需要先启动 `pnpm dev`）
- 详细的控制台输出
- 浏览器开发者工具可用

**查看日志**：
```powershell
# 实时查看日志
Get-Content config/app.log -Wait

# 查看最后100行
Get-Content config/app.log -Tail 100
```

### 批量下载技术细节

**架构说明**：

```
前端 (React)
    ↓ 读取配置文件
    ↓ 解析任务列表
    ↓ JSON-RPC调用
Aria2服务
    ↓ 多线程下载
    ↓ 断点续传
CDN服务器
```

**工作流程**：
1. **配置文件生成**：采集完成后，后端生成Aria2输入文件格式的配置
2. **文件解析**：前端读取配置文件，按3行一组解析（URL、dir、out）
3. **任务提交**：逐个调用 `aria2.addUri` 提交下载任务
4. **进度监控**：每秒调用 `aria2.tellStatus` 查询任务状态
5. **任务清理**：完成或失败的任务自动从跟踪列表移除

**配置文件格式**：
```
https://example.com/video1.mp4
  dir=/path/to/download
  out=video1.mp4
https://example.com/video2.mp4
  dir=/path/to/download
  out=video2.mp4
```

**错误处理策略**：
- Aria2连接失败 → 显示明确提示，引导用户检查服务
- 配置文件不存在 → 提示先完成采集任务
- 部分任务失败 → 继续处理其他任务，最后显示统计
- 文件已存在 → 自动跳过（依赖Aria2的continue选项）

**性能优化**：
- 批量状态查询：一次RPC调用查询所有任务
- 智能轮询：无任务时自动停止轮询
- 内存管理：任务完成后立即清理跟踪信息

### 性能优化建议

**大量数据采集**：
- 分批采集，避免一次性采集过多
- 使用限制参数控制数量
- 定期清理结果缓存

**批量下载优化**：
- 合理设置并发数（建议3-5）
  - 网络好：可设置为5-8
  - 网络一般：保持3-5
  - 网络差：降低到1-3
- 避免短时间大量下载（可能触发限流）
- 监控磁盘空间和网络带宽
- 使用Aria2的断点续传功能
- 定期清理下载目录

**Aria2配置优化**：
```json
{
  "maxRetries": 5,           // 网络不稳定时增加重试
  "maxConcurrency": 5,       // 网络好时可增加到5-8
  "aria2Host": "localhost",  // 保持本地，安全性更好
  "aria2Port": 6800,         // 默认端口，避免冲突
  "aria2Secret": "your_secret" // 建议设置密钥
}
```

**应用配置优化**：
```json
{
  "windowWidth": 1200,    // 大屏幕可增加窗口尺寸
  "windowHeight": 800,
  "downloadPath": "D:/Downloads/Douyin"  // 使用SSD提高速度
}
```

---

## 📚 相关资源

- [项目主页](https://github.com/erma0/douyin)
- [Aria2文档](https://aria2.github.io/)
- [PyWebView文档](https://pywebview.flowrl.com/)
- [React文档](https://react.dev/)

---

**祝使用愉快！** 🎉
