"""
Scorpius Reporting Service - Configuration Management
Environment-based configuration with validation
"""

import os
from typing import List, Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Service Configuration
    APP_NAME: str = Field(default="Scorpius Reporting Service", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8007, env="API_PORT")
    API_PREFIX: str = Field(default="/v1", env="API_PREFIX")
    
    # Security Configuration
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    API_KEY_HEADER: str = Field(default="X-API-Key", env="API_KEY_HEADER")
    CORS_ORIGINS: str = Field(default="*", env="CORS_ORIGINS")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(',') if origin.strip()]
        return origins if origins else ["*"]
    
    # Database Configuration
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # AWS Configuration
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(None, env="AWS_SECRET_ACCESS_KEY")
    
    # QLDB Configuration
    QLDB_LEDGER_NAME: str = Field(default="scorpius-audit", env="QLDB_LEDGER_NAME")
    QLDB_TABLE_NAME: str = Field(default="report_hashes", env="QLDB_TABLE_NAME")
    
    # Signature Configuration
    SIGNATURE_CERT_PATH: str = Field(default="./certs/signing.crt", env="SIGNATURE_CERT_PATH")
    SIGNATURE_KEY_PATH: str = Field(default="./certs/signing.key", env="SIGNATURE_KEY_PATH")
    SIGNATURE_ALGORITHM: str = Field(default="RS256", env="SIGNATURE_ALGORITHM")
    
    # Storage Configuration
    REPORTS_BASE_PATH: str = Field(default="./reports", env="REPORTS_BASE_PATH")
    TEMP_PATH: str = Field(default="./temp", env="TEMP_PATH")
    MAX_FILE_SIZE: int = Field(default=100 * 1024 * 1024, env="MAX_FILE_SIZE")  # 100MB
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    PROMETHEUS_PORT: int = Field(default=8008, env="PROMETHEUS_PORT")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # External Services
    AUDIT_SERVICE_URL: str = Field(default="http://localhost:8003", env="AUDIT_SERVICE_URL")
    AUTH_SERVICE_URL: str = Field(default="http://localhost:8001", env="AUTH_SERVICE_URL")
    
    # PDF Generation
    PDF_TEMPLATE_PATH: str = Field(default="./templates", env="PDF_TEMPLATE_PATH")
    PDF_FONTS_PATH: str = Field(default="./fonts", env="PDF_FONTS_PATH")
    PDF_WATERMARK_ENABLED: bool = Field(default=True, env="PDF_WATERMARK_ENABLED")
    
    # SARIF Generation
    SARIF_SCHEMA_VERSION: str = Field(default="2.1.0", env="SARIF_SCHEMA_VERSION")
    SARIF_VALIDATION_ENABLED: bool = Field(default=True, env="SARIF_VALIDATION_ENABLED")
    
    # Background Tasks
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")
    
    # Additional Environment Configuration
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    HEALTH_CHECK_TIMEOUT: int = Field(default=30, env="HEALTH_CHECK_TIMEOUT")
    MAX_UPLOAD_SIZE: int = Field(default=10485760, env="MAX_UPLOAD_SIZE")
    MAX_REPORT_SIZE: int = Field(default=52428800, env="MAX_REPORT_SIZE")
    AUDIT_ENABLED: bool = Field(default=True, env="AUDIT_ENABLED")
    AUDIT_PROVIDER: str = Field(default="file", env="AUDIT_PROVIDER")
    AUDIT_LOG_PATH: str = Field(default="./logs/audit.log", env="AUDIT_LOG_PATH")
    METRICS_ENABLED: bool = Field(default=True, env="METRICS_ENABLED")
    METRICS_PATH: str = Field(default="/metrics", env="METRICS_PATH")
    PDF_TIMEOUT: int = Field(default=300, env="PDF_TIMEOUT")
    SARIF_TIMEOUT: int = Field(default=300, env="SARIF_TIMEOUT")
    CLEANUP_INTERVAL: int = Field(default=3600, env="CLEANUP_INTERVAL")
    REPORT_RETENTION_DAYS: int = Field(default=30, env="REPORT_RETENTION_DAYS")
    
    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'LOG_LEVEL must be one of {valid_levels}')
        return v.upper()
    
    @field_validator('SIGNATURE_ALGORITHM')
    @classmethod
    def validate_signature_algorithm(cls, v):
        valid_algorithms = ['RS256', 'RS384', 'RS512', 'ES256', 'ES384', 'ES512']
        if v not in valid_algorithms:
            raise ValueError(f'SIGNATURE_ALGORITHM must be one of {valid_algorithms}')
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_parse_none_str="None"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    CORS_ORIGINS: List[str] = ["*"]


class ProductionSettings(Settings):
    """Production environment settings"""
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = []  # Must be explicitly set in production


class TestingSettings(Settings):
    """Testing environment settings"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    DATABASE_URL: str = "sqlite:///./test.db"
    REDIS_URL: str = "redis://localhost:6379/15"  # Use different Redis DB for tests


def get_environment_settings():
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()
