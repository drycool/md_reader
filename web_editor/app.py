#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Веб-редактор Markdown
Исправление проблемы с пустым экраном
"""

import os
import sys
import threading
import time
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket

def find_free_port():
    """Поиск свободного порта"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

class MarkdownHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_editor_page()
        else:
            super().do_GET()
    
    def send_editor_page(self):
        """Отправка страницы редактора"""
        html_content = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown Редактор</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; height: 100vh; }
        .header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 15px; text-align: center; }
        .container { display: grid; grid-template-columns: 1fr 1fr; height: calc(100vh - 60px); }
        .editor-section, .preview-section { padding: 10px; }
        .editor-section { background: #2d2d2d; }
        .preview-section { background: white; border-left: 1px solid #ddd; }
        textarea { width: 100%; height: 100%; background: #2d2d2d; color: #f8f8f2; border: none; font-family: monospace; padding: 15px; resize: none; }
        .preview { height: 100%; overflow-y: auto; padding: 15px; background: white; }
        .footer { background: #333; color: white; padding: 8px 15px; font-size: 12px; }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body>
    <div class="header">
        <h1>📝 Markdown Редактор</h1>
        <p>Веб-редактор для файлов Markdown</p>
    </div>
    
    <div class="container">
        <div class="editor-section">
            <textarea id="editor" placeholder="Введите ваш Markdown текст здесь..."># Добро пожаловать в Markdown редактор!

Это веб-редактор для создания и редактирования файлов Markdown.

## Возможности

- ✅ Редактирование в реальном времени
- ✅ Предпросмотр справа
- ✅ Поддержка полного синтаксиса Markdown
- ✅ Русскоязычный интерфейс

## Пример синтаксиса

### Заголовки
# Заголовок 1
## Заголовок 2
### Заголовок 3

### Форматирование
**Жирный текст**
*Курсив*
`Код`

### Списки
- Пункт 1
- Пункт 2
- Пункт 3

1. Нумерованный список
2. Второй пункт
3. Третий пункт

### Код
```
function hello() {
    console.log("Привет, мир!");
}
```

Начните редактировать и увидите результат справа!</textarea>
        </div>
        
        <div class="preview-section">
            <div id="preview" class="preview"></div>
        </div>
    </div>
    
    <div class="footer">
        Статус: Готов | Markdown Редактор v1.0
    </div>

    <script>
        const editor = document.getElementById('editor');
        const preview = document.getElementById('preview');
        
        function updatePreview() {
            const text = editor.value;
            try {
                const html = marked.parse(text);
                preview.innerHTML = html;
            } catch (error) {
                preview.innerHTML = '<p style="color: red;">Ошибка: ' + error.message + '</p>';
            }
        }
        
        editor.addEventListener('input', updatePreview);
        window.addEventListener('load', updatePreview);
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(html_content.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))

def open_browser(port):
    """Открытие браузера"""
    time.sleep(1)
    url = f"http://127.0.0.1:{port}"
    webbrowser.open(url)
    print(f"Браузер открыт: {url}")

def run_server():
    """Запуск сервера"""
    port = find_free_port()
    
    print("=" * 50)
    print("    MARKDOWN РЕДАКТОР")
    print("=" * 50)
    print(f"Сервер запущен на: http://127.0.0.1:{port}")
    print("Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    # Открытие браузера
    browser_thread = threading.Thread(target=open_browser, args=(port,), daemon=True)
    browser_thread.start()
    
    try:
        with HTTPServer(('127.0.0.1', port), MarkdownHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен")

if __name__ == '__main__':
    run_server()