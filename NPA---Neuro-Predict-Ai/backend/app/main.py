"""
NeuroPredict-AI Main Application
FastAPI Backend for Alzheimer's and Parkinson's Disease Prediction
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from .core.config import settings
from .db.session import init_db, close_db
from .core.cache import cache_service
from .api import auth, patients, predictions, reports, models, analytics, users, mock_data, monitoring, websocket, optimization
from .api.integration import fhir, pacs, ehr, hl7v2, devices
from .api.streaming import realtime
from .services.streaming.realtime_service import realtime_service

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
    
    # Start real-time streaming service
    try:
        realtime_service.start()
        logger.info("Real-time streaming service started")
    except Exception as e:
        logger.error(f"Failed to start streaming service: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down NeuroPredict-AI application...")
    
    # Stop real-time streaming service
    try:
        realtime_service.stop()
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

# Metrics Middleware (for Prometheus)
if settings.ENVIRONMENT == "production":
    from .api.middleware import MetricsMiddleware
    app.add_middleware(MetricsMiddleware)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred"}
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
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(monitoring.router, prefix=settings.API_V1_PREFIX)
app.include_router(websocket.router, prefix=settings.API_V1_PREFIX)
app.include_router(mock_data.router, prefix=settings.API_V1_PREFIX)  # Mock data for development
app.include_router(optimization.router, prefix=settings.API_V1_PREFIX)

# Integration routers
app.include_router(fhir.router, prefix=settings.API_V1_PREFIX)
app.include_router(pacs.router, prefix=settings.API_V1_PREFIX)
app.include_router(ehr.router, prefix=settings.API_V1_PREFIX)
app.include_router(hl7v2.router, prefix=settings.API_V1_PREFIX)
app.include_router(devices.router, prefix=settings.API_V1_PREFIX)

# Streaming routers
app.include_router(realtime.router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

