"""
Tests for Configuration
"""
import pytest
import os
from app.core.config import Settings


def test_settings_defaults():
    """Test that settings have sensible defaults"""
    # Note: This test may fail if SECRET_KEY is required
    # In that case, set it in environment
    os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only-minimum-32-chars")
    
    settings = Settings()
    
    assert settings.APP_NAME == "NeuroPredict-AI"
    assert settings.API_V1_PREFIX == "/api/v1"
    assert isinstance(settings.DEBUG, bool)
    assert isinstance(settings.PORT, int)


def test_environment_validation():
    """Test environment validation"""
    os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only-minimum-32-chars")
    
    # Valid environment
    os.environ["ENVIRONMENT"] = "development"
    settings = Settings()
    assert settings.ENVIRONMENT == "development"
    
    # Invalid environment should raise error
    os.environ["ENVIRONMENT"] = "invalid"
    with pytest.raises(ValueError):
        Settings()


def test_debug_production_validation():
    """Test that DEBUG=True is blocked in production"""
    os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only-minimum-32-chars")
    
    os.environ["ENVIRONMENT"] = "production"
    os.environ["DEBUG"] = "True"
    
    with pytest.raises(ValueError, match="DEBUG=True is not allowed in production"):
        Settings()


def test_secret_key_validation():
    """Test SECRET_KEY validation"""
    # Test with insecure default
    os.environ["SECRET_KEY"] = "your-secret-key-change-this-in-production"
    
    with pytest.raises(ValueError, match="SECRET_KEY must be set"):
        Settings()
    
    # Test with short key
    os.environ["SECRET_KEY"] = "short"
    
    with pytest.raises(ValueError, match="at least 32 characters"):
        Settings()
    
    # Test with valid key
    os.environ["SECRET_KEY"] = "a-very-long-secure-secret-key-for-testing-purposes-only"
    settings = Settings()
    assert len(settings.SECRET_KEY) >= 32

