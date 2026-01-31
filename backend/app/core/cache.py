"""
Caching Service for Performance Optimization
سرویس Cache برای بهینه‌سازی عملکرد
"""
from typing import Optional, Any, Union
import json
import pickle
import hashlib
from datetime import timedelta
import redis.asyncio as redis
import logging

from .config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Service for caching data to improve performance"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = True
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = await redis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                encoding="utf-8",
                decode_responses=False  # We'll handle encoding ourselves
            )
            # Test connection
            await self.redis_client.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self.enabled = False
            self.redis_client = None
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis cache")
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage"""
        try:
            # Try JSON first (for simple types)
            return json.dumps(value).encode('utf-8')
        except (TypeError, ValueError):
            # Fall back to pickle for complex types
            return pickle.dumps(value)
    
    def _deserialize(self, value: bytes) -> Any:
        """Deserialize value from storage"""
        try:
            # Try JSON first
            return json.loads(value.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            return pickle.loads(value)
    
    def _make_key(self, prefix: str, key: str) -> str:
        """Create cache key"""
        return f"{prefix}:{key}"
    
    async def get(
        self,
        prefix: str,
        key: str,
        default: Any = None
    ) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            prefix: Key prefix (e.g., 'patient', 'prediction')
            key: Cache key
            default: Default value if not found
        
        Returns:
            Cached value or default
        """
        if not self.enabled or not self.redis_client:
            return default
        
        try:
            cache_key = self._make_key(prefix, key)
            value = await self.redis_client.get(cache_key)
            
            if value is None:
                return default
            
            return self._deserialize(value)
        
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return default
    
    async def set(
        self,
        prefix: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache
        
        Args:
            prefix: Key prefix
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for no expiration)
        
        Returns:
            True if successful
        """
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            cache_key = self._make_key(prefix, key)
            serialized = self._serialize(value)
            
            if ttl:
                await self.redis_client.setex(cache_key, ttl, serialized)
            else:
                await self.redis_client.set(cache_key, serialized)
            
            return True
        
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    async def delete(self, prefix: str, key: str) -> bool:
        """Delete value from cache"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            cache_key = self._make_key(prefix, key)
            await self.redis_client.delete(cache_key)
            return True
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    async def delete_pattern(self, prefix: str, pattern: str) -> int:
        """
        Delete all keys matching pattern
        
        Args:
            prefix: Key prefix
            pattern: Pattern to match (e.g., 'patient:*')
        
        Returns:
            Number of keys deleted
        """
        if not self.enabled or not self.redis_client:
            return 0
        
        try:
            full_pattern = self._make_key(prefix, pattern)
            keys = []
            async for key in self.redis_client.scan_iter(match=full_pattern):
                keys.append(key)
            
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        
        except Exception as e:
            logger.error(f"Error deleting pattern from cache: {e}")
            return 0
    
    async def exists(self, prefix: str, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            cache_key = self._make_key(prefix, key)
            return await self.redis_client.exists(cache_key) > 0
        except Exception as e:
            logger.error(f"Error checking cache existence: {e}")
            return False
    
    async def increment(self, prefix: str, key: str, amount: int = 1) -> Optional[int]:
        """Increment numeric value in cache"""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            cache_key = self._make_key(prefix, key)
            return await self.redis_client.incrby(cache_key, amount)
        except Exception as e:
            logger.error(f"Error incrementing cache: {e}")
            return None
    
    async def get_or_set(
        self,
        prefix: str,
        key: str,
        callable_func,
        ttl: Optional[int] = None
    ) -> Any:
        """
        Get value from cache or set it using callable
        
        Args:
            prefix: Key prefix
            key: Cache key
            callable_func: Function to call if cache miss
            ttl: Time to live in seconds
        
        Returns:
            Cached or computed value
        """
        # Try to get from cache
        cached = await self.get(prefix, key)
        if cached is not None:
            return cached
        
        # Compute value
        if callable(callable_func):
            value = await callable_func() if hasattr(callable_func, '__call__') else callable_func
        else:
            value = callable_func
        
        # Store in cache
        await self.set(prefix, key, value, ttl)
        
        return value


# Global cache service instance
cache_service = CacheService()

