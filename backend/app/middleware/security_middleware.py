"""
Security Middleware - IP Whitelist, Rate Limiting, Security Headers
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, timedelta
import time
import redis.asyncio as redis
from typing import Optional

from ..core.config import settings
from ..db.session import get_db
from ..models.security import IPWhitelist, SecurityLog
from ..services.security_service import SecurityService


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """Check IP whitelist for authenticated users"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip for public endpoints
        public_paths = ["/health", "/api/docs", "/api/redoc", "/api/openapi.json", "/api/v1/auth/login", "/api/v1/auth/register"]
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)
        
        # Get user from token if present
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            # Extract user from token (simplified - should use proper JWT decode)
            # For now, we'll check IP whitelist in the auth dependency
            pass
        
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis"""
    
    def __init__(self, app, redis_client: Optional[redis.Redis] = None):
        super().__init__(app)
        self.redis_client = redis_client
        self.rate_limit_requests = 100  # requests per window
        self.rate_limit_window = 60  # seconds
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/docs", "/api/redoc"]:
            return await call_next(request)
        
        if self.redis_client:
            client_ip = SecurityService.get_client_ip(request)
            key = f"rate_limit:{client_ip}"
            
            try:
                # Get current count
                count = await self.redis_client.get(key)
                
                if count is None:
                    # First request in window
                    await self.redis_client.setex(key, self.rate_limit_window, 1)
                else:
                    count = int(count)
                    if count >= self.rate_limit_requests:
                        # Rate limit exceeded
                        await SecurityService.log_security_event(
                            db=None,  # Will need to handle this differently
                            user_id=None,
                            event_type="rate_limit_exceeded",
                            severity="warning",
                            description=f"Rate limit exceeded for IP: {client_ip}",
                            ip_address=client_ip,
                            request_path=request.url.path
                        )
                        return Response(
                            content="Rate limit exceeded",
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            headers={"Retry-After": str(self.rate_limit_window)}
                        )
                    else:
                        # Increment count
                        await self.redis_client.incr(key)
            except Exception as e:
                # If Redis fails, allow request (fail open)
                pass
        
        return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for security monitoring"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = SecurityService.get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "Unknown")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log security event (async, don't block response)
        # This would typically be done in a background task
        # For now, we'll add it to response headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

