"""
Security Middleware - IP Whitelist, Rate Limiting, Security Headers
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, timedelta
import time
import redis.asyncio as redis
from typing import Optional
import uuid
import logging

from ..core.config import settings
from ..db.session import get_db
from ..models.security import IPWhitelist, SecurityLog
from ..services.security_service import SecurityService

# Initialize logger at module level
logger = logging.getLogger("app.middleware")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # CSP Configuration.
        # This middleware only governs the backend's own responses (JSON API +,
        # when settings.DEBUG is True, the Swagger/ReDoc docs pages). The React
        # frontends are served by their own dev server/nginx and are not affected.
        is_enforced = settings.ENVIRONMENT == "production" and settings.DEBUG is False

        # Swagger UI / ReDoc (docs_url/redoc_url in main.py) require 'unsafe-inline'
        # and 'unsafe-eval' to render, but those routes only exist when DEBUG is
        # True — i.e. never in the enforced (production) tier. So the enforced
        # policy can safely drop unsafe-* with no functional impact.
        script_src = "script-src 'self'" if is_enforced else "script-src 'self' 'unsafe-inline' 'unsafe-eval'"
        style_src = "style-src 'self'" if is_enforced else "style-src 'self' 'unsafe-inline'"

        csp_policy = [
            "default-src 'self'",
            script_src,
            style_src,
            "img-src 'self' data: blob: https:",
            "font-src 'self' data:",
            "connect-src 'self' " + " ".join(settings.CORS_ORIGINS),  # Allow API calls to same origin and CORS origins
            "frame-ancestors 'none'",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-src 'none'",
            "media-src 'self'",
            "worker-src 'self' blob:",
            "manifest-src 'self'",
            "report-uri /api/v1/security/csp/report",  # CSP violation reporting endpoint
        ]

        # Use Report-Only in development, enforce in production (when ready)
        if is_enforced:
            response.headers["Content-Security-Policy"] = "; ".join(csp_policy)
        else:
            response.headers["Content-Security-Policy-Report-Only"] = "; ".join(csp_policy)
        
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=()"
        response.headers["X-Download-Options"] = "noopen"  # Prevent IE from executing downloads
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"  # Prevent Flash/PDF cross-domain access
        
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
            token = authorization.split(" ", 1)[1]
            try:
                from ..core.security import decode_token
                from ..db.session import get_db
                from ..models.user import User
                from sqlalchemy import select
                
                # Decode token to get user_id
                payload = decode_token(token)
                user_id = int(payload.get("sub"))
                
                # Get user from database to check IP whitelist
                # Note: This creates a new DB session - for production, consider caching user IP whitelist in Redis
                async for db in get_db():
                    try:
                        result = await db.execute(select(User).where(User.id == user_id))
                        user = result.scalar_one_or_none()
                        
                        if user:
                            client_ip = SecurityService.get_client_ip(request)
                            ip_allowed = await SecurityService.check_ip_whitelist(user.id, client_ip, db)
                            
                            if not ip_allowed:
                                await SecurityService.log_security_event(
                                    db=db,
                                    user_id=user.id,
                                    event_type="access_blocked_ip",
                                    severity="warning",
                                    description=f"Access attempt from non-whitelisted IP: {client_ip}",
                                    ip_address=client_ip,
                                    request_path=request.url.path,
                                    success=False
                                )
                                return Response(
                                    content='{"detail": "Access denied from this IP address"}',
                                    status_code=status.HTTP_403_FORBIDDEN,
                                    headers={"Content-Type": "application/json"}
                                )
                    finally:
                        # Ensure session is closed
                        await db.close()
                    break
            except Exception:
                # If token decode fails or DB error, let auth dependency handle it
                pass
        
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis"""
    
    def __init__(self, app, redis_client: Optional[redis.Redis] = None):
        super().__init__(app)
        self.redis_client = redis_client
        # Defaults (overridden by per-route policies)
        self.default_ip_limit = settings.RATE_LIMIT_DEFAULT_PER_MINUTE
        self.default_ip_window = 60  # seconds
        # User-based window is hourly
        self.user_limit = settings.RATE_LIMIT_USER_PER_HOUR
        self.user_window = 3600  # seconds
        # Per-route policies
        self.login_ip_limit = settings.RATE_LIMIT_LOGIN_PER_MINUTE
        self.upload_ip_limit = settings.RATE_LIMIT_UPLOAD_PER_MINUTE
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting if disabled
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/docs", "/api/redoc"]:
            return await call_next(request)
        
        if self.redis_client:
            client_ip = SecurityService.get_client_ip(request)
            path = request.url.path
            # Determine policy by path
            if path.startswith(f"{settings.API_V1_PREFIX}/auth/login"):
                ip_limit = self.login_ip_limit
                ip_window = 60
                scope = "login"
            elif path.startswith(f"{settings.API_V1_PREFIX}/imaging/dicom"):
                ip_limit = self.upload_ip_limit
                ip_window = 60
                scope = "upload"
            elif path.startswith(f"{settings.API_V1_PREFIX}/predictions"):
                # Use prediction-specific limit if configured
                ip_limit = getattr(settings, "RATE_LIMIT_PREDICTION_PER_MINUTE", self.default_ip_limit)
                ip_window = 60
                scope = "prediction"
            else:
                ip_limit = self.default_ip_limit
                ip_window = self.default_ip_window
                scope = "default"

            ip_key = f"rate_limit:{scope}:ip:{client_ip}"

            # Use Authorization token (opaque) as user key if present
            auth_header = request.headers.get("Authorization")
            user_token = None
            if auth_header and auth_header.startswith("Bearer "):
                user_token = auth_header.split(" ", 1)[1]
            user_key = f"rate_limit:{scope}:user:{user_token}" if user_token else None
            
            try:
                # IP bucket
                ip_count = await self.redis_client.get(ip_key)
                if ip_count is None:
                    await self.redis_client.setex(ip_key, ip_window, 1)
                    ip_remaining = ip_limit - 1
                else:
                    ip_count = int(ip_count)
                    if ip_count >= ip_limit:
                        await SecurityService.log_security_event(
                            db=None,
                            user_id=None,
                            event_type="rate_limit_exceeded_ip",
                            severity="warning",
                            description=f"IP rate limit exceeded for IP: {client_ip}",
                            ip_address=client_ip,
                            request_path=request.url.path
                        )
                        return Response(
                            content="Rate limit exceeded",
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            headers={
                                "Retry-After": str(ip_window),
                                "X-RateLimit-Limit": str(ip_limit),
                                "X-RateLimit-Remaining": "0",
                            }
                        )
                    ip_remaining = max(0, ip_limit - (ip_count + 1))
                    await self.redis_client.incr(ip_key)

                # User bucket (if authenticated)
                user_remaining = None
                if user_key:
                    user_count = await self.redis_client.get(user_key)
                    if user_count is None:
                        await self.redis_client.setex(user_key, self.user_window, 1)
                        user_remaining = self.user_limit - 1
                    else:
                        user_count = int(user_count)
                        if user_count >= self.user_limit:
                            await SecurityService.log_security_event(
                                db=None,
                                user_id=None,
                                event_type="rate_limit_exceeded_user",
                                severity="warning",
                                description=f"User rate limit exceeded",
                                ip_address=client_ip,
                                request_path=request.url.path
                            )
                            return Response(
                                content="Rate limit exceeded",
                                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                                headers={
                                    "Retry-After": str(self.user_window),
                                    "X-RateLimit-Limit": str(ip_limit),
                                    "X-RateLimit-Remaining": str(ip_remaining),
                                    "X-RateLimit-User-Limit": str(self.user_limit),
                                    "X-RateLimit-User-Remaining": "0",
                                }
                            )
                        user_remaining = max(0, self.user_limit - (user_count + 1))
                        await self.redis_client.incr(user_key)
            except Exception as e:
                # If Redis fails, check fail-open setting
                if not settings.RATE_LIMIT_FAIL_OPEN:
                    logger.error(f"Rate limiting Redis error and fail-open disabled: {e}")
                    return Response(
                        content='{"detail": "Rate limiting service unavailable"}',
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        headers={"Content-Type": "application/json"}
                    )
                # Fail open - allow request if Redis unavailable
                logger.warning(f"Rate limiting Redis error, failing open: {e}")
        
        response = await call_next(request)
        # Attach rate limit headers when possible
        if self.redis_client:
            # Mirror the default policy numbers for visibility
            response.headers.setdefault("X-RateLimit-Limit", str(self.default_ip_limit))
            # We can't always know remaining here; keep headers if a 429 set them
            if "X-RateLimit-Remaining" not in response.headers:
                response.headers["X-RateLimit-Remaining"] = response.headers.get("X-RateLimit-Remaining", "")
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for security monitoring"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = SecurityService.get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "Unknown")
        logger = logging.getLogger("app.request")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        latency_ms = int(process_time * 1000)

        # Attach process time header
        response.headers["X-Process-Time"] = str(process_time)

        # Structured JSON log
        try:
            request_id = getattr(request.state, "request_id", None)
            user_id = None  # populate from auth if available in future
            error_code = None
            if 400 <= response.status_code < 600:
                # If handlers set a code, propagate; else None
                error_code = response.headers.get("X-Error-Code", None)

            logger.info(
                "request_completed",
                extra={
                    "request_id": request_id,
                    "user_id": user_id,
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "latency_ms": latency_ms,
                    "error_code": error_code,
                    # limited, non-PII attributes
                    "user_agent": user_agent,
                    "client_ip": client_ip,
                },
            )
        except Exception:
            # Never break request on logging issues
            pass

        return response


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Attach a unique request id to each request/response for traceability"""

    def __init__(self, app: ASGIApp, header_name: str = "X-Request-Id") -> None:
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get(self.header_name) or str(uuid.uuid4())
        # expose on request state for handlers
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[self.header_name] = request_id
        return response

