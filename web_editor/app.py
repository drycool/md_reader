#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Веб-редактор и просмотрщик Markdown
"""

import os
import sys
import threading
import time
import webbrowser
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'md-reader-secret-key'

WORKING_DIR = Path(__file__).parent


def find_free_port():
    """Поиск свободного порта"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        return s.getsockname()[1]


def read_file_content(file_path):
    """Чтение содержимого файла"""
    try:
        path = Path(file_path)
        if path.exists():
            return path.read_text(encoding='utf-8')
    except Exception:
        return None
    return None


@app.route('/')
def index():
    """Главная страница - выбор файла"""
    return render_template('index.html')


@app.route('/view')
def view_file():
    """Просмотр файла"""
    # Временный файл (drag&drop)
    if request.args.get('temp') == '1':
        content = session.get('temp_md_content', '')
        title = session.get('temp_md_name', 'Без названия')
        import markdown
        html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
        return render_template('viewer.html',
            title=title,
            content=html_content,
            file_path='',
            modified=False)

    file_path = request.args.get('file', '')
    modified = request.args.get('modified') == '1'

    if not file_path:
        return "Файл не указан", 400

    content = read_file_content(file_path)
    if content is None:
        return "Файл не найден", 404

    import markdown
    html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])

    return render_template('viewer.html',
        title=Path(file_path).name,
        content=html_content,
        file_path=file_path,
        modified=modified)


@app.route('/edit')
def edit_file():
    """Редактирование файла"""
    file_path = request.args.get('file', '')

    content = ""
    if file_path:
        content = read_file_content(file_path) or ""

    # Временный контент из sessionStorage
    temp_content = session.get('temp_md_content', '')
    if temp_content and not file_path:
        content = temp_content

    return render_template('editor.html',
        title=Path(file_path).name if file_path else 'Новый файл',
        content=content,
        file_path=file_path or '')


@app.route('/api/save', methods=['POST'])
def save_file():
    """Сохранение файла"""
    data = request.json
    file_path = data.get('path', '')
    content = data.get('content', '')

    if not file_path:
        return jsonify({'success': False, 'error': 'Путь не указан'})

    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/list-files')
def list_files():
    """Список .md файлов"""
    files = []
    search_dir = request.args.get('dir', '.')

    try:
        path = Path(search_dir)
        if path.is_dir():
            for f in path.rglob('*.md'):
                if f.is_file():
                    files.append(str(f.relative_to(path.parent)))
    except Exception:
        pass

    return jsonify(files)


def open_browser(url, delay=1):
    """Открытие браузера"""
    time.sleep(delay)
    webbrowser.open(url)


def run_server(port=None):
    """Запуск сервера"""
    if port is None:
        port = find_free_port()

    url = f"http://127.0.0.1:{port}"

    print("=" * 50)
    print("    MARKDOWN READER")
    print("    Просмотр и редактирование Markdown")
    print("=" * 50)
    print(f"Сервер: {url}")
    print("=" * 50)

    browser_thread = threading.Thread(target=open_browser, args=(url,), daemon=True)
    browser_thread.start()

    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        file_path = str(Path(file_path).resolve())

        if not Path(file_path).exists():
            print(f"Файл не найден: {file_path}")
            sys.exit(1)

        mode = sys.argv[2] if len(sys.argv) > 2 else 'view'
        port = find_free_port()

        if mode == 'edit':
            url = f"http://127.0.0.1:{port}/edit?file={file_path}"
        else:
            url = f"http://127.0.0.1:{port}/view?file={file_path}"

        print(f"Запуск: {url}")
        print(f"Порт: {port}")

        browser_thread = threading.Thread(target=open_browser, args=(url,), daemon=True)
        browser_thread.start()

        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    else:
        run_server()
