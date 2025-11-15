"""
Cache utilities for API endpoints
"""
from typing import Optional, Dict, Any
from fastapi import Request
import json
import hashlib

from ..services.performance_service import PerformanceService


async def get_cached_response(
    cache_key: str,
    expire_seconds: int = 300
) -> Optional[Any]:
    """Get cached response if available"""
    return await PerformanceService.cache_service.get(cache_key)


async def set_cached_response(
    cache_key: str,
    value: Any,
    expire_seconds: int = 300
):
    """Cache a response"""
    await PerformanceService.cache_service.set(
        cache_key,
        value,
        expire_seconds=expire_seconds
    )


def generate_cache_key(
    prefix: str,
    request: Optional[Request] = None,
    current_user: Optional[Any] = None,
    include_user: bool = False,
    **kwargs
) -> str:
    """
    Generate a cache key from request parameters
    
    Args:
        prefix: Cache key prefix (e.g., "predictions", "patients")
        request: FastAPI Request object
        current_user: Current user object
        include_user: Whether to include user ID in cache key
        **kwargs: Additional parameters to include in cache key
    """
    cache_key_parts = [prefix]
    
    # Include query parameters
    if request:
        query_params = dict(request.query_params)
        if query_params:
            query_str = json.dumps(query_params, sort_keys=True)
            cache_key_parts.append(f"q:{hashlib.md5(query_str.encode()).hexdigest()[:8]}")
        
        # Include path parameters
        if hasattr(request, 'path_params') and request.path_params:
            path_str = json.dumps(request.path_params, sort_keys=True)
            cache_key_parts.append(f"p:{hashlib.md5(path_str.encode()).hexdigest()[:8]}")
    
    # Include user ID if needed
    if include_user and current_user:
        cache_key_parts.append(f"u:{current_user.id}")
    
    # Include relevant kwargs
    relevant_kwargs = {}
    for key in ['patient_id', 'prediction_id', 'skip', 'limit', 'search', 'report_type', 'start_date', 'end_date']:
        if key in kwargs and kwargs[key] is not None:
            relevant_kwargs[key] = kwargs[key]
    
    if relevant_kwargs:
        kwargs_str = json.dumps(relevant_kwargs, sort_keys=True, default=str)
        cache_key_parts.append(f"k:{hashlib.md5(kwargs_str.encode()).hexdigest()[:8]}")
    
    # Use PerformanceService to generate final cache key
    # The generate_cache_key method expects prefix and kwargs
    key_string = "|".join(cache_key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


async def invalidate_cache_pattern(pattern: str):
    """Invalidate cache entries matching a pattern"""
    await PerformanceService.invalidate_cache_pattern(pattern)


async def invalidate_patient_cache(patient_id: int):
    """Invalidate all cache entries related to a patient"""
    patterns = [
        f"*patient:{patient_id}*",
        f"*patients*",
        f"*analytics*",
        f"*predictions*patient_id:{patient_id}*"
    ]
    for pattern in patterns:
        await invalidate_cache_pattern(pattern)


async def invalidate_prediction_cache(prediction_id: Optional[int] = None, patient_id: Optional[int] = None):
    """Invalidate cache entries related to predictions"""
    patterns = [
        "*predictions*",
        "*analytics*"
    ]
    
    if prediction_id:
        patterns.append(f"*prediction:{prediction_id}*")
    
    if patient_id:
        patterns.append(f"*predictions*patient_id:{patient_id}*")
    
    for pattern in patterns:
        await invalidate_cache_pattern(pattern)

