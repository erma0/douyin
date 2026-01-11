# User Guide

**English | [Tiếng Việt](./USAGE_VI.md) | [简体中文](./USAGE.md)**

## 📋 Table of Contents

- [Get Cookie](#get-cookie)
- [Features](#features)
- [FAQ](#faq)
- [Advanced Usage](#advanced-usage)

---

## 🍪 Get Cookie

Cookie is the necessary credential for obtaining data.

### Steps

1. Visit https://www.douyin.com and log in
2. Press `F12` to open developer tools
3. Switch to `Network` tab, refresh the page
4. Type `aweme` in filter, click any request
5. Find `Cookie:` field in `Request Headers`, copy the full content
6. Paste and save in application settings

![Schematic](./docs/images/image.png)

Valid Cookie should contain: `sessionid`, `ttwid`, `__ac_nonce`

---

## 🎯 Features

### Collection Types

| Type | Input Example |
|------|---------------|
| Single Work | `https://www.douyin.com/video/7xxx` |
| User Posts | `https://www.douyin.com/user/MS4wLjABxxx` |
| User Favorites/Collections | User homepage link |
| Hashtag | `https://www.douyin.com/hashtag/xxx` |
| Mix | Mix link |
| Music | `https://www.douyin.com/music/7xxx` |
| Keyword Search | `Scenery` |

### Batch Download

Requires Aria2 support:

```powershell
# Install Aria2
.\scripts\setup\aria2.ps1
```

Click "Download All" to automatically download collection results via Aria2.

### Settings

| Option | Default |
|--------|---------|
| Download Path | `./download` |
| Max Retries | 3 |
| Max Concurrency | 5 |
| Aria2 Port | 6800 |

---

## ❓ FAQ

### Cookie invalid or expired

Re-acquire Cookie, ensure it contains required fields like `sessionid`.

### Collection result is empty

1. Check if link format is correct
2. Update Cookie
3. Favorites/Collections require target user to have open permissions

### Download failed

1. Confirm Aria2 is installed: `aria2c --version`
2. Check disk space
3. Try reducing concurrency

### Application startup failed

```powershell
.\scripts\dev.ps1 -Clean
```

### Contact Support

When submitting an [Issue](https://github.com/erma0/douyin/issues), please include: target link, error message, software version

---

## 🎓 Advanced Usage

### Server Mode

```bash
python -m backend.server              # Default port 8000
python -m backend.server --port 9000  # Specify port
python -m backend.server --dev        # Development mode
```

Environment variables: `DOUYIN_HOST`, `DOUYIN_PORT`, `DOUYIN_DEV`, `DOUYIN_LOG_LEVEL`

### HTTP API

```bash
# Start collection task
curl -X POST http://localhost:8000/api/task/start \
  -H "Content-Type: application/json" \
  -d '{"type": "favorite", "target": "user_link", "limit": 20}'

# Get results
curl http://localhost:8000/api/task/results/task_xxx
```

Main endpoints:
- `POST /api/task/start` - Start task
- `GET /api/task/status` - Task status
- `GET /api/task/results/{task_id}` - Collection results
- `GET /api/settings` - Get settings
- `POST /api/settings` - Save settings
- `GET /api/events` - SSE event stream

### Command Line Mode

```bash
# Basic usage
python -m backend.cli -u https://www.douyin.com/user/xxx -l 20

# Specify type
python -m backend.cli -u link -t favorite  # post/favorite/collection/hashtag/music/mix/aweme/search

# Search filters
python -m backend.cli -u "food" -t search --sort-type 2 --publish-time 7

# Batch collection (urls.txt with one link per line)
python -m backend.cli -u urls.txt -l 50

# Collection only, no download
python -m backend.cli -u link --no-download
```

Filter parameters:
- `--sort-type`: 0=comprehensive, 1=most likes, 2=newest
- `--publish-time`: 0=unlimited, 1=within a day, 7=within a week, 180=within half a year
- `--filter-duration`: 0-1=under 1 min, 1-5=1-5 min, 5-10000=over 5 min

---

**Happy Using!** 🎉
