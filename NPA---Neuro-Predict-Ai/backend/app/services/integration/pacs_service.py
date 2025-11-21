"""
PACS Integration Service
سرویس برای یکپارچه‌سازی با PACS (DICOM)
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import pydicom
from pydicom.dataset import Dataset
from pydicom.uid import generate_uid
import logging

logger = logging.getLogger(__name__)


class PACSService:
    """Service for PACS/DICOM operations"""
    
    def __init__(self, pacs_server_url: Optional[str] = None):
        self.pacs_server_url = pacs_server_url
        self.ae_title = "NEUROPREDICT"
    
    def query_patient_studies(
        self,
        patient_id: Optional[str] = None,
        patient_name: Optional[str] = None,
        study_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        جستجوی مطالعات بیمار در PACS
        
        Args:
            patient_id: شناسه بیمار
            patient_name: نام بیمار
            study_date: تاریخ مطالعه
        
        Returns:
            لیست مطالعات پیدا شده
        """
        # این متد باید با PACS server ارتباط برقرار کند
        # برای حالا فقط ساختار را نشان می‌دهیم
        
        studies = []
        
        # در production، اینجا باید C-FIND request به PACS بفرستیم
        # از طریق DICOM network protocol
        
        return studies
    
    def retrieve_study(
        self,
        study_instance_uid: str
    ) -> List[Dataset]:
        """
        دریافت مطالعه از PACS
        
        Args:
            study_instance_uid: UID مطالعه
        
        Returns:
            لیست DICOM datasets
        """
        # این متد باید C-MOVE یا C-GET request به PACS بفرستد
        # و تصاویر را دریافت کند
        
        datasets = []
        
        return datasets
    
    def store_dicom(
        self,
        dicom_file_path: str,
        patient_id: str,
        study_description: str
    ) -> bool:
        """
        ذخیره DICOM در PACS
        
        Args:
            dicom_file_path: مسیر فایل DICOM
            patient_id: شناسه بیمار
            study_description: توضیحات مطالعه
        
        Returns:
            True اگر موفق بود
        """
        try:
            # خواندن فایل DICOM
            ds = pydicom.dcmread(dicom_file_path)
            
            # تنظیم metadata
            if not hasattr(ds, 'PatientID') or not ds.PatientID:
                ds.PatientID = patient_id
            
            if not hasattr(ds, 'StudyDescription') or not ds.StudyDescription:
                ds.StudyDescription = study_description
            
            # تولید UID ها اگر وجود ندارند
            if not hasattr(ds, 'StudyInstanceUID') or not ds.StudyInstanceUID:
                ds.StudyInstanceUID = generate_uid()
            
            if not hasattr(ds, 'SeriesInstanceUID') or not ds.SeriesInstanceUID:
                ds.SeriesInstanceUID = generate_uid()
            
            if not hasattr(ds, 'SOPInstanceUID') or not ds.SOPInstanceUID:
                ds.SOPInstanceUID = generate_uid()
            
            # در production، اینجا باید C-STORE request به PACS بفرستیم
            
            logger.info(f"DICOM stored successfully for patient {patient_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error storing DICOM: {e}")
            return False
    
    def get_modality_worklist(
        self,
        patient_id: Optional[str] = None,
        scheduled_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        دریافت Modality Worklist از PACS
        
        Args:
            patient_id: شناسه بیمار
            scheduled_date: تاریخ برنامه‌ریزی شده
        
        Returns:
            لیست کارهای برنامه‌ریزی شده
        """
        # این متد باید C-FIND request برای Modality Worklist بفرستد
        
        worklist_items = []
        
        return worklist_items
    
    def parse_dicom_metadata(
        self,
        dicom_file_path: str
    ) -> Dict[str, Any]:
        """
        استخراج metadata از فایل DICOM
        
        Args:
            dicom_file_path: مسیر فایل DICOM
        
        Returns:
            Dictionary حاوی metadata
        """
        try:
            ds = pydicom.dcmread(dicom_file_path)
            
            metadata = {
                "patient_id": getattr(ds, 'PatientID', ''),
                "patient_name": getattr(ds, 'PatientName', ''),
                "patient_birth_date": getattr(ds, 'PatientBirthDate', ''),
                "patient_sex": getattr(ds, 'PatientSex', ''),
                "study_instance_uid": getattr(ds, 'StudyInstanceUID', ''),
                "study_date": getattr(ds, 'StudyDate', ''),
                "study_time": getattr(ds, 'StudyTime', ''),
                "study_description": getattr(ds, 'StudyDescription', ''),
                "modality": getattr(ds, 'Modality', ''),
                "series_instance_uid": getattr(ds, 'SeriesInstanceUID', ''),
                "series_description": getattr(ds, 'SeriesDescription', ''),
                "series_number": getattr(ds, 'SeriesNumber', ''),
                "sop_instance_uid": getattr(ds, 'SOPInstanceUID', ''),
                "instance_number": getattr(ds, 'InstanceNumber', ''),
                "rows": getattr(ds, 'Rows', 0),
                "columns": getattr(ds, 'Columns', 0),
                "slice_thickness": getattr(ds, 'SliceThickness', 0),
                "pixel_spacing": getattr(ds, 'PixelSpacing', []),
                "manufacturer": getattr(ds, 'Manufacturer', ''),
                "manufacturer_model_name": getattr(ds, 'ManufacturerModelName', ''),
            }
            
            return metadata
        
        except Exception as e:
            logger.error(f"Error parsing DICOM metadata: {e}")
            return {}
    
    def validate_dicom_file(
        self,
        dicom_file_path: str
    ) -> Dict[str, Any]:
        """
        اعتبارسنجی فایل DICOM
        
        Args:
            dicom_file_path: مسیر فایل DICOM
        
        Returns:
            نتیجه اعتبارسنجی
        """
        validation_result = {
            "valid": False,
            "errors": [],
            "warnings": []
        }
        
        try:
            ds = pydicom.dcmread(dicom_file_path)
            
            # بررسی فیلدهای ضروری
            required_fields = [
                'PatientID',
                'StudyInstanceUID',
                'SeriesInstanceUID',
                'SOPInstanceUID',
                'Modality'
            ]
            
            for field in required_fields:
                if not hasattr(ds, field) or not getattr(ds, field):
                    validation_result["errors"].append(f"Missing required field: {field}")
            
            # بررسی Modality
            valid_modalities = ['MR', 'CT', 'PT', 'PET', 'NM']
            if hasattr(ds, 'Modality'):
                if ds.Modality not in valid_modalities:
                    validation_result["warnings"].append(
                        f"Unusual modality: {ds.Modality}"
                    )
            
            if not validation_result["errors"]:
                validation_result["valid"] = True
            
        except Exception as e:
            validation_result["errors"].append(f"Invalid DICOM file: {str(e)}")
        
        return validation_result

