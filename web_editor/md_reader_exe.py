#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown Reader - EXE Launcher
Запускает Flask-приложение из web_editor/app.py
"""

import sys
import os

# Определяем базовый путь (для EXE и для разработки)
if getattr(sys, 'frozen', False):
    # Запущен как EXE
    base_dir = os.path.dirname(sys.executable)
else:
    # Запущен как Python скрипт
    base_dir = os.path.dirname(os.path.abspath(__file__))

if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Импортируем и запускаем приложение
from app import run_server, find_free_port
from pathlib import Path
from urllib.parse import quote


def main():
    """Точка входа для EXE"""
    file_path = None

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        file_path = str(Path(file_path).resolve())

        if not Path(file_path).exists():
            print(f"Файл не найден: {file_path}")
            input("Нажмите Enter...")
            return

    port = find_free_port()

    if file_path:
        mode = sys.argv[2] if len(sys.argv) > 2 else 'view'

        if mode == 'edit':
            url = f"http://127.0.0.1:{port}/edit?file={quote(file_path, safe='')}"
        else:
            url = f"http://127.0.0.1:{port}/view?file={quote(file_path, safe='')}"

        print(f"Файл: {file_path}")
        print(f"Режим: {mode}")
    else:
        url = f"http://127.0.0.1:{port}"
        print("Перетащите .md файл или нажмите 'Новый файл'")

    print(f"URL: {url}")
    print("=" * 50)

    run_server(port)


if __name__ == '__main__':
    main()
