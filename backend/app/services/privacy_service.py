"""
Privacy Service - handle DSR requests (export/erasure stubs)
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Optional
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.privacy import DSRRequest, DSRStatus, DSRType
from ..models.patient import Patient
from ..models.prediction import Prediction
from ..models.longitudinal import LongitudinalReport


class PrivacyService:
    @staticmethod
    async def export_subject_data(db: AsyncSession, subject_identifier: str) -> str:
        """
        Create a simple JSON export of subject-related data (patients/predictions/reports by patient_id).
        Stores file under exports/privacy and returns path.
        """
        export_dir = Path("exports/privacy")
        export_dir.mkdir(parents=True, exist_ok=True)
        file_path = export_dir / f"export_{subject_identifier}.json"

        # Collect data (by patient_id when possible)
        export: Dict[str, Any] = {"patient_id": subject_identifier}

        pat = await db.execute(select(Patient).where(Patient.patient_id == subject_identifier))
        patient = pat.scalar_one_or_none()
        if patient:
            export["patient"] = {
                "id": patient.id,
                "patient_id": patient.patient_id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "date_of_birth": str(patient.date_of_birth) if patient.date_of_birth else None,
                "gender": str(patient.gender) if patient.gender else None,
            }
            preds = await db.execute(select(Prediction).where(Prediction.patient_id == patient.id))
            export["predictions"] = [
                {
                    "id": p.id,
                    "disease_type": str(p.disease_type),
                    "alzheimer_risk_score": p.alzheimer_risk_score,
                    "parkinson_risk_score": p.parkinson_risk_score,
                    "created_at": str(p.created_at),
                }
                for p in preds.scalars().all()
            ]
            reps = await db.execute(select(LongitudinalReport).where(LongitudinalReport.episode_id.in_([])))
            export["reports"] = []  # Placeholder; mapping episodes to patient can be added if needed

        file_path.write_text(json.dumps(export, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(file_path)

    @staticmethod
    async def update_dsr_status(db: AsyncSession, dsr: DSRRequest, status: DSRStatus, result_location: Optional[str] = None) -> DSRRequest:
        dsr.status = status
        if result_location:
            dsr.result_location = result_location
        await db.commit()
        await db.refresh(dsr)
        return dsr


