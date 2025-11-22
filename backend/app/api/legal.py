"""
Legal API: Terms of Use (FA) - fetch and accept
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db.session import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.legal import UserTermsAcceptance

router = APIRouter(prefix="/legal", tags=["Legal"])

TERMS_VERSION = "fa-1.0-2024-11-20"

# Concise summary/version pointer. Full text lives in docs and UI.
TERMS_SUMMARY = {
    "version": TERMS_VERSION,
    "title": "شرایط استفاده NeuroPredict-AI",
    "sections": [
        "صلاحیت و حساب کاربری (RBAC، مسئولیت حساب)",
        "استفاده مجاز (اهداف بالینی/پژوهشی؛ منع سوءاستفاده)",
        "محتوا و داده (مالکیت سازمان، دقت ورودی)",
        "هشدارهای پزشکی (ابزار کمکی؛ جایگزین تشخیص نیست)",
        "دسترس‌پذیری و تغییر سرویس",
        "محدودیت مسئولیت (as-is)",
        "امنیت (MFA/رمز عبور/گزارش رخداد)",
        "خاتمه دسترسی",
        "حقوق مالکیت فکری",
        "قانون حاکم و حل اختلاف",
        "تغییرات شرایط",
    ],
}


class AcceptTermsRequest(BaseModel):
    version: str


@router.get("/terms", response_model=dict)
async def get_terms_summary():
    return TERMS_SUMMARY


@router.post("/terms/accept", response_model=dict, status_code=status.HTTP_201_CREATED)
async def accept_terms(
    payload: AcceptTermsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.version != TERMS_VERSION:
        raise HTTPException(status_code=400, detail="Invalid terms version")
    # Upsert-like behavior: if already accepted, return existing
    existing = await db.execute(
        select(UserTermsAcceptance).where(
            UserTermsAcceptance.user_id == current_user.id,
            UserTermsAcceptance.version == payload.version,
        )
    )
    row = existing.scalar_one_or_none()
    if row:
        return {"accepted": True, "version": payload.version}

    rec = UserTermsAcceptance(user_id=current_user.id, version=payload.version)
    db.add(rec)
    await db.commit()
    return {"accepted": True, "version": payload.version}


