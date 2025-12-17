# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 打包配置文件 - 优化版
# 使用方法: python -m PyInstaller build.spec

import os

# 收集所有需要的数据文件
datas = [
    ('frontend/dist', 'frontend/dist'),  # 前端构建产物
    ('aria2', 'aria2'),  # Aria2可执行文件
    ('backend/lib/js', 'backend/lib/js'),  # JavaScript文件
]

# 收集所有需要的隐藏导入
# 注意：PyInstaller的自动检测已经很强大，只添加确实需要的模块
hiddenimports = [
    # 项目模块（必须手动指定）
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
        # 排除大型不需要的库以减小体积
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

# 单文件模式（推荐用于分发）
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='抖音爬虫',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='frontend/dist/favicon.ico' if os.path.exists('frontend/dist/favicon.ico') else None
)
