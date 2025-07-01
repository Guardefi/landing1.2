"""
Enterprise Reporting Configuration
==================================

Configuration management for the enterprise reporting system.
"""

import os
from pathlib import Path
from typing import List, Optional

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, validator
except ImportError:
    # Fallback for older Pydantic versions
    from pydantic import BaseSettings, Field, validator


class DatabaseConfig(BaseSettings):
    """Database configuration"""
    
    # SQLite configuration for development (change for production)
    database_type: str = Field(default="sqlite", env="DB_TYPE")  # sqlite, postgresql
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    database: str = Field(default="scorpius_reporting.db", env="DB_NAME")
    username: str = Field(default="reporting_user", env="DB_USER")
    password: str = Field(default="", env="DB_PASSWORD")
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    
    @property
    def url(self) -> str:
        """Database connection URL"""
        if self.database_type == "sqlite":
            # Use SQLite for development
            return f"sqlite+aiosqlite:///{self.database}"
        else:
            # Use PostgreSQL for production
            return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class RedisConfig(BaseSettings):
    """Redis configuration for caching and queues"""
    
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    db: int = Field(default=0, env="REDIS_DB")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    @property
    def url(self) -> str:
        """Redis connection URL"""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class SecurityConfig(BaseSettings):
    """Security configuration"""
    
    secret_key: str = Field(
        default="development-secret-key-change-in-production-this-is-not-secure-32-chars-long",
        env="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # PDF signing
    pdf_signing_enabled: bool = Field(default=True, env="PDF_SIGNING_ENABLED")
    pdf_cert_path: Optional[str] = Field(default=None, env="PDF_CERT_PATH")
    pdf_key_path: Optional[str] = Field(default=None, env="PDF_KEY_PATH")
    pdf_cert_password: Optional[str] = Field(default=None, env="PDF_CERT_PASSWORD")
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        if not v:
            raise ValueError("SECRET_KEY is required")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v


class ReportingConfig(BaseSettings):
    """Reporting system configuration"""
    
    # File storage
    reports_dir: Path = Field(default=Path("reports"), env="REPORTS_DIR")
    templates_dir: Path = Field(default=Path("templates"), env="TEMPLATES_DIR")
    static_dir: Path = Field(default=Path("static"), env="STATIC_DIR")
    max_file_size: int = Field(default=100 * 1024 * 1024, env="MAX_FILE_SIZE")  # 100MB
    
    # Report generation
    max_concurrent_reports: int = Field(default=5, env="MAX_CONCURRENT_REPORTS")
    report_timeout_minutes: int = Field(default=30, env="REPORT_TIMEOUT_MINUTES")
    cleanup_expired_reports: bool = Field(default=True, env="CLEANUP_EXPIRED_REPORTS")
    
    # Supported formats
    supported_formats: List[str] = Field(
        default=["pdf", "html", "json", "csv", "sarif", "markdown"],
        env="SUPPORTED_FORMATS"
    )
    
    # Theme configuration
    default_theme: str = Field(default="dark_pro", env="DEFAULT_THEME")
    custom_themes_dir: Optional[Path] = Field(default=None, env="CUSTOM_THEMES_DIR")
    
    # Watermarking
    watermark_enabled: bool = Field(default=True, env="WATERMARK_ENABLED")
    watermark_text: str = Field(default="CONFIDENTIAL", env="WATERMARK_TEXT")
    watermark_opacity: float = Field(default=0.1, env="WATERMARK_OPACITY")
    
    # Performance
    enable_caching: bool = Field(default=True, env="ENABLE_CACHING")
    cache_ttl_minutes: int = Field(default=60, env="CACHE_TTL_MINUTES")
    
    def __post_init__(self):
        """Create directories if they don't exist"""
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.static_dir.mkdir(parents=True, exist_ok=True)
        if self.custom_themes_dir:
            self.custom_themes_dir.mkdir(parents=True, exist_ok=True)


class APIConfig(BaseSettings):
    """API configuration"""
    
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    debug: bool = Field(default=False, env="DEBUG")
    reload: bool = Field(default=False, env="RELOAD")
    
    # CORS
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    cors_methods: List[str] = Field(default=["*"], env="CORS_METHODS")
    cors_headers: List[str] = Field(default=["*"], env="CORS_HEADERS")
    
    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds
    
    # Documentation
    docs_url: str = Field(default="/docs", env="DOCS_URL")
    redoc_url: str = Field(default="/redoc", env="REDOC_URL")
    openapi_url: str = Field(default="/openapi.json", env="OPENAPI_URL")


class LoggingConfig(BaseSettings):
    """Logging configuration"""
    
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # File logging
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    log_max_size: int = Field(default=10 * 1024 * 1024, env="LOG_MAX_SIZE")  # 10MB
    log_backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")
    
    # Structured logging
    structured_logging: bool = Field(default=True, env="STRUCTURED_LOGGING")
    
    # External logging
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    
    @validator("level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()


class MonitoringConfig(BaseSettings):
    """Monitoring and metrics configuration"""
    
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    health_check_enabled: bool = Field(default=True, env="HEALTH_CHECK_ENABLED")
    
    # Tracing
    tracing_enabled: bool = Field(default=False, env="TRACING_ENABLED")
    jaeger_endpoint: Optional[str] = Field(default=None, env="JAEGER_ENDPOINT")


class WebhookConfig(BaseSettings):
    """Webhook configuration"""
    
    enabled: bool = Field(default=False, env="WEBHOOK_ENABLED")
    endpoints: List[str] = Field(default=[], env="WEBHOOK_ENDPOINTS")
    timeout_seconds: int = Field(default=30, env="WEBHOOK_TIMEOUT")
    retry_attempts: int = Field(default=3, env="WEBHOOK_RETRY_ATTEMPTS")
    retry_delay_seconds: int = Field(default=5, env="WEBHOOK_RETRY_DELAY")
    
    # Webhook security
    secret_key: Optional[str] = Field(default=None, env="WEBHOOK_SECRET_KEY")
    signature_header: str = Field(default="X-Signature", env="WEBHOOK_SIGNATURE_HEADER")


class Settings(BaseSettings):
    """Main application settings"""
    
    app_name: str = Field(default="Scorpius Enterprise Reporting", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Component configurations
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    security: SecurityConfig = SecurityConfig()
    reporting: ReportingConfig = ReportingConfig()
    api: APIConfig = APIConfig()
    logging: LoggingConfig = LoggingConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    webhook: WebhookConfig = WebhookConfig()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    @validator("environment")
    def validate_environment(cls, v):
        valid_envs = ["development", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"Environment must be one of {valid_envs}")
        return v.lower()
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == "development"


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """Get global settings instance (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Create settings instance for immediate use
settings = get_settings()


# Environment-specific configuration loading
def load_config(config_file: Optional[str] = None) -> Settings:
    """Load configuration from file or environment"""
    if config_file and os.path.exists(config_file):
        return Settings(_env_file=config_file)
    return Settings()


# Configuration validation
def validate_config(config: Settings) -> List[str]:
    """Validate configuration and return list of issues"""
    issues = []
    
    # Check required directories
    if not config.reporting.templates_dir.exists():
        issues.append(f"Templates directory does not exist: {config.reporting.templates_dir}")
    
    # Check PDF signing configuration
    if config.security.pdf_signing_enabled:
        if not config.security.pdf_cert_path or not os.path.exists(config.security.pdf_cert_path):
            issues.append("PDF signing enabled but certificate path not found")
        if not config.security.pdf_key_path or not os.path.exists(config.security.pdf_key_path):
            issues.append("PDF signing enabled but key path not found")
    
    # Check webhook configuration
    if config.webhook.enabled and not config.webhook.endpoints:
        issues.append("Webhooks enabled but no endpoints configured")
    
    return issues

