"""
Tests for Configuration
"""
import pytest
import os
from app.core.config import Settings


def test_settings_defaults(monkeypatch):
    """Test that settings have sensible defaults"""
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-for-testing-only-minimum-32-chars")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("DEBUG", "false")
    
    settings = Settings()
    
    assert settings.APP_NAME == "NeuroPredict-AI"
    assert settings.API_V1_PREFIX == "/api/v1"
    assert isinstance(settings.DEBUG, bool)
    assert isinstance(settings.PORT, int)


def test_environment_validation(monkeypatch):
    """Test environment validation"""
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-for-testing-only-minimum-32-chars")
    
    # Valid environment
    monkeypatch.setenv("ENVIRONMENT", "development")
    settings = Settings()
    assert settings.ENVIRONMENT == "development"
    
    # Invalid environment should raise error
    monkeypatch.setenv("ENVIRONMENT", "invalid")
    with pytest.raises(ValueError):
        Settings()


def test_debug_production_validation(monkeypatch):
    """Test that DEBUG=True is blocked in production"""
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-for-testing-only-minimum-32-chars")
    
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DEBUG", "True")
    
    with pytest.raises(ValueError, match="DEBUG=True is not allowed in production"):
        Settings()


def test_secret_key_validation(monkeypatch):
    """Test SECRET_KEY validation"""
    # Isolate from any DEBUG/ENVIRONMENT left in the process environment
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("DEBUG", "false")
    # Test with insecure default
    monkeypatch.setenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    
    with pytest.raises(ValueError, match="SECRET_KEY must be set"):
        Settings()
    
    # Test with short key
    monkeypatch.setenv("SECRET_KEY", "short")
    
    with pytest.raises(ValueError, match="at least 32 characters"):
        Settings()
    
    # Test with valid key
    monkeypatch.setenv("SECRET_KEY", "a-very-long-secure-secret-key-for-testing-purposes-only")
    settings = Settings()
    assert len(settings.SECRET_KEY) >= 32

