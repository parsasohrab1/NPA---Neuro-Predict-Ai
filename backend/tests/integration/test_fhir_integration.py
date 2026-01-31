"""
Integration Tests for HL7 FHIR
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.integration.fhir_service import FHIRService


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_patient_resource(client: AsyncClient, auth_headers: dict):
    """Test creating a Patient resource via FHIR API"""
    patient_data = {
        "name": "John Doe",
        "birth_date": "1980-01-01",
        "gender": "male",
        "identifiers": []
    }
    
    response = await client.post(
        "/api/v1/fhir/Patient",
        json=patient_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["resourceType"] == "Patient"
    assert data["gender"] == "male"
    assert data["birthDate"] == "1980-01-01"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_observation_resource(client: AsyncClient, auth_headers: dict):
    """Test creating an Observation resource via FHIR API"""
    observation_data = {
        "patient_id": "patient-123",
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "33747-0",
                "display": "MMSE Score"
            }],
            "text": "MMSE Score"
        },
        "value": 28,
        "effective_datetime": "2024-01-15T10:00:00Z",
        "status": "final"
    }
    
    response = await client.post(
        "/api/v1/fhir/Observation",
        json=observation_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["resourceType"] == "Observation"
    assert data["status"] == "final"
    assert "subject" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_diagnostic_report(client: AsyncClient, auth_headers: dict):
    """Test creating a DiagnosticReport resource via FHIR API"""
    report_data = {
        "patient_id": "patient-123",
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                "code": "LAB",
                "display": "Laboratory"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "33747-0",
                "display": "Alzheimer's Risk Assessment"
            }]
        },
        "effective_datetime": "2024-01-15T10:00:00Z",
        "conclusion": "High risk of Alzheimer's disease"
    }
    
    response = await client.post(
        "/api/v1/fhir/DiagnosticReport",
        json=report_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["resourceType"] == "DiagnosticReport"
    assert data["status"] == "final"
    assert "conclusion" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_search_observations(client: AsyncClient, auth_headers: dict):
    """Test searching for Observation resources"""
    response = await client.get(
        "/api/v1/fhir/Observation?patient=patient-123",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["resourceType"] == "Bundle"
    assert data["type"] == "searchset"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_fhir_capability_statement(client: AsyncClient):
    """Test FHIR CapabilityStatement endpoint"""
    response = await client.get("/api/v1/fhir/metadata")
    
    assert response.status_code == 200
    data = response.json()
    assert data["resourceType"] == "CapabilityStatement"
    assert data["fhirVersion"] == "4.0.1"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_fhir_service_create_patient():
    """Test FHIR service creating Patient resource"""
    fhir_service = FHIRService()
    
    patient = fhir_service.create_patient_resource(
        patient_id="test-123",
        name="Test Patient",
        birth_date="1980-01-01",
        gender="male"
    )
    
    assert patient.resource_type == "Patient"
    assert patient.id == "test-123"
    assert patient.gender == "male"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_fhir_service_create_bundle():
    """Test FHIR service creating Bundle"""
    fhir_service = FHIRService()
    
    patient = fhir_service.create_patient_resource(
        patient_id="test-123",
        name="Test Patient",
        birth_date="1980-01-01",
        gender="male"
    )
    
    observation = fhir_service.create_observation_resource(
        observation_id="obs-123",
        patient_id="test-123",
        code={"text": "MMSE Score"},
        value=28,
        effective_datetime="2024-01-15T10:00:00Z"
    )
    
    bundle = fhir_service.create_bundle([patient, observation])
    
    assert bundle.resource_type == "Bundle"
    assert len(bundle.entry) == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_fhir_resource_validation():
    """Test FHIR resource validation"""
    fhir_service = FHIRService()
    
    patient = fhir_service.create_patient_resource(
        patient_id="test-123",
        name="Test Patient",
        birth_date="1980-01-01",
        gender="male"
    )
    
    validation = fhir_service.validate_resource(patient)
    
    assert validation["valid"] == True
    assert len(validation["errors"]) == 0

