# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MD Reader - инструмент для просмотра и редактирования Markdown документов:
- **CLI Viewer** - терминальный интерфейс (Textual TUI)
- **Web Editor** - веб-приложение (встроенный HTTP сервер, без внешних зависимостей)
- **EXE** - автономный исполняемый файл для Windows

## Commands

```bash
# Установка зависимостей
cd web_editor
pip install flask markdown

# Запуск Python версии
cd web_editor
python app.py                      # выбор файла
python app.py файл.md              # просмотр
python app.py файл.md edit        # редактирование

# Запуск EXE версии
MarkdownReader.exe                 # выбор файла
MarkdownReader.exe файл.md        # просмотр
MarkdownReader.exe файл.md edit   # редактирование

# Тестирование
pytest
pytest -m unit

# Сборка EXE
cd web_editor
py -m PyInstaller --onefile --console --name "MarkdownReader" md_reader_exe.py
```

## Quick Start (Windows)

| Файл | Описание |
|------|----------|
| `view_demo.bat` | Открыть demo.md в просмотрщике |
| `edit_demo.bat` | Открыть demo.md в редакторе |
| `MarkdownReader.exe` | Запуск приложения |
| `test_exe_view.bat` | Тест EXE с demo.md |

## Architecture

```
md_reader/
├── md_reader/           # Core CLI библиотека (Textual TUI)
│   ├── cli.py          # Typer CLI
│   └── tui.py          # Textual приложение
│
├── web_editor/          # Веб-приложение
│   ├── app.py          # Flask приложение
│   ├── md_reader_exe.py # Автон版本 (встроенный HTTP сервер)
│   └── templates/      # HTML шаблоны
│       ├── viewer.html  # Просмотрщик
│       └── editor.html  # Редактор
│
├── MarkdownReader.exe   # Готовый EXE
├── view_demo.bat       # Быстрый запуск просмотра
└── edit_demo.bat       # Быстрый запуск редактора
```

## Key Features

- **Просмотрщик**: оглавление из заголовков, навигация, минималистичный дизайн
- **Редактор**: предпросмотр в реальном времени, сохранение, форматирование
- **Автономность**: встроенный markdown парсер (без внешних библиотек)
- **Drag-and-drop**: перетаскивание файлов

## Known Issues

- Тестирование: при запуске могут быть проблемы с браузером (проверить логи в консоли)
- Логирование: используется файл `md_reader.log` для отладки
