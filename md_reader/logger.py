"""
Модуль логирования и обработки ошибок для md_reader.

Предоставляет централизованную систему логирования с различными уровнями
и декораторы для обработки исключений.
"""

import logging
import functools
import sys
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar, Union
from contextlib import contextmanager

from .exceptions import MdReaderError


# Настройка базового логирования
def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Настраивает систему логирования для приложения.
    
    Args:
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Путь к файлу логов (если None, логи выводятся в консоль)
        format_string: Кастомный формат логов
    
    Returns:
        Настроенный логгер
    """
    if format_string is None:
        format_string = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    
    # Создаем основной логгер
    logger = logging.getLogger("md_reader")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Очищаем существующие обработчики
    logger.handlers.clear()
    
    # Создаем форматтер
    formatter = logging.Formatter(format_string)
    
    # Настраиваем обработчик
    if log_file:
        # Логи в файл
        handler = logging.FileHandler(log_file, encoding='utf-8')
    else:
        # Логи в консоль
        handler = logging.StreamHandler(sys.stderr)
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


# Глобальный логгер
logger = setup_logging()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Получает логгер для конкретного модуля."""
    if name:
        return logging.getLogger(f"md_reader.{name}")
    return logging.getLogger("md_reader")


F = TypeVar('F', bound=Callable[..., Any])


def handle_exceptions(
    exception_types: Union[type, tuple] = Exception,
    reraise: bool = True,
    default_return: Any = None,
    log_level: str = "ERROR"
) -> Callable[[F], F]:
    """
    Декоратор для обработки исключений в функциях.
    
    Args:
        exception_types: Типы исключений для обработки
        reraise: Перевызывать исключение после логирования
        default_return: Значение по умолчанию при подавлении исключения
        log_level: Уровень логирования для ошибок
    
    Returns:
        Декорированная функция
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_types as e:
                func_name = f"{func.__module__}.{func.__name__}"
                
                # Логируем ошибку с контекстом
                log_message = f"Exception in {func_name}: {str(e)}"
                if hasattr(e, 'details') and e.details:
                    log_message += f" | Details: {e.details}"
                
                getattr(logger, log_level.lower())(
                    log_message,
                    exc_info=True if log_level.upper() == "DEBUG" else False
                )
                
                if reraise:
                    raise
                else:
                    return default_return
        
        return wrapper
    return decorator


@contextmanager
def error_context(operation: str, reraise: bool = True):
    """
    Контекстный менеджер для обработки ошибок в блоках кода.
    
    Args:
        operation: Описание операции для логирования
        reraise: Перевызывать исключение после логирования
    """
    try:
        logger.debug(f"Starting operation: {operation}")
        yield
        logger.debug(f"Completed operation: {operation}")
    except Exception as e:
        error_msg = f"Error during {operation}: {str(e)}"
        if hasattr(e, 'details') and e.details:
            error_msg += f" | Details: {e.details}"
        
        logger.error(error_msg, exc_info=True)
        
        if reraise:
            raise


def log_performance(func: F) -> F:
    """Декоратор для логирования времени выполнения функций."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import time
        
        start_time = time.time()
        func_name = f"{func.__module__}.{func.__name__}"
        
        logger.debug(f"Starting {func_name}")
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"Completed {func_name} in {execution_time:.4f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Failed {func_name} after {execution_time:.4f}s: {str(e)}")
            raise
    
    return wrapper


def safe_execute(
    operation: Callable,
    error_message: str,
    default_value: Any = None,
    exception_types: tuple = (Exception,)
) -> Any:
    """
    Безопасно выполняет операцию с обработкой ошибок.
    
    Args:
        operation: Функция для выполнения
        error_message: Сообщение об ошибке для логирования
        default_value: Возвращаемое значение при ошибке
        exception_types: Типы исключений для обработки
    
    Returns:
        Результат операции или значение по умолчанию
    """
    try:
        return operation()
    except exception_types as e:
        logger.error(f"{error_message}: {str(e)}")
        return default_value


class ErrorHandler:
    """Класс для централизованной обработки различных типов ошибок."""
    
    @staticmethod
    def handle_file_error(e: Exception, file_path: str) -> None:
        """Обрабатывает ошибки, связанные с файлами."""
        if isinstance(e, FileNotFoundError):
            logger.error(f"File not found: {file_path}")
        elif isinstance(e, PermissionError):
            logger.error(f"Permission denied accessing file: {file_path}")
        elif isinstance(e, UnicodeDecodeError):
            logger.error(f"Unicode decode error in file: {file_path}")
        else:
            logger.error(f"Unexpected file error for {file_path}: {str(e)}")
    
    @staticmethod
    def handle_validation_error(e: Exception, context: str) -> None:
        """Обрабатывает ошибки валидации."""
        if isinstance(e, MdReaderError):
            logger.error(f"Validation error in {context}: {e.message}")
            if e.details:
                logger.debug(f"Validation error details: {e.details}")
        else:
            logger.error(f"Unexpected validation error in {context}: {str(e)}")
    
    @staticmethod
    def handle_user_input_error(e: Exception, input_context: str) -> None:
        """Обрабатывает ошибки пользовательского ввода."""
        logger.warning(f"Invalid user input in {input_context}: {str(e)}")