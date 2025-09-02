# Автоматизированный просмотр Markdown-документации на Python

Ниже — минимальная, но расширяемая обёртка-CLI для чтения .md-файлов. 
Она превращает набор Markdown-документов в интерактивный «браузер» со структурой оглавления, 
поиском по заголовкам и быстрыми переходами.

## 1. Краткий обзор возможностей

* Чтение одиночного файла или целой папки с Markdown.
* Автоматическое построение оглавления (TOC) по заголовкам # H1 – #### H4.
* Быстрый интерактивный поиск (fuzzy-find) по заголовкам/подзаголовкам.
* Просмотр выбранной секции в консоли с окраской Markdown (через rich).
* Кеширование оглавления, чтобы не парсить заново при повторных запусках.
* Расширяемое API: легко прикрутить вывод в Telegram-бота или TUI.

## 2. Структура проекта
``` text
md_reader/
├── __init__.py
├── cli.py          # точка входа
├── loader.py       # чтение/кеширование файлов
├── toc.py          # построение оглавления
└── viewer.py       # вывод и навигация
```

## 3. Минимальные зависимости
``` bash
pip install rich typer markdown-it-py python-Levenshtein
```

```rich
 – цветной вывод и панели в терминале.

typer – создание CLI c автодокументацией.

markdown-it-py – быстрый парсер Markdown в AST.

python-Levenshtein – ускоренный fuzzy-поиск (использует rapidfuzz-like алгоритм).
```

## 4. Ключевые фрагменты кода
### 4.1 cli.py
```python
# md_reader/cli.py
import typer
from pathlib import Path
from .loader import load_markdown_files
from .toc import build_toc
from .viewer import interactive_view

app = typer.Typer(help="Interactive Markdown documentation viewer")

@app.command()
def open(path: str = typer.Argument(..., help="File or directory with .md docs")):
    """Open Markdown file/folder in interactive mode."""
    base = Path(path).expanduser().resolve()
    files = load_markdown_files(base)
    toc = build_toc(files)
    interactive_view(toc)

if __name__ == "__main__":
    app()
```

### 4.2 loader.py

```python
# md_reader/loader.py
from pathlib import Path
from typing import Dict, List

def load_markdown_files(base: Path) -> Dict[Path, List[str]]:
    """Return {file_path: list_of_lines} for all .md files under base."""
    if base.is_file() and base.suffix == ".md":
        targets = [base]
    else:
        targets = base.rglob("*.md")
    return {f: f.read_text(encoding="utf-8").splitlines() for f in targets}
```
### 4.3 toc.py

```python
# md_reader/toc.py
from typing import Dict, List, Tuple
from pathlib import Path
from markdown_it import MarkdownIt

Heading = Tuple[str, int, int]  # (title, level, line_no)

def build_toc(files: Dict[Path, List[str]]) -> Dict[Path, List[Heading]]:
    md = MarkdownIt()
    toc = {}
    for path, lines in files.items():
        tokens = md.parse("\n".join(lines))
        heads = []
        for tok in tokens:
            if tok.type == "heading_open":
                level = int(tok.tag[1])
                title = tokens[tokens.index(tok)+1].content
                heads.append((title, level, tok.map[0]))
        toc[path] = heads
    return toc
```    

### 4.4 viewer.py
```python
# md_reader/viewer.py
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rapidfuzz import process
from pathlib import Path
from typing import Dict, List, Tuple

console = Console()
Heading = Tuple[str, int, int]

def interactive_view(toc: Dict[Path, List[Heading]]):
    all_heads = [
        (f"{path.name} > {'  '*lvl}{title}", (path, line))
        for path, heads in toc.items()
        for title, lvl, line in heads
    ]
    while True:
        query = console.input("[bold cyan]Search (or 'q' to quit):[/] ")
        if query.lower() == 'q':
            break
        matches = process.extract(query, [h[0] for h in all_heads], limit=10)
        for idx, (title, score, pos) in enumerate(matches, 1):
            console.print(f"{idx}. {title} ({score:.0f}%)")
        sel = console.input("Choose number ▶ ")
        if sel.isdigit():
            path, line_no = all_heads[matches[int(sel)-1][2]][1]
            show_section(path, line_no)

def show_section(path: Path, start: int, context: int = 20):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    snippet = "\n".join(lines[start:start+context])
    console.print(Panel(f"[bold]{path.name}[/bold]\n{Syntax(snippet, 'markdown')}"))
```

### 5. Расширение под ваши задачи
#### Что добавить	Как внедрить

* Кэш TOC в SQLite	Сериализовать toc в таблицу (path, title, level, line) с sqlite3 или sqlmodel; при повторных запусках проверять mtime.
* Просмотр в Telegram-боте	Завернуть interactive_view в handlers: запрос → fuzzy-поиск → выдача секции в сообщение/InlineKeyboard.
* Поддержка кода с подсветкой	rich уже умеет; просто оставить блоки ```python в Markdown, Syntax распознает язык.
* Превью изображений	При парсинге искать ![](path); локальные картинки можно открывать через Pillow и показывать в терминале (rich.img).

6. Запуск

```text
# установка в editable-режиме
pip install -e .

# просмотр одного файла
md-viewer open README.md

# просмотр всей docs/ папки
md-viewer open docs/

## Итог
Получилась лёгкая CLI-обёртка, которую можно встроить в ваш стек (Docker-контейнер, n8n-флоу или Telegram-бот). При желании она расширяется до полноценных docs-порталов или интегрируется с вашей e-commerce системой для внутренних гайдлайнов.