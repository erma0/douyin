# Aria2自动下载脚本
# 自动下载aria2c.exe到项目目录

Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         Aria2 自动下载工具          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Cyan

$aria2Dir = "aria2"
$aria2Exe = "$aria2Dir\aria2c.exe"

# 检查是否已存在
if (Test-Path $aria2Exe) {
    Write-Host "[提示] aria2c.exe 已存在" -ForegroundColor Yellow
    $overwrite = Read-Host "是否重新下载？(y/N)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "已取消下载" -ForegroundColor Gray
        exit 0
    }
}

# 确保目录存在
New-Item -ItemType Directory -Force -Path $aria2Dir | Out-Null

Write-Host "[1/4] 获取最新版本信息..." -ForegroundColor Yellow

try {
    # 获取最新release信息
    $releaseUrl = "https://api.github.com/repos/aria2/aria2/releases/latest"
    $release = Invoke-RestMethod -Uri $releaseUrl -Headers @{"User-Agent"="PowerShell"}
    $version = $release.tag_name
    
    Write-Host "[成功] 最新版本: $version" -ForegroundColor Green
    
    # 查找Windows 64位版本的下载链接
    $asset = $release.assets | Where-Object { $_.name -like "*win-64bit-build1.zip" } | Select-Object -First 1
    
    if (-not $asset) {
        Write-Host "[错误] 未找到Windows 64位版本" -ForegroundColor Red
        exit 1
    }
    
    $downloadUrl = $asset.browser_download_url
    $zipFile = "$aria2Dir\aria2.zip"
    
    Write-Host "[2/4] 下载 aria2 $version ..." -ForegroundColor Yellow
    Write-Host "      URL: $downloadUrl" -ForegroundColor Gray
    
    # 下载文件
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile -UseBasicParsing
    
    Write-Host "[成功] 下载完成" -ForegroundColor Green
    
    Write-Host "[3/4] 解压文件..." -ForegroundColor Yellow
    
    # 解压
    Expand-Archive -Path $zipFile -DestinationPath $aria2Dir -Force
    
    # 查找aria2c.exe
    $extractedExe = Get-ChildItem -Path $aria2Dir -Filter "aria2c.exe" -Recurse | Select-Object -First 1
    
    if ($extractedExe) {
        # 移动到目标位置
        Move-Item -Path $extractedExe.FullName -Destination $aria2Exe -Force
        Write-Host "[成功] 文件已解压" -ForegroundColor Green
    } else {
        Write-Host "[错误] 未找到 aria2c.exe" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "[4/4] 清理临时文件..." -ForegroundColor Yellow
    
    # 清理
    Remove-Item -Path $zipFile -Force
    Get-ChildItem -Path $aria2Dir -Directory | Remove-Item -Recurse -Force
    
    Write-Host "[成功] 清理完成" -ForegroundColor Green
    
    Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║              下载完成！              ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Green
    Write-Host "[成功] aria2c.exe 已安装到: $aria2Exe" -ForegroundColor Green
    Write-Host ""
    
    # 验证
    $versionOutput = & $aria2Exe --version 2>&1 | Select-Object -First 1
    Write-Host "版本信息: $versionOutput" -ForegroundColor Gray
    Write-Host ""
    Write-Host "现在可以运行程序了: python main.py" -ForegroundColor Yellow
    
} catch {
    Write-Host ""
    Write-Host "[错误] 下载失败: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "手动下载方法：" -ForegroundColor Cyan
    Write-Host "1. 访问: https://github.com/aria2/aria2/releases" -ForegroundColor Yellow
    Write-Host "2. 下载: aria2-*-win-64bit-build1.zip" -ForegroundColor Yellow
    Write-Host "3. 解压后将 aria2c.exe 复制到: $aria2Dir" -ForegroundColor Yellow
    exit 1
}
