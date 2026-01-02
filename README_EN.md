![douyin](https://socialify.git.ci/erma0/douyin/image?description=1&font=Source%20Code%20Pro&forks=1&issues=1&language=1&owner=1&pattern=Circuit%20Board&stargazers=1&theme=Auto)

# ✨DouyinCrawler

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
- ✅ Specified work data
- ✅ User homepage works
- ✅ User liked works (requires target open permission)
- ✅ User favorite works (requires target open permission)
- ✅ Challenge topic works
- ✅ Collection works
- ✅ Music original works
- ✅ Keyword search works

### 🎯 Application Features
- 🔄 **Incremental Collection**: Intelligent incremental collection of user homepage works
- ⬇️ **Batch Download**: Integrated Aria2, supports video/image batch download
- 🎨 **Visual Interface**: React desktop application, real-time log display
- 🎉 **First Run Wizard**: Friendly welcome interface, guiding configuration

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

- **Backend**: Python 3.12, PyWebView
- **Frontend**: React 18, TypeScript, Vite
- **Download**: Aria2
- **Packaging**: PyInstaller / Nuitka

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=erma0/douyin&type=Date)](https://star-history.com/#erma0/douyin&Date)
