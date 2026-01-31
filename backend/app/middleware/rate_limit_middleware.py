"""
Rate Limiting Middleware
محدودیت نرخ برای endpointهای حساس (predictions, auth)
"""
import time
import asyncio
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limit request rate per IP for sensitive endpoints."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self._lock = asyncio.Lock()
        # (path_key, ip) -> (count, window_start_minute)
        self._counts: dict[tuple[str, str], tuple[int, int]] = defaultdict(lambda: (0, 0))
        self._paths = [
            (f"{settings.API_V1_PREFIX}/predictions", "POST", settings.RATE_LIMIT_PREDICTIONS_PER_MINUTE),
            (f"{settings.API_V1_PREFIX}/auth", "POST", settings.RATE_LIMIT_AUTH_PER_MINUTE),
        ]

    def _client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host or "unknown"
        return "unknown"

    def _current_minute(self) -> int:
        return int(time.time() // 60)

    async def _check_limit(self, path_key: str, ip: str, limit: int) -> bool:
        """Return True if under limit (allow), False if over limit (reject)."""
        async with self._lock:
            key = (path_key, ip)
            count, window = self._counts[key]
            now_minute = self._current_minute()
            if now_minute > window:
                count, window = 0, now_minute
            count += 1
            self._counts[key] = (count, window)
            return count <= limit

    def _is_rate_limited_path(self, request: Request) -> tuple[bool, str, int]:
        path = request.url.path
        method = request.method
        for path_prefix, allowed_method, limit in self._paths:
            if path.startswith(path_prefix) and method == allowed_method:
                return True, path_prefix, limit
        return False, "", 0

    async def dispatch(self, request: Request, call_next) -> Response:
        limited, path_key, limit = self._is_rate_limited_path(request)
        if not limited:
            return await call_next(request)

        ip = self._client_ip(request)
        allowed = await self._check_limit(path_key, ip, limit)
        if not allowed:
            logger.warning("Rate limit exceeded for %s from IP %s", path_key, ip)
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": 60,
                },
                headers={"Retry-After": "60"},
            )
        return await call_next(request)
