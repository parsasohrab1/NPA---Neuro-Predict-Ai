"""
Clinical Explainability Service — Explainable AI for clinical trust

Provides physician-friendly explanations:
- Clinical feature importance (labels in FA/EN + interpretation)
- Similar cohort comparison (percentile, distribution)
- Neurological progression visualization data
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.patient import Patient
from ..models.medical_record import MedicalRecord
from ..models.prediction import Prediction

logger = logging.getLogger(__name__)


# Map raw feature names to clinical labels (FA + EN) and short interpretation
FEATURE_CLINICAL_MAP: Dict[str, Dict[str, str]] = {
    "age": {
        "label_fa": "سن",
        "label_en": "Age",
        "interpretation_fa": "عامل خطر شناخته‌شده برای بیماری‌های عصبی-تحولی",
        "interpretation_en": "Known risk factor for neurodegenerative disease",
    },
    "gender_encoded": {
        "label_fa": "جنسیت",
        "label_en": "Gender",
        "interpretation_fa": "تفاوت‌های جنسی در بروز و پیشرفت بیماری",
        "interpretation_en": "Sex differences in disease incidence and progression",
    },
    "education_years": {
        "label_fa": "سال‌های تحصیل",
        "label_en": "Education (years)",
        "interpretation_fa": "ذخیره شناختی و مقاومت در برابر افت شناختی",
        "interpretation_en": "Cognitive reserve and resilience to decline",
    },
    "mmse_score": {
        "label_fa": "نمره MMSE",
        "label_en": "MMSE Score",
        "interpretation_fa": "ارزیابی کلی شناختی (۰–۳۰)",
        "interpretation_en": "Global cognitive assessment (0–30)",
    },
    "moca_score": {
        "label_fa": "نمره MoCA",
        "label_en": "MoCA Score",
        "interpretation_fa": "حساسیت بیشتر برای MCI و دمانس زودرس",
        "interpretation_en": "More sensitive for MCI and early dementia",
    },
    "memory_score": {
        "label_fa": "نمره حافظه",
        "label_en": "Memory Score",
        "interpretation_fa": "عملکرد حافظه اپیزودیک و معنایی",
        "interpretation_en": "Episodic and semantic memory performance",
    },
    "attention_score": {
        "label_fa": "نمره توجه",
        "label_en": "Attention Score",
        "interpretation_fa": "تمرکز و توجه پایدار",
        "interpretation_en": "Focus and sustained attention",
    },
    "executive_function_score": {
        "label_fa": "عملکرد اجرایی",
        "label_en": "Executive Function Score",
        "interpretation_fa": "برنامه‌ریزی، تصمیم‌گیری و بازداری",
        "interpretation_en": "Planning, decision-making, and inhibition",
    },
    "amyloid_beta": {
        "label_fa": "آمیلوئید بتا",
        "label_en": "Amyloid-β",
        "interpretation_fa": "بیومارکر پاتولوژی آلزایمر",
        "interpretation_en": "Biomarker of Alzheimer pathology",
    },
    "tau_protein": {
        "label_fa": "پروتئین تاو",
        "label_en": "Tau Protein",
        "interpretation_fa": "آسیب نورونی و پیشرفت بیماری",
        "interpretation_en": "Neuronal injury and disease progression",
    },
    "dopamine_level": {
        "label_fa": "سطح دوپامین",
        "label_en": "Dopamine Level",
        "interpretation_fa": "شاخص عملکرد دوپامینرژیک؛ مرتبط با پارکینسون",
        "interpretation_en": "Dopaminergic function; relevant to Parkinson's",
    },
    "apoe_e4_status": {
        "label_fa": "وضعیت APOE ε4",
        "label_en": "APOE ε4 Status",
        "interpretation_fa": "قوی‌ترین عامل خطر ژنتیکی آلزایمر",
        "interpretation_en": "Strongest genetic risk factor for Alzheimer's",
    },
    "hippocampal_volume": {
        "label_fa": "حجم هیپوکامپ",
        "label_en": "Hippocampal Volume",
        "interpretation_fa": "آتروفی زودرس در آلزایمر",
        "interpretation_en": "Early atrophy in Alzheimer's disease",
    },
    "cortical_thickness": {
        "label_fa": "ضخامت قشری",
        "label_en": "Cortical Thickness",
        "interpretation_fa": "نازک‌شدن قشر و پیشرفت بیماری",
        "interpretation_en": "Cortical thinning with disease progression",
    },
    "ventricular_volume": {
        "label_fa": "حجم بطنی",
        "label_en": "Ventricular Volume",
        "interpretation_fa": "گشادی بطنی به‌عنوان شاخص آتروفی",
        "interpretation_en": "Ventricular enlargement as atrophy marker",
    },
    "white_matter_hyperintensities": {
        "label_fa": "هایپراینتنسیتی ماده سفید",
        "label_en": "White Matter Hyperintensities",
        "interpretation_fa": "آسیب عروقی و خطر شناختی",
        "interpretation_en": "Vascular burden and cognitive risk",
    },
    "brain_volume_total": {
        "label_fa": "حجم کل مغز",
        "label_en": "Total Brain Volume",
        "interpretation_fa": "شاخص کلی آتروفی مغزی",
        "interpretation_en": "Global brain atrophy indicator",
    },
}


def _get_clinical_feature_label(raw_name: str) -> Dict[str, str]:
    """Get clinical label and interpretation for a raw feature name."""
    if raw_name in FEATURE_CLINICAL_MAP:
        return FEATURE_CLINICAL_MAP[raw_name].copy()
    # Imaging features
    if raw_name.startswith("imaging_feature_"):
        return {
            "label_fa": "ویژگی تصویربرداری مغز",
            "label_en": "Brain Imaging Feature",
            "interpretation_fa": "الگوهای استخراج‌شده از تصاویر MRI",
            "interpretation_en": "Patterns extracted from MRI images",
        }
    return {
        "label_fa": raw_name.replace("_", " "),
        "label_en": raw_name.replace("_", " ").title(),
        "interpretation_fa": "—",
        "interpretation_en": "—",
    }


class ClinicalExplainabilityService:
    """Build clinical explanations for predictions (feature importance, cohort, progression)."""

    def get_clinical_feature_importance(
        self, feature_importance_raw: Dict[str, float], top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Convert raw feature importance to clinical labels and interpretations.
        Returns list of {clinical_label_fa, clinical_label_en, importance, interpretation_fa, interpretation_en}.
        """
        if not feature_importance_raw:
            return []
        sorted_items = sorted(
            feature_importance_raw.items(), key=lambda x: x[1], reverse=True
        )[:top_n]
        result = []
        for feat_name, importance in sorted_items:
            labels = _get_clinical_feature_label(feat_name)
            result.append({
                "feature_key": feat_name,
                "clinical_label_fa": labels["label_fa"],
                "clinical_label_en": labels["label_en"],
                "importance": round(float(importance), 4),
                "interpretation_fa": labels["interpretation_fa"],
                "interpretation_en": labels["interpretation_en"],
            })
        return result

    async def get_cohort_comparison(
        self,
        db: AsyncSession,
        patient_age: float,
        mmse_score: Optional[float],
        alzheimer_risk_score: float,
        parkinson_risk_score: float,
        patient_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Compare this patient's risk scores to a similar cohort (age ±10 years, similar MMSE if available).
        Returns percentile and distribution summary for trust and context.
        """
        # Define similar cohort: same age bucket (e.g. ±10 years)
        age_low = max(0, patient_age - 10)
        age_high = patient_age + 10

        from datetime import date
        today = date.today()

        # Fetch predictions with patient date_of_birth; filter by age in Python for portability
        stmt = (
            select(
                Prediction.alzheimer_risk_score,
                Prediction.parkinson_risk_score,
                Patient.date_of_birth,
            )
            .join(Patient, Patient.id == Prediction.patient_id)
            .where(
                Prediction.alzheimer_risk_score.isnot(None),
                Prediction.parkinson_risk_score.isnot(None),
            )
        )
        try:
            result = await db.execute(stmt)
            all_rows = result.all()
            rows = []
            for r in all_rows:
                dob = r[2]
                if dob is None:
                    rows.append((r[0], r[1]))
                    continue
                d = dob.date() if hasattr(dob, "date") else dob
                age = (today - d).days / 365.25
                if age_low <= age <= age_high:
                    rows.append((r[0], r[1]))
            if not rows:
                rows = [(r[0], r[1]) for r in all_rows]
        except Exception as e:
            logger.warning("Cohort comparison query failed, using fallback: %s", e)
            stmt_all = select(
                Prediction.alzheimer_risk_score,
                Prediction.parkinson_risk_score,
            ).where(
                Prediction.alzheimer_risk_score.isnot(None),
                Prediction.parkinson_risk_score.isnot(None),
            )
            result = await db.execute(stmt_all)
            rows = result.all()

        if not rows:
            return {
                "cohort_size": 0,
                "alzheimer": {
                    "patient_percentile": None,
                    "cohort_min": None,
                    "cohort_p25": None,
                    "cohort_median": None,
                    "cohort_p75": None,
                    "cohort_max": None,
                    "summary_fa": "داده کافی برای مقایسه با همگروه موجود نیست.",
                    "summary_en": "Insufficient data for cohort comparison.",
                },
                "parkinson": {
                    "patient_percentile": None,
                    "cohort_min": None,
                    "cohort_p25": None,
                    "cohort_median": None,
                    "cohort_p75": None,
                    "cohort_max": None,
                    "summary_fa": "داده کافی برای مقایسه با همگروه موجود نیست.",
                    "summary_en": "Insufficient data for cohort comparison.",
                },
            }

        import numpy as np
        alz_scores = [float(r[0]) for r in rows if r[0] is not None]
        park_scores = [float(r[1]) for r in rows if r[1] is not None]

        def percentile_and_summary(scores: List[float], patient_value: float) -> Dict[str, Any]:
            if not scores:
                return {
                    "patient_percentile": None,
                    "cohort_min": None,
                    "cohort_p25": None,
                    "cohort_median": None,
                    "cohort_p75": None,
                    "cohort_max": None,
                    "summary_fa": "—",
                    "summary_en": "—",
                }
            arr = np.array(scores)
            p25, p50, p75 = float(np.percentile(arr, 25)), float(np.percentile(arr, 50)), float(np.percentile(arr, 75))
            pct = float(np.mean(arr <= patient_value) * 100) if arr.size else None
            return {
                "patient_percentile": round(pct, 1) if pct is not None else None,
                "cohort_min": round(float(np.min(arr)), 4),
                "cohort_p25": round(p25, 4),
                "cohort_median": round(p50, 4),
                "cohort_p75": round(p75, 4),
                "cohort_max": round(float(np.max(arr)), 4),
                "summary_fa": f"بیمار در صدک {pct:.0f} همگروه مشابه (سن ±۱۰ سال) قرار دارد." if pct is not None else "—",
                "summary_en": f"Patient is at the {pct:.0f}th percentile of a similar cohort (age ±10 years)." if pct is not None else "—",
            }

        alz_summary = percentile_and_summary(alz_scores, alzheimer_risk_score)
        park_summary = percentile_and_summary(park_scores, parkinson_risk_score)
        alz_summary["cohort_size"] = len(alz_scores)
        park_summary["cohort_size"] = len(park_scores)

        return {
            "cohort_size": len(rows),
            "cohort_description_fa": "همگروه مشابه (سن ±۱۰ سال)",
            "cohort_description_en": "Similar cohort (age ±10 years)",
            "alzheimer": alz_summary,
            "parkinson": park_summary,
        }

    async def get_progression_visualization(
        self,
        db: AsyncSession,
        patient_id: int,
        alzheimer_risk_level: str,
        parkinson_risk_level: str,
        mmse_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Return data for neurological progression visualization.
        If longitudinal data exists, include trend; else return recommended follow-up and expected trajectory message.
        """
        from ..models.longitudinal import LongitudinalEpisode, LongitudinalVisit

        # Check for longitudinal episodes for this patient
        stmt = select(LongitudinalEpisode).where(LongitudinalEpisode.patient_id == patient_id)
        result = await db.execute(stmt)
        episodes = result.scalars().all()

        trend_data: Optional[Dict[str, Any]] = None
        if episodes:
            episode_id = episodes[0].id
            visits_stmt = (
                select(LongitudinalVisit)
                .where(LongitudinalVisit.episode_id == episode_id)
                .order_by(LongitudinalVisit.visit_date.asc())
            )
            visits_result = await db.execute(visits_stmt)
            visits = visits_result.scalars().all()
            if visits:
                trend_data = {
                    "visit_dates": [v.visit_date.isoformat() if hasattr(v.visit_date, "isoformat") else str(v.visit_date) for v in visits],
                    "progression_scores": [float(v.progression_score) if v.progression_score is not None else None for v in visits],
                    "has_longitudinal": True,
                }

        # Recommended follow-up based on risk
        high_risk = alzheimer_risk_level == "high" or parkinson_risk_level == "high"
        medium_risk = alzheimer_risk_level == "medium" or parkinson_risk_level == "medium"
        if high_risk:
            follow_up_months = 3
            trajectory_fa = "با توجه به سطح خطر بالا، پیگیری ۳ ماهه و ارزیابی تخصصی عصبی توصیه می‌شود."
            trajectory_en = "Given high risk level, 3-month follow-up and specialist neurological assessment recommended."
        elif medium_risk:
            follow_up_months = 6
            trajectory_fa = "با توجه به خطر متوسط، پیگیری ۶ ماهه و تکرار ارزیابی شناختی توصیه می‌شود."
            trajectory_en = "Given moderate risk, 6-month follow-up and repeat cognitive assessment recommended."
        else:
            follow_up_months = 12
            trajectory_fa = "سطح خطر پایین؛ پیگیری سالانه برای پایش پیشرفت کافی است."
            trajectory_en = "Low risk; annual follow-up for progression monitoring is sufficient."

        return {
            "has_longitudinal_data": trend_data is not None and trend_data.get("has_longitudinal"),
            "trend_data": trend_data,
            "recommended_follow_up_months": follow_up_months,
            "trajectory_summary_fa": trajectory_fa,
            "trajectory_summary_en": trajectory_en,
            "risk_context": {
                "alzheimer_risk_level": alzheimer_risk_level,
                "parkinson_risk_level": parkinson_risk_level,
            },
        }

    async def build_full_explanation(
        self,
        db: AsyncSession,
        patient_id: int,
        patient_data: Dict[str, Any],
        prediction_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build full clinical explanation: feature importance, cohort comparison, progression.
        """
        feature_importance_raw = prediction_result.get("feature_importance") or {}
        alzheimer_risk = prediction_result.get("alzheimer", {})
        parkinson_risk = prediction_result.get("parkinson", {})
        alzheimer_risk_score = alzheimer_risk.get("risk_score") or 0.0
        parkinson_risk_score = parkinson_risk.get("risk_score") or 0.0
        alzheimer_risk_level = (alzheimer_risk.get("risk_level") or "low")
        if hasattr(alzheimer_risk_level, "value"):
            alzheimer_risk_level = alzheimer_risk_level.value
        parkinson_risk_level = (parkinson_risk.get("risk_level") or "low")
        if hasattr(parkinson_risk_level, "value"):
            parkinson_risk_level = parkinson_risk_level.value

        patient_age = float(patient_data.get("age", 65))
        mmse = patient_data.get("mmse_score")

        clinical_importance = self.get_clinical_feature_importance(feature_importance_raw)
        cohort = await self.get_cohort_comparison(
            db,
            patient_age=patient_age,
            mmse_score=mmse,
            alzheimer_risk_score=alzheimer_risk_score,
            parkinson_risk_score=parkinson_risk_score,
            patient_id=patient_id,
        )
        progression = await self.get_progression_visualization(
            db,
            patient_id=patient_id,
            alzheimer_risk_level=alzheimer_risk_level,
            parkinson_risk_level=parkinson_risk_level,
            mmse_score=mmse,
        )

        return {
            "clinical_feature_importance": clinical_importance,
            "cohort_comparison": cohort,
            "progression_visualization": progression,
        }


clinical_explainability_service = ClinicalExplainabilityService()
