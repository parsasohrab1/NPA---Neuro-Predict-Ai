"""
PATENT-PENDING: Data Fusion Report API Endpoints
Multi-Modal Medical Data Fusion and Interpretation
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
import torch

from ..db.session import get_db
from ..models.user import User
from ..models.patient import Patient
from ..models.medical_record import MedicalRecord
from ..models.data_fusion_report import DataFusionReport
from ..schemas.data_fusion import (
    DataFusionReportResponse,
    DataFusionReportCreate
)
from ..services.data_fusion_service import DataFusionService
from ..services.data_fusion_xai_service import get_data_fusion_xai_service
from ..services.data_fusion_model_service import get_data_fusion_model_service
from ..core.security import get_current_user

router = APIRouter(prefix="/data-fusion", tags=["Data Fusion Reports"])


@router.post("/generate", response_model=DataFusionReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_fusion_report(
    request: DataFusionReportCreate,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Disabled for development
):
    """
    PATENT-PENDING: Generate Multi-Modal Data Fusion Report
    
    This endpoint implements our proprietary data fusion algorithm that:
    - Integrates cognitive, biomarker, and imaging data
    - Performs cross-modal correlation analysis
    - Detects conflicting findings
    - Generates confidence-weighted interpretation
    - Produces automated clinical report
    
    This represents our key innovation for patent filing.
    """
    patient_id = request.patient_id
    medical_record_id = request.medical_record_id
    
    # If no medical_record_id provided, use latest
    if not medical_record_id:
        result = await db.execute(
            select(MedicalRecord)
            .where(MedicalRecord.patient_id == patient_id)
            .order_by(desc(MedicalRecord.visit_date))
            .limit(1)
        )
        latest_record = result.scalar_one_or_none()
        if not latest_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No medical records found for patient {patient_id}"
            )
        medical_record_id = latest_record.id
    
    # Generate fusion report using our patent-pending algorithm
    fusion_report = await DataFusionService.generate_fusion_report(
        patient_id=patient_id,
        medical_record_id=medical_record_id,
        db=db
    )
    
    db.add(fusion_report)
    await db.commit()
    await db.refresh(fusion_report)
    
    return fusion_report.to_dict()


@router.get("/patient/{patient_id}", response_model=List[DataFusionReportResponse])
async def get_patient_fusion_reports(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Disabled for development
):
    """Get all fusion reports for a specific patient"""
    result = await db.execute(
        select(DataFusionReport)
        .where(DataFusionReport.patient_id == patient_id)
        .order_by(desc(DataFusionReport.generated_at))
    )
    reports = result.scalars().all()
    
    return [report.to_dict() for report in reports]


@router.get("/{report_id}", response_model=DataFusionReportResponse)
async def get_fusion_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Disabled for development
):
    """Get a specific fusion report by ID"""
    result = await db.execute(
        select(DataFusionReport).where(DataFusionReport.id == report_id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fusion report {report_id} not found"
        )
    
    return report.to_dict()


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fusion_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(require_role("admin"))  # Disabled for development
):
    """Delete a fusion report"""
    result = await db.execute(
        select(DataFusionReport).where(DataFusionReport.id == report_id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fusion report {report_id} not found"
        )
    
    await db.delete(report)
    await db.commit()
    
    return None


@router.post("/batch-generate", status_code=status.HTTP_201_CREATED)
async def batch_generate_fusion_reports(
    patient_ids: List[int],
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(require_role("doctor"))  # Disabled for development
):
    """
    Batch generate fusion reports for multiple patients
    Useful for generating reports for all 100k patients
    """
    generated = []
    errors = []
    
    for patient_id in patient_ids:
        try:
            # Get latest medical record
            result = await db.execute(
                select(MedicalRecord)
                .where(MedicalRecord.patient_id == patient_id)
                .order_by(desc(MedicalRecord.visit_date))
                .limit(1)
            )
            record = result.scalar_one_or_none()
            
            if not record:
                errors.append(f"Patient {patient_id}: No medical records")
                continue
            
            # Generate fusion report
            fusion_report = await DataFusionService.generate_fusion_report(
                patient_id=patient_id,
                medical_record_id=record.id,
                db=db
            )
            
            db.add(fusion_report)
            generated.append({
                'patient_id': patient_id,
                'report_id': None,  # Will be set after commit
                'fusion_score': fusion_report.integrated_fusion_score
            })
            
        except Exception as e:
            errors.append(f"Patient {patient_id}: {str(e)}")
    
    await db.commit()
    
    return {
        'generated': len(generated),
        'errors': len(errors),
        'generated_reports': generated,
        'error_details': errors[:10]  # First 10 errors
    }


@router.post("/{report_id}/explain", status_code=status.HTTP_200_OK)
async def explain_fusion_report(
    report_id: int,
    method: str = "integrated_gradients",
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Disabled for development
):
    """
    PATENT CLAIM 3: Generate dynamic evidence and explanations for a fusion report
    
    This endpoint implements Patent Claim 3 by providing:
    (a) Computing model gradients with respect to input
    (b) Using Integrated Gradients for accurate attribution
    (c) Mapping attributions to anatomical brain regions
    (d) Visual display data for saliency maps
    
    Args:
        report_id: ID of the fusion report to explain
        method: XAI method to use ('integrated_gradients' or 'gradient_saliency')
    
    Returns:
        Comprehensive dynamic evidence supporting Patent Claim 3
    """
    # Get fusion report
    result = await db.execute(
        select(DataFusionReport).where(DataFusionReport.id == report_id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fusion report {report_id} not found"
        )
    
    # Get patient and medical record
    patient_result = await db.execute(
        select(Patient).where(Patient.id == report.patient_id)
    )
    patient = patient_result.scalar_one_or_none()
    
    record_result = await db.execute(
        select(MedicalRecord).where(MedicalRecord.id == report.medical_record_id)
    )
    medical_record = record_result.scalar_one_or_none()
    
    if not patient or not medical_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient or medical record not found"
        )
    
    # Get model service and XAI service
    model_service = get_data_fusion_model_service()
    
    if not model_service.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Deep Learning model not available. XAI requires trained model."
        )
    
    xai_service = get_data_fusion_xai_service(model_service.model)
    
    # Prepare fusion scores
    fusion_scores = {
        'cognitive_score': report.cognitive_modality_score,
        'biomarker_score': report.biomarker_modality_score,
        'imaging_score': report.imaging_modality_score,
        'integrated_fusion_score': report.integrated_fusion_score,
        'alzheimer_fusion_score': report.alzheimer_fusion_score,
        'parkinson_fusion_score': report.parkinson_fusion_score,
        'fusion_confidence': float(report.fusion_confidence.value) if hasattr(report.fusion_confidence, 'value') else 0.5
    }
    
    # Generate dynamic evidence (PATENT CLAIM 3)
    evidence = xai_service.generate_dynamic_evidence(
        medical_record=medical_record,
        patient=patient,
        fusion_scores=fusion_scores,
        method=method
    )
    
    return evidence


@router.get("/{report_id}/saliency-map", status_code=status.HTTP_200_OK)
async def get_saliency_map(
    report_id: int,
    target_output: str = "integrated_fusion_score",
    method: str = "integrated_gradients",
    db: AsyncSession = Depends(get_db),
):
    """
    PATENT CLAIM 3(d): Get visual saliency map data
    
    Returns saliency map data for visualization, supporting Patent Claim 3(d)
    which requires visual display of saliency maps for medical interpretation.
    
    Args:
        report_id: ID of the fusion report
        target_output: Which output to explain
        method: XAI method to use
    
    Returns:
        Saliency map data for visualization
    """
    # Get fusion report
    result = await db.execute(
        select(DataFusionReport).where(DataFusionReport.id == report_id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fusion report {report_id} not found"
        )
    
    # Get patient and medical record
    patient_result = await db.execute(
        select(Patient).where(Patient.id == report.patient_id)
    )
    patient = patient_result.scalar_one_or_none()
    
    record_result = await db.execute(
        select(MedicalRecord).where(MedicalRecord.id == report.medical_record_id)
    )
    medical_record = record_result.scalar_one_or_none()
    
    if not patient or not medical_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient or medical record not found"
        )
    
    # Get model service
    model_service = get_data_fusion_model_service()
    
    if not model_service.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Deep Learning model not available"
        )
    
    xai_service = get_data_fusion_xai_service(model_service.model)
    
    # Extract features
    from ..services.data_fusion_service import DataFusionService
    features = DataFusionService._extract_features_for_model(medical_record, patient)
    features_tensor = torch.FloatTensor(features).unsqueeze(0)
    
    # Compute saliency map
    if method == "integrated_gradients":
        result = xai_service.compute_integrated_gradients(
            features_tensor,
            target_output=target_output
        )
    else:
        result = xai_service.compute_gradient_saliency(
            features_tensor,
            target_output=target_output
        )
    
    # Get visual saliency data
    attributions = result.get('attribution') or result.get('saliency')
    visual_data = xai_service._prepare_visual_saliency_data(attributions)
    
    return {
        'report_id': report_id,
        'target_output': target_output,
        'method': method,
        'saliency_data': visual_data,
        'anatomical_regions': xai_service.map_to_anatomical_regions(attributions),
        'patent_claim_3_support': True
    }


