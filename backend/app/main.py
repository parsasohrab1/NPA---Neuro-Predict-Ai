"""
NeuroPredict-AI Main Application
FastAPI Backend for Alzheimer's and Parkinson's Disease Prediction
"""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from .core.config import settings
from .db.session import init_db, close_db
from .api import (
    auth, patients, predictions, imaging, reports, longitudinal,
    security, monitoring, integration, backup, products, admin, system, maintenance,
    notifications, comments, privacy, jobs, rum, ops, support, legal, webhooks
)
from .middleware.security_middleware import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    RequestIdMiddleware,
    IPWhitelistMiddleware
)
from .middleware.metrics_middleware import MetricsMiddleware
from .middleware.prometheus_middleware import PrometheusMiddleware
from .services.backup_service import BackupService
import redis.asyncio as redis
from .core.logging import setup_json_logging

# Configure logging
setup_json_logging(service_name=settings.APP_NAME, environment=settings.ENVIRONMENT, level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting NeuroPredict-AI application...")
    
    # Create upload directories
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.DICOM_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.MRI_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.REPORTS_DIR).mkdir(parents=True, exist_ok=True)
    Path("models").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(parents=True, exist_ok=True)
    Path("backups").mkdir(parents=True, exist_ok=True)
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Initialize Redis connection for caching
    try:
        redis_client = redis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
            decode_responses=False
        )
        await redis_client.ping()
        app.state.redis = redis_client
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
        app.state.redis = None
    
    # Schedule background backup/verify tasks per policy
    async def full_backup_loop():
        interval = max(1, settings.BACKUP_FULL_INTERVAL_HOURS)
        while True:
            try:
                logger.info("Running scheduled full backup...")
                await BackupService.create_database_backup(backup_dir=settings.BACKUP_DIR)
                await BackupService.cleanup_old_backups(
                    backup_dir=settings.BACKUP_DIR,
                    keep_days=settings.BACKUP_RETENTION_DAYS,
                )
            except Exception as e:
                logger.error(f"Scheduled full backup failed: {e}")
            await asyncio.sleep(interval * 3600)

    async def wal_archive_loop():
        minutes = max(1, settings.BACKUP_WAL_INTERVAL_MINUTES)
        while True:
            try:
                await BackupService.archive_wal_segment(wal_dir=f"{settings.BACKUP_DIR}/wal")
            except Exception as e:
                logger.warning(f"WAL archive failed: {e}")
            await asyncio.sleep(minutes * 60)

    async def weekly_verify_loop():
        if not settings.BACKUP_VERIFY_WEEKLY:
            return
        days = max(1, settings.BACKUP_VERIFY_INTERVAL_DAYS)
        while True:
            try:
                logger.info("Running weekly backup verification...")
                result = await BackupService.verify_latest_full_backup(backup_dir=settings.BACKUP_DIR)
                if not result.get("valid", False):
                    logger.error(f"Backup verification failed: {result}")
            except Exception as e:
                logger.error(f"Backup verification loop error: {e}")
            await asyncio.sleep(days * 86400)

    # Maintenance loops (weekly, biweekly, monthly, quarterly)
    from .services.maintenance_service import MaintenanceService

    async def weekly_maintenance_loop():
        while True:
            try:
                logger.info("Running weekly maintenance review...")
                # Requires DB session; here we call lightweight endpoints when available.
                # In background mode we skip DB to avoid creating sessions; API endpoint can be used by ops.
            except Exception as e:
                logger.warning(f"Weekly maintenance loop error: {e}")
            await asyncio.sleep(7 * 86400)

    async def biweekly_maintenance_loop():
        while True:
            try:
                logger.info("Running biweekly security maintenance...")
                await MaintenanceService.biweekly_security_maintenance()
            except Exception as e:
                logger.warning(f"Biweekly maintenance loop error: {e}")
            await asyncio.sleep(14 * 86400)

    async def monthly_maintenance_loop():
        while True:
            try:
                logger.info("Running monthly cost optimization scan...")
                await MaintenanceService.monthly_cost_optimization()
            except Exception as e:
                logger.warning(f"Monthly maintenance loop error: {e}")
            await asyncio.sleep(30 * 86400)

    async def quarterly_maintenance_loop():
        while True:
            try:
                logger.info("Running quarterly DR drill (verify latest backup)...")
                await MaintenanceService.quarterly_dr_drill()
            except Exception as e:
                logger.warning(f"Quarterly DR drill loop error: {e}")
            await asyncio.sleep(90 * 86400)

    import asyncio
    app.state._bg_tasks = [
        asyncio.create_task(full_backup_loop()),
        asyncio.create_task(wal_archive_loop()),
        asyncio.create_task(weekly_verify_loop()),
        asyncio.create_task(weekly_maintenance_loop()),
        asyncio.create_task(biweekly_maintenance_loop()),
        asyncio.create_task(monthly_maintenance_loop()),
        asyncio.create_task(quarterly_maintenance_loop()),
    ]

    yield
    
    # Shutdown
    logger.info("Shutting down NeuroPredict-AI application...")
    # Cancel background tasks
    try:
        for t in getattr(app.state, "_bg_tasks", []):
            t.cancel()
    except Exception:
        pass
    if hasattr(app.state, 'redis') and app.state.redis:
        await app.state.redis.close()
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

# Security Middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(IPWhitelistMiddleware)  # IP Whitelist check for authenticated requests
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIdMiddleware)
# (Metrics middleware will be added after redis_client initialization)
try:
    pass
except Exception:
    logger.warning("Metrics middleware disabled - Redis not available")

# Prometheus Metrics Middleware (no Redis required)
app.add_middleware(PrometheusMiddleware)

# Rate Limiting Middleware (requires Redis)
try:
    redis_client = redis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
        decode_responses=False
    )
    app.add_middleware(RateLimitMiddleware, redis_client=redis_client)
    # Add metrics middleware now that redis_client is available
    from .middleware.metrics_middleware import Metrics
    app.add_middleware(MetricsMiddleware, name="metrics_middleware", redis_client=redis_client)
except Exception:
    logger.warning("Rate limiting or metrics middleware disabled - Redis not available")


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(
        "Unhandled exception",
        exc_info=True,
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "path": request.url.path,
            "method": request.method,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "error_code": "INTERNAL_SERVER_ERROR",
        },
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error occurred",
            "code": "INTERNAL_SERVER_ERROR",
            "trace_id": getattr(request.state, "request_id", None),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTPException handler with standardized schema"""
    logger.warning(
        "HTTPException",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "error_code": getattr(exc, "code", None) or status.HTTPStatus(exc.status_code).phrase.replace(" ", "_").upper(),
        },
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail if isinstance(exc.detail, str) else "HTTP error",
            "code": getattr(exc, "code", None) or status.HTTPStatus(exc.status_code).phrase.replace(" ", "_").upper(),
            "trace_id": getattr(request.state, "request_id", None),
        },
        headers=exc.headers or None,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Validation error handler aligned with error schema"""
    logger.warning(
        "Validation error",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "path": request.url.path,
            "method": request.method,
            "status_code": status.HTTP_400_BAD_REQUEST,
            "error_code": "BAD_REQUEST",
        },
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Invalid input data",
            "code": "BAD_REQUEST",
            "trace_id": getattr(request.state, "request_id", None),
        },
    )


# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


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
app.include_router(imaging.router, prefix=settings.API_V1_PREFIX)
app.include_router(reports.router, prefix=settings.API_V1_PREFIX)
app.include_router(longitudinal.router, prefix=settings.API_V1_PREFIX)
app.include_router(security.router, prefix=settings.API_V1_PREFIX)
app.include_router(monitoring.router, prefix=settings.API_V1_PREFIX)
app.include_router(integration.router, prefix=settings.API_V1_PREFIX)
app.include_router(backup.router, prefix=settings.API_V1_PREFIX)
app.include_router(products.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)
app.include_router(system.router, prefix=settings.API_V1_PREFIX)
app.include_router(maintenance.router, prefix=settings.API_V1_PREFIX)
app.include_router(notifications.router, prefix=settings.API_V1_PREFIX)
app.include_router(comments.router, prefix=settings.API_V1_PREFIX)
app.include_router(privacy.router, prefix=settings.API_V1_PREFIX)
app.include_router(jobs.router, prefix=settings.API_V1_PREFIX)
app.include_router(rum.router, prefix=settings.API_V1_PREFIX)
app.include_router(ops.router, prefix=settings.API_V1_PREFIX)
app.include_router(support.router, prefix=settings.API_V1_PREFIX)
app.include_router(legal.router, prefix=settings.API_V1_PREFIX)
app.include_router(webhooks.router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

