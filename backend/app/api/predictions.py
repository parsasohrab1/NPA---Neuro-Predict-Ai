"""
AI Prediction API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from ..db.session import get_db
from ..models.user import User
from ..models.patient import Patient
from ..models.medical_record import MedicalRecord
from ..models.prediction import Prediction, DiseaseType
from ..schemas.prediction import PredictionRequest, PredictionResponse, PredictionReview
from ..core.security import get_current_user, require_role
from ..services.ai_model_service import ai_model_service

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post("/", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def create_prediction(
    request: PredictionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("doctor"))
):
    """Create a new disease risk prediction"""
    # Verify patient exists
    result = await db.execute(
        select(Patient).where(Patient.id == request.patient_id)
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {request.patient_id} not found"
        )
    
    # Get latest medical record
    result = await db.execute(
        select(MedicalRecord)
        .where(MedicalRecord.patient_id == request.patient_id)
        .order_by(MedicalRecord.visit_date.desc())
        .limit(1)
    )
    medical_record = result.scalar_one_or_none()
    
    if not medical_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No medical records found for this patient. Please add medical data first."
        )
    
    # Prepare patient data for prediction
    from datetime import date
    age = (date.today() - patient.date_of_birth).days / 365.25
    
    patient_data = {
        'age': age,
        'gender': patient.gender.value,
        'education_years': patient.education_years or 12,
        'mmse_score': medical_record.mmse_score or 25,
        'moca_score': medical_record.moca_score or 24,
        'memory_score': medical_record.memory_score or 50,
        'attention_score': medical_record.attention_score or 50,
        'executive_function_score': medical_record.executive_function_score or 50,
        'amyloid_beta': medical_record.amyloid_beta or 600,
        'tau_protein': medical_record.tau_protein or 200,
        'dopamine_level': medical_record.dopamine_level or 100,
        'apoe_e4_status': medical_record.apoe_e4_status or False,
        'hippocampal_volume': medical_record.hippocampal_volume or 3500,
        'cortical_thickness': medical_record.cortical_thickness or 2.3,
        'ventricular_volume': medical_record.ventricular_volume or 30000,
        'white_matter_hyperintensities': medical_record.white_matter_hyperintensities or 2,
        'brain_volume_total': medical_record.brain_volume_total or 1100000,
    }
    
    # Run AI prediction
    try:
        prediction_result = await ai_model_service.predict(patient_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during prediction: {str(e)}"
        )
    
    # Create prediction record
    new_prediction = Prediction(
        patient_id=request.patient_id,
        created_by=current_user.id,
        disease_type=request.disease_type,
        alzheimer_risk_score=prediction_result['alzheimer']['risk_score'],
        alzheimer_risk_level=prediction_result['alzheimer']['risk_level'],
        alzheimer_confidence=prediction_result['alzheimer']['confidence'],
        parkinson_risk_score=prediction_result['parkinson']['risk_score'],
        parkinson_risk_level=prediction_result['parkinson']['risk_level'],
        parkinson_confidence=prediction_result['parkinson']['confidence'],
        model_version=prediction_result['model_version'],
        model_name=prediction_result['model_name'],
        input_features=patient_data,
        feature_importance=prediction_result['feature_importance'],
        recommendations=prediction_result['recommendations']
    )
    
    db.add(new_prediction)
    await db.commit()
    await db.refresh(new_prediction)
    
    return new_prediction


@router.get("/", response_model=List[PredictionResponse])
async def get_predictions(
    patient_id: int = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of predictions with optional patient filter"""
    query = select(Prediction)
    
    if patient_id:
        query = query.where(Prediction.patient_id == patient_id)
    
    query = query.order_by(Prediction.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    predictions = result.scalars().all()
    
    return predictions


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get prediction by ID"""
    result = await db.execute(
        select(Prediction).where(Prediction.id == prediction_id)
    )
    prediction = result.scalar_one_or_none()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with ID {prediction_id} not found"
        )
    
    return prediction


@router.get("/{prediction_id}/imaging-studies")
async def get_prediction_imaging_studies(
    prediction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get imaging studies associated with a prediction (via patient's latest medical record)"""
    from ..models.imaging import ImagingStudy
    
    # Get prediction
    result = await db.execute(
        select(Prediction).where(Prediction.id == prediction_id)
    )
    prediction = result.scalar_one_or_none()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with ID {prediction_id} not found"
        )
    
    # Get latest medical record for patient
    result = await db.execute(
        select(MedicalRecord)
        .where(MedicalRecord.patient_id == prediction.patient_id)
        .order_by(MedicalRecord.visit_date.desc())
        .limit(1)
    )
    medical_record = result.scalar_one_or_none()
    
    if not medical_record:
        return []
    
    # Get imaging studies for this medical record
    result = await db.execute(
        select(ImagingStudy)
        .where(ImagingStudy.medical_record_id == medical_record.id)
        .order_by(ImagingStudy.study_date.desc())
    )
    studies = result.scalars().all()
    
    return [
        {
            "id": study.id,
            "study_id": study.study_id,
            "modality": study.modality.value,
            "study_date": study.study_date.isoformat() if study.study_date else None,
            "study_description": study.study_description,
            "image_count": study.image_count,
            "quality_score": study.quality_score,
        }
        for study in studies
    ]


@router.post("/{prediction_id}/review", response_model=PredictionResponse)
async def review_prediction(
    prediction_id: int,
    review: PredictionReview,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("doctor"))
):
    """Review and approve a prediction"""
    result = await db.execute(
        select(Prediction).where(Prediction.id == prediction_id)
    )
    prediction = result.scalar_one_or_none()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with ID {prediction_id} not found"
        )
    
    # Update review information
    prediction.is_reviewed = review.approved
    prediction.reviewed_by = current_user.id
    prediction.reviewed_at = datetime.utcnow()
    prediction.review_notes = review.review_notes
    
    await db.commit()
    await db.refresh(prediction)
    
    return prediction

