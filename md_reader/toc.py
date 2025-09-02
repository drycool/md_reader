import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from .exceptions import TocBuildError, MarkdownParsingError
from .logger import get_logger, handle_exceptions, error_context

logger = get_logger("toc")


class TocBuilder:
    """Безопасный строитель оглавления с обработкой ошибок и валидацией."""
    
    # Паттерн для поиска заголовков Markdown
    HEADER_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$")
    
    def __init__(self, max_header_level: int = 6):
        """
        Инициализация строителя оглавления.
        
        Args:
            max_header_level: Максимальный уровень заголовков (1-6)
        """
        self.max_header_level = min(max(max_header_level, 1), 6)
        self.processed_files_count = 0
        self.total_headers_count = 0
    
    @handle_exceptions(MarkdownParsingError, reraise=True)
    def parse_headers_from_lines(self, lines: List[str], file_path: Optional[Path] = None) -> List[Tuple[str, int, int]]:
        """
        Извлекает заголовки из строк файла.
        
        Args:
            lines: Строки файла
            file_path: Путь к файлу (для логирования)
            
        Returns:
            Список кортежей (заголовок, уровень, номер_строки)
            
        Raises:
            MarkdownParsingError: При ошибках парсинга
        """
        headers = []
        file_name = str(file_path) if file_path else "<unknown>"
        
        if not isinstance(lines, list):
            raise MarkdownParsingError(
                file_name, 0, "Lines must be a list"
            )
        
        try:
            with error_context(f"parsing headers from {file_name}"):
                for line_num, line in enumerate(lines):
                    if not isinstance(line, str):
                        logger.warning(
                            f"Non-string line at {line_num} in {file_name}: {type(line)}"
                        )
                        continue
                    
                    # Удаляем лишние пробелы
                    cleaned_line = line.strip()
                    
                    # Проверяем соответствие паттерну заголовка
                    match = self.HEADER_PATTERN.match(cleaned_line)
                    if match:
                        level_markers = match.group(1)  # Символы #
                        title = match.group(2).strip()  # Текст заголовка
                        
                        level = len(level_markers)
                        
                        # Проверяем уровень заголовка
                        if level > self.max_header_level:
                            logger.debug(
                                f"Skipping header at line {line_num} in {file_name}: "
                                f"level {level} exceeds maximum {self.max_header_level}"
                            )
                            continue
                        
                        # Проверяем, что заголовок не пустой
                        if not title:
                            logger.warning(
                                f"Empty header at line {line_num} in {file_name}"
                            )
                            continue
                        
                        # Ограничиваем длину заголовка
                        if len(title) > 200:
                            title = title[:197] + "..."
                            logger.debug(
                                f"Truncated long header at line {line_num} in {file_name}"
                            )
                        
                        headers.append((title, level, line_num))
                        logger.debug(
                            f"Found header at line {line_num}: level {level}, title '{title}'"
                        )
                
        except Exception as e:
            raise MarkdownParsingError(
                file_name, 
                getattr(e, 'line_num', 0),
                f"Unexpected error during header parsing: {str(e)}"
            )
        
        self.total_headers_count += len(headers)
        logger.debug(f"Parsed {len(headers)} headers from {file_name}")
        
        return headers
    
    @handle_exceptions(TocBuildError, reraise=False, default_return={})
    def build_toc(self, files: Dict[Path, List[str]]) -> Dict[Path, List[Tuple[str, int, int]]]:
        """
        Строит оглавление для коллекции файлов.
        
        Args:
            files: Словарь файлов и их содержимого
            
        Returns:
            Словарь с заголовками для каждого файла
            
        Raises:
            TocBuildError: При ошибках построения оглавления
        """
        if not isinstance(files, dict):
            raise TocBuildError("Files must be a dictionary")
        
        result = {}
        self.processed_files_count = 0
        self.total_headers_count = 0
        failed_files = []
        
        logger.info(f"Building TOC for {len(files)} files")
        
        for file_path, lines in files.items():
            try:
                if not isinstance(file_path, Path):
                    logger.warning(f"Skipping non-Path key: {type(file_path)}")
                    continue
                
                headers = self.parse_headers_from_lines(lines, file_path)
                result[file_path] = headers
                self.processed_files_count += 1
                
                logger.debug(
                    f"Processed {file_path}: {len(headers)} headers found"
                )
                
            except MarkdownParsingError as e:
                logger.error(f"Failed to parse headers from {file_path}: {e.message}")
                failed_files.append(str(file_path))
                # Добавляем пустой список заголовков для файлов с ошибками
                result[file_path] = []
                continue
            
            except Exception as e:
                logger.error(f"Unexpected error processing {file_path}: {str(e)}")
                failed_files.append(str(file_path))
                result[file_path] = []
                continue
        
        logger.info(
            f"TOC building completed: {self.processed_files_count} files processed, "
            f"{self.total_headers_count} total headers, {len(failed_files)} files failed"
        )
        
        if failed_files:
            logger.warning(f"Failed files: {', '.join(failed_files)}")
        
        if not result:
            logger.warning("No files were successfully processed for TOC")
        
        return result
    
    def get_stats(self) -> Dict[str, int]:
        """Возвращает статистику построения оглавления."""
        return {
            "processed_files": self.processed_files_count,
            "total_headers": self.total_headers_count
        }
    
    def validate_toc_structure(self, toc: Dict[Path, List[Tuple[str, int, int]]]) -> bool:
        """
        Валидирует структуру оглавления.
        
        Args:
            toc: Оглавление для валидации
            
        Returns:
            True, если структура корректна
        """
        try:
            for file_path, headers in toc.items():
                if not isinstance(file_path, Path):
                    logger.error(f"Invalid file path type: {type(file_path)}")
                    return False
                
                if not isinstance(headers, list):
                    logger.error(f"Invalid headers type for {file_path}: {type(headers)}")
                    return False
                
                for header in headers:
                    if not isinstance(header, tuple) or len(header) != 3:
                        logger.error(f"Invalid header format in {file_path}: {header}")
                        return False
                    
                    title, level, line_num = header
                    if not isinstance(title, str) or not isinstance(level, int) or not isinstance(line_num, int):
                        logger.error(f"Invalid header data types in {file_path}: {header}")
                        return False
                    
                    if level < 1 or level > 6:
                        logger.error(f"Invalid header level in {file_path}: {level}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error during TOC validation: {str(e)}")
            return False


# Функция обратной совместимости
def build_toc(files: Dict[Path, List[str]]) -> Dict[Path, List[Tuple[str, int, int]]]:
    """
    Функция обратной совместимости для построения оглавления.
    
    Args:
        files: Словарь файлов и их содержимого
        
    Returns:
        Словарь с заголовками для каждого файла
    """
    builder = TocBuilder()
    return builder.build_toc(files)