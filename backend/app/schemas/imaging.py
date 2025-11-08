"""
Imaging Schemas
"""
from typing import Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel

from ..models.imaging import ImagingModality


class ImagingStudySummary(BaseModel):
    id: int
    study_id: str
    medical_record_id: int
    study_date: datetime
    modality: ImagingModality
    dicom_path: str
    series_count: int
    image_count: int
    study_description: Optional[str] = None
    protocol_name: Optional[str] = None

    class Config:
        from_attributes = True


class DicomUploadResponse(BaseModel):
    imaging_study_id: int
    study_id: str
    medical_record_id: int
    dicom_path: str
    metadata: Dict[str, Any]
    created_at: datetime


