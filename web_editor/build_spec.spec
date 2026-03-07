# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

a = Analysis(
    [r'D:\md_reader\web_editor\md_reader_exe.py'],
    pathex=[r'D:\md_reader\web_editor'],
    binaries=[],
    datas=[
        (r'D:\md_reader\web_editor\templates', 'templates'),
        (r'D:\md_reader\web_editor\static', 'static'),
    ],
    hiddenimports=['flask', 'markdown', 'werkzeug', 'jinja2', 'click'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MarkdownReader_v1.1',
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
    icon=r'D:\md_reader\web_editor\static\favicon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MarkdownReader_v1.1',
)
