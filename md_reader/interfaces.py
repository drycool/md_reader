"""
Interfaces and protocols for md_reader dependency injection.

This module defines the contracts that various components should implement,
enabling better testability, modularity, and extensibility.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Tuple, Protocol, Union, Optional, Any
from contextlib import contextmanager


# Type aliases for better readability
FileContent = List[str]
HeaderInfo = Tuple[str, int, int]  # (title, level, line_number)
TOCData = Dict[Path, List[HeaderInfo]]
FileCollection = Dict[Path, FileContent]


class IFileLoader(Protocol):
    """Interface for file loading operations."""
    
    def load_single_file(self, file_path: Union[str, Path]) -> FileContent:
        """Load a single file and return its content as lines."""
        ...
    
    def load_markdown_files(self, base: Union[str, Path]) -> FileCollection:
        """Load all markdown files from a base path."""
        ...
    
    def get_stats(self) -> Dict[str, int]:
        """Get loading statistics."""
        ...


class ITOCBuilder(Protocol):
    """Interface for table of contents building."""
    
    def parse_headers_from_lines(
        self, 
        lines: FileContent, 
        file_path: Optional[Path] = None
    ) -> List[HeaderInfo]:
        """Parse headers from file lines."""
        ...
    
    def build_toc(self, files: FileCollection) -> TOCData:
        """Build table of contents from file collection."""
        ...
    
    def validate_toc_structure(self, toc: TOCData) -> bool:
        """Validate TOC structure integrity."""
        ...


class IValidator(Protocol):
    """Interface for validation operations."""
    
    def validate_path(self, path: Union[str, Path], must_exist: bool = True) -> Path:
        """Validate file system path."""
        ...
    
    def validate_input(self, user_input: str, context: str) -> str:
        """Validate user input."""
        ...


class ICache(Protocol):
    """Interface for caching operations."""
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        ...
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value in cache with optional TTL."""
        ...
    
    def invalidate(self, key: str) -> None:
        """Remove value from cache."""
        ...
    
    def clear(self) -> None:
        """Clear entire cache."""
        ...


class ILogger(Protocol):
    """Interface for logging operations."""
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        ...
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        ...
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        ...
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        ...


class IViewer(Protocol):
    """Interface for content viewing operations."""
    
    def interactive_view(self, toc: TOCData) -> None:
        """Start interactive viewing session."""
        ...
    
    def show_section(self, path: Path, start: int) -> None:
        """Display specific file section."""
        ...


# Abstract base classes for concrete implementations

class BaseFileLoader(ABC):
    """Abstract base class for file loaders."""
    
    def __init__(self, validator: IValidator, logger: ILogger):
        self.validator = validator
        self.logger = logger
        self.loaded_files_count = 0
        self.failed_files_count = 0
    
    @abstractmethod
    def load_single_file(self, file_path: Union[str, Path]) -> FileContent:
        """Load a single file and return its content as lines."""
        pass
    
    @abstractmethod
    def load_markdown_files(self, base: Union[str, Path]) -> FileCollection:
        """Load all markdown files from a base path."""
        pass
    
    def get_stats(self) -> Dict[str, int]:
        """Get loading statistics."""
        return {
            "loaded_files": self.loaded_files_count,
            "failed_files": self.failed_files_count
        }


class BaseTOCBuilder(ABC):
    """Abstract base class for TOC builders."""
    
    def __init__(self, logger: ILogger):
        self.logger = logger
        self.processed_files_count = 0
        self.total_headers_count = 0
    
    @abstractmethod
    def parse_headers_from_lines(
        self, 
        lines: FileContent, 
        file_path: Optional[Path] = None
    ) -> List[HeaderInfo]:
        """Parse headers from file lines."""
        pass
    
    @abstractmethod
    def build_toc(self, files: FileCollection) -> TOCData:
        """Build table of contents from file collection."""
        pass
    
    @abstractmethod
    def validate_toc_structure(self, toc: TOCData) -> bool:
        """Validate TOC structure integrity."""
        pass
    
    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        return {
            "processed_files": self.processed_files_count,
            "total_headers": self.total_headers_count
        }


class BaseViewer(ABC):
    """Abstract base class for viewers."""
    
    def __init__(self, validator: IValidator, logger: ILogger):
        self.validator = validator
        self.logger = logger
    
    @abstractmethod
    def interactive_view(self, toc: TOCData) -> None:
        """Start interactive viewing session."""
        pass
    
    @abstractmethod
    def show_section(self, path: Path, start: int) -> None:
        """Display specific file section."""
        pass


# Service interfaces for dependency injection

class IMarkdownService(Protocol):
    """High-level service interface for markdown operations."""
    
    def load_and_build_toc(self, base_path: Union[str, Path]) -> TOCData:
        """Load files and build TOC in one operation."""
        ...
    
    def search_content(self, query: str, toc: TOCData) -> List[Tuple[str, Path, int]]:
        """Search for content across loaded files."""
        ...
    
    def get_file_content(self, file_path: Path, start: int, end: int) -> str:
        """Get specific content range from file."""
        ...


class IConfigurationService(Protocol):
    """Interface for configuration management."""
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get configuration setting."""
        ...
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set configuration setting."""
        ...
    
    def load_config(self, config_path: Optional[Path] = None) -> None:
        """Load configuration from file."""
        ...


# Dependency injection container interface

class IDependencyContainer(Protocol):
    """Interface for dependency injection container."""
    
    def register(self, interface: type, implementation: type, singleton: bool = False) -> None:
        """Register an implementation for an interface."""
        ...
    
    def register_instance(self, interface: type, instance: Any) -> None:
        """Register a specific instance for an interface."""
        ...
    
    def resolve(self, interface: type) -> Any:
        """Resolve an implementation for an interface."""
        ...
    
    def create_scope(self) -> 'IDependencyContainer':
        """Create a new dependency scope."""
        ...


# Factory interfaces

class IMarkdownReaderFactory(Protocol):
    """Factory interface for creating markdown reader components."""
    
    def create_loader(self) -> IFileLoader:
        """Create a file loader instance."""
        ...
    
    def create_toc_builder(self) -> ITOCBuilder:
        """Create a TOC builder instance."""
        ...
    
    def create_viewer(self) -> IViewer:
        """Create a viewer instance."""
        ...
    
    def create_service(self) -> IMarkdownService:
        """Create a markdown service instance."""
        ...


# Context managers for resource management

@contextmanager
def file_operation_context(logger: ILogger, operation: str):
    """Context manager for file operations with logging."""
    try:
        logger.debug(f"Starting {operation}")
        yield
        logger.debug(f"Completed {operation}")
    except Exception as e:
        logger.error(f"Failed {operation}: {str(e)}")
        raise


@contextmanager
def performance_context(logger: ILogger, operation: str):
    """Context manager for performance monitoring."""
    import time
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        logger.info(f"{operation} completed in {duration:.4f}s")


# Event system interfaces

class IEventPublisher(Protocol):
    """Interface for event publishing."""
    
    def publish(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publish an event."""
        ...


class IEventSubscriber(Protocol):
    """Interface for event subscription."""
    
    def subscribe(self, event_type: str, handler: callable) -> None:
        """Subscribe to an event type."""
        ...
    
    def unsubscribe(self, event_type: str, handler: callable) -> None:
        """Unsubscribe from an event type."""
        ...


# Plugin system interface

class IPlugin(Protocol):
    """Interface for plugins."""
    
    def initialize(self, container: IDependencyContainer) -> None:
        """Initialize the plugin with dependency container."""
        ...
    
    def get_name(self) -> str:
        """Get plugin name."""
        ...
    
    def get_version(self) -> str:
        """Get plugin version."""
        ...


class IPluginManager(Protocol):
    """Interface for plugin management."""
    
    def load_plugin(self, plugin: IPlugin) -> None:
        """Load a plugin."""
        ...
    
    def unload_plugin(self, plugin_name: str) -> None:
        """Unload a plugin."""
        ...
    
    def get_loaded_plugins(self) -> List[str]:
        """Get list of loaded plugin names."""
        ...


# Quality of service interfaces

class IHealthCheck(Protocol):
    """Interface for health checking."""
    
    def check_health(self) -> Dict[str, Any]:
        """Perform health check and return status."""
        ...


class IMetrics(Protocol):
    """Interface for metrics collection."""
    
    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment a counter metric."""
        ...
    
    def set_gauge(self, name: str, value: float) -> None:
        """Set a gauge metric."""
        ...
    
    def record_histogram(self, name: str, value: float) -> None:
        """Record a histogram value."""
        ...
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        ...