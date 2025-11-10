"""
Imaging API Endpoints
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

import aiofiles

try:
    import pydicom
except ImportError:  # pragma: no cover - optional dependency guard
    pydicom = None
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.security import require_role
from ..db.session import get_db
from ..models.imaging import ImagingModality, ImagingStudy
from ..models.medical_record import MedicalRecord
from ..models.patient import Patient
from ..schemas.imaging import DicomUploadResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/imaging", tags=["Imaging"])

ALLOWED_CONTENT_TYPES = {
    "application/dicom",
    "application/dicom+xml",
    "application/octet-stream",
    "image/dicom",
}

MODALITY_MAP = {
    "MR": ImagingModality.MRI,
    "MRI": ImagingModality.MRI,
    "PT": ImagingModality.PET,
    "FMRI": ImagingModality.FMRI,
    "CT": ImagingModality.CT,
    "SPECT": ImagingModality.SPECT,
}


async def _save_upload_file(upload_file: UploadFile, destination: Path) -> int:
    """Save an UploadFile to disk asynchronously and return the total bytes written."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    total_written = 0
    chunk_size = 1024 * 1024  # 1MB

    async with aiofiles.open(destination, "wb") as out_file:
        while True:
            chunk = await upload_file.read(chunk_size)
            if not chunk:
                break
            total_written += len(chunk)
            if total_written > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE // (1024 * 1024)}MB",
                )
            await out_file.write(chunk)

    # Reset read pointer to allow further operations if needed
    await upload_file.seek(0)
    return total_written


def _parse_study_date(value: Optional[str]) -> datetime:
    """Parse study date from DICOM field or return current time as fallback."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        for fmt in ("%Y%m%d", "%Y-%m-%d", "%Y/%m/%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    return datetime.utcnow()


@router.post(
    "/dicom",
    response_model=DicomUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a DICOM study for a patient",
)
async def upload_dicom_study(
    patient_id: int = Form(..., description="Internal patient identifier"),
    medical_record_id: Optional[int] = Form(
        None, description="Optional existing medical record to attach the imaging study"
    ),
    file: UploadFile = File(..., description="DICOM file (.dcm)"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("doctor")),
):
    """Accept a DICOM file upload, store it on disk, and register an imaging study."""

    if pydicom is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DICOM processing is unavailable (missing pydicom dependency).",
        )

    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must have a filename")

    filename = Path(file.filename).name
    if not filename.lower().endswith(".dcm"):
        logger.warning("Rejected non-DICOM file upload attempt: %s", filename)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only DICOM (.dcm) files are supported")

    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        logger.warning("Unexpected content type for DICOM upload: %s", file.content_type)

    # Ensure patient exists
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient {patient_id} not found")

    # Fetch or create medical record
    medical_record: Optional[MedicalRecord] = None
    if medical_record_id:
        result = await db.execute(
            select(MedicalRecord).where(
                MedicalRecord.id == medical_record_id, MedicalRecord.patient_id == patient_id
            )
        )
        medical_record = result.scalar_one_or_none()
        if not medical_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medical record {medical_record_id} not found for patient {patient_id}",
            )
    else:
        medical_record = MedicalRecord(
            patient_id=patient_id,
            visit_date=datetime.utcnow(),
            visit_type="Imaging Upload",
        )
        db.add(medical_record)
        await db.flush()

    study_uuid = uuid4().hex
    patient_dir = Path(settings.DICOM_DIR) / f"patient_{patient_id}" / study_uuid
    patient_dir.mkdir(parents=True, exist_ok=True)
    destination = patient_dir / filename

    written_bytes = await _save_upload_file(file, destination)
    logger.info(
        "Stored DICOM file for patient %s at %s (%s bytes)",
        patient_id,
        destination,
        written_bytes,
    )

    try:
        dicom_dataset = pydicom.dcmread(str(destination))
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Failed to parse DICOM file %s: %s", destination, exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to parse DICOM file. Please upload a valid DICOM study.",
        ) from exc

    study_instance_uid = str(getattr(dicom_dataset, "StudyInstanceUID", uuid4()))
    modality_value = str(getattr(dicom_dataset, "Modality", "MR")).upper()
    modality = MODALITY_MAP.get(modality_value, ImagingModality.MRI)
    study_date = _parse_study_date(getattr(dicom_dataset, "StudyDate", None))
    image_count = int(getattr(dicom_dataset, "NumberOfFrames", 1) or 1)

    imaging_study = ImagingStudy(
        medical_record_id=medical_record.id,
        study_id=study_instance_uid,
        study_date=study_date,
        modality=modality,
        dicom_path=str(destination),
        series_count=1,
        image_count=image_count,
        study_description=str(getattr(dicom_dataset, "StudyDescription", "") or None),
        protocol_name=str(getattr(dicom_dataset, "ProtocolName", "") or None),
        processing_status="pending",
    )

    db.add(imaging_study)
    await db.commit()
    await db.refresh(imaging_study)

    metadata = {
        "patient_identifier": str(getattr(dicom_dataset, "PatientID", "") or ""),
        "study_date": study_date.isoformat(),
        "modality": modality_value,
        "study_description": imaging_study.study_description,
        "protocol_name": imaging_study.protocol_name,
        "series_count": imaging_study.series_count,
        "image_count": imaging_study.image_count,
        "study_instance_uid": study_instance_uid,
    }

    return DicomUploadResponse(
        imaging_study_id=imaging_study.id,
        study_id=imaging_study.study_id,
        medical_record_id=medical_record.id,
        dicom_path=imaging_study.dicom_path,
        metadata=metadata,
        created_at=imaging_study.created_at or datetime.utcnow(),
    )


@router.get(
    "/studies/{study_id}/preview",
    summary="Get MRI preview image for a study",
)
async def get_study_preview(
    study_id: int,
    slice_index: Optional[int] = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("doctor")),
):
    """Generate and return preview image for an imaging study"""
    from fastapi.responses import Response
    from ..services.image_processing_service import image_processing_service
    import base64
    import io
    from PIL import Image
    
    result = await db.execute(select(ImagingStudy).where(ImagingStudy.id == study_id))
    study = result.scalar_one_or_none()
    
    if not study or not study.dicom_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found or no DICOM path")
    
    try:
        # Load DICOM and generate preview
        image_array, _ = image_processing_service.load_dicom(study.dicom_path)
        normalized = image_processing_service.normalize_image(image_array)
        
        # Convert to uint8 for PIL
        preview_uint8 = (normalized * 255).astype('uint8')
        pil_image = Image.fromarray(preview_uint8)
        
        # Convert to PNG bytes
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        return Response(content=buffer.read(), media_type='image/png')
    except Exception as exc:
        logger.error(f"Error generating preview for study {study_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate preview: {str(exc)}"
        ) from exc


@router.get(
    "/studies/{study_id}/slices",
    summary="Get list of available slices for multi-slice viewing",
)
async def get_study_slices(
    study_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("doctor")),
):
    """Get metadata about available slices in a DICOM study"""
    result = await db.execute(select(ImagingStudy).where(ImagingStudy.id == study_id))
    study = result.scalar_one_or_none()
    
    if not study:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")
    
    return {
        "study_id": study.id,
        "total_slices": study.image_count or 1,
        "modality": study.modality.value,
        "study_date": study.study_date.isoformat() if study.study_date else None,
    }


@router.get(
    "/studies/{study_id}/slice/{slice_index}",
    summary="Get specific slice image",
)
async def get_study_slice(
    study_id: int,
    slice_index: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("doctor")),
):
    """Get a specific slice from a DICOM study"""
    from fastapi.responses import Response
    from ..services.image_processing_service import image_processing_service
    import io
    from PIL import Image
    
    result = await db.execute(select(ImagingStudy).where(ImagingStudy.id == study_id))
    study = result.scalar_one_or_none()
    
    if not study or not study.dicom_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")
    
    try:
        # For now, load single DICOM file
        # In production, load specific slice from series
        image_array, metadata = image_processing_service.load_dicom(study.dicom_path)
        normalized = image_processing_service.normalize_image(image_array)
        
        preview_uint8 = (normalized * 255).astype('uint8')
        pil_image = Image.fromarray(preview_uint8)
        
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        return Response(content=buffer.read(), media_type='image/png')
    except Exception as exc:
        logger.error(f"Error loading slice {slice_index} for study {study_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load slice: {str(exc)}"
        ) from exc


