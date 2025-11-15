"""
Reporting Service
"""
from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from ..models.patient import Patient
from ..models.medical_record import MedicalRecord
from ..models.prediction import Prediction, DiseaseType, RiskLevel
from ..schemas.reports import (
    ClinicalReport,
    ClinicalPatientSummary,
    ClinicalPredictionSummary,
    ResearchReport,
    ResearchAggregation,
    ManagementReport,
    ManagementKpi,
    ManagementAlert,
)


class ReportingService:
    async def clinical_report(
        self,
        db: AsyncSession,
        patient_id: int,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> ClinicalReport:
        # Load patient with eager loading to avoid N+1 queries
        patient_result = await db.execute(
            select(Patient)
            .where(Patient.id == patient_id)
            .options(selectinload(Patient.medical_records))
        )
        patient = patient_result.scalar_one_or_none()
        if not patient:
            raise ValueError("patient_not_found")

        # Load predictions with eager loading
        predictions_query = select(Prediction).options(
            selectinload(Prediction.patient)
        ).where(Prediction.patient_id == patient_id)
        if start:
            predictions_query = predictions_query.where(Prediction.created_at >= start)
        if end:
            predictions_query = predictions_query.where(Prediction.created_at <= end)
        predictions_query = predictions_query.order_by(Prediction.created_at.desc()).limit(10)

        predictions_result = await db.execute(predictions_query)
        predictions = predictions_result.scalars().all()

        last_record_result = await db.execute(
            select(MedicalRecord.visit_date)
            .where(MedicalRecord.patient_id == patient_id)
            .order_by(MedicalRecord.visit_date.desc())
            .limit(1)
        )
        last_visit = last_record_result.scalar_one_or_none()

        follow_up_pending = any(p.follow_up_date and p.follow_up_date > datetime.utcnow() for p in predictions)

        patient_summary = ClinicalPatientSummary(
            id=patient.id,
            patient_identifier=patient.patient_id,
            full_name=f"{patient.first_name} {patient.last_name}",
            age=((datetime.utcnow().date() - patient.date_of_birth).days / 365.25),
            gender=patient.gender.value,
        )

        prediction_summaries: List[ClinicalPredictionSummary] = [
            ClinicalPredictionSummary(
                id=p.id,
                created_at=p.created_at,
                disease_type=p.disease_type,
                alzheimer_risk_score=p.alzheimer_risk_score,
                alzheimer_risk_level=p.alzheimer_risk_level,
                parkinson_risk_score=p.parkinson_risk_score,
                parkinson_risk_level=p.parkinson_risk_level,
                recommendations=p.recommendations,
            )
            for p in predictions
        ]

        return ClinicalReport(
            patient=patient_summary,
            predictions=prediction_summaries,
            last_medical_record_at=last_visit,
            pending_follow_up=follow_up_pending,
        )

    async def research_report(
        self,
        db: AsyncSession,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        risk_level: Optional[RiskLevel] = None,
        disease_type: Optional[DiseaseType] = None,
    ) -> ResearchReport:
        base_query = select(
            Prediction.disease_type,
            Prediction.alzheimer_risk_level,
            func.count(Prediction.id),
        )

        if start:
            base_query = base_query.where(Prediction.created_at >= start)
        if end:
            base_query = base_query.where(Prediction.created_at <= end)
        if disease_type:
            base_query = base_query.where(Prediction.disease_type == disease_type)
        if risk_level:
            base_query = base_query.where(Prediction.alzheimer_risk_level == risk_level)

        base_query = base_query.group_by(Prediction.disease_type, Prediction.alzheimer_risk_level)
        result = await db.execute(base_query)

        aggregations = [
            ResearchAggregation(
                disease_type=row[0],
                risk_level=row[1],
                count=row[2],
            )
            for row in result.all()
        ]

        total_query = select(func.count(Prediction.id))
        if start:
            total_query = total_query.where(Prediction.created_at >= start)
        if end:
            total_query = total_query.where(Prediction.created_at <= end)
        total_predictions = (await db.execute(total_query)).scalar_one()

        unique_patients_query = select(func.count(func.distinct(Prediction.patient_id)))
        if start:
            unique_patients_query = unique_patients_query.where(Prediction.created_at >= start)
        if end:
            unique_patients_query = unique_patients_query.where(Prediction.created_at <= end)
        unique_patients = (await db.execute(unique_patients_query)).scalar_one()

        return ResearchReport(
            total_predictions=total_predictions,
            unique_patients=unique_patients,
            aggregation=aggregations,
            timeframe_start=start,
            timeframe_end=end,
        )

    async def management_report(
        self,
        db: AsyncSession,
        model_version: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> ManagementReport:
        # Use eager loading to avoid N+1 queries
        base_query = select(Prediction).options(
            selectinload(Prediction.patient),
            selectinload(Prediction.created_by_user)
        )
        if model_version:
            base_query = base_query.where(Prediction.model_version == model_version)
        if start:
            base_query = base_query.where(Prediction.created_at >= start)
        if end:
            base_query = base_query.where(Prediction.created_at <= end)
        predictions_result = await db.execute(base_query)
        predictions = predictions_result.scalars().all()

        total_predictions = len(predictions)
        reviewed_predictions = len([p for p in predictions if str(p.is_reviewed).lower() == "true"])
        unique_patient_ids = {p.patient_id for p in predictions}

        version_distribution: Dict[str, int] = {}
        for p in predictions:
            version = p.model_version or "unknown"
            version_distribution[version] = version_distribution.get(version, 0) + 1

        alerts: List[ManagementAlert] = []
        high_risk_count = len(
            [p for p in predictions if p.alzheimer_risk_level == RiskLevel.HIGH or p.parkinson_risk_level == RiskLevel.HIGH]
        )
        if high_risk_count > 0:
            alerts.append(
                ManagementAlert(
                    title="High risk predictions detected",
                    severity="critical",
                    description=f"{high_risk_count} high risk predictions in selected timeframe.",
                    created_at=datetime.utcnow(),
                )
            )

        kpi = ManagementKpi(
            total_predictions=total_predictions,
            reviewed_predictions=reviewed_predictions,
            active_patients=len(unique_patient_ids),
            avg_response_time_ms=None,  # Placeholder until latency metrics exist
        )

        return ManagementReport(
            kpi=kpi,
            model_version_distribution=version_distribution,
            alerts=alerts,
        )


reporting_service = ReportingService()


