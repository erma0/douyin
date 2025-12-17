# Aria2 可执行文件目录

## 📦 说明

此目录用于存放aria2c可执行文件，实现开箱即用的下载功能。

## 📥 下载Aria2

### Windows用户

1. 访问 [Aria2 Releases](https://github.com/aria2/aria2/releases)
2. 下载最新版本的 `aria2-*-win-64bit-build1.zip`
3. 解压后将 `aria2c.exe` 复制到此目录

## 🔧 自动下载脚本

运行以下命令自动下载aria2c.exe：

```powershell
# Windows PowerShell
.\download_aria2.ps1
```

## ⚠️ 注意事项

1. **版权说明**
   - Aria2是开源软件，遵循GPL-2.0许可证
   - 项目地址：https://github.com/aria2/aria2

2. **跨平台支持**
   - Windows: aria2c.exe
   - Linux: aria2c
   - Mac: aria2c

## 🚀 使用方式

程序会自动检测并使用此目录下的aria2c：

1. 优先使用 `aria2/aria2c.exe`（内置）
2. 其次使用系统PATH中的 `aria2c`（已安装）
3. 如果都没有，提示用户下载
