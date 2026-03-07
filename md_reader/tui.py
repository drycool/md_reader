from pathlib import Path
from typing import Dict, List

from textual.app import App, ComposeResult
from textual.widgets import Tree, Header, Footer, Static
from textual.scroll_view import ScrollView
from textual.containers import Horizontal

from rich.syntax import Syntax

from md_reader.loader import load_markdown_files
from md_reader.toc import build_toc


class MarkdownPane(ScrollView):
    def compose(self) -> ComposeResult:
        yield Static("")

    def update_source(self, path: Path, start: int, end: int):
        code = "\n".join(path.read_text(encoding="utf-8").splitlines()[start:end])
        content = self.query_one(Static)
        content.update(Syntax(code, "markdown", line_numbers=True, word_wrap=True))
        self.refresh()


class DocBrowser(App):
    CSS_PATH = "styles.css"  # Подключаем CSS
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Reload TOC"),
        ("f1", "open_editor", "Open Editor"),  # Горячая клавиша F1
    ]

    def action_open_editor(self) -> None:
        """Открывает редактор."""
        self.notify("Editor opened!", title="Info")

    def __init__(self, path: str):
        super().__init__()
        self.base = Path(path)
        self.files = {}
        self.toc = {}

        # Проверяем: это файл или директория?
        if self.base.is_file():
            # Это один .md файл
            if self.base.suffix == ".md":
                content = self.base.read_text(encoding="utf-8")
                self.files[self.base] = content.splitlines()
                self.toc = build_toc(self.files)
            else:
                raise ValueError(f"Not a markdown file: {self.base}")
        else:
            # Это директория — ищем все .md файлы
            self.files = load_markdown_files(self.base)
            self.toc = build_toc(self.files)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("🚀", id="icon")  # Добавляем иконку через Unicode
        self.tree_widget = Tree("Documentation", id="toc")
        self.tree_widget.auto_expand = False
        self.viewer_widget = MarkdownPane()

        with Horizontal():
            yield self.tree_widget
            yield self.viewer_widget

        yield Footer()

    def on_mount(self) -> None:
        self.tree_widget.focus()
        self._build_tree()

    # ---------- events ----------
    def action_refresh(self) -> None:
        self.files = load_markdown_files(self.base)
        self.toc = build_toc(self.files)
        self.tree_widget.root.remove_children()
        self._build_tree()

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        self.log(f"Node selected: {event.node.label}, data: {event.node.data}")
        if event.node.data:
            path, start, end = event.node.data
            self.log(f"Loading from {start} to {end}")
            self.viewer_widget.update_source(path, start, end)

    # Убираем on_tree_node_expanded, так как TreeNode не поддерживает animate()

    # ---------- helpers ----------
    def _build_tree(self) -> None:
        root = self.tree_widget.root
        root.remove_children()
        for path, heads in self.toc.items():
            file_node = root.add(path.name, expand=False)
            for idx, (title, lvl, line) in enumerate(heads):
                end = heads[idx + 1][2] if idx + 1 < len(heads) else line + 30
                file_node.add(f"{'  ' * (lvl - 1)}{title}", data=(path, line, end))
            if heads:
                file_node.expand()
        root.expand()


# --- точка входа --------------------------------------------------------
def run(path: Path = Path(".")):
    DocBrowser(str(path)).run()


if __name__ == "__main__":
    import sys
    run(sys.argv[1] if len(sys.argv) > 1 else ".")