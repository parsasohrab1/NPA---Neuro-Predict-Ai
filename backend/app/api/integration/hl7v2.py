"""
HL7 v2 Integration API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from ...services.integration.hl7v2_service import HL7v2Service, HL7v2Message
from ...core.security import get_current_user
from ...core.config import settings
from ...models.user import User

router = APIRouter(prefix="/hl7v2", tags=["HL7 v2"])

# Initialize HL7 v2 service
hl7v2_service = HL7v2Service(hl7_server_url=getattr(settings, 'HL7_SERVER_URL', None))


class AdmitPatientRequest(BaseModel):
    """Admit patient request"""
    patient_id: str
    patient_name: str
    birth_date: str
    gender: str
    admission_date: str
    admitting_doctor: str


class ObservationRequest(BaseModel):
    """Observation request"""
    patient_id: str
    observation_id: str
    observation_code: str
    observation_value: str
    observation_units: str
    observation_date: str
    status: str = "F"


class LabResultRequest(BaseModel):
    """Lab result request"""
    patient_id: str
    test_code: str
    test_name: str
    result_value: str
    units: str
    reference_range: str
    result_status: str = "F"


class VitalSignsRequest(BaseModel):
    """Vital signs request"""
    patient_id: str
    vital_signs: Dict[str, Any]


class SendMessageRequest(BaseModel):
    """Send message request"""
    message: str
    destination: Optional[str] = None


@router.post("/admit")
async def create_admit_message(
    request: AdmitPatientRequest,
    current_user: User = Depends(get_current_user)
):
    """
    ایجاد ADT^A01 (Admit Patient) message
    
    Returns:
        HL7 v2 message string
    """
    try:
        message = hl7v2_service.create_admit_message(
            patient_id=request.patient_id,
            patient_name=request.patient_name,
            birth_date=request.birth_date,
            gender=request.gender,
            admission_date=request.admission_date,
            admitting_doctor=request.admitting_doctor
        )
        
        # Validate message
        is_valid, errors = message.validate()
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={"message": "Invalid HL7 v2 message", "errors": errors}
            )
        
        return {
            "status": "success",
            "message": message.to_string(),
            "message_type": "ADT^A01"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating admit message: {str(e)}"
        )


@router.post("/observation")
async def create_observation_message(
    request: ObservationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    ایجاد ORU^R01 (Observation Result) message
    
    Returns:
        HL7 v2 message string
    """
    try:
        message = hl7v2_service.create_observation_message(
            patient_id=request.patient_id,
            observation_id=request.observation_id,
            observation_code=request.observation_code,
            observation_value=request.observation_value,
            observation_units=request.observation_units,
            observation_date=request.observation_date,
            status=request.status
        )
        
        is_valid, errors = message.validate()
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={"message": "Invalid HL7 v2 message", "errors": errors}
            )
        
        return {
            "status": "success",
            "message": message.to_string(),
            "message_type": "ORU^R01"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating observation message: {str(e)}"
        )


@router.post("/lab-result")
async def create_lab_result_message(
    request: LabResultRequest,
    current_user: User = Depends(get_current_user)
):
    """
    ایجاد ORU^R01 message برای نتایج آزمایش
    
    Returns:
        HL7 v2 message string
    """
    try:
        message = hl7v2_service.create_lab_result_message(
            patient_id=request.patient_id,
            test_code=request.test_code,
            test_name=request.test_name,
            result_value=request.result_value,
            units=request.units,
            reference_range=request.reference_range,
            result_status=request.result_status
        )
        
        is_valid, errors = message.validate()
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={"message": "Invalid HL7 v2 message", "errors": errors}
            )
        
        return {
            "status": "success",
            "message": message.to_string(),
            "message_type": "ORU^R01"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating lab result message: {str(e)}"
        )


@router.post("/vital-signs")
async def create_vital_signs_message(
    request: VitalSignsRequest,
    current_user: User = Depends(get_current_user)
):
    """
    ایجاد ORU^R01 message برای علائم حیاتی
    
    Returns:
        HL7 v2 message string
    """
    try:
        message = hl7v2_service.create_vital_signs_message(
            patient_id=request.patient_id,
            vital_signs=request.vital_signs
        )
        
        is_valid, errors = message.validate()
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={"message": "Invalid HL7 v2 message", "errors": errors}
            )
        
        return {
            "status": "success",
            "message": message.to_string(),
            "message_type": "ORU^R01"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating vital signs message: {str(e)}"
        )


@router.post("/parse")
async def parse_message(
    message: str = Body(..., description="HL7 v2 message string"),
    current_user: User = Depends(get_current_user)
):
    """
    Parse HL7 v2 message
    
    Returns:
        Parsed message structure
    """
    try:
        hl7_message = hl7v2_service.parse_message(message)
        
        is_valid, errors = hl7_message.validate()
        
        # Extract information
        patient_info = hl7v2_service.extract_patient_info(hl7_message)
        observations = hl7v2_service.extract_observations(hl7_message)
        
        return {
            "status": "success",
            "valid": is_valid,
            "errors": errors if not is_valid else [],
            "segments": [
                {
                    "type": seg["type"],
                    "fields": [f["value"] for f in seg["fields"]]
                }
                for seg in hl7_message.segments
            ],
            "patient_info": patient_info,
            "observations": observations
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing HL7 v2 message: {str(e)}"
        )


@router.post("/send")
async def send_message(
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user)
):
    """
    ارسال HL7 v2 message به destination
    
    Returns:
        نتیجه ارسال
    """
    try:
        message = hl7v2_service.parse_message(request.message)
        
        is_valid, errors = message.validate()
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={"message": "Invalid HL7 v2 message", "errors": errors}
            )
        
        success = hl7v2_service.send_message(
            message=message,
            destination=request.destination
        )
        
        if success:
            return {
                "status": "success",
                "message": "HL7 v2 message sent successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to send HL7 v2 message"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending HL7 v2 message: {str(e)}"
        )


@router.post("/validate")
async def validate_message(
    message: str = Body(..., description="HL7 v2 message string"),
    current_user: User = Depends(get_current_user)
):
    """
    اعتبارسنجی HL7 v2 message
    
    Returns:
        نتیجه اعتبارسنجی
    """
    try:
        hl7_message = hl7v2_service.parse_message(message)
        is_valid, errors = hl7_message.validate()
        
        return {
            "status": "success",
            "valid": is_valid,
            "errors": errors,
            "segments_count": len(hl7_message.segments),
            "segment_types": [seg["type"] for seg in hl7_message.segments]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error validating HL7 v2 message: {str(e)}"
        )

