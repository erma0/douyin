![douyin](https://socialify.git.ci/erma0/douyin/image?description=1&font=Source%20Code%20Pro&forks=1&issues=1&language=1&owner=1&pattern=Circuit%20Board&stargazers=1&theme=Auto)

# ✨DouyinCrawler

**English | [Tiếng Việt](./README_VI.md) | [简体中文](./README.md)**

> ❤️ [Open source is hard, welcome to star ⭐](#star-history)

## 📢 Disclaimer

> The original intention of this project is to learn `python` crawlers, command-line calls to `Aria2`, and `python` implementation of `WebUI` cases. It was later used to try AI programming (frontend and backend interaction parts are purely AI-generated). The application function is to obtain public information on the Douyin platform, only for testing and learning research, and is prohibited for commercial use or any illegal purposes.
>
> Any user who directly or indirectly uses or disseminates the content of this repository is solely responsible for their actions, and the contributors of this repository are not responsible for any consequences arising from such actions.
>
> **If relevant parties believe that the code of this project may infringe upon their rights, please contact me immediately to delete the relevant code**.
>
> Using the content of this repository means that you agree to all the terms and conditions of this disclaimer. If you do not accept the above disclaimer, please stop using this project immediately.

---

## 🏠 Project Address

> [https://github.com/erma0/douyin](https://github.com/erma0/douyin)

## 🍬 Features

### 📊 Data Collection
- ✅ Single work data
- ✅ User posts works
- ✅ User favorites works (requires target open permission)
- ✅ User collections works (requires target open permission)
- ✅ Hashtag works
- ✅ Mix works
- ✅ Music works
- ✅ Keyword search works

### 🎯 Application Features
- 🔄 **Incremental Collection**: Intelligent incremental collection of user homepage works
- ⬇️ **Batch Download**: Integrated Aria2, supports video/image batch download
- 🎨 **Visual Interface**: React desktop application, real-time log display
- 🎉 **First Run Wizard**: Friendly welcome interface, guiding configuration

## 📸 Interface Preview

![Software Interface](./docs/images/main.png)

## 🚀 Quick Start

### Environment Requirements

> 📍 Test Environment: `Win10 x64` + `Python 3.12` + `Node.js 22.13.0` + `uv 0.9+`


### Quick Start

- Download the latest version from [Releases](https://github.com/erma0/douyin/releases)
- Unzip and double-click to run `DouyinCrawler.exe`


Detailed usage instructions please view [USAGE_EN.md](USAGE_EN.md)

## 🔨 Build and Package

### 📁 Script Directory

All build scripts have been organized into the `scripts/` directory:

```
scripts/
├── build/              # Packaging scripts
│   ├── pyinstaller.ps1      # PyInstaller packaging
│   ├── pyinstaller-dir.spec # Directory mode configuration
│   ├── pyinstaller-onefile.spec # Single file configuration
│   └── nuitka.ps1           # Nuitka packaging
├── setup/              # Environment configuration
│   ├── uv.ps1               # Configure uv environment
│   ├── aria2.ps1            # Download aria2
│   └── pyinstaller.ps1      # Install PyInstaller separately
└── dev.ps1             # Development environment build
```

### 🚀 Quick Start

#### Method 1: Use Quick Start Menu (Recommended)

```powershell
.\quick-start.ps1
```

Provides an interactive menu, select operations by number.

#### Method 2: Manually Execute Scripts

See script directory for details.

### 📦 Packaging Instructions

#### PyInstaller (Recommended)
- ✅ Fast packaging speed (5-10 minutes)
- ✅ Supports directory mode and single file mode
- ✅ Good compatibility
- 📦 Size: Directory mode ~30MB, Single file ~21MB

#### Nuitka (High Performance)
- ✅ Compile to native code, better performance
- ✅ Fast startup speed
- ⚠️ Long compilation time (10-20 minutes)
- ⚠️ Requires MinGW64 compiler (automatically downloaded)
- 📦 Size: Directory mode ~45MB, Single file ~35MB

#### Packaging Artifacts
- **Directory Mode**: `dist/DouyinCrawler/DouyinCrawler.exe` (Fast startup)
- **Single File Mode**: `dist/DouyinCrawler.exe` (Easy to distribute)
- **Release Package**: `release/DouyinCrawler_*.zip` (Automatically generated)


## 📊 Tech Stack

- **Backend**: Python 3.12, FastAPI, PyWebView
- **Frontend**: React 18, TypeScript, Vite
- **Download**: Aria2
- **Packaging**: PyInstaller / Nuitka

## Server Mode

Backend is built with FastAPI, providing complete RESTful API.

```bash
# Start server
python -m backend.server

# Or use Docker
docker compose up -d
```

Visit `http://localhost:8000` (Docker: `http://localhost`)

```text
Command line arguments:
    python -m backend.server              # Default config
    python -m backend.server --port 9000  # Specify port
    python -m backend.server --dev        # Development mode

Environment variables (prefix DOUYIN_):
    DOUYIN_HOST          Listen address (default: 127.0.0.1)
    DOUYIN_PORT          Listen port (default: 8000)
    DOUYIN_DEV           Development mode (default: false)
    DOUYIN_LOG_LEVEL     Log level (default: info)
```

### API Architecture

v2.0 refactored to standard frontend-backend separation architecture:

- **Backend**: FastAPI provides RESTful API + SSE real-time push
- **Frontend**: React communicates with backend via HTTP API
- **Real-time**: SSE (Server-Sent Events) pushes collection progress and results

API modules:
- `/api/task/*` - Collection task management
- `/api/settings/*` - Application settings
- `/api/aria2/*` - Aria2 download service
- `/api/file/*` - File operations
- `/api/system/*` - System tools
- `/api/events` - SSE real-time event stream

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=erma0/douyin&type=Date)](https://star-history.com/#erma0/douyin&Date)
