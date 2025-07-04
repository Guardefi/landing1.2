"""Configuration module for Scorpius Bridge"""

import os
from typing import List


class Settings:
    """Application settings"""
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment == "development"
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost:5432/scorpius")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # CORS
    enable_cors: bool = True
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # JWT
    jwt_secret: str = os.getenv("JWT_SECRET", "bridge-secret-key")
    
    # Service
    service_name: str = os.getenv("SERVICE_NAME", "bridge")


# Global settings instance
settings = Settings() 