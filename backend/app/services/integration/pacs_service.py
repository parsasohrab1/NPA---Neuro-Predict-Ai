"""
PACS Integration Service

Local DICOM parse/validate work without a remote PACS.
DIMSE network operations (C-FIND / C-MOVE / C-GET / C-STORE / MWL) require:
  - ``PACS_SERVER_URL`` (or host/AE configuration), and
  - the optional ``pynetdicom`` package for DICOM network protocol.

Until both are present, remote operations raise ``IntegrationNotConfiguredError``
instead of returning empty success lists that look "green".
"""
from __future__ import annotations

from typing import Optional, List, Dict, Any
import logging

import pydicom
from pydicom.dataset import Dataset
from pydicom.uid import generate_uid

from .errors import IntegrationNotConfiguredError, IntegrationNotImplementedError

logger = logging.getLogger(__name__)

try:
    import pynetdicom  # noqa: F401

    _HAS_PYNETDICOM = True
except ImportError:
    _HAS_PYNETDICOM = False


class PACSService:
    """Service for PACS/DICOM operations."""

    def __init__(
        self,
        pacs_server_url: Optional[str] = None,
        ae_title: str = "NEUROPREDICT",
    ):
        self.pacs_server_url = (pacs_server_url or "").strip() or None
        self.ae_title = ae_title

    def is_configured(self) -> bool:
        return bool(self.pacs_server_url)

    def _require_dimse(self, operation: str) -> None:
        """Ensure DIMSE peer is configured and pynetdicom is available."""
        if not self.is_configured():
            raise IntegrationNotConfiguredError(
                f"PACS DIMSE '{operation}' is not configured. "
                "Set PACS_SERVER_URL (and AE title) to enable remote PACS. "
                "DIMSE C-FIND/C-MOVE/C-STORE requires the optional pynetdicom package."
            )
        if not _HAS_PYNETDICOM:
            raise IntegrationNotImplementedError(
                f"PACS DIMSE '{operation}' requires pynetdicom, which is not installed. "
                "Install pynetdicom and configure PACS_SERVER_URL / PACS_AE_TITLE."
            )
        # Peer configured and library present, but full DIMSE client not wired yet.
        raise IntegrationNotImplementedError(
            f"PACS DIMSE '{operation}' scaffolding is present but not fully implemented. "
            f"Configured peer: {self.pacs_server_url} (AE={self.ae_title})."
        )

    def query_patient_studies(
        self,
        patient_id: Optional[str] = None,
        patient_name: Optional[str] = None,
        study_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Query patient studies via C-FIND (requires configured PACS + pynetdicom)."""
        self._require_dimse("C-FIND study query")
        return []  # unreachable; keeps type checkers happy

    def retrieve_study(self, study_instance_uid: str) -> List[Dataset]:
        """Retrieve a study via C-MOVE/C-GET (requires configured PACS + pynetdicom)."""
        self._require_dimse(f"C-MOVE/C-GET retrieve ({study_instance_uid})")
        return []

    def store_dicom(
        self,
        dicom_file_path: str,
        patient_id: str,
        study_description: str,
    ) -> bool:
        """
        Prepare DICOM metadata locally, then attempt C-STORE to PACS.

        Raises IntegrationNotConfiguredError / IntegrationNotImplementedError
        when remote store cannot proceed (does not pretend success).
        """
        try:
            ds = pydicom.dcmread(dicom_file_path)

            if not hasattr(ds, "PatientID") or not ds.PatientID:
                ds.PatientID = patient_id

            if not hasattr(ds, "StudyDescription") or not ds.StudyDescription:
                ds.StudyDescription = study_description

            if not hasattr(ds, "StudyInstanceUID") or not ds.StudyInstanceUID:
                ds.StudyInstanceUID = generate_uid()

            if not hasattr(ds, "SeriesInstanceUID") or not ds.SeriesInstanceUID:
                ds.SeriesInstanceUID = generate_uid()

            if not hasattr(ds, "SOPInstanceUID") or not ds.SOPInstanceUID:
                ds.SOPInstanceUID = generate_uid()

            # Persist local metadata updates before remote C-STORE
            ds.save_as(dicom_file_path)
        except Exception as e:
            logger.error("Error preparing DICOM for PACS store: %s", e)
            raise

        self._require_dimse("C-STORE")
        return False

    def get_modality_worklist(
        self,
        patient_id: Optional[str] = None,
        scheduled_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Modality Worklist C-FIND (requires configured PACS + pynetdicom)."""
        self._require_dimse("C-FIND modality worklist")
        return []

    def parse_dicom_metadata(self, dicom_file_path: str) -> Dict[str, Any]:
        """Extract metadata from a local DICOM file (no remote PACS required)."""
        try:
            ds = pydicom.dcmread(dicom_file_path)

            return {
                "patient_id": getattr(ds, "PatientID", ""),
                "patient_name": str(getattr(ds, "PatientName", "")),
                "patient_birth_date": getattr(ds, "PatientBirthDate", ""),
                "patient_sex": getattr(ds, "PatientSex", ""),
                "study_instance_uid": getattr(ds, "StudyInstanceUID", ""),
                "study_date": getattr(ds, "StudyDate", ""),
                "study_time": getattr(ds, "StudyTime", ""),
                "study_description": getattr(ds, "StudyDescription", ""),
                "modality": getattr(ds, "Modality", ""),
                "series_instance_uid": getattr(ds, "SeriesInstanceUID", ""),
                "series_description": getattr(ds, "SeriesDescription", ""),
                "series_number": getattr(ds, "SeriesNumber", ""),
                "sop_instance_uid": getattr(ds, "SOPInstanceUID", ""),
                "instance_number": getattr(ds, "InstanceNumber", ""),
                "rows": getattr(ds, "Rows", 0),
                "columns": getattr(ds, "Columns", 0),
                "slice_thickness": getattr(ds, "SliceThickness", 0),
                "pixel_spacing": list(getattr(ds, "PixelSpacing", []) or []),
                "manufacturer": getattr(ds, "Manufacturer", ""),
                "manufacturer_model_name": getattr(ds, "ManufacturerModelName", ""),
            }
        except Exception as e:
            logger.error("Error parsing DICOM metadata: %s", e)
            return {}

    def validate_dicom_file(self, dicom_file_path: str) -> Dict[str, Any]:
        """Validate a local DICOM file (no remote PACS required)."""
        validation_result: Dict[str, Any] = {
            "valid": False,
            "errors": [],
            "warnings": [],
        }

        try:
            ds = pydicom.dcmread(dicom_file_path)

            required_fields = [
                "PatientID",
                "StudyInstanceUID",
                "SeriesInstanceUID",
                "SOPInstanceUID",
                "Modality",
            ]

            for field in required_fields:
                if not hasattr(ds, field) or not getattr(ds, field):
                    validation_result["errors"].append(f"Missing required field: {field}")

            valid_modalities = ["MR", "CT", "PT", "PET", "NM"]
            if hasattr(ds, "Modality") and ds.Modality not in valid_modalities:
                validation_result["warnings"].append(f"Unusual modality: {ds.Modality}")

            if not validation_result["errors"]:
                validation_result["valid"] = True

        except Exception as e:
            validation_result["errors"].append(f"Invalid DICOM file: {str(e)}")

        return validation_result
