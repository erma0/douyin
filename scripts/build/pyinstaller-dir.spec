# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 打包配置文件 - 目录模式（启动快）
# 使用方法: uv run python -m PyInstaller scripts/build/pyinstaller-dir.spec
# 注意：必须从项目根目录执行

import os

# 获取项目根目录
# spec 文件在 scripts/build/ 下，向上两级到达根目录
spec_root = os.path.abspath(os.path.join(os.path.dirname(SPEC), '..', '..'))

# 收集所有需要的数据文件
datas = [
    (os.path.join(spec_root, 'frontend/dist'), 'frontend/dist'),
    (os.path.join(spec_root, 'aria2'), 'aria2'),
    (os.path.join(spec_root, 'backend/lib/douyin/js'), 'backend/lib/douyin/js'),
]

# 隐藏导入（只保留必要的）
hiddenimports = [
    'backend',
]

a = Analysis(
    [os.path.join(spec_root, 'main.py')],
    pathex=[spec_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'backend.test',  # 排除测试文件
        'pytest',
        'unittest',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# 目录模式（启动快但文件多）
icon_path = os.path.join(spec_root, 'frontend/dist/favicon.ico')
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DouyinCrawler',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 生产环境禁用控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path if os.path.exists(icon_path) else None,
    runtime_tmpdir=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DouyinCrawler',
)
