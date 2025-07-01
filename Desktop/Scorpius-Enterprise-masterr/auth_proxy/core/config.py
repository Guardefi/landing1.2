"""
Configuration for Auth Proxy Service
"""

from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Auth proxy settings"""

    # Service settings
    HOST: str = "0.0.0.0"
    PORT: int = 8086
    DEBUG: bool = False
    BASE_URL: str = "http://localhost:8086"

    # Security
    JWT_SECRET: str = "your-super-secret-jwt-key-change-in-production"
    CORS_ORIGINS: List[str] = ["*"]

    # Keycloak settings
    KEYCLOAK_SERVER_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "scorpius"
    KEYCLOAK_CLIENT_ID: str = "scorpius-backend"
    KEYCLOAK_CLIENT_SECRET: str = ""

    # Database
    POSTGRES_URL: str = (
        "postgresql://scorpius:scorpius_secure_pass@localhost:5433/scorpius"
    )
    REDIS_URL: str = "redis://localhost:6380"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
