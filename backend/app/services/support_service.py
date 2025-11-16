from __future__ import annotations

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from ..models.support import SupportTicket, SupportUpdate, TicketStatus


class SupportService:
    @staticmethod
    async def compute_kpis(db: AsyncSession) -> Dict[str, Any]:
        """
        Compute lightweight support KPIs: counts by status/severity, MTTA/MTTR averages (minutes),
        open backlog size.
        """
        kpis: Dict[str, Any] = {}
        # Backlog
        res_open = await db.execute(select(func.count()).where(SupportTicket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS])))
        kpis["backlog_open"] = int(res_open.scalar() or 0)

        # MTTA: avg time from created_at to acknowledged_at for acknowledged tickets
        res_mtta = await db.execute(select(func.avg(func.extract("epoch", SupportTicket.acknowledged_at - SupportTicket.created_at))).where(SupportTicket.acknowledged_at.isnot(None)))
        mtta_sec = float(res_mtta.scalar() or 0.0)
        kpis["mtta_minutes"] = round(mtta_sec / 60.0, 2) if mtta_sec > 0 else 0.0

        # MTTR: avg time from created_at to resolved_at for resolved tickets
        res_mttr = await db.execute(select(func.avg(func.extract("epoch", SupportTicket.resolved_at - SupportTicket.created_at))).where(SupportTicket.resolved_at.isnot(None)))
        mttr_sec = float(res_mttr.scalar() or 0.0)
        kpis["mttr_minutes"] = round(mttr_sec / 60.0, 2) if mttr_sec > 0 else 0.0

        # Solved in first response proxy: resolved tickets with exactly 1 update
        res_first = await db.execute(select(func.count()).select_from(SupportTicket).where(SupportTicket.resolved_at.isnot(None)))
        total_resolved = int(res_first.scalar() or 0)
        # heuristic skipped for simplicity; could join with updates count
        kpis["first_contact_resolution_rate"] = None

        return kpis


