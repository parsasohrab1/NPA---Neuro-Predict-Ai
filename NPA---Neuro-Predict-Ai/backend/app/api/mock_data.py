"""
Mock Data API Endpoints for development/demo
Returns sample data without requiring database
"""
from fastapi import APIRouter
from typing import List
from datetime import datetime, timedelta, date
import random

router = APIRouter(prefix="/mock", tags=["Mock Data"])


# Sample patients data
MOCK_PATIENTS = [
    {
        "id": 1,
        "patient_id": "PT-2024-001",
        "first_name": "احمد",
        "last_name": "محمدی",
        "date_of_birth": "1955-03-15",
        "gender": "male",
        "email": "ahmad.mohammadi@example.com",
        "phone": "09123456789",
        "education_years": 12,
        "medical_history": "فشار خون بالا، دیابت نوع 2",
        "family_history": "سابقه آلزایمر در مادر",
        "created_at": (datetime.now() - timedelta(days=90)).isoformat(),
    },
    {
        "id": 2,
        "patient_id": "PT-2024-002",
        "first_name": "فاطمه",
        "last_name": "حسینی",
        "date_of_birth": "1948-07-22",
        "gender": "female",
        "email": "fateme.hosseini@example.com",
        "phone": "09123456790",
        "education_years": 16,
        "medical_history": "پوکی استخوان",
        "family_history": "سابقه پارکینسون در پدر",
        "created_at": (datetime.now() - timedelta(days=75)).isoformat(),
    },
    {
        "id": 3,
        "patient_id": "PT-2024-003",
        "first_name": "محمد",
        "last_name": "کریمی",
        "date_of_birth": "1960-11-08",
        "gender": "male",
        "email": "mohammad.karimi@example.com",
        "phone": "09123456791",
        "education_years": 14,
        "medical_history": "بیماری قلبی",
        "family_history": "بدون سابقه",
        "created_at": (datetime.now() - timedelta(days=60)).isoformat(),
    },
    {
        "id": 4,
        "patient_id": "PT-2024-004",
        "first_name": "زهرا",
        "last_name": "احمدی",
        "date_of_birth": "1952-05-30",
        "gender": "female",
        "email": "zahra.ahmadi@example.com",
        "phone": "09123456792",
        "education_years": 10,
        "medical_history": "کم‌خونی",
        "family_history": "سابقه آلزایمر در خواهر",
        "created_at": (datetime.now() - timedelta(days=45)).isoformat(),
    },
    {
        "id": 5,
        "patient_id": "PT-2024-005",
        "first_name": "علی",
        "last_name": "نوری",
        "date_of_birth": "1958-09-12",
        "gender": "male",
        "email": "ali.nouri@example.com",
        "phone": "09123456793",
        "education_years": 18,
        "medical_history": "آرتریت",
        "family_history": "بدون سابقه",
        "created_at": (datetime.now() - timedelta(days=30)).isoformat(),
    },
    {
        "id": 6,
        "patient_id": "PT-2024-006",
        "first_name": "مریم",
        "last_name": "صادقی",
        "date_of_birth": "1945-12-03",
        "gender": "female",
        "email": "maryam.sadeghi@example.com",
        "phone": "09123456794",
        "education_years": 8,
        "medical_history": "دیابت، فشار خون",
        "family_history": "سابقه پارکینسون در مادر",
        "created_at": (datetime.now() - timedelta(days=15)).isoformat(),
    },
    {
        "id": 7,
        "patient_id": "PT-2024-007",
        "first_name": "حسن",
        "last_name": "رضایی",
        "date_of_birth": "1962-02-18",
        "gender": "male",
        "email": "hasan.rezaei@example.com",
        "phone": "09123456795",
        "education_years": 15,
        "medical_history": "بدون سابقه",
        "family_history": "بدون سابقه",
        "created_at": (datetime.now() - timedelta(days=7)).isoformat(),
    },
    {
        "id": 8,
        "patient_id": "PT-2024-008",
        "first_name": "سمیه",
        "last_name": "موسوی",
        "date_of_birth": "1950-08-25",
        "gender": "female",
        "email": "somayeh.mousavi@example.com",
        "phone": "09123456796",
        "education_years": 12,
        "medical_history": "مشکلات تیروئید",
        "family_history": "سابقه آلزایمر در مادربزرگ",
        "created_at": (datetime.now() - timedelta(days=3)).isoformat(),
    },
]


def generate_mock_predictions():
    """Generate mock predictions for all patients"""
    predictions = []
    for i, patient in enumerate(MOCK_PATIENTS):
        # Generate 1-3 predictions per patient
        num_preds = random.randint(1, 3)
        for j in range(num_preds):
            age = (datetime.now().date() - datetime.fromisoformat(patient["date_of_birth"]).date()).days / 365.25
            
            # Calculate risk scores
            alzheimer_risk = min(0.95, max(0.1, (age - 60) / 40.0 * 0.4 + random.uniform(0.2, 0.6)))
            parkinson_risk = min(0.95, max(0.1, (age - 60) / 40.0 * 0.3 + random.uniform(0.15, 0.55)))
            
            def get_risk_level(score):
                if score < 0.33:
                    return "low"
                elif score < 0.66:
                    return "medium"
                else:
                    return "high"
            
            disease_type = "both" if alzheimer_risk > 0.5 and parkinson_risk > 0.5 else \
                          "alzheimer" if alzheimer_risk > parkinson_risk else "parkinson"
            
            predictions.append({
                "id": len(predictions) + 1,
                "patient_id": patient["id"],
                "created_by": 1,
                "disease_type": disease_type,
                "alzheimer_risk_score": round(alzheimer_risk, 3),
                "alzheimer_risk_level": get_risk_level(alzheimer_risk),
                "alzheimer_confidence": round(1.0 - 2.0 * abs(alzheimer_risk - 0.5), 3),
                "parkinson_risk_score": round(parkinson_risk, 3),
                "parkinson_risk_level": get_risk_level(parkinson_risk),
                "parkinson_confidence": round(1.0 - 2.0 * abs(parkinson_risk - 0.5), 3),
                "model_version": "1.0.0-mock",
                "model_name": "MockPredictionModel",
                "created_at": (datetime.now() - timedelta(days=random.randint(0, 180), hours=random.randint(0, 23))).isoformat(),
            })
    
    return predictions


MOCK_PREDICTIONS = generate_mock_predictions()


@router.get("/patients")
async def get_mock_patients():
    """Get mock patients data"""
    return MOCK_PATIENTS


@router.get("/predictions")
async def get_mock_predictions():
    """Get mock predictions data"""
    return MOCK_PREDICTIONS


@router.get("/reports/summary")
async def get_mock_report_summary():
    """Get mock report summary"""
    high_risk = len([p for p in MOCK_PREDICTIONS if p["alzheimer_risk_level"] == "high" or p["parkinson_risk_level"] == "high"])
    
    return {
        "report_type": "clinical",
        "period": {
            "start": (datetime.now() - timedelta(days=30)).isoformat(),
            "end": datetime.now().isoformat()
        },
        "statistics": {
            "total_patients": len(MOCK_PATIENTS),
            "total_predictions": len(MOCK_PREDICTIONS),
            "high_risk_cases": high_risk,
            "low_risk_cases": len(MOCK_PREDICTIONS) - high_risk
        }
    }


@router.get("/reports/predictions-trend")
async def get_mock_predictions_trend(days: int = 30):
    """Get mock predictions trend"""
    trend_data = []
    for i in range(days):
        date_str = (datetime.now() - timedelta(days=days-i-1)).date().isoformat()
        count = len([p for p in MOCK_PREDICTIONS if p["created_at"].startswith(date_str)])
        trend_data.append({
            "date": date_str,
            "count": count if count > 0 else random.randint(0, 3)
        })
    
    return {
        "period_days": days,
        "data": trend_data
    }


@router.get("/reports/risk-distribution")
async def get_mock_risk_distribution():
    """Get mock risk distribution"""
    low = len([p for p in MOCK_PREDICTIONS if p["alzheimer_risk_level"] == "low" and p["parkinson_risk_level"] == "low"])
    medium = len([p for p in MOCK_PREDICTIONS if p["alzheimer_risk_level"] == "medium" or p["parkinson_risk_level"] == "medium"])
    high = len([p for p in MOCK_PREDICTIONS if p["alzheimer_risk_level"] == "high" or p["parkinson_risk_level"] == "high"])
    
    return {
        "distribution": {
            "low": low,
            "medium": medium,
            "high": high
        },
        "total": len(MOCK_PREDICTIONS)
    }


@router.get("/analytics/population/age-distribution")
async def get_mock_age_distribution():
    """Get mock age distribution"""
    age_groups = {"40-50": 0, "50-60": 0, "60-70": 0, "70-80": 0, "80+": 0}
    
    for patient in MOCK_PATIENTS:
        age = (datetime.now().date() - datetime.fromisoformat(patient["date_of_birth"]).date()).days / 365.25
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


@router.get("/analytics/population/gender-distribution")
async def get_mock_gender_distribution():
    """Get mock gender distribution"""
    male = len([p for p in MOCK_PATIENTS if p["gender"] == "male"])
    female = len([p for p in MOCK_PATIENTS if p["gender"] == "female"])
    total = len(MOCK_PATIENTS)
    
    return {
        "distribution": [
            {"gender": "Male", "value": male, "count": male, "percentage": round(male/total*100, 1)},
            {"gender": "Female", "value": female, "count": female, "percentage": round(female/total*100, 1)}
        ]
    }


@router.get("/analytics/population/statistics")
async def get_mock_population_statistics():
    """Get mock population statistics"""
    high_risk = len([p for p in MOCK_PREDICTIONS if p["alzheimer_risk_level"] == "high" or p["parkinson_risk_level"] == "high"])
    total_age = sum([(datetime.now().date() - datetime.fromisoformat(p["date_of_birth"]).date()).days / 365.25 for p in MOCK_PATIENTS])
    
    return {
        "total_patients": len(MOCK_PATIENTS),
        "total_predictions": len(MOCK_PREDICTIONS),
        "high_risk_cases": high_risk,
        "prevalence_percentage": round(high_risk / len(MOCK_PATIENTS) * 100, 2) if MOCK_PATIENTS else 0,
        "average_age": round(total_age / len(MOCK_PATIENTS), 1) if MOCK_PATIENTS else 0,
        "predictions_per_patient": round(len(MOCK_PREDICTIONS) / len(MOCK_PATIENTS), 1) if MOCK_PATIENTS else 0
    }


@router.get("/analytics/longitudinal/{patient_id}")
async def get_mock_longitudinal_data(patient_id: int):
    """Get mock longitudinal data for a patient"""
    patient_predictions = [p for p in MOCK_PREDICTIONS if p["patient_id"] == patient_id]
    
    timeline = []
    for pred in patient_predictions:
        timeline.append({
            "date": pred["created_at"],
            "prediction_id": pred["id"],
            "alzheimer_risk_score": pred["alzheimer_risk_score"],
            "parkinson_risk_score": pred["parkinson_risk_score"],
        })
    
    # Sort by date
    timeline.sort(key=lambda x: x["date"])
    
    return {
        "patient_id": patient_id,
        "total_predictions": len(patient_predictions),
        "timeline": timeline
    }


@router.get("/models/")
async def get_mock_models():
    """Get mock models"""
    return {
        "models": [
            {
                "id": "alzheimer-v1.0",
                "name": "Alzheimer Prediction Model",
                "version": "1.0.0",
                "status": "active",
                "disease_type": "alzheimer",
                "accuracy": 0.95,
                "precision": 0.93,
                "recall": 0.94,
                "f1_score": 0.935,
            },
            {
                "id": "parkinson-v1.0",
                "name": "Parkinson Prediction Model",
                "version": "1.0.0",
                "status": "active",
                "disease_type": "parkinson",
                "accuracy": 0.92,
                "precision": 0.91,
                "recall": 0.90,
                "f1_score": 0.905,
            }
        ],
        "total": 2
    }


@router.get("/users/")
async def get_mock_users():
    """Get mock users"""
    return [
        {
            "id": 1,
            "email": "doctor@neuropredict.ai",
            "username": "doctor",
            "full_name": "دکتر نمونه",
            "role": "doctor",
            "is_active": True
        },
        {
            "id": 2,
            "email": "admin@neuropredict.ai",
            "username": "admin",
            "full_name": "مدیر سیستم",
            "role": "admin",
            "is_active": True
        }
    ]
