"""
Notifications API - preferences and test sends
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..core.security import get_current_user, require_role
from ..models.user import User
from ..services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class PreferencesUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    on_prediction_ready: Optional[bool] = None
    on_report_ready: Optional[bool] = None
    on_longitudinal_alert: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None


@router.get("/preferences")
async def get_my_prefs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pref = await NotificationService.get_preferences(db, current_user.id)
    return pref or {}


@router.put("/preferences")
async def update_my_prefs(
    payload: PreferencesUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pref = await NotificationService.upsert_preferences(db, current_user.id, payload.dict(exclude_none=True))
    return {"updated": True, "preferences": pref}


class EmailTest(BaseModel):
    to_email: str
    subject: str
    body: str


@router.post("/test/email")
async def send_test_email(
    payload: EmailTest,
    current_user: User = Depends(require_role("admin")),
):
    ok = await NotificationService.send_email(payload.to_email, payload.subject, payload.body)
    if not ok:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Email send failed")
    return {"sent": True}


class SMSTest(BaseModel):
    to_number: str
    body: str


@router.post("/test/sms")
async def send_test_sms(
    payload: SMSTest,
    current_user: User = Depends(require_role("admin")),
):
    ok = await NotificationService.send_sms(payload.to_number, payload.body)
    if not ok:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="SMS send failed")
    return {"sent": True}


