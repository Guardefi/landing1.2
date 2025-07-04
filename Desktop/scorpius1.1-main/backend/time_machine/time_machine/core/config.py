"""
Time Machine Configuration Management
Enterprise-grade configuration with environment variable support
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration settings"""

    url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./time_machine.db")
    )
    pool_size: int = field(
        default_factory=lambda: int(os.getenv("DATABASE_POOL_SIZE", "10"))
    )
    max_overflow: int = field(
        default_factory=lambda: int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
    )
    echo: bool = field(
        default_factory=lambda: os.getenv("DATABASE_ECHO", "false").lower() == "true"
    )


@dataclass
class RedisConfig:
    """Redis configuration settings"""

    url: str = field(
        default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379/0")
    )
    max_connections: int = field(
        default_factory=lambda: int(os.getenv("REDIS_MAX_CONNECTIONS", "10"))
    )
    socket_timeout: int = field(
        default_factory=lambda: int(os.getenv("REDIS_SOCKET_TIMEOUT", "5"))
    )


@dataclass
class BlockchainConfig:
    """Blockchain RPC configuration"""

    eth_rpc_url: str = field(default_factory=lambda: os.getenv("ETH_RPC_URL", ""))
    eth_ws_url: str = field(default_factory=lambda: os.getenv("ETH_WS_URL", ""))
    polygon_rpc_url: str = field(
        default_factory=lambda: os.getenv("POLYGON_RPC_URL", "")
    )
    bsc_rpc_url: str = field(default_factory=lambda: os.getenv("BSC_RPC_URL", ""))
    etherscan_api_key: str = field(
        default_factory=lambda: os.getenv("ETHERSCAN_API_KEY", "")
    )
    polygonscan_api_key: str = field(
        default_factory=lambda: os.getenv("POLYGONSCAN_API_KEY", "")
    )
    bscscan_api_key: str = field(
        default_factory=lambda: os.getenv("BSCSCAN_API_KEY", "")
    )


@dataclass
class SecurityConfig:
    """Security configuration settings"""

    secret_key: str = field(
        default_factory=lambda: os.getenv(
            "SECRET_KEY", "dev-secret-key-change-in-production"
        )
    )
    jwt_secret_key: str = field(
        default_factory=lambda: os.getenv(
            "JWT_SECRET_KEY", "dev-jwt-secret-change-in-production"
        )
    )
    jwt_access_token_expire_minutes: int = field(
        default_factory=lambda: int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    )
    jwt_refresh_token_expire_days: int = field(
        default_factory=lambda: int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    )
    cors_origins: List[str] = field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
        ]
    )


@dataclass
class ServerConfig:
    """Server configuration settings"""

    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    workers: int = field(default_factory=lambda: int(os.getenv("WORKERS", "4")))
    reload: bool = field(
        default_factory=lambda: os.getenv("APP_ENV", "development") == "development"
    )
    debug: bool = field(
        default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true"
    )


@dataclass
class LoggingConfig:
    """Logging configuration settings"""

    level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    format: str = field(default_factory=lambda: os.getenv("LOG_FORMAT", "json"))
    log_file: str = field(
        default_factory=lambda: os.getenv("LOG_FILE", "logs/time_machine.log")
    )
    error_log_file: str = field(
        default_factory=lambda: os.getenv(
            "ERROR_LOG_FILE", "logs/time_machine.error.log"
        )
    )
    max_file_size: str = field(
        default_factory=lambda: os.getenv("LOG_MAX_FILE_SIZE", "10MB")
    )
    backup_count: int = field(
        default_factory=lambda: int(os.getenv("LOG_BACKUP_COUNT", "5"))
    )


@dataclass
class StorageConfig:
    """Storage configuration settings"""

    storage_path: str = field(
        default_factory=lambda: os.getenv("STORAGE_PATH", "./store")
    )
    snapshots_path: str = field(
        default_factory=lambda: os.getenv("SNAPSHOTS_PATH", "./store/snapshots")
    )
    bundles_path: str = field(
        default_factory=lambda: os.getenv("BUNDLES_PATH", "./store/bundles")
    )
    max_snapshot_size: str = field(
        default_factory=lambda: os.getenv("MAX_SNAPSHOT_SIZE", "100MB")
    )
    cleanup_interval_hours: int = field(
        default_factory=lambda: int(os.getenv("CLEANUP_INTERVAL_HOURS", "24"))
    )


@dataclass
class MonitoringConfig:
    """Monitoring and metrics configuration"""

    enable_metrics: bool = field(
        default_factory=lambda: os.getenv("ENABLE_METRICS", "true").lower() == "true"
    )
    metrics_port: int = field(
        default_factory=lambda: int(os.getenv("METRICS_PORT", "8001"))
    )
    health_check_interval: int = field(
        default_factory=lambda: int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))
    )
    enable_tracing: bool = field(
        default_factory=lambda: os.getenv("ENABLE_TRACING", "false").lower() == "true"
    )


@dataclass
class FeatureFlags:
    """Feature flags for enabling/disabling functionality"""

    enable_demo_data: bool = field(
        default_factory=lambda: os.getenv("ENABLE_DEMO_DATA", "true").lower() == "true"
    )
    enable_real_time_monitoring: bool = field(
        default_factory=lambda: os.getenv("ENABLE_REAL_TIME_MONITORING", "true").lower()
        == "true"
    )
    enable_gas_optimization: bool = field(
        default_factory=lambda: os.getenv("ENABLE_GAS_OPTIMIZATION", "true").lower()
        == "true"
    )
    enable_security_scanning: bool = field(
        default_factory=lambda: os.getenv("ENABLE_SECURITY_SCANNING", "true").lower()
        == "true"
    )
    enable_webhooks: bool = field(
        default_factory=lambda: os.getenv("ENABLE_WEBHOOKS", "false").lower() == "true"
    )
    enable_rate_limiting: bool = field(
        default_factory=lambda: os.getenv("ENABLE_RATE_LIMITING", "true").lower()
        == "true"
    )


@dataclass
class TimeMachineConfig:
    """Main configuration class combining all settings"""

    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "time-machine"))
    app_version: str = field(default_factory=lambda: os.getenv("APP_VERSION", "1.0.0"))
    app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))

    # Configuration sections
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    blockchain: BlockchainConfig = field(default_factory=BlockchainConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    features: FeatureFlags = field(default_factory=FeatureFlags)

    def __post_init__(self):
        """Validate configuration and create necessary directories"""
        self._validate_config()
        self._create_directories()

    def _validate_config(self):
        """Validate critical configuration values"""
        if self.app_env == "production":
            if self.security.secret_key == "dev-secret-key-change-in-production":
                raise ValueError("SECRET_KEY must be changed in production environment")
            if self.security.jwt_secret_key == "dev-jwt-secret-change-in-production":
                raise ValueError(
                    "JWT_SECRET_KEY must be changed in production environment"
                )

        # Validate required blockchain settings if features are enabled
        if (
            self.features.enable_real_time_monitoring
            and not self.blockchain.eth_rpc_url
        ):
            raise ValueError(
                "ETH_RPC_URL is required when real-time monitoring is enabled"
            )

    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.storage.storage_path,
            self.storage.snapshots_path,
            self.storage.bundles_path,
            os.path.dirname(self.logging.log_file),
            os.path.dirname(self.logging.error_log_file),
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "TimeMachineConfig":
        """Load configuration from YAML file"""
        with open(yaml_path, "r") as f:
            config_data = yaml.safe_load(f)

        # Override with environment variables
        return cls(**config_data)

    def to_dict(self) -> dict:
        """Convert configuration to dictionary"""
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "app_env": self.app_env,
            "database": self.database.__dict__,
            "redis": self.redis.__dict__,
            "blockchain": self.blockchain.__dict__,
            "security": {
                k: v
                for k, v in self.security.__dict__.items()
                if "secret" not in k.lower()
            },
            "server": self.server.__dict__,
            "logging": self.logging.__dict__,
            "storage": self.storage.__dict__,
            "monitoring": self.monitoring.__dict__,
            "features": self.features.__dict__,
        }

    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.app_env == "production"

    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.app_env == "development"

    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self.app_env == "testing"


# Global configuration instance
config = TimeMachineConfig()


def get_config() -> TimeMachineConfig:
    """Get the global configuration instance"""
    return config


def reload_config():
    """Reload configuration from environment variables"""
    global config
    config = TimeMachineConfig()
    return config
