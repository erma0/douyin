# User Guide

**English | [Tiếng Việt](./USAGE_VI.md) | [简体中文](./USAGE.md)**

## 📋 Table of Contents

- [Install Aria2](#install-aria2)
- [Get Cookie](#get-cookie)
- [Feature Description](#feature-description)
- [Configuration Management](#configuration-management)
- [FAQ](#faq)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

---

## Install Aria2

Batch download function requires Aria2 support:

```powershell
# Method 1: Use project script (Recommended)
.\scripts\setup\aria2.ps1

# Method 2: Manual Installation
# 1. Download https://github.com/aria2/aria2/releases
# 2. Extract to the project's aria2 directory or add to system PATH
# 3. Verify: aria2c --version
```


## 🍪 Get Cookie

Cookie is the necessary credential for obtaining data.

### Acquisition Steps

1. **Open Douyin Web Version**
   - Visit https://www.douyin.com
   - Log in to your Douyin account

2. **Open Developer Tools**
   - Press `F12` key
   - Or right-click on the page → Select "Inspect"

3. **Switch to Network Tab**
   - Click on the top `Network` tab
   - Refresh the page (F5)

4. **Find Request**
   - Input `aweme` in the filter
   - Find any `post/?` or similar request

5. **Copy Cookie**
   - Click on the request
   - Find `Request Headers` on the right
   - Find the `Cookie:` field
   - Double-click the Cookie value to select all and copy

6. **Save Cookie**
   - Click the settings icon in the application
   - Paste the Cookie into the input box
   - Click Save

![Schematic Diagram](./docs/images/image.png)

### Cookie Verification

A valid Cookie should contain the following fields:
- `sessionid`
- `ttwid`
- `__ac_nonce`

If the Cookie is missing these fields, it may not work properly.

---

## 🎯 Feature Description

### Collection Types

| Type | Description | Input Example | Status |
|------|-------------|---------------|--------|
| **Single Work** | Get single work info | `https://www.douyin.com/video/7xxx` | ✅ Normal |
| **User Posts** | Get user published works | `https://www.douyin.com/user/MS4wLjABxxx` | ✅ Normal |
| **User Favorites** | Get user liked works | User homepage link | ✅ Normal |
| **User Collections** | Get user collected works | User homepage link | ✅ Normal |
| **Hashtag** | Get works under hashtag | `https://www.douyin.com/hashtag/xxx` | ✅ Normal |
| **Mix** | Get works in mix | Mix link | ✅ Normal |
| **Music** | Get works using this music | `https://www.douyin.com/music/7xxx` | ✅ Normal |
| **Keyword Search** | Search related works | `Scenery` | ✅ Normal |

### Collection Quantity Limit

- **All**: Collect all available data (may be slow)
- **20/50/100 items**: Quickly collect specified quantity
- **Custom**: Input any quantity

### Batch Download

Click the "One-click Download All" button, the system will automatically:
1. Read the Aria2 configuration of the collection result
2. Submit download tasks to Aria2 via JSON-RPC
3. Display download progress and status in real-time
4. Automatically handle failed tasks and errors

**Features**:
- ✅ Real-time progress display
- ✅ Supports breakpoint resume
- ✅ Automatically skip existing files
- ✅ Intelligent error handling and retry

### Settings Options

| Option | Description | Default Value |
|--------|-------------|---------------|
| **Cookie** | Douyin login credential | Empty |
| **Download Path** | File save location | `./download` |
| **Max Retries** | Download failure retry count | 3 |
| **Max Concurrency** | Simultaneous download task count | 5 |
| **Aria2 Host** | Aria2 service address | localhost |
| **Aria2 Port** | Aria2 service port | 6800 |
| **Aria2 Secret** | Aria2 RPC secret | douyin_crawler_default_secret |



## ❓ FAQ

### Q1: Prompt "Cookie invalid or expired"

**Reason:**
- Cookie has expired
- Cookie format is incorrect
- Not logged into Douyin account

**Solution:**
1. Re-acquire Cookie (refer to steps above)
2. Ensure Cookie is completely copied
3. Check if necessary fields are included

### Q2: Collection result is empty

**Solution:**
1. Check if the link is correct
2. Update Cookie
3. Check network connection

### Q3: Download failed

**Solution:**
1. Confirm Aria2 is installed: `aria2c --version`
2. View detailed error information in the log panel
3. Check if disk space is sufficient
4. Try reducing concurrency (adjust in settings)

### Q4: Application startup failed

**Possible Reasons:**
- Dependencies not installed
- Port occupied
- Frontend not built
- Configuration file corrupted

**Solution:**
```powershell
# Method 1: Use build script (Recommended)
.\scripts\dev.ps1 -Clean

# Method 2: Manual Reinstall
pip install -r requirements.txt
cd frontend
pnpm install  # or npm install
pnpm build    # or npm run build
```

### Q5: Frontend page blank

**Possible Reasons:**
- Firewall blocking access
- Frontend not built
- Build path error
- Missing files in dist directory

**Solution:**
1. Check firewall settings, ensure application is allowed to access network (usually private network configuration is sufficient)
2. Confirm frontend is built
3. Check if build path is correct

### Q6: Some features unavailable

**Known Issues:**
- Douyin ID parsing function not yet implemented
- Like/Favorite function requires target open permission, some targets cannot be obtained
- Auto get Cookie function has been removed

**Solution:**
1. Use recommended stable features
2. Manually configure Cookie
3. Use full links

### Q7: Configuration lost or reset

**Possible Reasons:**
- Configuration file deleted
- Configuration file format error
- Permission issues

**Solution:**
```powershell
# Check configuration file
cat config/settings.json

# If file is corrupted, delete and restart
Remove-Item config/settings.json
python main.py
```

#### Q8: Some tasks failed

**This is normal**, possible reasons:
- File already exists (automatically skipped)
- Download link expired
- Network temporary interruption
- Cookie expired


### Contact Support

If the problem is not solved:

1. View project Issues: https://github.com/erma0/douyin/issues
2. When submitting a new Issue, please include:
   - Target link
   - Error information
   - Software version
   - System and environment version

## 🎓 Advanced Usage

### Server Mode

In addition to the desktop application, it can also run as a standalone server:

```powershell
# Start server
python -m backend.server

# Specify port
python -m backend.server --port 9000

# Development mode (hot reload)
python -m backend.server --dev
```

Visit `http://localhost:8000` to use the Web interface.

### HTTP API

v2.0 provides complete RESTful API for automation scripts or third-party integration:

```powershell
# Start collection task
curl -X POST http://localhost:8000/api/task/start `
  -H "Content-Type: application/json" `
  -d '{"type": "favorite", "target": "user_link", "limit": 20}'

# Get task status
curl http://localhost:8000/api/task/status?task_id=task_xxx

# Get collection results
curl http://localhost:8000/api/task/results/task_xxx
```

Main API endpoints:
- `POST /api/task/start` - Start collection task
- `GET /api/task/status` - Query task status
- `GET /api/task/results/{task_id}` - Get collection results
- `GET /api/settings` - Get settings
- `POST /api/settings` - Save settings
- `GET /api/events` - SSE real-time event stream

### Command Line Mode

In addition to the GUI interface, command line operation is also supported:

```powershell
# View Help
python -m backend.cli --help

# Collect user homepage works
python -m backend.cli -u https://www.douyin.com/user/MS4wLjABxxx

# Limit quantity
python -m backend.cli -u https://www.douyin.com/user/MS4wLjABxxx -l 20

# Specify type
python -m backend.cli -u https://www.douyin.com/user/MS4wLjABxxx -t favorite
```

### Batch Collection

Create a text file, one link per line:

```text
https://www.douyin.com/user/MS4wLjABxxx
https://www.douyin.com/user/MS4wLjAByyy
https://www.douyin.com/user/MS4wLjABzzz
```

Then run:

```powershell
python -m backend.cli -u urls.txt -l 50
```

---

**Happy Using!** 🎉
