#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрационная версия Markdown редактора
Упрощенная версия для тестирования без EXE
"""

import os
import sys
import threading
import time
import webbrowser
from pathlib import Path
import socket

# Простой демонстрационный сервер без Flask
import http.server
import socketserver
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

class MarkdownHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_demo_page()
        elif self.path.startswith('/api/'):
            self.handle_api_get()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path.startswith('/api/'):
            self.handle_api_post()
        else:
            self.send_error(404)
    
    def send_demo_page(self):
        """Отправка демонстрационной страницы"""
        html_content = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown Редактор - Демо</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }
        .content { display: grid; grid-template-columns: 1fr 1fr; min-height: 500px; }
        .editor-section, .preview-section { padding: 20px; }
        .editor-section { background: #2d2d2d; }
        .preview-section { background: white; border-left: 1px solid #ddd; }
        textarea { width: 100%; height: 400px; background: #2d2d2d; color: #f8f8f2; border: none; outline: none; font-family: monospace; padding: 10px; resize: none; }
        .preview { height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; background: white; }
        .controls { padding: 20px; background: #f9f9f9; text-align: center; }
        .btn { background: #4CAF50; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #45a049; }
        .status { color: #666; margin-top: 10px; }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📝 Markdown Редактор - Демонстрация</h1>
            <p>Упрощенная версия для демонстрации функциональности</p>
        </div>
        
        <div class="content">
            <div class="editor-section">
                <h3 style="color: #f8f8f2; margin-top: 0;">Редактор</h3>
                <textarea id="editor" placeholder="Введите ваш Markdown текст здесь..."># Добро пожаловать в Markdown редактор!

Это демонстрационная версия редактора.

## Возможности

- ✅ Редактирование Markdown
- ✅ Предпросмотр в реальном времени  
- ✅ Простой интерфейс
- ✅ Поддержка русского языка

## Пример синтаксиса

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

### Код
```python
def hello():
    print("Привет, мир!")
```

Измените этот текст и посмотрите предпросмотр справа!</textarea>
            </div>
            
            <div class="preview-section">
                <h3 style="margin-top: 0;">Предпросмотр</h3>
                <div id="preview" class="preview"></div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="saveDemo()">Сохранить в localStorage</button>
            <button class="btn" onclick="loadDemo()">Загрузить из localStorage</button>
            <button class="btn" onclick="clearEditor()">Очистить</button>
            <div class="status" id="status">Готов к работе</div>
        </div>
    </div>

    <script>
        const editor = document.getElementById('editor');
        const preview = document.getElementById('preview');
        const status = document.getElementById('status');
        
        function updatePreview() {
            const markdownText = editor.value;
            try {
                const html = marked.parse(markdownText);
                preview.innerHTML = html;
            } catch (error) {
                preview.innerHTML = '<p style="color: red;">Ошибка: ' + error.message + '</p>';
            }
        }
        
        function saveDemo() {
            localStorage.setItem('markdown_demo', editor.value);
            status.textContent = 'Сохранено в браузере';
            setTimeout(() => status.textContent = 'Готов к работе', 2000);
        }
        
        function loadDemo() {
            const saved = localStorage.getItem('markdown_demo');
            if (saved) {
                editor.value = saved;
                updatePreview();
                status.textContent = 'Загружено из браузера';
                setTimeout(() => status.textContent = 'Готов к работе', 2000);
            } else {
                status.textContent = 'Нет сохраненных данных';
                setTimeout(() => status.textContent = 'Готов к работе', 2000);
            }
        }
        
        function clearEditor() {
            if (confirm('Очистить редактор?')) {
                editor.value = '';
                updatePreview();
                status.textContent = 'Редактор очищен';
                setTimeout(() => status.textContent = 'Готов к работе', 2000);
            }
        }
        
        editor.addEventListener('input', updatePreview);
        
        // Начальное обновление
        updatePreview();
        
        // Попытка загрузить сохраненное
        window.addEventListener('load', () => {
            const saved = localStorage.getItem('markdown_demo');
            if (saved && confirm('Загрузить сохраненный текст?')) {
                loadDemo();
            }
        });
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(html_content.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def handle_api_get(self):
        """Обработка GET API запросов"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status": "demo_mode"}')
    
    def handle_api_post(self):
        """Обработка POST API запросов"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"success": true, "message": "Demo mode"}')

def find_free_port():
    """Поиск свободного порта"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def open_browser(port):
    """Открытие браузера с задержкой"""
    time.sleep(1)
    url = f"http://127.0.0.1:{port}"
    try:
        webbrowser.open(url)
        print(f"Браузер открыт: {url}")
    except Exception as e:
        print(f"Не удалось открыть браузер: {e}")
        print(f"Откройте браузер вручную: {url}")

def run_demo_server():
    """Запуск демонстрационного сервера"""
    port = find_free_port()
    
    print("=" * 50)
    print("    ДЕМОНСТРАЦИОННЫЙ MARKDOWN РЕДАКТОР")
    print("=" * 50)
    print(f"Запуск сервера на порту: {port}")
    print(f"Адрес: http://127.0.0.1:{port}")
    print()
    print("Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    # Запуск браузера в отдельном потоке
    browser_thread = threading.Thread(target=open_browser, args=(port,), daemon=True)
    browser_thread.start()
    
    try:
        with HTTPServer(('127.0.0.1', port), MarkdownHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен")
    except Exception as e:
        print(f"Ошибка сервера: {e}")

if __name__ == '__main__':
    run_demo_server()