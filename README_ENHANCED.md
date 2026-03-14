# MD Reader - Enhanced Security & Reliability

**Интерактивный CLI-инструмент для просмотра Markdown документации с улучшенной безопасностью и надежностью.**

## 🚀 Недавние улучшения

### ✅ Фаза 1: Критические улучшения безопасности (Завершена)

#### 🔒 Безопасность и валидация
- **Валидация путей**: Защита от path traversal атак и проверка безопасности файловых путей
- **Безопасная обработка файлов**: Проверка размера файлов, кодировки и прав доступа
- **Валидация пользовательского ввода**: Санитизация поисковых запросов и пользовательского выбора

#### 🐛 Обработка ошибок
- **Кастомные исключения**: Типизированные исключения для различных типов ошибок
- **Централизованное логирование**: Настраиваемая система логирования с различными уровнями
- **Graceful error handling**: Изящная обработка ошибок без аварийного завершения

#### 📊 Мониторинг
- **Статистика загрузки**: Отслеживание успешно загруженных и проблемных файлов
- **Подробное логирование**: Детальная информация о работе приложения
- **Валидация структур данных**: Проверка корректности построенного оглавления

## 📦 Установка

### Способ 1: Готовый EXE (рекомендуется для Windows)

Скачайте готовый исполняемый файл из раздела [Releases](https://github.com/your-repo/md_reader/releases):

```bash
# Запуск без аргументов - выбор файла через диалог
MarkdownReader.exe

# Просмотр файла
MarkdownReader.exe document.md

# Редактирование файла
MarkdownReader.exe document.md edit
```

### Способ 2: Веб-редактор (Flask)

```bash
# Клонирование репозитория
git clone https://github.com/your-repo/md_reader.git
cd md_reader/web_editor

# Установка зависимостей
pip install flask markdown

# Запуск редактора
python app.py                    # выбор файла
python app.py document.md        # просмотр
python app.py document.md edit  # редактирование

# Или через скрипт запуска
python run.py
```

### Способ 3: Python пакет

```bash
# Клонирование репозитория
git clone https://github.com/your-repo/md_reader.git
cd md_reader

# Установка зависимостей
pip install -e .

# Для разработки (включает инструменты тестирования и линтинга)
pip install -e ".[dev]"
```

### Быстрый старт (Windows)

| Файл | Описание |
|------|----------|
| `view_demo.bat` | Открыть demo.md в просмотрщике |
| `edit_demo.bat` | Открыть demo.md в редакторе |

## 🎯 Использование

### Базовое использование
```bash
# TUI режим (рекомендуется)
md-viewer tui /path/to/markdown/files

# CLI режим 
md-viewer open /path/to/markdown/files

# Просмотр одного файла
md-viewer tui document.md
```

### Программное использование
```python
from md_reader.loader import MarkdownLoader
from md_reader.toc import TocBuilder
from md_reader.logger import setup_logging

# Настройка логирования
setup_logging(level="INFO", log_file="md_reader.log")

# Безопасная загрузка файлов
loader = MarkdownLoader()
files = loader.load_markdown_files("/path/to/docs")

# Построение оглавления
builder = TocBuilder()
toc = builder.build_toc(files)

# Получение статистики
print(f"Загружено файлов: {loader.get_stats()}")
print(f"Обработано заголовков: {builder.get_stats()}")
```

## 🔧 Конфигурация

### Настройка логирования
```python
from md_reader.logger import setup_logging

# Логирование в файл
setup_logging(
    level="DEBUG",
    log_file="app.log",
    format_string="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

# Логирование в консоль
setup_logging(level="INFO")
```

### Кастомизация валидации
```python
from md_reader.validators import PathValidator, FileContentValidator

# Изменение максимального размера файла (по умолчанию 10MB)
FileContentValidator.MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Кастомные проверки
try:
    safe_path = PathValidator.validate_markdown_file("document.md")
    print(f"Файл безопасен: {safe_path}")
except PathValidationError as e:
    print(f"Небезопасный путь: {e.message}")
```

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest

# Тесты с покрытием
pytest --cov=md_reader --cov-report=html

# Тесты безопасности
pytest test_security_improvements.py -v

# Проверка безопасности кода
bandit -r md_reader/
```

## 🛠️ Разработка

### Настройка окружения разработки
```bash
# Установка pre-commit hooks
pre-commit install

# Запуск проверок кода
pre-commit run --all-files

# Форматирование кода
black md_reader/
isort md_reader/

# Проверка типов
mypy md_reader/
```

### Архитектурные компоненты

#### Модули безопасности
- `exceptions.py` - Кастомные исключения с контекстом
- `validators.py` - Валидация путей и пользовательского ввода  
- `logger.py` - Централизованное логирование и обработка ошибок

#### Основные модули
- `loader.py` - Безопасная загрузка Markdown файлов
- `toc.py` - Построение оглавления с валидацией
- `viewer.py` - Интерактивный просмотр с защищенным вводом
- `tui.py` - Textual UI интерфейс
- `cli.py` - Command-line интерфейс

## 📋 Roadmap

### 🔄 Фаза 2: Архитектура и производительность (Планируется)
- [ ] Dependency injection и интерфейсы
- [ ] Кэширование файлов и оглавления  
- [ ] Ленивая загрузка для больших проектов

### 🧪 Фаза 3: Тестирование и качество (Планируется)
- [ ] Comprehensive test suite (80%+ покрытие)
- [ ] Автоматизированные проверки качества
- [ ] Performance benchmarking

### 📚 Фаза 4: Документация и CI/CD (Планируется)
- [ ] Автоматизированная сборка и тестирование
- [ ] Подробная документация API
- [ ] Примеры интеграции

## 🔒 Безопасность

Приложение теперь включает множественные уровни защиты:

- **Path Traversal Protection**: Предотвращение доступа к файлам вне разрешенных директорий
- **Input Sanitization**: Очистка и валидация всех пользовательских вводов
- **File Size Limits**: Защита от DoS атак через большие файлы
- **Encoding Validation**: Безопасное определение и обработка кодировок файлов
- **Error Boundaries**: Изоляция ошибок без аварийного завершения

## 🐛 Отчет об ошибках

При обнаружении проблем, пожалуйста, предоставьте:
1. Лог файлы (при включенном логировании)
2. Версию Python и операционной системы
3. Шаги для воспроизведения
4. Результат работы команды с флагом `--debug`

## 📄 Лицензия

MIT License - см. файл LICENSE для деталей.

---

**Статус проекта**: ✅ Фаза 1 завершена | 🔄 Фаза 2 в планах | Версия: 0.2.0