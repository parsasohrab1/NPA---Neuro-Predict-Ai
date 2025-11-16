"""
Pytest configuration and shared fixtures
"""
import pytest
from datetime import date, datetime
from pathlib import Path
from typing import AsyncGenerator, Callable, Awaitable
from unittest.mock import AsyncMock

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy import select

from app.core.config import settings
from app.core.security import get_current_user, get_current_active_user
from app.db.session import Base, get_db
from app.main import app
from app.models.user import User, UserRole
from app.models.patient import Patient, Gender
from app.models.medical_record import MedicalRecord
from app.models.prediction import Prediction, DiseaseType, RiskLevel


# ---------------------
# Global seeds & faker
# ---------------------
@pytest.fixture(autouse=True, scope="session")
def _global_seed():
    """Set deterministic seeds for reproducibility across tests."""
    import random
    import numpy as np
    random.seed(42)
    np.random.seed(42)
    try:
        import torch  # type: ignore
        torch.manual_seed(42)
    except Exception:
        pass
    yield


class TestUser:
    """Mock user for testing"""
    def __init__(self, user_id=1, role=UserRole.DOCTOR, is_active=True):
        self.id = user_id
        self.role = role
        self.is_active = is_active
        self.email = "test@example.com"
        self.username = "testuser"
        self.full_name = "Test User"
        self.is_verified = True


@pytest.fixture
async def test_db_engine():
    """Create in-memory test database"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_session(test_db_engine):
    """Create test database session"""
    async_session = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def test_client(test_db_engine, tmp_path: Path):
    """Create test HTTP client with database override"""
    session_factory = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    # Override dependencies
    app.dependency_overrides[get_db] = override_get_db
    
    # Save original settings
    original_upload_dir = settings.UPLOAD_DIR
    original_dicom_dir = settings.DICOM_DIR
    
    # Use temporary directory for uploads
    storage_root = tmp_path / "storage"
    settings.UPLOAD_DIR = str(storage_root)
    settings.DICOM_DIR = str(storage_root / "dicom")
    Path(settings.DICOM_DIR).mkdir(parents=True, exist_ok=True)

    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")

    yield client

    # Cleanup
    await client.aclose()
    await test_db_engine.dispose()
    app.dependency_overrides.clear()
    settings.UPLOAD_DIR = original_upload_dir
    settings.DICOM_DIR = original_dicom_dir


@pytest.fixture
def test_user():
    """Create test user"""
    return TestUser(user_id=1, role=UserRole.DOCTOR)


@pytest.fixture
def test_patient_data():
    """Sample patient data for testing"""
    return {
        "patient_id": "PT-001",
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1980-01-15",
        "gender": "male",
        "email": "john.doe@example.com",
        "phone": "+1234567890"
    }


@pytest.fixture
async def sample_patient(test_session: AsyncSession):
    """Create a sample patient in database"""
    patient = Patient(
        patient_id="PT-001",
        first_name="John",
        last_name="Doe",
        date_of_birth=date(1980, 1, 15),
        gender=Gender.MALE,
        email="john.doe@example.com"
    )
    test_session.add(patient)
    await test_session.commit()
    await test_session.refresh(patient)
    return patient


@pytest.fixture
async def sample_medical_record(test_session: AsyncSession, sample_patient: Patient):
    """Create a sample medical record"""
    record = MedicalRecord(
        patient_id=sample_patient.id,
        visit_date=datetime.utcnow(),
        visit_type="Initial",
        mmse_score=25.0,
        moca_score=24.0,
        amyloid_beta=600.0,
        tau_protein=200.0
    )
    test_session.add(record)
    await test_session.commit()
    await test_session.refresh(record)
    return record


@pytest.fixture
async def sample_prediction(test_session: AsyncSession, sample_patient: Patient):
    """Create a sample prediction"""
    prediction = Prediction(
        patient_id=sample_patient.id,
        created_by=1,
        disease_type=DiseaseType.BOTH,
        alzheimer_risk_score=0.65,
        alzheimer_risk_level=RiskLevel.MEDIUM,
        alzheimer_confidence=0.82,
        parkinson_risk_score=0.35,
        parkinson_risk_level=RiskLevel.LOW,
        parkinson_confidence=0.78
    )
    test_session.add(prediction)
    await test_session.commit()
    await test_session.refresh(prediction)
    return prediction


def override_get_current_user(user: TestUser = None):
    """Override for get_current_user dependency"""
    if user is None:
        user = TestUser()
    
    async def _get_current_user():
        return user
    
    return _get_current_user


def override_get_current_active_user(user: TestUser = None):
    """Override for get_current_active_user dependency"""
    if user is None:
        user = TestUser()
    
    async def _get_current_active_user():
        return user
    
    return _get_current_active_user


def override_require_role(required_role):
    """Override for require_role dependency"""
    async def _require_role(current_user: TestUser = None):
        if current_user is None:
            current_user = TestUser()
        if current_user.role != required_role:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role} role"
            )
        return current_user
    return _require_role


# ---------------------
# Factories
# ---------------------
@pytest.fixture
def user_factory():
    def _make_user(user_id: int = 1, role: UserRole = UserRole.DOCTOR) -> TestUser:
        return TestUser(user_id=user_id, role=role)
    return _make_user


@pytest.fixture
def auth_token_factory():
    from app.core.security import create_access_token
    def _make_token(user_id: int) -> str:
        return create_access_token({"sub": str(user_id)})
    return _make_token


@pytest.fixture
async def make_patient(test_session: AsyncSession):
    async def _create(
        pid: str = "PT-FAKE",
        first_name: str = "Ali",
        last_name: str = "Rezaei",
        gender: Gender = Gender.MALE,
        dob: date = date(1985, 5, 20),
    ) -> Patient:
        p = Patient(
            patient_id=pid,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=dob,
            gender=gender,
            email=f"{pid.lower()}@example.com",
        )
        test_session.add(p)
        await test_session.commit()
        await test_session.refresh(p)
        return p
    return _create


@pytest.fixture
async def make_medical_record(test_session: AsyncSession):
    async def _create(
        patient: Patient,
        visit_date: datetime | None = None,
        mmse: float = 26.0,
        moca: float = 25.0,
    ) -> MedicalRecord:
        rec = MedicalRecord(
            patient_id=patient.id,
            visit_date=visit_date or datetime.utcnow(),
            visit_type="Follow-up",
            mmse_score=mmse,
            moca_score=moca,
            amyloid_beta=600.0,
            tau_protein=200.0,
        )
        test_session.add(rec)
        await test_session.commit()
        await test_session.refresh(rec)
        return rec
    return _create


# ---------------------
# Mocks
# ---------------------
@pytest.fixture
def mock_ai_model_service(monkeypatch):
    """Mock AI model outputs with deterministic numbers."""
    try:
        from app.services import ai_model_service as _maybe  # type: ignore
    except Exception:
        _maybe = None

    async def _predict_stub(patient_data):
        return {
            "alzheimer": {"risk_score": 0.42, "risk_level": RiskLevel.MEDIUM, "confidence": 0.9},
            "parkinson": {"risk_score": 0.13, "risk_level": RiskLevel.LOW, "confidence": 0.88},
            "attention_scores": {"MRI": 0.5, "Biomarker": 0.3, "Cognitive": 0.2},
            "feature_importance": {"mmse_score": 0.4},
            "recommendations": "mock",
            "model_version": "test-1.0",
            "model_name": "mock",
        }
    try:
        from app.services.ai_model_service import ai_model_service
        monkeypatch.setattr(ai_model_service, "predict", _predict_stub, raising=True)
    except Exception:
        pass
    return True


@pytest.fixture
def mock_integration_service(monkeypatch):
    """Mock integration service external calls."""
    try:
        from app.services import integration_service  # type: ignore
    except Exception:
        integration_service = None  # type: ignore

    try:
        from app.services.integration_service import IntegrationService
        async def _ok(*args, **kwargs):
            return {"ok": True}
        monkeypatch.setattr(IntegrationService, "send_hl7_message", _ok, raising=False)
        monkeypatch.setattr(IntegrationService, "send_fhir_resource", _ok, raising=False)
        monkeypatch.setattr(IntegrationService, "get_fhir_resource", _ok, raising=False)
        monkeypatch.setattr(IntegrationService, "query_fhir_resources", _ok, raising=False)
        monkeypatch.setattr(IntegrationService, "fetch_pacs_study", _ok, raising=False)
        monkeypatch.setattr(IntegrationService, "sync_imaging_from_pacs", _ok, raising=False)
    except Exception:
        pass
    return True


@pytest.fixture
def redis_client_fake(monkeypatch):
    """In-memory fake for cache layer style get/set during tests."""
    store: dict[str, str] = {}

    class FakeRedis:
        async def get(self, k): return store.get(k)
        async def set(self, k, v): store[k] = v; return True
        async def setex(self, k, ttl, v): store[k] = v; return True
        async def incr(self, k): store[k] = str(int(store.get(k, "0")) + 1); return int(store[k])
        async def ping(self): return True
        async def close(self): return True

    return FakeRedis()
