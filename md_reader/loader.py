from pathlib import Path
from typing import Dict, List, Optional, Union

from .exceptions import FileLoadError, PathValidationError
from .validators import PathValidator, FileContentValidator
from .logger import get_logger, handle_exceptions, error_context

logger = get_logger("loader")


class MarkdownLoader:
    """Безопасный загрузчик Markdown файлов с валидацией и обработкой ошибок."""
    
    def __init__(self, max_file_size: Optional[int] = None):
        """Инициализация загрузчика.
        
        Args:
            max_file_size: Максимальный размер файла в байтах
        """
        self.max_file_size = max_file_size or FileContentValidator.MAX_FILE_SIZE
        self.loaded_files_count = 0
        self.failed_files_count = 0
    
    @handle_exceptions((FileLoadError, PathValidationError), reraise=True)
    def load_single_file(self, file_path: Union[str, Path]) -> List[str]:
        """
        Загружает один Markdown файл с валидацией.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Список строк файла
            
        Raises:
            FileLoadError: При ошибках загрузки
            PathValidationError: При невалидном пути
        """
        # Валидация пути
        validated_path = PathValidator.validate_markdown_file(file_path)
        
        # Проверка размера файла
        FileContentValidator.validate_file_size(validated_path)
        
        # Определение кодировки
        encoding = FileContentValidator.validate_text_encoding(validated_path)
        
        try:
            with error_context(f"loading file {validated_path}"):
                content = validated_path.read_text(encoding=encoding)
                lines = content.splitlines()
                
                logger.info(
                    f"Successfully loaded {validated_path}: "
                    f"{len(content)} chars, {len(lines)} lines"
                )
                
                self.loaded_files_count += 1
                return lines
                
        except (OSError, UnicodeDecodeError) as e:
            self.failed_files_count += 1
            raise FileLoadError(
                str(validated_path),
                f"Failed to read file: {str(e)}"
            )
    
    @handle_exceptions((FileLoadError, PathValidationError), reraise=False, default_return={})
    def load_markdown_files(self, base: Union[str, Path]) -> Dict[Path, List[str]]:
        """
        Загружает все .md файлы из указанной директории и её поддиректорий.
        
        Args:
            base: Базовый путь (файл или директория)
            
        Returns:
            Словарь, где ключ — путь к файлу, значение — список строк файла
            
        Raises:
            PathValidationError: При невалидном базовом пути
        """
        files = {}
        self.loaded_files_count = 0
        self.failed_files_count = 0
        
        # Валидация базового пути
        base_path = PathValidator.validate_path(base, must_exist=True)
        
        logger.info(f"Starting to load Markdown files from: {base_path}")
        
        try:
            if base_path.is_file():
                # Если указан конкретный файл
                if PathValidator.is_markdown_file(base_path):
                    try:
                        lines = self.load_single_file(base_path)
                        files[base_path] = lines
                    except (FileLoadError, PathValidationError) as e:
                        logger.error(f"Failed to load file {base_path}: {e.message}")
                        self.failed_files_count += 1
                else:
                    raise PathValidationError(
                        str(base_path),
                        "Specified file is not a Markdown file"
                    )
            else:
                # Если указана директория, ищем все .md файлы
                validated_dir = PathValidator.validate_directory_path(base_path)
                
                markdown_files = list(validated_dir.rglob("*.md"))
                logger.info(f"Found {len(markdown_files)} potential Markdown files")
                
                for file_path in markdown_files:
                    try:
                        if file_path.is_file() and PathValidator.is_markdown_file(file_path):
                            lines = self.load_single_file(file_path)
                            files[file_path] = lines
                    except (FileLoadError, PathValidationError) as e:
                        logger.warning(f"Skipping file {file_path}: {e.message}")
                        self.failed_files_count += 1
                        continue
        
        except Exception as e:
            logger.error(f"Unexpected error during file loading: {str(e)}")
            raise
        
        logger.info(
            f"Loading completed: {self.loaded_files_count} files loaded, "
            f"{self.failed_files_count} files failed"
        )
        
        if not files:
            logger.warning("No Markdown files were successfully loaded")
        
        return files
    
    def get_stats(self) -> Dict[str, int]:
        """Возвращает статистику загрузки."""
        return {
            "loaded_files": self.loaded_files_count,
            "failed_files": self.failed_files_count
        }


# Функция обратной совместимости
def load_markdown_files(base: Path) -> Dict[Path, List[str]]:
    """
    Функция обратной совместимости для загрузки Markdown файлов.
    
    Args:
        base: Базовый путь
        
    Returns:
        Словарь с загруженными файлами
    """
    loader = MarkdownLoader()
    return loader.load_markdown_files(base)