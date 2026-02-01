"""
Disease Tracking API - Real-time feature monitoring for Alzheimer's and Parkinson's
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..core.security import require_role, get_current_user
from ..models.patient import Patient, Gender
from ..models.medical_record import MedicalRecord
from ..models.prediction import Prediction, RiskLevel, DiseaseType
from ..models.user import User, UserRole
from ..services.ai_model_service import AIModelService

router = APIRouter(prefix="/disease-tracking", tags=["Disease Tracking"])

# Normal ranges for vital signs (for alerting) - (min, max) per range
VITAL_SIGN_RANGES = {
    "blood_pressure_systolic": {"normal": (90, 120), "warning": (80, 90), "critical": (0, 80)},  # mmHg - flag if <80 or >140
    "blood_pressure_diastolic": {"normal": (60, 80), "warning": (50, 60), "critical": (0, 50)},
    "temperature": {"normal": (36.1, 37.2), "warning": (35.5, 38.5), "critical": (0, 35)},  # °C
    "heart_rate": {"normal": (60, 100), "warning": (50, 120), "critical": (0, 50)},  # bpm
    "respiratory_rate": {"normal": (12, 20), "warning": (10, 24), "critical": (0, 10)},
    "oxygen_saturation": {"normal": (95, 100), "warning": (90, 95), "critical": (0, 90)},  # %
}

# Normal ranges for features (for alerting)
FEATURE_RANGES = {
    "mmse_score": {"normal": (24, 30), "warning": (18, 24), "critical": (0, 18)},
    "moca_score": {"normal": (26, 30), "warning": (18, 26), "critical": (0, 18)},
    "memory_score": {"normal": (70, 100), "warning": (50, 70), "critical": (0, 50)},
    "attention_score": {"normal": (70, 100), "warning": (50, 70), "critical": (0, 50)},
    "executive_function_score": {"normal": (70, 100), "warning": (50, 70), "critical": (0, 50)},
    "amyloid_beta": {"normal": (400, 600), "warning": (300, 400), "critical": (0, 300)},  # pg/mL
    "tau_protein": {"normal": (150, 250), "warning": (250, 400), "critical": (400, 1000)},  # pg/mL
    "dopamine_level": {"normal": (80, 120), "warning": (50, 80), "critical": (0, 50)},  # ng/mL
    "hippocampal_volume": {"normal": (3500, 5000), "warning": (2500, 3500), "critical": (0, 2500)},  # mm³
    "cortical_thickness": {"normal": (2.2, 3.0), "warning": (1.8, 2.2), "critical": (0, 1.8)},  # mm
    "ventricular_volume": {"normal": (15000, 30000), "warning": (30000, 45000), "critical": (45000, 100000)},  # mm³
}


@router.get("/patient/{patient_id}/features")
async def get_patient_features(
    patient_id: int,
    days: int = Query(default=365, ge=1, le=3650),
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(require_role("doctor")),  # Disabled for development
) -> Dict[str, Any]:
    """
    Get all features for a patient over time with trends and alerts
    """
    # Get patient
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Get medical records
    result = await db.execute(
        select(MedicalRecord)
        .where(
            and_(
                MedicalRecord.patient_id == patient_id,
                MedicalRecord.visit_date >= start_date,
            )
        )
        .order_by(MedicalRecord.visit_date.asc())
    )
    records = result.scalars().all()

    # Get predictions
    result = await db.execute(
        select(Prediction)
        .where(
            and_(
                Prediction.patient_id == patient_id,
                Prediction.created_at >= start_date,
            )
        )
        .order_by(Prediction.created_at.asc())
    )
    predictions = result.scalars().all()

    # Organize features by category
    cognitive_features = []
    biomarker_features = []
    mri_features = []
    genetic_features = []
    vital_signs_features = []

    for record in records:
        date = record.visit_date.isoformat()
        
        # Vital signs & clinical conditions
        if any([
            record.blood_pressure_systolic is not None,
            record.blood_pressure_diastolic is not None,
            record.temperature is not None,
            record.heart_rate is not None,
            record.oxygen_saturation is not None,
        ]):
            vital_signs_features.append({
                "date": date,
                "blood_pressure_systolic": record.blood_pressure_systolic,
                "blood_pressure_diastolic": record.blood_pressure_diastolic,
                "temperature": record.temperature,
                "heart_rate": record.heart_rate,
                "respiratory_rate": record.respiratory_rate,
                "oxygen_saturation": record.oxygen_saturation,
                "weight": record.weight,
                "height": record.height,
                "bmi": record.bmi,
                "blood_glucose": record.blood_glucose,
                "cholesterol_total": record.cholesterol_total,
            })
        
        # Cognitive scores
        if record.mmse_score is not None or record.moca_score is not None:
            cognitive_features.append({
                "date": date,
                "mmse_score": record.mmse_score,
                "moca_score": record.moca_score,
                "memory_score": record.memory_score,
                "attention_score": record.attention_score,
                "executive_function_score": record.executive_function_score,
            })
        
        # Biomarkers
        if record.amyloid_beta is not None or record.tau_protein is not None:
            biomarker_features.append({
                "date": date,
                "amyloid_beta": record.amyloid_beta,
                "tau_protein": record.tau_protein,
                "dopamine_level": record.dopamine_level,
            })
        
        # MRI features
        if record.hippocampal_volume is not None:
            mri_features.append({
                "date": date,
                "hippocampal_volume": record.hippocampal_volume,
                "cortical_thickness": record.cortical_thickness,
                "ventricular_volume": record.ventricular_volume,
                "white_matter_hyperintensities": record.white_matter_hyperintensities,
                "brain_volume_total": record.brain_volume_total,
            })
        
        # Genetic
        if record.apoe_e4_status is not None:
            genetic_features.append({
                "date": date,
                "apoe_e4_status": record.apoe_e4_status,
            })

    # Get latest values
    latest_record = records[-1] if records else None
    
    # If no records, return empty structure
    if not records:
        return {
            "patient_id": patient_id,
            "patient_name": f"{patient.first_name} {patient.last_name}",
            "age": (datetime.now().date() - patient.date_of_birth).days // 365,
            "gender": patient.gender.value,
            "cognitive_features": [],
            "biomarker_features": [],
            "mri_features": [],
            "genetic_features": [],
            "vital_signs_features": [],
            "latest_values": {},
            "trends": {},
            "alerts": [],
            "latest_prediction": None,
        }
    
    # Calculate trends (simple linear regression slope)
    def calculate_trend(values: List[float]) -> Optional[float]:
        if len(values) < 2:
            return None
        n = len(values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        if denominator == 0:
            return None
        return numerator / denominator

    # Generate alerts
    alerts = []
    if latest_record:
        for feature_name, ranges in FEATURE_RANGES.items():
            value = getattr(latest_record, feature_name, None)
            if value is not None:
                if value < ranges["critical"][0] or value > ranges["critical"][1]:
                    alerts.append({
                        "feature": feature_name,
                        "severity": "critical",
                        "value": value,
                        "normal_range": ranges["normal"],
                        "message": f"{feature_name} is in critical range: {value}",
                    })
                elif value < ranges["warning"][0] or value > ranges["warning"][1]:
                    alerts.append({
                        "feature": feature_name,
                        "severity": "warning",
                        "value": value,
                        "normal_range": ranges["normal"],
                        "message": f"{feature_name} is outside normal range: {value}",
                    })
        # Vital signs alerts
        for vs_name, ranges in VITAL_SIGN_RANGES.items():
            value = getattr(latest_record, vs_name, None)
            if value is not None:
                if value < ranges["critical"][0] or value > ranges["critical"][1]:
                    alerts.append({
                        "feature": vs_name,
                        "severity": "critical",
                        "value": value,
                        "normal_range": ranges["normal"],
                        "message": f"{vs_name} is in critical range: {value}",
                    })
                elif value < ranges["warning"][0] or value > ranges["warning"][1]:
                    alerts.append({
                        "feature": vs_name,
                        "severity": "warning",
                        "value": value,
                        "normal_range": ranges["normal"],
                        "message": f"{vs_name} is outside normal range: {value}",
                    })

    # Calculate feature trends
    feature_trends = {}
    if cognitive_features:
        mmse_values = [r["mmse_score"] for r in cognitive_features if r["mmse_score"] is not None]
        if mmse_values:
            feature_trends["mmse_trend"] = calculate_trend(mmse_values)
    
    if biomarker_features:
        amyloid_values = [r["amyloid_beta"] for r in biomarker_features if r["amyloid_beta"] is not None]
        if amyloid_values:
            feature_trends["amyloid_trend"] = calculate_trend(amyloid_values)
    
    if mri_features:
        hippocampal_values = [r["hippocampal_volume"] for r in mri_features if r["hippocampal_volume"] is not None]
        if hippocampal_values:
            feature_trends["hippocampal_trend"] = calculate_trend(hippocampal_values)

    # Get latest prediction
    latest_prediction = predictions[-1] if predictions else None

    return {
        "patient_id": patient_id,
        "patient_name": f"{patient.first_name} {patient.last_name}",
        "age": (datetime.now().date() - patient.date_of_birth).days // 365,
        "gender": patient.gender.value,
        "cognitive_features": cognitive_features,
        "biomarker_features": biomarker_features,
        "mri_features": mri_features,
        "genetic_features": genetic_features,
        "vital_signs_features": vital_signs_features,
        "latest_values": {
            "mmse_score": latest_record.mmse_score if latest_record else None,
            "moca_score": latest_record.moca_score if latest_record else None,
            "amyloid_beta": latest_record.amyloid_beta if latest_record else None,
            "tau_protein": latest_record.tau_protein if latest_record else None,
            "dopamine_level": latest_record.dopamine_level if latest_record else None,
            "hippocampal_volume": latest_record.hippocampal_volume if latest_record else None,
            "cortical_thickness": latest_record.cortical_thickness if latest_record else None,
            "ventricular_volume": latest_record.ventricular_volume if latest_record else None,
            "brain_volume_total": latest_record.brain_volume_total if latest_record else None,
            "memory_score": latest_record.memory_score if latest_record else None,
            "attention_score": latest_record.attention_score if latest_record else None,
            "executive_function_score": latest_record.executive_function_score if latest_record else None,
            "apoe_e4_status": latest_record.apoe_e4_status if latest_record else None,
            "blood_pressure_systolic": latest_record.blood_pressure_systolic if latest_record else None,
            "blood_pressure_diastolic": latest_record.blood_pressure_diastolic if latest_record else None,
            "temperature": latest_record.temperature if latest_record else None,
            "heart_rate": latest_record.heart_rate if latest_record else None,
            "respiratory_rate": latest_record.respiratory_rate if latest_record else None,
            "oxygen_saturation": latest_record.oxygen_saturation if latest_record else None,
            "weight": latest_record.weight if latest_record else None,
            "height": latest_record.height if latest_record else None,
            "bmi": latest_record.bmi if latest_record else None,
            "blood_glucose": latest_record.blood_glucose if latest_record else None,
            "cholesterol_total": latest_record.cholesterol_total if latest_record else None,
        },
        "trends": feature_trends,
        "alerts": alerts,
        "latest_prediction": {
            "alzheimer_risk": latest_prediction.alzheimer_risk_score if latest_prediction else None,
            "parkinson_risk": latest_prediction.parkinson_risk_score if latest_prediction else None,
            "alzheimer_level": latest_prediction.alzheimer_risk_level.value if latest_prediction and latest_prediction.alzheimer_risk_level else None,
            "parkinson_level": latest_prediction.parkinson_risk_level.value if latest_prediction and latest_prediction.parkinson_risk_level else None,
            "date": latest_prediction.created_at.isoformat() if latest_prediction else None,
        } if latest_prediction else None,
    }


@router.get("/patient/{patient_id}/future-risk")
async def predict_future_risk(
    patient_id: int,
    months_ahead: int = Query(default=12, ge=1, le=60),
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(require_role("doctor")),  # Disabled for development
) -> Dict[str, Any]:
    """
    Predict future disease risk based on current trends
    """
    # Get patient and latest data
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get latest medical record
    result = await db.execute(
        select(MedicalRecord)
        .where(MedicalRecord.patient_id == patient_id)
        .order_by(MedicalRecord.visit_date.desc())
        .limit(1)
    )
    latest_record = result.scalar_one_or_none()

    if not latest_record:
        raise HTTPException(status_code=404, detail="No medical records found for patient")

    # Get trend data
    result = await db.execute(
        select(MedicalRecord)
        .where(MedicalRecord.patient_id == patient_id)
        .order_by(MedicalRecord.visit_date.desc())
        .limit(6)  # Last 6 visits for trend
    )
    recent_records = list(reversed(result.scalars().all()))

    # Simple trend-based prediction
    # This is a simplified model - in production, use proper ML models
    
    # Calculate trends
    mmse_trend = 0
    amyloid_trend = 0
    hippocampal_trend = 0
    
    if len(recent_records) >= 2:
        mmse_values = [r.mmse_score for r in recent_records if r.mmse_score is not None]
        if len(mmse_values) >= 2:
            mmse_trend = (mmse_values[-1] - mmse_values[0]) / len(mmse_values)
        
        amyloid_values = [r.amyloid_beta for r in recent_records if r.amyloid_beta is not None]
        if len(amyloid_values) >= 2:
            amyloid_trend = (amyloid_values[-1] - amyloid_values[0]) / len(amyloid_values)
        
        hippocampal_values = [r.hippocampal_volume for r in recent_records if r.hippocampal_volume is not None]
        if len(hippocampal_values) >= 2:
            hippocampal_trend = (hippocampal_values[-1] - hippocampal_values[0]) / len(hippocampal_values)

    # Project future values
    months_factor = months_ahead / 12.0
    
    projected_mmse = latest_record.mmse_score + (mmse_trend * months_factor * 12) if latest_record.mmse_score else None
    projected_amyloid = latest_record.amyloid_beta + (amyloid_trend * months_factor * 12) if latest_record.amyloid_beta else None
    projected_hippocampal = latest_record.hippocampal_volume + (hippocampal_trend * months_factor * 12) if latest_record.hippocampal_volume else None

    # Estimate risk based on projections (simplified heuristic)
    alzheimer_risk = 0.0
    parkinson_risk = 0.0
    
    if projected_mmse is not None and projected_mmse < 24:
        alzheimer_risk += 0.3
    if projected_amyloid is not None and projected_amyloid < 400:
        alzheimer_risk += 0.4
    if projected_hippocampal is not None and projected_hippocampal < 3000:
        alzheimer_risk += 0.3
    
    if latest_record.dopamine_level is not None and latest_record.dopamine_level < 70:
        parkinson_risk += 0.5
    if latest_record.apoe_e4_status:
        alzheimer_risk += 0.2

    # Normalize to 0-1
    alzheimer_risk = min(1.0, alzheimer_risk)
    parkinson_risk = min(1.0, parkinson_risk)

    return {
        "patient_id": patient_id,
        "months_ahead": months_ahead,
        "projected_values": {
            "mmse_score": projected_mmse,
            "amyloid_beta": projected_amyloid,
            "hippocampal_volume": projected_hippocampal,
        },
        "predicted_risks": {
            "alzheimer": {
                "risk_score": alzheimer_risk,
                "risk_level": "high" if alzheimer_risk > 0.66 else "medium" if alzheimer_risk > 0.33 else "low",
            },
            "parkinson": {
                "risk_score": parkinson_risk,
                "risk_level": "high" if parkinson_risk > 0.66 else "medium" if parkinson_risk > 0.33 else "low",
            },
        },
        "trends": {
            "mmse_trend": mmse_trend,
            "amyloid_trend": amyloid_trend,
            "hippocampal_trend": hippocampal_trend,
        },
    }


@router.get("/patient/{patient_id}/recommendations")
async def get_recommendations(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(require_role("doctor")),  # Disabled for development
) -> Dict[str, Any]:
    """
    Get prevention and control recommendations based on patient's current status
    """
    # Get patient and latest data
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    result = await db.execute(
        select(MedicalRecord)
        .where(MedicalRecord.patient_id == patient_id)
        .order_by(MedicalRecord.visit_date.desc())
        .limit(1)
    )
    latest_record = result.scalar_one_or_none()

    result = await db.execute(
        select(Prediction)
        .where(Prediction.patient_id == patient_id)
        .order_by(Prediction.created_at.desc())
        .limit(1)
    )
    latest_prediction = result.scalar_one_or_none()

    recommendations = {
        "alzheimer": [],
        "parkinson": [],
        "general": [],
    }

    if latest_record:
        # Alzheimer's recommendations
        if latest_record.mmse_score is not None and latest_record.mmse_score < 24:
            recommendations["alzheimer"].append({
                "priority": "high",
                "category": "Cognitive Training",
                "title": "Cognitive Rehabilitation Program",
                "description": "Engage in structured cognitive training exercises to improve memory and executive function",
                "actions": [
                    "Participate in memory training programs",
                    "Practice problem-solving activities",
                    "Engage in social activities",
                ],
            })
        
        if latest_record.amyloid_beta is not None and latest_record.amyloid_beta < 400:
            recommendations["alzheimer"].append({
                "priority": "high",
                "category": "Lifestyle",
                "title": "Amyloid-Beta Management",
                "description": "Low amyloid-beta levels indicate increased risk. Focus on lifestyle interventions",
                "actions": [
                    "Maintain Mediterranean diet",
                    "Regular physical exercise (150 min/week)",
                    "Adequate sleep (7-9 hours)",
                    "Stress management",
                ],
            })
        
        if latest_record.hippocampal_volume is not None and latest_record.hippocampal_volume < 3000:
            recommendations["alzheimer"].append({
                "priority": "medium",
                "category": "Medical",
                "title": "Hippocampal Volume Monitoring",
                "description": "Reduced hippocampal volume detected. Regular monitoring recommended",
                "actions": [
                    "Schedule follow-up MRI in 6 months",
                    "Consider neuroprotective medications",
                    "Monitor cognitive function closely",
                ],
            })

        # Parkinson's recommendations
        if latest_record.dopamine_level is not None and latest_record.dopamine_level < 70:
            recommendations["parkinson"].append({
                "priority": "high",
                "category": "Medical",
                "title": "Dopamine Level Management",
                "description": "Low dopamine levels detected. Consider medical intervention",
                "actions": [
                    "Consult with neurologist",
                    "Consider dopamine replacement therapy",
                    "Monitor motor symptoms",
                ],
            })

        # General recommendations
        age = (datetime.now().date() - patient.date_of_birth).days // 365
        if age > 65:
            recommendations["general"].append({
                "priority": "medium",
                "category": "Lifestyle",
                "title": "Age-Related Risk Management",
                "description": "Age is a significant risk factor. Focus on preventive measures",
                "actions": [
                    "Regular health checkups",
                    "Maintain active lifestyle",
                    "Healthy diet rich in antioxidants",
                    "Social engagement",
                ],
            })

        if latest_record.apoe_e4_status:
            recommendations["alzheimer"].append({
                "priority": "medium",
                "category": "Genetic",
                "title": "APOE ε4 Carrier Management",
                "description": "APOE ε4 allele detected. Increased Alzheimer's risk",
                "actions": [
                    "Enhanced monitoring schedule",
                    "Lifestyle modifications",
                    "Consider genetic counseling",
                ],
            })

    if latest_prediction:
        if latest_prediction.alzheimer_risk_score and latest_prediction.alzheimer_risk_score > 0.66:
            recommendations["alzheimer"].append({
                "priority": "critical",
                "category": "Medical",
                "title": "High Alzheimer's Risk Detected",
                "description": "Immediate medical attention and intervention recommended",
                "actions": [
                    "Schedule appointment with neurologist",
                    "Consider medication evaluation",
                    "Family counseling",
                    "Advanced care planning",
                ],
            })
        
        if latest_prediction.parkinson_risk_score and latest_prediction.parkinson_risk_score > 0.66:
            recommendations["parkinson"].append({
                "priority": "critical",
                "category": "Medical",
                "title": "High Parkinson's Risk Detected",
                "description": "Immediate medical attention and intervention recommended",
                "actions": [
                    "Schedule appointment with movement disorder specialist",
                    "Consider medication evaluation",
                    "Physical therapy assessment",
                    "Monitor motor symptoms",
                ],
            })

    return {
        "patient_id": patient_id,
        "recommendations": recommendations,
        "generated_at": datetime.now().isoformat(),
    }


@router.get("/health")
async def health_check():
    """Health check endpoint to verify API is running"""
    return {"status": "ok", "message": "Disease tracking API is running"}


# Feature ranges for Alzheimer vs Parkinson (health vs patient)
CLASSIFICATION_FEATURE_RANGES = {
    "cognitive": {
        "mmse_score": {
            "normal": {"min": 28, "max": 30, "label": "Healthy"},
            "alzheimer": {"min": 12, "max": 28, "label": "Alzheimer"},
            "parkinson": {"min": 22, "max": 30, "label": "Mild Parkinson"},
        },
        "moca_score": {
            "normal": {"min": 26, "max": 30, "label": "Healthy"},
            "alzheimer": {"min": 10, "max": 26, "label": "Alzheimer"},
            "parkinson": {"min": 18, "max": 30, "label": "Mild Parkinson"},
        },
    },
    "biomarkers": {
        "amyloid_beta": {
            "normal": {"min": 400, "max": 1000, "label": "Healthy"},
            "alzheimer": {"min": 100, "max": 500, "label": "Low (diagnostic Alzheimer)"},
            "parkinson": {"min": 350, "max": 950, "label": "Normal"},
        },
        "tau_protein": {
            "normal": {"min": 40, "max": 360, "label": "Healthy"},
            "alzheimer": {"min": 300, "max": 900, "label": "High (diagnostic Alzheimer)"},
            "parkinson": {"min": 50, "max": 450, "label": "Normal"},
        },
        "dopamine_level": {
            "normal": {"min": 80, "max": 160, "label": "Healthy"},
            "alzheimer": {"min": 60, "max": 160, "label": "Normal to slightly low"},
            "parkinson": {"min": 0, "max": 125, "label": "Low (diagnostic Parkinson)"},
        },
    },
    "mri": {
        "hippocampal_volume": {
            "normal": {"min": 3400, "max": 4600, "label": "Healthy"},
            "alzheimer": {"min": 1500, "max": 3500, "label": "Atrophy"},
            "parkinson": {"min": 2700, "max": 4300, "label": "Mild decrease"},
        },
    },
}


@router.get("/feature-ranges")
async def get_feature_ranges() -> Dict[str, Any]:
    """
    Return healthy vs at-risk vs disease ranges for biomarkers (Alzheimer/Parkinson related).
    Used by admin dashboard to display feature ranges.
    """
    return {
        "risk_score_ranges": {
            "alzheimer": {
                "low": {"min": 0, "max": 0.33, "label": "Healthy", "label_en": "Healthy"},
                "medium": {"min": 0.33, "max": 0.66, "label": "At Risk", "label_en": "At Risk"},
                "high": {"min": 0.66, "max": 1.0, "label": "High Risk / Disease", "label_en": "High Risk / Disease"},
            },
            "parkinson": {
                "low": {"min": 0, "max": 0.33, "label": "Healthy", "label_en": "Healthy"},
                "medium": {"min": 0.33, "max": 0.66, "label": "At Risk", "label_en": "At Risk"},
                "high": {"min": 0.66, "max": 1.0, "label": "High Risk / Disease", "label_en": "High Risk / Disease"},
            },
        },
        "biomarker_ranges": FEATURE_RANGES,
        "classification_feature_ranges": CLASSIFICATION_FEATURE_RANGES,
    }


@router.get("/patient-classification")
async def get_patient_classification(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Patient classification in database by diagnosis (normal/Alzheimer/Parkinson).
    Returns patient classification with diagnosis, feature ranges, and per-patient breakdown.
    """
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(Patient).options(selectinload(Patient.medical_records))
    )
    all_patients = result.scalars().unique().all()

    classification_summary = {
        "normal": 0,
        "alzheimer": 0,
        "parkinson": 0,
        "unknown": 0,
    }
    patients_list = []

    for patient in all_patients:
        pred_result = await db.execute(
            select(Prediction)
            .where(Prediction.patient_id == patient.id)
            .order_by(Prediction.created_at.desc())
            .limit(1)
        )
        latest_pred = pred_result.scalar_one_or_none()

        mr_result = await db.execute(
            select(MedicalRecord)
            .where(MedicalRecord.patient_id == patient.id)
            .order_by(MedicalRecord.visit_date.desc())
            .limit(1)
        )
        latest_record = mr_result.scalar_one_or_none()

        diagnosis = "unknown"
        if latest_pred and latest_pred.disease_type:
            dt_val = latest_pred.disease_type.value if hasattr(latest_pred.disease_type, "value") else str(latest_pred.disease_type)
            dt = (dt_val or "").lower()
            if dt == "alzheimer":
                diagnosis = "alzheimer"
                classification_summary["alzheimer"] += 1
            elif dt == "parkinson":
                diagnosis = "parkinson"
                classification_summary["parkinson"] += 1
            else:
                diagnosis = "normal"
                classification_summary["normal"] += 1
        else:
            classification_summary["unknown"] += 1

        age = (datetime.now().date() - patient.date_of_birth).days // 365 if patient.date_of_birth else None
        features = {}
        if latest_record:
            features = {
                "mmse_score": latest_record.mmse_score,
                "moca_score": latest_record.moca_score,
                "amyloid_beta": latest_record.amyloid_beta,
                "tau_protein": latest_record.tau_protein,
                "dopamine_level": latest_record.dopamine_level,
                "hippocampal_volume": latest_record.hippocampal_volume,
            }

        patients_list.append({
            "patient_id": patient.id,
            "patient_external_id": patient.patient_id,
            "name": f"{patient.first_name} {patient.last_name}",
            "age": age,
            "diagnosis": diagnosis,
            "diagnosis_fa": {"normal": "Normal", "alzheimer": "Alzheimer", "parkinson": "Parkinson", "unknown": "Unknown"}.get(diagnosis, "Unknown"),
            "alzheimer_risk": round(latest_pred.alzheimer_risk_score, 3) if latest_pred else None,
            "parkinson_risk": round(latest_pred.parkinson_risk_score, 3) if latest_pred else None,
            "features": features,
        })

    return {
        "feature_ranges": CLASSIFICATION_FEATURE_RANGES,
        "classification_summary": classification_summary,
        "classification_summary_fa": {
            "normal": f"Normal: {classification_summary['normal']}",
            "alzheimer": f"Alzheimer: {classification_summary['alzheimer']}",
            "parkinson": f"Parkinson: {classification_summary['parkinson']}",
            "unknown": f"Unknown: {classification_summary['unknown']}",
        },
        "total_patients": len(all_patients),
        "patients": patients_list,
    }


@router.get("/all-patients/summary")
async def get_all_patients_summary(
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(require_role("doctor")),  # Disabled for development
) -> Dict[str, Any]:
    """
    Get summary of all patients with their risk levels and alerts
    Returns all patients, even if they don't have predictions yet
    """
    # Get all patients
    result = await db.execute(select(Patient))
    all_patients = result.scalars().all()
    
    # Get latest prediction for each patient
    summary = {
        "total_patients": len(all_patients),
        "high_risk_alzheimer": 0,
        "high_risk_parkinson": 0,
        "medium_risk_alzheimer": 0,
        "medium_risk_parkinson": 0,
        "low_risk": 0,
        "patients": [],
    }

    for patient in all_patients:
        # Get latest prediction for this patient
        result = await db.execute(
            select(Prediction)
            .where(Prediction.patient_id == patient.id)
            .order_by(Prediction.created_at.desc())
            .limit(1)
        )
        latest_prediction = result.scalar_one_or_none()
        
        alz_risk = latest_prediction.alzheimer_risk_score if latest_prediction else 0.0
        park_risk = latest_prediction.parkinson_risk_score if latest_prediction else 0.0
        
        # Count risk levels
        if alz_risk > 0.66 or park_risk > 0.66:
            if alz_risk > 0.66:
                summary["high_risk_alzheimer"] += 1
            if park_risk > 0.66:
                summary["high_risk_parkinson"] += 1
        elif alz_risk > 0.33 or park_risk > 0.33:
            if alz_risk > 0.33:
                summary["medium_risk_alzheimer"] += 1
            if park_risk > 0.33:
                summary["medium_risk_parkinson"] += 1
        else:
            summary["low_risk"] += 1
        
        alz_level = "high" if alz_risk >= 0.66 else "medium" if alz_risk >= 0.33 else "low"
        park_level = "high" if park_risk >= 0.66 else "medium" if park_risk >= 0.33 else "low"
        summary["patients"].append({
            "patient_id": patient.id,
            "name": f"{patient.first_name} {patient.last_name}",
            "alzheimer_risk": round(alz_risk, 3),
            "parkinson_risk": round(park_risk, 3),
            "alzheimer_level": alz_level,
            "parkinson_level": park_level,
            "last_prediction_date": latest_prediction.created_at.isoformat() if latest_prediction else None,
        })

    return summary


@router.post("/load-all-datasets")
async def load_all_datasets(
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(require_role("admin")),  # Disabled for development
) -> Dict[str, Any]:
    """
    Load medical records and predictions for ALL 500 existing patients in the database.
    This reads existing patients and creates medical records + predictions for those who don't have them.
    """
    import random
    from datetime import timedelta
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info("=== Starting load_all_datasets - Processing DATABASE patients ===")
    
    total_patients_processed = 0
    total_records_created = 0
    total_predictions_created = 0
    skipped_patients = 0
    errors = []
    
    # Fetch ALL patients from database
    result = await db.execute(select(Patient))
    all_patients = result.scalars().all()
    
    logger.info(f"Found {len(all_patients)} patients in database")
    
    if not all_patients:
        return {
            "message": "No patients found in database. Please import patients first.",
            "total_patients": 0,
            "total_records": 0,
            "total_predictions": 0,
            "skipped": 0,
            "errors": ["No patients in database"],
            "error_count": 1,
        }
    
    # Process each patient
    for patient in all_patients:
        try:
            # Check if patient already has medical records
            result_mr = await db.execute(
                select(MedicalRecord).where(MedicalRecord.patient_id == patient.id)
            )
            if result_mr.scalar_one_or_none():
                skipped_patients += 1
                continue
            
            # Generate medical data
            age = (datetime.now().date() - patient.date_of_birth).days // 365
            age_factor = max(0, (age - 50) / 30)
            age_adjustment = age_factor * random.uniform(-3, -1)
            
            mmse_score = max(18, min(30, 28.0 + age_adjustment + random.uniform(-2, 2)))
            moca_score = max(16, min(30, 26.0 + age_adjustment + random.uniform(-2, 2)))
            memory_score = max(50, min(100, 75.0 + age_adjustment * 5 + random.uniform(-10, 10)))
            attention_score = max(60, min(100, 80.0 + age_adjustment * 3 + random.uniform(-8, 8)))
            executive_score = max(55, min(100, 75.0 + age_adjustment * 4 + random.uniform(-10, 10)))
            
            amyloid_beta = random.uniform(450, 650)
            tau_protein = random.uniform(180, 280)
            dopamine_level = random.uniform(85, 115)
            
            # Adjust for disease patterns
            patient_id_upper = patient.patient_id.upper()
            if 'AD' in patient_id_upper or 'ALZHEIMER' in patient_id_upper:
                amyloid_beta = random.uniform(250, 400)
                tau_protein = random.uniform(350, 550)
                mmse_score = max(15, min(25, mmse_score - random.uniform(3, 8)))
                moca_score = max(10, min(20, moca_score - random.uniform(3, 8)))
            elif 'PD' in patient_id_upper or 'PARKINSON' in patient_id_upper:
                dopamine_level = random.uniform(40, 75)
                mmse_score = max(20, min(28, mmse_score - random.uniform(1, 4)))
                moca_score = max(15, min(25, moca_score - random.uniform(1, 4)))
            
            apoe_e4_status = random.random() < 0.25
            
            hippocampal_volume = random.uniform(3500, 4800)
            cortical_thickness = random.uniform(2.3, 2.9)
            ventricular_volume = random.uniform(18000, 28000)
            white_matter_hyperintensities = random.uniform(0.5, 2.5)
            brain_volume_total = random.uniform(1050000, 1150000)
            
            if age > 70:
                hippocampal_volume *= random.uniform(0.85, 0.95)
                cortical_thickness *= random.uniform(0.90, 0.98)
                ventricular_volume *= random.uniform(1.05, 1.15)
            
            # Create medical record
            visit_date = datetime.now() - timedelta(days=random.randint(0, 90))
            medical_record = MedicalRecord(
                patient_id=patient.id,
                visit_date=visit_date,
                visit_type="Initial",
                mmse_score=round(mmse_score, 1),
                moca_score=round(moca_score, 1),
                memory_score=round(memory_score, 1),
                attention_score=round(attention_score, 1),
                executive_function_score=round(executive_score, 1),
                amyloid_beta=round(amyloid_beta, 1),
                tau_protein=round(tau_protein, 1),
                dopamine_level=round(dopamine_level, 1),
                apoe_e4_status=apoe_e4_status,
                hippocampal_volume=round(hippocampal_volume, 0),
                cortical_thickness=round(cortical_thickness, 2),
                ventricular_volume=round(ventricular_volume, 0),
                white_matter_hyperintensities=round(white_matter_hyperintensities, 2),
                brain_volume_total=round(brain_volume_total, 0),
                symptoms="Routine check-up",
                clinical_notes=f"Disease tracking data. Age: {age}, Gender: {patient.gender.value}",
            )
            
            db.add(medical_record)
            await db.flush()
            total_records_created += 1
            
            # Calculate risk scores
            alzheimer_risk = 0.0
            parkinson_risk = 0.0
            
            if mmse_score < 24: alzheimer_risk += 0.3
            if moca_score < 22: alzheimer_risk += 0.25
            if amyloid_beta < 400: alzheimer_risk += 0.35
            if tau_protein > 350: alzheimer_risk += 0.3
            if hippocampal_volume < 3000: alzheimer_risk += 0.25
            if apoe_e4_status: alzheimer_risk += 0.2
            if age > 75: alzheimer_risk += 0.15
            
            if dopamine_level < 70: parkinson_risk += 0.5
            if dopamine_level < 50: parkinson_risk += 0.3
            if age > 70: parkinson_risk += 0.2
            if attention_score < 65: parkinson_risk += 0.15
            
            alzheimer_risk = min(1.0, alzheimer_risk)
            parkinson_risk = min(1.0, parkinson_risk)
            
            alzheimer_level = (
                RiskLevel.HIGH if alzheimer_risk >= 0.66
                else RiskLevel.MEDIUM if alzheimer_risk >= 0.33
                else RiskLevel.LOW
            )
            parkinson_level = (
                RiskLevel.HIGH if parkinson_risk >= 0.66
                else RiskLevel.MEDIUM if parkinson_risk >= 0.33
                else RiskLevel.LOW
            )
            
            # Determine disease type
            if 'AD' in patient_id_upper or 'ALZHEIMER' in patient_id_upper:
                disease_type = DiseaseType.ALZHEIMER
            elif 'PD' in patient_id_upper or 'PARKINSON' in patient_id_upper:
                disease_type = DiseaseType.PARKINSON
            else:
                disease_type = DiseaseType.BOTH
            
            # Create prediction
            prediction = Prediction(
                patient_id=patient.id,
                disease_type=disease_type,
                alzheimer_risk_score=round(alzheimer_risk, 2),
                parkinson_risk_score=round(parkinson_risk, 2),
                alzheimer_risk_level=alzheimer_level,
                parkinson_risk_level=parkinson_level,
                created_at=datetime.now(),
            )
            
            db.add(prediction)
            total_predictions_created += 1
            total_patients_processed += 1
            
        except Exception as e:
            logger.error(f"Error processing patient {patient.patient_id}: {str(e)}", exc_info=True)
            errors.append(f"Patient {patient.patient_id}: {str(e)[:100]}")
            continue
    
    # Commit all changes
    try:
        await db.commit()
        logger.info(f"SUCCESS: {total_patients_processed} patients, {total_records_created} records, {total_predictions_created} predictions")
    except Exception as e:
        logger.error(f"Failed to commit: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save data: {str(e)}"
        )
    
    return {
        "message": f"Loaded {total_patients_processed} patients successfully!" if not errors else "Loaded with some errors",
        "total_patients": total_patients_processed,
        "total_records": total_records_created,
        "total_predictions": total_predictions_created,
        "skipped": skipped_patients,
        "errors": errors[:10] if errors else [],
        "error_count": len(errors),
    }


@router.post("/load-sample-datasets")
async def load_sample_datasets(
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(require_role("admin")),  # Disabled for development
) -> Dict[str, Any]:
    """
    Load 200 sample patients from CSV files with specific distribution:
    - 120 Normal patients (60 synthetic + 60 real)
    - 40 Alzheimer patients (20 synthetic + 20 real)
    - 40 Parkinson patients (20 synthetic + 20 real)
    Total: 100 synthetic + 100 real = 200 patients
    """
    import random
    from datetime import timedelta, date
    import logging
    import pandas as pd
    from pathlib import Path
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=== Starting load_sample_datasets - Loading 200 specific patients ===")
        
        total_patients_processed = 0
        total_records_created = 0
        total_predictions_created = 0
        skipped_patients = 0
        errors = []
    
        # Paths to CSV files - try multiple locations (generated data paths)
        project_root = Path(__file__).parent.parent.parent.parent
        synthetic_csv = project_root / 'data' / 'data' / 'csv' / 'sample_dataset_complete.csv'
        if not synthetic_csv.exists():
            synthetic_csv = project_root / 'data' / 'large_dataset' / 'synthetic' / 'synthetic_patients_complete.csv'
        real_csv = project_root / 'data' / 'real_data' / 'csv' / 'real_dataset_complete.csv'
        if not real_csv.exists():
            real_csv = project_root / 'data' / 'large_dataset' / 'real' / 'real_patients_complete.csv'
    
        # Load CSV files
        synthetic_df = None
        real_df = None
    
        try:
            if synthetic_csv.exists():
                synthetic_df = pd.read_csv(synthetic_csv)
                logger.info(f"Loaded synthetic data: {len(synthetic_df)} records")
                logger.info(f"Synthetic CSV columns: {list(synthetic_df.columns)}")
            else:
                logger.warning(f"Synthetic CSV not found: {synthetic_csv}")
        except Exception as e:
            logger.error(f"Error loading synthetic CSV: {e}", exc_info=True)
            synthetic_df = None
    
        try:
            if real_csv.exists():
                real_df = pd.read_csv(real_csv)
                logger.info(f"Loaded real data: {len(real_df)} records")
                logger.info(f"Real CSV columns: {list(real_df.columns)}")
            else:
                logger.warning(f"Real CSV not found: {real_csv}")
        except Exception as e:
            logger.error(f"Error loading real CSV: {e}", exc_info=True)
            real_df = None
    
        if synthetic_df is None and real_df is None:
            return {
                "message": "No CSV data files found. Please ensure data files exist.",
                "total_patients": 0,
                "total_records": 0,
                "total_predictions": 0,
                "skipped": 0,
                "errors": ["No CSV files found"],
                "error_count": 1,
            }
    
        # Categorize and sample from each dataset
        def categorize_df(df):
            try:
                # Check if diagnosis column exists
                if 'diagnosis' not in df.columns:
                    logger.warning(f"CSV file missing 'diagnosis' column. Available columns: {list(df.columns)}")
                    # Return empty dataframes
                    return df.iloc[0:0].copy(), df.iloc[0:0].copy(), df.iloc[0:0].copy()
                
                # Convert diagnosis to string and handle NaN values
                df['diagnosis'] = df['diagnosis'].astype(str).str.upper().str.strip()
                
                normal = df[df['diagnosis'] == 'NORMAL']
                alzheimer = df[df['diagnosis'] == 'ALZHEIMER']
                parkinson = df[df['diagnosis'] == 'PARKINSON']
                return normal, alzheimer, parkinson
            except Exception as e:
                logger.error(f"Error categorizing dataframe: {e}", exc_info=True)
                # Return empty dataframes on error
                return df.iloc[0:0].copy(), df.iloc[0:0].copy(), df.iloc[0:0].copy()
    
        selected_rows = []
    
        # Sample from synthetic data - take all available
        # Target: 60 normal, 20 Alzheimer, 20 Parkinson (but take what's available)
        if synthetic_df is not None:
            syn_normal, syn_alzheimer, syn_parkinson = categorize_df(synthetic_df)
            
            # Take all available, up to target
            n_syn_normal = min(len(syn_normal), 60)
            n_syn_alzheimer = min(len(syn_alzheimer), 20)
            n_syn_parkinson = min(len(syn_parkinson), 20)
            
            if n_syn_normal > 0:
                selected_rows.extend(syn_normal.sample(n=n_syn_normal).to_dict('records'))
            if n_syn_alzheimer > 0:
                selected_rows.extend(syn_alzheimer.sample(n=n_syn_alzheimer).to_dict('records'))
            if n_syn_parkinson > 0:
                selected_rows.extend(syn_parkinson.sample(n=n_syn_parkinson).to_dict('records'))
            
            logger.info(f"Sampled from synthetic: {n_syn_normal} normal, {n_syn_alzheimer} Alzheimer, {n_syn_parkinson} Parkinson")
    
        # Sample from real data - take all available to reach 200 total
        # Calculate how many more we need to reach target of 120 normal, 40 Alzheimer, 40 Parkinson
        if real_df is not None:
            real_normal, real_alzheimer, real_parkinson = categorize_df(real_df)
            
            # Calculate needed to reach targets (accounting for what we got from synthetic)
            syn_normal_count = len([r for r in selected_rows if str(r.get('diagnosis', '')).upper().strip() == 'NORMAL'])
            syn_alzheimer_count = len([r for r in selected_rows if str(r.get('diagnosis', '')).upper().strip() == 'ALZHEIMER'])
            syn_parkinson_count = len([r for r in selected_rows if str(r.get('diagnosis', '')).upper().strip() == 'PARKINSON'])
            
            needed_normal = max(0, 120 - syn_normal_count)
            needed_alzheimer = max(0, 40 - syn_alzheimer_count)
            needed_parkinson = max(0, 40 - syn_parkinson_count)
            
            # Take what's available from real data
            n_real_normal = min(len(real_normal), needed_normal)
            n_real_alzheimer = min(len(real_alzheimer), needed_alzheimer)
            n_real_parkinson = min(len(real_parkinson), needed_parkinson)
            
            if n_real_normal > 0:
                selected_rows.extend(real_normal.sample(n=n_real_normal).to_dict('records'))
            if n_real_alzheimer > 0:
                selected_rows.extend(real_alzheimer.sample(n=n_real_alzheimer).to_dict('records'))
            if n_real_parkinson > 0:
                selected_rows.extend(real_parkinson.sample(n=n_real_parkinson).to_dict('records'))
            
            logger.info(f"Sampled from real: {n_real_normal} normal, {n_real_alzheimer} Alzheimer, {n_real_parkinson} Parkinson")
    
        logger.info(f"Selected {len(selected_rows)} patients for sample (Target: 200)")
    
        # Get or create a doctor user for created_by
        user_result = await db.execute(select(User).where(User.role == UserRole.DOCTOR).limit(1))
        doctor = user_result.scalar_one_or_none()
        if not doctor:
            user_result = await db.execute(select(User).limit(1))
            doctor = user_result.scalar_one_or_none()
        created_by_id = doctor.id if doctor else 1  # Fallback if no users exist
    
        # Process each selected patient row from CSV
        for idx, row in enumerate(selected_rows):
            try:
                # Validate required fields
                if 'patient_id' not in row or pd.isna(row.get('patient_id')):
                    errors.append(f"Row {idx}: Missing patient_id")
                    continue
                
                patient_id = str(row['patient_id']).strip()
            
                # Check if patient already exists
                result = await db.execute(
                    select(Patient).where(Patient.patient_id == patient_id)
                )
                patient = result.scalar_one_or_none()
            
                if patient:
                    # Check if patient already has medical records
                    result_mr = await db.execute(
                        select(MedicalRecord).where(MedicalRecord.patient_id == patient.id)
                    )
                    if result_mr.scalar_one_or_none():
                        skipped_patients += 1
                        continue
                else:
                    # Create new patient from CSV data
                    age = int(row['age'])
                    dob = date(datetime.now().year - age, 1, 1)
                
                    gender_str = str(row['gender']).lower()
                    gender = Gender.MALE if gender_str == 'male' else Gender.FEMALE if gender_str == 'female' else Gender.OTHER
                
                    patient = Patient(
                        patient_id=patient_id,
                        first_name=f"Patient",
                        last_name=patient_id.replace('PT_', ''),
                        date_of_birth=dob,
                        gender=gender,
                        education_years=int(row.get('education_years', 12)) if pd.notna(row.get('education_years')) else None,
                    )
                
                    db.add(patient)
                    await db.flush()
            
                # Parse visit date
                try:
                    visit_date = pd.to_datetime(row['visit_date'])
                except:
                    visit_date = datetime.now()
            
                # Create medical record from CSV
                medical_record = MedicalRecord(
                    patient_id=patient.id,
                    visit_date=visit_date,
                    visit_type="Initial",
                    mmse_score=float(row['mmse_score']) if pd.notna(row['mmse_score']) else None,
                    moca_score=float(row['moca_score']) if pd.notna(row['moca_score']) else None,
                    memory_score=float(row['memory_score']) if pd.notna(row['memory_score']) else None,
                    attention_score=float(row['attention_score']) if pd.notna(row['attention_score']) else None,
                    executive_function_score=float(row['executive_function_score']) if pd.notna(row['executive_function_score']) else None,
                    amyloid_beta=float(row['amyloid_beta']) if pd.notna(row['amyloid_beta']) else None,
                    tau_protein=float(row['tau_protein']) if pd.notna(row['tau_protein']) else None,
                    dopamine_level=float(row['dopamine_level']) if pd.notna(row['dopamine_level']) else None,
                    apoe_e4_status=bool(int(row['apoe_e4_status'])) if pd.notna(row['apoe_e4_status']) else False,
                    hippocampal_volume=float(row['hippocampal_volume']) if pd.notna(row['hippocampal_volume']) else None,
                    cortical_thickness=float(row['cortical_thickness']) if pd.notna(row['cortical_thickness']) else None,
                    ventricular_volume=float(row['ventricular_volume']) if pd.notna(row['ventricular_volume']) else None,
                    white_matter_hyperintensities=float(row['white_matter_hyperintensities']) if pd.notna(row['white_matter_hyperintensities']) else None,
                    brain_volume_total=float(row['brain_volume_total']) if pd.notna(row['brain_volume_total']) else None,
                    clinical_notes=f"Sample data (200 patients). Diagnosis: {row.get('diagnosis', 'Unknown')}",
                )
            
                db.add(medical_record)
                await db.flush()
                total_records_created += 1
            
                # Calculate risk scores based on diagnosis
                diagnosis = str(row.get('diagnosis', 'Normal')).upper()
                mmse = medical_record.mmse_score or 25
                moca = medical_record.moca_score or 24
                amyloid = medical_record.amyloid_beta or 600
                tau = medical_record.tau_protein or 200
                dopamine = medical_record.dopamine_level or 100
                hippocampal = medical_record.hippocampal_volume or 3500
            
                alzheimer_risk = 0.0
                parkinson_risk = 0.0
            
                if diagnosis == 'ALZHEIMER':
                    alzheimer_risk = 0.85
                    if mmse < 20: alzheimer_risk = 0.95
                    elif mmse < 24: alzheimer_risk = 0.80
                    if tau > 500 and amyloid < 500: alzheimer_risk = min(0.98, alzheimer_risk + 0.1)
                    if hippocampal < 2500: alzheimer_risk = min(0.98, alzheimer_risk + 0.08)
                elif diagnosis == 'PARKINSON':
                    parkinson_risk = 0.80
                    if dopamine < 50: parkinson_risk = 0.90
                    elif dopamine < 70: parkinson_risk = 0.75
                    if mmse >= 26: parkinson_risk = min(0.95, parkinson_risk + 0.1)
                else:  # Normal
                    alzheimer_risk = 0.15
                    parkinson_risk = 0.12
                    if mmse >= 28 and moca >= 26:
                        alzheimer_risk = 0.08
                        parkinson_risk = 0.05
            
                alzheimer_level = (
                    RiskLevel.HIGH if alzheimer_risk >= 0.66
                    else RiskLevel.MEDIUM if alzheimer_risk >= 0.33
                    else RiskLevel.LOW
                )
                parkinson_level = (
                    RiskLevel.HIGH if parkinson_risk >= 0.66
                    else RiskLevel.MEDIUM if parkinson_risk >= 0.33
                    else RiskLevel.LOW
                )
            
                # Determine disease type
                if diagnosis == 'ALZHEIMER':
                    disease_type = DiseaseType.ALZHEIMER
                elif diagnosis == 'PARKINSON':
                    disease_type = DiseaseType.PARKINSON
                else:  # Normal - assessed for both diseases
                    disease_type = DiseaseType.BOTH
            
                # Create prediction
                prediction = Prediction(
                    patient_id=patient.id,
                    created_by=created_by_id,
                    disease_type=disease_type,
                    alzheimer_risk_score=round(alzheimer_risk, 2),
                    parkinson_risk_score=round(parkinson_risk, 2),
                    alzheimer_risk_level=alzheimer_level,
                    parkinson_risk_level=parkinson_level,
                    created_at=datetime.now(),
                )
            
                db.add(prediction)
                total_predictions_created += 1
                total_patients_processed += 1
            
                if (idx + 1) % 50 == 0:
                    logger.info(f"Progress: {idx + 1}/{len(selected_rows)} records processed...")
            
            except Exception as e:
                logger.error(f"Error processing row {idx}: {str(e)}", exc_info=True)
                errors.append(f"Row {idx}: {str(e)[:100]}")
                continue
    
        # Commit all changes
        try:
            await db.commit()
            logger.info(f"SUCCESS: {total_patients_processed} patients (200 sample), {total_records_created} records, {total_predictions_created} predictions")
        except Exception as e:
            logger.error(f"Failed to commit: {e}", exc_info=True)
            await db.rollback()
        
            # Provide detailed error message
            error_detail = f"Failed to save data: {str(e)}"
            if errors:
                error_detail += f". Processing errors: {len(errors)} errors occurred. First error: {errors[0] if errors else 'Unknown'}"
        
            raise HTTPException(
                status_code=500,
                detail=error_detail
            )
    
        # Count categories from loaded rows
        normal_count = len([r for r in selected_rows if str(r.get('diagnosis', '')).upper() == 'NORMAL'])
        alzheimer_count = len([r for r in selected_rows if str(r.get('diagnosis', '')).upper() == 'ALZHEIMER'])
        parkinson_count = len([r for r in selected_rows if str(r.get('diagnosis', '')).upper() == 'PARKINSON'])
    
        # Create appropriate message
        if skipped_patients > 0 and total_patients_processed == 0:
            message = f"⚠️ All {len(selected_rows)} patients already exist in database! Please use 'Clear All Data' button first, then try loading again."
        elif skipped_patients > 0:
            message = f"Loaded {total_patients_processed} patients successfully ({skipped_patients} skipped - already exist)"
        elif errors:
            message = f"Loaded {total_patients_processed} patients with {len(errors)} errors"
        else:
            message = f"Successfully loaded {total_patients_processed} patients!"
    
        return {
            "message": message,
            "total_patients": total_patients_processed,
            "total_records": total_records_created,
            "total_predictions": total_predictions_created,
            "skipped": skipped_patients,
            "sample_size": len(selected_rows),
            "categories_included": f"Normal: {normal_count}, Alzheimer: {alzheimer_count}, Parkinson: {parkinson_count}",
            "source_distribution": f"{len(selected_rows)} total available in CSV files",
            "errors": errors[:10] if errors else [],
            "error_count": len(errors),
        }
    except Exception as e:
        logger.error(f"Unexpected error in load_sample_datasets: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load sample datasets: {str(e)}. Check backend logs for details."
        )


@router.post("/clear-all-data")
async def clear_all_disease_tracking_data(
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(require_role("admin")),  # Disabled for development
) -> Dict[str, Any]:
    """
    Clear all patients, medical records, predictions, and fusion reports from the disease tracking system.
    WARNING: This deletes ALL data!
    """
    import logging
    from ..models.data_fusion_report import DataFusionReport
    
    logger = logging.getLogger(__name__)
    logger.info("=== Clearing all disease tracking data ===")
    
    try:
        # Delete all fusion reports first (to avoid foreign key issues)
        try:
            result = await db.execute(select(DataFusionReport))
            fusion_reports = result.scalars().all()
            for report in fusion_reports:
                await db.delete(report)
            fusion_reports_deleted = len(fusion_reports)
        except Exception as e:
            logger.warning(f"Could not delete fusion reports (may not exist or have schema issues): {e}")
            fusion_reports_deleted = 0
        
        # Delete all predictions
        result = await db.execute(select(Prediction))
        predictions = result.scalars().all()
        for pred in predictions:
            await db.delete(pred)
        predictions_deleted = len(predictions)
        
        # Delete all medical records
        result = await db.execute(select(MedicalRecord))
        records = result.scalars().all()
        for record in records:
            await db.delete(record)
        records_deleted = len(records)
        
        # Delete all patients
        result = await db.execute(select(Patient))
        patients = result.scalars().all()
        for patient in patients:
            await db.delete(patient)
        patients_deleted = len(patients)
        
        await db.commit()
        
        logger.info(f"Deleted {patients_deleted} patients, {records_deleted} records, {predictions_deleted} predictions, {fusion_reports_deleted} fusion reports")
        
        return {
            "message": "All disease tracking data cleared successfully",
            "patients_deleted": patients_deleted,
            "records_deleted": records_deleted,
            "predictions_deleted": predictions_deleted,
            "fusion_reports_deleted": fusion_reports_deleted,
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"Error clearing data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to clear data: {str(e)}")


@router.post("/add-default-data")
async def add_default_data_for_all_patients(
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(require_role("admin")),  # Disabled for development
) -> Dict[str, Any]:
    """
    Add default medical records and predictions for all patients who don't have any
    This is useful for populating disease tracking with sample data
    """
    import random
    from datetime import timedelta
    
    # Get all patients
    result = await db.execute(select(Patient))
    all_patients = result.scalars().all()
    
    if not all_patients:
        return {
            "message": "No patients found",
            "added_records": 0,
            "added_predictions": 0,
            "skipped": 0,
        }
    
    added_records = 0
    added_predictions = 0
    skipped = 0
    
    for patient in all_patients:
        # Check if patient already has medical records
        result = await db.execute(
            select(MedicalRecord).where(MedicalRecord.patient_id == patient.id)
        )
        existing_records = result.scalars().all()
        
        if existing_records:
            skipped += 1
            continue
        
        # Calculate age
        age = (datetime.now().date() - patient.date_of_birth).days // 365
        
        # Generate default medical data
        age_factor = max(0, (age - 50) / 30)
        age_adjustment = age_factor * random.uniform(-3, -1)
        
        mmse_score = max(18, min(30, 28.0 + age_adjustment + random.uniform(-2, 2)))
        moca_score = max(16, min(30, 26.0 + age_adjustment + random.uniform(-2, 2)))
        memory_score = max(50, min(100, 75.0 + age_adjustment * 5 + random.uniform(-10, 10)))
        attention_score = max(60, min(100, 80.0 + age_adjustment * 3 + random.uniform(-8, 8)))
        executive_score = max(55, min(100, 75.0 + age_adjustment * 4 + random.uniform(-10, 10)))
        
        amyloid_beta = random.uniform(450, 650)
        tau_protein = random.uniform(180, 280)
        dopamine_level = random.uniform(85, 115)
        
        if random.random() < 0.2:
            amyloid_beta = random.uniform(300, 400)
            tau_protein = random.uniform(300, 450)
        if random.random() < 0.15:
            dopamine_level = random.uniform(50, 75)
        
        apoe_e4_status = random.random() < 0.25
        
        hippocampal_volume = random.uniform(3500, 4800)
        cortical_thickness = random.uniform(2.3, 2.9)
        ventricular_volume = random.uniform(18000, 28000)
        white_matter_hyperintensities = random.uniform(0.5, 2.5)
        brain_volume_total = random.uniform(1050000, 1150000)
        
        if age > 70:
            hippocampal_volume *= random.uniform(0.85, 0.95)
            cortical_thickness *= random.uniform(0.90, 0.98)
            ventricular_volume *= random.uniform(1.05, 1.15)
        
        # Create medical record
        visit_date = datetime.now() - timedelta(days=random.randint(0, 90))
        medical_record = MedicalRecord(
            patient_id=patient.id,
            visit_date=visit_date,
            visit_type="Initial",
            mmse_score=round(mmse_score, 1),
            moca_score=round(moca_score, 1),
            memory_score=round(memory_score, 1),
            attention_score=round(attention_score, 1),
            executive_function_score=round(executive_score, 1),
            amyloid_beta=round(amyloid_beta, 1),
            tau_protein=round(tau_protein, 1),
            dopamine_level=round(dopamine_level, 1),
            apoe_e4_status=apoe_e4_status,
            hippocampal_volume=round(hippocampal_volume, 0),
            cortical_thickness=round(cortical_thickness, 2),
            ventricular_volume=round(ventricular_volume, 0),
            white_matter_hyperintensities=round(white_matter_hyperintensities, 2),
            brain_volume_total=round(brain_volume_total, 0),
            symptoms="Routine check-up",
            clinical_notes=f"Initial assessment for disease tracking. Age: {age}, Gender: {patient.gender.value}",
        )
        
        db.add(medical_record)
        await db.flush()
        
        # Calculate risk scores
        alzheimer_risk = 0.0
        parkinson_risk = 0.0
        
        if mmse_score < 24:
            alzheimer_risk += 0.3
        if moca_score < 22:
            alzheimer_risk += 0.25
        if amyloid_beta < 400:
            alzheimer_risk += 0.35
        if tau_protein > 350:
            alzheimer_risk += 0.3
        if hippocampal_volume < 3000:
            alzheimer_risk += 0.25
        if apoe_e4_status:
            alzheimer_risk += 0.2
        if age > 75:
            alzheimer_risk += 0.15
        
        if dopamine_level < 70:
            parkinson_risk += 0.5
        if dopamine_level < 50:
            parkinson_risk += 0.3
        if age > 70:
            parkinson_risk += 0.2
        if attention_score < 65:
            parkinson_risk += 0.15
        
        alzheimer_risk = min(1.0, alzheimer_risk)
        parkinson_risk = min(1.0, parkinson_risk)
        
        alzheimer_level = (
            RiskLevel.HIGH if alzheimer_risk >= 0.66
            else RiskLevel.MEDIUM if alzheimer_risk >= 0.33
            else RiskLevel.LOW
        )
        parkinson_level = (
            RiskLevel.HIGH if parkinson_risk >= 0.66
            else RiskLevel.MEDIUM if parkinson_risk >= 0.33
            else RiskLevel.LOW
        )
        
        # Create prediction
        prediction = Prediction(
            patient_id=patient.id,
            disease_type=DiseaseType.BOTH,
            alzheimer_risk_score=alzheimer_risk,
            parkinson_risk_score=parkinson_risk,
            alzheimer_risk_level=alzheimer_level,
            parkinson_risk_level=parkinson_level,
            created_at=datetime.now(),
        )
        
        db.add(prediction)
        added_records += 1
        added_predictions += 1
    
    await db.commit()
    
    return {
        "message": "Default data added successfully",
        "added_records": added_records,
        "added_predictions": added_predictions,
        "skipped": skipped,
        "total_patients": len(all_patients),
    }


