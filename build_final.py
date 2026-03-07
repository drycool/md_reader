#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script for MD Reader EXE
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import os
import subprocess
import shutil
from pathlib import Path


def get_project_root():
    return Path(__file__).parent.resolve()


def check_dependencies():
    deps = ['PyInstaller', 'flask', 'markdown']
    for dep in deps:
        try:
            __import__(dep)
            print(f"  + {dep}")
        except ImportError:
            print(f"  ! Installing {dep}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
    return True


def build_exe():
    print("\n--- Building EXE...")

    root = get_project_root()
    web_editor_dir = root / 'web_editor'
    icon_path = web_editor_dir / 'static' / 'favicon.ico'

    # Create spec with raw strings (r'')
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

a = Analysis(
    [r'{web_editor_dir}\\md_reader_exe.py'],
    pathex=[r'{web_editor_dir}'],
    binaries=[],
    datas=[
        (r'{web_editor_dir}\\templates', 'templates'),
        (r'{web_editor_dir}\\static', 'static'),
    ],
    hiddenimports=['flask', 'markdown', 'werkzeug', 'jinja2', 'click'],
    hookspath=[],
    hooksconfig={{}},
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
'''

    if icon_path.exists():
        spec_content += f'''    icon=r'{icon_path}',
'''

    spec_content += ''')

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
'''

    spec_file = web_editor_dir / 'build_spec.spec'
    spec_file.write_text(spec_content, encoding='utf-8')
    print(f"  + Created spec")

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--noconfirm',
        '--distpath', str(root / 'dist'),
        '--workpath', str(web_editor_dir / 'build'),
        str(spec_file)
    ]

    print(f"  + Running PyInstaller...")

    try:
        result = subprocess.run(
            cmd,
            cwd=str(web_editor_dir),
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            print("  + Build OK")
            return True
        else:
            print("  ! Error:")
            print(result.stdout[-1000:])
            print(result.stderr[-1000:])
            return False

    except Exception as e:
        print(f"  ! Error: {e}")
        return False


def test_exe():
    root = get_project_root()
    exe_path = root / 'dist' / 'MarkdownReader_v1.0.exe'

    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n+ EXE created: {exe_path.name} ({size_mb:.1f} MB)")
        return True

    # Search in subfolders
    for f in (root / 'dist').rglob('*.exe'):
        if 'MarkdownReader' in f.name:
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"\n+ Found: {f.name} ({size_mb:.1f} MB)")
            return True

    print("  ! EXE not found")
    return False


def create_readme():
    root = get_project_root()
    readme_path = root / 'dist' / 'README.txt'

    readme_content = """MD READER v1.0 - EXECUTABLE
=====================================

Standalone Markdown viewer and editor.

USAGE:
1. Run MarkdownReader_v1.0.exe
2. Wait for browser to open
3. Drag and drop .md files or create new

FEATURES:
- Works offline (no internet required)
- Local styles and scripts included
- Windows 7/8/10/11 compatible

(c) 2026 MD Reader Team
"""

    readme_path.write_text(readme_content, encoding='utf-8')
    print(f"  + Created README")


def main():
    print("============================================================")
    print("  BUILDING MD READER EXE v1.0")
    print("============================================================")

    root = get_project_root()
    print(f"Project root: {root}")

    required = [
        root / 'web_editor' / 'md_reader_exe.py',
        root / 'web_editor' / 'app.py',
        root / 'web_editor' / 'templates',
        root / 'web_editor' / 'static',
    ]

    for f in required:
        print(f"  {'+' if f.exists() else '-'} {f.name}")

    print("\n--- Checking dependencies...")
    if not check_dependencies():
        return False

    if not build_exe():
        return False

    if not test_exe():
        return False

    create_readme()

    print("\n============================================================")
    print("  BUILD COMPLETE!")
    print("  Result: dist/MarkdownReader_v1.0.exe")
    print("============================================================")

    return True


if __name__ == '__main__':
    try:
        success = main()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
