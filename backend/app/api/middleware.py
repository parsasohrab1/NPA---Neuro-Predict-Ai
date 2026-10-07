"""
Middleware for Metrics Collection
"""
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.metrics import errors_total, http_request_duration_seconds, http_requests_total


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP metrics for Prometheus"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        method = request.method
        path = request.url.path
        
        # Start timer
        start_time = time.time()
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            # Re-raise to let exception handler deal with it
            raise
        finally:
            # Record metrics
            duration = time.time() - start_time
            
            # Increment request counter
            http_requests_total.labels(
                method=method,
                endpoint=path,
                status_code=status_code
            ).inc()
            
            # Record duration
            http_request_duration_seconds.labels(
                method=method,
                endpoint=path
            ).observe(duration)
            
            # Track errors
            if status_code >= 400:
                severity = "high" if status_code >= 500 else "medium"
                errors_total.labels(
                    error_type="http_error",
                    severity=severity
                ).inc()
        
        return response

