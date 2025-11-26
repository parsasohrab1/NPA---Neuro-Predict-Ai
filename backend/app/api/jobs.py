"""
Jobs API - enqueue and inspect job queue
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from ..core.security import require_role
from ..services.job_queue_service import JobQueueService

router = APIRouter(prefix="/jobs", tags=["Jobs"])


class EnqueueRequest(BaseModel):
    job_type: str = Field(..., min_length=2)
    payload: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: Optional[str] = None


@router.post("/enqueue")
async def enqueue_job(
    req: EnqueueRequest,
):
    try:
        result = await JobQueueService.enqueue(req.job_type, req.payload, req.idempotency_key)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))


@router.get("/stats")
async def queue_stats(current_user=Depends(require_role("admin"))):
    return await JobQueueService.stats()



