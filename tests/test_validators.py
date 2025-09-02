"""
Unit tests for validators module.

Tests path validation, input validation, and file content validation
including security edge cases and error handling.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from md_reader.validators import (
    PathValidator, InputValidator, FileContentValidator
)
from md_reader.exceptions import (
    PathValidationError, UserInputError, FileLoadError
)


@pytest.mark.unit
class TestPathValidator:
    """Test path validation functionality."""
    
    def test_validate_safe_path_existing_file(self, temp_dir):
        """Test validation of safe, existing file path."""
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test", encoding='utf-8')
        
        result = PathValidator.validate_path(test_file)
        assert result.exists()
        assert result.is_absolute()
    
    def test_validate_safe_path_non_existing_file(self, temp_dir):
        """Test validation when file doesn't exist but path is safe."""
        test_file = temp_dir / "nonexistent.md"
        
        with pytest.raises(PathValidationError) as exc_info:
            PathValidator.validate_path(test_file, must_exist=True)
        assert "does not exist" in str(exc_info.value)
    
    def test_validate_path_without_existence_check(self, temp_dir):
        """Test validation without requiring file existence."""
        test_file = temp_dir / "nonexistent.md"
        
        result = PathValidator.validate_path(test_file, must_exist=False)
        assert result.is_absolute()
    
    @pytest.mark.security
    def test_reject_path_traversal_attacks(self, dangerous_paths):
        """Test rejection of path traversal attacks."""
        for dangerous_path in dangerous_paths:
            with pytest.raises(PathValidationError) as exc_info:
                PathValidator.validate_path(dangerous_path, must_exist=False)
            assert "dangerous pattern" in str(exc_info.value).lower() or \
                   "invalid path" in str(exc_info.value).lower()
    
    def test_reject_none_path(self):
        """Test rejection of None path."""
        with pytest.raises(PathValidationError) as exc_info:
            PathValidator.validate_path(None)
        assert "cannot be None" in str(exc_info.value)
    
    def test_reject_too_long_path(self):
        """Test rejection of excessively long paths."""
        long_path = "x" * 300 + ".md"
        
        with pytest.raises(PathValidationError) as exc_info:
            PathValidator.validate_path(long_path, must_exist=False)
        assert "too long" in str(exc_info.value).lower()
    
    def test_validate_file_path_success(self, temp_dir):
        """Test successful file path validation."""
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test", encoding='utf-8')
        
        result = PathValidator.validate_file_path(test_file)
        assert result == test_file.resolve()
    
    def test_validate_file_path_is_directory(self, temp_dir):
        """Test rejection when path points to directory."""
        with pytest.raises(PathValidationError) as exc_info:
            PathValidator.validate_file_path(temp_dir)
        assert "not a file" in str(exc_info.value)
    
    def test_validate_file_path_unreadable(self, temp_dir):
        """Test handling of unreadable files."""
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test", encoding='utf-8')
        
        # Mock os.access to return False
        with patch('os.access', return_value=False):
            with pytest.raises(FileLoadError) as exc_info:
                PathValidator.validate_file_path(test_file, check_readable=True)
            assert "not readable" in str(exc_info.value)
    
    def test_validate_directory_path_success(self, temp_dir):
        """Test successful directory path validation."""
        result = PathValidator.validate_directory_path(temp_dir)
        assert result == temp_dir.resolve()
    
    def test_validate_directory_path_is_file(self, temp_dir):
        """Test rejection when path points to file instead of directory."""
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test", encoding='utf-8')
        
        with pytest.raises(PathValidationError) as exc_info:
            PathValidator.validate_directory_path(test_file)
        assert "not a directory" in str(exc_info.value)
    
    def test_is_markdown_file_true_cases(self):
        """Test markdown file detection for valid extensions."""
        valid_extensions = ['.md', '.markdown', '.mdown', '.mkd', '.MD', '.Markdown']
        
        for ext in valid_extensions:
            path = Path(f"test{ext}")
            assert PathValidator.is_markdown_file(path)
    
    def test_is_markdown_file_false_cases(self):
        """Test markdown file detection for invalid extensions."""
        invalid_extensions = ['.txt', '.html', '.pdf', '.doc', '.py', '']
        
        for ext in invalid_extensions:
            path = Path(f"test{ext}")
            assert not PathValidator.is_markdown_file(path)
    
    def test_validate_markdown_file_success(self, temp_dir):
        """Test successful markdown file validation."""
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test", encoding='utf-8')
        
        result = PathValidator.validate_markdown_file(test_file)
        assert result == test_file.resolve()
    
    def test_validate_markdown_file_wrong_extension(self, temp_dir):
        """Test rejection of non-markdown file."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test content", encoding='utf-8')
        
        with pytest.raises(PathValidationError) as exc_info:
            PathValidator.validate_markdown_file(test_file)
        assert "not a Markdown file" in str(exc_info.value)


@pytest.mark.unit
class TestInputValidator:
    """Test input validation functionality."""
    
    def test_validate_search_query_success(self):
        """Test successful search query validation."""
        valid_queries = [
            "simple query",
            "query with numbers 123",
            "query-with-dashes",
            "query_with_underscores",
            "Query With Capitals",
            "query.with.dots",
            "query!with?punctuation",
            "query (with) [brackets] {braces}",
            "query 'with' \"quotes\""
        ]
        
        for query in valid_queries:
            result = InputValidator.validate_search_query(query)
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_validate_search_query_edge_cases(self):
        """Test search query validation edge cases."""
        # Empty query after stripping
        with pytest.raises(UserInputError):
            InputValidator.validate_search_query("   ")
        
        # Empty query
        with pytest.raises(UserInputError):
            InputValidator.validate_search_query("")
        
        # None query
        with pytest.raises(UserInputError):
            InputValidator.validate_search_query(None)
    
    def test_validate_search_query_too_long(self):
        """Test rejection of excessively long queries."""
        long_query = "x" * 1001
        
        with pytest.raises(UserInputError) as exc_info:
            InputValidator.validate_search_query(long_query)
        assert "too long" in str(exc_info.value)
    
    def test_validate_search_query_sanitization(self):
        """Test that dangerous characters are sanitized."""
        dangerous_query = "normal<script>alert('xss')</script>text"
        result = InputValidator.validate_search_query(dangerous_query)
        
        # Should not contain script tags
        assert "<script>" not in result
        assert "alert" not in result or "script" not in result
    
    def test_validate_search_query_non_string(self):
        """Test rejection of non-string input."""
        with pytest.raises(UserInputError):
            InputValidator.validate_search_query(123)
        
        with pytest.raises(UserInputError):
            InputValidator.validate_search_query(['list', 'input'])
    
    def test_validate_selection_input_success(self):
        """Test successful selection input validation."""
        test_cases = [
            ("1", 5, 1),
            ("3", 10, 3),
            ("10", 10, 10),
            ("  2  ", 5, 2)  # With whitespace
        ]
        
        for input_val, max_options, expected in test_cases:
            result = InputValidator.validate_selection_input(input_val, max_options)
            assert result == expected
    
    def test_validate_selection_input_out_of_range(self):
        """Test rejection of out-of-range selections."""
        # Below range
        with pytest.raises(UserInputError):
            InputValidator.validate_selection_input("0", 5)
        
        # Above range
        with pytest.raises(UserInputError):
            InputValidator.validate_selection_input("6", 5)
        
        # Negative
        with pytest.raises(UserInputError):
            InputValidator.validate_selection_input("-1", 5)
    
    def test_validate_selection_input_non_numeric(self):
        """Test rejection of non-numeric selections."""
        invalid_inputs = ["abc", "1.5", "1a", "a1", "", "  "]
        
        for invalid_input in invalid_inputs:
            with pytest.raises(UserInputError):
                InputValidator.validate_selection_input(invalid_input, 5)
    
    def test_validate_selection_input_non_string(self):
        """Test rejection of non-string selection input."""
        with pytest.raises(UserInputError):
            InputValidator.validate_selection_input(123, 5)
        
        with pytest.raises(UserInputError):
            InputValidator.validate_selection_input(None, 5)


@pytest.mark.unit
class TestFileContentValidator:
    """Test file content validation functionality."""
    
    def test_validate_file_size_success(self, temp_dir):
        """Test successful file size validation."""
        test_file = temp_dir / "small.md"
        test_file.write_text("# Small file\nContent", encoding='utf-8')
        
        # Should not raise exception
        FileContentValidator.validate_file_size(test_file)
    
    def test_validate_file_size_too_large(self, temp_dir):
        """Test rejection of files that are too large."""
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test", encoding='utf-8')
        
        # Mock stat to return large size
        with patch.object(Path, 'stat') as mock_stat:
            mock_stat.return_value.st_size = FileContentValidator.MAX_FILE_SIZE + 1
            
            with pytest.raises(FileLoadError) as exc_info:
                FileContentValidator.validate_file_size(test_file)
            assert "too large" in str(exc_info.value)
    
    def test_validate_file_size_stat_error(self, temp_dir):
        """Test handling of stat errors."""
        nonexistent_file = temp_dir / "nonexistent.md"
        
        with pytest.raises(FileLoadError) as exc_info:
            FileContentValidator.validate_file_size(nonexistent_file)
        assert "Cannot get file size" in str(exc_info.value)
    
    def test_validate_text_encoding_utf8(self, temp_dir):
        """Test UTF-8 encoding detection."""
        test_file = temp_dir / "utf8.md"
        test_file.write_text("# UTF-8 Test 测试", encoding='utf-8')
        
        encoding = FileContentValidator.validate_text_encoding(test_file)
        assert encoding == 'utf-8'
    
    def test_validate_text_encoding_with_bom(self, temp_dir):
        """Test UTF-8 with BOM encoding detection."""
        test_file = temp_dir / "utf8_bom.md"
        
        with open(test_file, 'w', encoding='utf-8-sig') as f:
            f.write("# UTF-8 with BOM")
        
        encoding = FileContentValidator.validate_text_encoding(test_file)
        assert encoding in ['utf-8', 'utf-8-sig']
    
    def test_validate_text_encoding_cp1251(self, temp_dir):
        """Test CP1251 encoding detection."""
        test_file = temp_dir / "cp1251.md"
        
        # Write file with CP1251 encoding
        with open(test_file, 'w', encoding='cp1251') as f:
            f.write("# Тест на русском")
        
        encoding = FileContentValidator.validate_text_encoding(test_file)
        assert encoding in ['cp1251', 'utf-8', 'latin1']  # Fallback order
    
    def test_validate_text_encoding_binary_file(self, binary_file):
        """Test handling of binary files."""
        with pytest.raises(FileLoadError) as exc_info:
            FileContentValidator.validate_text_encoding(binary_file)
        assert "Cannot determine file encoding" in str(exc_info.value)
    
    @pytest.mark.security
    def test_max_file_size_constant(self):
        """Test that max file size is reasonable for security."""
        # Should be reasonable for markdown files but not too large
        assert 1024 <= FileContentValidator.MAX_FILE_SIZE <= 100 * 1024 * 1024
        assert isinstance(FileContentValidator.MAX_FILE_SIZE, int)


@pytest.mark.integration
class TestValidatorsIntegration:
    """Integration tests for validator components."""
    
    def test_complete_file_validation_pipeline(self, temp_dir):
        """Test complete validation pipeline for a file."""
        # Create test file
        test_file = temp_dir / "complete_test.md"
        content = "# Test Header\nSome content here."
        test_file.write_text(content, encoding='utf-8')
        
        # Run complete validation pipeline
        validated_path = PathValidator.validate_markdown_file(test_file)
        FileContentValidator.validate_file_size(validated_path)
        encoding = FileContentValidator.validate_text_encoding(validated_path)
        
        # Verify results
        assert validated_path.exists()
        assert encoding == 'utf-8'
        
        # Verify content can be read with detected encoding
        content_read = validated_path.read_text(encoding=encoding)
        assert "Test Header" in content_read
    
    def test_validation_with_user_input_workflow(self, temp_dir, sample_markdown_files):
        """Test validation in typical user workflow."""
        # Simulate user providing path
        user_path = str(temp_dir)
        
        # Validate directory path
        validated_dir = PathValidator.validate_directory_path(user_path)
        
        # Simulate user search query
        user_query = "  test search query  "
        validated_query = InputValidator.validate_search_query(user_query)
        assert validated_query == "test search query"
        
        # Simulate user selection
        user_selection = "2"
        validated_selection = InputValidator.validate_selection_input(user_selection, 5)
        assert validated_selection == 2
    
    @pytest.mark.security
    def test_security_validation_comprehensive(self, dangerous_paths):
        """Comprehensive security validation test."""
        # Test all dangerous paths are rejected
        for dangerous_path in dangerous_paths:
            with pytest.raises((PathValidationError, OSError)):
                PathValidator.validate_path(dangerous_path, must_exist=False)
        
        # Test malicious input queries are sanitized
        malicious_queries = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "\x00\x01\x02malicious"
        ]
        
        for malicious_query in malicious_queries:
            try:
                result = InputValidator.validate_search_query(malicious_query)
                # Should be sanitized
                assert "<script>" not in result
                assert "DROP TABLE" not in result
                assert "\x00" not in result
            except UserInputError:
                # Rejection is also acceptable
                pass
    
    def test_error_handling_consistency(self, temp_dir):
        """Test that error handling is consistent across validators."""
        # Test that all validators raise appropriate custom exceptions
        nonexistent_file = temp_dir / "nonexistent.md"
        
        # PathValidator should raise PathValidationError
        with pytest.raises(PathValidationError):
            PathValidator.validate_path(nonexistent_file, must_exist=True)
        
        # InputValidator should raise UserInputError
        with pytest.raises(UserInputError):
            InputValidator.validate_search_query("")
        
        # FileContentValidator should raise FileLoadError
        with pytest.raises(FileLoadError):
            FileContentValidator.validate_file_size(nonexistent_file)