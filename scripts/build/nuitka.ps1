# DouyinCrawler Nuitka 打包脚本
# 使用方法: .\scripts\build\nuitka.ps1 [-Mode dir|onefile] [-Clean]

param(
    [ValidateSet("dir", "onefile")]
    [string]$Mode = "dir",
    [switch]$Clean,
    [switch]$Debug
)

$ErrorActionPreference = "Stop"

function Write-Step { Write-Host "`n━━━ $args ━━━`n" -ForegroundColor Cyan }
function Write-OK { Write-Host "✓ $args" -ForegroundColor Green }
function Write-Info { Write-Host "ℹ $args" -ForegroundColor Blue }
function Write-Err { Write-Host "✗ $args" -ForegroundColor Red }

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "DouyinCrawler Nuitka 打包工具 ($Mode 模式)" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

try {
    # 0. 检查环境
    Write-Step "检查环境"
    
    # 检查是否有 uv
    $useUv = Get-Command uv -ErrorAction SilentlyContinue
    
    if ($useUv) {
        Write-OK "使用 uv 环境"
    } else {
        Write-Info "使用传统 Python 环境"
    }
    
    # 检查虚拟环境
    if (-not (Test-Path ".venv")) {
        Write-Err "虚拟环境不存在，请先运行: .\scripts\setup\uv.ps1"
        exit 1
    }
    Write-OK "虚拟环境: .venv"
    
    # 检查 Nuitka 是否安装
    Write-Info "检查 Nuitka..."
    $nuitkaInstalled = $false
    
    try {
        $null = & python -c "import nuitka" 2>&1
        if ($LASTEXITCODE -eq 0) {
            $nuitkaInstalled = $true
            Write-OK "Nuitka 已安装"
        }
    } catch {
        # 忽略错误，继续安装
    }
    
    if (-not $nuitkaInstalled) {
        Write-Info "Nuitka 未安装，正在安装..."
        if ($useUv) {
            uv add --dev nuitka ordered-set
        } else {
            python -m pip install nuitka ordered-set
        }
        if ($LASTEXITCODE -ne 0) {
            Write-Err "Nuitka 安装失败"
            Write-Host "提示: 可能需要安装 C 编译器 (MinGW64)" -ForegroundColor Yellow
            exit 1
        }
        Write-OK "Nuitka 安装完成"
    }

    # 1. 检查前端是否已构建
    Write-Step "检查前置条件"
    
    if (-not (Test-Path "frontend/dist/index.html")) {
        Write-Info "前端未构建，正在构建..."
        Push-Location frontend
        try {
            if (-not (Test-Path "node_modules")) {
                pnpm install
            }
            pnpm build
            if ($LASTEXITCODE -ne 0) { throw "前端构建失败" }
        } finally {
            Pop-Location
        }
    }
    Write-OK "前端已构建"

    # 检查 aria2 是否存在
    if (-not (Test-Path "aria2/aria2c.exe")) {
        Write-Err "aria2c.exe 不存在，请先运行: .\scripts\setup\aria2.ps1"
        exit 1
    }
    Write-OK "aria2 已就绪"

    # 2. 清理旧的构建产物
    Write-Step "清理旧的构建产物"
    
    $cleanPaths = @("build/nuitka", "nuitka-crash-report.xml")
    
    # 根据模式添加清理路径
    if ($Mode -eq "onefile") {
        $cleanPaths += "dist/DouyinCrawler.exe"
    } else {
        $cleanPaths += "dist/main.dist"
    }
    
    if ($Clean) {
        $cleanPaths += "frontend/dist"
    }
    
    foreach ($path in $cleanPaths) {
        if (Test-Path $path) {
            Remove-Item -Recurse -Force $path
            Write-Info "删除: $path"
        }
    }
    Write-OK "清理完成"

    # 3. 开始打包
    Write-Step "开始打包 ($Mode 模式)"
    Write-Host "⚠️  Nuitka 编译需要 3-5 分钟，请耐心等待..." -ForegroundColor Yellow
    Write-Host ""

    # 确保输出目录存在
    if (-not (Test-Path "dist")) {
        New-Item -ItemType Directory -Path "dist" | Out-Null
    }

    # 构建 nuitka 命令参数
    $nuitkaArgs = @(
        "-m", "nuitka",
        
        # 基本模式
        "--standalone",
        "--mingw64",
        
        # 输出配置
        "--output-dir=dist"
    )
    
    # 单文件模式
    if ($Mode -eq "onefile") {
        $nuitkaArgs += "--onefile"
        $nuitkaArgs += "--output-filename=DouyinCrawler.exe"
        
        # 单文件模式确保临时目录可写
        $nuitkaArgs += "--onefile-tempdir-spec={TEMP}/DouyinCrawler"
    }
    
    # 通用配置
    $nuitkaArgs += @(
        # 包含数据目录
        "--include-data-dir=frontend/dist=frontend/dist",
        "--include-data-dir=backend/lib/douyin/js=backend/lib/douyin/js",
        
        # 明确包含 aria2 可执行文件和配置
        "--include-data-files=aria2/aria2c.exe=aria2/aria2c.exe",
        
        # 排除配置文件和下载目录（用户数据不应打包）
        "--nofollow-import-to=backend.test",
        "--nofollow-import-to=pytest",
        "--nofollow-import-to=unittest",
        "--nofollow-import-to=test",
        
        # Windows 配置
        "--windows-icon-from-ico=frontend/dist/favicon.ico",
        
        # 稳定性配置
        "--disable-ccache",
        "--lto=no",
        
        "--assume-yes-for-downloads",
        
        # 入口文件
        "main.py"
    )
    
    # 调试模式：启用控制台
    if (-not $Debug) {
        $nuitkaArgs += "--windows-console-mode=disable"
    }

    # 执行打包
    Write-Info "执行打包..."
    python $nuitkaArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "=" -NoNewline -ForegroundColor Green
        Write-Host ("=" * 59) -ForegroundColor Green
        Write-Host "✓ 打包成功！" -ForegroundColor Green
        
        $exePath = if ($Mode -eq "onefile") { "dist/DouyinCrawler.exe" } else { "dist/main.dist/main.exe" }
        
        if (Test-Path $exePath) {
            $exeSize = [math]::Round((Get-Item $exePath).Length / 1MB, 2)
            Write-Host "✓ 可执行文件: $exePath ($exeSize MB)" -ForegroundColor Green
        }
        
        Write-Host "=" -NoNewline -ForegroundColor Green
        Write-Host ("=" * 59) -ForegroundColor Green
        
        # 4. 创建发布包
        Write-Step "创建发布包"
        
        $releaseDir = "release"
        if (-not (Test-Path $releaseDir)) {
            New-Item -ItemType Directory -Path $releaseDir | Out-Null
        }
        
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $releaseName = "DouyinCrawler_nuitka_${Mode}_${timestamp}"
        $releaseTarget = Join-Path $releaseDir $releaseName
        
        New-Item -ItemType Directory -Path $releaseTarget -Force | Out-Null
        
        if ($Mode -eq "onefile") {
            Copy-Item "dist/DouyinCrawler.exe" $releaseTarget
        } else {
            Copy-Item "dist/main.dist" $releaseTarget -Recurse
            Rename-Item (Join-Path $releaseTarget "main.dist") "DouyinCrawler"
        }
        
        # 复制文档
        @("README.md", "USAGE.md", "LICENSE") | ForEach-Object {
            if (Test-Path $_) { Copy-Item $_ $releaseTarget }
        }
        
        # 创建使用说明
        $exePathInRelease = if ($Mode -eq "onefile") { "DouyinCrawler.exe" } else { "DouyinCrawler\main.exe" }
        @"
# DouyinCrawler - 使用说明

## 快速开始
1. 双击运行 $exePathInRelease
2. 在设置中配置抖音 Cookie
3. 开始使用

## 文件说明
程序运行后会在 exe 所在目录自动创建以下文件夹：
- config/ - 配置文件目录
  - settings.json - 应用配置（包含 Cookie、下载路径等）
  - aria2.conf - Aria2 下载器配置
  - app.log - 应用日志
- download/ - 默认下载目录（可在设置中修改）

注意：
- 首次运行会自动创建默认配置
- 配置文件不会被打包，每次运行都使用 exe 所在目录的配置
- 可以安全删除 config 目录来重置所有设置

## 获取 Cookie
1. 浏览器登录抖音网页版 (https://www.douyin.com)
2. F12 打开开发者工具 → Network
3. 刷新页面，找到任意请求
4. 复制请求头中的 Cookie

打包方式: Nuitka ($Mode 模式)
打包时间: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@ | Out-File -FilePath (Join-Path $releaseTarget "使用说明.txt") -Encoding UTF8
        
        # 创建压缩包
        $zipPath = Join-Path $releaseDir "$releaseName.zip"
        Compress-Archive -Path $releaseTarget -DestinationPath $zipPath -Force
        $zipSize = [math]::Round((Get-Item $zipPath).Length / 1MB, 2)
        
        Write-OK "发布包已创建"
        Write-Host ""
        Write-Host "📦 压缩包: " -NoNewline
        Write-Host $zipPath -ForegroundColor Yellow
        Write-Host "💾 大小: " -NoNewline
        Write-Host "$zipSize MB" -ForegroundColor Yellow
        Write-Host "`n测试运行: " -NoNewline
        Write-Host "$releaseTarget\$exePathInRelease`n" -ForegroundColor Cyan
        
    } else {
        Write-Host ""
        Write-Host "=" -NoNewline -ForegroundColor Red
        Write-Host ("=" * 59) -ForegroundColor Red
        Write-Err "打包失败"
        Write-Host "=" -NoNewline -ForegroundColor Red
        Write-Host ("=" * 59) -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host ""
    Write-Host "=" -NoNewline -ForegroundColor Red
    Write-Host ("=" * 59) -ForegroundColor Red
    Write-Err "打包失败: $_"
    Write-Host "=" -NoNewline -ForegroundColor Red
    Write-Host ("=" * 59) -ForegroundColor Red
    exit 1
}
