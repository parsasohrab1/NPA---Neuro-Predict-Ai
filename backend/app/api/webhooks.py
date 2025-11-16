"""
Webhooks Outbound API - enqueue reliable sends with HMAC and idempotency
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, Any, Optional

from ..core.security import require_role
from ..services.job_queue_service import JobQueueService

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


class WebhookSendRequest(BaseModel):
    url: HttpUrl
    event_type: str = Field(..., min_length=2)
    data: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: Optional[str] = None


@router.post("/send", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def enqueue_webhook_send(
    payload: WebhookSendRequest,
    current_user=Depends(require_role("admin")),
):
    job = await JobQueueService.enqueue(
        "webhook.send",
        {"url": str(payload.url), "event_type": payload.event_type, "data": payload.data},
        idempotency_key=payload.idempotency_key,
    )
    return job


@router.get("/stats", response_model=dict)
async def webhook_stats(current_user=Depends(require_role("admin"))):
    return await JobQueueService.stats()


@router.get("/dlq", response_model=dict)
async def webhook_dlq(limit: int = Query(50, ge=1, le=200), current_user=Depends(require_role("admin"))):
    items = await JobQueueService.list_dlq(limit=limit)
    return {"items": items, "count": len(items)}


