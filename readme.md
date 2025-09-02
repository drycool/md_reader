# MD Reader - Markdown Documentation Tool

MD Reader is a comprehensive tool for viewing and editing Markdown documents. It includes both a command-line interface (CLI) for browsing documentation and a web-based editor for creating and modifying Markdown files.

## Features

### CLI Viewer
- Interactive viewing of Markdown files and directories
- Automatic table of contents generation
- Fuzzy search through headers
- Syntax-highlighted section viewing
- Caching for improved performance
- Security enhancements (path validation, input sanitization)

### Web Editor
- Modern web-based editor with real-time preview
- Syntax highlighting for code blocks
- Automatic table of contents navigation
- Auto-save functionality
- Drag-and-drop file support
- Fully localized Russian interface
- Responsive design for all devices

## Documentation

### For Users
- [User Guide (English)](docs/USER_GUIDE_EN.md) - Complete guide for using MD Reader
- [Руководство пользователя (Russian)](docs/USER_GUIDE_RU.md) - Полное руководство по использованию MD Reader

### For Developers
- [Specification (English)](docs/SPECIFICATION_EN.md) - Technical specification of the project
- [Спецификация (Russian)](docs/SPECIFICATION_RU.md) - Техническая спецификация проекта
- [README_ENHANCED.md](README_ENHANCED.md) - Enhanced security and reliability features
- [PROJECT_COMPLETION_SUMMARY.md](PROJECT_COMPLETION_SUMMARY.md) - Project completion summary

### Component Documentation
- [md_reader CLI documentation](md_reader/readme.md) - Documentation for the command-line interface
- [web_editor documentation](web_editor/README.md) - Documentation for the web editor

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd md_reader

# Install in development mode
pip install -e .

# For development (includes testing tools)
pip install -e ".[dev]"
```

## Usage

### CLI Mode
```bash
# View a single file in interactive mode
md-viewer open document.md

# View all files in a directory
md-viewer open /path/to/markdown/files

# Launch TUI interface
md-viewer tui /path/to/markdown/files
```

### Web Editor
```bash
# Navigate to the web editor directory
cd web_editor

# Run the editor
python run.py
```

## Project Structure

```
md_reader/
├── md_reader/              # Core CLI library
├── web_editor/             # Web-based editor
├── docs/                   # Documentation
├── tests/                  # Test suite
├── dist/                   # Compiled executables
└── README.md               # This file
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# Web-редактор для файлов Markdown с интуитивно понятным интерфейсом на русском языке.

## Особенности

- 🌐 Веб-интерфейс с разделенным экраном (редактор + предпросмотр)
- 📝 Редактирование и предпросмотр Markdown в реальном времени
- 💾 Сохранение и загрузка файлов
- 📁 Управление множественными файлами
- 🎨 Современный и удобный интерфейс
- 🇷🇺 Полная локализация на русский язык
- 📦 Возможность компиляции в исполняемый файл (.exe)
- 📂 **Выбор локальных файлов** - загрузка .md и .txt файлов с компьютера
- 🖱️ **Drag-and-Drop** - перетаскивание файлов в редактор
- 📤 **Экспорт документов** - HTML и TXT форматы
- 🔍 **Синтаксическая подсветка** кода с Prism.js
- ⚡ **Быстрый запуск** - автономный EXE без установки Python

## 📋 Что нового (v2.0)

### ✨ Добавленные возможности
- **📂 Выбор локальных файлов** - загрузка .md и .txt файлов с компьютера
- **🖱️ Drag-and-Drop** - перетаскивание файлов в редактор
- **📤 Экспорт в HTML** - сохранение документов с форматированием
- **📝 Экспорт в TXT** - очистка Markdown синтаксиса
- **🔍 Синтаксическая подсветка** - Prism.js для блоков кода
- **⚡ Автономный EXE** - готовый исполняемый файл без Python

### 🔧 Технические улучшения
- **Обновлённые зависимости** - Flask 3.1.2, PyInstaller 6.15.0
- **Виртуальное окружение** - изолированная среда сборки
- **Улучшенная архитектура** - RESTful API для управления файлами
- **HTML5 APIs** - File API, Drag-and-Drop, Blob API

### 🎨 Улучшения интерфейса
- **Стильная кнопка выбора файла** с иконкой
- **Визуальная обратная связь** при перетаскивании
- **Индикатор несохранённых изменений** (красная точка)
- **Счётчик слов** в статусной строке
- **Модальные окна** для создания файлов

## Быстрый старт

### Метод 1: Запуск через Python

``bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск приложения
python app.py
```

### Метод 2: Демонстрационная версия

``bash
# Запуск упрощенной версии (без Flask)
python run_demo.py
```

### Метод 3: Готовый исполняемый файл

``bash
# Просто запустите готовый файл
.\dist\MarkdownEditor.exe
```

### Метод 4: Сборка из исходников

``bash
# Базовая сборка
build.bat

# Расширенная сборка (рекомендуется)
build_advanced.bat
```

## Решение проблем

### Проблема: Бесконечный цикл открытия браузера

Если при запуске MarkdownEditor.exe браузер открывается многократно:

1. **Используйте улучшенную версию** - в `app.py` добавлены защитные механизмы
2. **Переменная окружения** - приложение использует `BROWSER_OPENED` для предотвращения повторных запусков
3. **Запуск в режиме отладки**:
   ```bash
   set BROWSER_OPENED=true
   MarkdownEditor.exe
   ```

### Проблема: Невозможно подключиться к 127.0.0.1

1. **Проверьте порт** - приложение автоматически находит свободный порт
2. **Брандмауэр** - убедитесь, что брандмауэр не блокирует соединение
3. **Антивирус** - добавьте приложение в исключения
4. **Альтернативный запуск**:
   ```bash
   python run_demo.py
   ```

### Проблема: Ошибки компиляции

1. **Обновите PyInstaller**:
   ```bash
   pip install --upgrade pyinstaller
   ```

2. **Используйте базовую сборку**:
   ```bash
   pyinstaller --onefile --add-data="templates;templates" --add-data="static;static" app.py
   ```

3. **Проверьте зависимости**:
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

## Структура проекта

```
md_reader/
├── app.py                 # Основное приложение Flask с API
├── run_demo.py           # Демонстрационная версия
├── requirements.txt      # Зависимости Python
├── build.bat            # Скрипт сборки с виртуальным окружением
├── build_advanced.bat   # Расширенный скрипт сборки
├── readme.md            # Основная документация
├── README_ENHANCED.md   # Расширенная документация
├── templates/
│   └── index.html       # HTML шаблон с полным интерфейсом
├── static/              # Статические файлы (создается автоматически)
├── markdown_files/      # Папка для Markdown файлов (создается автоматически)
├── dist/
│   ├── MarkdownEditor.exe    # Автономный исполняемый файл
│   └── MarkdownEditor_old.exe # Предыдущая версия
└── venv/               # Виртуальное окружение Python
```

## Технические детали

### Зависимости

- **Flask 3.1.2** - веб-фреймворк с улучшенной производительностью
- **PyInstaller 6.15.0** - для создания автономных EXE файлов
- **Marked.js 4.0.10** - обработка Markdown на клиенте
- **Prism.js 1.29.0** - синтаксическая подсветка кода

### Новые возможности

#### 📂 Локальная загрузка файлов
- **File API**: Использование HTML5 File API для чтения локальных файлов
- **FileReader**: Асинхронное чтение содержимого файлов
- **Валидация**: Проверка типов файлов (.md, .txt) и размера
- **Drag-and-Drop**: HTML5 Drag and Drop API для удобной загрузки

#### 📤 Экспорт документов
- **HTML экспорт**: Генерация полностраничного HTML с CSS стилями
- **TXT экспорт**: Очистка Markdown синтаксиса с сохранением структуры
- **Blob API**: Создание и скачивание файлов через браузер
- **Автоматическое именование**: Умное именование экспортированных файлов

#### 🔧 Улучшенная архитектура
- **RESTful API**: Полноценное API для управления файлами
- **Виртуальное окружение**: Изолированная среда Python
- **Автономная сборка**: EXE без зависимостей от системного Python

### Защита от циклов

Приложение включает несколько механизмов защиты:

1. **Проверка frozen состояния** - определение запуска как EXE
2. **Переменная окружения** - `BROWSER_OPENED` предотвращает повторные запуски
3. **Multiprocessing.freeze_support()** - поддержка многопроцессности в EXE
4. **Проверка порта** - автоматический поиск свободного порта

### Файлы Markdown

- Создаются в папке `markdown_files/`
- Автоматическое создание демонстрационного файла
- Поддержка полного синтаксиса Markdown
- Автосохранение изменений

## Использование

1. **Запустите приложение** любым из способов выше
2. **Откроется браузер** с интерфейсом редактора
3. **Выберите файл** из списка в боковой панели или создайте новый
4. **Загрузите локальный файл**:
   - Нажмите кнопку "📁 Выбрать файл" в панели инструментов
   - Или перетащите .md/.txt файл в область редактора
5. **Редактируйте** в левой панели, **просматривайте** в правой
6. **Экспортируйте** документ кнопками "Экспорт HTML" или "Экспорт TXT"
7. **Сохраняйте** изменения кнопкой "Сохранить" или Ctrl+S

### Работа с локальными файлами

- **Выбор файла**: Кнопка "📁 Выбрать файл" открывает диалог выбора
- **Drag-and-Drop**: Перетащите файл в область редактора для мгновенной загрузки
- **Поддержка форматов**: .md (Markdown) и .txt (обычный текст)
- **Предупреждения**: Система предупредит о несохранённых изменениях
- **Только чтение**: Локальные файлы нельзя сохранить на сервер (работают локально)

### Экспорт документов

- **HTML экспорт**: Сохраняет документ с полным форматированием и стилями
- **TXT экспорт**: Удаляет Markdown синтаксис, оставляя чистый текст
- **Автоматическое скачивание**: Файлы автоматически скачиваются в папку загрузок

## Горячие клавиши

- `Ctrl + S` - Сохранить файл
- `Ctrl + N` - Новый файл (в планах)

## Поддержка

При возникновении проблем:

1. Проверьте логи в консоли
2. Попробуйте демонстрационную версию
3. Пересоберите EXE с чистого окружения
4. Убедитесь в корректности установки зависимостей

## Лицензия

MIT License - свободное использование и модификация.
