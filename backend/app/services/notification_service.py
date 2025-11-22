"""
Notification Service - email/SMS/in-app dispatch (stubs for Phase 3)
"""
from __future__ import annotations
from typing import Optional, Dict, Any

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.communication import NotificationPreference


class NotificationService:
    @staticmethod
    async def get_preferences(db: AsyncSession, user_id: int) -> Optional[NotificationPreference]:
        result = await db.execute(
            select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def upsert_preferences(db: AsyncSession, user_id: int, data: Dict[str, Any]) -> NotificationPreference:
        pref = await NotificationService.get_preferences(db, user_id)
        if pref is None:
            pref = NotificationPreference(user_id=user_id)
            db.add(pref)
        for key, value in data.items():
            if hasattr(pref, key):
                setattr(pref, key, value)
        await db.commit()
        await db.refresh(pref)
        return pref

    @staticmethod
    async def send_email(to_email: str, subject: str, body: str) -> bool:
        # Stub: integrate with real provider in production
        await asyncio.sleep(0)  # yield
        return True

    @staticmethod
    async def send_sms(to_number: str, body: str) -> bool:
        # Stub: integrate with real SMS provider
        await asyncio.sleep(0)
        return True

