"""
Maintenance API - trigger/inspect periodic maintenance tasks
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from ..db.session import get_db
from ..core.security import require_role
from ..services.maintenance_service import MaintenanceService
from ..services.data_lifecycle_service import DataLifecycleService

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


@router.post("/weekly")
async def run_weekly(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    return await MaintenanceService.weekly_review(db)


@router.post("/biweekly")
async def run_biweekly(current_user=Depends(require_role("admin"))) -> Dict[str, Any]:
    return await MaintenanceService.biweekly_security_maintenance()


@router.post("/monthly/db")
async def run_monthly_db(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    return await MaintenanceService.monthly_db_maintenance(db)


@router.post("/monthly/cost")
async def run_monthly_cost(current_user=Depends(require_role("admin"))) -> Dict[str, Any]:
    return await MaintenanceService.monthly_cost_optimization()


@router.post("/quarterly/dr-drill")
async def run_quarterly_dr(current_user=Depends(require_role("admin"))) -> Dict[str, Any]:
    return await MaintenanceService.quarterly_dr_drill()


@router.post("/retention/archive-reports")
async def archive_old_reports(
    days: int = 540,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Archive reports older than N days (default ~18 months) to cold storage path.
    """
    return await DataLifecycleService.archive_reports_older_than(db, days=days)



