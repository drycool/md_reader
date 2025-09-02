"""
Базовые тесты для валидации улучшений md_reader.

Проверяет основную функциональность после внедрения безопасной обработки ошибок,
валидации входных данных и централизованного логирования.
"""

import pytest
import tempfile
from pathlib import Path
from typing import Dict, List

# Импорты обновленных модулей
from md_reader.exceptions import (
    MdReaderError, FileLoadError, PathValidationError, 
    MarkdownParsingError, UserInputError
)
from md_reader.validators import PathValidator, InputValidator, FileContentValidator
from md_reader.loader import MarkdownLoader, load_markdown_files
from md_reader.toc import TocBuilder, build_toc
from md_reader.logger import setup_logging, get_logger


class TestPathValidator:
    """Тесты валидатора путей."""
    
    def test_validate_safe_path(self):
        """Тест валидации безопасного пути."""
        with tempfile.TemporaryDirectory() as temp_dir:
            safe_path = Path(temp_dir) / "test.md"
            safe_path.write_text("# Test\nContent", encoding='utf-8')
            
            result = PathValidator.validate_path(safe_path)
            assert result.exists()
    
    def test_reject_dangerous_path(self):
        """Тест отклонения опасных путей."""
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "/etc/passwd",
            "test\x00file.md"
        ]
        
        for dangerous_path in dangerous_paths:
            with pytest.raises(PathValidationError):
                PathValidator.validate_path(dangerous_path, must_exist=False)
    
    def test_validate_markdown_file(self):
        """Тест валидации Markdown файлов."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Создаем валидный Markdown файл
            md_file = Path(temp_dir) / "test.md"
            md_file.write_text("# Header\nContent", encoding='utf-8')
            
            result = PathValidator.validate_markdown_file(md_file)
            assert result == md_file.resolve()
            
            # Тестируем невалидный файл
            txt_file = Path(temp_dir) / "test.txt"
            txt_file.write_text("content", encoding='utf-8')
            
            with pytest.raises(PathValidationError):
                PathValidator.validate_markdown_file(txt_file)


class TestInputValidator:
    """Тесты валидатора пользовательского ввода."""
    
    def test_validate_search_query(self):
        """Тест валидации поискового запроса."""
        valid_queries = ["test", "search query", "123", "test-file.md"]
        
        for query in valid_queries:
            result = InputValidator.validate_search_query(query)
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_reject_invalid_search_query(self):
        """Тест отклонения невалидных запросов."""
        invalid_queries = ["", "   ", "a" * 2000, None]
        
        for query in invalid_queries:
            with pytest.raises(UserInputError):
                if query is None:
                    InputValidator.validate_search_query(query)
                else:
                    InputValidator.validate_search_query(query)
    
    def test_validate_selection_input(self):
        """Тест валидации выбора пользователя."""
        valid_selections = [("1", 5), ("3", 10), ("5", 5)]
        
        for selection, max_options in valid_selections:
            result = InputValidator.validate_selection_input(selection, max_options)
            assert isinstance(result, int)
            assert 1 <= result <= max_options
    
    def test_reject_invalid_selection(self):
        """Тест отклонения невалидного выбора."""
        invalid_selections = [("0", 5), ("6", 5), ("abc", 5), ("", 5)]
        
        for selection, max_options in invalid_selections:
            with pytest.raises(UserInputError):
                InputValidator.validate_selection_input(selection, max_options)


class TestMarkdownLoader:
    """Тесты загрузчика Markdown файлов."""
    
    def test_load_single_file(self):
        """Тест загрузки одного файла."""
        with tempfile.TemporaryDirectory() as temp_dir:
            md_file = Path(temp_dir) / "test.md"
            content = "# Header 1\nContent line 1\n## Header 2\nContent line 2"
            md_file.write_text(content, encoding='utf-8')
            
            loader = MarkdownLoader()
            result = loader.load_single_file(md_file)
            
            assert isinstance(result, list)
            assert len(result) == 4
            assert result[0] == "# Header 1"
    
    def test_load_markdown_files_directory(self):
        """Тест загрузки файлов из директории."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Создаем несколько Markdown файлов
            file1 = temp_path / "file1.md"
            file1.write_text("# File 1\nContent 1", encoding='utf-8')
            
            file2 = temp_path / "file2.md"
            file2.write_text("# File 2\nContent 2", encoding='utf-8')
            
            # Создаем не-Markdown файл (должен быть проигнорирован)
            txt_file = temp_path / "file.txt"
            txt_file.write_text("Not markdown", encoding='utf-8')
            
            loader = MarkdownLoader()
            result = loader.load_markdown_files(temp_path)
            
            assert len(result) == 2
            assert all(isinstance(lines, list) for lines in result.values())
            assert all(path.suffix == '.md' for path in result.keys())
    
    def test_handle_file_load_error(self):
        """Тест обработки ошибок загрузки файла."""
        loader = MarkdownLoader()
        
        # Тест несуществующего файла
        with pytest.raises(PathValidationError):
            loader.load_single_file("/nonexistent/file.md")


class TestTocBuilder:
    """Тесты строителя оглавления."""
    
    def test_parse_headers_from_lines(self):
        """Тест парсинга заголовков из строк."""
        lines = [
            "# Header 1",
            "Some content",
            "## Header 2", 
            "More content",
            "### Header 3",
            "Final content"
        ]
        
        builder = TocBuilder()
        result = builder.parse_headers_from_lines(lines)
        
        assert len(result) == 3
        assert result[0] == ("Header 1", 1, 0)
        assert result[1] == ("Header 2", 2, 2)
        assert result[2] == ("Header 3", 3, 4)
    
    def test_build_toc(self):
        """Тест построения оглавления."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            file1 = temp_path / "file1.md"
            file1.write_text("# Header 1\n## Subheader", encoding='utf-8')
            
            files = {file1: ["# Header 1", "## Subheader"]}
            
            builder = TocBuilder()
            result = builder.build_toc(files)
            
            assert file1 in result
            assert len(result[file1]) == 2
            assert result[file1][0] == ("Header 1", 1, 0)
            assert result[file1][1] == ("Subheader", 2, 1)
    
    def test_validate_toc_structure(self):
        """Тест валидации структуры оглавления."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            file1 = temp_path / "test.md"
            
            valid_toc = {
                file1: [("Header", 1, 0), ("Subheader", 2, 1)]
            }
            
            builder = TocBuilder()
            assert builder.validate_toc_structure(valid_toc) is True
            
            # Тест невалидной структуры
            invalid_toc = {
                file1: [("Header", "invalid_level", 0)]
            }
            assert builder.validate_toc_structure(invalid_toc) is False


def test_backward_compatibility():
    """Тест обратной совместимости с существующим API."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        md_file = temp_path / "test.md"
        md_file.write_text("# Header\nContent", encoding='utf-8')
        
        # Тест функций обратной совместимости
        files = load_markdown_files(temp_path)
        assert len(files) == 1
        
        toc = build_toc(files)
        assert len(toc) == 1
        assert len(toc[md_file]) == 1


if __name__ == "__main__":
    # Настройка логирования для тестов
    setup_logging(level="DEBUG")
    
    # Запуск тестов
    pytest.main([__file__, "-v"])