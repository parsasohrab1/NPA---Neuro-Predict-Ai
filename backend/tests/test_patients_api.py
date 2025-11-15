"""
Tests for Patients API endpoints
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.patient import Patient, Gender
from app.models.medical_record import MedicalRecord
from conftest import override_get_current_user, TestUser, UserRole


@pytest.mark.asyncio
async def test_create_patient_success(
    test_client: AsyncClient,
    test_session: AsyncSession,
    test_patient_data: dict
):
    """Test successful patient creation"""
    test_user = TestUser(role=UserRole.NURSE)
    app.dependency_overrides[override_get_current_user(test_user)] = override_get_current_user(test_user)
    
    response = await test_client.post("/api/v1/patients/", json=test_patient_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["patient_id"] == test_patient_data["patient_id"]
    assert data["first_name"] == test_patient_data["first_name"]
    assert data["last_name"] == test_patient_data["last_name"]


@pytest.mark.asyncio
async def test_create_patient_duplicate_id(
    test_client: AsyncClient,
    test_session: AsyncSession,
    sample_patient: Patient,
    test_patient_data: dict
):
    """Test creating patient with duplicate patient_id fails"""
    test_user = TestUser(role=UserRole.NURSE)
    app.dependency_overrides[override_get_current_user(test_user)] = override_get_current_user(test_user)
    
    # Use same patient_id as sample_patient
    test_patient_data["patient_id"] = sample_patient.patient_id
    
    response = await test_client.post("/api/v1/patients/", json=test_patient_data)
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_patients_list(
    test_client: AsyncClient,
    test_session: AsyncSession,
    sample_patient: Patient
):
    """Test getting list of patients"""
    test_user = TestUser()
    app.dependency_overrides[override_get_current_user(test_user)] = override_get_current_user(test_user)
    
    response = await test_client.get("/api/v1/patients/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(p["id"] == sample_patient.id for p in data)


@pytest.mark.asyncio
async def test_get_patients_with_pagination(
    test_client: AsyncClient,
    test_session: AsyncSession,
    sample_patient: Patient
):
    """Test getting patients with pagination"""
    test_user = TestUser()
    app.dependency_overrides[override_get_current_user(test_user)] = override_get_current_user(test_user)
    
    response = await test_client.get("/api/v1/patients/?skip=0&limit=10")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10


@pytest.mark.asyncio
async def test_get_patients_with_search(
    test_client: AsyncClient,
    test_session: AsyncSession,
    sample_patient: Patient
):
    """Test searching patients"""
    test_user = TestUser()
    app.dependency_overrides[override_get_current_user(test_user)] = override_get_current_user(test_user)
    
    response = await test_client.get(f"/api/v1/patients/?search={sample_patient.first_name}")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(p["first_name"] == sample_patient.first_name for p in data)


@pytest.mark.asyncio
async def test_get_patient_by_id(
    test_client: AsyncClient,
    test_session: AsyncSession,
    sample_patient: Patient
):
    """Test getting patient by ID"""
    test_user = TestUser()
    app.dependency_overrides[override_get_current_user(test_user)] = override_get_current_user(test_user)
    
    response = await test_client.get(f"/api/v1/patients/{sample_patient.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_patient.id
    assert data["patient_id"] == sample_patient.patient_id


@pytest.mark.asyncio
async def test_get_patient_not_found(test_client: AsyncClient, test_session: AsyncSession):
    """Test getting non-existent patient"""
    test_user = TestUser()
    app.dependency_overrides[override_get_current_user(test_user)] = override_get_current_user(test_user)
    
    response = await test_client.get("/api/v1/patients/99999")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_patient(
    test_client: AsyncClient,
    test_session: AsyncSession,
    sample_patient: Patient
):
    """Test updating patient"""
    test_user = TestUser(role=UserRole.NURSE)
    app.dependency_overrides[override_get_current_user(test_user)] = override_get_current_user(test_user)
    
    update_data = {
        "first_name": "Updated",
        "phone": "+9876543210"
    }
    
    response = await test_client.put(
        f"/api/v1/patients/{sample_patient.id}",
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == update_data["first_name"]
    assert data["phone"] == update_data["phone"]


@pytest.mark.asyncio
async def test_get_patient_medical_records(
    test_client: AsyncClient,
    test_session: AsyncSession,
    sample_patient: Patient,
    sample_medical_record: MedicalRecord
):
    """Test getting patient medical records"""
    test_user = TestUser()
    app.dependency_overrides[override_get_current_user(test_user)] = override_get_current_user(test_user)
    
    response = await test_client.get(f"/api/v1/patients/{sample_patient.id}/medical-records")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(r["id"] == sample_medical_record.id for r in data)

