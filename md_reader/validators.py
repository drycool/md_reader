"""
Модуль валидации для md_reader.

Обеспечивает безопасную валидацию путей, файлов и пользовательского ввода
для предотвращения уязвимостей и повышения надежности.
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Union

from .exceptions import PathValidationError, UserInputError, FileLoadError
from .logger import get_logger, handle_exceptions

logger = get_logger("validators")


class PathValidator:
    """Валидатор для безопасной работы с путями файловой системы."""
    
    # Опасные паттерны в путях
    DANGEROUS_PATTERNS = [
        r'\.\.[\\/]',  # Path traversal
        r'^[\\/]',     # Absolute paths начинающиеся с root
        r'[\x00-\x1f]', # Control characters
        r'[<>:"|?*]',  # Windows недопустимые символы
    ]
    
    # Максимальная длина пути
    MAX_PATH_LENGTH = 260  # Windows ограничение
    
    @classmethod
    @handle_exceptions(PathValidationError, reraise=True)
    def validate_path(cls, path: Union[str, Path], must_exist: bool = True) -> Path:
        """
        Валидирует путь на безопасность и корректность.
        
        Args:
            path: Путь для валидации
            must_exist: Требовать существования пути
            
        Returns:
            Валидированный объект Path
            
        Raises:
            PathValidationError: При невалидном пути
        """
        if path is None:
            raise PathValidationError("", "Path cannot be None")
        
        # Конвертируем в строку для валидации
        path_str = str(path)
        
        # Проверка длины
        if len(path_str) > cls.MAX_PATH_LENGTH:
            raise PathValidationError(
                path_str, 
                f"Path too long (max {cls.MAX_PATH_LENGTH} characters)"
            )
        
        # Проверка на опасные паттерны
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, path_str):
                raise PathValidationError(
                    path_str, 
                    f"Path contains dangerous pattern: {pattern}"
                )
        
        # Нормализация пути
        try:
            normalized_path = Path(path_str).resolve()
        except (OSError, ValueError) as e:
            raise PathValidationError(path_str, f"Invalid path format: {str(e)}")
        
        # Проверка существования
        if must_exist and not normalized_path.exists():
            raise PathValidationError(
                str(normalized_path), 
                "Path does not exist"
            )
        
        logger.debug(f"Path validated successfully: {normalized_path}")
        return normalized_path
    
    @classmethod
    @handle_exceptions(PathValidationError, reraise=True)
    def validate_file_path(cls, path: Union[str, Path], check_readable: bool = True) -> Path:
        """
        Валидирует путь к файлу.
        
        Args:
            path: Путь к файлу
            check_readable: Проверять читаемость файла
            
        Returns:
            Валидированный путь к файлу
            
        Raises:
            PathValidationError: При невалидном пути
            FileLoadError: При проблемах с доступом к файлу
        """
        validated_path = cls.validate_path(path, must_exist=True)
        
        if not validated_path.is_file():
            raise PathValidationError(
                str(validated_path), 
                "Path is not a file"
            )
        
        if check_readable:
            try:
                # Проверяем права на чтение
                if not os.access(validated_path, os.R_OK):
                    raise FileLoadError(
                        str(validated_path),
                        "File is not readable"
                    )
                
                # Пробуем открыть файл
                with open(validated_path, 'r', encoding='utf-8') as f:
                    f.read(1)  # Читаем один символ для проверки
                    
            except (PermissionError, OSError) as e:
                raise FileLoadError(
                    str(validated_path),
                    f"Cannot access file: {str(e)}"
                )
        
        return validated_path
    
    @classmethod
    @handle_exceptions(PathValidationError, reraise=True)
    def validate_directory_path(cls, path: Union[str, Path], check_readable: bool = True) -> Path:
        """
        Валидирует путь к директории.
        
        Args:
            path: Путь к директории
            check_readable: Проверять читаемость директории
            
        Returns:
            Валидированный путь к директории
            
        Raises:
            PathValidationError: При невалидном пути
        """
        validated_path = cls.validate_path(path, must_exist=True)
        
        if not validated_path.is_dir():
            raise PathValidationError(
                str(validated_path), 
                "Path is not a directory"
            )
        
        if check_readable and not os.access(validated_path, os.R_OK):
            raise PathValidationError(
                str(validated_path), 
                "Directory is not readable"
            )
        
        return validated_path
    
    @classmethod
    def is_markdown_file(cls, path: Path) -> bool:
        """Проверяет, является ли файл Markdown файлом."""
        return path.suffix.lower() in ['.md', '.markdown', '.mdown', '.mkd']
    
    @classmethod
    @handle_exceptions(PathValidationError, reraise=True)
    def validate_markdown_file(cls, path: Union[str, Path]) -> Path:
        """
        Валидирует Markdown файл.
        
        Args:
            path: Путь к Markdown файлу
            
        Returns:
            Валидированный путь
            
        Raises:
            PathValidationError: При невалидном файле
        """
        validated_path = cls.validate_file_path(path)
        
        if not cls.is_markdown_file(validated_path):
            raise PathValidationError(
                str(validated_path), 
                f"File is not a Markdown file (extension: {validated_path.suffix})"
            )
        
        return validated_path


class InputValidator:
    """Валидатор для пользовательского ввода."""
    
    # Максимальная длина строки ввода
    MAX_INPUT_LENGTH = 1000
    
    @classmethod
    @handle_exceptions(UserInputError, reraise=True)
    def validate_search_query(cls, query: str) -> str:
        """
        Валидирует поисковый запрос.
        
        Args:
            query: Поисковый запрос
            
        Returns:
            Очищенный запрос
            
        Raises:
            UserInputError: При невалидном запросе
        """
        if not isinstance(query, str):
            raise UserInputError(str(query), "Query must be a string")
        
        # Удаляем лишние пробелы
        cleaned_query = query.strip()
        
        if not cleaned_query:
            raise UserInputError(query, "Query cannot be empty")
        
        if len(cleaned_query) > cls.MAX_INPUT_LENGTH:
            raise UserInputError(
                query, 
                f"Query too long (max {cls.MAX_INPUT_LENGTH} characters)"
            )
        
        # Удаляем потенциально опасные символы
        # Оставляем только буквы, цифры, пробелы и основные знаки препинания
        safe_query = re.sub(r'[^\w\s\-.,!?()[\]{}\'"`]+', '', cleaned_query)
        
        if not safe_query:
            raise UserInputError(query, "Query contains only invalid characters")
        
        logger.debug(f"Search query validated: '{safe_query}'")
        return safe_query
    
    @classmethod
    @handle_exceptions(UserInputError, reraise=True)
    def validate_selection_input(cls, selection: str, max_options: int) -> int:
        """
        Валидирует пользовательский выбор из списка опций.
        
        Args:
            selection: Пользовательский ввод
            max_options: Максимальное количество опций
            
        Returns:
            Валидированный номер выбора (1-based)
            
        Raises:
            UserInputError: При невалидном выборе
        """
        if not isinstance(selection, str):
            raise UserInputError(str(selection), "Selection must be a string")
        
        cleaned_selection = selection.strip()
        
        if not cleaned_selection.isdigit():
            raise UserInputError(
                selection, 
                "Selection must be a number"
            )
        
        try:
            selection_num = int(cleaned_selection)
        except ValueError:
            raise UserInputError(
                selection, 
                "Invalid number format"
            )
        
        if selection_num < 1 or selection_num > max_options:
            raise UserInputError(
                selection,
                f"Selection must be between 1 and {max_options}"
            )
        
        return selection_num


class FileContentValidator:
    """Валидатор содержимого файлов."""
    
    # Максимальный размер файла в байтах (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    @classmethod
    @handle_exceptions(FileLoadError, reraise=True)
    def validate_file_size(cls, file_path: Path) -> None:
        """
        Проверяет размер файла.
        
        Args:
            file_path: Путь к файлу
            
        Raises:
            FileLoadError: При превышении максимального размера
        """
        try:
            file_size = file_path.stat().st_size
        except OSError as e:
            raise FileLoadError(
                str(file_path),
                f"Cannot get file size: {str(e)}"
            )
        
        if file_size > cls.MAX_FILE_SIZE:
            raise FileLoadError(
                str(file_path),
                f"File too large: {file_size} bytes (max {cls.MAX_FILE_SIZE})"
            )
    
    @classmethod
    @handle_exceptions(FileLoadError, reraise=True)
    def validate_text_encoding(cls, file_path: Path) -> str:
        """
        Проверяет и определяет кодировку текстового файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Определенная кодировка
            
        Raises:
            FileLoadError: При проблемах с кодировкой
        """
        encodings_to_try = ['utf-8', 'utf-8-sig', 'cp1251', 'latin1']
        
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read()
                logger.debug(f"File {file_path} detected encoding: {encoding}")
                return encoding
            except UnicodeDecodeError:
                continue
        
        raise FileLoadError(
            str(file_path),
            "Cannot determine file encoding"
        )