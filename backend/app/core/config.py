"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, model_validator
from typing import Optional
import os
import secrets


class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "NeuroPredict-AI"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Environment Configuration
    ENVIRONMENT: str = Field(
        default="development",
        description="Application environment: 'development' or 'production'"
    )
    
    DEBUG: bool = Field(
        default=False,
        description="Debug mode. Automatically set to False in production for security."
    )
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database Configuration
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/neuropredict_db"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/neuropredict_db"
    
    # Security
    SECRET_KEY: str = Field(
        ...,
        description="Secret key for JWT token signing. Must be set via SECRET_KEY environment variable.",
        min_length=32
    )
    
    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate that SECRET_KEY is not using the default insecure value"""
        insecure_defaults = [
            "your-secret-key-change-this-in-production",
            "your-super-secret-key-change-this",
            "secret-key",
            "change-me",
            ""
        ]
        if v in insecure_defaults:
            raise ValueError(
                "SECRET_KEY must be set via environment variable and cannot use default/insecure values. "
                "Generate a secure key using: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long for security")
        return v
    
    @field_validator('ENVIRONMENT')
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value"""
        valid_environments = ["development", "production", "staging", "test"]
        if v.lower() not in valid_environments:
            raise ValueError(f"ENVIRONMENT must be one of: {', '.join(valid_environments)}")
        return v.lower()
    
    @model_validator(mode='after')
    def validate_debug_in_production(self):
        """Ensure DEBUG is False in production for security"""
        if self.ENVIRONMENT.lower() == 'production' and self.DEBUG is True:
            raise ValueError(
                "DEBUG=True is not allowed in production environment for security reasons. "
                "Set ENVIRONMENT=development for development mode or DEBUG=False for production."
            )
        return self
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8080"
    ]
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    UPLOAD_DIR: str = "uploads"
    DICOM_DIR: str = "uploads/dicom"
    MRI_DIR: str = "uploads/mri"
    REPORTS_DIR: str = "uploads/reports"
    
    # AI Model Paths
    ALZHEIMER_MODEL_PATH: str = "models/alzheimer_model.pth"
    PARKINSON_MODEL_PATH: str = "models/parkinson_model.pth"
    ENSEMBLE_MODEL_PATH: str = "models/ensemble_model.pth"
    MODEL_REGISTRY_PATH: str = "models/registry.json"
    
    # Model Configuration
    MODEL_CONFIDENCE_THRESHOLD: float = 0.75
    BATCH_SIZE: int = 32
    USE_TRAINED_MODEL: bool = True  # If True, loads trained model from registry
    
    # Training Configuration
    TRAINING_DATA_DIR: Optional[str] = None  # Default: data/data/csv
    TRAIN_RATIO: float = 0.7
    VAL_RATIO: float = 0.15
    TEST_RATIO: float = 0.15
    TRAINING_EPOCHS: int = 100
    TRAINING_BATCH_SIZE: int = 32
    TRAINING_LEARNING_RATE: float = 0.001
    TRAINING_WEIGHT_DECAY: float = 1e-5
    TRAINING_PATIENCE: int = 10
    
    # Redis Configuration (for caching and task queue)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # External Systems Integration
    PACS_SERVER_URL: Optional[str] = None
    EHR_API_URL: Optional[str] = None
    HL7_FHIR_ENDPOINT: Optional[str] = None
    INTEGRATION_HMAC_SECRET: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/neuropredict.log"
    
    # Compliance & Audit
    ENABLE_AUDIT_LOG: bool = True
    AUDIT_LOG_FILE: str = "logs/audit.log"
    
    # Performance
    MAX_CONCURRENT_PREDICTIONS: int = 10
    PREDICTION_TIMEOUT: int = 300  # seconds

    # Rate Limiting Configuration
    # Per-minute limits for IP-based rate limiting (Redis-based)
    RATE_LIMIT_DEFAULT_PER_MINUTE: int = Field(
        default=120,
        description="Default rate limit per IP address per minute for general endpoints"
    )
    # Per-hour limit for authenticated users (by token)
    RATE_LIMIT_USER_PER_HOUR: int = Field(
        default=1000,
        description="Rate limit per authenticated user per hour"
    )
    # Specialized limits for sensitive endpoints
    RATE_LIMIT_LOGIN_PER_MINUTE: int = Field(
        default=10,
        description="Rate limit per IP for login attempts (brute-force protection)"
    )
    RATE_LIMIT_UPLOAD_PER_MINUTE: int = Field(
        default=10,
        description="Rate limit per IP for file upload endpoints"
    )
    RATE_LIMIT_PREDICTION_PER_MINUTE: int = Field(
        default=20,
        description="Rate limit per user for prediction endpoints (resource-intensive)"
    )
    # Rate limiting behavior
    RATE_LIMIT_ENABLED: bool = Field(
        default=True,
        description="Enable/disable rate limiting globally"
    )
    RATE_LIMIT_FAIL_OPEN: bool = Field(
        default=True,
        description="If Redis is unavailable, allow requests (fail open) vs block (fail closed)"
    )

    # Backup & DR
    BACKUP_DIR: str = "backups"
    BACKUP_OFFSITE_DIR: str = "backups_offsite"  # simulate offsite/secondary storage
    BACKUP_FULL_INTERVAL_HOURS: int = 24  # daily full backup
    BACKUP_WAL_INTERVAL_MINUTES: int = 15  # incremental/WAL archiving
    BACKUP_RETENTION_DAYS: int = 14  # keep 7–14 daily copies
    BACKUP_VERIFY_WEEKLY: bool = True
    BACKUP_VERIFY_INTERVAL_DAYS: int = 7
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

