#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Веб-редактор и просмотрщик Markdown
"""

import sys
import threading
import time
import webbrowser
import logging
import uuid
from pathlib import Path
from urllib.parse import quote

# Настройка логирования
import tempfile

# Определяем папку для логов
if getattr(sys, 'frozen', False):
    # Для EXE используем %TEMP%
    log_dir = Path(tempfile.gettempdir()) / 'md_reader_logs'
else:
    # Для разработки - папка приложения
    log_dir = Path(__file__).parent

log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / 'app_debug.log'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(log_file), encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

from flask import Flask, render_template, request, jsonify, session

# Определяем корень проекта и путь к шаблонам
def get_base_path():
    """Определение базового пути (для EXE и разработки)"""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent

def get_template_folder():
    """Определение папки с шаблонами"""
    return get_base_path() / 'templates'

def get_static_folder():
    """Определение папки со статикой"""
    return get_base_path() / 'static'

# Для temp_cache используем рабочую директорию (доступна для записи)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
WORKING_DIR = Path(__file__).parent
TEMPLATE_FOLDER = get_template_folder()
STATIC_FOLDER = get_static_folder()

# Папка для временного хранения контента (вместо сессий)
# Для EXE используем tempfile, для разработки - локальную папку
if getattr(sys, 'frozen', False):
    import tempfile
    TEMP_CACHE_DIR = Path(tempfile.gettempdir()) / 'md_reader_temp'
else:
    TEMP_CACHE_DIR = WORKING_DIR / 'temp_cache'
TEMP_CACHE_DIR.mkdir(parents=True, exist_ok=True)

logger.info(f"TEMPLATE_FOLDER: {TEMPLATE_FOLDER}")
logger.info(f"STATIC_FOLDER: {STATIC_FOLDER}")
logger.info(f"STATIC_FOLDER exists: {STATIC_FOLDER.exists() if STATIC_FOLDER else 'None'}")
logger.info(f"TEMP_CACHE_DIR: {TEMP_CACHE_DIR}")

app = Flask(__name__,
    template_folder=str(TEMPLATE_FOLDER),
    static_folder=str(STATIC_FOLDER),
    static_url_path='/static')
app.config['SECRET_KEY'] = 'md-reader-secret-key'


def resolve_file_path(file_path):
    """Разрешение пути к файлу - поддержка абсолютных и относительных путей"""
    if not file_path:
        return None
    path = Path(file_path)
    # Если абсолютный и существует - ок
    if path.is_absolute() and path.exists():
        return str(path)
    # Пробуем относительно корня проекта
    full_path = PROJECT_ROOT / path
    if full_path.exists():
        return str(full_path)
    # Пробуем относительно текущей директории
    if path.exists():
        return str(path.resolve())
    return None


@app.errorhandler(404)
def handle_404(error):
    """Обработчик 404 ошибок - для отладки статических файлов"""
    logger.warning(f"[404] Path not found: {request.path}")
    logger.warning(f"[404] Request URL: {request.url}")
    logger.warning(f"[404] Static folder: {app.static_folder}")
    logger.warning(f"[404] Static exists: {app.static_folder is not None and Path(app.static_folder).exists()}")
    return f"Resource not found: {request.path}", 404


@app.route('/static/<path:filename>')
def debug_static(filename):
    """Отладочный маршрут для статических файлов"""
    logger.debug(f"[STATIC] Requested: {filename}")
    full_path = Path(app.static_folder) / filename
    logger.debug(f"[STATIC] Full path: {full_path}")
    logger.debug(f"[STATIC] Exists: {full_path.exists()}")
    if not full_path.exists():
        logger.warning(f"[STATIC] File not found: {full_path}")
        return f"Static file not found: {filename}", 404
    return app.send_static_file(filename)


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


def get_temp_content():
    """Чтение контента из временного файла по ID из сессии"""
    temp_id = session.get('temp_content_id')
    if not temp_id:
        return None, None

    temp_file = TEMP_CACHE_DIR / f"{temp_id}.md"

    if not temp_file.exists():
        logger.warning(f"[TEMP] Temp file not found: {temp_file}")
        return None, None

    try:
        content = temp_file.read_text(encoding='utf-8')
        name = session.get('temp_content_name', 'Без названия')
        logger.debug(f"[TEMP] Loaded from {temp_file.name}, length: {len(content)}")
        return content, name
    except Exception as e:
        logger.error(f"[TEMP] Failed to read temp file: {e}")
        return None, None


def save_temp_content(content, file_name=''):
    """Сохранение контента во временный файл (для EXE запуска с файлом)"""
    import uuid
    temp_id = str(uuid.uuid4())
    temp_file = TEMP_CACHE_DIR / f"{temp_id}.md"

    try:
        temp_file.write_text(content, encoding='utf-8')
        logger.info(f"[TEMP] Saved content to {temp_file.name}, length: {len(content)}")
        return temp_id, file_name or 'Без названия'
    except Exception as e:
        logger.error(f"[TEMP] Failed to save temp file: {e}")
        return None, None


def save_temp_content(content, file_name=''):
    """Сохранение контента в temp_cache (для EXE)"""
    import uuid
    temp_id = str(uuid.uuid4())
    temp_file = TEMP_CACHE_DIR / f"{temp_id}.md"

    try:
        temp_file.write_text(content, encoding='utf-8')
        logger.info(f"[TEMP] Saved content to {temp_file.name}, length: {len(content)}")
        return temp_id, file_name or 'Без названия'
    except Exception as e:
        logger.error(f"[TEMP] Failed to save temp file: {e}")
        return None, None


def clear_temp_cache():
    """Очистка папки temp_cache от старых файлов"""
    if not TEMP_CACHE_DIR.exists():
        return

    import time as time_module
    now = time_module.time()
    # Удаляем файлы старше 1 часа
    for f in TEMP_CACHE_DIR.glob("*.md"):
        try:
            age = now - f.stat().st_mtime
            if age > 3600:  # 1 час
                f.unlink()
                logger.info(f"[TEMP] Deleted old temp file: {f.name}")
        except Exception as e:
            logger.warning(f"[TEMP] Failed to delete {f.name}: {e}")


def find_free_port():
    """Поиск свободного порта"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        return s.getsockname()[1]


@app.route('/')
def index():
    """Главная страница - выбор файла"""
    # Очистка устаревших ключей сессии
    session.pop('temp_content_id', None)
    session.pop('temp_content_name', None)
    session.pop('temp_md_content', None)
    session.pop('temp_md_file_path', None)
    session.pop('temp_md_name', None)
    return render_template('index.html')


@app.route('/view')
def view_file():
    """Просмотр файла"""
    session_id = session.sid if hasattr(session, 'sid') else 'unknown'
    logger.debug(f"[VIEW] Request received. Session ID: {session_id}")
    logger.debug(f"[VIEW] Request args: {dict(request.args)}")

    # Временный файл (drag&drop) или запуск из EXE с файлом
    if request.args.get('temp') == '1':
        # Проверяем: сначала session, потом URL параметр (для EXE)
        content, title = get_temp_content()

        # Если не найдено в сессии, пробуем получить по temp_id из URL
        if not content and request.args.get('temp_id'):
            temp_id = request.args.get('temp_id')
            temp_file = TEMP_CACHE_DIR / f"{temp_id}.md"
            if temp_file.exists():
                try:
                    content = temp_file.read_text(encoding='utf-8')
                    title = request.args.get('name', 'Без названия')
                    logger.info(f"[VIEW] Loaded from temp_id={temp_id}, length: {len(content)}")
                except Exception as e:
                    logger.error(f"[VIEW] Failed to load from temp_id: {e}")

        title = title or 'Без названия'

        logger.debug(f"[VIEW] Temp mode - loaded content length: {len(content) if content else 0}")
        logger.debug(f"[VIEW] Session keys: {list(session.keys())}")

        # Проверка на пустой контент
        if not content:
            logger.warning(f"[VIEW] Empty content from temp_cache! Session ID: {session_id}")
            return render_template('viewer.html',
                title='Ошибка',
                content='<div class="error-message"><p>Файл не выбран или пуст</p></div>',
                raw_content='',
                file_path='',
                modified=False)

        import markdown
        html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
        logger.info(f"[VIEW] Rendered temp file, content length: {len(html_content)}")
        return render_template('viewer.html',
            title=title,
            content=html_content,
            raw_content=content,
            file_path='',
            modified=False)

    file_path = request.args.get('file', '')
    logger.debug(f"[VIEW] Raw file_path from request: '{file_path}'")

    resolved_path = resolve_file_path(file_path) if file_path else ''
    logger.debug(f"[VIEW] Resolved file_path: '{resolved_path}'")

    modified = request.args.get('modified') == '1'

    if not resolved_path:
        logger.warning(f"[VIEW] File path not resolved! Original: '{file_path}'")
        return "Файл не указан", 400

    content = read_file_content(resolved_path)
    logger.debug(f"[VIEW] File read result: {'SUCCESS' if content is not None else 'FAILED'}")
    logger.debug(f"[VIEW] Content length: {len(content) if content else 0}")

    if content is None:
        logger.error(f"[VIEW] File not found on disk: '{resolved_path}'")
        return "Файл не найден", 404

    import markdown
    html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])

    logger.info(f"[VIEW] Rendering viewer. title='{Path(resolved_path).name}', content_len={len(html_content)}, raw_len={len(content)}")

    return render_template('viewer.html',
        title=Path(resolved_path).name,
        content=html_content,
        raw_content=content,
        file_path=resolved_path,
        modified=modified)


@app.route('/edit')
def edit_file():
    """Редактирование файла"""
    session_id = session.sid if hasattr(session, 'sid') else 'unknown'
    logger.debug(f"[EDIT] Request received. Session ID: {session_id}")
    logger.debug(f"[EDIT] Request args: {dict(request.args)}")
    logger.debug(f"[EDIT] Session keys: {list(session.keys())}")

    file_path = request.args.get('file', '')
    logger.debug(f"[EDIT] Raw file_path from request: '{file_path}'")

    resolved_path = resolve_file_path(file_path) if file_path else ''
    logger.debug(f"[EDIT] Resolved file_path: '{resolved_path}'")

    content = ""
    temp_name = ""

    if resolved_path:
        # Приоритет: 1) временный контент из temp_cache, 2) содержимое файла
        temp_content, temp_name = get_temp_content()

        if temp_content:
            content = temp_content
            logger.info(f"[EDIT] Using temp content from file, length: {len(content)}")
        else:
            content = read_file_content(resolved_path) or ""
            logger.info(f"[EDIT] Read from file, length: {len(content)}")
    else:
        # Без файла - используем временный контент
        temp_content, temp_name = get_temp_content()
        if temp_content:
            content = temp_content
            logger.info(f"[EDIT] Using temp content, length: {len(content)}")
        else:
            logger.debug(f"[EDIT] No temp content available")

    if not content:
        logger.warning(f"[EDIT] Empty content! Session ID: {session_id}, file_path: '{resolved_path}'")

    title = temp_name if temp_name else (Path(resolved_path).name if resolved_path else 'Новый файл')
    logger.info(f"[EDIT] Rendering editor. title='{title}', content_len={len(content)}")

    return render_template('editor.html',
        title=title,
        content=content,
        temp_content=content,  # Для совместимости с шаблоном
        file_path=resolved_path or '')


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


@app.route('/api/set-temp-content', methods=['POST'])
def set_temp_content():
    """Сохранение контента в файл (вместо сессии)"""
    session_id = session.sid if hasattr(session, 'sid') else 'unknown'
    data = request.json
    content = data.get('content', '')
    file_path = data.get('file_path', '')

    # Генерируем уникальный ID
    temp_id = str(uuid.uuid4())
    temp_file = TEMP_CACHE_DIR / f"{temp_id}.md"

    # Сохраняем контент в файл
    try:
        temp_file.write_text(content, encoding='utf-8')
        logger.info(f"[API] set-temp-content: temp_id={temp_id}, content_len={len(content)}, file_path='{file_path}'")
    except Exception as e:
        logger.error(f"[API] Failed to write temp file: {e}")
        return jsonify({'success': False, 'error': str(e)})

    # В сессии сохраняем только ID и имя файла
    session['temp_content_id'] = temp_id
    # Извлекаем только имя файла из полного пути
    file_name = Path(file_path).name if file_path else 'Без названия'
    session['temp_content_name'] = file_name
    session.modified = True

    logger.debug(f"[API] Session temp_content_id set: {temp_id}")

    return jsonify({'success': True, 'temp_id': temp_id})


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
    logger.info(f"Opening browser: {url}")
    time.sleep(delay)
    try:
        webbrowser.open(url)
    except Exception as e:
        logger.error(f"Browser open error: {e}")


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
    logger.info(f"Server starting on port {port}")

    browser_thread = threading.Thread(target=open_browser, args=(url,), daemon=True)
    browser_thread.start()

    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)


if __name__ == '__main__':
    logger.info("Starting MD Reader")

    # Очищаем старые temp файлы при запуске
    clear_temp_cache()

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        file_path = str(Path(file_path).resolve())

        if not Path(file_path).exists():
            logger.error(f"File not found: {file_path}")
            print(f"Файл не найден: {file_path}")
            sys.exit(1)

        mode = sys.argv[2] if len(sys.argv) > 2 else 'view'
        port = find_free_port()

        if mode == 'edit':
            url = f"http://127.0.0.1:{port}/edit?file={quote(file_path, safe='')}"
        else:
            url = f"http://127.0.0.1:{port}/view?file={quote(file_path, safe='')}"

        logger.info(f"Opening file: {file_path}, mode: {mode}")
        print(f"Запуск: {url}")
        print(f"Порт: {port}")

        browser_thread = threading.Thread(target=open_browser, args=(url,), daemon=True)
        browser_thread.start()

        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    else:
        run_server()
