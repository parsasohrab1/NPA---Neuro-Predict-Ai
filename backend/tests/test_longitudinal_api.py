from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Awaitable, Callable, Tuple

import pytest
pytest.importorskip("pydicom")
pytest.importorskip("numpy")

import numpy as np
import pydicom
from httpx import ASGITransport, AsyncClient
from pydicom.uid import ExplicitVRLittleEndian, MRImageStorage, generate_uid
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security import get_current_active_user
from app.db.session import Base, get_db
from app.main import app
from app.models.imaging import ImagingStudy, ImagingModality
from app.models.medical_record import MedicalRecord
from app.models.patient import Gender, Patient
from app.models.user import User, UserRole
from app.core.config import settings


class DummyUser:
    id = 1
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

    transport = ASGITransport(app=app, lifespan="auto")
    client = AsyncClient(transport=transport, base_url="http://test")

    async def cleanup():
        await client.aclose()
        await engine.dispose()
        app.dependency_overrides.clear()

    return client, session_factory, cleanup


def _create_dummy_dicom(path: Path, intensity: int) -> None:
    file_meta = pydicom.dataset.Dataset()
    file_meta.MediaStorageSOPClassUID = MRImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    ds = pydicom.dataset.FileDataset(
        str(path),
        {},
        file_meta=file_meta,
        preamble=b"\x00" * 128,
    )
    ds.PatientID = "TEST"
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.Modality = "MR"
    ds.Rows = 64
    ds.Columns = 64
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 0
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    pixel_array = np.full((64, 64), intensity, dtype=np.uint16)
    ds.PixelData = pixel_array.tobytes()
    ds.save_as(str(path))


@pytest.mark.asyncio
async def test_longitudinal_episode_flow(tmp_path: Path):
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
                patient_id="PT-LON-001",
                first_name="Amir",
                last_name="Karimi",
                date_of_birth=date(1975, 2, 12),
                gender=Gender.MALE,
            )
            session.add(patient)
            await session.commit()
            await session.refresh(patient)
            patient_id = patient.id

            # Create medical records and imaging studies
            record_a = MedicalRecord(
                patient_id=patient_id,
                visit_date=datetime.utcnow(),
            )
            record_b = MedicalRecord(
                patient_id=patient_id,
                visit_date=datetime.utcnow(),
            )
            session.add_all([record_a, record_b])
            await session.commit()
            await session.refresh(record_a)
            await session.refresh(record_b)

            dicom_a = tmp_path / "visit_a.dcm"
            dicom_b = tmp_path / "visit_b.dcm"
            _create_dummy_dicom(dicom_a, 120)
            _create_dummy_dicom(dicom_b, 200)

            imaging_a = ImagingStudy(
                medical_record_id=record_a.id,
                study_id=generate_uid(),
                study_date=datetime.utcnow(),
                modality=ImagingModality.MRI,
                dicom_path=str(dicom_a),
            )
            imaging_b = ImagingStudy(
                medical_record_id=record_b.id,
                study_id=generate_uid(),
                study_date=datetime.utcnow(),
                modality=ImagingModality.MRI,
                dicom_path=str(dicom_b),
            )
            session.add_all([imaging_a, imaging_b])
            await session.commit()
            await session.refresh(imaging_a)
            await session.refresh(imaging_b)

        # Create episode
        response = await client.post(
            f"/api/v1/longitudinal/{patient_id}/episodes",
            json={"title": "Baseline Program", "start_date": datetime.utcnow().isoformat()},
        )
        assert response.status_code == 201, response.text
        episode_id = response.json()["id"]

        # Add visit
        response = await client.post(
            f"/api/v1/longitudinal/episodes/{episode_id}/visits",
            json={
                "visit_type": "baseline",
                "visit_date": datetime.utcnow().isoformat(),
                "notes": "Initial assessment",
                "imaging_study_id": imaging_a.id,
            },
        )
        assert response.status_code == 201, response.text
        visit_id = response.json()["id"]
        visit_a_id = visit_id

        # Add metrics
        response = await client.post(
            f"/api/v1/longitudinal/visits/{visit_id}/metrics",
            params={"episode_id": episode_id},
            json=[
                {
                    "metric_type": "cognitive",
                    "metric_key": "mmse",
                    "metric_value": 27,
                    "unit": "score",
                },
                {
                    "metric_type": "biomarker",
                    "metric_key": "amyloid_beta",
                    "metric_value": 580,
                    "unit": "pg/mL",
                },
            ],
        )
        assert response.status_code == 201, response.text

        # Add follow-up visit with imaging
        response = await client.post(
            f"/api/v1/longitudinal/episodes/{episode_id}/visits",
            json={
                "visit_type": "followup",
                "visit_date": datetime.utcnow().isoformat(),
                "notes": "Follow-up imaging",
                "imaging_study_id": imaging_b.id,
            },
        )
        assert response.status_code == 201, response.text
        visit_b_id = response.json()["id"]

        # Timeline
        response = await client.get(f"/api/v1/longitudinal/episodes/{episode_id}/timeline")
        assert response.status_code == 200, response.text
        timeline = response.json()
        assert len(timeline) == 2
        assert timeline[0]["metrics"][0]["metric_key"] == "mmse"
        assert timeline[0]["imaging_available"] is True
        assert timeline[1]["imaging_available"] is True

        # Add follow-up metrics with decline
        response = await client.post(
            f"/api/v1/longitudinal/visits/{visit_b_id}/metrics",
            params={"episode_id": episode_id},
            json=[
                {
                    "metric_type": "cognitive",
                    "metric_key": "mmse",
                    "metric_value": 22,
                    "unit": "score",
                }
            ],
        )
        assert response.status_code == 201, response.text

        # Trend
        response = await client.get(
            f"/api/v1/longitudinal/episodes/{episode_id}/trend",
            params={"metric_key": "mmse"},
        )
        assert response.status_code == 200, response.text
        trend = response.json()
        assert trend[-1]["metric_value"] == 22

        # Alerts
        response = await client.get(f"/api/v1/longitudinal/episodes/{episode_id}/alerts")
        assert response.status_code == 200, response.text
        alerts = response.json()
        assert alerts, "Expected at least one alert for MMSE decline"
        alert_id = alerts[0]["id"]

        # Progression summary
        response = await client.get(f"/api/v1/longitudinal/episodes/{episode_id}/progression")
        assert response.status_code == 200, response.text
        progression = response.json()
        assert "mmse" in progression["metrics"]
        assert progression["metrics"]["mmse"]["slope"] is not None

        # Acknowledge alert
        response = await client.post(f"/api/v1/longitudinal/alerts/{alert_id}/acknowledge")
        assert response.status_code == 200, response.text
        assert response.json()["acknowledged_at"] is not None

        # Generate longitudinal report (excel)
        response = await client.post(
            f"/api/v1/longitudinal/episodes/{episode_id}/reports",
            json={
                "start_date": (datetime.utcnow() - timedelta(days=7)).isoformat(),
                "end_date": datetime.utcnow().isoformat(),
                "format": "xlsx",
            },
        )
        assert response.status_code == 201, response.text
        report_id = response.json()["id"]

        response = await client.get(f"/api/v1/longitudinal/episodes/{episode_id}/reports")
        assert response.status_code == 200, response.text
        reports = response.json()
        assert len(reports) == 1

        response = await client.get(f"/api/v1/longitudinal/reports/{report_id}/download")
        assert response.status_code == 200, response.text
        assert (
            response.headers.get("content-type")
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Cohort report
        response = await client.post(
            f"/api/v1/longitudinal/episodes/{episode_id}/reports",
            json={
                "report_type": "cohort_patient_vs_average",
                "format": "xlsx",
                "cohort_filters": {"gender": "male"},
            },
        )
        assert response.status_code == 201, response.text
        cohort_report_id = response.json()["id"]
        assert response.json()["summary"]["report_type"] == "cohort_patient_vs_average"
        assert response.json()["heatmap_path"] is not None

        response = await client.get(f"/api/v1/longitudinal/reports/{cohort_report_id}/heatmap")
        assert response.status_code == 200, response.text
        assert response.headers["content-type"] == "image/png"

        # Report schedules
        response = await client.post(
            "/api/v1/longitudinal/reports/schedules",
            json={
                "name": "Weekly summary",
                "episode_id": episode_id,
                "report_type": "summary",
                "schedule_cron": "0 6 * * 1",
            },
        )
        assert response.status_code == 201, response.text
        schedule_id = response.json()["id"]

        response = await client.get("/api/v1/longitudinal/reports/schedules")
        assert response.status_code == 200
        assert any(item["id"] == schedule_id for item in response.json())

        response = await client.patch(
            f"/api/v1/longitudinal/reports/schedules/{schedule_id}",
            json={"status": "paused"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "paused"

        response = await client.post(f"/api/v1/longitudinal/reports/schedules/{schedule_id}/runs")
        assert response.status_code == 201
        run_id = response.json()["id"]

        response = await client.get(f"/api/v1/longitudinal/reports/schedules/{schedule_id}/runs")
        assert response.status_code == 200
        assert any(run["id"] == run_id for run in response.json())

        response = await client.post(f"/api/v1/longitudinal/reports/runs/{run_id}/execute")
        assert response.status_code == 200, response.text
        assert response.json()["status"] in {"success", "failed"}

        # Imaging comparison
        response = await client.get(
            f"/api/v1/longitudinal/episodes/{episode_id}/comparison",
            params={"visit_a": visit_a_id, "visit_b": visit_b_id},
        )
        assert response.status_code == 200, response.text
        comparison = response.json()
        assert comparison["episode_id"] == episode_id
        assert comparison["mean_absolute_difference"] > 0
        assert comparison["heatmap"].startswith("data:image/png;base64,")
    finally:
        settings.REPORTS_DIR = original_reports_dir
        await cleanup()


