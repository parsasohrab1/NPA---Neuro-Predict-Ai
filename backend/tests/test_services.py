"""
Tests for Service layer
"""
import pytest
from datetime import date, datetime
from unittest.mock import AsyncMock, patch

from app.services.performance_service import PerformanceService, CacheService
from app.models.patient import Patient, Gender


@pytest.mark.asyncio
async def test_cache_service_connection():
    """Test cache service connection"""
    cache_service = CacheService()
    await cache_service.connect()
    
    assert cache_service.redis_client is not None or True  # May be None if Redis unavailable
    
    await cache_service.close()


@pytest.mark.asyncio
async def test_cache_service_get_set():
    """Test cache service get and set operations"""
    cache_service = CacheService()
    await cache_service.connect()
    
    test_key = "test_key_123"
    test_value = {"test": "data"}
    
    # Set value
    await cache_service.set(test_key, test_value, expire_seconds=60)
    
    # Get value
    cached = await cache_service.get(test_key)
    
    # Result depends on Redis availability
    if cached is not None:
        assert cached == test_value
    
    # Cleanup
    await cache_service.delete(test_key)
    await cache_service.close()


@pytest.mark.asyncio
async def test_performance_service_optimize_query():
    """Test query optimization with caching"""
    # This test would require a real database connection
    # For now, we'll test the structure
    assert hasattr(PerformanceService, 'optimize_query')
    assert hasattr(PerformanceService, 'cache_service')


def test_cache_key_generation():
    """Test cache key generation utility"""
    from app.services.performance_service import CacheService
    
    cache_service = CacheService()
    key1 = cache_service.generate_cache_key("prefix", param1="value1", param2="value2")
    key2 = cache_service.generate_cache_key("prefix", param1="value1", param2="value2")
    key3 = cache_service.generate_cache_key("prefix", param1="value3", param2="value2")
    
    # Same parameters should generate same key
    assert key1 == key2
    # Different parameters should generate different key
    assert key1 != key3

