"""
Unit Tests for Security Module
"""
import pytest
from datetime import timedelta
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    check_permission
)
from app.models.user import User, UserRole


class TestPasswordHashing:
    """Tests for password hashing"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)
    
    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes"""
        password1 = "password1"
        password2 = "password2"
        
        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)
        
        assert hash1 != hash2


class TestTokenCreation:
    """Tests for JWT token creation"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        data = {"sub": "123"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        data = {"sub": "123"}
        token = create_refresh_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_token_with_custom_expiry(self):
        """Test token with custom expiry"""
        data = {"sub": "123"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=expires_delta)
        
        decoded = decode_token(token)
        assert decoded["sub"] == "123"
        assert "exp" in decoded


class TestTokenValidation:
    """Tests for token validation"""
    
    def test_decode_valid_token(self):
        """Test decoding valid token"""
        data = {"sub": "123", "role": "doctor"}
        token = create_access_token(data)
        decoded = decode_token(token)
        
        assert decoded["sub"] == "123"
        assert decoded["role"] == "doctor"
    
    def test_decode_invalid_token(self):
        """Test decoding invalid token"""
        with pytest.raises(Exception):
            decode_token("invalid_token")
    
    def test_token_expiry(self):
        """Test token expiry"""
        data = {"sub": "123"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(data, expires_delta=expires_delta)
        
        with pytest.raises(Exception):
            decode_token(token)


class TestPermissions:
    """Tests for permission checking"""
    
    def test_admin_has_all_permissions(self):
        """Test that admin has all permissions"""
        admin = User(role=UserRole.ADMIN)
        
        assert check_permission(admin, "admin")
        assert check_permission(admin, "doctor")
        assert check_permission(admin, "nurse")
        assert check_permission(admin, "viewer")
    
    def test_doctor_permissions(self):
        """Test doctor permissions"""
        doctor = User(role=UserRole.DOCTOR)
        
        assert check_permission(doctor, "doctor")
        assert check_permission(doctor, "nurse")
        assert check_permission(doctor, "viewer")
        assert not check_permission(doctor, "admin")
    
    def test_nurse_permissions(self):
        """Test nurse permissions"""
        nurse = User(role=UserRole.NURSE)
        
        assert check_permission(nurse, "nurse")
        assert check_permission(nurse, "viewer")
        assert not check_permission(nurse, "doctor")
        assert not check_permission(nurse, "admin")
    
    def test_viewer_permissions(self):
        """Test viewer permissions"""
        viewer = User(role=UserRole.VIEWER)
        
        assert check_permission(viewer, "viewer")
        assert not check_permission(viewer, "nurse")
        assert not check_permission(viewer, "doctor")
        assert not check_permission(viewer, "admin")

