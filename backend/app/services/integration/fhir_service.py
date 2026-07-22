"""
HL7 FHIR Service

Local resource builders (Patient/Observation/…) work offline.
Remote search/read require ``HL7_FHIR_ENDPOINT`` (or an explicit base URL);
otherwise operations return ``not_configured`` rather than silent stubs.
"""
from __future__ import annotations

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

import httpx
from fhir.resources.patient import Patient
from fhir.resources.observation import Observation
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.imagingstudy import ImagingStudy
from fhir.resources.bundle import Bundle, BundleEntry
from fhir.resources.resource import Resource

from .errors import IntegrationNotConfiguredError

logger = logging.getLogger(__name__)


class FHIRService:
    """Service for HL7 FHIR operations (local builders + optional remote client)."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000/fhir",
        remote_endpoint: Optional[str] = None,
        timeout_seconds: float = 30.0,
    ):
        # Public base used when building Bundle fullUrl values (local).
        self.base_url = (base_url or "").rstrip("/")
        # External FHIR server for search/read (HL7_FHIR_ENDPOINT).
        endpoint = (remote_endpoint or "").strip().rstrip("/") or None
        self.remote_endpoint = endpoint
        self.timeout_seconds = timeout_seconds

    def is_remote_configured(self) -> bool:
        return bool(self.remote_endpoint)

    def _require_remote(self, operation: str) -> str:
        if not self.remote_endpoint:
            raise IntegrationNotConfiguredError(
                f"FHIR remote '{operation}' is not configured. "
                "Set HL7_FHIR_ENDPOINT (or pass remote_endpoint) to a FHIR base URL."
            )
        return self.remote_endpoint

    def create_patient_resource(
        self,
        patient_id: str,
        name: str,
        birth_date: str,
        gender: str,
        identifiers: Optional[List[Dict]] = None,
    ) -> Patient:
        """Create a Patient Resource (local builder, no remote call)."""
        patient_data = {
            "resourceType": "Patient",
            "id": patient_id,
            "identifier": identifiers or [],
            "name": [{"use": "official", "text": name}],
            "gender": gender,
            "birthDate": birth_date,
        }
        return Patient(**patient_data)

    def create_observation_resource(
        self,
        observation_id: str,
        patient_id: str,
        code: Dict[str, Any],
        value: Any,
        effective_datetime: str,
        status: str = "final",
    ) -> Observation:
        """Create an Observation Resource (local builder)."""
        observation_data = {
            "resourceType": "Observation",
            "id": observation_id,
            "status": status,
            "subject": {"reference": f"Patient/{patient_id}"},
            "code": code,
            "effectiveDateTime": effective_datetime,
            "valueQuantity": {
                "value": value,
                "unit": code.get("text", ""),
                "system": "http://unitsofmeasure.org",
                "code": code.get("text", ""),
            },
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
        results: Optional[List[Dict]] = None,
    ) -> DiagnosticReport:
        """Create a DiagnosticReport Resource (local builder)."""
        report_data: Dict[str, Any] = {
            "resourceType": "DiagnosticReport",
            "id": report_id,
            "status": status,
            "category": category,
            "code": code,
            "subject": {"reference": f"Patient/{patient_id}"},
            "effectiveDateTime": effective_datetime,
            "issued": datetime.now().isoformat(),
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
        status: str = "available",
    ) -> ImagingStudy:
        """Create an ImagingStudy Resource (local builder)."""
        study_data = {
            "resourceType": "ImagingStudy",
            "id": study_id,
            "status": status,
            "modality": [
                {
                    "system": "http://dicom.nema.org/resources/ontology/DCM",
                    "code": modality,
                }
            ],
            "subject": {"reference": f"Patient/{patient_id}"},
            "started": started,
            "series": series,
        }
        return ImagingStudy(**study_data)

    def create_bundle(
        self,
        resources: List[Resource],
        bundle_type: str = "collection",
    ) -> Bundle:
        """Create a Bundle from FHIR resources (local builder)."""
        entries = []
        for resource in resources:
            entry = BundleEntry(
                resource=resource,
                fullUrl=f"{self.base_url}/{resource.resource_type}/{resource.id}",
            )
            entries.append(entry)

        return Bundle(
            **{
                "resourceType": "Bundle",
                "type": bundle_type,
                "entry": entries,
            }
        )

    def search_resources(
        self,
        resource_type: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Search resources on the remote FHIR server via HTTP GET.

        Raises IntegrationNotConfiguredError when HL7_FHIR_ENDPOINT is unset.
        Returns the parsed Bundle (or server JSON) on success.
        """
        base = self._require_remote(f"search {resource_type}")
        url = f"{base}/{resource_type}"
        logger.info("FHIR search %s params=%s", url, params)

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.get(
                url,
                params=params,
                headers={"Accept": "application/fhir+json"},
            )
            response.raise_for_status()
            return response.json()

    def read_resource(
        self,
        resource_type: str,
        resource_id: str,
    ) -> Dict[str, Any]:
        """
        Read a single resource from the remote FHIR server.

        Raises IntegrationNotConfiguredError when HL7_FHIR_ENDPOINT is unset.
        """
        base = self._require_remote(f"read {resource_type}/{resource_id}")
        url = f"{base}/{resource_type}/{resource_id}"
        logger.info("FHIR read %s", url)

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.get(
                url,
                headers={"Accept": "application/fhir+json"},
            )
            response.raise_for_status()
            return response.json()

    def validate_resource(self, resource: Resource) -> Dict[str, Any]:
        """Basic local validation of a FHIR resource object."""
        validation_result: Dict[str, Any] = {
            "valid": True,
            "errors": [],
            "warnings": [],
        }

        if not hasattr(resource, "resource_type"):
            validation_result["valid"] = False
            validation_result["errors"].append("Missing resourceType")

        if not hasattr(resource, "id") or not resource.id:
            validation_result["warnings"].append("Missing id field")

        return validation_result
