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
    # Запущен как EXE - используем _MEIPASS для ресурсов
    base_dir = sys._MEIPASS
else:
    # Запущен как Python скрипт
    base_dir = os.path.dirname(os.path.abspath(__file__))

if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Импортируем и запускаем приложение
from app import run_server, find_free_port, save_temp_content
from pathlib import Path
from urllib.parse import quote
import threading
import time


def main():
    """Точка входа для EXE"""
    try:
        file_path = None
        open_url = None

        print(f"Args: {sys.argv}")
        print(f"Frozen: {getattr(sys, 'frozen', False)}")

        if len(sys.argv) > 1:
            # Получаем путь к файлу (может содержать кавычки)
            file_path = sys.argv[1].strip().strip('"').strip("'")
            print(f"File path from args: {file_path}")

            # Пробуем найти файл
            try:
                # Пробуем разные варианты пути
                path = Path(file_path)

                # Проверяем разные варианты
                if path.exists():
                    file_path = str(path.resolve())
                    print(f"File exists (absolute): {file_path}")
                else:
                    # Пробуем относительно текущей директории
                    path2 = Path.cwd() / file_path
                    if path2.exists():
                        file_path = str(path2.resolve())
                        print(f"File exists (relative): {file_path}")
                    else:
                        print(f"Файл не найден: {file_path}")
                        print(f"CWD: {Path.cwd()}")
                        input("Нажмите Enter...")
                        return
            except Exception as e:
                print(f"Ошибка при обработке пути: {e}")
                import traceback
                traceback.print_exc()
                input("Нажмите Enter...")
                return

        port = find_free_port()
        print(f"Port: {port}")

        if file_path:
            mode = sys.argv[2] if len(sys.argv) > 2 else 'view'
            print(f"Mode: {mode}")

            # Сохраняем контент в temp_cache для передачи между страницами
            try:
                content = Path(file_path).read_text(encoding='utf-8')
                print(f"Content length: {len(content)}")

                temp_id, temp_name = save_temp_content(content, Path(file_path).name)
                print(f"Temp ID: {temp_id}, Temp name: {temp_name}")

                # Кодируем параметры для URL
                if mode == 'edit':
                    open_url = f"http://127.0.0.1:{port}/edit?temp=1&temp_id={temp_id}&name={quote(temp_name, safe='')}"
                else:
                    open_url = f"http://127.0.0.1:{port}/view?temp=1&temp_id={temp_id}&name={quote(temp_name, safe='')}"

                print(f"Файл: {file_path}")
                print(f"Режим: {mode}")
            except Exception as e:
                print(f"Ошибка чтения файла: {e}")
                import traceback
                traceback.print_exc()
                input("Нажмите Enter...")
                return
        else:
            open_url = f"http://127.0.0.1:{port}"
            print("Перетащите .md файл или нажмите 'Новый файл'")

        print(f"URL: {open_url}")
        print("=" * 50)

        # Запускаем сервер и открываем браузер
        def open_browser():
            time.sleep(1)
            import webbrowser
            webbrowser.open(open_url)

        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()

        # Запускаем сервер (блокирует)
        run_server(port)

    except Exception as e:
        # Записываем ошибку в лог файл
        with open('md_reader_error.log', 'w', encoding='utf-8') as f:
            f.write(f"Error: {e}\n")
            import traceback
            traceback.print_exc(file=f)
        print(f"Critical error: {e}")
        import traceback
        traceback.print_exc()
        time.sleep(5)  # Даем время увидеть ошибку


if __name__ == '__main__':
    main()
