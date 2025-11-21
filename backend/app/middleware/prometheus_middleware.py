"""
Prometheus Metrics Middleware for FastAPI
Exposes metrics in Prometheus format for monitoring
"""
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

from ..core.config import settings

# In-memory metrics storage (in production, use Prometheus client library)
_metrics = {
    'http_requests_total': {},
    'http_request_duration_seconds': {},
    'http_request_size_bytes': {},
    'http_response_size_bytes': {},
}


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timer
        start_time = time.time()
        
        # Track request
        method = request.method
        path = request.url.path
        
        # Normalize path (replace IDs with placeholders)
        normalized_path = self._normalize_path(path)
        
        # Record request
        metric_key = f"{method}_{normalized_path}"
        if metric_key not in _metrics['http_requests_total']:
            _metrics['http_requests_total'][metric_key] = 0
        _metrics['http_requests_total'][metric_key] += 1
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Record duration
        if metric_key not in _metrics['http_request_duration_seconds']:
            _metrics['http_request_duration_seconds'][metric_key] = []
        _metrics['http_request_duration_seconds'][metric_key].append(duration)
        
        # Keep only last 1000 durations per endpoint
        if len(_metrics['http_request_duration_seconds'][metric_key]) > 1000:
            _metrics['http_request_duration_seconds'][metric_key] = \
                _metrics['http_request_duration_seconds'][metric_key][-1000:]
        
        # Record status code
        status_key = f"{metric_key}_{response.status_code}"
        if status_key not in _metrics['http_requests_total']:
            _metrics['http_requests_total'][status_key] = 0
        _metrics['http_requests_total'][status_key] += 1
        
        return response
    
    @staticmethod
    def _normalize_path(path: str) -> str:
        """Normalize path by replacing IDs with placeholders"""
        import re
        # Replace UUIDs
        path = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '{id}', path)
        # Replace numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)
        return path
    
    @staticmethod
    def get_metrics() -> str:
        """Get metrics in Prometheus format"""
        lines = []
        
        # HTTP requests total
        lines.append("# HELP http_requests_total Total number of HTTP requests")
        lines.append("# TYPE http_requests_total counter")
        for key, value in _metrics['http_requests_total'].items():
            method, path = key.rsplit('_', 1) if '_' not in key.split('_', 1)[1] else (key.split('_', 1)[0], key.split('_', 1)[1])
            lines.append(f'http_requests_total{{method="{method}",path="{path}"}} {value}')
        
        # HTTP request duration
        lines.append("\n# HELP http_request_duration_seconds HTTP request duration in seconds")
        lines.append("# TYPE http_request_duration_seconds histogram")
        for key, durations in _metrics['http_request_duration_seconds'].items():
            if durations:
                import statistics
                count = len(durations)
                total = sum(durations)
                avg = statistics.mean(durations)
                p50 = statistics.median(durations)
                p95 = statistics.quantiles(durations, n=20)[18] if len(durations) >= 20 else max(durations)
                p99 = statistics.quantiles(durations, n=100)[98] if len(durations) >= 100 else max(durations)
                
                method, path = key.rsplit('_', 1) if '_' not in key.split('_', 1)[1] else (key.split('_', 1)[0], key.split('_', 1)[1])
                lines.append(f'http_request_duration_seconds_count{{method="{method}",path="{path}"}} {count}')
                lines.append(f'http_request_duration_seconds_sum{{method="{method}",path="{path}"}} {total:.6f}')
                lines.append(f'http_request_duration_seconds_bucket{{method="{method}",path="{path}",le="0.005"}} {sum(1 for d in durations if d <= 0.005)}')
                lines.append(f'http_request_duration_seconds_bucket{{method="{method}",path="{path}",le="0.01"}} {sum(1 for d in durations if d <= 0.01)}')
                lines.append(f'http_request_duration_seconds_bucket{{method="{method}",path="{path}",le="0.025"}} {sum(1 for d in durations if d <= 0.025)}')
                lines.append(f'http_request_duration_seconds_bucket{{method="{method}",path="{path}",le="0.05"}} {sum(1 for d in durations if d <= 0.05)}')
                lines.append(f'http_request_duration_seconds_bucket{{method="{method}",path="{path}",le="0.1"}} {sum(1 for d in durations if d <= 0.1)}')
                lines.append(f'http_request_duration_seconds_bucket{{method="{method}",path="{path}",le="0.25"}} {sum(1 for d in durations if d <= 0.25)}')
                lines.append(f'http_request_duration_seconds_bucket{{method="{method}",path="{path}",le="0.5"}} {sum(1 for d in durations if d <= 0.5)}')
                lines.append(f'http_request_duration_seconds_bucket{{method="{method}",path="{path}",le="1"}} {sum(1 for d in durations if d <= 1)}')
                lines.append(f'http_request_duration_seconds_bucket{{method="{method}",path="{path}",le="2.5"}} {sum(1 for d in durations if d <= 2.5)}')
                lines.append(f'http_request_duration_seconds_bucket{{method="{method}",path="{path}",le="5"}} {sum(1 for d in durations if d <= 5)}')
                lines.append(f'http_request_duration_seconds_bucket{{method="{method}",path="{path}",le="+Inf"}} {count}')
        
        return '\n'.join(lines)


def get_prometheus_metrics() -> str:
    """Get Prometheus metrics string"""
    return PrometheusMiddleware.get_metrics()


