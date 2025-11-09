"""
Longitudinal Tracking Service
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, List, Optional

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.longitudinal import (
    LongitudinalEpisode,
    LongitudinalEpisodeStatus,
    LongitudinalMetric,
    LongitudinalVisit,
    LongitudinalVisitType,
    MetricCategory,
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

    async def get_episode(self, db: AsyncSession, episode_id: int, patient_id: Optional[int] = None) -> Optional[LongitudinalEpisode]:
        stmt = (
            select(LongitudinalEpisode)
            .options(
                selectinload(LongitudinalEpisode.visits)
                .selectinload(LongitudinalVisit.metrics)
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


longitudinal_service = LongitudinalTrackingService()


