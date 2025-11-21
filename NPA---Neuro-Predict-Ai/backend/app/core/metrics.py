"""
Prometheus Metrics for NeuroPredict-AI
"""
from prometheus_client import Counter, Histogram, Gauge, Summary
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from typing import Optional
import time

# HTTP Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Application Metrics
active_connections = Gauge(
    'active_connections',
    'Active WebSocket connections'
)

active_users = Gauge(
    'active_users',
    'Number of active users'
)

# AI/ML Metrics
prediction_requests_total = Counter(
    'prediction_requests_total',
    'Total prediction requests',
    ['disease_type', 'risk_level']
)

prediction_duration_seconds = Histogram(
    'prediction_duration_seconds',
    'Prediction processing time in seconds',
    ['disease_type'],
    buckets=[0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
)

prediction_confidence_score = Summary(
    'prediction_confidence_score',
    'Prediction confidence scores',
    ['disease_type']
)

model_drift_score = Gauge(
    'model_drift_score',
    'Model drift score (0-1)',
    ['model_version']
)

# Database Metrics
database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type']
)

database_connections_active = Gauge(
    'database_connections_active',
    'Active database connections'
)

database_connections_idle = Gauge(
    'database_connections_idle',
    'Idle database connections'
)

# Cache Metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

# Error Metrics
errors_total = Counter(
    'errors_total',
    'Total errors',
    ['error_type', 'severity']
)

# Business Metrics
patients_total = Gauge(
    'patients_total',
    'Total number of patients'
)

predictions_total = Gauge(
    'predictions_total',
    'Total number of predictions'
)

high_risk_predictions_total = Counter(
    'high_risk_predictions_total',
    'Total high risk predictions',
    ['disease_type']
)


class MetricsMiddleware:
    """Middleware to collect HTTP metrics"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        method = scope["method"]
        path = scope["path"]
        
        # Start timer
        start_time = time.time()
        
        # Track request
        status_code = 200
        
        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            # Record metrics
            duration = time.time() - start_time
            http_requests_total.labels(
                method=method,
                endpoint=path,
                status_code=status_code
            ).inc()
            http_request_duration_seconds.labels(
                method=method,
                endpoint=path
            ).observe(duration)
            
            # Track errors
            if status_code >= 400:
                errors_total.labels(
                    error_type="http_error",
                    severity="high" if status_code >= 500 else "medium"
                ).inc()


def get_metrics_response() -> Response:
    """Get Prometheus metrics endpoint response"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

