"""
Cache Middleware for API Responses
Middleware برای cache کردن responses
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import hashlib
import json
from typing import Callable

from ..core.cache import cache_service


class CacheMiddleware(BaseHTTPMiddleware):
    """Middleware to cache API responses"""
    
    def __init__(self, app: ASGIApp, cache_ttl: int = 300):
        super().__init__(app)
        self.cache_ttl = cache_ttl
        self.cacheable_methods = {"GET"}
        self.cacheable_paths = [
            "/api/v1/patients/",
            "/api/v1/predictions/",
            "/api/v1/analytics/",
        ]
    
    def _is_cacheable(self, request: Request) -> bool:
        """Check if request is cacheable"""
        if request.method not in self.cacheable_methods:
            return False
        
        # Check if path is cacheable
        for path in self.cacheable_paths:
            if request.url.path.startswith(path):
                return True
        
        return False
    
    def _make_cache_key(self, request: Request) -> str:
        """Create cache key from request"""
        # Include path and query params
        key_data = f"{request.method}:{request.url.path}:{request.url.query_string}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"api:{key_hash}"
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with caching"""
        # Check if request is cacheable
        if not self._is_cacheable(request):
            return await call_next(request)
        
        # Try to get from cache
        cache_key = self._make_cache_key(request)
        cached_response = await cache_service.get("response", cache_key)
        
        if cached_response:
            # Return cached response
            return Response(
                content=json.dumps(cached_response["body"]),
                status_code=cached_response["status_code"],
                headers=cached_response["headers"],
                media_type="application/json"
            )
        
        # Process request
        response = await call_next(request)
        
        # Cache successful GET responses
        if response.status_code == 200 and request.method == "GET":
            try:
                # Read response body
                body = await response.body()
                body_json = json.loads(body.decode())
                
                # Cache response
                await cache_service.set(
                    "response",
                    cache_key,
                    {
                        "body": body_json,
                        "status_code": response.status_code,
                        "headers": dict(response.headers)
                    },
                    ttl=self.cache_ttl
                )
            except Exception:
                # If caching fails, just continue
                pass
        
        return response

