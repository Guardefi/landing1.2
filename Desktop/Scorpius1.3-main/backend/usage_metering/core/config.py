"""
Configuration settings for usage metering service
"""

import os
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Service configuration
    service_name: str = "usage-metering"
    debug: bool = False

    # Database configuration
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 2  # Use different DB for usage data

    # Stripe configuration
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    stripe_publishable_key: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")

    # JWT configuration
    jwt_secret: str = os.getenv("JWT_SECRET", "changeme-in-production")
    jwt_algorithm: str = "HS256"

    # Usage configuration
    usage_reset_frequency: str = "monthly"  # monthly, daily
    default_plan: str = "free"

    # Metrics configuration
    metrics_retention_days: int = 90
    export_batch_size: int = 1000

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 1000
    rate_limit_window: int = 3600  # 1 hour

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    """Get cached settings instance"""
    return Settings()
