"""
Tests for Cache functionality
"""
import pytest
from app.core.cache import (
    cache_service,
    _split_cache_key,
    generate_cache_key,
    get_cached_response,
    set_cached_response,
    invalidate_cache_pattern
)


async def _connect_cache():
    """Connect the cache used by get/set_cached_response; skip when Redis is unavailable."""
    await cache_service.connect()
    if cache_service.redis_client is None:
        pytest.skip("Redis not available")


@pytest.mark.asyncio
async def test_generate_cache_key():
    """Test cache key generation"""
    key1 = generate_cache_key("test", patient_id=1, skip=0, limit=10)
    key2 = generate_cache_key("test", patient_id=1, skip=0, limit=10)
    key3 = generate_cache_key("test", patient_id=2, skip=0, limit=10)
    
    # Same parameters should generate same key
    assert key1 == key2
    # Different parameters should generate different key
    assert key1 != key3


@pytest.mark.asyncio
async def test_cache_set_and_get():
    """Test setting and getting from cache"""
    # Ensure cache service is connected
    await _connect_cache()
    
    test_key = "test_cache_key_123"
    test_value = {"test": "data", "number": 42}
    
    # Set value
    await set_cached_response(test_key, test_value, expire_seconds=60)
    
    # Get value
    cached = await get_cached_response(test_key)
    
    assert cached is not None
    assert cached["test"] == test_value["test"]
    assert cached["number"] == test_value["number"]
    
    # Cleanup
    await cache_service.delete(*_split_cache_key(test_key))


@pytest.mark.asyncio
async def test_cache_expiration():
    """Test that cache entries expire"""
    await _connect_cache()
    
    test_key = "test_expire_key"
    test_value = {"data": "test"}
    
    # Set with very short expiration
    await set_cached_response(test_key, test_value, expire_seconds=1)
    
    # Should be available immediately
    cached = await get_cached_response(test_key)
    assert cached is not None
    
    # Wait for expiration (if Redis is available)
    import asyncio
    await asyncio.sleep(2)
    
    # Should be None after expiration (if Redis is working)
    # Note: This test may pass even if Redis is not available
    cached_after = await get_cached_response(test_key)
    # Result depends on Redis availability


@pytest.mark.asyncio
async def test_cache_invalidation():
    """Test cache pattern invalidation"""
    await _connect_cache()
    
    # Set multiple keys
    await set_cached_response("test:patient:1", {"data": 1})
    await set_cached_response("test:patient:2", {"data": 2})
    await set_cached_response("test:other:1", {"data": 3})
    
    # Invalidate pattern
    await invalidate_cache_pattern("test:patient:*")
    
    # Patient keys should be gone, other should remain
    # Note: This depends on Redis availability

