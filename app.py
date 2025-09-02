#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Веб-редактор Markdown
Простой веб-интерфейс для редактирования файлов Markdown
"""

import os
import sys
import threading
import time
import webbrowser
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
import socket

# Предотвращение повторного запуска при компиляции в EXE
if getattr(sys, 'frozen', False):
    # Если запущен как скомпилированный executable
    import multiprocessing
    multiprocessing.freeze_support()

app = Flask(__name__)

# Глобальные переменные
MARKDOWN_DIR = Path("markdown_files")
current_file = None
server_started = False

def ensure_directories():
    """Создание необходимых директорий"""
    MARKDOWN_DIR.mkdir(exist_ok=True)
    Path("templates").mkdir(exist_ok=True)
    Path("static").mkdir(exist_ok=True)

def find_free_port():
    """Поиск свободного порта"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def create_demo_file():
    """Создание демонстрационного файла"""
    demo_content = """# Добро пожаловать в Markdown редактор

Это демонстрационный файл для тестирования редактора.

## Возможности

- Редактирование Markdown файлов
- Предпросмотр в реальном времени
- Сохранение файлов
- Простой и удобный интерфейс

## Синтаксис Markdown

### Заголовки
# H1
## H2
### H3

### Текст
**Жирный текст**
*Курсив*
`Код`

### Списки
- Элемент 1
- Элемент 2
- Элемент 3

1. Первый
2. Второй
3. Третий

### Ссылки
[Пример ссылки](https://example.com)

### Код
```python
def hello():
    print("Привет, мир!")
```

Измените этот текст и посмотрите предпросмотр!
"""
    
    demo_file = MARKDOWN_DIR / "demo.md"
    if not demo_file.exists():
        with open(demo_file, 'w', encoding='utf-8') as f:
            f.write(demo_content)

@app.route('/')
def index():
    """Главная страница"""
    files = []
    if MARKDOWN_DIR.exists():
        files = [f.name for f in MARKDOWN_DIR.glob("*.md")]
    return render_template('index.html', files=files)

@app.route('/api/files')
def list_files():
    """API для получения списка файлов"""
    files = []
    if MARKDOWN_DIR.exists():
        files = [f.name for f in MARKDOWN_DIR.glob("*.md")]
    return jsonify(files)

@app.route('/api/file/<filename>')
def get_file(filename):
    """API для получения содержимого файла"""
    try:
        file_path = MARKDOWN_DIR / filename
        if file_path.exists() and file_path.suffix == '.md':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({'success': True, 'content': content})
        else:
            return jsonify({'success': False, 'error': 'Файл не найден'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/file/<filename>', methods=['POST'])
def save_file(filename):
    """API для сохранения файла"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        file_path = MARKDOWN_DIR / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({'success': True, 'message': 'Файл сохранен'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/new', methods=['POST'])
def new_file():
    """API для создания нового файла"""
    try:
        data = request.get_json()
        filename = data.get('filename', '')

        if not filename.endswith('.md'):
            filename += '.md'

        file_path = MARKDOWN_DIR / filename
        if file_path.exists():
            return jsonify({'success': False, 'error': 'Файл уже существует'})

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('# Новый документ\n\nВведите ваш текст здесь...')

        return jsonify({'success': True, 'message': 'Файл создан'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/file/<filename>', methods=['DELETE'])
def delete_file(filename):
    """API для удаления файла"""
    try:
        file_path = MARKDOWN_DIR / filename
        if file_path.exists() and file_path.suffix == '.md':
            file_path.unlink()
            return jsonify({'success': True, 'message': 'Файл удален'})
        else:
            return jsonify({'success': False, 'error': 'Файл не найден'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/export/<filename>/<format>')
def export_file(filename, format):
    """API для экспорта файла в разные форматы"""
    try:
        file_path = MARKDOWN_DIR / filename
        if not file_path.exists() or file_path.suffix != '.md':
            return jsonify({'success': False, 'error': 'Файл не найден'})

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if format == 'html':
            # Простой HTML экспорт
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{filename}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 4px; }}
        code {{ background: #f4f4f4; padding: 2px 4px; }}
        blockquote {{ border-left: 4px solid #ccc; padding-left: 10px; }}
    </style>
</head>
<body>
    {content}
</body>
</html>"""
            return html_content, 200, {'Content-Type': 'text/html', 'Content-Disposition': f'attachment; filename={filename.replace(".md", ".html")}'}

        elif format == 'txt':
            # Экспорт в обычный текст
            import re
            # Удаляем Markdown синтаксис
            text = re.sub(r'#+\s*', '', content)  # Заголовки
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Жирный
            text = re.sub(r'\*(.*?)\*', r'\1', text)  # Курсив
            text = re.sub(r'`(.*?)`', r'\1', text)  # Код
            text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # Ссылки
            return text, 200, {'Content-Type': 'text/plain', 'Content-Disposition': f'attachment; filename={filename.replace(".md", ".txt")}'}

        else:
            return jsonify({'success': False, 'error': 'Неподдерживаемый формат'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def open_browser(port):
    """Открытие браузера с задержкой"""
    time.sleep(1.5)  # Ждем запуска сервера
    url = f"http://127.0.0.1:{port}"
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Не удалось открыть браузер: {e}")
        print(f"Откройте браузер вручную и перейдите по адресу: {url}")

def run_server():
    """Запуск Flask сервера"""
    global server_started
    
    if server_started:
        print("Сервер уже запущен!")
        return
    
    ensure_directories()
    create_demo_file()
    
    port = find_free_port()
    server_started = True
    
    print(f"Запуск Markdown редактора...")
    print(f"Открытие браузера по адресу: http://127.0.0.1:{port}")
    
    # Открываем браузер в отдельном потоке только если не EXE или первый запуск
    if not getattr(sys, 'frozen', False) or os.environ.get('BROWSER_OPENED') != 'true':
        os.environ['BROWSER_OPENED'] = 'true'
        browser_thread = threading.Thread(target=open_browser, args=(port,), daemon=True)
        browser_thread.start()
    
    try:
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Ошибка запуска сервера: {e}")
        print("Попробуйте запустить приложение снова")

if __name__ == '__main__':
    run_server()
