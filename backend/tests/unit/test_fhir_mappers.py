"""
Unit tests for FHIR mappers.

These tests deliberately avoid the database: they construct lightweight
``SimpleNamespace`` stand-ins shaped like the SQLAlchemy models. The mappers
only read attributes, so this is faithful and far cheaper than spinning up a
real session for what is effectively a pure transformation.
"""
from __future__ import annotations

from datetime import date, datetime
from types import SimpleNamespace

import pytest

from app.services.integration.fhir_mappers import (
    build_capability_statement,
    build_searchset_bundle,
    medical_record_to_observations,
    patient_to_fhir,
    prediction_to_diagnostic_report,
)

pytestmark = pytest.mark.unit


def _make_patient() -> SimpleNamespace:
    gender = SimpleNamespace(value="female")
    return SimpleNamespace(
        id=42,
        patient_id="MRN-0001",
        first_name="Jane",
        last_name="Doe",
        date_of_birth=date(1960, 5, 15),
        gender=gender,
        email="jane@example.org",
        phone="+1-555-0100",
        address="123 Test St",
    )


def test_patient_to_fhir_basic_shape() -> None:
    patient = _make_patient()
    resource = patient_to_fhir(patient)

    assert resource["resourceType"] == "Patient"
    assert resource["id"] == "42"
    assert resource["gender"] == "female"
    assert resource["birthDate"] == "1960-05-15"
    assert resource["name"][0]["family"] == "Doe"
    assert resource["name"][0]["given"] == ["Jane"]
    assert {entry["system"] for entry in resource["telecom"]} == {"email", "phone"}
    assert resource["identifier"][0]["value"] == "MRN-0001"


def test_patient_to_fhir_unknown_gender_falls_back() -> None:
    patient = _make_patient()
    patient.gender = SimpleNamespace(value="prefer-not-to-say")
    resource = patient_to_fhir(patient)
    assert resource["gender"] == "unknown"


def test_medical_record_to_observations_skips_none_values() -> None:
    record = SimpleNamespace(
        id=7,
        patient_id=42,
        visit_date=datetime(2024, 1, 2, 10, 0, 0),
        mmse_score=27.0,
        moca_score=None,
        memory_score=None,
        attention_score=None,
        executive_function_score=None,
        amyloid_beta=None,
        tau_protein=None,
        dopamine_level=None,
        apoe_e4_status=None,
        hippocampal_volume=None,
        cortical_thickness=None,
        ventricular_volume=None,
        white_matter_hyperintensities=None,
        brain_volume_total=None,
        blood_pressure_systolic=128.0,
        blood_pressure_diastolic=82.0,
        temperature=None,
        heart_rate=72.0,
        respiratory_rate=None,
        oxygen_saturation=None,
        weight=None,
        height=None,
        bmi=None,
        blood_glucose=None,
        cholesterol_total=None,
    )
    obs = medical_record_to_observations(record)

    codes = {o["code"]["coding"][0]["code"] for o in obs}
    # mmse + 2 BPs + heart rate
    assert codes == {"72133-2", "8480-6", "8462-4", "8867-4"}
    for o in obs:
        assert o["resourceType"] == "Observation"
        assert o["status"] == "final"
        assert o["subject"] == {"reference": "Patient/42"}
        assert o["effectiveDateTime"].startswith("2024-01-02")


def test_prediction_to_diagnostic_report_includes_components() -> None:
    prediction = SimpleNamespace(
        id=99,
        patient_id=42,
        created_at=datetime(2024, 6, 1, 12, 0, 0),
        alzheimer_risk_score=0.65,
        alzheimer_risk_level=SimpleNamespace(value="medium"),
        alzheimer_confidence=0.8,
        parkinson_risk_score=0.20,
        parkinson_risk_level=SimpleNamespace(value="low"),
        parkinson_confidence=0.7,
        model_version="1.2.3",
        model_name="AttentionFusion",
    )
    report = prediction_to_diagnostic_report(prediction)

    assert report["resourceType"] == "DiagnosticReport"
    assert report["id"] == "99"
    assert report["subject"] == {"reference": "Patient/42"}
    assert "Alzheimer" in report["conclusion"]
    assert "Parkinson" in report["conclusion"]
    component_codes = {c["code"]["coding"][0]["code"] for c in report["result"]}
    assert component_codes == {"alzheimer-risk-score", "parkinson-risk-score"}
    assert report["performer"][0]["display"] == "AttentionFusion (1.2.3)"


def test_build_searchset_bundle_wraps_resources() -> None:
    bundle = build_searchset_bundle(
        [
            {"resourceType": "Patient", "id": "1"},
            {"resourceType": "Patient", "id": "2"},
        ],
        base_url="http://api.example/api/v1/fhir",
    )
    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "searchset"
    assert bundle["total"] == 2
    assert bundle["entry"][0]["fullUrl"].endswith("Patient/1")
    assert bundle["entry"][1]["resource"]["id"] == "2"


def test_build_searchset_bundle_handles_empty() -> None:
    bundle = build_searchset_bundle([], base_url="http://api.example/api/v1/fhir")
    assert bundle["total"] == 0
    assert bundle["entry"] == []


def test_capability_statement_advertises_resources() -> None:
    cap = build_capability_statement()
    assert cap["resourceType"] == "CapabilityStatement"
    assert cap["fhirVersion"] == "4.0.1"
    types = {entry["type"] for entry in cap["rest"][0]["resource"]}
    assert {"Patient", "Observation", "DiagnosticReport", "ImagingStudy"} <= types
