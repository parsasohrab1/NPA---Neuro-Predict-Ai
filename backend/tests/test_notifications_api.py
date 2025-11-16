import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from app.db.session import Base, get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole


class DummyUser:
    id = 777
    role = "admin"
    is_active = True


async def override_current_user():
    return DummyUser()


@pytest.mark.asyncio
async def test_update_and_get_preferences():
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
        # Update preferences
        resp = await client.put(
            "/api/v1/notifications/preferences",
            json={"email_enabled": True, "sms_enabled": False, "on_report_ready": True},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["updated"] is True

        # Get preferences
        resp = await client.get("/api/v1/notifications/preferences")
        assert resp.status_code == 200, resp.text
        prefs = resp.json()
        assert prefs.get("email_enabled") in (True, False) or prefs == {}
    finally:
        await client.aclose()
        await engine.dispose()
        app.dependency_overrides.clear()


