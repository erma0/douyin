# DouyinCrawler 快速启动菜单
# 使用方法: .\quick-start.ps1

$ErrorActionPreference = "Stop"

function Show-Menu {
    Clear-Host
    Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║      DouyinCrawler  快速启动菜单       ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Cyan
    
    Write-Host "【首次使用】" -ForegroundColor Yellow
    Write-Host "  1. 配置 uv 环境" -ForegroundColor White -NoNewline
    Write-Host " (首次必须)" -ForegroundColor Gray
    Write-Host "  2. 下载 aria2 工具" -ForegroundColor White -NoNewline
    Write-Host " (下载功能需要)" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "【开发调试】" -ForegroundColor Yellow
    Write-Host "  3. 构建开发环境" -ForegroundColor White -NoNewline
    Write-Host " (构建前端)" -ForegroundColor Gray
    Write-Host "  4. 运行应用" -ForegroundColor White -NoNewline
    Write-Host " (开发模式)" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "【打包发布】" -ForegroundColor Yellow
    Write-Host "  5. PyInstaller 打包" -ForegroundColor White -NoNewline
    Write-Host " (目录模式)" -ForegroundColor Gray
    Write-Host "  6. PyInstaller 打包" -ForegroundColor White -NoNewline
    Write-Host " (单文件模式)" -ForegroundColor Gray
    Write-Host "  7. Nuitka 打包" -ForegroundColor White -NoNewline
    Write-Host " (目录模式)" -ForegroundColor Gray
    Write-Host "  8. Nuitka 打包" -ForegroundColor White -NoNewline
    Write-Host " (单文件模式)" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "【工具】" -ForegroundColor Yellow
    Write-Host "  9. 清理打包缓存" -ForegroundColor White -NoNewline
    Write-Host ""
    
    Write-Host "  0. 退出" -ForegroundColor DarkGray
    Write-Host ""
}

while ($true) {
    Show-Menu
    $choice = Read-Host "请选择操作"
    
    try {
        switch ($choice) {
            "1" {
                Write-Host "`n━━━ 配置 uv 环境 ━━━`n" -ForegroundColor Cyan
                Write-Host "说明: 创建虚拟环境并安装项目依赖" -ForegroundColor Gray
                Write-Host "执行: .\scripts\setup\uv.ps1`n" -ForegroundColor Yellow
                & ".\scripts\setup\uv.ps1"
                Read-Host "`n按回车键继续"
            }
            "2" {
                Write-Host "`n━━━ 下载 aria2 工具 ━━━`n" -ForegroundColor Cyan
                Write-Host "说明: 从 GitHub 下载最新版 aria2c.exe" -ForegroundColor Gray
                Write-Host "执行: .\scripts\setup\aria2.ps1`n" -ForegroundColor Yellow
                & ".\scripts\setup\aria2.ps1"
                Read-Host "`n按回车键继续"
            }
            "3" {
                Write-Host "`n━━━ 构建开发环境 ━━━`n" -ForegroundColor Cyan
                Write-Host "说明: 安装依赖并构建前端资源" -ForegroundColor Gray
                Write-Host "执行: .\scripts\dev.ps1`n" -ForegroundColor Yellow
                & ".\scripts\dev.ps1"
                Read-Host "`n按回车键继续"
            }
            "4" {
                Write-Host "`n━━━ 运行应用 ━━━`n" -ForegroundColor Cyan
                Write-Host "说明: 以开发模式运行应用" -ForegroundColor Gray
                Write-Host "执行: python main.py`n" -ForegroundColor Yellow
                python main.py
                Read-Host "`n按回车键继续"
            }
            "5" {
                Write-Host "`n━━━ PyInstaller 打包（目录模式）━━━`n" -ForegroundColor Cyan
                Write-Host "说明: 打包为目录，启动快，文件多" -ForegroundColor Gray
                Write-Host "执行: .\scripts\build\pyinstaller.ps1 -Mode dir`n" -ForegroundColor Yellow
                & ".\scripts\build\pyinstaller.ps1" -Mode dir
                Read-Host "`n按回车键继续"
            }
            "6" {
                Write-Host "`n━━━ PyInstaller 打包（单文件模式）━━━`n" -ForegroundColor Cyan
                Write-Host "说明: 打包为单个 exe，便于分发" -ForegroundColor Gray
                Write-Host "执行: .\scripts\build\pyinstaller.ps1 -Mode onefile`n" -ForegroundColor Yellow
                & ".\scripts\build\pyinstaller.ps1" -Mode onefile
                Read-Host "`n按回车键继续"
            }
            "7" {
                Write-Host "`n━━━ Nuitka 打包（目录模式）━━━`n" -ForegroundColor Cyan
                Write-Host "说明: 编译为原生代码，性能好，启动快" -ForegroundColor Gray
                Write-Host "执行: .\scripts\build\nuitka.ps1 -Mode dir`n" -ForegroundColor Yellow
                & ".\scripts\build\nuitka.ps1" -Mode dir
                Read-Host "`n按回车键继续"
            }
            "8" {
                Write-Host "`n━━━ Nuitka 打包（单文件模式）━━━`n" -ForegroundColor Cyan
                Write-Host "说明: 编译为单个 exe，耗时较长（3-5分钟）" -ForegroundColor Gray
                Write-Host "执行: .\scripts\build\nuitka.ps1 -Mode onefile`n" -ForegroundColor Yellow
                & ".\scripts\build\nuitka.ps1" -Mode onefile
                Read-Host "`n按回车键继续"
            }
            "9" {
                Write-Host "`n━━━ 清理打包缓存 ━━━`n" -ForegroundColor Cyan
                Write-Host "说明: 清理所有打包相关的缓存和临时文件" -ForegroundColor Gray
                Write-Host "      适用于打包出错或需要完全重新打包时使用`n" -ForegroundColor Gray
                
                $cleanDirs = @("frontend/dist", "build", "dist", "release")
                $totalSize = 0
                
                Write-Host "将清理以下目录:" -ForegroundColor Yellow
                foreach ($dir in $cleanDirs) {
                    if (Test-Path $dir) {
                        $size = (Get-ChildItem $dir -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
                        if ($size) {
                            $sizeMB = [math]::Round($size / 1MB, 2)
                            $totalSize += $size
                            Write-Host "  - $dir ($sizeMB MB)" -ForegroundColor White
                        } else {
                            Write-Host "  - $dir (空)" -ForegroundColor DarkGray
                        }
                    } else {
                        Write-Host "  - $dir (不存在)" -ForegroundColor DarkGray
                    }
                }
                
                # 统计 __pycache__ 目录
                $pycacheDirs = Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue
                $pycacheSize = 0
                $pycacheCount = 0
                foreach ($dir in $pycacheDirs) {
                    $size = (Get-ChildItem $dir.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
                    if ($size) {
                        $pycacheSize += $size
                        $pycacheCount++
                    }
                }
                if ($pycacheCount -gt 0) {
                    $pycacheSizeMB = [math]::Round($pycacheSize / 1MB, 2)
                    Write-Host "  - __pycache__ ($pycacheCount 个目录, $pycacheSizeMB MB)" -ForegroundColor White
                    $totalSize += $pycacheSize
                }
                
                if ($totalSize -gt 0) {
                    $totalSizeMB = [math]::Round($totalSize / 1MB, 2)
                    Write-Host "`n总计: $totalSizeMB MB`n" -ForegroundColor Cyan
                    
                    $confirm = Read-Host "确认清理？(y/N)"
                    if ($confirm -eq "y" -or $confirm -eq "Y") {
                        Write-Host ""
                        foreach ($dir in $cleanDirs) {
                            if (Test-Path $dir) {
                                Remove-Item -Recurse -Force $dir -ErrorAction SilentlyContinue
                                Write-Host "✓ 已清理 $dir" -ForegroundColor Green
                            }
                        }
                        
                        # 清理 __pycache__
                        if ($pycacheCount -gt 0) {
                            $pycacheDirs = Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue
                            foreach ($dir in $pycacheDirs) {
                                Remove-Item -Recurse -Force $dir.FullName -ErrorAction SilentlyContinue
                            }
                            Write-Host "✓ 已清理 $pycacheCount 个 __pycache__ 目录" -ForegroundColor Green
                        }
                        
                        Write-Host "`n✓ 清理完成！" -ForegroundColor Green
                    } else {
                        Write-Host "`n已取消" -ForegroundColor Yellow
                    }
                } else {
                    Write-Host "`n没有需要清理的文件" -ForegroundColor Yellow
                }
                
                Read-Host "`n按回车键继续"
            }
            "0" {
                Write-Host "`n再见！`n" -ForegroundColor Green
                exit 0
            }
            default {
                Write-Host "`n无效选择，请重试`n" -ForegroundColor Red
                Start-Sleep -Seconds 1
            }
        }
    } catch {
        Write-Host "`n错误: $_`n" -ForegroundColor Red
        Read-Host "按回车键继续"
    }
}
