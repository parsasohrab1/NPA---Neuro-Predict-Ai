"""
Support Playbook APIs
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from ..db.session import get_db
from ..core.security import get_current_user, require_role
from ..models.user import User
from ..models.support import SupportTicket, SupportUpdate, TicketSeverity, TicketStatus
from ..services.support_service import SupportService

router = APIRouter(prefix="/support", tags=["Support"])


class TicketCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    severity: TicketSeverity = TicketSeverity.SEV3
    domain: Optional[str] = Field(None, description="fe|be|infra|integration")


class TicketUpdateStatus(BaseModel):
    status: TicketStatus
    owner: Optional[str] = None
    acknowledge: bool = False
    resolve: bool = False
    close: bool = False


class TicketAddMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    payload: TicketCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    t = SupportTicket(
        title=payload.title,
        description=payload.description,
        request_id=getattr(request.state, "request_id", None),
        reporter_user_id=current_user.id if current_user else None,
        severity=payload.severity,
        domain=payload.domain,
        status=TicketStatus.OPEN,
    )
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return {"id": t.id, "status": t.status}


@router.get("/", response_model=List[dict])
async def list_tickets(
    status_filter: Optional[TicketStatus] = None,
    severity: Optional[TicketSeverity] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    q = select(SupportTicket).order_by(SupportTicket.created_at.desc())
    if status_filter:
        q = q.where(SupportTicket.status == status_filter)
    if severity:
        q = q.where(SupportTicket.severity == severity)
    res = await db.execute(q)
    items = res.scalars().all()
    return [
        {
            "id": t.id,
            "title": t.title,
            "severity": t.severity,
            "status": t.status,
            "owner": t.owner,
            "domain": t.domain,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in items
    ]


@router.post("/{ticket_id}/status", response_model=dict)
async def update_ticket_status(
    ticket_id: int,
    payload: TicketUpdateStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    res = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    t = res.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")
    t.status = payload.status
    if payload.owner is not None:
        t.owner = payload.owner
    now = datetime.utcnow()
    if payload.acknowledge and t.acknowledged_at is None:
        t.acknowledged_at = now
    if payload.resolve:
        t.resolved_at = now
    if payload.close:
        t.closed_at = now
    await db.commit()
    await db.refresh(t)
    return {"id": t.id, "status": t.status}


@router.post("/{ticket_id}/messages", response_model=dict)
async def add_ticket_message(
    ticket_id: int,
    payload: TicketAddMessage,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    res = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    t = res.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")
    upd = SupportUpdate(ticket_id=t.id, message=payload.message, author_user_id=getattr(current_user, "id", None))
    db.add(upd)
    await db.commit()
    return {"id": t.id, "message_id": upd.id if hasattr(upd, 'id') else None}


@router.get("/kpis", response_model=dict)
async def support_kpis(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    return await SupportService.compute_kpis(db)


@router.get("/templates", response_model=dict)
async def response_templates(
    current_user: User = Depends(get_current_user),
):
    return {
        "ack": "درخواست شما با شماره {ticket_id} ثبت شد و در حال بررسی است.",
        "update": "وضعیت تیکت {ticket_id}: {status} - ETA: {eta}",
        "resolve": "مشکل تیکت {ticket_id} برطرف شد؛ لطفاً بررسی کنید و در صورت باقی بودن اطلاع دهید.",
    }


