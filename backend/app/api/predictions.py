"""
AI Prediction API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from typing import List, Optional, Any
from datetime import date, datetime

from ..db.session import get_db
from ..models.user import User
from ..models.patient import Patient
from ..models.medical_record import MedicalRecord
from ..models.prediction import Prediction, DiseaseType
from ..models.audit import AuditLog
from ..schemas.prediction import PredictionRequest, PredictionResponse, PredictionReview
from ..core.security import get_current_user, require_role
from ..core.cache import cache_service
from ..services.ai_model_service import ai_model_service, ModelNotReadyError
from ..services.clinical_explainability_service import clinical_explainability_service

router = APIRouter(prefix="/predictions", tags=["Predictions"])

# Cache TTL in seconds
PREDICTION_ITEM_TTL = 300   # 5 min for single prediction
PREDICTION_LIST_TTL = 180  # 3 min for list


def _json_safe_metadata(obj: Any) -> Any:
    """Make metadata JSON-serializable (e.g. numpy scalars)."""
    if hasattr(obj, "item"):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _json_safe_metadata(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe_metadata(x) for x in obj]
    return obj


@router.post("/", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def create_prediction(
    request: PredictionRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
):
    """Create a new disease risk prediction"""
    # Single query: Patient + latest MedicalRecord via join and scalar subquery
    latest_mr_subq = (
        select(MedicalRecord.id)
        .where(MedicalRecord.patient_id == request.patient_id)
        .order_by(MedicalRecord.visit_date.desc())
        .limit(1)
        .scalar_subquery()
    )
    stmt = (
        select(Patient, MedicalRecord)
        .select_from(Patient)
        .outerjoin(
            MedicalRecord,
            (Patient.id == MedicalRecord.patient_id)
            & (MedicalRecord.id == latest_mr_subq),
        )
        .where(Patient.id == request.patient_id)
    )
    result = await db.execute(stmt)
    row = result.one_or_none()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {request.patient_id} not found"
        )

    patient, medical_record = row
    if medical_record is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No medical records found for this patient. Please add medical data first."
        )

    # Prepare patient data for prediction
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
    except ModelNotReadyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during prediction: {str(e)}"
        )
    
    # Build clinical explainability (feature importance with clinical labels, cohort comparison, progression)
    try:
        clinical_explanation = await clinical_explainability_service.build_full_explanation(
            db, request.patient_id, patient_data, prediction_result
        )
    except Exception as e:
        clinical_explanation = None
        logging.getLogger(__name__).warning("Clinical explanation build failed: %s", e)

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
        attention_scores=prediction_result.get('attention_scores'),
        clinical_explanation=clinical_explanation,
        recommendations=prediction_result['recommendations']
    )

    db.add(new_prediction)
    await db.flush()

    # Audit log for create_prediction (SRS: attention scores and details in audit)
    audit_metadata: dict = {
        "patient_id": request.patient_id,
        "prediction_id": new_prediction.id,
        "disease_type": request.disease_type.value if hasattr(request.disease_type, "value") else str(request.disease_type),
        "attention_score": patient_data.get("attention_score"),
        "attention_scores": _json_safe_metadata(prediction_result.get("attention_scores") or {}),
        "feature_importance": _json_safe_metadata(prediction_result.get("feature_importance") or {}),
        "alzheimer_risk_score": prediction_result["alzheimer"]["risk_score"],
        "parkinson_risk_score": prediction_result["parkinson"]["risk_score"],
        "model_version": prediction_result.get("model_version"),
        "model_name": prediction_result.get("model_name"),
    }
    audit_log = AuditLog(
        action="create_prediction",
        resource_type="prediction",
        resource_id=str(new_prediction.id),
        user_id=current_user.id,
        ip_address=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent"),
        request_method="POST",
        request_path="/predictions/",
        status_code=201,
        success="true",
        additional_metadata=audit_metadata,
    )
    db.add(audit_log)

    await db.commit()
    await db.refresh(new_prediction)

    # Invalidate cache: list for this patient and global list
    await cache_service.delete_pattern("prediction", f"list:{request.patient_id}:*")
    await cache_service.delete_pattern("prediction", "list:all:*")

    return new_prediction


def _prediction_to_cache_dict(p: Prediction) -> dict:
    """Convert Prediction ORM to JSON-serializable dict for cache."""
    resp = PredictionResponse.model_validate(p)
    return resp.model_dump(mode="json")


@router.get("/", response_model=List[PredictionResponse])
async def get_predictions(
    patient_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of predictions with optional patient filter (cached)."""
    cache_key = f"list:{patient_id or 'all'}:{skip}:{limit}"
    cached = await cache_service.get("prediction", cache_key)
    if cached is not None:
        return [PredictionResponse.model_validate(d) for d in cached]

    query = select(Prediction)
    if patient_id is not None:
        query = query.where(Prediction.patient_id == patient_id)
    query = query.order_by(Prediction.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    predictions = result.scalars().all()
    cache_value = [_prediction_to_cache_dict(p) for p in predictions]
    await cache_service.set("prediction", cache_key, cache_value, ttl=PREDICTION_LIST_TTL)

    return predictions


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get prediction by ID (cached)."""
    cache_key = f"item:{prediction_id}"
    cached = await cache_service.get("prediction", cache_key)
    if cached is not None:
        return PredictionResponse.model_validate(cached)

    result = await db.execute(
        select(Prediction).where(Prediction.id == prediction_id)
    )
    prediction = result.scalar_one_or_none()
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with ID {prediction_id} not found"
        )

    cache_value = _prediction_to_cache_dict(prediction)
    await cache_service.set("prediction", cache_key, cache_value, ttl=PREDICTION_ITEM_TTL)
    return prediction


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

    # Invalidate cache for this prediction and lists including it
    await cache_service.delete("prediction", f"item:{prediction_id}")
    await cache_service.delete_pattern("prediction", f"list:{prediction.patient_id}:*")
    await cache_service.delete_pattern("prediction", "list:all:*")

    return prediction

