"""
Maintenance & Periodic Update Service
Implements routine tasks per MAINTENANCE_AND_UPDATE_PLAN_FA.md
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path
import shutil

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func

from ..core.config import settings
from .monitoring_service import MonitoringService
from .backup_service import BackupService


class MaintenanceService:
    @staticmethod
    async def weekly_review(db: AsyncSession) -> Dict[str, Any]:
        """
        - Review alerts and high-severity incidents (proxy via security_logs count)
        - Check backup health and disk/DB/Redis capacity (via monitoring)
        - Summarize SLA/SLO proxy (latency/errors via MonitoringService)
        """
        health = await MonitoringService.get_health_status(db)
        metrics = await MonitoringService.get_metrics(db)
        backup_verify = await BackupService.verify_latest_full_backup(backup_dir=settings.BACKUP_DIR)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "health": health,
            "metrics": metrics.get("metrics", {}),
            "backup_verify": backup_verify,
        }

    @staticmethod
    async def biweekly_security_maintenance() -> Dict[str, Any]:
        """
        - Placeholder: run SAST/DAST externally in CI; here we can rotate simple logs or prune old artefacts.
        - Clean old logs exceeding retention (default 90 days INFO retention approximated by size/time).
        """
        log_dir = Path("logs")
        removed = []
        if log_dir.exists():
            for p in log_dir.glob("*.log*"):
                try:
                    if p.stat().st_mtime < (datetime.utcnow() - timedelta(days=90)).timestamp():
                        removed.append(p.name)
                        p.unlink(missing_ok=True)  # type: ignore[arg-type]
                except Exception:
                    continue
        return {"removed_logs": removed}

    @staticmethod
    async def monthly_db_maintenance(db: AsyncSession) -> Dict[str, Any]:
        """
        - Run lightweight ANALYZE and VACUUM recommendations proxy (only when using Postgres).
        - This is a placeholder that records table sizes and returns hints; actual VACUUM/REINDEX should be done by DBA or cron.
        """
        sizes: Dict[str, Any] = {}
        try:
            # Works on Postgres; on sqlite this will fail and be ignored gracefully.
            result = await db.execute(text("SELECT relname AS table, reltuples::bigint AS est_rows FROM pg_class WHERE relkind='r' ORDER BY reltuples DESC LIMIT 10"))
            sizes["top_tables"] = [{"table": r[0], "estimated_rows": int(r[1])} for r in result.fetchall()]
        except Exception:
            sizes["top_tables"] = []
        return {"tables": sizes}

    @staticmethod
    async def monthly_cost_optimization() -> Dict[str, Any]:
        """
        - Apply simple retention policies on Prometheus/ELK data directories if present (simulation via size report).
        """
        report: Dict[str, Any] = {}
        for name, path in [("prometheus", Path("monitoring/prometheus_data")), ("elasticsearch", Path("elasticsearch_data"))]:
            try:
                total = 0
                if path.exists():
                    for p in path.rglob("*"):
                        if p.is_file():
                            total += p.stat().st_size
                report[name] = {"bytes": total}
            except Exception:
                report[name] = {"bytes": None}
        return report

    @staticmethod
    async def quarterly_dr_drill() -> Dict[str, Any]:
        """
        - Trigger backup verification as a proxy for DR Drill.
        """
        verify = await BackupService.verify_latest_full_backup(backup_dir=settings.BACKUP_DIR)
        return {"verify": verify}


