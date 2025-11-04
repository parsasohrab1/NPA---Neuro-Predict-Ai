"""
Analytics API Endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime, timedelta

from ..db.session import get_db
from ..models.user import User
from ..models.patient import Patient
from ..models.prediction import Prediction
from ..core.security import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/population/age-distribution")
async def get_age_distribution(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get age distribution of patients"""
    result = await db.execute(select(Patient))
    patients = result.scalars().all()
    
    age_groups = {
        "40-50": 0,
        "50-60": 0,
        "60-70": 0,
        "70-80": 0,
        "80+": 0
    }
    
    today = datetime.now().date()
    
    for patient in patients:
        age = (today - patient.date_of_birth).days / 365.25
        
        if 40 <= age < 50:
            age_groups["40-50"] += 1
        elif 50 <= age < 60:
            age_groups["50-60"] += 1
        elif 60 <= age < 70:
            age_groups["60-70"] += 1
        elif 70 <= age < 80:
            age_groups["70-80"] += 1
        elif age >= 80:
            age_groups["80+"] += 1
    
    return {
        "distribution": [
            {"age_group": k, "count": v}
            for k, v in age_groups.items()
        ]
    }


@router.get("/population/gender-distribution")
async def get_gender_distribution(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get gender distribution of patients"""
    male_count = await db.scalar(
        select(func.count(Patient.id)).where(Patient.gender == "male")
    )
    
    female_count = await db.scalar(
        select(func.count(Patient.id)).where(Patient.gender == "female")
    )
    
    total = male_count + female_count
    
    return {
        "distribution": [
            {"gender": "Male", "count": male_count, "percentage": (male_count / total * 100) if total > 0 else 0},
            {"gender": "Female", "count": female_count, "percentage": (female_count / total * 100) if total > 0 else 0}
        ],
        "total": total
    }


@router.get("/population/statistics")
async def get_population_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overall population statistics"""
    total_patients = await db.scalar(select(func.count(Patient.id)))
    total_predictions = await db.scalar(select(func.count(Prediction.id)))
    
    # High risk cases
    result = await db.execute(select(Prediction))
    predictions = result.scalars().all()
    high_risk_count = len([p for p in predictions if 
                          (hasattr(p, 'alzheimer_risk_level') and p.alzheimer_risk_level == 'high') or
                          (hasattr(p, 'parkinson_risk_level') and p.parkinson_risk_level == 'high')])
    
    # Average age
    result = await db.execute(select(Patient))
    patients = result.scalars().all()
    today = datetime.now().date()
    ages = [(today - p.date_of_birth).days / 365.25 for p in patients]
    avg_age = sum(ages) / len(ages) if ages else 0
    
    prevalence = (high_risk_count / total_patients * 100) if total_patients > 0 else 0
    
    return {
        "total_patients": total_patients,
        "total_predictions": total_predictions,
        "high_risk_cases": high_risk_count,
        "average_age": round(avg_age, 1),
        "prevalence_percentage": round(prevalence, 2),
        "predictions_per_patient": round(total_predictions / total_patients, 1) if total_patients > 0 else 0
    }


@router.get("/longitudinal/{patient_id}")
async def get_longitudinal_data(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get longitudinal tracking data for a patient"""
    # Get all predictions for patient
    result = await db.execute(
        select(Prediction)
        .where(Prediction.patient_id == patient_id)
        .order_by(Prediction.created_at.asc())
    )
    predictions = result.scalars().all()
    
    timeline = []
    for pred in predictions:
        timeline.append({
            "date": pred.created_at.isoformat(),
            "event_type": "prediction",
            "prediction_id": pred.id,
            "alzheimer_risk_score": getattr(pred, 'alzheimer_risk_score', None),
            "parkinson_risk_score": getattr(pred, 'parkinson_risk_score', None),
        })
    
    return {
        "patient_id": patient_id,
        "timeline": timeline,
        "total_predictions": len(predictions)
    }
