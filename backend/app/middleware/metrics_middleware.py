"""
Metrics Middleware - request latency buckets, request/error counters
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time
from typing import Optional, List
import redis.asyncio as redis


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Collect coarse-grained latency histograms and request/error counters.
    Stores in Redis for aggregation by MonitoringService.
    """

    def __init__(self, app, redis_client: Optional[redis.Redis] = None):
        super().__init__(app)
        self.redis_client = redis_client
        # latency buckets in seconds
        self.buckets: List[float] = [0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10]

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        status_code = 500
        try:
            response: Response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration = time.time() - start
            if self.redis_client:
                try:
                    # overall counters
                    await self.redis_client.incr("metrics:req_total")
                    await self.redis_client.incrbyfloat("metrics:req_duration_sum", duration)
                    # errors
                    if status_code >= 500:
                        await self.redis_client.incr("metrics:error_5xx_total")
                    elif status_code >= 400:
                        await self.redis_client.incr("metrics:error_4xx_total")
                    # latency bucket
                    bucket_label = self._bucket_label(duration)
                    await self.redis_client.incr(f"metrics:latency_bucket:{bucket_label}")
                except Exception:
                    # fail open
                    pass

    def _bucket_label(self, duration: float) -> str:
        for b in self.buckets:
            if duration <= b:
                return f"le_{b}"
        return "gt_10"


