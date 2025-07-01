"""
Scorpius Bridge Configuration Settings
Production-ready configuration management with environment variables.
"""

from decimal import Decimal

from pydantic import Field
from pydantic_settings import BaseSettings


class BridgeSettings(BaseSettings):
    """Configuration settings for the Scorpius Bridge Network."""

    # =============================================================================
    # DATABASE CONFIGURATION
    # =============================================================================
    database_url: str = Field(
        default="postgresql+asyncpg://scorpius:password@localhost/scorpius_bridge",
        description="Database connection URL",
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for caching",
    )

    # =============================================================================
    # BLOCKCHAIN RPC ENDPOINTS
    # =============================================================================
    ethereum_rpc: str = Field(
        default="https://mainnet.infura.io/v3/YOUR_KEY",
        description="Ethereum mainnet RPC URL",
    )
    polygon_rpc: str = Field(
        default="https://polygon-rpc.com", description="Polygon mainnet RPC URL"
    )
    bsc_rpc: str = Field(
        default="https://bsc-dataseed.binance.org", description="BSC mainnet RPC URL"
    )
    arbitrum_rpc: str = Field(
        default="https://arb1.arbitrum.io/rpc", description="Arbitrum One RPC URL"
    )
    optimism_rpc: str = Field(
        default="https://mainnet.optimism.io", description="Optimism mainnet RPC URL"
    )
    avalanche_rpc: str = Field(
        default="https://api.avax.network/ext/bc/C/rpc",
        description="Avalanche C-Chain RPC URL",
    )

    # =============================================================================
    # SECURITY CONFIGURATION
    # =============================================================================
    private_key: str = Field(
        default="",
        description="Private key for signing transactions (use HSM in production)",
    )
    jwt_secret: str = Field(
        default="your-super-secret-jwt-key-change-in-production",
        description="JWT secret for API authentication",
    )
    encryption_key: str = Field(
        default="", description="Key for encrypting sensitive data"
    )

    # =============================================================================
    # BRIDGE OPERATIONAL PARAMETERS
    # =============================================================================
    min_validators: int = Field(
        default=3, description="Minimum number of validators required"
    )
    consensus_threshold: float = Field(
        default=0.67, description="Consensus threshold (67% of validators must agree)"
    )
    transfer_timeout_hours: int = Field(
        default=24, description="Transfer timeout in hours"
    )
    # =============================================================================
    # NETWORK CONFIGURATION
    # =============================================================================
    supported_chains: list[str] = Field(
        default=["ethereum", "polygon", "bsc", "arbitrum", "optimism", "avalanche"],
        description="List of supported blockchain networks",
    )

    # =============================================================================
    # FEES AND LIMITS
    # =============================================================================
    base_bridge_fee_percentage: Decimal = Field(
        default=Decimal("0.003"), description="Base bridge fee percentage (0.3%)"
    )
    min_transfer_amount: Decimal = Field(
        default=Decimal("1.0"), description="Minimum transfer amount in USD equivalent"
    )
    max_transfer_amount: Decimal = Field(
        default=Decimal("1000000.0"),
        description="Maximum transfer amount in USD equivalent",
    )
    daily_transfer_limit: Decimal = Field(
        default=Decimal("10000000.0"),
        description="Daily transfer limit per user in USD equivalent",
    )

    # =============================================================================
    # PERFORMANCE AND SCALING
    # =============================================================================
    max_concurrent_transfers: int = Field(
        default=1000, description="Maximum concurrent transfers"
    )
    batch_size: int = Field(
        default=50, description="Batch size for processing transfers"
    )
    cache_ttl_seconds: int = Field(default=300, description="Cache TTL in seconds")

    # =============================================================================
    # MONITORING AND LOGGING
    # =============================================================================
    log_level: str = Field(default="INFO", description="Logging level")
    enable_metrics: bool = Field(
        default=True, description="Enable Prometheus metrics collection"
    )
    enable_health_checks: bool = Field(
        default=True, description="Enable health check endpoints"
    )

    # =============================================================================
    # EXTERNAL SERVICES
    # =============================================================================
    slack_webhook_url: str | None = Field(
        default=None, description="Slack webhook URL for alerts"
    )
    telegram_bot_token: str | None = Field(
        default=None, description="Telegram bot token for alerts"
    )
    telegram_chat_id: str | None = Field(
        default=None, description="Telegram chat ID for alerts"
    )

    # =============================================================================
    # DEVELOPMENT SETTINGS
    # =============================================================================
    environment: str = Field(
        default="development",
        description="Environment (development, staging, production)",
    )
    debug: bool = Field(default=False, description="Enable debug mode")
    enable_cors: bool = Field(default=True, description="Enable CORS for API")

    class Config:
        env_file = ".env"
        env_prefix = "BRIDGE_"
        case_sensitive = False


# Global settings instance
settings = BridgeSettings()


def get_chain_rpc_url(chain_name: str) -> str:
    """Get RPC URL for a specific chain."""
    rpc_mapping = {
        "ethereum": settings.ethereum_rpc,
        "polygon": settings.polygon_rpc,
        "bsc": settings.bsc_rpc,
        "arbitrum": settings.arbitrum_rpc,
        "optimism": settings.optimism_rpc,
        "avalanche": settings.avalanche_rpc,
    }

    return rpc_mapping.get(chain_name.lower(), "")


def is_production() -> bool:
    """Check if running in production environment."""
    return settings.environment.lower() == "production"


def is_development() -> bool:
    """Check if running in development environment."""
    return settings.environment.lower() == "development"
