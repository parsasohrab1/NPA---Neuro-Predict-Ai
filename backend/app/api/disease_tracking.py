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
from ..models.patient import Patient
from ..models.medical_record import MedicalRecord
from ..models.prediction import Prediction
from ..services.ai_model_service import AIModelService

router = APIRouter(prefix="/disease-tracking", tags=["Disease Tracking"])

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
    current_user = Depends(require_role("doctor")),
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

    for record in records:
        date = record.visit_date.isoformat()
        
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
        "latest_values": {
            "mmse_score": latest_record.mmse_score if latest_record else None,
            "moca_score": latest_record.moca_score if latest_record else None,
            "amyloid_beta": latest_record.amyloid_beta if latest_record else None,
            "tau_protein": latest_record.tau_protein if latest_record else None,
            "dopamine_level": latest_record.dopamine_level if latest_record else None,
            "hippocampal_volume": latest_record.hippocampal_volume if latest_record else None,
            "cortical_thickness": latest_record.cortical_thickness if latest_record else None,
            "apoe_e4_status": latest_record.apoe_e4_status if latest_record else None,
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
    current_user = Depends(require_role("doctor")),
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
    current_user = Depends(require_role("doctor")),
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


@router.get("/all-patients/summary")
async def get_all_patients_summary(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin")),
) -> Dict[str, Any]:
    """
    Get summary of all patients with their risk levels and alerts
    """
    # Get all patients with recent predictions
    result = await db.execute(
        select(Patient, Prediction)
        .join(Prediction, Patient.id == Prediction.patient_id)
        .order_by(Prediction.created_at.desc())
    )
    patients_data = result.all()

    summary = {
        "total_patients": 0,
        "high_risk_alzheimer": 0,
        "high_risk_parkinson": 0,
        "medium_risk_alzheimer": 0,
        "medium_risk_parkinson": 0,
        "low_risk": 0,
        "patients": [],
    }

    patient_ids_seen = set()
    for patient, prediction in patients_data:
        if patient.id in patient_ids_seen:
            continue
        patient_ids_seen.add(patient.id)
        
        summary["total_patients"] += 1
        
        alz_risk = prediction.alzheimer_risk_score or 0
        park_risk = prediction.parkinson_risk_score or 0
        
        if alz_risk > 0.66 or park_risk > 0.66:
            summary["high_risk_alzheimer"] += 1 if alz_risk > 0.66 else 0
            summary["high_risk_parkinson"] += 1 if park_risk > 0.66 else 0
        elif alz_risk > 0.33 or park_risk > 0.33:
            summary["medium_risk_alzheimer"] += 1 if alz_risk > 0.33 else 0
            summary["medium_risk_parkinson"] += 1 if park_risk > 0.33 else 0
        else:
            summary["low_risk"] += 1
        
        summary["patients"].append({
            "patient_id": patient.id,
            "name": f"{patient.first_name} {patient.last_name}",
            "alzheimer_risk": alz_risk,
            "parkinson_risk": park_risk,
            "last_prediction_date": prediction.created_at.isoformat(),
        })

    return summary

