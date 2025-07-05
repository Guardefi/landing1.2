import os
import secrets
from typing import Dict, List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable loading"""

    # API Configuration
    API_KEY: str = secrets.token_urlsafe(32)
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*",
    ]
    DEBUG: bool = True

    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "honeypot_detector"

    # Blockchain RPC URLs
    ETHEREUM_RPC_URL: str = "https://eth-mainnet.g.alchemy.com/v2/your-key"
    BSC_RPC_URL: str = "https://bsc-dataseed.binance.org/"

    # Blockchain Explorer API Keys
    ETHERSCAN_API_KEY: str = ""
    BSCSCAN_API_KEY: str = ""

    # ML Configuration
    MODEL_UPDATE_INTERVAL: int = 3600  # seconds

    # Detector Configuration
    DEFAULT_CHAIN_ID: int = 1
    DEEP_ANALYSIS_TIMEOUT: int = 60  # seconds

    # Cache Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600  # seconds

    # Worker Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # Service Configuration
    SERVICE_NAME: str = "Enterprise Honeypot Detector"
    SERVICE_VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


# Generate .env.example if it doesn't exist
def generate_env_example():
    """Generate .env.example file with settings placeholder"""
    env_example_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), ".env.example"
    )

    if not os.path.exists(env_example_path):
        with open(env_example_path, "w") as f:
            f.write("# API Configuration\n")
            f.write("API_KEY=your-api-key-here\n")
            f.write('ALLOWED_ORIGINS=["*"]\n')
            f.write("DEBUG=false\n\n")

            f.write("# Database\n")
            f.write("MONGODB_URL=mongodb://mongo:27017\n")
            f.write("DATABASE_NAME=honeypot_detector\n\n")

            f.write("# Blockchain RPC URLs\n")
            f.write("ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/your-key\n")
            f.write("BSC_RPC_URL=https://bsc-dataseed.binance.org/\n\n")

            f.write("# Blockchain Explorer API Keys\n")
            f.write("ETHERSCAN_API_KEY=your-etherscan-api-key\n")
            f.write("BSCSCAN_API_KEY=your-bscscan-api-key\n\n")

            f.write("# ML Configuration\n")
            f.write("MODEL_UPDATE_INTERVAL=3600\n\n")

            f.write("# Cache Configuration\n")
            f.write("REDIS_URL=redis://redis:6379/0\n")
            f.write("CACHE_TTL=3600\n\n")

            f.write("# Worker Configuration\n")
            f.write("CELERY_BROKER_URL=redis://redis:6379/1\n")
            f.write("CELERY_RESULT_BACKEND=redis://redis:6379/1\n")


# Generate .env.example on import
generate_env_example()
