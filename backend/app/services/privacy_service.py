"""
Privacy Service - handle DSR requests (export/erasure)
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.privacy import DSRRequest, DSRStatus, DSRType
from ..models.patient import Patient
from ..models.prediction import Prediction
from ..models.longitudinal import LongitudinalEpisode, LongitudinalReport

logger = logging.getLogger(__name__)

# Fields included in subject export (documented surface area)
EXPORT_INCLUDES = [
    "patient demographics (as stored)",
    "predictions linked to patient.id",
    "longitudinal reports via patient → episodes → reports",
]
EXPORT_EXCLUDES = [
    "raw DICOM/MRI binary files (paths only if present on reports)",
    "other users' audit logs",
    "system credentials",
]


class PrivacyService:
    @staticmethod
    async def export_subject_data(db: AsyncSession, subject_identifier: str) -> str:
        """
        Create a JSON export of subject-related data.

        Includes:
        - Patient demographics
        - Predictions for the patient
        - Longitudinal reports via patient → episodes (when models allow)

        Excludes raw imaging binaries; report file paths are listed when available.
        Stores file under exports/privacy and returns path.
        """
        export_dir = Path("exports/privacy")
        export_dir.mkdir(parents=True, exist_ok=True)
        file_path = export_dir / f"export_{subject_identifier}.json"

        export: Dict[str, Any] = {
            "patient_id": subject_identifier,
            "export_includes": EXPORT_INCLUDES,
            "export_excludes": EXPORT_EXCLUDES,
        }

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
                "email": patient.email,
                "phone": patient.phone,
                "erased_at": str(patient.erased_at) if getattr(patient, "erased_at", None) else None,
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

            # Reports via patient → episodes
            episodes = await db.execute(
                select(LongitudinalEpisode).where(LongitudinalEpisode.patient_id == patient.id)
            )
            episode_list = episodes.scalars().all()
            episode_ids = [e.id for e in episode_list]
            export["episodes"] = [
                {
                    "id": e.id,
                    "title": e.title,
                    "status": str(e.status),
                    "start_date": str(e.start_date) if e.start_date else None,
                    "end_date": str(e.end_date) if e.end_date else None,
                }
                for e in episode_list
            ]
            reports: List[Dict[str, Any]] = []
            if episode_ids:
                reps = await db.execute(
                    select(LongitudinalReport).where(LongitudinalReport.episode_id.in_(episode_ids))
                )
                for r in reps.scalars().all():
                    reports.append(
                        {
                            "id": r.id,
                            "episode_id": r.episode_id,
                            "report_type": str(getattr(r, "report_type", None)),
                            "status": str(getattr(r, "status", None)),
                            "file_path": getattr(r, "file_path", None)
                            or getattr(r, "pdf_path", None)
                            or getattr(r, "output_path", None),
                            "created_at": str(r.created_at) if getattr(r, "created_at", None) else None,
                        }
                    )
            export["reports"] = reports
        else:
            export["patient"] = None
            export["predictions"] = []
            export["episodes"] = []
            export["reports"] = []
            export["note"] = "No patient record found for subject_identifier"

        file_path.write_text(json.dumps(export, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(file_path)

    @staticmethod
    async def erase_subject_data(db: AsyncSession, subject_identifier: str) -> Dict[str, Any]:
        """
        Erase / anonymize PHI for a subject (right to erasure).

        - Anonymize Patient PHI fields (names → REDACTED, contacts → null)
        - Mark patient erased_at
        - Remove identifiable longitudinal export files; clear report path fields
        - Keep predictions with de-identified patient link for audit
        """
        pat = await db.execute(select(Patient).where(Patient.patient_id == subject_identifier))
        patient = pat.scalar_one_or_none()
        if not patient:
            return {"erased": False, "reason": "patient_not_found", "subject_identifier": subject_identifier}

        now = datetime.now(timezone.utc)
        patient.first_name = "REDACTED"
        patient.last_name = "REDACTED"
        patient.email = None
        patient.phone = None
        patient.address = None
        patient.medical_history = None
        patient.family_history = None
        patient.current_medications = None
        patient.erased_at = now

        removed_files: List[str] = []
        episodes = await db.execute(
            select(LongitudinalEpisode).where(LongitudinalEpisode.patient_id == patient.id)
        )
        episode_list = episodes.scalars().all()
        episode_ids = [e.id for e in episode_list]

        if episode_ids:
            reps = await db.execute(
                select(LongitudinalReport).where(LongitudinalReport.episode_id.in_(episode_ids))
            )
            for r in reps.scalars().all():
                for attr in ("file_path", "pdf_path", "heatmap_path"):
                    path_val = getattr(r, attr, None)
                    if path_val:
                        try:
                            p = Path(path_val)
                            if p.exists() and p.is_file():
                                p.unlink()
                                removed_files.append(str(p))
                        except Exception as e:
                            logger.warning(f"Could not remove report file {path_val}: {e}")
                        # file_path is non-nullable — replace with sentinel
                        try:
                            if attr == "file_path":
                                setattr(r, attr, "REDACTED")
                            else:
                                setattr(r, attr, None)
                        except Exception:
                            pass
                if getattr(r, "summary", None) is not None:
                    r.summary = {"redacted": True}
                if getattr(r, "charts_payload", None) is not None:
                    r.charts_payload = None
                if getattr(r, "cohort_definition", None) is not None:
                    r.cohort_definition = None
                if getattr(r, "comparison_definition", None) is not None:
                    r.comparison_definition = None

            # Soft-archive episodes
            for e in episode_list:
                if hasattr(e, "title") and e.title:
                    e.title = "[REDACTED]"

        # Remove privacy export artifacts for this subject
        export_dir = Path("exports/privacy")
        if export_dir.exists():
            for f in export_dir.glob(f"export_{subject_identifier}*"):
                try:
                    f.unlink()
                    removed_files.append(str(f))
                except Exception as e:
                    logger.warning(f"Could not remove export {f}: {e}")

        await db.commit()
        await db.refresh(patient)

        return {
            "erased": True,
            "subject_identifier": subject_identifier,
            "patient_id": patient.id,
            "erased_at": str(patient.erased_at),
            "predictions_retained_deidentified": True,
            "removed_files": removed_files,
        }

    @staticmethod
    async def update_dsr_status(
        db: AsyncSession,
        dsr: DSRRequest,
        status: DSRStatus,
        result_location: Optional[str] = None,
    ) -> DSRRequest:
        dsr.status = status
        if result_location:
            dsr.result_location = result_location
        await db.commit()
        await db.refresh(dsr)
        return dsr
