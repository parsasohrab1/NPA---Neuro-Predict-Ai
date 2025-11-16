import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from app.db.session import Base, get_db
from app.core.security import get_current_user, require_role
from app.models.user import User, UserRole


class DummyUser:
    id = 555
    role = "admin"
    is_active = True


async def override_current_user():
    return DummyUser()


@pytest.mark.asyncio
async def test_create_and_export_dsr():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user

    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")

    try:
        # Create DSR
        resp = await client.post(
            "/api/v1/privacy/dsr",
            json={"request_type": "access", "subject_identifier": "PT-XYZ"},
        )
        assert resp.status_code == 201, resp.text
        dsr_id = resp.json()["id"]

        # Export (admin)
        resp = await client.post(f"/api/v1/privacy/dsr/{dsr_id}/export")
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] in ("completed", "in_progress")
    finally:
        await client.aclose()
        await engine.dispose()
        app.dependency_overrides.clear()


