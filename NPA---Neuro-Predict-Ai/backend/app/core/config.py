"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "NeuroPredict-AI"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database Configuration
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/neuropredict_db"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/neuropredict_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
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
    
    # AI Model Paths
    ALZHEIMER_MODEL_PATH: str = "models/alzheimer_model.pth"
    PARKINSON_MODEL_PATH: str = "models/parkinson_model.pth"
    ENSEMBLE_MODEL_PATH: str = "models/ensemble_model.pth"
    
    # Model Configuration
    MODEL_CONFIDENCE_THRESHOLD: float = 0.75
    BATCH_SIZE: int = 32
    
    # Redis Configuration (for caching and task queue)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # External Systems Integration
    PACS_SERVER_URL: Optional[str] = None
    EHR_API_URL: Optional[str] = None
    HL7_FHIR_ENDPOINT: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/neuropredict.log"
    
    # Compliance & Audit
    ENABLE_AUDIT_LOG: bool = True
    AUDIT_LOG_FILE: str = "logs/audit.log"
    
    # Performance
    MAX_CONCURRENT_PREDICTIONS: int = 10
    PREDICTION_TIMEOUT: int = 300  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

