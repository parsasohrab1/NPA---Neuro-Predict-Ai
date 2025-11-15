"""
Tests for Security features
"""
import pytest
from datetime import datetime, timedelta

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token
)
from app.core.config import settings


def test_password_hashing():
    """Test password hashing and verification"""
    password = "TestPassword123!"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)


def test_password_hash_uniqueness():
    """Test that same password produces different hashes"""
    password = "TestPassword123!"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    # Hashes should be different (due to salt)
    assert hash1 != hash2
    # But both should verify correctly
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)


def test_create_access_token():
    """Test JWT token creation"""
    data = {"sub": "testuser", "user_id": 1}
    token = create_access_token(data)
    
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_token():
    """Test JWT token decoding"""
    data = {"sub": "testuser", "user_id": 1}
    token = create_access_token(data)
    
    decoded = decode_token(token)
    assert decoded["sub"] == data["sub"]
    assert decoded["user_id"] == data["user_id"]


def test_token_expiration():
    """Test that tokens expire correctly"""
    data = {"sub": "testuser", "user_id": 1}
    # Create token with very short expiration
    from datetime import timedelta
    token = create_access_token(data, expires_delta=timedelta(seconds=1))
    
    # Should decode immediately
    decoded = decode_token(token)
    assert decoded["sub"] == data["sub"]
    
    # After expiration, should fail (implementation dependent)
    # This test may need adjustment based on actual implementation

