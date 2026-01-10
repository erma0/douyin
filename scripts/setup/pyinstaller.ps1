# PyInstaller 单独安装脚本
# 使用方法: .\scripts\setup\pyinstaller.ps1

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "      PyInstaller 安装工具" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "💡 提示：如果安装失败，请尝试以下方法：" -ForegroundColor Yellow
Write-Host "  1. 临时关闭杀毒软件或 Windows Defender" -ForegroundColor White
Write-Host "  2. 将项目目录添加到杀毒软件白名单" -ForegroundColor White
Write-Host "  3. 以管理员身份运行此脚本`n" -ForegroundColor White

try {
    # 检查环境
    $useUv = Get-Command uv -ErrorAction SilentlyContinue
    
    if ($useUv) {
        Write-Host "✓ 使用 uv 安装" -ForegroundColor Green
    } else {
        Write-Host "✓ 使用 pip 安装" -ForegroundColor Green
    }
    
    # 检查虚拟环境
    if (-not (Test-Path ".venv")) {
        Write-Host "❌ 虚拟环境不存在，请先运行: .\scripts\setup\uv.ps1" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "开始安装 PyInstaller..." -ForegroundColor Cyan
    Write-Host ""
    
    # 尝试安装
    $maxRetries = 3
    $retryCount = 0
    $installed = $false
    
    while (-not $installed -and $retryCount -lt $maxRetries) {
        if ($retryCount -gt 0) {
            Write-Host "`n⏳ 等待 2 秒后重试..." -ForegroundColor Yellow
            Start-Sleep -Seconds 2
            Write-Host "🔄 第 $retryCount 次重试..." -ForegroundColor Yellow
        }
        
        if ($useUv) {
            uv add --dev pyinstaller
        } else {
            python -m pip install pyinstaller
        }
        
        if ($LASTEXITCODE -eq 0) {
            $installed = $true
        } else {
            $retryCount++
        }
    }
    
    if ($installed) {
        Write-Host "`n========================================" -ForegroundColor Green
        Write-Host "          安装成功！" -ForegroundColor Green
        Write-Host "========================================`n" -ForegroundColor Green
        
        # 验证安装
        $version = python -c "import PyInstaller; print(PyInstaller.__version__)" 2>&1
        Write-Host "PyInstaller 版本: $version" -ForegroundColor Cyan
        Write-Host "`n现在可以使用打包功能了：" -ForegroundColor Yellow
        Write-Host "  .\scripts\build\pyinstaller.ps1" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "`n========================================" -ForegroundColor Red
        Write-Host "          安装失败！" -ForegroundColor Red
        Write-Host "========================================`n" -ForegroundColor Red
        
        Write-Host "❌ PyInstaller 安装失败" -ForegroundColor Red
        Write-Host "`n可能的原因：" -ForegroundColor Yellow
        Write-Host "  1. 杀毒软件阻止了文件操作" -ForegroundColor White
        Write-Host "  2. Windows Defender 实时保护阻止" -ForegroundColor White
        Write-Host "  3. 文件被占用或权限不足" -ForegroundColor White
        
        Write-Host "`n解决方案：" -ForegroundColor Cyan
        Write-Host "  1. 临时关闭杀毒软件" -ForegroundColor White
        Write-Host "  2. 将项目目录添加到 Windows Defender 排除列表：" -ForegroundColor White
        Write-Host "     设置 → 更新和安全 → Windows 安全中心 → 病毒和威胁防护 → 排除项" -ForegroundColor Gray
        Write-Host "  3. 以管理员身份运行 PowerShell 后重试" -ForegroundColor White
        Write-Host "  4. 使用 pip 直接安装：" -ForegroundColor White
        Write-Host "     .\.venv\Scripts\activate" -ForegroundColor Gray
        Write-Host "     pip install pyinstaller" -ForegroundColor Gray
        Write-Host ""
        
        exit 1
    }
    
} catch {
    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host "          安装失败！" -ForegroundColor Red
    Write-Host "========================================`n" -ForegroundColor Red
    Write-Host "错误: $_" -ForegroundColor Red
    Write-Host ""
    exit 1
}
