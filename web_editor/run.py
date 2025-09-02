#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт запуска веб-редактора Markdown
Launch script for Web Markdown Editor

Использование:
    python run.py
    python run.py --port 8080
    python run.py --host 0.0.0.0 --port 5000 --debug
"""

import os
import sys
import argparse
from pathlib import Path

# Добавляем путь к модулям md_reader
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(current_dir))

# Импортируем приложение
try:
    from app import app
except ImportError:
    print("❌ Ошибка: не удалось импортировать приложение Flask")
    print("Убедитесь что вы находитесь в папке web_editor")
    sys.exit(1)

def setup_directories():
    """Создаём необходимые директории"""
    directories = [
        'uploads',
        'logs',
        'cache',
        'static/css',
        'static/js',
        'static/images',
        'templates'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Директория {directory} готова")

def check_dependencies():
    """Проверяем наличие необходимых зависимостей"""
    required_packages = [
        'flask',
        'rich',
        'markdown_it',
        'textual',
        'typer'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} установлен")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} не найден")
    
    if missing_packages:
        print(f"\n❌ Отсутствуют пакеты: {', '.join(missing_packages)}")
        print("Установите их командой:")
        print(f"pip install {' '.join(missing_packages)}")
        print("Или используйте файл зависимостей:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def create_sample_files():
    """Создаём примеры файлов для демонстрации"""
    uploads_dir = Path('uploads')
    
    # Создаём приветственный файл
    welcome_file = uploads_dir / 'добро_пожаловать.md'
    if not welcome_file.exists():
        welcome_content = """# Добро пожаловать в веб-редактор Markdown! 🚀

Это **красочный и удобный** редактор для работы с Markdown документами прямо в вашем браузере.

## ✨ Основные возможности

- 🎨 **Красивый интерфейс** с современным дизайном
- 👀 **Живой предварительный просмотр** - видите результат в реальном времени
- 🌈 **Подсветка синтаксиса** для удобного редактирования
- 📋 **Автоматическое оглавление** для быстрой навигации
- 💾 **Автосохранение** каждые 30 секунд
- ⌨️ **Горячие клавиши** для быстрой работы
- 🔍 **Быстрый поиск** файлов (Ctrl+Shift+O)

## 🛠️ Как использовать

### Создание нового файла
1. Нажмите кнопку "**Новый**" в шапке
2. Введите название файла
3. Начните печатать!

### Открытие существующего файла
- Выберите файл в боковой панели
- Или нажмите "**Открыть**" для загрузки с компьютера
- Или перетащите .md файл в окно редактора

### Режимы просмотра
- 📝 **Редактор** - только редактирование
- 👁️ **Предварительный просмотр** - только просмотр результата  
- ⚡ **Разделённый режим** - редактор и просмотр одновременно

## 📝 Синтаксис Markdown

### Заголовки
```markdown
# Заголовок 1 уровня
## Заголовок 2 уровня  
### Заголовок 3 уровня
```

### Форматирование текста
```markdown
**Жирный текст**
*Курсив*
~~Зачёркнутый~~
`Код в строке`
```

### Ссылки и изображения
```markdown
[Текст ссылки](https://example.com)
![Описание изображения](https://example.com/image.jpg)
```

### Списки
```markdown
- Маркированный список
- Ещё один пункт

1. Нумерованный список
2. Второй пункт

- [ ] Задача
- [x] Выполненная задача
```

### Цитаты
```markdown
> Это цитата
> Она может быть многострочной
```

### Блоки кода
```markdown
```python
def hello_world():
    print("Привет, мир!")
    return "🌍"
```
```

### Таблицы
```markdown
| Колонка 1 | Колонка 2 | Колонка 3 |
|-----------|-----------|-----------|
| Ячейка 1  | Ячейка 2  | Ячейка 3  |
| Ячейка 4  | Ячейка 5  | Ячейка 6  |
```

## ⌨️ Горячие клавиши

| Комбинация | Действие |
|------------|----------|
| `Ctrl+S` | Сохранить файл |
| `Ctrl+O` | Открыть файл |
| `Ctrl+N` | Новый файл |
| `Ctrl+Shift+O` | Быстрое открытие |
| `F11` | Полноэкранный режим |
| `F1` | Справка |

## 🎨 Дополнительные возможности

### Эмодзи в тексте
Поддерживаются все эмодзи Unicode: 😀 🎉 💡 ⚡ 🔥 🚀 ⭐ ✅ ❌ 

### Математические формулы (планируется)
В будущих версиях планируется поддержка LaTeX математики.

### Диаграммы (планируется)  
Будет добавлена поддержка Mermaid диаграмм.

---

## 🤝 Обратная связь

Если у вас есть предложения по улучшению редактора или вы нашли ошибку, сообщите нам!

**Удачной работы с редактором!** ✨

> Создано с ❤️ на основе проекта md_reader
"""
        welcome_file.write_text(welcome_content, encoding='utf-8')
        print(f"✓ Создан файл примера: {welcome_file}")
    
    # Создаём файл с документацией по API
    api_doc_file = uploads_dir / 'api_документация.md'
    if not api_doc_file.exists():
        api_content = """# API документация веб-редактора

## Эндпоинты REST API

### GET /api/files
Получить список всех Markdown файлов

**Ответ:**
```json
{
    "status": "success",
    "message": "Найдено N файлов",
    "files": [
        {
            "name": "example.md",
            "size": 1024,
            "modified": 1640995200,
            "path": "example.md"
        }
    ]
}
```

### GET /api/file/<filename>
Получить содержимое файла

**Ответ:**
```json
{
    "status": "success", 
    "message": "Файл загружен",
    "content": "# Содержимое файла...",
    "filename": "example.md",
    "toc": [["Заголовок", 1, 0]]
}
```

### POST /api/file/<filename>
Сохранить содержимое файла

**Запрос:**
```json
{
    "content": "# Новое содержимое..."
}
```

### POST /api/upload
Загрузить новый файл

**Запрос:** multipart/form-data с файлом

### POST /api/new
Создать новый файл

**Запрос:**
```json
{
    "filename": "новый_файл.md"
}
```

### GET /api/download/<filename>
Скачать файл

Возвращает файл для скачивания.
"""
        api_doc_file.write_text(api_content, encoding='utf-8')
        print(f"✓ Создан файл API документации: {api_doc_file}")

def print_banner():
    """Выводим красивый баннер"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                   🚀 ВЕБ-РЕДАКТОР MARKDOWN 🚀                ║
║                                                              ║
║  Красочный и удобный редактор для работы с Markdown         ║
║  Создан на основе проекта md_reader                         ║
║                                                              ║
║  Все сообщения интерфейса на русском языке 🇷🇺                ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def main():
    """Главная функция запуска"""
    parser = argparse.ArgumentParser(
        description="Веб-редактор Markdown с русским интерфейсом"
    )
    parser.add_argument(
        '--host', 
        default='127.0.0.1',
        help='Хост для запуска сервера (по умолчанию: 127.0.0.1)'
    )
    parser.add_argument(
        '--port',
        type=int, 
        default=5000,
        help='Порт для запуска сервера (по умолчанию: 5000)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Запуск в режиме отладки'
    )
    parser.add_argument(
        '--no-browser',
        action='store_true', 
        help='Не открывать браузер автоматически'
    )
    
    args = parser.parse_args()
    
    print_banner()
    print("🔧 Подготовка к запуску...")
    
    # Проверяем зависимости
    if not check_dependencies():
        sys.exit(1)
    
    # Создаём директории
    setup_directories()
    
    # Создаём примеры файлов
    create_sample_files()
    
    print("\n🎉 Всё готово к запуску!")
    
    # Настройки Flask
    app.config['DEBUG'] = args.debug
    
    # URL сервера
    url = f"http://{args.host}:{args.port}"
    
    print(f"""
📡 Запуск сервера...
🌐 URL: {url}
📁 Папка файлов: uploads/
🔧 Режим отладки: {'включён' if args.debug else 'отключён'}

💡 Советы:
   • Откройте {url} в браузере
   • Используйте Ctrl+C для остановки сервера
   • Файлы сохраняются в папке uploads/
   • Посмотрите файл 'добро_пожаловать.md' для начала работы
""")
    
    # Автоматически открываем браузер
    if not args.no_browser:
        import webbrowser
        import threading
        import time
        
        def open_browser():
            time.sleep(1.5)  # Ждём запуска сервера
            webbrowser.open(url)
        
        threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        # Запускаем Flask сервер
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            use_reloader=args.debug
        )
    except KeyboardInterrupt:
        print("\n\n👋 Сервер остановлен. До свидания!")
    except Exception as e:
        print(f"\n❌ Ошибка запуска сервера: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()