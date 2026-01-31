"""
EHR/HIS Integration API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from pydantic import BaseModel

from ...services.integration.ehr_service import EHRService
from ...core.security import get_current_user
from ...core.config import settings
from ...models.user import User

router = APIRouter(prefix="/ehr", tags=["EHR"])

# Initialize EHR service
ehr_service = EHRService(
    ehr_api_url=settings.EHR_API_URL,
    api_key=getattr(settings, 'EHR_API_KEY', None)
)


class PredictionResult(BaseModel):
    """Prediction result to send to EHR"""
    disease_type: str
    risk_level: str
    risk_score: float
    confidence: float
    recommendations: list


@router.get("/patients/{patient_id}")
async def get_patient_from_ehr(
    patient_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    دریافت اطلاعات بیمار از EHR
    
    Parameters:
        patient_id: شناسه بیمار در EHR
    
    Returns:
        اطلاعات بیمار
    """
    try:
        patient_data = await ehr_service.get_patient_data(patient_id)
        
        if not patient_data:
            raise HTTPException(
                status_code=404,
                detail="Patient not found in EHR"
            )
        
        return {
            "status": "success",
            "patient": patient_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching patient from EHR: {str(e)}"
        )


@router.get("/patients/{patient_id}/lab-results")
async def get_lab_results(
    patient_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """
    دریافت نتایج آزمایش‌های بیمار از EHR
    
    Parameters:
        patient_id: شناسه بیمار
        start_date: تاریخ شروع (YYYY-MM-DD)
        end_date: تاریخ پایان (YYYY-MM-DD)
    
    Returns:
        لیست نتایج آزمایش
    """
    try:
        lab_results = await ehr_service.get_patient_lab_results(
            patient_id=patient_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "status": "success",
            "count": len(lab_results),
            "lab_results": lab_results
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching lab results: {str(e)}"
        )


@router.get("/patients/{patient_id}/medications")
async def get_medications(
    patient_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    دریافت داروهای بیمار از EHR
    
    Parameters:
        patient_id: شناسه بیمار
    
    Returns:
        لیست داروها
    """
    try:
        medications = await ehr_service.get_patient_medications(patient_id)
        
        return {
            "status": "success",
            "count": len(medications),
            "medications": medications
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching medications: {str(e)}"
        )


@router.get("/patients/{patient_id}/vital-signs")
async def get_vital_signs(
    patient_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """
    دریافت علائم حیاتی بیمار از EHR
    
    Parameters:
        patient_id: شناسه بیمار
        start_date: تاریخ شروع
        end_date: تاریخ پایان
    
    Returns:
        لیست علائم حیاتی
    """
    try:
        vital_signs = await ehr_service.get_patient_vital_signs(
            patient_id=patient_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "status": "success",
            "count": len(vital_signs),
            "vital_signs": vital_signs
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching vital signs: {str(e)}"
        )


@router.post("/patients/{patient_id}/sync")
async def sync_patient_data(
    patient_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    همگام‌سازی کامل اطلاعات بیمار از EHR
    
    Parameters:
        patient_id: شناسه بیمار
    
    Returns:
        اطلاعات همگام‌سازی شده
    """
    try:
        sync_result = await ehr_service.sync_patient_data(patient_id)
        
        if not sync_result["success"]:
            raise HTTPException(
                status_code=500,
                detail="Failed to sync patient data"
            )
        
        return sync_result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error syncing patient data: {str(e)}"
        )


@router.post("/patients/{patient_id}/predictions")
async def send_prediction_to_ehr(
    patient_id: str,
    prediction: PredictionResult,
    current_user: User = Depends(get_current_user)
):
    """
    ارسال نتیجه پیش‌بینی به EHR
    
    Parameters:
        patient_id: شناسه بیمار
        prediction: نتیجه پیش‌بینی
    
    Returns:
        نتیجه ارسال
    """
    try:
        prediction_result = {
            "disease_type": prediction.disease_type,
            "risk_level": prediction.risk_level,
            "risk_score": prediction.risk_score,
            "confidence": prediction.confidence,
            "recommendations": prediction.recommendations
        }
        
        success = await ehr_service.send_prediction_result(
            patient_id=patient_id,
            prediction_result=prediction_result
        )
        
        if success:
            return {
                "status": "success",
                "message": "Prediction sent to EHR successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to send prediction to EHR"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending prediction to EHR: {str(e)}"
        )

