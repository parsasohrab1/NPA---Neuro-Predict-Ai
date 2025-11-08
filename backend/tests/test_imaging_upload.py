import io
from datetime import date, datetime
from pathlib import Path
from typing import Tuple

import numpy as np
import pytest
import pydicom
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.security import get_current_active_user
from app.db.session import Base, get_db
from app.main import app
from app.models.imaging import ImagingStudy
from app.models.patient import Gender, Patient


class DummyUser:
    id = 1
    role = "doctor"
    is_active = True


async def override_current_user():
    return DummyUser()


async def create_test_client(tmp_path: Path) -> Tuple[AsyncClient, async_sessionmaker[AsyncSession]]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_current_user

    original_upload_dir = settings.UPLOAD_DIR
    original_dicom_dir = settings.DICOM_DIR

    storage_root = tmp_path / "storage"
    settings.UPLOAD_DIR = str(storage_root)
    settings.DICOM_DIR = str(storage_root / "dicom")
    Path(settings.DICOM_DIR).mkdir(parents=True, exist_ok=True)

    transport = ASGITransport(app=app, lifespan="auto")
    client = AsyncClient(transport=transport, base_url="http://test")

    async def cleanup():
        await client.aclose()
        await engine.dispose()
        app.dependency_overrides.clear()
        settings.UPLOAD_DIR = original_upload_dir
        settings.DICOM_DIR = original_dicom_dir

    client._cleanup = cleanup  # type: ignore[attr-defined]
    return client, session_factory


def create_dicom_file() -> bytes:
    """Generate a minimal valid DICOM file in-memory for testing."""
    file_meta = pydicom.dataset.Dataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.MRImageStorage
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

    ds = pydicom.dataset.FileDataset(
        "test", {}, file_meta=file_meta, preamble=b"\x00" * 128
    )
    ds.PatientID = "TESTPATIENT"
    ds.StudyInstanceUID = pydicom.uid.generate_uid()
    ds.StudyDate = datetime.utcnow().strftime("%Y%m%d")
    ds.Modality = "MR"
    ds.Rows = 64
    ds.Columns = 64
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 0
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    pixel_array = (np.zeros((64, 64), dtype=np.uint16)).tobytes()
    ds.PixelData = pixel_array

    buffer = io.BytesIO()
    ds.save_as(buffer)
    buffer.seek(0)
    return buffer.read()


@pytest.mark.asyncio
async def test_upload_dicom_creates_imaging_study(tmp_path):
    client, session_factory = await create_test_client(tmp_path)

    try:
        async with session_factory() as session:
            patient = Patient(
                patient_id="PT-001",
                first_name="Test",
                last_name="Patient",
                date_of_birth=date(1980, 1, 1),
                gender=Gender.MALE,
            )
            session.add(patient)
            await session.commit()
            await session.refresh(patient)
            patient_id = patient.id

        dicom_bytes = create_dicom_file()
        files = {
            "file": ("test.dcm", dicom_bytes, "application/dicom"),
        }
        data = {"patient_id": str(patient_id)}

        response = await client.post("/api/v1/imaging/dicom", files=files, data=data)
        assert response.status_code == 201, response.text

        payload = response.json()
        assert payload["imaging_study_id"] > 0
        assert payload["study_id"]
        assert payload["metadata"]["modality"] == "MR"

        stored_path = Path(payload["dicom_path"])
        assert stored_path.exists()

        async with session_factory() as session:
            result = await session.execute(select(ImagingStudy))
            study = result.scalar_one()
            assert study.study_id == payload["study_id"]
            assert study.medical_record_id == payload["medical_record_id"]
    finally:
        await client._cleanup()  # type: ignore[attr-defined]


