"""
Performance Service - Caching, Query Optimization, Compression
"""
import json
import gzip
import pickle
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import hashlib

from ..core.config import settings


class CacheService:
    """Redis-based caching service"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        if not self.redis_client:
            self.redis_client = redis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                decode_responses=False
            )
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            await self.connect()
        
        try:
            data = await self.redis_client.get(key)
            if data:
                # Decompress and deserialize
                decompressed = gzip.decompress(data)
                return pickle.loads(decompressed)
        except Exception:
            return None
        
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire_seconds: Optional[int] = 3600
    ):
        """Set value in cache"""
        if not self.redis_client:
            await self.connect()
        
        try:
            # Serialize and compress
            serialized = pickle.dumps(value)
            compressed = gzip.compress(serialized)
            await self.redis_client.setex(key, expire_seconds, compressed)
        except Exception:
            pass
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.redis_client:
            await self.connect()
        
        try:
            await self.redis_client.delete(key)
        except Exception:
            pass
    
    async def delete_pattern(self, pattern: str):
        """Delete keys matching pattern"""
        if not self.redis_client:
            await self.connect()
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
        except Exception:
            pass
    
    def generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from prefix and parameters"""
        key_parts = [prefix]
        for k, v in sorted(kwargs.items()):
            if v is not None:
                key_parts.append(f"{k}:{v}")
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()


class PerformanceService:
    """Service for performance optimization"""
    
    cache_service = CacheService()
    
    @staticmethod
    async def optimize_query(db: AsyncSession, query: str, params: Dict[str, Any] = None) -> Any:
        """Execute optimized query with caching"""
        # Generate cache key
        cache_key = PerformanceService.cache_service.generate_cache_key(
            "query",
            query=query,
            params=json.dumps(params or {}, sort_keys=True)
        )
        
        # Try cache first
        cached_result = await PerformanceService.cache_service.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Execute query
        if params:
            result = await db.execute(text(query), params)
        else:
            result = await db.execute(text(query))
        
        # Fetch results
        rows = result.fetchall()
        data = [dict(row._mapping) for row in rows]
        
        # Cache result (5 minutes default)
        await PerformanceService.cache_service.set(cache_key, data, expire_seconds=300)
        
        return data
    
    @staticmethod
    async def invalidate_cache_pattern(pattern: str):
        """Invalidate cache entries matching pattern"""
        await PerformanceService.cache_service.delete_pattern(pattern)
    
    @staticmethod
    def compress_data(data: bytes) -> bytes:
        """Compress data using gzip"""
        return gzip.compress(data, compresslevel=6)
    
    @staticmethod
    def decompress_data(compressed_data: bytes) -> bytes:
        """Decompress gzip data"""
        return gzip.decompress(compressed_data)
    
    @staticmethod
    async def get_cache_stats() -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            await PerformanceService.cache_service.connect()
            info = await PerformanceService.cache_service.redis_client.info("stats")
            return {
                "connected": True,
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "total_keys": await PerformanceService.cache_service.redis_client.dbsize()
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }

