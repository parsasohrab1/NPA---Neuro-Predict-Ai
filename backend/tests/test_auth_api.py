"""
Tests for Authentication API endpoints
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_register_user_success(test_client: AsyncClient, test_session: AsyncSession):
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "full_name": "New User",
        "password": "SecurePass123!",
        "role": "viewer",
    }

    response = await test_client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(test_client: AsyncClient, test_session: AsyncSession):
    existing_user = User(
        email="existing@example.com",
        username="existing",
        full_name="Existing User",
        hashed_password=get_password_hash("password123"),
        role=UserRole.VIEWER,
    )
    test_session.add(existing_user)
    await test_session.commit()

    response = await test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "existing@example.com",
            "username": "newuser2",
            "full_name": "New User",
            "password": "SecurePass123!",
            "role": "viewer",
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(test_client: AsyncClient, test_session: AsyncSession):
    user = User(
        email="login@example.com",
        username="loginuser",
        full_name="Login User",
        hashed_password=get_password_hash("password123"),
        role=UserRole.DOCTOR,
        is_active=True,
    )
    test_session.add(user)
    await test_session.commit()

    response = await test_client.post(
        "/api/v1/auth/login",
        data={"username": "loginuser", "password": "password123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_invalid_credentials(test_client: AsyncClient):
    response = await test_client.post(
        "/api/v1/auth/login",
        data={"username": "nobody", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(test_client: AsyncClient, auth_headers: dict):
    response = await test_client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_logout(test_client: AsyncClient, auth_headers: dict):
    response = await test_client.post("/api/v1/auth/logout", headers=auth_headers)
    assert response.status_code == 200
