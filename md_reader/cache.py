"""
Caching system for md_reader.

This module provides various caching implementations to improve performance
by avoiding redundant file loading and TOC building operations.
"""

import time
import hashlib
import pickle
import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, Dict, List, Tuple, Union
from dataclasses import dataclass
from collections import OrderedDict

from .interfaces import ICache
from .exceptions import CacheError
from .logger import get_logger

logger = get_logger("cache")


@dataclass
class CacheEntry:
    """Represents a cache entry with metadata."""
    value: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    ttl: Optional[int] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if the entry is expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    @property
    def age(self) -> float:
        """Get the age of the entry in seconds."""
        return time.time() - self.created_at
    
    def touch(self) -> None:
        """Update access time and count."""
        self.last_accessed = time.time()
        self.access_count += 1


class MemoryCache(ICache):
    """In-memory cache implementation with LRU eviction and TTL support."""
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[int] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expirations': 0
        }
        logger.debug(f"Memory cache initialized with max_size={max_size}, default_ttl={default_ttl}")
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        with self._lock:
            if key not in self._cache:
                self._stats['misses'] += 1
                logger.debug(f"Cache miss for key: {key}")
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry.is_expired:
                del self._cache[key]
                self._stats['expirations'] += 1
                self._stats['misses'] += 1
                logger.debug(f"Cache entry expired for key: {key}")
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            entry.touch()
            self._stats['hits'] += 1
            
            logger.debug(f"Cache hit for key: {key} (age: {entry.age:.2f}s, access_count: {entry.access_count})")
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value in cache with optional TTL."""
        with self._lock:
            # Use provided TTL or default
            effective_ttl = ttl if ttl is not None else self.default_ttl
            
            # Create cache entry
            entry = CacheEntry(
                value=value,
                created_at=time.time(),
                last_accessed=time.time(),
                ttl=effective_ttl
            )
            
            # Add to cache
            self._cache[key] = entry
            self._cache.move_to_end(key)
            
            # Evict if necessary
            self._evict_if_needed()
            
            logger.debug(f"Cache set for key: {key} (ttl: {effective_ttl})")
    
    def invalidate(self, key: str) -> None:
        """Remove value from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Cache invalidated for key: {key}")
    
    def clear(self) -> None:
        """Clear entire cache."""
        with self._lock:
            self._cache.clear()
            self._stats = {
                'hits': 0,
                'misses': 0,
                'evictions': 0,
                'expirations': 0
            }
            logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = self._stats['hits'] / total_requests if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hit_rate': hit_rate,
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'evictions': self._stats['evictions'],
                'expirations': self._stats['expirations']
            }
    
    def _evict_if_needed(self) -> None:
        """Evict oldest entries if cache is full."""
        while len(self._cache) > self.max_size:
            # Remove oldest entry (first in OrderedDict)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            self._stats['evictions'] += 1
            logger.debug(f"Cache entry evicted: {oldest_key}")


class FileBasedCache(ICache):
    """File-based cache implementation for persistence across sessions."""
    
    def __init__(self, cache_dir: Path, max_size: int = 100):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size = max_size
        self._lock = threading.RLock()
        logger.debug(f"File-based cache initialized at {self.cache_dir}")
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from file cache."""
        with self._lock:
            cache_file = self._get_cache_file(key)
            
            if not cache_file.exists():
                return None
            
            try:
                with open(cache_file, 'rb') as f:
                    entry = pickle.load(f)
                
                if entry.is_expired:
                    cache_file.unlink(missing_ok=True)
                    logger.debug(f"File cache entry expired: {key}")
                    return None
                
                entry.touch()
                
                # Update access time in file
                with open(cache_file, 'wb') as f:
                    pickle.dump(entry, f)
                
                logger.debug(f"File cache hit: {key}")
                return entry.value
                
            except (pickle.PickleError, OSError) as e:
                logger.warning(f"Error reading cache file {cache_file}: {e}")
                cache_file.unlink(missing_ok=True)
                return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value in file cache."""
        with self._lock:
            cache_file = self._get_cache_file(key)
            
            entry = CacheEntry(
                value=value,
                created_at=time.time(),
                last_accessed=time.time(),
                ttl=ttl
            )
            
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(entry, f)
                
                self._cleanup_if_needed()
                logger.debug(f"File cache set: {key}")
                
            except (pickle.PickleError, OSError) as e:
                logger.error(f"Error writing cache file {cache_file}: {e}")
                raise CacheError("write", f"Failed to write cache file: {e}")
    
    def invalidate(self, key: str) -> None:
        """Remove value from file cache."""
        with self._lock:
            cache_file = self._get_cache_file(key)
            cache_file.unlink(missing_ok=True)
            logger.debug(f"File cache invalidated: {key}")
    
    def clear(self) -> None:
        """Clear entire file cache."""
        with self._lock:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink(missing_ok=True)
            logger.info("File cache cleared")
    
    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for key."""
        # Hash the key to create a safe filename
        hashed_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hashed_key}.cache"
    
    def _cleanup_if_needed(self) -> None:
        """Remove old cache files if needed."""
        cache_files = list(self.cache_dir.glob("*.cache"))
        
        if len(cache_files) <= self.max_size:
            return
        
        # Sort by modification time and remove oldest
        cache_files.sort(key=lambda f: f.stat().st_mtime)
        files_to_remove = cache_files[:-self.max_size]
        
        for cache_file in files_to_remove:
            cache_file.unlink(missing_ok=True)
            logger.debug(f"Old cache file removed: {cache_file}")


class TieredCache(ICache):
    """Tiered cache implementation with L1 (memory) and L2 (file) caches."""
    
    def __init__(
        self, 
        l1_cache: ICache, 
        l2_cache: ICache,
        promote_on_l2_hit: bool = True
    ):
        self.l1_cache = l1_cache
        self.l2_cache = l2_cache
        self.promote_on_l2_hit = promote_on_l2_hit
        logger.debug("Tiered cache initialized")
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from tiered cache."""
        # Try L1 cache first
        value = self.l1_cache.get(key)
        if value is not None:
            logger.debug(f"Tiered cache L1 hit: {key}")
            return value
        
        # Try L2 cache
        value = self.l2_cache.get(key)
        if value is not None:
            logger.debug(f"Tiered cache L2 hit: {key}")
            # Promote to L1 if configured
            if self.promote_on_l2_hit:
                self.l1_cache.set(key, value)
            return value
        
        logger.debug(f"Tiered cache miss: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value in both cache levels."""
        self.l1_cache.set(key, value, ttl)
        self.l2_cache.set(key, value, ttl)
        logger.debug(f"Tiered cache set: {key}")
    
    def invalidate(self, key: str) -> None:
        """Remove value from both cache levels."""
        self.l1_cache.invalidate(key)
        self.l2_cache.invalidate(key)
        logger.debug(f"Tiered cache invalidated: {key}")
    
    def clear(self) -> None:
        """Clear both cache levels."""
        self.l1_cache.clear()
        self.l2_cache.clear()
        logger.info("Tiered cache cleared")


class SmartFileCache:
    """Smart file cache that handles markdown files and TOC caching with invalidation."""
    
    def __init__(self, cache: ICache):
        self.cache = cache
        self._file_timestamps: Dict[str, float] = {}
        self._lock = threading.RLock()
        logger.debug("Smart file cache initialized")
    
    def get_file_content(self, file_path: Path) -> Optional[List[str]]:
        """Get cached file content if not modified."""
        with self._lock:
            file_key = f"file_content:{file_path}"
            timestamp_key = f"file_timestamp:{file_path}"
            
            try:
                current_mtime = file_path.stat().st_mtime
            except OSError:
                # File doesn't exist or can't be accessed
                return None
            
            # Check if we have cached content
            cached_content = self.cache.get(file_key)
            cached_timestamp = self.cache.get(timestamp_key)
            
            if cached_content is not None and cached_timestamp is not None:
                if cached_timestamp == current_mtime:
                    logger.debug(f"File cache hit: {file_path}")
                    return cached_content
                else:
                    # File modified, invalidate cache
                    self.cache.invalidate(file_key)
                    self.cache.invalidate(timestamp_key)
                    logger.debug(f"File modified, cache invalidated: {file_path}")
            
            return None
    
    def set_file_content(self, file_path: Path, content: List[str]) -> None:
        """Cache file content with timestamp."""
        with self._lock:
            try:
                current_mtime = file_path.stat().st_mtime
                
                file_key = f"file_content:{file_path}"
                timestamp_key = f"file_timestamp:{file_path}"
                
                self.cache.set(file_key, content)
                self.cache.set(timestamp_key, current_mtime)
                
                logger.debug(f"File cached: {file_path}")
                
            except OSError as e:
                logger.warning(f"Could not cache file {file_path}: {e}")
    
    def get_toc(self, files_hash: str) -> Optional[Dict[Path, List[Tuple[str, int, int]]]]:
        """Get cached TOC for a set of files."""
        toc_key = f"toc:{files_hash}"
        cached_toc = self.cache.get(toc_key)
        
        if cached_toc is not None:
            logger.debug(f"TOC cache hit: {files_hash}")
            return cached_toc
        
        return None
    
    def set_toc(self, files_hash: str, toc: Dict[Path, List[Tuple[str, int, int]]]) -> None:
        """Cache TOC for a set of files."""
        toc_key = f"toc:{files_hash}"
        self.cache.set(toc_key, toc)
        logger.debug(f"TOC cached: {files_hash}")
    
    def compute_files_hash(self, files: Dict[Path, List[str]]) -> str:
        """Compute hash for a collection of files based on paths and modification times."""
        hash_input = []
        
        for file_path in sorted(files.keys()):
            try:
                mtime = file_path.stat().st_mtime
                hash_input.append(f"{file_path}:{mtime}")
            except OSError:
                # File doesn't exist, use path only
                hash_input.append(str(file_path))
        
        return hashlib.md5(":".join(hash_input).encode()).hexdigest()
    
    def invalidate_file(self, file_path: Path) -> None:
        """Invalidate cache entries for a specific file."""
        with self._lock:
            file_key = f"file_content:{file_path}"
            timestamp_key = f"file_timestamp:{file_path}"
            
            self.cache.invalidate(file_key)
            self.cache.invalidate(timestamp_key)
            
            logger.debug(f"File cache invalidated: {file_path}")


# Factory functions for common cache configurations

def create_memory_cache(max_size: int = 1000, default_ttl: Optional[int] = None) -> MemoryCache:
    """Create a memory cache with specified configuration."""
    return MemoryCache(max_size=max_size, default_ttl=default_ttl)


def create_file_cache(cache_dir: Union[str, Path], max_size: int = 100) -> FileBasedCache:
    """Create a file-based cache with specified configuration."""
    return FileBasedCache(cache_dir=Path(cache_dir), max_size=max_size)


def create_tiered_cache(
    memory_size: int = 100,
    cache_dir: Union[str, Path] = ".cache",
    file_cache_size: int = 1000
) -> TieredCache:
    """Create a tiered cache with memory and file levels."""
    l1_cache = create_memory_cache(max_size=memory_size, default_ttl=3600)  # 1 hour TTL
    l2_cache = create_file_cache(cache_dir=cache_dir, max_size=file_cache_size)
    
    return TieredCache(l1_cache=l1_cache, l2_cache=l2_cache)


def create_smart_file_cache(
    cache_type: str = "tiered",
    **kwargs
) -> SmartFileCache:
    """Create a smart file cache with specified backend."""
    if cache_type == "memory":
        cache = create_memory_cache(**kwargs)
    elif cache_type == "file":
        cache = create_file_cache(**kwargs)
    elif cache_type == "tiered":
        cache = create_tiered_cache(**kwargs)
    else:
        raise ValueError(f"Unknown cache type: {cache_type}")
    
    return SmartFileCache(cache=cache)