from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..models.rum import RUMEvent, UserFeedback


class RUMService:
    @staticmethod
    async def ingest_events(db: AsyncSession, events: List[Dict[str, Any]]) -> int:
        count = 0
        for ev in events:
            item = RUMEvent(
                event_type=str(ev.get("type"))[:64],
                value=str(ev.get("value"))[:64] if ev.get("value") is not None else None,
                metadata=ev.get("meta") or {},
                sampled="true" if ev.get("sampled", True) else "false",
            )
            db.add(item)
            count += 1
        if count:
            await db.commit()
        return count

    @staticmethod
    async def submit_feedback(db: AsyncSession, rating: Optional[int], comment: Optional[str], context: Optional[Dict[str, Any]]) -> int:
        fb = UserFeedback(
            rating=rating,
            comment=(comment or '')[:2000],
            context=context or {},
        )
        db.add(fb)
        await db.commit()
        await db.refresh(fb)
        return fb.id

    @staticmethod
    async def metrics_summary(db: AsyncSession, hours: int = 24) -> Dict[str, Any]:
        since = datetime.utcnow() - timedelta(hours=hours)
        out: Dict[str, Any] = {"since": since.isoformat()}
        # Count by type
        stmt = select(RUMEvent.event_type, func.count()).where(RUMEvent.created_at >= since).group_by(RUMEvent.event_type)
        res = await db.execute(stmt)
        out["counts_by_type"] = {row[0]: row[1] for row in res.fetchall()}
        # Basic JS error count
        err_stmt = select(func.count()).where(RUMEvent.event_type == "js_error", RUMEvent.created_at >= since)
        out["js_errors"] = (await db.execute(err_stmt)).scalar() or 0
        # Feedback count and avg rating
        fb_count = await db.execute(select(func.count()).select_from(UserFeedback).where(UserFeedback.created_at >= since))
        out["feedback_count"] = fb_count.scalar() or 0
        avg_rating = await db.execute(select(func.avg(UserFeedback.rating)).where(UserFeedback.created_at >= since))
        out["avg_rating"] = float(avg_rating.scalar() or 0)
        return out


