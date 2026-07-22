"""
Privacy & DSR API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db.session import get_db
from ..core.security import get_current_user, require_role
from ..models.user import User
from ..models.privacy import DSRRequest, DSRType, DSRStatus
from ..services.privacy_service import PrivacyService

router = APIRouter(prefix="/privacy", tags=["Privacy"])


class DSRCreate(BaseModel):
    request_type: DSRType
    subject_identifier: str = Field(..., min_length=1, max_length=256)
    reason: Optional[str] = None


@router.post("/dsr", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_dsr_request(
    payload: DSRCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dsr = DSRRequest(
        requester_user_id=current_user.id if current_user else None,
        request_type=payload.request_type,
        subject_identifier=payload.subject_identifier,
        reason=payload.reason,
        status=DSRStatus.RECEIVED,
    )
    db.add(dsr)
    await db.commit()
    await db.refresh(dsr)
    return {"id": dsr.id, "status": dsr.status}


@router.get("/dsr", response_model=List[dict])
async def list_dsr_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    result = await db.execute(select(DSRRequest).order_by(DSRRequest.created_at.desc()))
    items = result.scalars().all()
    return [
        {
            "id": i.id,
            "request_type": i.request_type,
            "subject_identifier": i.subject_identifier,
            "status": i.status,
            "result_location": i.result_location,
            "created_at": str(i.created_at),
        }
        for i in items
    ]


@router.post("/dsr/{dsr_id}/export")
async def export_dsr(
    dsr_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    result = await db.execute(select(DSRRequest).where(DSRRequest.id == dsr_id))
    dsr = result.scalar_one_or_none()
    if not dsr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DSR not found")
    path = await PrivacyService.export_subject_data(db, dsr.subject_identifier)
    dsr = await PrivacyService.update_dsr_status(db, dsr, DSRStatus.COMPLETED, result_location=path)
    return {"id": dsr.id, "status": dsr.status, "result_location": dsr.result_location}


@router.post("/dsr/{dsr_id}/erase")
async def erase_dsr(
    dsr_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Admin endpoint: fulfill erasure DSR by anonymizing PHI for the subject."""
    result = await db.execute(select(DSRRequest).where(DSRRequest.id == dsr_id))
    dsr = result.scalar_one_or_none()
    if not dsr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DSR not found")

    erase_result = await PrivacyService.erase_subject_data(db, dsr.subject_identifier)
    note = json_dumps_safe(erase_result)
    dsr = await PrivacyService.update_dsr_status(
        db, dsr, DSRStatus.COMPLETED, result_location=note
    )
    return {
        "id": dsr.id,
        "status": dsr.status,
        "erase_result": erase_result,
    }


def json_dumps_safe(obj) -> str:
    import json
    return json.dumps(obj, default=str)
