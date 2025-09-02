"""
Test configuration and fixtures for md_reader test suite.

This module provides common test fixtures, utilities, and configuration
for the comprehensive test suite.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Generator, Optional
from unittest.mock import Mock, MagicMock

# Import all modules to test
from md_reader.exceptions import *
from md_reader.logger import setup_logging, get_logger
from md_reader.validators import PathValidator, InputValidator, FileContentValidator
from md_reader.loader import MarkdownLoader
from md_reader.enhanced_loader import EnhancedMarkdownLoader, LoadingOptions
from md_reader.toc import TocBuilder
from md_reader.viewer import InteractiveViewer
from md_reader.cache import MemoryCache, FileBasedCache, SmartFileCache
from md_reader.container import DependencyContainer
from md_reader.interfaces import *


@pytest.fixture(scope="session")
def test_logger():
    """Setup test logger."""
    return setup_logging(level="DEBUG")


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_markdown_files(temp_dir):
    """Create sample markdown files for testing."""
    files = {}
    
    # File 1: Simple structure
    file1 = temp_dir / "simple.md"
    content1 = """# Main Header
This is the introduction.

## Section 1
Content of section 1.

### Subsection 1.1
More detailed content.

## Section 2
Content of section 2.
"""
    file1.write_text(content1, encoding='utf-8')
    files['simple'] = file1
    
    # File 2: Complex structure
    file2 = temp_dir / "complex.md"
    content2 = """# Complex Document
Introduction with **bold** and *italic* text.

## Overview
- Item 1
- Item 2
- Item 3

### Technical Details
```python
def example_function():
    return "Hello, World!"
```

#### Implementation Notes
Some implementation details here.

## Conclusion
Final thoughts.

# Appendix
Additional information.
"""
    file2.write_text(content2, encoding='utf-8')
    files['complex'] = file2
    
    # File 3: Empty headers
    file3 = temp_dir / "edge_cases.md"
    content3 = """#
## 
### Valid Header
Content here.

####    Spaces Header    
More content.

###### Deep Header
Deep content.
"""
    file3.write_text(content3, encoding='utf-8')
    files['edge_cases'] = file3
    
    # File 4: No headers
    file4 = temp_dir / "no_headers.md"
    content4 = """This file has no headers.
Just plain text content.
Multiple lines of content.
"""
    file4.write_text(content4, encoding='utf-8')
    files['no_headers'] = file4
    
    # File 5: Unicode content
    file5 = temp_dir / "unicode.md"
    content5 = """# Unicode Test 测试
Content with émojis 🚀 and special characters.

## Раздел на русском
Русский текст для проверки кодировки.

### Section en français
Contenu en français avec des accents: café, résumé.
"""
    file5.write_text(content5, encoding='utf-8')
    files['unicode'] = file5
    
    # Subdirectory with files
    subdir = temp_dir / "subdir"
    subdir.mkdir()
    
    file6 = subdir / "nested.md"
    content6 = """# Nested File
This file is in a subdirectory.

## Nested Section
Nested content.
"""
    file6.write_text(content6, encoding='utf-8')
    files['nested'] = file6
    
    # Non-markdown file (should be ignored)
    txt_file = temp_dir / "not_markdown.txt"
    txt_file.write_text("This is not a markdown file.", encoding='utf-8')
    
    return files


@pytest.fixture
def expected_toc_data():
    """Expected TOC data for sample files."""
    return {
        'simple': [
            ("Main Header", 1, 0),
            ("Section 1", 2, 3),
            ("Subsection 1.1", 3, 6),
            ("Section 2", 2, 9)
        ],
        'complex': [
            ("Complex Document", 1, 0),
            ("Overview", 2, 3),
            ("Technical Details", 3, 8),
            ("Implementation Notes", 4, 14),
            ("Conclusion", 2, 17),
            ("Appendix", 1, 20)
        ],
        'edge_cases': [
            ("Valid Header", 3, 2),
            ("Spaces Header", 4, 5),
            ("Deep Header", 6, 8)
        ],
        'no_headers': [],
        'unicode': [
            ("Unicode Test 测试", 1, 0),
            ("Раздел на русском", 2, 3),
            ("Section en français", 3, 6)
        ],
        'nested': [
            ("Nested File", 1, 0),
            ("Nested Section", 2, 3)
        ]
    }


@pytest.fixture
def mock_cache():
    """Create a mock cache for testing."""
    cache = Mock(spec=ICache)
    cache.get.return_value = None
    cache.set.return_value = None
    cache.invalidate.return_value = None
    cache.clear.return_value = None
    return cache


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    logger = Mock()
    logger.debug.return_value = None
    logger.info.return_value = None
    logger.warning.return_value = None
    logger.error.return_value = None
    return logger


@pytest.fixture
def dependency_container():
    """Create a fresh dependency container for each test."""
    container = DependencyContainer()
    yield container
    container.dispose_scope()


@pytest.fixture
def markdown_loader():
    """Create a markdown loader instance."""
    return MarkdownLoader()


@pytest.fixture
def enhanced_loader():
    """Create an enhanced markdown loader instance."""
    options = LoadingOptions(
        max_workers=2,
        enable_cache=False,  # Disable cache for predictable tests
        preload_headers_only=False
    )
    return EnhancedMarkdownLoader(options)


@pytest.fixture
def toc_builder():
    """Create a TOC builder instance."""
    return TocBuilder()


@pytest.fixture
def memory_cache():
    """Create a memory cache instance."""
    return MemoryCache(max_size=10, default_ttl=60)


@pytest.fixture
def file_cache(temp_dir):
    """Create a file-based cache instance."""
    cache_dir = temp_dir / "cache"
    return FileBasedCache(cache_dir=cache_dir, max_size=5)


@pytest.fixture
def large_file(temp_dir):
    """Create a large file for testing file size limits."""
    large_file = temp_dir / "large.md"
    # Create a file larger than default limit (simulate with repeated content)
    content = "# Large File\n" + "This is a line of content.\n" * 1000
    large_file.write_text(content, encoding='utf-8')
    return large_file


@pytest.fixture
def binary_file(temp_dir):
    """Create a binary file that should cause encoding errors."""
    binary_file = temp_dir / "binary.md"
    # Write binary data that will cause encoding issues
    with open(binary_file, 'wb') as f:
        f.write(b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09')
    return binary_file


@pytest.fixture
def dangerous_paths():
    """Provide dangerous path patterns for security testing."""
    return [
        "../../../etc/passwd",
        "..\\..\\windows\\system32\\config\\sam",
        "/etc/shadow",
        "C:\\Windows\\System32\\config\\SAM",
        "test\x00file.md",
        "test\nfile.md",
        "test\rfile.md",
        "con.md",  # Windows reserved name
        "aux.md",  # Windows reserved name
        "file" + "x" * 300 + ".md"  # Too long filename
    ]


@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset global state before each test."""
    # Reset any global caches or singletons
    yield
    # Cleanup after test


# Test utilities

def create_test_file(directory: Path, name: str, content: str) -> Path:
    """Create a test file with given content."""
    file_path = directory / name
    file_path.write_text(content, encoding='utf-8')
    return file_path


def assert_file_list_equal(actual: List[Path], expected: List[Path]):
    """Assert that two lists of file paths are equal (order-independent)."""
    assert set(actual) == set(expected), f"Expected {expected}, got {actual}"


def assert_toc_equal(actual_toc, expected_toc):
    """Assert that two TOC structures are equal."""
    assert len(actual_toc) == len(expected_toc)
    
    for file_path, headers in actual_toc.items():
        assert file_path.name in expected_toc or str(file_path) in expected_toc
        
        key = file_path.name if file_path.name in expected_toc else str(file_path)
        expected_headers = expected_toc[key]
        
        assert len(headers) == len(expected_headers)
        
        for actual_header, expected_header in zip(headers, expected_headers):
            assert actual_header == expected_header


class MockTextualApp:
    """Mock Textual app for UI testing."""
    
    def __init__(self):
        self.notifications = []
        self.log_messages = []
    
    def notify(self, message: str, title: str = None):
        self.notifications.append({"message": message, "title": title})
    
    def log(self, message: str):
        self.log_messages.append(message)


@pytest.fixture
def mock_textual_app():
    """Create a mock Textual app for UI testing."""
    return MockTextualApp()


# Performance testing utilities

class PerformanceMetrics:
    """Collect performance metrics during tests."""
    
    def __init__(self):
        self.metrics = {}
    
    def record(self, operation: str, duration: float):
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(duration)
    
    def get_average(self, operation: str) -> float:
        if operation not in self.metrics:
            return 0.0
        return sum(self.metrics[operation]) / len(self.metrics[operation])
    
    def get_total(self, operation: str) -> float:
        if operation not in self.metrics:
            return 0.0
        return sum(self.metrics[operation])


@pytest.fixture
def performance_metrics():
    """Create performance metrics collector."""
    return PerformanceMetrics()


# Markers for different test categories
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.performance = pytest.mark.performance
pytest.mark.security = pytest.mark.security
pytest.mark.slow = pytest.mark.slow