"""
Pytest Configuration and Fixtures
"""
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base, get_db
from app.models.user import User, UserRole
from app.models.patient import Patient, Gender
from app.models.medical_record import MedicalRecord
from app.models.prediction import Prediction, DiseaseType, RiskLevel
from app.core.security import get_password_hash, create_access_token
from datetime import datetime, date


# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client"""
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


# Aliases used by legacy integration-style tests
@pytest.fixture(scope="function")
async def test_client(client: AsyncClient) -> AsyncClient:
    return client


@pytest.fixture(scope="function")
async def test_session(test_db: AsyncSession) -> AsyncSession:
    return test_db


@pytest.fixture
async def sample_patient(test_patient: Patient) -> Patient:
    return test_patient


@pytest.fixture
async def test_user(test_db: AsyncSession) -> User:
    """Create test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=get_password_hash("testpass123"),
        role=UserRole.DOCTOR,
        is_active=True,
        is_verified=True
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
async def test_admin(test_db: AsyncSession) -> User:
    """Create test admin user"""
    admin = User(
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )
    test_db.add(admin)
    await test_db.commit()
    await test_db.refresh(admin)
    return admin


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create auth headers for test user"""
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(test_admin: User) -> dict:
    """Create auth headers for admin user"""
    token = create_access_token({"sub": str(test_admin.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_patient(test_db: AsyncSession, test_user: User) -> Patient:
    """Create test patient"""
    patient = Patient(
        first_name="John",
        last_name="Doe",
        date_of_birth=date(1950, 1, 1),
        gender=Gender.MALE,
        email="john.doe@example.com",
        phone="+1234567890",
        address="123 Test St",
        assigned_doctor_id=test_user.id
    )
    test_db.add(patient)
    await test_db.commit()
    await test_db.refresh(patient)
    return patient


@pytest.fixture
async def test_medical_record(test_db: AsyncSession, test_patient: Patient) -> MedicalRecord:
    """Create test medical record"""
    record = MedicalRecord(
        patient_id=test_patient.id,
        visit_date=datetime.now(),
        visit_type="Initial",
        mmse_score=25.0,
        moca_score=24.0,
        memory_score=50.0,
        attention_score=50.0,
        executive_function_score=50.0,
        amyloid_beta=600.0,
        tau_protein=200.0,
        dopamine_level=100.0,
        apoe_e4_status=False,
        hippocampal_volume=3500.0,
        cortical_thickness=2.3,
        ventricular_volume=30000.0,
        white_matter_hyperintensities=2.0,
        brain_volume_total=1100000.0
    )
    test_db.add(record)
    await test_db.commit()
    await test_db.refresh(record)
    return record


@pytest.fixture
async def test_prediction(test_db: AsyncSession, test_patient: Patient, test_user: User) -> Prediction:
    """Create test prediction"""
    prediction = Prediction(
        patient_id=test_patient.id,
        created_by=test_user.id,
        disease_type=DiseaseType.ALZHEIMER,
        alzheimer_risk_score=0.65,
        alzheimer_risk_level=RiskLevel.MEDIUM,
        alzheimer_confidence=0.75,
        model_version="1.0.0",
        model_name="TestModel"
    )
    test_db.add(prediction)
    await test_db.commit()
    await test_db.refresh(prediction)
    return prediction


@pytest.fixture
def sample_patient_data() -> dict:
    """Sample patient data for testing"""
    return {
        "first_name": "Jane",
        "last_name": "Smith",
        "date_of_birth": "1960-05-15",
        "gender": "female",
        "email": "jane.smith@example.com",
        "phone": "+1234567891",
        "address": "456 Test Ave"
    }


@pytest.fixture
def sample_prediction_data() -> dict:
    """Sample prediction request data"""
    return {
        "patient_id": 1,
        "disease_type": "alzheimer"
    }


@pytest.fixture
def sample_medical_record_data() -> dict:
    """Sample medical record data"""
    return {
        "visit_date": datetime.now().isoformat(),
        "visit_type": "Follow-up",
        "mmse_score": 26.0,
        "moca_score": 25.0,
        "memory_score": 55.0,
        "attention_score": 55.0,
        "executive_function_score": 55.0,
        "amyloid_beta": 550.0,
        "tau_protein": 180.0,
        "dopamine_level": 110.0,
        "apoe_e4_status": False,
        "hippocampal_volume": 3600.0,
        "cortical_thickness": 2.4,
        "ventricular_volume": 28000.0,
        "white_matter_hyperintensities": 1.5,
        "brain_volume_total": 1120000.0
    }

