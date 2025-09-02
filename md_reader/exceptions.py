"""
Кастомные исключения для md_reader.

Этот модуль определяет специфичные для проекта исключения,
которые обеспечивают более точную обработку различных типов ошибок.
"""

from typing import Optional


class MdReaderError(Exception):
    """Базовое исключение для всех ошибок md_reader."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class FileLoadError(MdReaderError):
    """Исключение при ошибках загрузки файлов."""
    
    def __init__(self, file_path: str, message: str, details: Optional[str] = None):
        self.file_path = file_path
        super().__init__(f"Error loading file '{file_path}': {message}", details)


class PathValidationError(MdReaderError):
    """Исключение при валидации путей."""
    
    def __init__(self, path: str, message: str, details: Optional[str] = None):
        self.path = path
        super().__init__(f"Invalid path '{path}': {message}", details)


class MarkdownParsingError(MdReaderError):
    """Исключение при парсинге Markdown."""
    
    def __init__(self, file_path: str, line_number: int, message: str, details: Optional[str] = None):
        self.file_path = file_path
        self.line_number = line_number
        super().__init__(
            f"Markdown parsing error in '{file_path}' at line {line_number}: {message}", 
            details
        )


class TocBuildError(MdReaderError):
    """Исключение при построении содержания."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, details: Optional[str] = None):
        self.file_path = file_path
        if file_path:
            message = f"TOC build error for '{file_path}': {message}"
        super().__init__(message, details)


class ConfigurationError(MdReaderError):
    """Исключение при ошибках конфигурации."""
    
    def __init__(self, setting: str, message: str, details: Optional[str] = None):
        self.setting = setting
        super().__init__(f"Configuration error for '{setting}': {message}", details)


class UserInputError(MdReaderError):
    """Исключение при неверном пользовательском вводе."""
    
    def __init__(self, input_value: str, message: str, details: Optional[str] = None):
        self.input_value = input_value
        super().__init__(f"Invalid user input '{input_value}': {message}", details)


class CacheError(MdReaderError):
    """Исключение при работе с кэшем."""
    
    def __init__(self, operation: str, message: str, details: Optional[str] = None):
        self.operation = operation
        super().__init__(f"Cache error during '{operation}': {message}", details)