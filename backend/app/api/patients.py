"""
Patient Management API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from ..db.session import get_db
from ..models.user import User
from ..models.patient import Patient
from ..models.medical_record import MedicalRecord
from ..schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from ..core.security import get_current_user, require_role
from ..core.cache import generate_cache_key, get_cached_response, set_cached_response, invalidate_patient_cache

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("nurse"))
):
    """Create a new patient (requires nurse role or higher)"""
    # Check if patient_id already exists
    result = await db.execute(
        select(Patient).where(Patient.patient_id == patient_data.patient_id)
    )
    existing_patient = result.scalar_one_or_none()
    
    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Patient with ID {patient_data.patient_id} already exists"
        )
    
    # Create new patient
    new_patient = Patient(**patient_data.model_dump())
    db.add(new_patient)
    await db.commit()
    await db.refresh(new_patient)
    
    # Invalidate cache
    await invalidate_patient_cache(new_patient.id)
    
    return new_patient


@router.get("/", response_model=List[PatientResponse])
async def get_patients(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of patients with pagination (cached for 5 minutes)"""
    # Generate cache key
    cache_key = generate_cache_key(
        "patients",
        request=request,
        current_user=current_user,
        skip=skip,
        limit=limit,
        search=search
    )
    
    # Try to get from cache
    cached_result = await get_cached_response(cache_key, expire_seconds=300)
    if cached_result is not None:
        return cached_result
    
    # Query database with eager loading to avoid N+1 queries
    query = select(Patient).options(
        selectinload(Patient.assigned_doctor)  # Load assigned doctor relationship
    )
    
    # Search filter
    if search:
        query = query.where(
            (Patient.first_name.ilike(f"%{search}%")) |
            (Patient.last_name.ilike(f"%{search}%")) |
            (Patient.patient_id.ilike(f"%{search}%"))
        )
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    patients = result.scalars().all()
    
    # Cache result
    await set_cached_response(cache_key, patients, expire_seconds=300)
    
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    request: Request,
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get patient by ID (cached for 10 minutes)"""
    # Generate cache key
    cache_key = generate_cache_key(
        "patient",
        request=request,
        current_user=current_user,
        patient_id=patient_id
    )
    
    # Try to get from cache
    cached_result = await get_cached_response(cache_key, expire_seconds=600)
    if cached_result is not None:
        return cached_result
    
    # Query database with eager loading to avoid N+1 queries
    result = await db.execute(
        select(Patient)
        .where(Patient.id == patient_id)
        .options(
            selectinload(Patient.assigned_doctor),
            selectinload(Patient.medical_records),
            selectinload(Patient.predictions)
        )
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    
    # Cache result
    await set_cached_response(cache_key, patient, expire_seconds=600)
    
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("nurse"))
):
    """Update patient information"""
    result = await db.execute(
        select(Patient).where(Patient.id == patient_id)
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    
    # Update fields
    update_data = patient_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    await db.commit()
    await db.refresh(patient)
    
    # Invalidate cache
    await invalidate_patient_cache(patient_id)
    
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Delete a patient (requires admin role)"""
    result = await db.execute(
        select(Patient).where(Patient.id == patient_id)
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    
    await db.delete(patient)
    await db.commit()
    
    # Invalidate cache
    await invalidate_patient_cache(patient_id)
    
    return None


@router.get("/{patient_id}/medical-records")
async def get_patient_medical_records(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all medical records for a patient"""
    # Verify patient exists with eager loading to avoid N+1 queries
    result = await db.execute(
        select(Patient)
        .where(Patient.id == patient_id)
        .options(
            selectinload(Patient.medical_records).selectinload(MedicalRecord.imaging_studies)
        )
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    
    # Medical records already loaded via relationship, just sort them
    from datetime import datetime
    records = sorted(
        patient.medical_records,
        key=lambda x: x.visit_date if x.visit_date else datetime.min,
        reverse=True
    )
    
    return [
        {
            "id": record.id,
            "visit_date": record.visit_date.isoformat() if record.visit_date else None,
            "visit_type": record.visit_type,
            "mmse_score": record.mmse_score,
            "moca_score": record.moca_score,
            "memory_score": record.memory_score,
            "attention_score": record.attention_score,
            "executive_function_score": record.executive_function_score,
            "amyloid_beta": record.amyloid_beta,
            "tau_protein": record.tau_protein,
            "dopamine_level": record.dopamine_level,
            "apoe_e4_status": record.apoe_e4_status,
            "hippocampal_volume": record.hippocampal_volume,
            "cortical_thickness": record.cortical_thickness,
            "ventricular_volume": record.ventricular_volume,
            "white_matter_hyperintensities": record.white_matter_hyperintensities,
            "brain_volume_total": record.brain_volume_total,
            "symptoms": record.symptoms,
            "clinical_notes": record.clinical_notes,
            "created_at": record.created_at.isoformat() if record.created_at else None,
        }
        for record in records
    ]

