#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Главный входной файл для компиляции веб-редактора Markdown в EXE
Main entry point for compiling Markdown Web Editor to EXE
"""

import os
import sys
import subprocess
import webbrowser
import threading
import time
from pathlib import Path

# Добавляем пути для импорта
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(current_dir))

def check_dependencies():
    """Проверяем наличие необходимых зависимостей"""
    required_packages = {
        'flask': 'Flask',
        'rich': 'Rich',
        'markdown_it': 'markdown-it-py',
        'jinja2': 'Jinja2',
        'werkzeug': 'Werkzeug',
        'markupsafe': 'MarkupSafe'
    }
    
    missing = []
    available = []
    
    for package, display_name in required_packages.items():
        try:
            __import__(package.replace('-', '_'))
            available.append(display_name)
        except ImportError:
            missing.append(display_name)
    
    print(f"📦 Доступные пакеты: {', '.join(available) if available else 'нет'}")
    if missing:
        print(f"❌ Отсутствующие пакеты: {', '.join(missing)}")
    
    return missing

def setup_directories():
    """Создаём необходимые директории"""
    directories = ['uploads', 'logs', 'cache']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def create_sample_files():
    """Больше не создаём демо файлы - убрано"""
    pass

def open_browser(url, delay=2):
    """Открывает браузер с задержкой"""
    time.sleep(delay)
    webbrowser.open(url)

def run_demo_mode():
    """Запускаем демо-режим без Flask"""
    print("🎨 Запуск демо-режима...")
    
    # Проверяем наличие demo.html
    demo_file = Path('demo.html')
    if not demo_file.exists():
        print("❌ Файл demo.html не найден")
        input("Нажмите Enter для выхода...")
        return
    
    try:
        demo_url = "http://127.0.0.1:8080/demo.html"
        print(f"🌎 Демо-сервер: {demo_url}")
        print("🎉 Браузер откроется автоматически...")
        print("📌 Используйте Ctrl+C для остановки\n")
        
        browser_thread = threading.Thread(
            target=open_browser, 
            args=(demo_url,), 
            daemon=True
        )
        browser_thread.start()
        
        subprocess.run([
            sys.executable, '-m', 'http.server', '8080'
        ])
        
    except KeyboardInterrupt:
        print("\n\n👋 Приложение остановлено. До свидания!")
    except Exception as e:
        print(f"❌ Ошибка запуска демо: {e}")
        input("Нажмите Enter для выхода...")

def main():
    """Главная функция"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                   🚀 ВЕБ-РЕДАКТОР MARKDOWN 🚀                ║
║                                                              ║
║           Компилированная версия для Windows                 ║
║           Все интерфейсы на русском языке                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    print("🔧 Инициализация приложения...")
    
    # Проверяем зависимости
    missing = check_dependencies()
    if missing:
        print(f"⚠️ Некоторые зависимости отсутствуют, запускаем в режиме демо...")
        run_demo_mode()
        return
    else:
        print("✅ Все зависимости найдены!")
    
    # Настраиваем окружение
    setup_directories()

    print("✅ Инициализация завершена!")
    print("\n📡 Запуск веб-сервера...")
    
    try:
        # Импортируем Flask приложение
        from app import app
        
        # Настройки
        host = '127.0.0.1'
        port = 5000
        url = f"http://{host}:{port}"
        
        print(f"""
🌐 Сервер запущен: {url}
📁 Папка файлов: uploads/
💡 Используйте Ctrl+C для остановки

🎉 Браузер откроется автоматически через 2 секунды...
""")
        
        # Открываем браузер в отдельном потоке
        browser_thread = threading.Thread(
            target=open_browser, 
            args=(url,), 
            daemon=True
        )
        browser_thread.start()
        
        # Запускаем Flask
        app.run(
            host=host,
            port=port,
            debug=False,
            use_reloader=False
        )
        
    except ImportError as e:
        print(f"⚠️ Ошибка импорта Flask приложения: {e}")
        print("🎨 Запускаем демо-версию...")
        run_demo_mode()
            
    except KeyboardInterrupt:
        print("\n\n👋 Приложение остановлено. До свидания!")
        
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        print("🎨 Пробуем запустить демо-режим...")
        run_demo_mode()

if __name__ == '__main__':
    main()