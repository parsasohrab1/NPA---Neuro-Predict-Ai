"""
Backup & Disaster Recovery API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from pydantic import BaseModel

from ..db.session import get_db
from ..core.security import require_role
from ..models.user import User
from ..services.backup_service import BackupService

router = APIRouter(prefix="/backup", tags=["Backup & DR"])


class RestoreRequest(BaseModel):
    backup_path: str


@router.post("/create")
async def create_backup(
    current_user: User = Depends(require_role("admin"))
) -> Dict[str, Any]:
    """Create database backup"""
    result = await BackupService.create_database_backup()
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Backup failed")
        )
    
    return result


@router.post("/restore")
async def restore_backup(
    request: RestoreRequest,
    current_user: User = Depends(require_role("admin"))
) -> Dict[str, Any]:
    """Restore database from backup"""
    result = await BackupService.restore_database_backup(request.backup_path)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Restore failed")
        )
    
    return result


@router.get("/list")
async def list_backups(
    current_user: User = Depends(require_role("admin"))
) -> List[Dict[str, Any]]:
    """List all available backups"""
    backups = await BackupService.list_backups()
    return backups


@router.post("/verify")
async def verify_backup(
    request: RestoreRequest,
    current_user: User = Depends(require_role("admin"))
) -> Dict[str, Any]:
    """Verify backup integrity"""
    result = await BackupService.verify_backup(request.backup_path)
    return result


@router.post("/cleanup")
async def cleanup_old_backups(
    keep_days: int = 30,
    current_user: User = Depends(require_role("admin"))
) -> Dict[str, Any]:
    """Clean up old backups"""
    result = await BackupService.cleanup_old_backups(keep_days=keep_days)
    return result

