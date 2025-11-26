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
        
        summary["patients"].append({
            "patient_id": patient.id,
            "name": f"{patient.first_name} {patient.last_name}",
            "alzheimer_risk": alz_risk,
            "parkinson_risk": park_risk,
            "last_prediction_date": latest_prediction.created_at.isoformat() if latest_prediction else None,
        })

    return summary


@router.post("/load-all-datasets")
async def load_all_datasets(
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(require_role("admin")),  # Disabled for development
) -> Dict[str, Any]:
    """
    Load all existing patients from database into disease tracking
    This creates medical records and predictions for all patients (500 total)
    """
    import random
    from datetime import timedelta
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Get ALL patients from database (not from CSV)
    result = await db.execute(select(Patient))
    all_patients = result.scalars().all()
    
    if not all_patients:
        return {
            "message": "No patients found in database",
            "total_patients": 0,
            "total_records": 0,
            "total_predictions": 0,
            "skipped": 0,
            "errors": [],
            "error_count": 0,
        }
    
    logger.info(f"Found {len(all_patients)} patients in database")
    
    total_patients = len(all_patients)
    total_records = 0
    total_predictions = 0
    skipped = 0
    errors = []
    
    # Process all existing patients from database
    for patient in all_patients:
        try:
            # Check if patient already has medical records
            result = await db.execute(
                select(MedicalRecord).where(MedicalRecord.patient_id == patient.id)
            )
            existing_records = result.scalars().all()
            
            if existing_records:
                # Patient already has medical records, skip
                skipped += 1
                continue
            
            # Calculate age
            age = (datetime.now().date() - patient.date_of_birth).days // 365
            
            # Generate realistic medical data based on age and existing patient data
            age_factor = max(0, (age - 50) / 30)
            age_adjustment = age_factor * random.uniform(-3, -1)
            
            mmse_score = max(18, min(30, 28.0 + age_adjustment + random.uniform(-2, 2)))
            moca_score = max(16, min(30, 26.0 + age_adjustment + random.uniform(-2, 2)))
            memory_score = max(50, min(100, 75.0 + age_adjustment * 5 + random.uniform(-10, 10)))
            attention_score = max(60, min(100, 80.0 + age_adjustment * 3 + random.uniform(-8, 8)))
            executive_score = max(55, min(100, 75.0 + age_adjustment * 4 + random.uniform(-10, 10)))
            
            # Biomarkers - vary based on patient type (from patient_id)
            patient_id = patient.patient_id
            is_alzheimer = 'AD' in patient_id.upper() or 'ALZHEIMER' in patient_id.upper()
            is_parkinson = 'PD' in patient_id.upper() or 'PARKINSON' in patient_id.upper()
            
            if is_alzheimer:
                # Alzheimer's patients - low amyloid-beta, high tau
                amyloid_beta = random.uniform(250, 400)
                tau_protein = random.uniform(350, 550)
                dopamine_level = random.uniform(90, 120)
                hippocampal_volume = random.uniform(2200, 3000)
                mmse_score = max(15, min(25, mmse_score - random.uniform(3, 7)))
                moca_score = max(13, min(23, moca_score - random.uniform(3, 7)))
            elif is_parkinson:
                # Parkinson's patients - low dopamine
                amyloid_beta = random.uniform(450, 700)
                tau_protein = random.uniform(180, 300)
                dopamine_level = random.uniform(40, 75)
                hippocampal_volume = random.uniform(3300, 4200)
                mmse_score = max(20, min(28, mmse_score - random.uniform(1, 3)))
                moca_score = max(18, min(26, moca_score - random.uniform(1, 3)))
            else:
                # Normal patients
                amyloid_beta = random.uniform(550, 750)
                tau_protein = random.uniform(150, 250)
                dopamine_level = random.uniform(95, 125)
                hippocampal_volume = random.uniform(3700, 4500)
            
            apoe_e4_status = random.random() < (0.7 if is_alzheimer else 0.3 if is_parkinson else 0.2)
            
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
                symptoms="Loaded for disease tracking",
                clinical_notes=f"Medical record created for disease tracking. Age: {age}, Patient Type: {patient_id}",
            )
            
            db.add(medical_record)
            await db.flush()
            total_records += 1
            
            # Calculate risk scores based on medical data
            alzheimer_risk = 0.0
            parkinson_risk = 0.0
            
            # Alzheimer's risk factors
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
            
            # Parkinson's risk factors
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
            
            from ..models.prediction import RiskLevel, DiseaseType
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
            if alzheimer_risk > 0.6 and parkinson_risk > 0.6:
                disease_type = DiseaseType.BOTH
            elif alzheimer_risk > parkinson_risk and alzheimer_risk > 0.5:
                disease_type = DiseaseType.ALZHEIMER
            elif parkinson_risk > alzheimer_risk and parkinson_risk > 0.5:
                disease_type = DiseaseType.PARKINSON
            else:
                disease_type = DiseaseType.BOTH
            
            # Create prediction
            prediction = Prediction(
                patient_id=patient.id,
                disease_type=disease_type,
                alzheimer_risk_score=alzheimer_risk,
                parkinson_risk_score=parkinson_risk,
                alzheimer_risk_level=alzheimer_level,
                parkinson_risk_level=parkinson_level,
                created_at=datetime.now(),
            )
            
            db.add(prediction)
            total_predictions += 1
            
        except Exception as e:
            logger.error(f"Error processing patient {patient.patient_id}: {str(e)}", exc_info=True)
            errors.append(f"Patient {patient.patient_id}: {str(e)[:100]}")
            continue
    
    try:
        await db.commit()
        logger.info(f"Successfully committed: {total_records} medical records, {total_predictions} predictions for {total_patients} total patients ({skipped} already had records)")
    except Exception as e:
        logger.error(f"Failed to commit changes: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save data to database: {str(e)}"
        )
    
    message = f"Loaded {total_patients} patients from database"
    if total_records > 0:
        message += f", created {total_records} medical records and {total_predictions} predictions"
    if skipped > 0:
        message += f" ({skipped} patients already had medical records)"
    
    return {
        "message": message,
        "total_patients": total_patients,
        "total_records": total_records,
        "total_predictions": total_predictions,
        "skipped": skipped,
        "errors": errors[:10] if errors else [],  # Return first 10 errors
        "error_count": len(errors),
    }


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
        
        from ..models.prediction import RiskLevel
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
        from ..models.prediction import DiseaseType
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

