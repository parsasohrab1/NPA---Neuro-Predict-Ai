"""
Data Lifecycle Service - Archiving and Retention
"""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import shutil

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..core.config import settings
from ..models.longitudinal import LongitudinalReport


class DataLifecycleService:
    @staticmethod
    async def archive_reports_older_than(db: AsyncSession, days: int = 540) -> Dict[str, Any]:
        """
        Move report files older than N days to an archive directory to reduce hot storage usage.
        Updates file paths in DB.
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await db.execute(
            select(LongitudinalReport).where(LongitudinalReport.created_at < cutoff)
        )
        reports: List[LongitudinalReport] = result.scalars().all()
        archive_root = Path("archives/reports")
        archive_root.mkdir(parents=True, exist_ok=True)

        moved: List[int] = []
        for r in reports:
            try:
                # Move main file
                if r.file_path and Path(r.file_path).exists():
                    dst = archive_root / Path(r.file_path).name
                    shutil.move(r.file_path, dst)
                    r.file_path = str(dst)
                # Move pdf variant
                if r.pdf_path and Path(r.pdf_path).exists():
                    dst_pdf = archive_root / Path(r.pdf_path).name
                    shutil.move(r.pdf_path, dst_pdf)
                    r.pdf_path = str(dst_pdf)
                # Move heatmap
                if r.heatmap_path and Path(r.heatmap_path).exists():
                    dst_heat = archive_root / Path(r.heatmap_path).name
                    shutil.move(r.heatmap_path, dst_heat)
                    r.heatmap_path = str(dst_heat)
                moved.append(r.id)
            except Exception:
                continue

        if moved:
            await db.commit()
        return {"moved_count": len(moved), "report_ids": moved, "cutoff": cutoff.isoformat()}


