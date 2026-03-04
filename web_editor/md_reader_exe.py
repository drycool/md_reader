#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown Reader - Standalone EXE version
"""

import sys
import threading
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket
import urllib.parse
import html
import re
import logging
import io

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('md_reader.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        return s.getsockname()[1]

def read_file(file_path):
    try:
        return Path(file_path).read_text(encoding='utf-8')
    except Exception as e:
        logger.error(f"Ошибка чтения файла {file_path}: {e}")
        return None

def get_file_path_from_args():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return None


def simple_markdown(text):
    """Простой markdown парсер"""
    if not text:
        return ''

    logger.info(f"Конвертируем markdown, длина: {len(text)} символов")

    lines = text.split('\n')
    result = []
    in_code = False

    for line in lines:
        if '```' in line:
            if in_code:
                in_code = False
                result.append('</code></pre>')
            else:
                in_code = True
                lang = line.replace('`', '').strip()
                result.append(f'<pre><code class="language-{lang}">')
            continue

        if in_code:
            result.append(line)
            continue

        # Заголовки
        if line.startswith('# '):
            result.append(f'<h1>{line[2:]}</h1>')
        elif line.startswith('## '):
            result.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('### '):
            result.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('#### '):
            result.append(f'<h4>{line[5:]}</h4>')
        elif line.startswith('##### '):
            result.append(f'<h5>{line[6:]}</h5>')
        elif line.startswith('###### '):
            result.append(f'<h6>{line[7:]}</h6>')
        elif line.startswith('&gt; ') or line.startswith('> '):
            result.append(f'<blockquote>{line[2:]}</blockquote>')
        elif line.strip() in ['---', '***', '___']:
            result.append('<hr>')
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            result.append(f'<li>{line[2:]}</li>')
        elif line.strip():
            result.append(f'<p>{line}</p>')
        else:
            result.append('')

    text = '\n'.join(result)

    # Форматирование
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'~~(.+?)~~', r'<del>\1</del>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'!\[([^\]]*)\]\(([^\)]+)\)', r'<img src="\2" alt="\1">', text)

    logger.info(f"Конвертация завершена, результат: {len(text)} символов")
    return text


# HTML Templates
VIEWER_TEMPLATE = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Markdown Viewer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #fff; color: #1a1a2e; height: 100vh; overflow: hidden; }
        .header { height: 56px; background: #fff; border-bottom: 1px solid #e5e7eb; display: flex; align-items: center; justify-content: space-between; padding: 0 24px; position: fixed; top: 0; left: 0; right: 0; z-index: 100; }
        .file-title { font-size: 16px; font-weight: 600; max-width: 400px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .modified-badge { background: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 500; }
        .btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border: none; border-radius: 6px; font-size: 13px; font-weight: 500; cursor: pointer; background: #4f46e5; color: white; }
        .btn:hover { background: #4338ca; }
        .btn-ghost { background: transparent; color: #6b7280; }
        .btn-ghost:hover { background: #f8f9fa; }
        .main { display: flex; height: calc(100vh - 56px); margin-top: 56px; }
        .sidebar { width: 260px; background: #f8f9fa; border-right: 1px solid #e5e7eb; overflow-y: auto; padding: 20px 0; display: none; }
        .sidebar.visible { display: block; }
        .sidebar-header { padding: 0 20px 16px; font-size: 11px; font-weight: 600; text-transform: uppercase; color: #6b7280; }
        .toc-list { list-style: none; }
        .toc-item { padding: 8px 20px; cursor: pointer; font-size: 13px; color: #6b7280; border-left: 2px solid transparent; }
        .toc-item:hover { background: rgba(79,70,229,0.05); }
        .toc-item.active { background: rgba(79,70,229,0.08); color: #4f46e5; border-left-color: #4f46e5; font-weight: 500; }
        .content { flex: 1; overflow-y: auto; padding: 40px 60px; max-width: 900px; margin: 0 auto; }
        .content h1 { font-size: 32px; font-weight: 700; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #e5e7eb; }
        .content h2 { font-size: 24px; font-weight: 600; margin: 32px 0 16px; padding-bottom: 8px; border-bottom: 1px solid #e5e7eb; }
        .content h3 { font-size: 20px; font-weight: 600; margin: 24px 0 12px; }
        .content p { line-height: 1.7; margin: 16px 0; color: #374151; }
        .content a { color: #4f46e5; text-decoration: none; }
        .content code { background: #f8f9fa; padding: 2px 6px; border-radius: 4px; font-family: monospace; }
        .content pre { background: #1f2937; color: #f3f4f6; padding: 16px; border-radius: 8px; overflow-x: auto; margin: 16px 0; }
        .content pre code { background: none; color: inherit; }
        .content blockquote { border-left: 4px solid #4f46e5; margin: 16px 0; padding: 12px 20px; background: #f8f9fa; color: #6b7280; }
        .content ul { margin: 16px 0; padding-left: 24px; }
        .content li { margin: 8px 0; }
    </style>
</head>
<body>
    <header class="header">
        <div style="display:flex;align-items:center;gap:12px">
            <span class="file-title">{{ title }}</span>
            {{ modified_badge }}
        </div>
        <div style="display:flex;gap:8px">
            <button class="btn btn-ghost" id="toggleToc">☰</button>
            <button class="btn" id="editBtn">✏️ Редактировать</button>
        </div>
    </header>
    <main class="main">
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">Оглавление</div>
            <ul class="toc-list" id="tocList"></ul>
        </aside>
        <div class="content" id="content">{{ content }}</div>
    </main>
    <script>
        console.log('Viewer loaded');
        const content = document.getElementById('content');
        const tocList = document.getElementById('tocList');
        const sidebar = document.getElementById('sidebar');
        const filePath = '{{ file_path }}';

        function buildToc() {
            console.log('Building TOC');
            const headers = content.querySelectorAll('h1, h2, h3, h4');
            headers.forEach((h, i) => {
                h.id = 'h' + i;
                const li = document.createElement('li');
                li.className = 'toc-item';
                li.textContent = h.textContent;
                li.onclick = () => document.getElementById(h.id).scrollIntoView({behavior:'smooth'});
                tocList.appendChild(li);
            });
            console.log('TOC built, headers:', headers.length);
        }

        document.getElementById('toggleToc').onclick = () => sidebar.classList.toggle('visible');
        document.getElementById('editBtn').onclick = () => window.location.href = '/edit?file=' + encodeURIComponent(filePath);
        buildToc();
    </script>
</body>
</html>'''

EDITOR_TEMPLATE = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Markdown Editor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: #fff; height: 100vh; overflow: hidden; }
        .header { height: 56px; background: #fff; border-bottom: 1px solid #e5e7eb; display: flex; align-items: center; justify-content: space-between; padding: 0 24px; }
        .file-title { font-size: 14px; font-weight: 500; }
        .unsaved-dot { width: 8px; height: 8px; background: #ef4444; border-radius: 50%; display: none; }
        .unsaved-dot.visible { display: block; }
        .btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border: none; border-radius: 6px; font-size: 13px; font-weight: 500; cursor: pointer; }
        .btn-primary { background: #4f46e5; color: white; }
        .btn-success { background: #10b981; color: white; }
        .btn-ghost { background: transparent; color: #6b7280; }
        .main { display: flex; height: calc(100vh - 56px); }
        .editor-pane { flex: 1; display: flex; flex-direction: column; background: #1e1e1e; }
        .editor { flex: 1; width: 100%; padding: 20px; background: #1e1e1e; color: #d4d4d4; border: none; font-family: 'Consolas', monospace; font-size: 14px; line-height: 1.6; resize: none; outline: none; }
        .preview-pane { flex: 1; border-left: 1px solid #e5e7eb; overflow-y: auto; padding: 30px 40px; }
        .preview-pane h1 { font-size: 28px; font-weight: 700; margin-bottom: 16px; padding-bottom: 10px; border-bottom: 1px solid #e5e7eb; }
        .preview-pane h2 { font-size: 22px; font-weight: 600; margin: 28px 0 14px; }
        .preview-pane p { line-height: 1.7; margin: 14px 0; color: #374151; }
    </style>
</head>
<body>
    <header class="header">
        <div style="display:flex;align-items:center;gap:12px">
            <span class="file-title">{{ title }}</span>
            <span class="unsaved-dot" id="unsavedDot"></span>
        </div>
        <div style="display:flex;gap:8px">
            <button class="btn btn-ghost" id="newBtn">➕ Новый</button>
            <button class="btn btn-success" id="saveBtn">💾 Сохранить</button>
            <button class="btn btn-ghost" id="viewBtn">👁 Просмотр</button>
        </div>
    </header>
    <input type="file" id="fileInput" accept=".md,.txt" style="display:none">
    <main class="main">
        <div class="editor-pane">
            <textarea class="editor" id="editor">{{ content }}</textarea>
        </div>
        <div class="preview-pane" id="preview"></div>
    </main>
    <script>
        console.log('Editor loaded');
        const editor = document.getElementById('editor');
        const preview = document.getElementById('preview');
        const filePath = '{{ file_path }}';
        let originalContent = '{{ content }}';

        function render() {
            let text = editor.value;
            // Простой рендеринг
            text = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            text = text.replace(/^# (.+)$/gm, '<h1>$1</h1>');
            text = text.replace(/^## (.+)$/gm, '<h2>$1</h2>');
            text = text.replace(/^### (.+)$/gm, '<h3>$1</h3>');
            text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
            text = text.replace(/\*(.+?)\*/g, '<em>$1</em>');
            text = text.replace(/`(.+?)`/g, '<code>$1</code>');
            text = text.replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2">$1</a>');
            text = text.replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>');
            text = text.replace(/^- (.+)$/gm, '<li>$1</li>');
            text = text.replace(/(<li>.*?<\\/li>\\n?)+/g, '<ul>$&</ul>');
            text = text.replace(/^(?!<[hupl])(.+)$/gm, '<p>$1</p>');
            text = text.replace(/<p>\\s*<\\/p>/g, '');
            preview.innerHTML = text;
            document.getElementById('unsavedDot').classList.toggle('visible', editor.value !== originalContent);
        }

        editor.oninput = () => { render(); };
        render();

        document.getElementById('saveBtn').onclick = () => {
            if (!filePath) { alert('Нельзя сохранить'); return; }
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/save');
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.onload = () => {
                if (xhr.status === 200) {
                    originalContent = editor.value;
                    render();
                    alert('Сохранено!');
                } else alert('Ошибка');
            };
            xhr.send(JSON.stringify({path: filePath, content: editor.value}));
        };

        document.getElementById('viewBtn').onclick = () => {
            if (editor.value !== originalContent && !confirm('Есть изменения. Перейти?')) return;
            window.location.href = '/view?file=' + encodeURIComponent(filePath) + '&modified=1';
        };

        document.getElementById('newBtn').onclick = () => {
            if (editor.value !== originalContent && !confirm('Есть изменения. Создать новый?')) return;
            window.location.href = '/edit';
        };

        document.getElementById('openBtn').onclick = () => document.getElementById('fileInput').click();
    </script>
</body>
</html>'''

INDEX_TEMPLATE = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown Reader</title>
    <style>
        body { font-family: -apple-system, sans-serif; background: #fff; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px; }
        h1 { font-size: 32px; margin-bottom: 8px; }
        .subtitle { color: #6b7280; margin-bottom: 32px; }
        .card { background: #f8f9fa; border: 1px solid #e5e7eb; border-radius: 12px; padding: 32px; text-align: center; max-width: 400px; width: 100%; }
        .card-header { font-size: 13px; font-weight: 600; color: #6b7280; text-transform: uppercase; margin-bottom: 16px; }
        .drop-zone { border: 2px dashed #e5e7eb; border-radius: 8px; padding: 32px; margin-bottom: 16px; cursor: pointer; transition: 0.2s; }
        .drop-zone:hover { border-color: #4f46e5; background: rgba(79,70,229,0.05); }
        .btn { display: inline-block; padding: 12px 24px; background: #4f46e5; color: white; border-radius: 8px; text-decoration: none; font-weight: 500; }
        .btn:hover { background: #4338ca; }
    </style>
</head>
<body>
    <h1>📄 Markdown Reader</h1>
    <p class="subtitle">Просмотр и редактирование Markdown</p>
    <div class="card">
        <div class="card-header">Выберите файл</div>
        <div class="drop-zone" id="dropZone">
            <p>📁 Перетащите .md файл сюда</p>
        </div>
        <input type="file" id="fileInput" accept=".md,.txt" style="display:none">
        <a href="/edit" class="btn">➕ Новый файл</a>
    </div>
    <script>
        console.log('Index loaded');
        const dz = document.getElementById('dropZone');
        const fi = document.getElementById('fileInput');

        dz.onclick = () => fi.click();
        fi.onchange = (e) => {
            const f = e.target.files[0];
            if (f) {
                const r = new FileReader();
                r.onload = (ev) => { sessionStorage.setItem('temp_md', ev.target.result); window.location.href = '/view?temp=1'; };
                r.readAsText(f);
            }
        };

        dz.ondragover = (e) => { e.preventDefault(); dz.style.borderColor = '#4f46e5'; };
        dz.ondragleave = (e) => { e.preventDefault(); dz.style.borderColor = '#e5e7eb'; };
        dz.ondrop = (e) => {
            e.preventDefault();
            dz.style.borderColor = '#e5e7eb';
            const f = e.dataTransfer.files[0];
            if (f && (f.name.endsWith('.md') || f.name.endsWith('.txt'))) {
                fi.files = e.dataTransfer.files;
                fi.dispatchEvent(new Event('change'));
            }
        };
    </script>
</body>
</html>'''


class MarkdownHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)

    def do_GET(self):
        logger.info(f"GET request: {self.path}")
        if self.path == '/' or self.path == '/index.html':
            self.send_html(INDEX_TEMPLATE)
        elif self.path.startswith('/view'):
            self.handle_view()
        elif self.path.startswith('/edit'):
            self.handle_edit()
        else:
            logger.warning(f"404: {self.path}")
            super().do_GET()

    def do_POST(self):
        logger.info(f"POST request: {self.path}")
        if self.path == '/api/save':
            self.handle_save()
        else:
            self.send_error(404)

    def handle_view(self):
        logger.info("handle_view called")
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        logger.info(f"Params: {params}")

        if params.get('temp') == ['1']:
            content = ''
            title = 'Без названия'
            file_path = ''
            logger.info("Using temp content")
        else:
            file_path = params.get('file', [''])[0]
            if not file_path:
                logger.warning("No file path provided")
                return self.send_error(400)
            content = read_file(file_path)
            if content is None:
                logger.error(f"File not found: {file_path}")
                return self.send_error(404)
            title = Path(file_path).name
            logger.info(f"Loaded file: {file_path}, size: {len(content)}")

        modified = params.get('modified') == ['1']
        modified_badge = '<span class="modified-badge">Изменено</span>' if modified else ''

        # Конвертируем markdown
        html_content = simple_markdown(content)
        logger.info(f"HTML content generated, length: {len(html_content)}")

        html = VIEWER_TEMPLATE
        html = html.replace('{{ title }}', title)
        html = html.replace('{{ content }}', html_content)
        html = html.replace('{{ file_path }}', file_path.replace('\\', '/'))
        html = html.replace('{{ modified_badge }}', modified_badge)

        logger.info("Sending HTML response")
        self.send_html(html)

    def handle_edit(self):
        logger.info("handle_edit called")
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        file_path = params.get('file', [''])[0]
        content = ''

        if file_path:
            content = read_file(file_path) or ''

        title = Path(file_path).name if file_path else 'Новый файл'
        logger.info(f"Edit mode, file: {file_path}")

        html = EDITOR_TEMPLATE
        html = html.replace('{{ title }}', title)
        html = html.replace('{{ content }}', content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
        html = html.replace('{{ file_path }}', file_path)

        self.send_html(html)

    def handle_save(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        params = urllib.parse.parse_qs(body)

        file_path = params.get('path', [''])[0]
        content = params.get('content', [''])[0]

        logger.info(f"Save request: {file_path}")

        if not file_path:
            self.send_json({'success': False, 'error': 'Путь не указан'})
            return

        try:
            Path(file_path).write_text(content, encoding='utf-8')
            logger.info(f"File saved: {file_path}")
            self.send_json({'success': True})
        except Exception as e:
            logger.error(f"Save error: {e}")
            self.send_json({'success': False, 'error': str(e)})

    def send_html(self, html):
        logger.info(f"Sending HTML, length: {len(html)}")
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(html.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def send_json(self, data):
        import json
        text = json.dumps(data)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(text.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(text.encode('utf-8'))

    def log_message(self, format, *args):
        logger.info(format % args)


def open_browser(url):
    logger.info(f"Opening browser: {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        logger.error(f"Browser open error: {e}")


def main():
    print("=" * 50)
    print("    MARKDOWN READER")
    print("=" * 50)

    port = find_free_port()
    file_path = get_file_path_from_args()

    if file_path:
        file_path = str(Path(file_path).resolve())
        if not Path(file_path).exists():
            logger.error(f"Файл не найден: {file_path}")
            print(f"Файл не найден: {file_path}")
            input("Нажмите Enter...")
            return

        mode = sys.argv[2] if len(sys.argv) > 2 else 'view'

        if mode == 'edit':
            url = f"http://127.0.0.1:{port}/edit?file={urllib.parse.quote(file_path)}"
        else:
            url = f"http://127.0.0.1:{port}/view?file={urllib.parse.quote(file_path)}"

        print(f"Файл: {file_path}")
        print(f"Режим: {mode}")
        print(f"URL: {url}")
    else:
        url = f"http://127.0.0.1:{port}"
        print(f"URL: {url}")
        print("Перетащите .md файл или нажмите 'Новый файл'")

    print("=" * 50)
    logger.info(f"Server starting on port {port}")

    threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    try:
        HTTPServer(('127.0.0.1', port), MarkdownHandler).serve_forever()
    except KeyboardInterrupt:
        print("\nОстановка...")


if __name__ == '__main__':
    main()
