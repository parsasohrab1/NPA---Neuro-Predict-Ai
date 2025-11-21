"""
Operational (Runbook) APIs - admin-only helpers for incident response
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import require_role
from ..db.session import get_db
from ..services.rum_service import RUMService
from ..services.maintenance_service import MaintenanceService
from ..services.backup_service import BackupService
from ..core.config import settings
from .. import main as app_module

router = APIRouter(prefix="/ops", tags=["Operations"])


@router.post("/rate-limit")
async def set_rate_limits(
    ip_limit: Optional[int] = Body(None, embed=True),
    ip_window: Optional[int] = Body(None, embed=True),
    user_limit: Optional[int] = Body(None, embed=True),
    user_window: Optional[int] = Body(None, embed=True),
    current_user=Depends(require_role("admin")),
):
    """
    Dynamically adjust global rate-limit parameters (best-effort; effective if middleware supports runtime overrides).
    """
    if not hasattr(app_module, "app"):
        raise HTTPException(status_code=500, detail="App not initialized")
    current = getattr(app_module.app.state, "rate_limits", {}) or {}
    new_cfg = {
        "ip_limit": ip_limit or current.get("ip_limit", getattr(settings, "RATE_LIMIT_DEFAULT_PER_MINUTE", 100)),
        "ip_window": ip_window or current.get("ip_window", 60),
        "user_limit": (user_limit or current.get("user_limit", getattr(settings, "RATE_LIMIT_USER_PER_HOUR", 1000))),
        "user_window": user_window or current.get("user_window", 3600),
    }
    app_module.app.state.rate_limits = new_cfg
    return {"rate_limits": new_cfg}


@router.post("/circuit")
async def toggle_circuit(
    service: str = Body(..., embed=True),  # e.g. 'ehr' | 'pacs' | 'hl7'
    open: bool = Body(..., embed=True),
    current_user=Depends(require_role("admin")),
):
    """
    Toggle a simple circuit-breaker flag for external integrations (advisory; integration layer may consult this flag).
    """
    if not hasattr(app_module, "app"):
        raise HTTPException(status_code=500, detail="App not initialized")
    breakers: Dict[str, bool] = getattr(app_module.app.state, "circuit_breakers", {}) or {}
    breakers[service] = bool(open)
    app_module.app.state.circuit_breakers = breakers
    return {"service": service, "open": bool(open)}


@router.post("/dr/verify")
async def trigger_backup_verify(current_user=Depends(require_role("admin"))):
    """Trigger a backup verification run (DR drill check)."""
    res = await BackupService.verify_latest_full_backup(backup_dir=settings.BACKUP_DIR)
    return {"verify": res}


@router.get("/summary")
async def ops_summary(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    """Operational summary for runbooks: health, basic metrics, RUM & feedback overview, current RL config."""
    from ..services.monitoring_service import MonitoringService
    health = await MonitoringService.get_health_status(db)
    metrics = await MonitoringService.get_metrics(db)
    rum = await RUMService.metrics_summary(db, hours=hours)
    rl = getattr(app_module.app.state, "rate_limits", None) if hasattr(app_module, "app") else None
    return {
        "health": health,
        "metrics": metrics.get("metrics", {}),
        "rum": rum,
        "rate_limits": rl,
    }


@router.get("/metrics/prometheus")
async def prometheus_metrics(
    current_user=Depends(require_role("admin"))
):
    """
    Prometheus metrics endpoint for scraping
    Returns metrics in Prometheus text format
    """
    from fastapi.responses import Response
    from ..middleware.prometheus_middleware import get_prometheus_metrics
    
    metrics_text = get_prometheus_metrics()
    return Response(content=metrics_text, media_type="text/plain; version=0.0.4")


