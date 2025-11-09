"""
Longitudinal Tracking Service
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

import numpy as np
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.config import settings
from ..models.longitudinal import (
    AlertSeverity,
    AlertType,
    LongitudinalAlert,
    LongitudinalEpisode,
    LongitudinalEpisodeStatus,
    LongitudinalMetric,
    LongitudinalVisit,
    LongitudinalVisitType,
    MetricCategory,
    LongitudinalReport,
    LongitudinalReportFormat,
    LongitudinalReportStatus,
)
from ..schemas.longitudinal import (
    LongitudinalEpisodeCreate,
    LongitudinalMetricCreate,
    LongitudinalVisitCreate,
)
from ..services.image_processing_service import image_processing_service


class LongitudinalTrackingService:
    async def list_episodes(self, db: AsyncSession, patient_id: int) -> List[LongitudinalEpisode]:
        stmt: Select[LongitudinalEpisode] = (
            select(LongitudinalEpisode)
            .where(LongitudinalEpisode.patient_id == patient_id)
            .order_by(LongitudinalEpisode.start_date.nullslast())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_episode(
        self,
        db: AsyncSession,
        episode_id: int,
        patient_id: Optional[int] = None,
    ) -> Optional[LongitudinalEpisode]:
        stmt = (
            select(LongitudinalEpisode)
            .options(
                selectinload(LongitudinalEpisode.visits).selectinload(LongitudinalVisit.metrics),
                selectinload(LongitudinalEpisode.alerts),
            )
            .where(LongitudinalEpisode.id == episode_id)
        )
        if patient_id is not None:
            stmt = stmt.where(LongitudinalEpisode.patient_id == patient_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_episode(
        self,
        db: AsyncSession,
        patient_id: int,
        payload: LongitudinalEpisodeCreate,
    ) -> LongitudinalEpisode:
        episode = LongitudinalEpisode(
            patient_id=patient_id,
            title=payload.title,
            start_date=payload.start_date,
            end_date=payload.end_date,
            status=LongitudinalEpisodeStatus.ACTIVE,
        )
        db.add(episode)
        await db.commit()
        await db.refresh(episode)
        return episode

    async def add_visit(
        self,
        db: AsyncSession,
        episode_id: int,
        payload: LongitudinalVisitCreate,
    ) -> LongitudinalVisit:
        visit = LongitudinalVisit(
            episode_id=episode_id,
            medical_record_id=payload.medical_record_id,
            imaging_study_id=payload.imaging_study_id,
            prediction_id=payload.prediction_id,
            visit_date=payload.visit_date or datetime.utcnow(),
            visit_type=payload.visit_type,
            notes=payload.notes,
            progression_score=payload.progression_score,
        )
        db.add(visit)
        await db.commit()
        await db.refresh(visit)
        return visit

    async def add_metrics(
        self,
        db: AsyncSession,
        visit_id: int,
        metrics: Iterable[LongitudinalMetricCreate],
    ) -> List[LongitudinalMetric]:
        metric_entities: List[LongitudinalMetric] = []
        for metric in metrics:
            metric_entities.append(
                LongitudinalMetric(
                    visit_id=visit_id,
                    metric_type=metric.metric_type,
                    metric_key=metric.metric_key,
                    metric_value=metric.metric_value,
                    metric_payload=metric.metric_payload,
                    unit=metric.unit,
                    z_score=metric.z_score,
                )
            )
        db.add_all(metric_entities)
        await db.commit()
        for entity in metric_entities:
            await db.refresh(entity)

        visit_stmt = select(LongitudinalVisit).where(LongitudinalVisit.id == visit_id)
        visit_result = await db.execute(visit_stmt)
        visit = visit_result.scalar_one()
        await self._evaluate_alerts_for_visit(db, visit, metric_entities)
        return metric_entities

    async def get_timeline(self, db: AsyncSession, episode_id: int) -> List[LongitudinalVisit]:
        stmt = (
            select(LongitudinalVisit)
            .options(selectinload(LongitudinalVisit.metrics))
            .where(LongitudinalVisit.episode_id == episode_id)
            .order_by(LongitudinalVisit.visit_date)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_metric_trend(
        self,
        db: AsyncSession,
        episode_id: int,
        metric_key: str,
        metric_type: Optional[MetricCategory] = None,
    ) -> List[LongitudinalMetric]:
        stmt = (
            select(LongitudinalMetric)
            .join(LongitudinalVisit)
            .where(
                LongitudinalVisit.episode_id == episode_id,
                LongitudinalMetric.metric_key == metric_key,
            )
            .order_by(LongitudinalVisit.visit_date)
        )
        if metric_type:
            stmt = stmt.where(LongitudinalMetric.metric_type == metric_type)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_episode_visit_count(self, db: AsyncSession, episode_id: int) -> int:
        stmt = select(func.count(LongitudinalVisit.id)).where(LongitudinalVisit.episode_id == episode_id)
        result = await db.execute(stmt)
        return result.scalar_one()

    async def compare_imaging(
        self,
        db: AsyncSession,
        episode_id: int,
        visit_a_id: int,
        visit_b_id: int,
    ) -> Dict[str, object]:
        stmt = (
            select(LongitudinalVisit)
            .options(selectinload(LongitudinalVisit.imaging_study))
            .where(
                LongitudinalVisit.episode_id == episode_id,
                LongitudinalVisit.id.in_([visit_a_id, visit_b_id]),
            )
        )
        result = await db.execute(stmt)
        visits = {visit.id: visit for visit in result.scalars()}

        visit_a = visits.get(visit_a_id)
        visit_b = visits.get(visit_b_id)

        if not visit_a or not visit_b:
            raise ValueError("visit_not_found")
        if visit_a.episode_id != episode_id or visit_b.episode_id != episode_id:
            raise ValueError("episode_mismatch")
        if visit_a.imaging_study is None or visit_b.imaging_study is None:
            raise ValueError("imaging_not_available")

        comparison = image_processing_service.compare_dicom_files(
            visit_a.imaging_study.dicom_path,
            visit_b.imaging_study.dicom_path,
        )
        comparison.update(
            {
                "episode_id": episode_id,
                "visit_a_id": visit_a_id,
                "visit_b_id": visit_b_id,
                "visit_a_date": visit_a.visit_date,
                "visit_b_date": visit_b.visit_date,
            }
        )
        return comparison

    async def get_alerts(self, db: AsyncSession, episode_id: int) -> List[LongitudinalAlert]:
        stmt = (
            select(LongitudinalAlert)
            .where(LongitudinalAlert.episode_id == episode_id)
            .order_by(LongitudinalAlert.created_at.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def acknowledge_alert(self, db: AsyncSession, alert_id: int) -> Optional[LongitudinalAlert]:
        stmt = select(LongitudinalAlert).where(LongitudinalAlert.id == alert_id)
        result = await db.execute(stmt)
        alert = result.scalar_one_or_none()
        if alert is None:
            return None
        alert.acknowledged_at = datetime.utcnow()
        await db.commit()
        await db.refresh(alert)
        return alert

    async def get_progression_summary(
        self,
        db: AsyncSession,
        episode_id: int,
        metric_keys: Optional[Sequence[str]] = None,
    ) -> Dict[str, Dict[str, Optional[float]]]:
        keys = metric_keys or ["mmse", "amyloid_beta", "parkinson_risk_score"]
        summary: Dict[str, Dict[str, Optional[float]]] = {}
        for key in keys:
            metrics = await self.get_metric_trend(db, episode_id, key)
            if not metrics:
                summary[key] = {
                    "slope": None,
                    "latest_value": None,
                    "latest_recorded_at": None,
                }
                continue
            slope = self._compute_slope(metrics)
            latest = metrics[-1]
            summary[key] = {
                "slope": slope,
                "latest_value": latest.metric_value,
                "latest_recorded_at": latest.visit.visit_date if latest.visit else None,
            }
        return summary

    async def create_report(
        self,
        db: AsyncSession,
        episode_id: int,
        created_by: Optional[int],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        report_format: LongitudinalReportFormat = LongitudinalReportFormat.EXCEL,
    ) -> LongitudinalReport:
        timeline = await self.get_timeline(db, episode_id)
        if not timeline:
            raise ValueError("no_data")

        visits_in_range = [
            visit
            for visit in timeline
            if (start_date is None or visit.visit_date >= start_date)
            and (end_date is None or visit.visit_date <= end_date)
        ]
        if not visits_in_range:
            raise ValueError("no_data_in_range")

        metrics_summary: Dict[str, Dict[str, Optional[float]]] = {}
        for key in ["mmse", "amyloid_beta", "parkinson_risk_score"]:
            metrics = await self.get_metric_trend(db, episode_id, key)
            filtered = [
                metric
                for metric in metrics
                if metric.visit and metric.visit in visits_in_range and metric.metric_value is not None
            ]
            if not filtered:
                metrics_summary[key] = {}
                continue
            values = [metric.metric_value for metric in filtered if metric.metric_value is not None]
            slope = self._compute_slope(filtered)
            metrics_summary[key] = {
                "average": float(np.mean(values)) if values else None,
                "minimum": float(np.min(values)) if values else None,
                "maximum": float(np.max(values)) if values else None,
                "slope": slope,
                "latest": filtered[-1].metric_value,
            }

        summary_payload = {
            "episode_id": episode_id,
            "range": {
                "from": start_date.isoformat() if start_date else None,
                "to": end_date.isoformat() if end_date else None,
            },
            "metrics": metrics_summary,
            "visit_count": len(visits_in_range),
            "generated_at": datetime.utcnow().isoformat(),
        }

        reports_dir = Path(settings.REPORTS_DIR)
        reports_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        base_name = f"episode_{episode_id}_{timestamp}"

        excel_path = reports_dir / f"{base_name}.xlsx"
        pdf_path = reports_dir / f"{base_name}.pdf"

        file_path: Path
        pdf_path_str: Optional[str] = None

        if report_format == LongitudinalReportFormat.PDF:
            self._write_pdf_report(pdf_path, summary_payload)
            file_path = pdf_path
        else:
            self._write_excel_report(excel_path, summary_payload)
            file_path = excel_path
            # Generate companion PDF for quick preview
            self._write_pdf_report(pdf_path, summary_payload)
            pdf_path_str = str(pdf_path)

        report = LongitudinalReport(
            episode_id=episode_id,
            created_by=created_by,
            start_date=start_date,
            end_date=end_date,
            report_type="summary",
            format=report_format,
            status=LongitudinalReportStatus.COMPLETED,
            file_path=str(file_path),
            pdf_path=pdf_path_str,
            summary=summary_payload,
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)
        return report

    async def list_reports(self, db: AsyncSession, episode_id: int) -> List[LongitudinalReport]:
        stmt = (
            select(LongitudinalReport)
            .where(LongitudinalReport.episode_id == episode_id)
            .order_by(LongitudinalReport.created_at.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_report(self, db: AsyncSession, report_id: int) -> Optional[LongitudinalReport]:
        stmt = select(LongitudinalReport).where(LongitudinalReport.id == report_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def _evaluate_alerts_for_visit(
        self,
        db: AsyncSession,
        visit: LongitudinalVisit,
        new_metrics: Iterable[LongitudinalMetric],
    ) -> None:
        metric_keys = {metric.metric_key for metric in new_metrics if metric.metric_value is not None}
        if not metric_keys:
            return

        for metric_key in metric_keys:
            metrics = await self.get_metric_trend(db, visit.episode_id, metric_key)
            if len(metrics) < 2:
                continue
            latest = metrics[-1]
            previous = metrics[-2]
            if latest.metric_value is None or previous.metric_value is None:
                continue

            delta = latest.metric_value - previous.metric_value
            previous_date = previous.visit.visit_date if previous.visit else latest.visit.visit_date
            days = (latest.visit.visit_date - previous_date).days if latest.visit else 0
            days = max(days, 1)
            rate = delta / days

            alert_payload = self._evaluate_alert_rule(metric_key, delta, rate)
            if alert_payload is None:
                continue

            existing_stmt = (
                select(LongitudinalAlert)
                .where(
                    LongitudinalAlert.episode_id == visit.episode_id,
                    LongitudinalAlert.metric_key == metric_key,
                    LongitudinalAlert.visit_id == latest.visit_id,
                    LongitudinalAlert.acknowledged_at.is_(None),
                )
            )
            existing_result = await db.execute(existing_stmt)
            if existing_result.scalar_one_or_none():
                continue

            alert = LongitudinalAlert(
                episode_id=visit.episode_id,
                visit_id=latest.visit_id,
                metric_key=metric_key,
                alert_type=AlertType.PROGRESSION_SPEED,
                severity=alert_payload["severity"],
                message=alert_payload["message"],
            )
            db.add(alert)
            await db.commit()

    def _evaluate_alert_rule(
        self,
        metric_key: str,
        delta: float,
        rate_per_day: float,
    ) -> Optional[Dict[str, AlertSeverity]]:
        metric_key_lower = metric_key.lower()
        if metric_key_lower == "mmse":
            if delta <= -3 or rate_per_day <= -1:
                return {
                    "severity": AlertSeverity.HIGH,
                    "message": "Rapid decline in MMSE score detected.",
                }
            if delta <= -2 or rate_per_day <= -0.5:
                return {
                    "severity": AlertSeverity.MEDIUM,
                    "message": "Noticeable decline in MMSE score detected.",
                }
        elif metric_key_lower in {"amyloid_beta", "tau_protein"}:
            if delta >= 150 or rate_per_day >= 30:
                return {
                    "severity": AlertSeverity.HIGH,
                    "message": f"Sharp increase in {metric_key} levels observed.",
                }
            if delta >= 80 or rate_per_day >= 15:
                return {
                    "severity": AlertSeverity.MEDIUM,
                    "message": f"Rising {metric_key} levels observed.",
                }
        elif "risk" in metric_key_lower:
            if delta >= 0.2 or rate_per_day >= 0.05:
                return {
                    "severity": AlertSeverity.HIGH,
                    "message": f"Risk score increased significantly ({metric_key}).",
                }
            if delta >= 0.1 or rate_per_day >= 0.03:
                return {
                    "severity": AlertSeverity.MEDIUM,
                    "message": f"Risk score trending upward ({metric_key}).",
                }
        return None

    def _compute_slope(self, metrics: List[LongitudinalMetric]) -> Optional[float]:
        if len(metrics) < 2:
            return None
        x: List[float] = []
        y: List[float] = []
        base_visit = metrics[0].visit
        base_date = base_visit.visit_date if base_visit else None
        if base_date is None:
            return None
        for metric in metrics:
            if metric.metric_value is None or metric.visit is None:
                continue
            delta_days = (metric.visit.visit_date - base_date).total_seconds() / 86400.0
            x.append(delta_days)
            y.append(metric.metric_value)
        if len(x) < 2:
            return None
        slope, _ = np.polyfit(np.array(x, dtype=float), np.array(y, dtype=float), 1)
        return float(slope)

    def _write_excel_report(self, path: Path, summary: Dict[str, object]) -> None:
        metrics = summary.get("metrics", {})
        rows = []
        for key, stats in metrics.items():
            rows.append(
                {
                    "Metric": key,
                    "Average": stats.get("average"),
                    "Minimum": stats.get("minimum"),
                    "Maximum": stats.get("maximum"),
                    "Slope": stats.get("slope"),
                    "Latest": stats.get("latest"),
                }
            )
        df = pd.DataFrame(rows)
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Metrics Summary")
            meta = pd.DataFrame(
                [
                    {"Field": "Episode ID", "Value": summary.get("episode_id")},
                    {"Field": "From", "Value": summary.get("range", {}).get("from")},
                    {"Field": "To", "Value": summary.get("range", {}).get("to")},
                    {"Field": "Generated At", "Value": summary.get("generated_at")},
                    {"Field": "Visit Count", "Value": summary.get("visit_count")},
                ]
            )
            meta.to_excel(writer, index=False, sheet_name="Metadata")

    def _write_pdf_report(self, path: Path, summary: Dict[str, object]) -> None:
        c = canvas.Canvas(str(path), pagesize=letter)
        c.setTitle("Longitudinal Report")
        width, height = letter
        margin = 40
        y = height - margin

        c.setFont("Helvetica-Bold", 16)
        c.drawString(margin, y, "Longitudinal Episode Report")
        y -= 30

        c.setFont("Helvetica", 10)
        range_info = summary.get("range", {})
        c.drawString(margin, y, f"Generated at: {summary.get('generated_at')}")
        y -= 14
        c.drawString(
            margin,
            y,
            f"Range: {range_info.get('from') or 'Start'} → {range_info.get('to') or 'Latest'}",
        )
        y -= 24

        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, "Metrics Summary")
        y -= 20

        c.setFont("Helvetica", 10)
        metrics = summary.get("metrics", {})
        for key, stats in metrics.items():
            if y < margin + 80:
                c.showPage()
                y = height - margin
                c.setFont("Helvetica", 10)
            c.drawString(margin, y, f"- {key.upper()}")
            y -= 14
            c.drawString(margin + 20, y, f"Average: {stats.get('average')}")
            y -= 12
            c.drawString(margin + 20, y, f"Min/Max: {stats.get('minimum')} / {stats.get('maximum')}")
            y -= 12
            c.drawString(margin + 20, y, f"Slope: {stats.get('slope')}")
            y -= 18

        c.showPage()
        c.save()


longitudinal_service = LongitudinalTrackingService()

