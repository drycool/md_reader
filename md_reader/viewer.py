from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rapidfuzz import process
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from .exceptions import UserInputError, FileLoadError
from .validators import InputValidator, PathValidator
from .logger import get_logger, handle_exceptions, error_context

logger = get_logger("viewer")
console = Console()
Heading = Tuple[str, int, int]


class InteractiveViewer:
    """Интерактивный просмотрщик с безопасной обработкой ввода."""
    
    def __init__(self, max_search_results: int = 10, context_lines: int = 20):
        self.max_search_results = max_search_results
        self.context_lines = context_lines
        self.search_count = 0
    
    @handle_exceptions(UserInputError, reraise=False, default_return=None)
    def get_user_search_input(self) -> Optional[str]:
        """Безопасно получает поисковый запрос от пользователя."""
        try:
            query = console.input("[bold cyan]Search (or 'q' to quit):[/] ")
            return InputValidator.validate_search_query(query)
        except KeyboardInterrupt:
            logger.info("User interrupted search")
            return None
        except EOFError:
            logger.info("End of input reached")
            return None
    
    @handle_exceptions(UserInputError, reraise=False, default_return=None)
    def get_user_selection(self, max_options: int) -> Optional[int]:
        """Безопасно получает выбор пользователя."""
        try:
            selection = console.input("Choose number ▶ ")
            return InputValidator.validate_selection_input(selection, max_options)
        except KeyboardInterrupt:
            logger.info("User interrupted selection")
            return None
    
    @handle_exceptions(FileLoadError, reraise=False)
    def show_section(self, path: Path, start: int) -> None:
        """Безопасно отображает секцию файла."""
        try:
            validated_path = PathValidator.validate_file_path(path)
            lines = validated_path.read_text(encoding="utf-8").splitlines()
            
            end = min(start + self.context_lines, len(lines))
            snippet = "\n".join(lines[start:end])
            
            syntax = Syntax(snippet, "markdown", line_numbers=True, word_wrap=True)
            panel = Panel(syntax, title=str(path.name), border_style="cyan")
            console.print(panel)
            
        except Exception as e:
            logger.error(f"Error displaying section from {path}: {str(e)}")
            console.print(f"[red]Error: Could not display file {path.name}[/red]")
    
    def interactive_view(self, toc: Dict[Path, List[Heading]]) -> None:
        """Главный интерактивный цикл просмотра."""
        if not toc:
            console.print("[yellow]Warning: No table of contents available[/yellow]")
            return
        
        # Подготавливаем список всех заголовков
        all_heads = [
            (f"{path.name} > {'  ' * lvl}{title}", (path, line))
            for path, heads in toc.items()
            for title, lvl, line in heads
        ]
        
        if not all_heads:
            console.print("[yellow]Warning: No headers found in files[/yellow]")
            return
        
        logger.info(f"Starting interactive view with {len(all_heads)} headers")
        
        while True:
            try:
                query = self.get_user_search_input()
                if query is None or query.lower() == 'q':
                    break
                
                with error_context("performing search"):
                    matches = process.extract(
                        query, [h[0] for h in all_heads], 
                        limit=self.max_search_results
                    )
                    
                    if not matches:
                        console.print("[yellow]No matches found[/yellow]")
                        continue
                    
                    for idx, (title, score, pos) in enumerate(matches, 1):
                        console.print(f"{idx}. {title} ({score:.0f}%)")
                    
                    selection = self.get_user_selection(len(matches))
                    if selection is None:
                        continue
                    
                    path, line_no = all_heads[matches[selection - 1][2]][1]
                    self.show_section(path, line_no)
                    self.search_count += 1
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Exiting...[/yellow]")
                break
            except Exception as e:
                logger.error(f"Unexpected error in interactive view: {str(e)}")
                console.print("[red]An error occurred. Please try again.[/red]")
        
        logger.info(f"Interactive session ended. Searches performed: {self.search_count}")


# Функция обратной совместимости
def interactive_view(toc: Dict[Path, List[Heading]]) -> None:
    """Функция обратной совместимости для интерактивного просмотра."""
    viewer = InteractiveViewer()
    viewer.interactive_view(toc)


def show_section(path: Path, start: int, context: int = 20) -> None:
    """Функция обратной совместимости для отображения секции."""
    viewer = InteractiveViewer(context_lines=context)
    viewer.show_section(path, start)
