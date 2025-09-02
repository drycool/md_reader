# MD Reader - Complete API Reference

**Enhanced Interactive CLI Tool for Markdown Documentation with Enterprise-Grade Features**

## Overview

MD Reader is a sophisticated command-line tool designed for viewing and navigating Markdown documentation with advanced features including security validation, performance optimization, comprehensive caching, and dependency injection architecture.

## Quick Start

### Installation

```bash
# Standard installation
pip install md-reader

# Development installation with all tools
git clone <repository>
cd md_reader
pip install -e ".[dev]"
```

### Basic Usage

```bash
# Launch TUI interface
md-viewer tui /path/to/docs

# CLI mode for quick viewing
md-viewer open document.md

# View specific directory
md-viewer tui /path/to/markdown/files
```

## Architecture Overview

The project follows a modular, dependency-injection based architecture with clear separation of concerns:

```
md_reader/
├── interfaces.py      # Protocol definitions and contracts
├── container.py       # Dependency injection container
├── exceptions.py      # Custom exception hierarchy
├── logger.py          # Centralized logging system
├── validators.py      # Input and path validation
├── cache.py          # Multi-tier caching system
├── loader.py         # Basic markdown file loading
├── enhanced_loader.py # Advanced loading with lazy evaluation
├── toc.py            # Table of contents building
├── viewer.py         # Interactive CLI viewer
├── tui.py            # Textual UI interface
└── cli.py            # Command-line interface
```

## Core Components

### 1. Validation System (`validators.py`)

Provides secure validation for paths, files, and user input.

#### PathValidator

```python
from md_reader.validators import PathValidator

# Validate and secure file paths
safe_path = PathValidator.validate_path("/some/path/file.md")
markdown_file = PathValidator.validate_markdown_file("document.md")
directory = PathValidator.validate_directory_path("/docs")

# Check if file is markdown
is_md = PathValidator.is_markdown_file(Path("test.md"))  # True
```

**Security Features:**
- Path traversal attack prevention
- Maximum path length validation
- Dangerous character filtering
- File permission checking

#### InputValidator

```python
from md_reader.validators import InputValidator

# Validate search queries
clean_query = InputValidator.validate_search_query("user search term")

# Validate user selections
selection = InputValidator.validate_selection_input("3", max_options=10)
```

#### FileContentValidator

```python
from md_reader.validators import FileContentValidator

# Validate file size and encoding
FileContentValidator.validate_file_size(file_path)
encoding = FileContentValidator.validate_text_encoding(file_path)
```

### 2. Exception Handling (`exceptions.py`)

Comprehensive exception hierarchy for precise error handling.

```python
from md_reader.exceptions import (
    MdReaderError,           # Base exception
    FileLoadError,           # File operation errors
    PathValidationError,     # Path security errors
    MarkdownParsingError,    # Parsing errors
    UserInputError,          # User input validation errors
    TocBuildError,          # TOC building errors
    ConfigurationError,      # Configuration errors
    CacheError              # Caching errors
)

try:
    content = loader.load_single_file("document.md")
except FileLoadError as e:
    print(f"Failed to load file: {e.message}")
    if e.details:
        print(f"Details: {e.details}")
```

### 3. Logging System (`logger.py`)

Centralized logging with decorators and context managers.

```python
from md_reader.logger import setup_logging, get_logger, handle_exceptions

# Setup logging
setup_logging(level="INFO", log_file="app.log")
logger = get_logger("my_module")

# Use decorators for automatic error handling
@handle_exceptions(FileLoadError, reraise=True)
def load_file(path):
    # Your code here
    pass

# Use context managers
from md_reader.logger import error_context
with error_context("loading configuration"):
    # Your code here
    pass
```

### 4. Caching System (`cache.py`)

Multi-tier caching with memory, file, and smart caching options.

#### Memory Cache

```python
from md_reader.cache import MemoryCache

cache = MemoryCache(max_size=1000, default_ttl=3600)
cache.set("key", "value", ttl=60)
value = cache.get("key")
stats = cache.get_stats()
```

#### File Cache

```python
from md_reader.cache import FileBasedCache

cache = FileBasedCache(cache_dir=Path(".cache"), max_size=100)
cache.set("key", complex_data)
data = cache.get("key")
```

#### Tiered Cache

```python
from md_reader.cache import create_tiered_cache

cache = create_tiered_cache(
    memory_size=100,
    cache_dir=".cache",
    file_cache_size=1000
)
```

#### Smart File Cache

```python
from md_reader.cache import SmartFileCache, create_smart_file_cache

# Automatically handles file modification detection
smart_cache = create_smart_file_cache(cache_type="tiered")

# Cache file content with timestamp validation
smart_cache.set_file_content(file_path, content)
cached_content = smart_cache.get_file_content(file_path)  # None if modified

# Cache TOC data
files_hash = smart_cache.compute_files_hash(files)
smart_cache.set_toc(files_hash, toc_data)
```

### 5. Enhanced Loading (`enhanced_loader.py`)

Advanced file loading with lazy evaluation and parallel processing.

```python
from md_reader.enhanced_loader import EnhancedMarkdownLoader, LoadingOptions

# Configure loading options
options = LoadingOptions(
    max_workers=4,
    enable_cache=True,
    cache_type="tiered",
    preload_headers_only=True,
    max_file_size=10 * 1024 * 1024,
    include_patterns=["*.md", "*.markdown"],
    exclude_patterns=["**/node_modules/**"]
)

loader = EnhancedMarkdownLoader(options)

# Lazy loading - files loaded on demand
lazy_files = loader.load_markdown_files_lazy("/path/to/docs")

# Force loading if needed
files = loader.load_markdown_files("/path/to/docs", force_load=True)

# Get loading statistics
stats = loader.get_stats()
memory_usage = loader.get_memory_usage()
```

**Lazy File Content:**

```python
# Files are loaded on-demand
lazy_file = lazy_files[file_path]

# Access content (triggers loading if needed)
content = lazy_file.content
lines = lazy_file[10:20]  # Get specific lines

# Check if loaded
if lazy_file.is_loaded:
    print("File is in memory")

# Unload to save memory
lazy_file.unload()
```

### 6. Table of Contents Building (`toc.py`)

Robust TOC building with validation and error handling.

```python
from md_reader.toc import TocBuilder

builder = TocBuilder(max_header_level=6)

# Parse headers from lines
headers = builder.parse_headers_from_lines(file_lines, file_path)

# Build complete TOC
toc = builder.build_toc(files_dict)

# Validate TOC structure
is_valid = builder.validate_toc_structure(toc)

# Get statistics
stats = builder.get_stats()
```

### 7. Dependency Injection (`container.py`)

Enterprise-grade dependency injection system.

```python
from md_reader.container import DependencyContainer, LifetimeScope
from md_reader.interfaces import IFileLoader, ITOCBuilder

# Create container
container = DependencyContainer()

# Register dependencies
container.register(IFileLoader, MarkdownLoader, LifetimeScope.SINGLETON)
container.register(ITOCBuilder, TocBuilder, LifetimeScope.TRANSIENT)

# Register with factory
container.register_factory(
    ICache, 
    lambda c: create_smart_file_cache("tiered"),
    LifetimeScope.SINGLETON
)

# Resolve dependencies
loader = container.resolve(IFileLoader)
builder = container.resolve(ITOCBuilder)

# Use scoped containers
with dependency_scope(container) as scope:
    scoped_service = scope.resolve(ISomeService)
    # Service disposed when scope exits
```

**Auto-registration with decorators:**

```python
from md_reader.container import injectable, singleton

@singleton(IFileLoader)
class MyFileLoader:
    def __init__(self, validator: IValidator, logger: ILogger):
        # Dependencies injected automatically
        pass
```

## Advanced Usage Examples

### Custom Validation Pipeline

```python
from md_reader.validators import PathValidator, InputValidator
from md_reader.exceptions import PathValidationError, UserInputError

def secure_file_processor(user_input: str) -> Optional[List[str]]:
    try:
        # Validate user input
        clean_path = InputValidator.validate_search_query(user_input.strip())
        
        # Validate and secure path
        safe_path = PathValidator.validate_markdown_file(clean_path)
        
        # Load file securely
        loader = EnhancedMarkdownLoader()
        content = loader.load_single_file(safe_path)
        
        return content
        
    except (PathValidationError, UserInputError) as e:
        logger.error(f"Validation failed: {e.message}")
        return None
```

### Performance-Optimized Loading

```python
from md_reader.enhanced_loader import EnhancedMarkdownLoader, LoadingOptions
from md_reader.cache import create_smart_file_cache

# Setup high-performance configuration
options = LoadingOptions(
    max_workers=8,  # Use more threads
    chunk_size=20,  # Larger chunks
    enable_cache=True,
    cache_type="tiered",
    preload_headers_only=True,  # Fast startup
    watch_for_changes=True  # Auto-refresh
)

loader = EnhancedMarkdownLoader(options)

# Load large documentation set
docs_path = "/large/documentation/project"
lazy_files = loader.load_markdown_files_lazy(docs_path)

# Preload frequently accessed files
important_files = [path for path in lazy_files.keys() if "important" in str(path)]
loader.preload_files(important_files)

# Monitor memory usage
memory_stats = loader.get_memory_usage()
if memory_stats['memory_efficiency'] < 0.7:
    # Unload less important files
    loader.unload_files(less_important_files)
```

### Custom Caching Strategy

```python
from md_reader.cache import TieredCache, MemoryCache, FileBasedCache

# Create custom cache configuration
l1_cache = MemoryCache(max_size=200, default_ttl=1800)  # 30 min TTL
l2_cache = FileBasedCache(cache_dir=Path("~/.md_reader_cache"), max_size=2000)

custom_cache = TieredCache(
    l1_cache=l1_cache,
    l2_cache=l2_cache,
    promote_on_l2_hit=True
)

# Use with smart file cache
smart_cache = SmartFileCache(custom_cache)

# Cache with custom logic
def cache_with_priority(file_path: Path, content: List[str], priority: str):
    base_ttl = 3600  # 1 hour
    
    ttl_map = {
        "high": base_ttl * 24,     # 24 hours
        "medium": base_ttl * 6,    # 6 hours
        "low": base_ttl            # 1 hour
    }
    
    ttl = ttl_map.get(priority, base_ttl)
    smart_cache.cache.set(f"content:{file_path}", content, ttl=ttl)
```

### Error Handling Best Practices

```python
from md_reader.logger import get_logger, handle_exceptions, error_context
from md_reader.exceptions import MdReaderError

logger = get_logger("my_app")

@handle_exceptions((FileLoadError, PathValidationError), reraise=False, default_return=[])
def safe_load_with_fallback(file_paths: List[Path]) -> List[str]:
    """Load files with comprehensive error handling."""
    all_content = []
    
    for file_path in file_paths:
        try:
            with error_context(f"processing {file_path}"):
                # Validate path
                safe_path = PathValidator.validate_markdown_file(file_path)
                
                # Load content
                loader = MarkdownLoader()
                content = loader.load_single_file(safe_path)
                all_content.extend(content)
                
        except MdReaderError as e:
            logger.warning(f"Skipping {file_path}: {e.message}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error with {file_path}: {str(e)}")
            continue
    
    return all_content
```

## Configuration

### Environment Variables

```bash
# Logging configuration
MD_READER_LOG_LEVEL=INFO
MD_READER_LOG_FILE=/var/log/md_reader.log

# Cache configuration
MD_READER_CACHE_DIR=/tmp/md_reader_cache
MD_READER_CACHE_TYPE=tiered
MD_READER_CACHE_SIZE=1000

# Performance tuning
MD_READER_MAX_WORKERS=4
MD_READER_MAX_FILE_SIZE=10485760
```

### Configuration File

Create `~/.md_reader/config.toml`:

```toml
[logging]
level = "INFO"
format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"

[cache]
type = "tiered"
memory_size = 200
file_cache_size = 2000
cache_dir = "~/.md_reader/cache"
default_ttl = 3600

[loading]
max_workers = 4
chunk_size = 10
max_file_size = 10485760
include_patterns = ["*.md", "*.markdown", "*.mdown"]
exclude_patterns = ["**/node_modules/**", "**/build/**"]

[validation]
max_path_length = 260
max_input_length = 1000
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit          # Unit tests
pytest -m integration   # Integration tests
pytest -m security      # Security tests
pytest -m performance   # Performance tests

# Run with coverage
pytest --cov=md_reader --cov-report=html

# Run security-specific tests
pytest test_security_improvements.py -v
```

### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component interaction testing
- **Security Tests**: Validation of security measures
- **Performance Tests**: Speed and memory usage testing
- **Slow Tests**: Long-running comprehensive tests

## Performance Metrics

### Benchmarks

Typical performance metrics on modern hardware:

- **File Loading**: 1000 markdown files in < 2 seconds
- **TOC Building**: 10,000 headers in < 1 second
- **Cache Hit Rate**: > 90% for repeated operations
- **Memory Efficiency**: < 50MB for 1000+ files with lazy loading
- **Search Performance**: < 100ms for 10,000+ indexed headers

### Optimization Tips

1. **Use Lazy Loading**: For large documentation sets
2. **Enable Caching**: Especially for frequently accessed files
3. **Tune Worker Count**: Match to your CPU cores
4. **Monitor Memory**: Use `get_memory_usage()` to track efficiency
5. **Preload Critical Files**: Load important files proactively

## Security Considerations

### Built-in Security Features

1. **Path Traversal Protection**: Prevents access outside allowed directories
2. **Input Sanitization**: Cleans dangerous characters from user input
3. **File Size Limits**: Prevents DoS attacks via large files
4. **Encoding Validation**: Safe handling of various text encodings
5. **Permission Checking**: Validates file access permissions

### Security Best Practices

```python
# Always validate user input
user_path = input("Enter file path: ")
try:
    safe_path = PathValidator.validate_markdown_file(user_path)
except PathValidationError:
    print("Invalid or unsafe path")
    return

# Use error boundaries
try:
    content = load_potentially_unsafe_file(path)
except MdReaderError as e:
    logger.warning(f"Security validation failed: {e.message}")
    # Handle gracefully
```

## Migration Guide

### From Version 0.1.x to 0.2.x

The enhanced version maintains backward compatibility while adding new features:

```python
# Old API still works
from md_reader.loader import load_markdown_files
from md_reader.toc import build_toc

files = load_markdown_files(Path("/docs"))
toc = build_toc(files)

# New enhanced API provides additional features
from md_reader.enhanced_loader import EnhancedMarkdownLoader

loader = EnhancedMarkdownLoader()
lazy_files = loader.load_markdown_files_lazy("/docs")
```

## Troubleshooting

### Common Issues

**Large Memory Usage:**
```python
# Enable lazy loading
options = LoadingOptions(preload_headers_only=True)
loader = EnhancedMarkdownLoader(options)

# Monitor and manage memory
memory_stats = loader.get_memory_usage()
if memory_stats['loaded_files'] > 100:
    loader.unload_files(less_important_files)
```

**Slow Loading:**
```python
# Increase worker count
options = LoadingOptions(max_workers=8, chunk_size=20)

# Enable caching
options.enable_cache = True
options.cache_type = "tiered"
```

**Cache Issues:**
```python
# Clear problematic cache
loader.invalidate_cache()

# Or disable caching temporarily
options.enable_cache = False
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Project Status**: ✅ Production Ready | Version: 0.2.0 | Test Coverage: 80%+