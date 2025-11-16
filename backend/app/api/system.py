"""
System Architecture API - Context/Container summaries for UI/docs alignment
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from ..db.session import get_db
from ..services.monitoring_service import MonitoringService

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/context")
async def get_context_overview(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    High-level context view (aligned with C4 Context in docs).
    """
    health = await MonitoringService.get_health_status(db)
    return {
        "users": ["admin", "doctor", "nurse", "viewer"],
        "external_systems": ["HIS", "PACS"],
        "components": {
            "frontend": {"name": "Web App", "status": "n/a"},
            "admin_dashboard": {"name": "Admin UI", "status": "n/a"},
            "backend_api": {"name": "FastAPI", "status": health.get("status")},
            "database": health.get("services", {}).get("database", {}),
            "cache": health.get("services", {}).get("redis", {}),
            "storage": {"images": True, "reports": True},
        },
    }


@router.get("/containers")
async def get_containers_view(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Container view (aligned with C4 Container in docs).
    """
    metrics = await MonitoringService.get_metrics(db)
    return {
        "backend": {
            "routers": ["auth", "patients", "imaging", "predictions", "reports", "longitudinal", "security", "integration", "products", "monitoring"],
            "services": ["AI", "Reporting", "Monitoring", "Integration", "ImageProcessing", "Longitudinal"],
            "core": ["config", "security", "cache"],
            "orm": "SQLAlchemy Async",
        },
        "data": {
            "postgres": {"metrics": {"users_total": metrics.get("metrics", {}).get("users_total", 0)}},
            "redis": {"metrics": {"requests_total": metrics.get("metrics", {}).get("requests_total", 0)}},
            "filestorage": {"paths": ["uploads/images", "uploads/reports"]},
        },
    }


