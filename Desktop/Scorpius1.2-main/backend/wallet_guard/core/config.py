"""
Configuration settings for Wallet Guard service
"""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Service settings
    HOST: str = "0.0.0.0"
    PORT: int = 8085
    DEBUG: bool = False
    WORKERS: int = 4

    # Security settings
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["*"]

    # Database settings
    REDIS_URL: str = "redis://localhost:6380"
    POSTGRES_URL: str = (
        "postgresql://scorpius:scorpius_secure_pass@localhost:5433/scorpius"
    )

    # Chain RPC URLs
    ETHEREUM_RPC: str = "https://eth-mainnet.alchemyapi.io/v2/demo"
    BSC_RPC: str = "https://bsc-dataseed.binance.org/"
    ARBITRUM_RPC: str = "https://arb1.arbitrum.io/rpc"
    BASE_RPC: str = "https://mainnet.base.org"

    # API Keys
    ALCHEMY_API_KEY: str = ""
    INFURA_API_KEY: str = ""

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    DEFAULT_RATE_LIMIT: str = "60/minute"

    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    AUDIT_LOGGING_ENABLED: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
