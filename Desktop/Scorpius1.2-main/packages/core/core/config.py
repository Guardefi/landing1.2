"""
Configuration Management
-----------------------
Environment-aware configuration for Scorpius services.
"""
import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger("scorpius_core.config")


class DatabaseConfig(BaseModel):
    """Database configuration"""
    url: str = Field(default="postgresql+asyncpg://localhost/scorpius")
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)
    pool_timeout: int = Field(default=30)
    pool_recycle: int = Field(default=3600)


class RedisConfig(BaseModel):
    """Redis configuration"""
    url: str = Field(default="redis://localhost:6379")
    db: int = Field(default=0)
    max_connections: int = Field(default=100)
    socket_timeout: float = Field(default=5.0)
    health_check_interval: int = Field(default=30)


class SecurityConfig(BaseModel):
    """Security configuration"""
    jwt_secret: str = Field(default="changeme-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expire_minutes: int = Field(default=60)
    rate_limit_per_minute: int = Field(default=60)
    cors_origins: list = Field(default_factory=lambda: [
        "http://localhost:3000", 
        "http://localhost:3010", 
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3010",
        "http://127.0.0.1:8080"
    ])


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = Field(default="INFO")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    structured: bool = Field(default=True)
    correlation_id_header: str = Field(default="X-Correlation-ID")


class Config(BaseModel):
    """Main configuration object"""
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    
    # Component configs
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables"""
        config_data = {}
        
        # Load from environment
        if db_url := os.getenv("DATABASE_URL"):
            config_data.setdefault("database", {})["url"] = db_url
        if redis_url := os.getenv("REDIS_URL"):
            config_data.setdefault("redis", {})["url"] = redis_url
        if jwt_secret := os.getenv("JWT_SECRET"):
            config_data.setdefault("security", {})["jwt_secret"] = jwt_secret
        if cors_origins := os.getenv("CORS_ORIGINS"):
            config_data.setdefault("security", {})["cors_origins"] = cors_origins.split(",")
            
        # Environment settings
        config_data["environment"] = os.getenv("ENVIRONMENT", "development")
        config_data["debug"] = os.getenv("DEBUG", "false").lower() == "true"
        config_data["host"] = os.getenv("HOST", "0.0.0.0")
        config_data["port"] = int(os.getenv("PORT", "8000"))
        
        return cls(**config_data)
    
    @classmethod
    def from_file(cls, config_path: Path) -> "Config":
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            return cls(**config_data)
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
            return cls()


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def set_config(config: Config) -> None:
    """Set the global configuration instance"""
    global _config
    _config = config
