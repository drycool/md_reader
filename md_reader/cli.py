# md_reader/cli.py
import typer
from pathlib import Path

from .loader import load_markdown_files
from .toc    import build_toc
from .viewer import interactive_view

app = typer.Typer(add_completion=False)

# ───────── команда «tui» ─────────
@app.command()                       # ← без name=, функция-имя станет именем команды
def tui(
    path: Path = typer.Argument(".", help="Файл или каталог с .md-доками")
):
    """Запуск TUI-браузера (Textual)."""
    from .tui import run            # импорт внутри, чтобы не тянуть Textual, если не надо
    run(path)

# ───────── команда «open» (CLI-режим) ─────────
@app.command()
def open(
    path: Path = typer.Argument(".", help="Файл или каталог с .md-доками")
):
    """Интерактивный поиск/просмотр в терминале (старый режим)."""
    files = load_markdown_files(path)
    toc   = build_toc(files)
    interactive_view(toc)

if __name__ == "__main__":
    app()
