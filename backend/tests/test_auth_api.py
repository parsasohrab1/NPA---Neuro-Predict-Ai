"""
Tests for Authentication API endpoints
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User, UserRole
from app.core.security import get_password_hash
from conftest import override_get_current_user, TestUser


@pytest.mark.asyncio
async def test_register_user_success(test_client: AsyncClient, test_session: AsyncSession):
    """Test successful user registration"""
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "full_name": "New User",
        "password": "SecurePass123!",
        "role": "viewer"
    }
    
    response = await test_client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "hashed_password" not in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(test_client: AsyncClient, test_session: AsyncSession):
    """Test registration with duplicate email fails"""
    # Create existing user
    existing_user = User(
        email="existing@example.com",
        username="existing",
        full_name="Existing User",
        hashed_password=get_password_hash("password123"),
        role=UserRole.VIEWER
    )
    test_session.add(existing_user)
    await test_session.commit()
    
    # Try to register with same email
    user_data = {
        "email": "existing@example.com",
        "username": "newuser",
        "full_name": "New User",
        "password": "SecurePass123!",
        "role": "viewer"
    }
    
    response = await test_client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower() or "already" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_success(test_client: AsyncClient, test_session: AsyncSession):
    """Test successful login"""
    # Create user
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=get_password_hash("password123"),
        role=UserRole.DOCTOR,
        is_active=True
    )
    test_session.add(user)
    await test_session.commit()
    
    # Login
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    
    response = await test_client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(test_client: AsyncClient, test_session: AsyncSession):
    """Test login with invalid credentials"""
    login_data = {
        "username": "nonexistent",
        "password": "wrongpassword"
    }
    
    response = await test_client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(test_client: AsyncClient, test_session: AsyncSession):
    """Test getting current user info"""
    test_user = TestUser(user_id=1, role=UserRole.DOCTOR)
    app.dependency_overrides[override_get_current_user(test_user)] = override_get_current_user(test_user)
    
    response = await test_client.get("/api/v1/auth/me")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_logout(test_client: AsyncClient):
    """Test logout endpoint"""
    test_user = TestUser()
    app.dependency_overrides[override_get_current_user(test_user)] = override_get_current_user(test_user)
    
    response = await test_client.post("/api/v1/auth/logout")
    
    assert response.status_code == 200
    assert "message" in response.json()

