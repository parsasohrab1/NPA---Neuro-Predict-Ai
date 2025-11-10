"""
Integration API Endpoints - PACS/EHR/HL7/FHIR
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from ..db.session import get_db
from ..core.security import require_role, get_current_user
from ..models.user import User
from ..services.integration_service import (
    IntegrationService,
    HL7Message,
    FHIRResource
)

router = APIRouter(prefix="/integration", tags=["Integration"])


# Schemas
class HL7MessageRequest(BaseModel):
    message_type: str
    message_control_id: str
    sending_application: str
    sending_facility: str
    receiving_application: str
    receiving_facility: str
    data: Dict[str, Any]


class FHIRResourceRequest(BaseModel):
    resource_type: str
    id: Optional[str] = None
    data: Dict[str, Any]


class SyncPatientRequest(BaseModel):
    patient_id: str


class SyncImagingRequest(BaseModel):
    study_instance_uid: str


# HL7 Endpoints
@router.post("/hl7/send")
async def send_hl7_message(
    request: HL7MessageRequest,
    current_user: User = Depends(require_role("admin"))
) -> Dict[str, Any]:
    """Send HL7 message to external system"""
    from datetime import datetime
    
    message = HL7Message(
        message_type=request.message_type,
        message_control_id=request.message_control_id,
        sending_application=request.sending_application,
        sending_facility=request.sending_facility,
        receiving_application=request.receiving_application,
        receiving_facility=request.receiving_facility,
        message_datetime=datetime.utcnow(),
        data=request.data
    )
    
    result = await IntegrationService.send_hl7_message(message)
    return result


# FHIR Endpoints
@router.post("/fhir/send")
async def send_fhir_resource(
    request: FHIRResourceRequest,
    current_user: User = Depends(require_role("admin"))
) -> Dict[str, Any]:
    """Send FHIR resource to external system"""
    resource = FHIRResource(
        resource_type=request.resource_type,
        id=request.id,
        data=request.data
    )
    
    result = await IntegrationService.send_fhir_resource(resource)
    return result


@router.get("/fhir/{resource_type}/{resource_id}")
async def get_fhir_resource(
    resource_type: str,
    resource_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get FHIR resource from external system"""
    resource = await IntegrationService.get_fhir_resource(resource_type, resource_id)
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    return resource


@router.get("/fhir/{resource_type}")
async def query_fhir_resources(
    resource_type: str,
    search_params: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Query FHIR resources"""
    resources = await IntegrationService.query_fhir_resources(resource_type, search_params)
    return resources


# PACS Integration
@router.post("/pacs/fetch")
async def fetch_pacs_study(
    request: SyncImagingRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Fetch study from PACS system"""
    result = await IntegrationService.fetch_pacs_study(request.study_instance_uid)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study not found in PACS system"
        )
    
    return result


@router.post("/pacs/sync")
async def sync_imaging_from_pacs(
    request: SyncImagingRequest,
    current_user: User = Depends(require_role("admin"))
) -> Dict[str, Any]:
    """Sync imaging study from PACS system"""
    result = await IntegrationService.sync_imaging_from_pacs(request.study_instance_uid)
    return result


# EHR Integration
@router.post("/ehr/fetch")
async def fetch_ehr_patient(
    request: SyncPatientRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Fetch patient data from EHR system"""
    result = await IntegrationService.fetch_ehr_patient(request.patient_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found in EHR system"
        )
    
    return result


@router.post("/ehr/sync")
async def sync_patient_from_ehr(
    request: SyncPatientRequest,
    current_user: User = Depends(require_role("admin"))
) -> Dict[str, Any]:
    """Sync patient data from EHR system"""
    result = await IntegrationService.sync_patient_from_ehr(request.patient_id)
    return result

