"""
NeuroPredict-AI Main Application
FastAPI Backend for Alzheimer's and Parkinson's Disease Prediction
"""
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from .core.config import settings
from .db.session import init_db, close_db
from .core.cache import cache_service
from .api import auth, patients, predictions, reports, models, model_metrics, analytics, users, mock_data, monitoring, websocket, optimization, disease_tracking, data_monitoring, admin, longitudinal

# Optional integration routers (FHIR etc. may require extra deps / Pydantic compatibility)
_integration = None
try:
    from .api.integration import fhir, pacs, ehr, hl7v2, devices
    _integration = (fhir, pacs, ehr, hl7v2, devices)
except Exception as e:
    import warnings
    warnings.warn(f"Integration routers (FHIR, PACS, EHR, HL7v2, devices) not loaded: {e}")

_realtime_router = None
_realtime_service = None
try:
    from .api.streaming import realtime
    from .services.streaming.realtime_service import realtime_service
    _realtime_router = realtime
    _realtime_service = realtime_service
except Exception as e:
    import warnings
    warnings.warn(f"Streaming router not loaded: {e}")

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting NeuroPredict-AI application...")
    logger.info(
        "Config: ENVIRONMENT=%s, DEBUG=%s, API docs=%s",
        settings.ENVIRONMENT,
        settings.DEBUG,
        "enabled" if settings.DEBUG else "disabled",
    )

    # Create upload directories
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.DICOM_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.MRI_DIR).mkdir(parents=True, exist_ok=True)
    Path("models").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(parents=True, exist_ok=True)
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Connect Redis for cache
    try:
        await cache_service.connect()
        logger.info("Cache service (Redis) connected")
    except Exception as e:
        logger.warning(f"Cache connection failed: {e}. Response caching disabled.")
    
    # Start real-time streaming service (if loaded)
    if _realtime_service:
        try:
            _realtime_service.start()
            logger.info("Real-time streaming service started")
        except Exception as e:
            logger.error(f"Failed to start streaming service: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down NeuroPredict-AI application...")
    
    # Stop real-time streaming service (if loaded)
    if _realtime_service:
        try:
            _realtime_service.stop()
            logger.info("Real-time streaming service stopped")
        except Exception as e:
            logger.error(f"Error stopping streaming service: {e}")
    
    # Disconnect cache
    try:
        await cache_service.disconnect()
        logger.info("Cache service disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting cache: {e}")
    
    await close_db()


# Create FastAPI application
# Disable docs in production for security
docs_url = "/api/docs" if settings.DEBUG else None
redoc_url = "/api/redoc" if settings.DEBUG else None
openapi_url = "/api/openapi.json" if settings.DEBUG else None

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Clinical Decision Support System for Neurodegenerative Diseases",
    lifespan=lifespan,
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression Middleware for performance
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Cache Middleware for GET responses (patients, predictions, analytics)
from .middleware.cache_middleware import CacheMiddleware
app.add_middleware(CacheMiddleware, cache_ttl=300)

# Rate limiting for sensitive endpoints (POST /predictions, POST /auth)
from .middleware.rate_limit_middleware import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware)

# Metrics Middleware (for Prometheus)
if settings.ENVIRONMENT == "production":
    from .api.middleware import MetricsMiddleware
    app.add_middleware(MetricsMiddleware)


def _cors_headers(request: Request) -> dict:
    """Return CORS headers for the request origin if allowed."""
    origin = request.headers.get("origin")
    if origin and origin in settings.CORS_ORIGINS:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        }
    return {}


# Exception handlers (include CORS so browser shows real error instead of CORS error)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    headers = _cors_headers(request)
    detail = str(exc) if settings.DEBUG else "Internal server error occurred"
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail},
        headers=headers,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Ensure 4xx responses include CORS headers so browser doesn't report CORS instead of status."""
    headers = _cors_headers(request)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers,
    )


# Health check endpoints (DB and Redis connectivity for load balancer / monitoring)
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check: verifies PostgreSQL and Redis. Returns 503 if DB or Redis is down."""
    from sqlalchemy import text
    from .db.session import engine

    db_ok = False
    redis_ok = False
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        logger.warning("Health check DB failed: %s", e)

    try:
        if cache_service.enabled and cache_service.redis_client:
            await cache_service.redis_client.ping()
            redis_ok = True
        else:
            redis_ok = True  # Redis optional; consider healthy if disabled
    except Exception as e:
        logger.warning("Health check Redis failed: %s", e)

    if not db_ok:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "database": "down",
                "redis": "ok" if redis_ok else "down",
            },
        )
    if not redis_ok:
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "service": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "database": "ok",
                "redis": "down",
            },
        )
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "ok",
        "redis": "ok",
    }


# Prometheus metrics endpoint
@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrics endpoint"""
    from .core.metrics import get_metrics_response
    return get_metrics_response()


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "health": "/health"
    }


# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(patients.router, prefix=settings.API_V1_PREFIX)
app.include_router(predictions.router, prefix=settings.API_V1_PREFIX)
app.include_router(reports.router, prefix=settings.API_V1_PREFIX)
app.include_router(models.router, prefix=settings.API_V1_PREFIX)
app.include_router(model_metrics.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(monitoring.router, prefix=settings.API_V1_PREFIX)
app.include_router(websocket.router, prefix=settings.API_V1_PREFIX)
app.include_router(mock_data.router, prefix=settings.API_V1_PREFIX)  # Mock data for development
app.include_router(optimization.router, prefix=settings.API_V1_PREFIX)
app.include_router(disease_tracking.router, prefix=settings.API_V1_PREFIX)
app.include_router(data_monitoring.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)
logger.info(f"About to include longitudinal router: {longitudinal.router}")
app.include_router(longitudinal.router, prefix=settings.API_V1_PREFIX)
logger.info("Longitudinal router included successfully")

# Integration routers (optional)
if _integration:
    fhir, pacs, ehr, hl7v2, devices = _integration
    app.include_router(fhir.router, prefix=settings.API_V1_PREFIX)
    app.include_router(pacs.router, prefix=settings.API_V1_PREFIX)
    app.include_router(ehr.router, prefix=settings.API_V1_PREFIX)
    app.include_router(hl7v2.router, prefix=settings.API_V1_PREFIX)
    app.include_router(devices.router, prefix=settings.API_V1_PREFIX)

# Streaming routers (optional)
if _realtime_router:
    app.include_router(_realtime_router.router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

