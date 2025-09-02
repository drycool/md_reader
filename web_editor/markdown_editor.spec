# -*- mode: python ; coding: utf-8 -*-
"""
Спецификация PyInstaller для компиляции веб-редактора Markdown
PyInstaller spec file for Markdown Web Editor compilation
"""

import os
from pathlib import Path

# Пути к файлам
current_dir = Path(__file__).parent
app_dir = current_dir
templates_dir = app_dir / 'templates'
static_dir = app_dir / 'static'

block_cipher = None

# Данные для включения в EXE
added_files = [
    # HTML шаблоны
    (str(templates_dir), 'templates'),
    # Статические файлы (CSS, JS)
    (str(static_dir), 'static'),
    # Демо файл
    (str(app_dir / 'demo.html'), '.'),
    # Локализация
    (str(app_dir / 'localization.py'), '.'),
]

# Скрытые импорты (модули, которые могут не определяться автоматически)
hidden_imports = [
    'flask',
    'jinja2',
    'werkzeug',
    'markupsafe',
    'markdown_it',
    'markdown_it.parser_core',
    'markdown_it.parser_block',
    'markdown_it.parser_inline',
    'markdown_it.renderer',
    'markdown_it.ruler',
    'markdown_it.rules_core',
    'markdown_it.rules_block',
    'markdown_it.rules_inline',
    'rich',
    'rich.console',
    'rich.syntax',
    'rich.panel',
    'typer',
    'textual',
    'rapidfuzz',
    'levenshtein',
    'pathlib',
    'threading',
    'webbrowser',
    'http.server',
    'socketserver'
]

a = Analysis(
    ['main.py'],
    pathex=[str(current_dir)],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MarkdownEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
    version_file='version_info.txt' if os.path.exists('version_info.txt') else None
)