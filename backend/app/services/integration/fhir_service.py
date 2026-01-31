"""
HL7 FHIR Service
سرویس برای مدیریت منابع FHIR
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
from fhir.resources.patient import Patient
from fhir.resources.observation import Observation
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.imagingstudy import ImagingStudy
from fhir.resources.bundle import Bundle, BundleEntry
from fhir.resources.resource import Resource


class FHIRService:
    """Service for HL7 FHIR operations"""
    
    def __init__(self, base_url: str = "http://localhost:8000/fhir"):
        self.base_url = base_url
    
    def create_patient_resource(
        self,
        patient_id: str,
        name: str,
        birth_date: str,
        gender: str,
        identifiers: Optional[List[Dict]] = None
    ) -> Patient:
        """
        ایجاد Patient Resource از FHIR
        
        Args:
            patient_id: شناسه بیمار
            name: نام بیمار
            birth_date: تاریخ تولد (YYYY-MM-DD)
            gender: جنسیت (male, female, other, unknown)
            identifiers: لیست شناسه‌های اضافی
        
        Returns:
            Patient resource
        """
        patient_data = {
            "resourceType": "Patient",
            "id": patient_id,
            "identifier": identifiers or [],
            "name": [
                {
                    "use": "official",
                    "text": name
                }
            ],
            "gender": gender,
            "birthDate": birth_date
        }
        
        return Patient(**patient_data)
    
    def create_observation_resource(
        self,
        observation_id: str,
        patient_id: str,
        code: Dict[str, Any],
        value: Any,
        effective_datetime: str,
        status: str = "final"
    ) -> Observation:
        """
        ایجاد Observation Resource از FHIR
        
        Args:
            observation_id: شناسه observation
            patient_id: شناسه بیمار
            code: کد observation (CodeableConcept)
            value: مقدار observation
            effective_datetime: زمان انجام observation
            status: وضعیت (preliminary, final, amended, etc.)
        
        Returns:
            Observation resource
        """
        observation_data = {
            "resourceType": "Observation",
            "id": observation_id,
            "status": status,
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "code": code,
            "effectiveDateTime": effective_datetime,
            "valueQuantity": {
                "value": value,
                "unit": code.get("text", ""),
                "system": "http://unitsofmeasure.org",
                "code": code.get("text", "")
            }
        }
        
        return Observation(**observation_data)
    
    def create_diagnostic_report_resource(
        self,
        report_id: str,
        patient_id: str,
        status: str,
        category: List[Dict],
        code: Dict[str, Any],
        effective_datetime: str,
        conclusion: Optional[str] = None,
        results: Optional[List[Dict]] = None
    ) -> DiagnosticReport:
        """
        ایجاد DiagnosticReport Resource از FHIR
        
        Args:
            report_id: شناسه گزارش
            patient_id: شناسه بیمار
            status: وضعیت گزارش
            category: دسته‌بندی گزارش
            code: کد گزارش
            effective_datetime: زمان گزارش
            conclusion: نتیجه‌گیری
            results: نتایج آزمایش
        
        Returns:
            DiagnosticReport resource
        """
        report_data = {
            "resourceType": "DiagnosticReport",
            "id": report_id,
            "status": status,
            "category": category,
            "code": code,
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": effective_datetime,
            "issued": datetime.now().isoformat()
        }
        
        if conclusion:
            report_data["conclusion"] = conclusion
        
        if results:
            report_data["result"] = results
        
        return DiagnosticReport(**report_data)
    
    def create_imaging_study_resource(
        self,
        study_id: str,
        patient_id: str,
        modality: str,
        started: str,
        series: List[Dict],
        status: str = "available"
    ) -> ImagingStudy:
        """
        ایجاد ImagingStudy Resource از FHIR
        
        Args:
            study_id: شناسه مطالعه
            patient_id: شناسه بیمار
            modality: نوع تصویربرداری (CT, MR, PET, etc.)
            started: زمان شروع
            series: لیست سری‌های تصویر
            status: وضعیت (registered, available, cancelled, etc.)
        
        Returns:
            ImagingStudy resource
        """
        study_data = {
            "resourceType": "ImagingStudy",
            "id": study_id,
            "status": status,
            "modality": [
                {
                    "system": "http://dicom.nema.org/resources/ontology/DCM",
                    "code": modality
                }
            ],
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "started": started,
            "series": series
        }
        
        return ImagingStudy(**study_data)
    
    def create_bundle(
        self,
        resources: List[Resource],
        bundle_type: str = "collection"
    ) -> Bundle:
        """
        ایجاد Bundle از منابع FHIR
        
        Args:
            resources: لیست منابع FHIR
            bundle_type: نوع bundle (document, message, transaction, etc.)
        
        Returns:
            Bundle resource
        """
        entries = []
        for resource in resources:
            entry = BundleEntry(
                resource=resource,
                fullUrl=f"{self.base_url}/{resource.resource_type}/{resource.id}"
            )
            entries.append(entry)
        
        bundle_data = {
            "resourceType": "Bundle",
            "type": bundle_type,
            "entry": entries
        }
        
        return Bundle(**bundle_data)
    
    def search_resources(
        self,
        resource_type: str,
        params: Dict[str, Any]
    ) -> Bundle:
        """
        جستجوی منابع FHIR
        
        Args:
            resource_type: نوع منبع (Patient, Observation, etc.)
            params: پارامترهای جستجو
        
        Returns:
            Bundle حاوی نتایج جستجو
        """
        # این متد باید با FHIR server ارتباط برقرار کند
        # در اینجا فقط ساختار را نشان می‌دهیم
        pass
    
    def validate_resource(self, resource: Resource) -> Dict[str, Any]:
        """
        اعتبارسنجی منبع FHIR
        
        Args:
            resource: منبع FHIR برای اعتبارسنجی
        
        Returns:
            نتیجه اعتبارسنجی
        """
        # اعتبارسنجی اولیه
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # بررسی resourceType
        if not hasattr(resource, 'resource_type'):
            validation_result["valid"] = False
            validation_result["errors"].append("Missing resourceType")
        
        # بررسی id
        if not hasattr(resource, 'id') or not resource.id:
            validation_result["warnings"].append("Missing id field")
        
        return validation_result

