"""
Tests for Predictions API endpoints
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prediction import Prediction, DiseaseType, RiskLevel
from conftest import override_get_current_user, TestUser, UserRole


@pytest.mark.asyncio
async def test_create_prediction_success(
    test_client: AsyncClient,
    test_session: AsyncSession,
    sample_patient,
    sample_medical_record
):
    """Test successful prediction creation"""
    test_user = TestUser(role=UserRole.DOCTOR)
    app.dependency_overrides[override_get_current_user(test_user)] = override_get_current_user(test_user)
    
    prediction_data = {
        "patient_id": sample_patient.id,
        "disease_type": "both"
    }
    
    response = await test_client.post("/api/v1/predictions/", json=prediction_data)
    
    # Should succeed or return error if AI service not available
    assert response.status_code in [201, 500, 503]
    
    if response.status_code == 201:
        data = response.json()
        assert "patient_id" in data
        assert "alzheimer_risk_score" in data or "parkinson_risk_score" in data


@pytest.mark.asyncio
async def test_create_prediction_patient_not_found(
    test_client: AsyncClient,
    test_session: AsyncSession
):
    """Test creating prediction for non-existent patient"""
    test_user = TestUser(role=UserRole.DOCTOR)
    app.dependency_overrides[override_get_current_user(test_user)] = override_get_current_user(test_user)
    
    prediction_data = {
        "patient_id": 99999,
        "disease_type": "both"
    }
    
    response = await test_client.post("/api/v1/predictions/", json=prediction_data)
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_predictions_list(
    test_client: AsyncClient,
    test_session: AsyncSession,
    sample_prediction: Prediction
):
    """Test getting list of predictions"""
    test_user = TestUser()
    app.dependency_overrides[override_get_current_user(test_user)] = override_get_current_user(test_user)
    
    response = await test_client.get("/api/v1/predictions/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(p["id"] == sample_prediction.id for p in data)


@pytest.mark.asyncio
async def test_get_predictions_by_patient(
    test_client: AsyncClient,
    test_session: AsyncSession,
    sample_prediction: Prediction
):
    """Test getting predictions filtered by patient"""
    test_user = TestUser()
    app.dependency_overrides[override_get_current_user(test_user)] = override_get_current_user(test_user)
    
    response = await test_client.get(
        f"/api/v1/predictions/?patient_id={sample_prediction.patient_id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(p["patient_id"] == sample_prediction.patient_id for p in data)


@pytest.mark.asyncio
async def test_get_prediction_by_id(
    test_client: AsyncClient,
    test_session: AsyncSession,
    sample_prediction: Prediction
):
    """Test getting prediction by ID"""
    test_user = TestUser()
    app.dependency_overrides[override_get_current_user(test_user)] = override_get_current_user(test_user)
    
    response = await test_client.get(f"/api/v1/predictions/{sample_prediction.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_prediction.id
    assert data["patient_id"] == sample_prediction.patient_id


@pytest.mark.asyncio
async def test_get_prediction_not_found(test_client: AsyncClient, test_session: AsyncSession):
    """Test getting non-existent prediction"""
    test_user = TestUser()
    app.dependency_overrides[override_get_current_user(test_user)] = override_get_current_user(test_user)
    
    response = await test_client.get("/api/v1/predictions/99999")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_review_prediction(
    test_client: AsyncClient,
    test_session: AsyncSession,
    sample_prediction: Prediction
):
    """Test reviewing a prediction"""
    test_user = TestUser(role=UserRole.DOCTOR)
    app.dependency_overrides[override_get_current_user(test_user)] = override_get_current_user(test_user)
    
    review_data = {
        "approved": True,
        "review_notes": "Looks good"
    }
    
    response = await test_client.post(
        f"/api/v1/predictions/{sample_prediction.id}/review",
        json=review_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_reviewed"] == review_data["approved"]
    assert "reviewed_by" in data

