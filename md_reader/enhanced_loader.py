"""
Enhanced loader with lazy loading and caching capabilities.

This module provides optimized loading strategies for large markdown projects,
with intelligent caching and lazy loading to minimize memory usage and
improve startup performance.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Union, Iterator, Generator, Set
from dataclasses import dataclass, field
from threading import Lock
import time

from .interfaces import IFileLoader, ITOCBuilder, ICache
from .exceptions import FileLoadError, PathValidationError
from .validators import PathValidator, FileContentValidator
from .cache import SmartFileCache, create_smart_file_cache
from .logger import get_logger, handle_exceptions, performance_context

logger = get_logger("enhanced_loader")


@dataclass
class LoadingOptions:
    """Configuration options for enhanced loading."""
    max_workers: int = 4
    chunk_size: int = 10
    enable_cache: bool = True
    cache_type: str = "tiered"
    cache_dir: Path = field(default_factory=lambda: Path(".cache"))
    preload_headers_only: bool = False
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    include_patterns: List[str] = field(default_factory=lambda: ["*.md", "*.markdown"])
    exclude_patterns: List[str] = field(default_factory=list)
    watch_for_changes: bool = False


@dataclass
class FileMetadata:
    """Metadata about a markdown file."""
    path: Path
    size: int
    mtime: float
    encoding: Optional[str] = None
    is_loaded: bool = False
    header_count: Optional[int] = None
    load_time: Optional[float] = None
    error: Optional[str] = None


class LazyFileContent:
    """Lazy-loaded file content that loads on demand."""
    
    def __init__(
        self, 
        file_path: Path, 
        loader: 'EnhancedMarkdownLoader',
        metadata: FileMetadata
    ):
        self.file_path = file_path
        self.loader = loader
        self.metadata = metadata
        self._content: Optional[List[str]] = None
        self._lock = Lock()
    
    @property
    def content(self) -> List[str]:
        """Get file content, loading if necessary."""
        if self._content is None:
            with self._lock:
                if self._content is None:
                    self._load_content()
        return self._content or []
    
    @property
    def is_loaded(self) -> bool:
        """Check if content is already loaded in memory."""
        return self._content is not None
    
    def _load_content(self) -> None:
        """Load content from file or cache."""
        try:
            start_time = time.time()
            
            # Try cache first if enabled
            if self.loader.cache:
                cached_content = self.loader.cache.get_file_content(self.file_path)
                if cached_content is not None:
                    self._content = cached_content
                    self.metadata.is_loaded = True
                    self.metadata.load_time = time.time() - start_time
                    logger.debug(f"Loaded from cache: {self.file_path}")
                    return
            
            # Load from file
            with performance_context(logger, f"loading {self.file_path}"):
                content = self.loader._load_single_file_sync(self.file_path)
                self._content = content
                self.metadata.is_loaded = True
                self.metadata.load_time = time.time() - start_time
                
                # Cache if enabled
                if self.loader.cache:
                    self.loader.cache.set_file_content(self.file_path, content)
                    
        except Exception as e:
            logger.error(f"Failed to load {self.file_path}: {e}")
            self.metadata.error = str(e)
            self._content = []
    
    def unload(self) -> None:
        """Unload content from memory to save space."""
        with self._lock:
            self._content = None
            self.metadata.is_loaded = False
            logger.debug(f"Unloaded from memory: {self.file_path}")
    
    def __len__(self) -> int:
        """Get number of lines in file."""
        return len(self.content)
    
    def __getitem__(self, key) -> Union[str, List[str]]:
        """Get specific line(s) from file."""
        return self.content[key]
    
    def __iter__(self) -> Iterator[str]:
        """Iterate over file lines."""
        return iter(self.content)


class EnhancedMarkdownLoader(IFileLoader):
    """Enhanced markdown loader with lazy loading and caching."""
    
    def __init__(self, options: Optional[LoadingOptions] = None):
        self.options = options or LoadingOptions()
        self.cache: Optional[SmartFileCache] = None
        self._setup_cache()
        
        self.file_metadata: Dict[Path, FileMetadata] = {}
        self.lazy_files: Dict[Path, LazyFileContent] = {}
        self._stats = {
            'files_discovered': 0,
            'files_loaded': 0,
            'files_cached': 0,
            'cache_hits': 0,
            'total_load_time': 0.0,
            'errors': 0
        }
        self._lock = Lock()
        
        logger.info(f"Enhanced loader initialized with options: {self.options}")
    
    def _setup_cache(self) -> None:
        """Setup caching if enabled."""
        if not self.options.enable_cache:
            return
        
        try:
            cache_config = {
                'memory_size': 100,
                'cache_dir': self.options.cache_dir,
                'file_cache_size': 1000
            }
            
            self.cache = create_smart_file_cache(
                cache_type=self.options.cache_type,
                **cache_config
            )
            logger.info(f"Cache enabled: {self.options.cache_type}")
            
        except Exception as e:
            logger.warning(f"Failed to setup cache: {e}")
            self.options.enable_cache = False
    
    @handle_exceptions((FileLoadError, PathValidationError), reraise=True)
    def load_single_file(self, file_path: Union[str, Path]) -> List[str]:
        """Load a single file (synchronous interface)."""
        validated_path = PathValidator.validate_markdown_file(file_path)
        
        # Check if already loaded
        if validated_path in self.lazy_files:
            lazy_file = self.lazy_files[validated_path]
            return lazy_file.content
        
        # Load and create lazy wrapper
        content = self._load_single_file_sync(validated_path)
        metadata = self._create_file_metadata(validated_path)
        lazy_file = LazyFileContent(validated_path, self, metadata)
        lazy_file._content = content  # Already loaded
        
        self.lazy_files[validated_path] = lazy_file
        self.file_metadata[validated_path] = metadata
        
        return content
    
    def load_markdown_files(self, base: Union[str, Path]) -> Dict[Path, List[str]]:
        """Load markdown files (synchronous interface for compatibility)."""
        return self.load_markdown_files_lazy(base, force_load=True)
    
    def load_markdown_files_lazy(
        self, 
        base: Union[str, Path], 
        force_load: bool = False
    ) -> Dict[Path, Union[List[str], LazyFileContent]]:
        """
        Load markdown files with lazy loading support.
        
        Args:
            base: Base path to load from
            force_load: If True, load all content immediately
            
        Returns:
            Dictionary mapping paths to content (list or lazy loader)
        """
        base_path = PathValidator.validate_path(base, must_exist=True)
        
        with performance_context(logger, f"discovering files in {base_path}"):
            file_paths = self._discover_files(base_path)
        
        logger.info(f"Discovered {len(file_paths)} markdown files")
        self._stats['files_discovered'] = len(file_paths)
        
        if not file_paths:
            return {}
        
        # Create metadata for all files
        with performance_context(logger, "creating file metadata"):
            self._create_metadata_for_files(file_paths)
        
        # Load files based on options
        if force_load or not self.options.preload_headers_only:
            return self._load_files_parallel(file_paths, force_content_load=force_load)
        else:
            return self._create_lazy_files(file_paths)
    
    def _discover_files(self, base_path: Path) -> List[Path]:
        """Discover markdown files in base path."""
        files = []
        
        if base_path.is_file():
            if PathValidator.is_markdown_file(base_path):
                files.append(base_path)
        else:
            # Search for files matching patterns
            for pattern in self.options.include_patterns:
                files.extend(base_path.rglob(pattern))
            
            # Filter out excluded patterns
            if self.options.exclude_patterns:
                filtered_files = []
                for file_path in files:
                    exclude = False
                    for exclude_pattern in self.options.exclude_patterns:
                        if file_path.match(exclude_pattern):
                            exclude = True
                            break
                    if not exclude:
                        filtered_files.append(file_path)
                files = filtered_files
            
            # Filter markdown files only
            files = [f for f in files if f.is_file() and PathValidator.is_markdown_file(f)]
        
        return sorted(files)
    
    def _create_metadata_for_files(self, file_paths: List[Path]) -> None:
        """Create metadata for discovered files."""
        for file_path in file_paths:
            if file_path not in self.file_metadata:
                self.file_metadata[file_path] = self._create_file_metadata(file_path)
    
    def _create_file_metadata(self, file_path: Path) -> FileMetadata:
        """Create metadata for a single file."""
        try:
            stat = file_path.stat()
            return FileMetadata(
                path=file_path,
                size=stat.st_size,
                mtime=stat.st_mtime
            )
        except OSError as e:
            logger.error(f"Failed to get metadata for {file_path}: {e}")
            return FileMetadata(
                path=file_path,
                size=0,
                mtime=0,
                error=str(e)
            )
    
    def _load_files_parallel(
        self, 
        file_paths: List[Path], 
        force_content_load: bool = False
    ) -> Dict[Path, Union[List[str], LazyFileContent]]:
        """Load files in parallel using thread pool."""
        results = {}
        
        # Split into chunks for better progress tracking
        chunks = [
            file_paths[i:i + self.options.chunk_size] 
            for i in range(0, len(file_paths), self.options.chunk_size)
        ]
        
        with ThreadPoolExecutor(max_workers=self.options.max_workers) as executor:
            for chunk in chunks:
                # Submit chunk for processing
                future_to_path = {
                    executor.submit(self._process_file_for_loading, path, force_content_load): path
                    for path in chunk
                }
                
                # Collect results
                for future in as_completed(future_to_path):
                    path = future_to_path[future]
                    try:
                        result = future.result()
                        if result is not None:
                            results[path] = result
                    except Exception as e:
                        logger.error(f"Failed to process {path}: {e}")
                        self._stats['errors'] += 1
        
        return results
    
    def _process_file_for_loading(
        self, 
        file_path: Path, 
        force_content_load: bool
    ) -> Optional[Union[List[str], LazyFileContent]]:
        """Process a single file for loading."""
        try:
            # Validate file
            PathValidator.validate_markdown_file(file_path)
            FileContentValidator.validate_file_size(file_path)
            
            metadata = self.file_metadata.get(file_path)
            if not metadata:
                metadata = self._create_file_metadata(file_path)
                self.file_metadata[file_path] = metadata
            
            # Create lazy file
            lazy_file = LazyFileContent(file_path, self, metadata)
            self.lazy_files[file_path] = lazy_file
            
            if force_content_load:
                # Force load content and return it
                content = lazy_file.content
                self._stats['files_loaded'] += 1
                return content
            else:
                # Return lazy loader
                return lazy_file
                
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")
            self._stats['errors'] += 1
            return None
    
    def _create_lazy_files(self, file_paths: List[Path]) -> Dict[Path, LazyFileContent]:
        """Create lazy file loaders without loading content."""
        results = {}
        
        for file_path in file_paths:
            try:
                metadata = self.file_metadata.get(file_path)
                if not metadata:
                    metadata = self._create_file_metadata(file_path)
                    self.file_metadata[file_path] = metadata
                
                lazy_file = LazyFileContent(file_path, self, metadata)
                self.lazy_files[file_path] = lazy_file
                results[file_path] = lazy_file
                
            except Exception as e:
                logger.error(f"Failed to create lazy file for {file_path}: {e}")
                self._stats['errors'] += 1
        
        return results
    
    def _load_single_file_sync(self, file_path: Path) -> List[str]:
        """Load a single file synchronously."""
        # Validate file
        PathValidator.validate_markdown_file(file_path)
        FileContentValidator.validate_file_size(file_path)
        
        # Determine encoding
        encoding = FileContentValidator.validate_text_encoding(file_path)
        
        try:
            content = file_path.read_text(encoding=encoding)
            lines = content.splitlines()
            
            # Update stats
            with self._lock:
                self._stats['files_loaded'] += 1
            
            return lines
            
        except (OSError, UnicodeDecodeError) as e:
            raise FileLoadError(
                str(file_path),
                f"Failed to read file: {str(e)}"
            )
    
    def get_loaded_files(self) -> Dict[Path, LazyFileContent]:
        """Get all loaded files."""
        return self.lazy_files.copy()
    
    def get_file_metadata(self, file_path: Path) -> Optional[FileMetadata]:
        """Get metadata for a specific file."""
        return self.file_metadata.get(file_path)
    
    def preload_files(self, file_paths: List[Path]) -> None:
        """Preload specific files into memory."""
        for file_path in file_paths:
            if file_path in self.lazy_files:
                lazy_file = self.lazy_files[file_path]
                if not lazy_file.is_loaded:
                    _ = lazy_file.content  # Trigger loading
                    logger.debug(f"Preloaded: {file_path}")
    
    def unload_files(self, file_paths: Optional[List[Path]] = None) -> None:
        """Unload files from memory to save space."""
        if file_paths is None:
            file_paths = list(self.lazy_files.keys())
        
        for file_path in file_paths:
            if file_path in self.lazy_files:
                self.lazy_files[file_path].unload()
    
    def get_memory_usage(self) -> Dict[str, int]:
        """Get memory usage statistics."""
        loaded_count = sum(1 for lf in self.lazy_files.values() if lf.is_loaded)
        total_count = len(self.lazy_files)
        
        return {
            'total_files': total_count,
            'loaded_files': loaded_count,
            'unloaded_files': total_count - loaded_count,
            'memory_efficiency': (total_count - loaded_count) / total_count if total_count > 0 else 0
        }
    
    def get_stats(self) -> Dict[str, any]:
        """Get loading statistics."""
        memory_stats = self.get_memory_usage()
        
        return {
            **self._stats,
            **memory_stats,
            'cache_enabled': self.options.enable_cache,
            'options': self.options
        }
    
    def invalidate_cache(self, file_path: Optional[Path] = None) -> None:
        """Invalidate cache for specific file or all files."""
        if not self.cache:
            return
        
        if file_path:
            self.cache.invalidate_file(file_path)
            if file_path in self.lazy_files:
                self.lazy_files[file_path].unload()
        else:
            self.cache.cache.clear()
            self.unload_files()
    
    def refresh_file(self, file_path: Path) -> bool:
        """Refresh a specific file if it has been modified."""
        if file_path not in self.file_metadata:
            return False
        
        try:
            current_mtime = file_path.stat().st_mtime
            stored_mtime = self.file_metadata[file_path].mtime
            
            if current_mtime > stored_mtime:
                # File has been modified
                self.invalidate_cache(file_path)
                self.file_metadata[file_path] = self._create_file_metadata(file_path)
                logger.info(f"File refreshed: {file_path}")
                return True
                
        except OSError as e:
            logger.error(f"Failed to check file modification time {file_path}: {e}")
        
        return False
    
    def watch_for_changes(self) -> Generator[Path, None, None]:
        """
        Watch for file changes and yield modified files.
        Note: This is a simple implementation. For production use,
        consider using a proper file watching library like watchdog.
        """
        if not self.options.watch_for_changes:
            return
        
        while True:
            modified_files = []
            
            for file_path in self.file_metadata.keys():
                if self.refresh_file(file_path):
                    modified_files.append(file_path)
            
            for file_path in modified_files:
                yield file_path
            
            time.sleep(1)  # Check every second


# Factory function for enhanced loader
def create_enhanced_loader(
    max_workers: int = 4,
    enable_cache: bool = True,
    cache_type: str = "tiered",
    preload_headers_only: bool = False,
    **kwargs
) -> EnhancedMarkdownLoader:
    """Create an enhanced markdown loader with specified options."""
    options = LoadingOptions(
        max_workers=max_workers,
        enable_cache=enable_cache,
        cache_type=cache_type,
        preload_headers_only=preload_headers_only,
        **kwargs
    )
    
    return EnhancedMarkdownLoader(options)