from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Awaitable, Callable, Tuple

import pytest

pytest.importorskip("aiosqlite")
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security import get_current_active_user
from app.db.session import Base, get_db
from app.main import app
from app.models.medical_record import MedicalRecord
from app.models.patient import Gender, Patient
from app.models.prediction import DiseaseType, Prediction, RiskLevel
from app.models.user import User, UserRole


class DummyUser:
  id = 999
  role = "admin"
  is_active = True


async def override_current_user():
  return DummyUser()


async def create_test_client() -> Tuple[AsyncClient, async_sessionmaker[AsyncSession], Callable[[], Awaitable[None]]]:
  engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)

  session_factory = async_sessionmaker(engine, expire_on_commit=False)

  async def override_get_db():
    async with session_factory() as session:
      yield session

  app.dependency_overrides[get_db] = override_get_db
  app.dependency_overrides[get_current_active_user] = override_current_user

  transport = ASGITransport(app=app)
  client = AsyncClient(transport=transport, base_url="http://test")

  async def cleanup():
    await client.aclose()
    await engine.dispose()
    app.dependency_overrides.clear()

  return client, session_factory, cleanup


@pytest.mark.asyncio
async def test_clinical_report_endpoint_returns_latest_predictions(tmp_path: Path):
  client, session_factory, cleanup = await create_test_client()

  try:
    async with session_factory() as session:
      user = User(
        email="doctor@example.com",
        username="doctor",
        full_name="Doctor Example",
        hashed_password="hashed",
        role=UserRole.DOCTOR,
      )
      session.add(user)

      patient = Patient(
        patient_id="PT-1001",
        first_name="Sara",
        last_name="Rad",
        date_of_birth=date(1978, 5, 14),
        gender=Gender.FEMALE,
      )
      session.add(patient)
      await session.flush()

      record = MedicalRecord(
        patient_id=patient.id,
        visit_date=datetime.utcnow() - timedelta(days=2),
        visit_type="Follow-up",
      )
      session.add(record)

      prediction = Prediction(
        patient_id=patient.id,
        created_by=user.id,
        disease_type=DiseaseType.BOTH,
        alzheimer_risk_score=0.82,
        alzheimer_risk_level=RiskLevel.HIGH,
        parkinson_risk_score=0.34,
        parkinson_risk_level=RiskLevel.MEDIUM,
        model_version="alzheimers-v2",
        model_name="NeuroNet",
        recommendations="Recommend detailed neurological assessment.",
      )
      session.add(prediction)

      await session.commit()

    response = await client.get(f"/api/v1/reports/clinical?patient_id=1")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["patient"]["full_name"] == "Sara Rad"
    assert payload["predictions"][0]["alzheimer_risk_level"] == "high"
  finally:
    await cleanup()


@pytest.mark.asyncio
async def test_research_report_aggregates_predictions(tmp_path: Path):
  client, session_factory, cleanup = await create_test_client()

  try:
    async with session_factory() as session:
      user = User(
        email="admin@example.com",
        username="admin",
        full_name="Admin Example",
        hashed_password="hashed",
        role=UserRole.ADMIN,
      )
      session.add(user)

      patient = Patient(
        patient_id="PT-2001",
        first_name="Nima",
        last_name="Azad",
        date_of_birth=date(1968, 3, 3),
        gender=Gender.MALE,
      )
      session.add(patient)
      await session.flush()

      predictions = [
        Prediction(
          patient_id=patient.id,
          created_by=user.id,
          disease_type=DiseaseType.ALZHEIMER,
          alzheimer_risk_score=0.45,
          alzheimer_risk_level=RiskLevel.MEDIUM,
          model_version="alzheimers-v1",
        ),
        Prediction(
          patient_id=patient.id,
          created_by=user.id,
          disease_type=DiseaseType.PARKINSON,
          parkinson_risk_score=0.72,
          parkinson_risk_level=RiskLevel.HIGH,
          model_version="parkinsons-v1",
        ),
      ]
      session.add_all(predictions)
      await session.commit()

    response = await client.get("/api/v1/reports/research")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["total_predictions"] == 2
    assert payload["unique_patients"] == 1
  finally:
    await cleanup()


