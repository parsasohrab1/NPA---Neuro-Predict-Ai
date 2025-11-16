"""
RUM & Feedback API
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, conint
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..services.rum_service import RUMService
from ..core.security import require_role

router = APIRouter(prefix="/rum", tags=["RUM"])


class RUMEventIn(BaseModel):
    type: str = Field(..., max_length=64)
    value: Optional[float] = None
    meta: Optional[Dict[str, Any]] = None
    sampled: Optional[bool] = True


class RUMBatchIn(BaseModel):
    events: List[RUMEventIn]


@router.post("/events")
async def post_events(payload: RUMBatchIn, db: AsyncSession = Depends(get_db)):
    if not payload.events:
        raise HTTPException(status_code=400, detail="No events")
    count = await RUMService.ingest_events(db, [e.model_dump() for e in payload.events])
    return {"ingested": count}


class FeedbackIn(BaseModel):
    rating: Optional[conint(ge=1, le=5)] = None
    comment: Optional[str] = Field(None, max_length=2000)
    context: Optional[Dict[str, Any]] = None


@router.post("/feedback")
async def post_feedback(payload: FeedbackIn, db: AsyncStudioSession := Depends(get_db)):
    fid = await RUMService.submit_feedback(db, payload.rating, payload.comment, payload.context)
    return {"id": fid}


@router.get("/metrics")
async def get_metrics_summary(hours: int = Query(24, ge=1, le=168), db: AsyncSession = Depends(get_db), current_user=Depends(require_role("admin"))):
    return await RUMService.metrics_summary(db, hours=hours)


