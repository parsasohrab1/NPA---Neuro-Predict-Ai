"""
Monitoring API Endpoints - Health Checks, Metrics, Observability
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from ..db.session import get_db
from ..core.security import require_role
from ..models.user import User
from ..services.monitoring_service import MonitoringService

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Comprehensive health check endpoint"""
    return await MonitoringService.get_health_status(db)


@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Kubernetes readiness probe"""
    health = await MonitoringService.get_health_status(db)
    if health["status"] == "healthy":
        return {"status": "ready"}
    else:
        return {"status": "not_ready", "details": health}


@router.get("/metrics")
async def get_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = require_role("admin")
) -> Dict[str, Any]:
    """Get system metrics (Prometheus format)"""
    metrics = await MonitoringService.get_metrics(db)
    return metrics


@router.get("/metrics/prometheus")
async def get_prometheus_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = require_role("admin")
) -> str:
    """Get metrics in Prometheus format"""
    metrics = await MonitoringService.get_metrics(db)
    return MonitoringService.format_prometheus_metrics(metrics)

