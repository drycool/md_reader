#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт сборки EXE файла для веб-редактора Markdown
Build script for Markdown Web Editor executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Печатаем баннер сборки"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    📦 СБОРКА EXE ФАЙЛА                       ║
║                                                              ║
║            Компиляция веб-редактора Markdown                 ║
║            в автономный исполняемый файл                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

def check_pyinstaller():
    """Проверяем наличие PyInstaller"""
    try:
        import PyInstaller
        print("✅ PyInstaller найден")
        return True
    except ImportError:
        print("❌ PyInstaller не найден")
        print("Устанавливаю PyInstaller...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
            print("✅ PyInstaller установлен")
            return True
        except subprocess.CalledProcessError:
            print("❌ Не удалось установить PyInstaller")
            return False

def clean_build():
    """Очищаем предыдущие сборки"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.pyc', '*.pyo']
    
    for directory in dirs_to_clean:
        if Path(directory).exists():
            print(f"🧹 Удаляю {directory}/")
            shutil.rmtree(directory)
    
    # Удаляем .pyc файлы
    for pyc_file in Path('.').rglob('*.pyc'):
        pyc_file.unlink()
    
    print("✅ Очистка завершена")

def create_icon():
    """Создаём простую иконку (опционально)"""
    # Здесь можно добавить код для создания .ico файла
    # Пока просто проверяем наличие
    if not Path('icon.ico').exists():
        print("ℹ️  Иконка не найдена (icon.ico), будет использована стандартная")

def build_exe():
    """Собираем EXE файл"""
    print("🔨 Начинаю сборку...")
    
    # Команда PyInstaller
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        'markdown_editor.spec'
    ]
    
    try:
        print("📦 Запускаю PyInstaller...")
        print(f"Команда: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Сборка успешна!")
            return True
        else:
            print("❌ Ошибка сборки:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Ошибка выполнения PyInstaller: {e}")
        return False

def test_exe():
    """Тестируем собранный EXE"""
    exe_path = Path('dist/MarkdownEditor.exe')
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ EXE файл создан: {exe_path}")
        print(f"📏 Размер: {size_mb:.1f} МБ")
        
        # Опционально: краткий тест запуска
        print("🧪 Хотите протестировать EXE? (y/n): ", end='')
        try:
            if input().lower().startswith('y'):
                print("🚀 Запускаю тест...")
                subprocess.Popen([str(exe_path)], shell=True)
        except:
            pass
        
        return True
    else:
        print("❌ EXE файл не найден")
        return False

def create_installer_info():
    """Создаём информацию об установке"""
    readme_path = Path('dist/README_EXE.txt')
    readme_content = """
ВЕБЕРАКТОР MARKDOWN - ИСПОЛНЯЕМЫЙ ФАЙЛ
=====================================

Это автономная версия веб-редактора Markdown.

📁 СОДЕРЖИМОЕ:
- MarkdownEditor.exe - главный исполняемый файл

🚀 ЗАПУСК:
1. Запустите MarkdownEditor.exe
2. Дождитесь открытия браузера
3. Если браузер не открылся, перейдите по адресу: http://127.0.0.1:5000

💡 СОВЕТЫ:
- Файлы сохраняются в папке uploads/ рядом с EXE
- Используйте Ctrl+C в консоли для остановки сервера
- При первом запуске создастся папка с примерами файлов

🔧 СИСТЕМНЫЕ ТРЕБОВАНИЯ:
- Windows 7/8/10/11
- 50 МБ свободного места
- Порт 5000 должен быть свободен

❓ ПОДДЕРЖКА:
При возникновении проблем проверьте:
1. Антивирус не блокирует файл
2. Порт 5000 не занят другой программой
3. У вас есть права на запись в папку с программой

Создано на основе проекта md_reader
© 2025 md_reader team
"""
    
    readme_path.write_text(readme_content, encoding='utf-8')
    print(f"📝 Создан файл инструкций: {readme_path}")

def main():
    """Главная функция сборки"""
    print_banner()
    
    # Проверяем рабочую директорию
    if not Path('main.py').exists():
        print("❌ Файл main.py не найден. Убедитесь что вы в папке web_editor")
        return False
    
    # Шаги сборки
    steps = [
        ("Проверка PyInstaller", check_pyinstaller),
        ("Очистка предыдущих сборок", clean_build),
        ("Создание иконки", create_icon),
        ("Сборка EXE", build_exe),
        ("Тестирование EXE", test_exe),
        ("Создание инструкций", create_installer_info)
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        try:
            if not step_func():
                print(f"❌ Ошибка на этапе: {step_name}")
                return False
        except Exception as e:
            print(f"❌ Исключение на этапе {step_name}: {e}")
            return False
    
    print(f"""
🎉 СБОРКА ЗАВЕРШЕНА УСПЕШНО!

📁 Результат: dist/MarkdownEditor.exe
📏 Проверьте папку dist/ для всех файлов

🚀 Теперь вы можете:
1. Запустить MarkdownEditor.exe
2. Скопировать dist/ на другой компьютер
3. Поделиться EXE файлом с другими

💡 EXE файл полностью автономный и не требует установки Python!
""")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        if not success:
            print("\n❌ Сборка неуспешна")
            input("Нажмите Enter для выхода...")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Сборка прервана пользователем")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        input("Нажмите Enter для выхода...")