# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 打包配置文件 - 目录模式（启动快）
# 使用方法: python -m PyInstaller build-dir.spec

import os
from PyInstaller.utils.hooks import collect_data_files

# 收集所有需要的数据文件
datas = [
    ('frontend/dist', 'frontend/dist'),
    ('aria2', 'aria2'),
    ('backend/lib/js', 'backend/lib/js'),
]

# 动态收集webview相关数据文件
try:
    webview_datas = collect_data_files('webview')
    if webview_datas:
        datas.extend(webview_datas)
except Exception:
    pass

# 隐藏导入
hiddenimports = [
    'backend.api',
    'backend.aria2_manager',
    'backend.constants',
    'backend.lib.douyin',
    'backend.lib.request',
    'backend.lib.util',
    'backend.lib.cookies',
    'backend.lib.download',
    'backend.lib.execjs_fix',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'PIL',
        'pygments',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# 目录模式（启动快但文件多）
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='抖音爬虫',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='frontend/dist/favicon.ico' if os.path.exists('frontend/dist/favicon.ico') else None,
    # 添加运行时选项，禁用临时目录清理警告
    runtime_tmpdir=None,  # 使用系统临时目录
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='抖音爬虫',
)
