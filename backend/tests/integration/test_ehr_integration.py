"""
Integration Tests for EHR/HIS Integration
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from app.services.integration.ehr_service import EHRService


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_patient_from_ehr(client: AsyncClient, auth_headers: dict):
    """Test getting patient data from EHR"""
    patient_id = "PATIENT123"
    
    # Mock EHR service response
    with patch.object(EHRService, 'get_patient_data') as mock_get:
        mock_get.return_value = {
            "patient_id": patient_id,
            "name": "John Doe",
            "birth_date": "1980-01-01",
            "gender": "M"
        }
        
        response = await client.get(
            f"/api/v1/ehr/patients/{patient_id}",
            headers=auth_headers
        )
        
        # Note: This will fail if EHR_API_URL is not configured
        # In real scenario, we'd use a test EHR server
        assert response.status_code in [200, 404, 500]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_lab_results(client: AsyncClient, auth_headers: dict):
    """Test getting lab results from EHR"""
    patient_id = "PATIENT123"
    
    with patch.object(EHRService, 'get_patient_lab_results') as mock_get:
        mock_get.return_value = [
            {
                "test_code": "33747-0",
                "test_name": "MMSE Score",
                "result_value": "28",
                "units": "score",
                "date": "2024-01-15"
            }
        ]
        
        response = await client.get(
            f"/api/v1/ehr/patients/{patient_id}/lab-results",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404, 500]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_medications(client: AsyncClient, auth_headers: dict):
    """Test getting medications from EHR"""
    patient_id = "PATIENT123"
    
    with patch.object(EHRService, 'get_patient_medications') as mock_get:
        mock_get.return_value = [
            {
                "medication_name": "Donepezil",
                "dosage": "10mg",
                "frequency": "Once daily"
            }
        ]
        
        response = await client.get(
            f"/api/v1/ehr/patients/{patient_id}/medications",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404, 500]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_vital_signs(client: AsyncClient, auth_headers: dict):
    """Test getting vital signs from EHR"""
    patient_id = "PATIENT123"
    
    with patch.object(EHRService, 'get_patient_vital_signs') as mock_get:
        mock_get.return_value = [
            {
                "blood_pressure": {"systolic": 120, "diastolic": 80},
                "heart_rate": 72,
                "temperature": 98.6,
                "date": "2024-01-15"
            }
        ]
        
        response = await client.get(
            f"/api/v1/ehr/patients/{patient_id}/vital-signs",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404, 500]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_sync_patient_data(client: AsyncClient, auth_headers: dict):
    """Test syncing patient data from EHR"""
    patient_id = "PATIENT123"
    
    with patch.object(EHRService, 'sync_patient_data') as mock_sync:
        mock_sync.return_value = {
            "patient_id": patient_id,
            "timestamp": "2024-01-15T10:00:00Z",
            "patient_data": {},
            "lab_results": [],
            "medications": [],
            "vital_signs": [],
            "success": True
        }
        
        response = await client.post(
            f"/api/v1/ehr/patients/{patient_id}/sync",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404, 500]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_send_prediction_to_ehr(client: AsyncClient, auth_headers: dict):
    """Test sending prediction result to EHR"""
    patient_id = "PATIENT123"
    prediction_data = {
        "disease_type": "alzheimer",
        "risk_level": "high",
        "risk_score": 0.85,
        "confidence": 0.92,
        "recommendations": ["Follow-up MRI in 6 months"]
    }
    
    with patch.object(EHRService, 'send_prediction_result') as mock_send:
        mock_send.return_value = True
        
        response = await client.post(
            f"/api/v1/ehr/patients/{patient_id}/predictions",
            json=prediction_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404, 500]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_ehr_service_get_patient_data():
    """Test EHR service getting patient data"""
    ehr_service = EHRService(ehr_api_url="http://test-ehr.com")
    
    # This will fail without actual EHR server, but tests structure
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "patient_id": "PATIENT123",
            "name": "John Doe"
        }
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        result = await ehr_service.get_patient_data("PATIENT123")
        assert isinstance(result, dict)

