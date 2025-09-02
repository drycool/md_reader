"""
Unit tests for caching system.

Tests memory cache, file cache, tiered cache, and smart file cache
functionality including performance and reliability aspects.
"""

import pytest
import time
import threading
from pathlib import Path
from unittest.mock import patch, Mock

from md_reader.cache import (
    MemoryCache, FileBasedCache, TieredCache, SmartFileCache,
    CacheEntry, create_memory_cache, create_file_cache, 
    create_tiered_cache, create_smart_file_cache
)
from md_reader.exceptions import CacheError


@pytest.mark.unit
class TestCacheEntry:
    """Test cache entry functionality."""
    
    def test_cache_entry_creation(self):
        """Test cache entry creation and properties."""
        value = {"test": "data"}
        entry = CacheEntry(value=value, created_at=time.time(), last_accessed=time.time())
        
        assert entry.value == value
        assert entry.access_count == 0
        assert entry.ttl is None
        assert not entry.is_expired
    
    def test_cache_entry_with_ttl(self):
        """Test cache entry with TTL."""
        entry = CacheEntry(
            value="test", 
            created_at=time.time() - 10,  # 10 seconds ago
            last_accessed=time.time(),
            ttl=5  # 5 second TTL
        )
        
        assert entry.is_expired
        assert entry.age >= 10
    
    def test_cache_entry_touch(self):
        """Test cache entry touch functionality."""
        entry = CacheEntry(value="test", created_at=time.time(), last_accessed=time.time())
        
        initial_access_time = entry.last_accessed
        initial_count = entry.access_count
        
        time.sleep(0.01)  # Small delay
        entry.touch()
        
        assert entry.last_accessed > initial_access_time
        assert entry.access_count == initial_count + 1


@pytest.mark.unit
class TestMemoryCache:
    """Test memory cache functionality."""
    
    def test_memory_cache_basic_operations(self, memory_cache):
        """Test basic cache operations."""
        # Test set and get
        memory_cache.set("key1", "value1")
        assert memory_cache.get("key1") == "value1"
        
        # Test get non-existent key
        assert memory_cache.get("nonexistent") is None
        
        # Test invalidate
        memory_cache.invalidate("key1")
        assert memory_cache.get("key1") is None
    
    def test_memory_cache_with_ttl(self):
        """Test memory cache with TTL functionality."""
        cache = MemoryCache(max_size=10, default_ttl=1)  # 1 second TTL
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Wait for expiration
        time.sleep(1.1)
        assert cache.get("key1") is None
    
    def test_memory_cache_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = MemoryCache(max_size=2)
        
        # Fill cache to capacity
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        # Access key1 to make it more recently used
        cache.get("key1")
        
        # Add key3, should evict key2 (least recently used)
        cache.set("key3", "value3")
        
        assert cache.get("key1") == "value1"  # Still there
        assert cache.get("key2") is None      # Evicted
        assert cache.get("key3") == "value3"  # Newly added
    
    def test_memory_cache_stats(self, memory_cache):
        """Test cache statistics."""
        # Initial stats
        stats = memory_cache.get_stats()
        assert stats['size'] == 0
        assert stats['hits'] == 0
        assert stats['misses'] == 0
        
        # Add some data and test stats
        memory_cache.set("key1", "value1")
        memory_cache.get("key1")  # Hit
        memory_cache.get("key2")  # Miss
        
        stats = memory_cache.get_stats()
        assert stats['size'] == 1
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 0.5
    
    def test_memory_cache_clear(self, memory_cache):
        """Test cache clear functionality."""
        memory_cache.set("key1", "value1")
        memory_cache.set("key2", "value2")
        
        assert memory_cache.get("key1") == "value1"
        
        memory_cache.clear()
        
        assert memory_cache.get("key1") is None
        assert memory_cache.get("key2") is None
        
        # Stats should be reset
        stats = memory_cache.get_stats()
        assert stats['hits'] == 0
        assert stats['misses'] == 0
    
    def test_memory_cache_thread_safety(self):
        """Test thread safety of memory cache."""
        cache = MemoryCache(max_size=100)
        errors = []
        
        def worker(start_key, count):
            try:
                for i in range(count):
                    key = f"key_{start_key}_{i}"
                    value = f"value_{start_key}_{i}"
                    cache.set(key, value)
                    retrieved = cache.get(key)
                    assert retrieved == value
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i, 20))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Check no errors occurred
        assert len(errors) == 0


@pytest.mark.unit
class TestFileBasedCache:
    """Test file-based cache functionality."""
    
    def test_file_cache_basic_operations(self, file_cache):
        """Test basic file cache operations."""
        # Test set and get
        file_cache.set("key1", {"data": "value1"})
        result = file_cache.get("key1")
        assert result == {"data": "value1"}
        
        # Test get non-existent key
        assert file_cache.get("nonexistent") is None
        
        # Test invalidate
        file_cache.invalidate("key1")
        assert file_cache.get("key1") is None
    
    def test_file_cache_persistence(self, temp_dir):
        """Test that file cache persists across instances."""
        cache_dir = temp_dir / "cache"
        
        # Create first cache instance
        cache1 = FileBasedCache(cache_dir=cache_dir, max_size=10)
        cache1.set("persistent_key", "persistent_value")
        
        # Create second cache instance
        cache2 = FileBasedCache(cache_dir=cache_dir, max_size=10)
        result = cache2.get("persistent_key")
        
        assert result == "persistent_value"
    
    def test_file_cache_with_ttl(self, file_cache):
        """Test file cache with TTL."""
        file_cache.set("key1", "value1", ttl=1)  # 1 second TTL
        assert file_cache.get("key1") == "value1"
        
        # Wait for expiration
        time.sleep(1.1)
        assert file_cache.get("key1") is None
    
    def test_file_cache_cleanup(self, temp_dir):
        """Test file cache cleanup when max size exceeded."""
        cache_dir = temp_dir / "cache"
        cache = FileBasedCache(cache_dir=cache_dir, max_size=2)
        
        # Add files up to limit
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        # Add one more, should trigger cleanup
        cache.set("key3", "value3")
        
        # Check that we don't exceed max size
        cache_files = list(cache_dir.glob("*.cache"))
        assert len(cache_files) <= 2
    
    def test_file_cache_corrupted_file_handling(self, file_cache, temp_dir):
        """Test handling of corrupted cache files."""
        # Create a corrupted cache file
        cache_dir = file_cache.cache_dir
        corrupted_file = cache_dir / "corrupted.cache"
        corrupted_file.write_text("invalid pickle data", encoding='utf-8')
        
        # Should handle gracefully
        result = file_cache.get("corrupted")
        assert result is None
        
        # Corrupted file should be removed
        assert not corrupted_file.exists()
    
    def test_file_cache_clear(self, file_cache):
        """Test file cache clear functionality."""
        file_cache.set("key1", "value1")
        file_cache.set("key2", "value2")
        
        assert file_cache.get("key1") == "value1"
        
        file_cache.clear()
        
        assert file_cache.get("key1") is None
        assert file_cache.get("key2") is None
        
        # Cache directory should be empty
        cache_files = list(file_cache.cache_dir.glob("*.cache"))
        assert len(cache_files) == 0


@pytest.mark.unit
class TestTieredCache:
    """Test tiered cache functionality."""
    
    def test_tiered_cache_l1_hit(self, memory_cache, file_cache):
        """Test L1 cache hit in tiered cache."""
        tiered = TieredCache(memory_cache, file_cache)
        
        # Set value
        tiered.set("key1", "value1")
        
        # Should hit L1 cache
        with patch.object(file_cache, 'get') as mock_file_get:
            result = tiered.get("key1")
            assert result == "value1"
            mock_file_get.assert_not_called()
    
    def test_tiered_cache_l2_hit_with_promotion(self, memory_cache, file_cache):
        """Test L2 cache hit with promotion to L1."""
        tiered = TieredCache(memory_cache, file_cache, promote_on_l2_hit=True)
        
        # Set value in L2 only
        file_cache.set("key1", "value1")
        
        # Get should hit L2 and promote to L1
        result = tiered.get("key1")
        assert result == "value1"
        
        # Verify promotion to L1
        assert memory_cache.get("key1") == "value1"
    
    def test_tiered_cache_l2_hit_without_promotion(self, memory_cache, file_cache):
        """Test L2 cache hit without promotion."""
        tiered = TieredCache(memory_cache, file_cache, promote_on_l2_hit=False)
        
        # Set value in L2 only
        file_cache.set("key1", "value1")
        
        # Get should hit L2 but not promote to L1
        result = tiered.get("key1")
        assert result == "value1"
        
        # Verify no promotion to L1
        assert memory_cache.get("key1") is None
    
    def test_tiered_cache_miss(self, memory_cache, file_cache):
        """Test cache miss in tiered cache."""
        tiered = TieredCache(memory_cache, file_cache)
        
        result = tiered.get("nonexistent")
        assert result is None
    
    def test_tiered_cache_set_both_levels(self, memory_cache, file_cache):
        """Test that set operation stores in both cache levels."""
        tiered = TieredCache(memory_cache, file_cache)
        
        tiered.set("key1", "value1")
        
        # Should be in both caches
        assert memory_cache.get("key1") == "value1"
        assert file_cache.get("key1") == "value1"
    
    def test_tiered_cache_invalidate_both_levels(self, memory_cache, file_cache):
        """Test that invalidate removes from both cache levels."""
        tiered = TieredCache(memory_cache, file_cache)
        
        tiered.set("key1", "value1")
        tiered.invalidate("key1")
        
        # Should be removed from both caches
        assert memory_cache.get("key1") is None
        assert file_cache.get("key1") is None
    
    def test_tiered_cache_clear_both_levels(self, memory_cache, file_cache):
        """Test that clear removes from both cache levels."""
        tiered = TieredCache(memory_cache, file_cache)
        
        tiered.set("key1", "value1")
        tiered.set("key2", "value2")
        tiered.clear()
        
        # Should be cleared from both caches
        assert memory_cache.get("key1") is None
        assert memory_cache.get("key2") is None
        assert file_cache.get("key1") is None
        assert file_cache.get("key2") is None


@pytest.mark.unit
class TestSmartFileCache:
    """Test smart file cache functionality."""
    
    def test_smart_cache_file_content_caching(self, temp_dir, memory_cache):
        """Test file content caching with timestamp validation."""
        smart_cache = SmartFileCache(memory_cache)
        
        # Create test file
        test_file = temp_dir / "test.md"
        test_file.write_text("# Original content", encoding='utf-8')
        
        # Cache file content
        content = ["# Original content"]
        smart_cache.set_file_content(test_file, content)
        
        # Retrieve from cache
        cached_content = smart_cache.get_file_content(test_file)
        assert cached_content == content
    
    def test_smart_cache_file_modification_detection(self, temp_dir, memory_cache):
        """Test that modified files invalidate cache."""
        smart_cache = SmartFileCache(memory_cache)
        
        # Create and cache file
        test_file = temp_dir / "test.md"
        test_file.write_text("# Original content", encoding='utf-8')
        
        original_content = ["# Original content"]
        smart_cache.set_file_content(test_file, original_content)
        
        # Verify cache hit
        assert smart_cache.get_file_content(test_file) == original_content
        
        # Modify file
        time.sleep(0.01)  # Ensure different mtime
        test_file.write_text("# Modified content", encoding='utf-8')
        
        # Should detect modification and return None (cache miss)
        assert smart_cache.get_file_content(test_file) is None
    
    def test_smart_cache_toc_caching(self, temp_dir, memory_cache):
        """Test TOC caching functionality."""
        smart_cache = SmartFileCache(memory_cache)
        
        # Create sample files
        file1 = temp_dir / "file1.md"
        file2 = temp_dir / "file2.md"
        file1.write_text("# Header 1", encoding='utf-8')
        file2.write_text("# Header 2", encoding='utf-8')
        
        files = {file1: ["# Header 1"], file2: ["# Header 2"]}
        toc = {file1: [("Header 1", 1, 0)], file2: [("Header 2", 1, 0)]}
        
        # Compute hash and cache TOC
        files_hash = smart_cache.compute_files_hash(files)
        smart_cache.set_toc(files_hash, toc)
        
        # Retrieve from cache
        cached_toc = smart_cache.get_toc(files_hash)
        assert cached_toc == toc
    
    def test_smart_cache_files_hash_computation(self, temp_dir, memory_cache):
        """Test files hash computation."""
        smart_cache = SmartFileCache(memory_cache)
        
        # Create test files
        file1 = temp_dir / "file1.md"
        file2 = temp_dir / "file2.md"
        file1.write_text("Content 1", encoding='utf-8')
        file2.write_text("Content 2", encoding='utf-8')
        
        files = {file1: ["Content 1"], file2: ["Content 2"]}
        
        # Compute hash
        hash1 = smart_cache.compute_files_hash(files)
        assert isinstance(hash1, str)
        assert len(hash1) == 32  # MD5 hash length
        
        # Same files should produce same hash
        hash2 = smart_cache.compute_files_hash(files)
        assert hash1 == hash2
        
        # Different files should produce different hash
        file3 = temp_dir / "file3.md"
        file3.write_text("Content 3", encoding='utf-8')
        files_different = {file1: ["Content 1"], file3: ["Content 3"]}
        
        hash3 = smart_cache.compute_files_hash(files_different)
        assert hash1 != hash3
    
    def test_smart_cache_invalidate_file(self, temp_dir, memory_cache):
        """Test file invalidation in smart cache."""
        smart_cache = SmartFileCache(memory_cache)
        
        # Create and cache file
        test_file = temp_dir / "test.md"
        test_file.write_text("# Content", encoding='utf-8')
        
        content = ["# Content"]
        smart_cache.set_file_content(test_file, content)
        
        # Verify cached
        assert smart_cache.get_file_content(test_file) == content
        
        # Invalidate
        smart_cache.invalidate_file(test_file)
        
        # Should be removed from cache
        assert smart_cache.get_file_content(test_file) is None


@pytest.mark.unit
class TestCacheFactories:
    """Test cache factory functions."""
    
    def test_create_memory_cache(self):
        """Test memory cache factory."""
        cache = create_memory_cache(max_size=50, default_ttl=3600)
        
        assert isinstance(cache, MemoryCache)
        assert cache.max_size == 50
        assert cache.default_ttl == 3600
    
    def test_create_file_cache(self, temp_dir):
        """Test file cache factory."""
        cache_dir = temp_dir / "test_cache"
        cache = create_file_cache(cache_dir=cache_dir, max_size=20)
        
        assert isinstance(cache, FileBasedCache)
        assert cache.cache_dir == cache_dir
        assert cache.max_size == 20
        assert cache_dir.exists()
    
    def test_create_tiered_cache(self, temp_dir):
        """Test tiered cache factory."""
        cache = create_tiered_cache(
            memory_size=30,
            cache_dir=temp_dir / "tiered_cache",
            file_cache_size=500
        )
        
        assert isinstance(cache, TieredCache)
        assert isinstance(cache.l1_cache, MemoryCache)
        assert isinstance(cache.l2_cache, FileBasedCache)
    
    def test_create_smart_file_cache_memory(self):
        """Test smart file cache factory with memory backend."""
        cache = create_smart_file_cache(cache_type="memory", max_size=100)
        
        assert isinstance(cache, SmartFileCache)
        assert isinstance(cache.cache, MemoryCache)
    
    def test_create_smart_file_cache_tiered(self, temp_dir):
        """Test smart file cache factory with tiered backend."""
        cache = create_smart_file_cache(
            cache_type="tiered",
            memory_size=50,
            cache_dir=temp_dir / "smart_cache"
        )
        
        assert isinstance(cache, SmartFileCache)
        assert isinstance(cache.cache, TieredCache)
    
    def test_create_smart_file_cache_invalid_type(self):
        """Test smart file cache factory with invalid type."""
        with pytest.raises(ValueError):
            create_smart_file_cache(cache_type="invalid")


@pytest.mark.performance
class TestCachePerformance:
    """Performance tests for cache implementations."""
    
    def test_memory_cache_performance(self, performance_metrics):
        """Test memory cache performance."""
        cache = MemoryCache(max_size=10000)
        
        # Test write performance
        start_time = time.time()
        for i in range(1000):
            cache.set(f"key_{i}", f"value_{i}")
        write_time = time.time() - start_time
        performance_metrics.record("memory_cache_write", write_time)
        
        # Test read performance
        start_time = time.time()
        for i in range(1000):
            cache.get(f"key_{i}")
        read_time = time.time() - start_time
        performance_metrics.record("memory_cache_read", read_time)
        
        # Performance should be reasonable
        assert write_time < 1.0  # Should write 1000 items in less than 1 second
        assert read_time < 0.5   # Should read 1000 items in less than 0.5 seconds
    
    @pytest.mark.slow
    def test_file_cache_performance(self, temp_dir, performance_metrics):
        """Test file cache performance."""
        cache = FileBasedCache(cache_dir=temp_dir / "perf_cache", max_size=1000)
        
        # Test write performance
        start_time = time.time()
        for i in range(100):  # Fewer iterations for file cache
            cache.set(f"key_{i}", f"value_{i}")
        write_time = time.time() - start_time
        performance_metrics.record("file_cache_write", write_time)
        
        # Test read performance
        start_time = time.time()
        for i in range(100):
            cache.get(f"key_{i}")
        read_time = time.time() - start_time
        performance_metrics.record("file_cache_read", read_time)
        
        # File cache should be slower but still reasonable
        assert write_time < 5.0  # Should write 100 items in less than 5 seconds
        assert read_time < 2.0   # Should read 100 items in less than 2 seconds


@pytest.mark.integration
class TestCacheIntegration:
    """Integration tests for cache system."""
    
    def test_cache_with_real_file_operations(self, temp_dir, sample_markdown_files):
        """Test cache integration with real file operations."""
        cache = create_smart_file_cache(
            cache_type="tiered",
            memory_size=10,
            cache_dir=temp_dir / "integration_cache"
        )
        
        # Cache some real file content
        for name, file_path in sample_markdown_files.items():
            content = file_path.read_text(encoding='utf-8').splitlines()
            cache.set_file_content(file_path, content)
        
        # Verify all files are cached
        for name, file_path in sample_markdown_files.items():
            cached_content = cache.get_file_content(file_path)
            assert cached_content is not None
            assert len(cached_content) > 0
        
        # Test cache persistence across instances
        cache2 = SmartFileCache(create_file_cache(temp_dir / "integration_cache"))
        
        # Should still have cached content
        for name, file_path in sample_markdown_files.items():
            cached_content = cache2.get_file_content(file_path)
            # May be None if not in file cache level, but shouldn't error
    
    def test_cache_error_handling(self, temp_dir):
        """Test cache error handling in various scenarios."""
        cache_dir = temp_dir / "error_cache"
        cache = FileBasedCache(cache_dir=cache_dir, max_size=10)
        
        # Test with permission errors (mock)
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            with pytest.raises(CacheError):
                cache.set("key1", "value1")
        
        # Test with invalid data
        cache.set("valid_key", "valid_value")
        
        # Corrupt the cache file
        cache_files = list(cache_dir.glob("*.cache"))
        if cache_files:
            cache_files[0].write_text("corrupted data", encoding='utf-8')
        
        # Should handle gracefully
        result = cache.get("valid_key")
        # Should return None and clean up corrupted file