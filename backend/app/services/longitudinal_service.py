    async def _create_summary_report(
        self,
        db: AsyncSession,
        episode_id: int,
        created_by: Optional[int],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        report_format: LongitudinalReportFormat,
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
        charts_payload: Dict[str, List[Dict[str, Any]]] = {}
        for key in ["mmse", "amyloid_beta", "parkinson_risk_score"]:
            metrics = await self.get_metric_trend(db, episode_id, key)
            filtered = [
                metric
                for metric in metrics
                if metric.visit and metric.visit in visits_in_range and metric.metric_value is not None
            ]
            if not filtered:
                metrics_summary[key] = {}
                charts_payload[key] = []
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
            charts_payload[key] = [
                {
                    "visit_id": metric.visit_id,
                    "visit_date": metric.visit.visit_date.isoformat() if metric.visit else None,
                    "value": metric.metric_value,
                }
                for metric in filtered
            ]

        summary_payload = {
            "episode_id": episode_id,
            "report_type": "summary",
            "range": {
                "from": start_date.isoformat() if start_date else None,
                "to": end_date.isoformat() if end_date else None,
            },
            "metrics": metrics_summary,
            "visit_count": len(visits_in_range),
            "generated_at": datetime.utcnow().isoformat(),
        }

        reports_dir, base_name = self._prepare_report_paths(episode_id)
        excel_path = reports_dir / f"{base_name}.xlsx"
        pdf_path = reports_dir / f"{base_name}.pdf"

        file_path: Path
        pdf_path_str: Optional[str] = None

        if report_format == LongitudinalReportFormat.PDF:
            self._write_pdf_report(pdf_path, summary_payload, charts_payload=charts_payload)
            file_path = pdf_path
        else:
            self._write_excel_report(excel_path, summary_payload, charts_payload=charts_payload)
            file_path = excel_path
            self._write_pdf_report(pdf_path, summary_payload, charts_payload=charts_payload)
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
            charts_payload=charts_payload,
            summary=summary_payload,
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)
        return report

    def _prepare_report_paths(self, episode_id: int) -> Tuple[Path, str]:
        reports_dir = Path(settings.REPORTS_DIR)
        reports_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        base_name = f"episode_{episode_id}_{timestamp}"
        return reports_dir, base_name

    async def _generate_cohort_summary(
        self,
        db: AsyncSession,
        episode_id: int,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        report_type: str,
        cohort_filters: Dict[str, Any],
        comparison_filters: Dict[str, Any],
    ) -> Dict[str, Any]:
        cohort_series = await self._collect_cohort_metrics(db, cohort_filters, start_date, end_date)
        if not cohort_series:
            raise ValueError("no_data")

        summary: Dict[str, Any] = {
            "episode_id": episode_id,
            "report_type": report_type,
            "range": {
                "from": start_date.isoformat() if start_date else None,
                "to": end_date.isoformat() if end_date else None,
            },
            "generated_at": datetime.utcnow().isoformat(),
        }

        comparison_payload: Optional[Dict[str, Any]] = None
        base_series: Dict[str, Dict[str, float]]
        target_series: Dict[str, Dict[str, float]]
        heatmap_matrix: Optional[np.ndarray] = None
        x_labels: List[str] = []
        charts_payload: Dict[str, List[Dict[str, Any]]] = {}

        patient_series = await self._collect_episode_metric_series(db, episode_id, start_date, end_date)

        if report_type == "cohort_patient_vs_average":
            base_series = cohort_series
            target_series = patient_series
            comparison_payload = self._build_patient_vs_cohort_summary(base_series, target_series)
        elif report_type == "cohort_vs_cohort":
            comparison_series = await self._collect_cohort_metrics(db, comparison_filters, start_date, end_date)
            if not comparison_series:
                raise ValueError("no_comparison_data")
            base_series = cohort_series
            target_series = comparison_series
            comparison_payload = self._build_cohort_vs_cohort_summary(base_series, comparison_series)
        else:
            base_series = cohort_series
            target_series = {}

        summary["metrics"] = self._aggregate_metric_summary(base_series)
        summary["cohort_size"] = base_series.get("_meta", {}).get("count")

        if comparison_payload:
            summary["comparison"] = comparison_payload

        charts_payload = self._build_chart_payload(base_series, target_series)

        heatmap_matrix, x_labels = self._build_heatmap_matrix(base_series, target_series, report_type=report_type)
        heatmap_path = None
        if heatmap_matrix is not None and heatmap_matrix.size > 0:
            heatmap_path = self._render_heatmap(
                heatmap_matrix,
                metrics=list(m for m in base_series.keys() if not m.startswith("_")),
                time_labels=x_labels,
                prefix=f"episode_{episode_id}_{report_type}",
            )

        return {
            "summary": summary,
            "charts": charts_payload,
            "comparison": comparison_payload,
            "heatmap_path": heatmap_path,
            "cohort_definition": cohort_filters,
            "comparison_definition": comparison_filters,
        }

    async def _collect_cohort_metrics(
        self,
        db: AsyncSession,
        filters: Dict[str, Any],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
    ) -> Dict[str, List[Dict[str, Any]]]:
        filters = filters or {}

        stmt = (
            select(
                LongitudinalMetric.metric_key,
                LongitudinalMetric.metric_value,
                LongitudinalVisit.visit_date,
                Patient.id,
                Patient.patient_id,
                Patient.date_of_birth,
                Patient.gender,
                LongitudinalEpisode.id,
            )
            .join(LongitudinalVisit, LongitudinalMetric.visit_id == LongitudinalVisit.id)
            .join(LongitudinalEpisode, LongitudinalVisit.episode_id == LongitudinalEpisode.id)
            .join(Patient, LongitudinalEpisode.patient_id == Patient.id)
            .where(LongitudinalMetric.metric_value.isnot(None))
        )

        if start_date:
            stmt = stmt.where(LongitudinalVisit.visit_date >= start_date)
        if end_date:
            stmt = stmt.where(LongitudinalVisit.visit_date <= end_date)

        gender_filter = filters.get("gender")
        if gender_filter:
            try:
                stmt = stmt.where(Patient.gender == Gender(gender_filter))
            except ValueError:
                pass

        patient_ids = filters.get("patient_ids")
        if patient_ids:
            stmt = stmt.where(Patient.patient_id.in_(patient_ids))

        result = await db.execute(stmt)
        rows = result.all()

        age_min = filters.get("age_min")
        age_max = filters.get("age_max")

        buckets: Dict[str, Dict[str, List[float]]] = {}
        patient_set: set[int] = set()

        for metric_key, metric_value, visit_date, patient_db_id, _, date_of_birth, gender, episode_db_id in rows:
            if metric_value is None:
                continue

            if age_min is not None or age_max is not None:
                age = self._calculate_age(date_of_birth)
                if age is None:
                    continue
                if age_min is not None and age < age_min:
                    continue
                if age_max is not None and age > age_max:
                    continue

            date_key = visit_date.date().isoformat()
            metric_bucket = buckets.setdefault(metric_key, {})
            metric_bucket.setdefault(date_key, []).append(float(metric_value))
            patient_set.add(patient_db_id)

        series: Dict[str, List[Dict[str, Any]]] = {}
        for metric_key, date_map in buckets.items():
            items = []
            for date_key in sorted(date_map.keys()):
                values = date_map[date_key]
                items.append({"visit_date": date_key, "value": float(np.mean(values))})
            series[metric_key] = items

        series["_meta"] = {"count": len(patient_set)}
        return series

    async def _collect_episode_metric_series(
        self,
        db: AsyncSession,
        episode_id: int,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
    ) -> Dict[str, List[Dict[str, Any]]]:
        metric_keys = ["mmse", "amyloid_beta", "parkinson_risk_score"]
        series: Dict[str, List[Dict[str, Any]]] = {}
        for key in metric_keys:
            trend = await self.get_metric_trend(db, episode_id, key)
            entries: List[Dict[str, Any]] = []
            for metric in trend:
                if metric.metric_value is None or metric.visit is None:
                    continue
                visit_date = metric.visit.visit_date
                if start_date and visit_date < start_date:
                    continue
                if end_date and visit_date > end_date:
                    continue
                entries.append(
                    {
                        "visit_date": visit_date.date().isoformat(),
                        "value": float(metric.metric_value),
                    }
                )
            if entries:
                series[key] = entries
        return series

    def _build_patient_vs_cohort_summary(
        self,
        cohort_series: Dict[str, List[Dict[str, Any]]],
        patient_series: Dict[str, List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        table: List[Dict[str, Any]] = []
        for metric_key, cohort_entries in cohort_series.items():
            if metric_key.startswith("_"):
                continue
            cohort_values = [entry["value"] for entry in cohort_entries]
            patient_values = [entry["value"] for entry in patient_series.get(metric_key, [])]
            if not cohort_values:
                continue
            cohort_avg = float(np.mean(cohort_values))
            patient_avg = float(np.mean(patient_values)) if patient_values else None
            delta = patient_avg - cohort_avg if patient_avg is not None else None
            table.append(
                {
                    "metric": metric_key,
                    "cohort_average": cohort_avg,
                    "patient_average": patient_avg,
                    "delta": delta,
                }
            )
        return {"table": table}

    def _build_cohort_vs_cohort_summary(
        self,
        cohort_a: Dict[str, List[Dict[str, Any]]],
        cohort_b: Dict[str, List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        table: List[Dict[str, Any]] = []
        for metric_key, cohort_entries in cohort_a.items():
            if metric_key.startswith("_"):
                continue
            values_a = [entry["value"] for entry in cohort_entries]
            values_b = [entry["value"] for entry in cohort_b.get(metric_key, [])]
            if not values_a and not values_b:
                continue
            avg_a = float(np.mean(values_a)) if values_a else None
            avg_b = float(np.mean(values_b)) if values_b else None
            delta = None
            if avg_a is not None and avg_b is not None:
                delta = avg_a - avg_b
            table.append(
                {
                    "metric": metric_key,
                    "cohort_a_average": avg_a,
                    "cohort_b_average": avg_b,
                    "delta": delta,
                }
            )
        return {"table": table}

    def _aggregate_metric_summary(self, series: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Optional[float]]]:
        summary: Dict[str, Dict[str, Optional[float]]] = {}
        for metric_key, entries in series.items():
            if metric_key.startswith("_"):
                continue
            values = [entry["value"] for entry in entries if entry.get("value") is not None]
            if not values:
                summary[metric_key] = {}
                continue
            summary[metric_key] = {
                "average": float(np.mean(values)),
                "minimum": float(np.min(values)),
                "maximum": float(np.max(values)),
                "latest": values[-1],
                "slope": self._compute_slope_from_series(entries),
            }
        return summary

    def _build_chart_payload(
        self,
        cohort_series: Dict[str, List[Dict[str, Any]]],
        target_series: Dict[str, List[Dict[str, Any]]],
    ) -> Dict[str, List[Dict[str, Any]]]:
        payload: Dict[str, List[Dict[str, Any]]] = {}
        for metric_key, cohort_entries in cohort_series.items():
            if metric_key.startswith("_"):
                continue
            rows: List[Dict[str, Any]] = [
                {
                    "series": "cohort",
                    "visit_date": entry["visit_date"],
                    "value": entry["value"],
                }
                for entry in cohort_entries
            ]
            for entry in target_series.get(metric_key, []):
                rows.append(
                    {
                        "series": "target",
                        "visit_date": entry["visit_date"],
                        "value": entry["value"],
                    }
                )
            payload[metric_key] = rows
        return payload

    def _build_heatmap_matrix(
        self,
        cohort_series: Dict[str, List[Dict[str, Any]]],
        target_series: Dict[str, List[Dict[str, Any]]],
        report_type: str = "summary",
    ) -> Tuple[Optional[np.ndarray], List[str]]:
        metric_keys = [key for key in cohort_series.keys() if not key.startswith("_")]
        if not metric_keys:
            return None, []

        time_set = set()
        for entries in cohort_series.values():
            if isinstance(entries, list):
                for entry in entries:
                    time_set.add(entry["visit_date"])
        for entries in target_series.values():
            for entry in entries:
                time_set.add(entry["visit_date"])

        time_labels = sorted(time_set)
        if not time_labels:
            return None, []

        matrix_rows: List[List[float]] = []
        for metric_key in metric_keys:
            cohort_map = {entry["visit_date"]: entry["value"] for entry in cohort_series.get(metric_key, [])}
            target_map = {entry["visit_date"]: entry["value"] for entry in target_series.get(metric_key, [])}
            row: List[float] = []
            for label in time_labels:
                cohort_value = cohort_map.get(label, 0.0)
                if target_map:
                    target_value = target_map.get(label, 0.0)
                    if report_type == "cohort_patient_vs_average":
                        row.append(target_value - cohort_value)
                    elif report_type == "cohort_vs_cohort":
                        row.append(cohort_value - target_value)
                    else:
                        row.append(cohort_value)
                else:
                    row.append(cohort_value)
            matrix_rows.append(row)

        matrix = np.array(matrix_rows, dtype=float)
        return matrix, time_labels

    def _render_heatmap(self, matrix: np.ndarray, metrics: List[str], time_labels: List[str], prefix: str) -> str:
        reports_dir = Path(settings.REPORTS_DIR)
        reports_dir.mkdir(parents=True, exist_ok=True)
        path = reports_dir / f"{prefix}_heatmap.png"

        plt.figure(figsize=(max(6, len(time_labels) * 0.6), max(3, len(metrics) * 0.5)))
        plt.imshow(matrix, aspect="auto", cmap="coolwarm")
        plt.colorbar(label="Difference" if matrix.shape[0] > 0 else "")
        plt.xticks(range(len(time_labels)), time_labels, rotation=45, ha="right")
        plt.yticks(range(len(metrics)), [metric.upper() for metric in metrics])
        plt.tight_layout()
        plt.savefig(path, dpi=180)
        plt.close()
        return str(path)

    def _compute_slope_from_series(self, entries: List[Dict[str, Any]]) -> Optional[float]:
        if len(entries) < 2:
            return None
        first_date = datetime.fromisoformat(entries[0]["visit_date"])
        x_vals: List[float] = []
        y_vals: List[float] = []
        for entry in entries:
            visit_datetime = datetime.fromisoformat(entry["visit_date"])
            delta_days = (visit_datetime - first_date).total_seconds() / 86400.0
            x_vals.append(delta_days)
            y_vals.append(entry["value"])
        if len(x_vals) < 2:
            return None
        slope, _ = np.polyfit(np.array(x_vals, dtype=float), np.array(y_vals, dtype=float), 1)
        return float(slope)

    def _calculate_age(self, date_of_birth: Optional[date]) -> Optional[int]:
        if date_of_birth is None:
            return None
        today = datetime.utcnow().date()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        return age

    async def _create_cohort_report(
        self,
        db: AsyncSession,
        episode_id: int,
        created_by: Optional[int],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        report_format: LongitudinalReportFormat,
        report_type: str,
        cohort_filters: Dict[str, Any],
        comparison_filters: Dict[str, Any],
    ) -> LongitudinalReport:
        cohort_result = await self._generate_cohort_summary(
            db=db,
            episode_id=episode_id,
            start_date=start_date,
            end_date=end_date,
            report_type=report_type,
            cohort_filters=cohort_filters,
            comparison_filters=comparison_filters,
        )

        reports_dir, base_name = self._prepare_report_paths(episode_id)
        excel_path = reports_dir / f"{base_name}_{report_type}.xlsx"
        pdf_path = reports_dir / f"{base_name}_{report_type}.pdf"

        file_path: Path
        pdf_path_str: Optional[str] = None

        if report_format == LongitudinalReportFormat.PDF:
            self._write_pdf_report(
                pdf_path,
                cohort_result["summary"],
                charts_payload=cohort_result["charts"],
                heatmap_path=cohort_result.get("heatmap_path"),
            )
            file_path = pdf_path
        else:
            self._write_excel_report(
                excel_path,
                cohort_result["summary"],
                charts_payload=cohort_result["charts"],
                comparison_payload=cohort_result.get("comparison"),
                heatmap_path=cohort_result.get("heatmap_path"),
            )
            file_path = excel_path
            self._write_pdf_report(
                pdf_path,
                cohort_result["summary"],
                charts_payload=cohort_result["charts"],
                heatmap_path=cohort_result.get("heatmap_path"),
            )
            pdf_path_str = str(pdf_path)

        report = LongitudinalReport(
            episode_id=episode_id,
            created_by=created_by,
            start_date=start_date,
            end_date=end_date,
            report_type=report_type,
            format=report_format,
            status=LongitudinalReportStatus.COMPLETED,
            file_path=str(file_path),
            pdf_path=pdf_path_str,
            heatmap_path=cohort_result.get("heatmap_path"),
            charts_payload=cohort_result["charts"],
            summary=cohort_result["summary"],
            cohort_definition=cohort_result.get("cohort_definition"),
            comparison_definition=cohort_result.get("comparison_definition"),
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)
        return report
"""
Longitudinal Tracking Service
"""
from __future__ import annotations

from datetime import datetime, date
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy import Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

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
    LongitudinalReportSchedule,
    LongitudinalReportScheduleStatus,
    LongitudinalReportRun,
    LongitudinalReportRunStatus,
)
from ..models.patient import Patient, Gender
from ..schemas.longitudinal import (
    LongitudinalEpisodeCreate,
    LongitudinalMetricCreate,
    LongitudinalVisitCreate,
    ReportScheduleCreate,
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
        report_type: str = "summary",
        cohort_filters: Optional[Dict[str, Any]] = None,
        comparison_filters: Optional[Dict[str, Any]] = None,
    ) -> LongitudinalReport:
        if report_type == "summary":
            return await self._create_summary_report(
                db=db,
                episode_id=episode_id,
                created_by=created_by,
                start_date=start_date,
                end_date=end_date,
                report_format=report_format,
            )

        return await self._create_cohort_report(
            db=db,
            episode_id=episode_id,
            created_by=created_by,
            start_date=start_date,
            end_date=end_date,
            report_format=report_format,
            report_type=report_type,
            cohort_filters=cohort_filters or {},
            comparison_filters=comparison_filters or {},
        )

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

    async def create_schedule(
        self,
        db: AsyncSession,
        payload: "ReportScheduleCreate",
        created_by: Optional[int],
    ) -> LongitudinalReportSchedule:
        schedule = LongitudinalReportSchedule(
            name=payload.name,
            episode_id=payload.episode_id,
            report_type=payload.report_type,
            cohort_definition=payload.cohort_filters,
            comparison_definition=payload.comparison_filters,
            schedule_cron=payload.schedule_cron,
            status=LongitudinalReportScheduleStatus.ACTIVE,
            created_by=created_by,
        )
        db.add(schedule)
        await db.commit()
        await db.refresh(schedule)
        return schedule

    async def list_schedules(self, db: AsyncSession) -> List[LongitudinalReportSchedule]:
        stmt = (
            select(LongitudinalReportSchedule)
            .options(joinedload(LongitudinalReportSchedule.runs))
            .order_by(LongitudinalReportSchedule.created_at.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def update_schedule_status(
        self,
        db: AsyncSession,
        schedule_id: int,
        status: LongitudinalReportScheduleStatus,
    ) -> Optional[LongitudinalReportSchedule]:
        schedule = await db.get(LongitudinalReportSchedule, schedule_id)
        if schedule is None:
            return None
        schedule.status = status
        await db.commit()
        await db.refresh(schedule)
        return schedule

    async def delete_schedule(self, db: AsyncSession, schedule_id: int) -> bool:
        schedule = await db.get(LongitudinalReportSchedule, schedule_id)
        if schedule is None:
            return False
        await db.delete(schedule)
        await db.commit()
        return True

    async def enqueue_schedule_run(
        self,
        db: AsyncSession,
        schedule_id: int,
    ) -> Optional[LongitudinalReportRun]:
        schedule = await db.get(LongitudinalReportSchedule, schedule_id)
        if schedule is None:
            return None
        run = LongitudinalReportRun(
            schedule_id=schedule.id,
            status=LongitudinalReportRunStatus.QUEUED,
        )
        db.add(run)
        await db.commit()
        await db.refresh(run)
        return run

    async def list_schedule_runs(self, db: AsyncSession, schedule_id: int) -> List[LongitudinalReportRun]:
        stmt = (
            select(LongitudinalReportRun)
            .where(LongitudinalReportRun.schedule_id == schedule_id)
            .order_by(LongitudinalReportRun.id.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def execute_schedule_run(
        self,
        db: AsyncSession,
        run_id: int,
    ) -> Optional[LongitudinalReportRun]:
        run = await db.get(LongitudinalReportRun, run_id)
        if run is None:
            return None
        schedule = await db.get(LongitudinalReportSchedule, run.schedule_id)
        if schedule is None:
            run.status = LongitudinalReportRunStatus.FAILED
            run.error_message = "schedule_missing"
            await db.commit()
            return run

        run.status = LongitudinalReportRunStatus.RUNNING
        run.started_at = datetime.utcnow()
        await db.commit()

        try:
            report = await self.create_report(
                db=db,
                episode_id=schedule.episode_id,
                created_by=schedule.created_by,
                start_date=None,
                end_date=None,
                report_format=LongitudinalReportFormat.EXCEL,
                report_type=schedule.report_type,
                cohort_filters=schedule.cohort_definition or {},
                comparison_filters=schedule.comparison_definition or {},
            )
            run.status = LongitudinalReportRunStatus.SUCCESS
            run.report_id = report.id
            run.finished_at = datetime.utcnow()
            schedule.last_run_at = run.finished_at
            await db.commit()
            return run
        except Exception as exc:
            run.status = LongitudinalReportRunStatus.FAILED
            run.error_message = str(exc)
            run.finished_at = datetime.utcnow()
            await db.commit()
            return run

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

    def _write_excel_report(
        self,
        path: Path,
        summary: Dict[str, object],
        charts_payload: Optional[Dict[str, Any]] = None,
        comparison_payload: Optional[Dict[str, Any]] = None,
        heatmap_path: Optional[str] = None,
    ) -> None:
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

            if charts_payload:
                for metric_key, datapoints in charts_payload.items():
                    df_chart = pd.DataFrame(datapoints)
                    df_chart.to_excel(writer, index=False, sheet_name=f"Chart_{metric_key[:28]}")

            if comparison_payload:
                comp_df = pd.DataFrame(comparison_payload.get("table", []))
                if not comp_df.empty:
                    comp_df.to_excel(writer, index=False, sheet_name="Cohort Comparison")

            if heatmap_path and Path(heatmap_path).exists():
                heatmap_sheet = pd.DataFrame([{"heatmap_path": heatmap_path}])
                heatmap_sheet.to_excel(writer, index=False, sheet_name="Heatmap Reference")

    def _write_pdf_report(
        self,
        path: Path,
        summary: Dict[str, object],
        charts_payload: Optional[Dict[str, Any]] = None,
        heatmap_path: Optional[str] = None,
    ) -> None:
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

        if charts_payload:
            for metric_key, datapoints in charts_payload.items():
                c.showPage()
                c.setFont("Helvetica-Bold", 12)
                c.drawString(margin, height - margin - 20, f"Chart Data – {metric_key}")
                c.setFont("Helvetica", 9)
                y = height - margin - 40
                for point in datapoints[:25]:
                    c.drawString(
                        margin,
                        y,
                        f"{point.get('visit_date', '-')}: {point.get('value', '-')}",
                    )
                    y -= 12
                    if y < margin + 40:
                        c.showPage()
                        c.setFont("Helvetica", 9)
                        y = height - margin - 40

        if heatmap_path and Path(heatmap_path).exists():
            c.showPage()
            c.setFont("Helvetica-Bold", 12)
            c.drawString(margin, height - margin - 20, "Heatmap")
            try:
                c.drawImage(str(heatmap_path), margin, margin, width=width - 2 * margin, preserveAspectRatio=True, mask="auto")
            except Exception:
                c.setFont("Helvetica", 10)
                c.drawString(margin, height / 2, f"Heatmap could not be embedded. Path: {heatmap_path}")

        c.showPage()
        c.save()


longitudinal_service = LongitudinalTrackingService()

