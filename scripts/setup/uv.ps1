# uv 环境快速配置脚本
$ErrorActionPreference = "Stop"

function Write-Step { Write-Host "`n--- $args ---`n" -ForegroundColor Cyan }
function Write-OK { Write-Host "[OK] $args" -ForegroundColor Green }
function Write-Info { Write-Host "[INFO] $args" -ForegroundColor Blue }
function Write-Err { Write-Host "[ERROR] $args" -ForegroundColor Red }

Write-Host "`n========================================" -ForegroundColor Magenta
Write-Host "         uv 环境配置工具" -ForegroundColor Magenta
Write-Host "========================================`n" -ForegroundColor Magenta

try {
    # 1. 检查 uv
    Write-Step "检查 uv"
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        Write-Err "未找到 uv，请先安装"
        Write-Host "安装方法: https://docs.astral.sh/uv/getting-started/installation/" -ForegroundColor Yellow
        exit 1
    }
    $uvVersion = uv --version
    Write-OK "uv 已安装: $uvVersion"
    
    # 2. 配置清华源
    Write-Step "配置清华镜像源"
    if (Test-Path "uv.toml") {
        Write-OK "uv.toml 配置文件已存在"
    } else {
        Write-Err "未找到 uv.toml 配置文件"
        exit 1
    }
    
    # 3. 虚拟环境
    Write-Step "配置虚拟环境"
    if (Test-Path ".venv") {
        Write-Info "虚拟环境已存在"
    } else {
        Write-Info "创建虚拟环境..."
        uv venv
        if ($LASTEXITCODE -ne 0) { throw "虚拟环境创建失败" }
    }
    Write-OK "虚拟环境: .venv"
    
    # 4. 安装依赖
    Write-Step "安装项目依赖"
    Write-Info "使用清华源安装依赖..."
    uv sync
    if ($LASTEXITCODE -ne 0) { throw "依赖安装失败" }
    Write-OK "项目依赖已安装"
    
    Write-Info "安装 PyInstaller..."
    
    # 尝试安装 PyInstaller，如果失败则提供解决方案
    $maxRetries = 3
    $retryCount = 0
    $installed = $false
    
    while (-not $installed -and $retryCount -lt $maxRetries) {
        try {
            if ($retryCount -gt 0) {
                Write-Info "重试安装 PyInstaller (第 $retryCount 次)..."
                Start-Sleep -Seconds 2
            }
            
            uv add --dev pyinstaller
            
            if ($LASTEXITCODE -eq 0) {
                $installed = $true
                Write-OK "PyInstaller 已安装"
            } else {
                $retryCount++
            }
        } catch {
            $retryCount++
            if ($retryCount -ge $maxRetries) {
                throw $_
            }
        }
    }
    
    if (-not $installed) {
        Write-Host "`n⚠️  PyInstaller 安装失败，可能的原因：" -ForegroundColor Yellow
        Write-Host "  1. 杀毒软件或 Windows Defender 阻止了文件操作" -ForegroundColor Yellow
        Write-Host "  2. 文件被占用或权限不足" -ForegroundColor Yellow
        Write-Host "`n解决方案：" -ForegroundColor Cyan
        Write-Host "  1. 临时关闭杀毒软件或将项目目录添加到白名单" -ForegroundColor White
        Write-Host "  2. 以管理员身份运行 PowerShell" -ForegroundColor White
        Write-Host "  3. 手动安装: uv add --dev pyinstaller" -ForegroundColor White
        Write-Host "`n项目依赖已安装，可以继续开发，打包时再安装 PyInstaller`n" -ForegroundColor Green
    }
    
    # 完成
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "            配置成功完成！" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Green
    
    Write-Host "后续使用:" -ForegroundColor Cyan
    Write-Host "  开发构建: .\scripts\dev.ps1" -ForegroundColor Yellow
    Write-Host "  完整打包: .\scripts\build\pyinstaller.ps1" -ForegroundColor Yellow
    Write-Host "  运行应用: python main.py" -ForegroundColor Yellow
    Write-Host ""
    
} catch {
    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host "              配置失败！" -ForegroundColor Red
    Write-Host "========================================`n" -ForegroundColor Red
    Write-Err "错误: $_"
    Write-Host "`n💡 提示：" -ForegroundColor Yellow
    Write-Host "  如果是 PyInstaller 安装失败，可以稍后手动安装：" -ForegroundColor White
    Write-Host "  .\.venv\Scripts\activate" -ForegroundColor Cyan
    Write-Host "  pip install pyinstaller" -ForegroundColor Cyan
    exit 1
}
