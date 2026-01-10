# 开发环境构建脚本
# 使用: .\scripts\dev.ps1 [-Clean]

param([switch]$Clean)
$ErrorActionPreference = "Stop"

function Write-Step { Write-Host "`n━━━ $args ━━━`n" -ForegroundColor Cyan }
function Write-OK { Write-Host "✓ $args" -ForegroundColor Green }
function Write-Info { Write-Host "ℹ $args" -ForegroundColor Blue }
function Write-Warn { Write-Host "⚠ $args" -ForegroundColor Yellow }
function Write-Err { Write-Host "✗ $args" -ForegroundColor Red }

try {
    Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║      DouyinCrawler - 开发环境构建      ║" -ForegroundColor Magenta
    Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Magenta
    
    # 1. 检查依赖
    Write-Step "检查依赖"
    
    # 检查 Python
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Err "未找到 Python"
        exit 1
    }
    Write-OK "Python 已安装"
    
    # 检查包管理器（优先使用uv）
    $useUv = Get-Command uv -ErrorAction SilentlyContinue
    if ($useUv) {
        Write-OK "使用 uv 管理Python依赖（推荐）"
    } else {
        Write-OK "使用 pip 管理Python依赖"
    }
    
    $pm = if (Get-Command pnpm -ErrorAction SilentlyContinue) { "pnpm" } else { "npm" }
    if ($pm -eq "npm" -and -not (Get-Command npm -ErrorAction SilentlyContinue)) {
        Write-Err "未找到 npm 或 pnpm"
        exit 1
    }
    Write-OK "包管理器: $pm"
    
    # 2. 清理
    if ($Clean) {
        Write-Step "清理旧文件"
        @("frontend/dist", "frontend/node_modules") | ForEach-Object {
            if (Test-Path $_) {
                Remove-Item -Recurse -Force $_
                Write-OK "已清理 $_"
            }
        }
    }
    
    # 3. 安装Python依赖
    Write-Step "安装 Python 依赖"
    
    # 确保虚拟环境存在
    if (-not (Test-Path ".venv")) {
        Write-Info "创建虚拟环境..."
        if ($useUv) {
            uv venv
        } else {
            python -m venv .venv
        }
    }
    
    # 安装依赖
    if ($useUv) {
        uv sync
    } else {
        python -m pip install -r requirements.txt
    }
    Write-OK "Python 依赖已安装"
    
    # 4. 构建前端
    Write-Step "构建前端"
    
    Push-Location frontend
    try {
        if (-not (Test-Path "node_modules") -or $Clean) {
            Write-Info "安装前端依赖..."
            & $pm install
        }
        
        Write-Info "构建中..."
        & $pm run build
        
        if (-not (Test-Path "dist/index.html")) {
            throw "构建失败"
        }
    } finally {
        Pop-Location
    }
    Write-OK "前端构建完成"
    
    # 5. 创建目录
    Write-Step "创建必要目录"
    @("config", "download") | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -ItemType Directory -Path $_ -Force | Out-Null
            Write-OK "已创建 $_"
        }
    }
    
    # 完成
    Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║            构建成功完成！             ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Green
    
    Write-Host "运行应用: " -NoNewline
    Write-Host "python main.py" -ForegroundColor Yellow
    Write-Host "打包应用: " -NoNewline
    Write-Host ".\scripts\build\pyinstaller.ps1" -ForegroundColor Yellow
    Write-Host "`n⚠ 首次使用请在设置中配置 Cookie`n" -ForegroundColor Yellow
} catch {
    Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║              构建失败！              ║" -ForegroundColor Red
    Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Red
    Write-Err "错误: $_"
    Write-Host "`n尝试: .\scripts\dev.ps1 -Clean`n" -ForegroundColor Yellow
    exit 1
}