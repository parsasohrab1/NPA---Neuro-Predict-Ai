"""
Notification Service - email/SMS/in-app dispatch

Honesty: in non-DEBUG environments, unconfigured providers return False
(or raise) instead of pretending success. DEBUG may stub-succeed for local demos.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..core.config import settings
from ..models.communication import NotificationPreference

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    async def get_preferences(db: AsyncSession, user_id: int) -> Optional[NotificationPreference]:
        result = await db.execute(
            select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def upsert_preferences(
        db: AsyncSession, user_id: int, data: Dict[str, Any]
    ) -> NotificationPreference:
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
    def _email_configured() -> bool:
        return bool(settings.SMTP_HOST and settings.SMTP_FROM)

    @staticmethod
    def _sms_configured() -> bool:
        return bool(settings.SMS_PROVIDER_URL and settings.SMS_API_KEY)

    @staticmethod
    async def send_email(to_email: str, subject: str, body: str) -> bool:
        """
        Send email via SMTP when configured.

        DEBUG + unconfigured: returns True (local stub).
        Production/non-DEBUG + unconfigured: returns False.
        """
        await asyncio.sleep(0)
        if not NotificationService._email_configured():
            if settings.DEBUG:
                logger.debug(
                    "SMTP not configured; DEBUG stub accepting email to %s", to_email
                )
                return True
            logger.warning(
                "SMTP not configured (set SMTP_HOST / SMTP_FROM); refusing email send"
            )
            return False

        # Provider wiring is still partial — do not claim success without a real client.
        if settings.DEBUG:
            logger.info(
                "SMTP configured (%s) but client not implemented; DEBUG stub for %s",
                settings.SMTP_HOST,
                to_email,
            )
            return True

        logger.error(
            "SMTP is configured but outbound email client is not implemented; "
            "refusing to pretend success in non-DEBUG"
        )
        return False

    @staticmethod
    async def send_sms(to_number: str, body: str) -> bool:
        """
        Send SMS when provider is configured.

        DEBUG + unconfigured: returns True (local stub).
        Production/non-DEBUG + unconfigured: returns False.
        """
        await asyncio.sleep(0)
        if not NotificationService._sms_configured():
            if settings.DEBUG:
                logger.debug(
                    "SMS provider not configured; DEBUG stub accepting SMS to %s",
                    to_number,
                )
                return True
            logger.warning(
                "SMS provider not configured (set SMS_PROVIDER_URL / SMS_API_KEY); "
                "refusing SMS send"
            )
            return False

        if settings.DEBUG:
            logger.info(
                "SMS provider configured (%s) but client not implemented; DEBUG stub for %s",
                settings.SMS_PROVIDER_URL,
                to_number,
            )
            return True

        logger.error(
            "SMS provider is configured but client is not implemented; "
            "refusing to pretend success in non-DEBUG"
        )
        return False
