"""
Integration Tests for HL7 v2 Integration
"""
import pytest
from httpx import AsyncClient

from app.services.integration.hl7v2_service import HL7v2Service, HL7v2Message


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_admit_message(client: AsyncClient, auth_headers: dict):
    """Test creating ADT^A01 (Admit Patient) message"""
    admit_data = {
        "patient_id": "PATIENT123",
        "patient_name": "DOE^JOHN^MIDDLE",
        "birth_date": "19800101",
        "gender": "M",
        "admission_date": "20240115100000",
        "admitting_doctor": "DOCTOR^ADMITTING"
    }
    
    response = await client.post(
        "/api/v1/hl7v2/admit",
        json=admit_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message_type"] == "ADT^A01"
    assert "message" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_observation_message(client: AsyncClient, auth_headers: dict):
    """Test creating ORU^R01 (Observation Result) message"""
    observation_data = {
        "patient_id": "PATIENT123",
        "observation_id": "OBS001",
        "observation_code": "8480-6",
        "observation_value": "120",
        "observation_units": "mmHg",
        "observation_date": "20240115100000",
        "status": "F"
    }
    
    response = await client.post(
        "/api/v1/hl7v2/observation",
        json=observation_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message_type"] == "ORU^R01"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_lab_result_message(client: AsyncClient, auth_headers: dict):
    """Test creating lab result message"""
    lab_data = {
        "patient_id": "PATIENT123",
        "test_code": "33747-0",
        "test_name": "MMSE Score",
        "result_value": "28",
        "units": "score",
        "reference_range": "24-30",
        "result_status": "F"
    }
    
    response = await client.post(
        "/api/v1/hl7v2/lab-result",
        json=lab_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message_type"] == "ORU^R01"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_vital_signs_message(client: AsyncClient, auth_headers: dict):
    """Test creating vital signs message"""
    vital_signs_data = {
        "patient_id": "PATIENT123",
        "vital_signs": {
            "blood_pressure": {"systolic": 120, "diastolic": 80},
            "heart_rate": 72,
            "temperature": 98.6,
            "respiratory_rate": 16,
            "oxygen_saturation": 98
        }
    }
    
    response = await client.post(
        "/api/v1/hl7v2/vital-signs",
        json=vital_signs_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message_type"] == "ORU^R01"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_parse_hl7_message(client: AsyncClient, auth_headers: dict):
    """Test parsing HL7 v2 message"""
    message = "MSH|^~\\&|NEUROPREDICT|HOSPITAL|LAB|LAB|20240115100000||ORU^R01^ORU_R01|MSG002|P|2.5\rPID|1||PATIENT123|||||||\rOBR|1|OBS001||8480-6^Systolic BP||||20240115100000|||||||||||F||||||\rOBX|1|NM|8480-6^Systolic BP||120|mmHg||||F|||20240115100000\r"
    
    response = await client.post(
        "/api/v1/hl7v2/parse",
        json={"message": message},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "segments" in data
    assert "patient_info" in data
    assert "observations" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_validate_hl7_message(client: AsyncClient, auth_headers: dict):
    """Test validating HL7 v2 message"""
    message = "MSH|^~\\&|NEUROPREDICT|HOSPITAL|LAB|LAB|20240115100000||ORU^R01^ORU_R01|MSG002|P|2.5\rPID|1||PATIENT123|||||||\r"
    
    response = await client.post(
        "/api/v1/hl7v2/validate",
        json={"message": message},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "valid" in data
    assert "errors" in data


@pytest.mark.asyncio
@pytest.mark.integration
def test_hl7v2_service_create_admit():
    """Test HL7 v2 service creating admit message"""
    hl7v2_service = HL7v2Service()
    
    message = hl7v2_service.create_admit_message(
        patient_id="PATIENT123",
        patient_name="DOE^JOHN^MIDDLE",
        birth_date="19800101",
        gender="M",
        admission_date="20240115100000",
        admitting_doctor="DOCTOR^ADMITTING"
    )
    
    assert isinstance(message, HL7v2Message)
    assert message.get_segment("MSH") is not None
    assert message.get_segment("PID") is not None
    assert message.get_segment("PV1") is not None


@pytest.mark.asyncio
@pytest.mark.integration
def test_hl7v2_message_validation():
    """Test HL7 v2 message validation"""
    hl7v2_service = HL7v2Service()
    
    message = hl7v2_service.create_admit_message(
        patient_id="PATIENT123",
        patient_name="DOE^JOHN^MIDDLE",
        birth_date="19800101",
        gender="M",
        admission_date="20240115100000",
        admitting_doctor="DOCTOR^ADMITTING"
    )
    
    is_valid, errors = message.validate()
    assert is_valid == True
    assert len(errors) == 0


@pytest.mark.asyncio
@pytest.mark.integration
def test_hl7v2_extract_patient_info():
    """Test extracting patient info from HL7 v2 message"""
    hl7v2_service = HL7v2Service()
    
    message = hl7v2_service.create_admit_message(
        patient_id="PATIENT123",
        patient_name="DOE^JOHN^MIDDLE",
        birth_date="19800101",
        gender="M",
        admission_date="20240115100000",
        admitting_doctor="DOCTOR^ADMITTING"
    )
    
    patient_info = hl7v2_service.extract_patient_info(message)
    assert patient_info["patient_id"] == "PATIENT123"
    assert patient_info["gender"] == "M"

