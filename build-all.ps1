# 完整打包脚本（前端+后端）
# 使用: .\build-all.ps1 [-Mode dir|onefile] [-Clean]

param(
    [ValidateSet("dir", "onefile")]
    [string]$Mode = "dir",
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

function Write-Step { Write-Host "`n━━━ $args ━━━`n" -ForegroundColor Cyan }
function Write-OK { Write-Host "✓ $args" -ForegroundColor Green }
function Write-Err { Write-Host "✗ $args" -ForegroundColor Red }

try {
    Write-Host "`n╔═══════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║   抖音爬虫 - 完整打包工具   ║" -ForegroundColor Magenta
    Write-Host "╚═══════════════════════════════╝`n" -ForegroundColor Magenta
    
    # 1. 清理
    if ($Clean) {
        Write-Step "清理旧文件"
        @("frontend/dist", "build", "dist", "release") | ForEach-Object {
            if (Test-Path $_) {
                Remove-Item -Recurse -Force $_
                Write-OK "已清理 $_"
            }
        }
    }
    
    # 2. 安装Python依赖
    Write-Step "安装 Python 依赖"
    
    $hasPyInstaller = python -c "import PyInstaller" 2>$null
    if ($LASTEXITCODE -ne 0) {
        pip install pyinstaller -q
    }
    pip install -r requirements.txt -q
    Write-OK "Python 依赖已就绪"
    
    # 3. 构建前端
    Write-Step "构建前端"
    
    $buildFrontendArgs = @()
    if ($Clean) { $buildFrontendArgs += "-Clean" }
    
    & .\build-frontend.ps1 @buildFrontendArgs
    if ($LASTEXITCODE -ne 0) { throw "前端构建失败" }
    
    # 4. 打包后端
    Write-Step "打包后端 ($Mode 模式)"
    
    $specFile = if ($Mode -eq "onefile") { "build.spec" } else { "build-dir.spec" }
    Write-Host "ℹ 打包中（需要几分钟）..." -ForegroundColor Blue
    
    python -m PyInstaller $specFile --clean --noconfirm
    if ($LASTEXITCODE -ne 0) { throw "打包失败" }
    
    $exePath = if ($Mode -eq "onefile") { "dist/抖音爬虫.exe" } else { "dist/抖音爬虫/抖音爬虫.exe" }
    if (-not (Test-Path $exePath)) { throw "未找到可执行文件" }
    
    $exeSize = [math]::Round((Get-Item $exePath).Length / 1MB, 2)
    Write-OK "打包完成 ($exeSize MB)"
    
    # 5. 创建发布包
    Write-Step "创建发布包"
    
    $releaseDir = "release"
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $releaseName = "抖音爬虫_${Mode}_${timestamp}"
    $releaseTarget = Join-Path $releaseDir $releaseName
    
    New-Item -ItemType Directory -Path $releaseTarget -Force | Out-Null
    
    if ($Mode -eq "onefile") {
        Copy-Item "dist/抖音爬虫.exe" $releaseTarget
    } else {
        Copy-Item "dist/抖音爬虫/*" $releaseTarget -Recurse
    }
    
    # 复制文档
    @("README.md", "USAGE.md", "LICENSE") | ForEach-Object {
        if (Test-Path $_) { Copy-Item $_ $releaseTarget }
    }
    
    # 创建使用说明
    @"
# 抖音爬虫 - 使用说明

## 快速开始
1. 双击运行 抖音爬虫.exe
2. 在设置中配置抖音 Cookie
3. 开始使用

## 文件说明
- config/ - 配置文件（自动创建）
- download/ - 下载目录（自动创建）
- config/app.log - 日志文件

## 获取 Cookie
1. 浏览器登录抖音网页版
2. F12 打开开发者工具 → Network
3. 刷新页面，找到任意请求
4. 复制请求头中的 Cookie

打包时间: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@ | Out-File -FilePath (Join-Path $releaseTarget "使用说明.txt") -Encoding UTF8
    
    # 创建压缩包
    $zipPath = Join-Path $releaseDir "$releaseName.zip"
    Compress-Archive -Path $releaseTarget -DestinationPath $zipPath -Force
    $zipSize = [math]::Round((Get-Item $zipPath).Length / 1MB, 2)
    
    Write-OK "发布包已创建"
    
    # 完成
    Write-Host "`n╔═══════════════════════════════╗" -ForegroundColor Green
    Write-Host "║       打包成功完成！        ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════╝`n" -ForegroundColor Green
    
    Write-Host "📦 压缩包: " -NoNewline
    Write-Host $zipPath -ForegroundColor Yellow
    Write-Host "💾 大小: " -NoNewline
    Write-Host "$zipSize MB" -ForegroundColor Yellow
    Write-Host "`n测试运行: " -NoNewline
    Write-Host "$releaseTarget\抖音爬虫.exe`n" -ForegroundColor Cyan
    
} catch {
    Write-Host "`n╔═══════════════════════════════╗" -ForegroundColor Red
    Write-Host "║       打包失败！            ║" -ForegroundColor Red
    Write-Host "╚═══════════════════════════════╝`n" -ForegroundColor Red
    Write-Err "错误: $_"
    Write-Host "`n尝试: .\build-all.ps1 -Clean`n" -ForegroundColor Yellow
    exit 1
}
