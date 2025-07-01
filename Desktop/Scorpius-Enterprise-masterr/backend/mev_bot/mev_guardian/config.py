"""
MevGuardian Enterprise Configuration
Unified configuration system for both Attack and Guardian modes
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

import yaml


class OperatingMode(Enum):
    """System operating modes"""

    GUARDIAN = "guardian"  # Defensive security mode
    ATTACK = "attack"  # Traditional MEV mode
    HYBRID = "hybrid"  # Both modes enabled


class ThreatLevel(Enum):
    """Threat severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ChainConfig:
    """Blockchain network configuration"""

    chain_id: int
    name: str
    rpc_url: str
    ws_url: Optional[str] = None
    block_time: float = 12.0
    gas_multiplier: float = 1.1
    flashbots_relay: Optional[str] = None
    enabled: bool = True


@dataclass
class DatabaseConfig:
    """Database configuration"""

    url: str
    pool_size: int = 20
    max_overflow: int = 40
    echo: bool = False


@dataclass
class RedisConfig:
    """Redis configuration"""

    url: str
    max_connections: int = 100
    decode_responses: bool = True


@dataclass
class GuardianConfig:
    """Guardian mode specific configuration"""

    # Threat Detection
    threat_confidence_threshold: float = 0.8
    alert_channels: List[str] = field(default_factory=lambda: ["webhook", "discord"])
    honeypot_scan_interval: int = 30
    threat_retention_hours: int = 168  # 1 week

    # Simulation Settings
    simulation_fork_provider: str = "tenderly"
    max_concurrent_simulations: int = 5
    simulation_cleanup_hours: int = 24
    fork_blocks_behind: int = 100

    # Mempool Surveillance
    mempool_batch_size: int = 1000
    surveillance_chains: List[int] = field(default_factory=lambda: [1, 137, 42161, 56])
    monitored_protocols: List[str] = field(
        default_factory=lambda: [
            "uniswap_v2",
            "uniswap_v3",
            "sushiswap",
            "curve",
            "balancer",
            "aave",
            "compound",
            "makerdao",
            "yearn",
        ]
    )

    # Forensic Analysis
    max_replay_blocks: int = 1000
    forensic_data_retention_days: int = 90
    pattern_learning_enabled: bool = True


@dataclass
class AttackConfig:
    """Attack mode specific configuration"""

    # Trading Settings
    profit_threshold_eth: float = 0.01
    max_gas_price_gwei: int = 150
    max_position_size_eth: float = 10.0
    stop_loss_percentage: float = 5.0

    # Strategy Settings
    enabled_strategies: List[str] = field(
        default_factory=lambda: [
            "flashloan_arbitrage",
            "sandwich_attack",
            "liquidation_bot",
        ]
    )

    # Flash Loan Providers
    flashloan_providers: List[str] = field(
        default_factory=lambda: ["aave", "maker", "dydx", "balancer"]
    )

    # MEV Protection
    mev_protection_enabled: bool = True
    preferred_relays: List[str] = field(
        default_factory=lambda: ["flashbots", "eden", "bloxroute"]
    )


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""

    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    grafana_enabled: bool = False

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    log_file_enabled: bool = True
    log_file_path: str = "logs/mev_guardian.log"
    log_max_size_mb: int = 100
    log_backup_count: int = 5

    # Health Checks
    health_check_interval: int = 30
    metrics_retention_hours: int = 24


@dataclass
class SecurityConfig:
    """Security configuration"""

    # Authentication
    api_key_required: bool = True
    jwt_secret_key: Optional[str] = None
    token_expiry_hours: int = 24

    # Rate Limiting
    rate_limit_enabled: bool = True
    requests_per_minute: int = 100
    burst_limit: int = 200

    # Data Protection
    encrypt_sensitive_data: bool = True
    audit_log_enabled: bool = True

    # Private Key Management (Attack Mode)
    use_kms: bool = False
    kms_key_id: Optional[str] = None
    private_key: Optional[str] = None  # Dev only


@dataclass
class MevGuardianConfig:
    """Main MevGuardian configuration"""

    # Core Settings
    mode: OperatingMode = OperatingMode.GUARDIAN
    debug: bool = False
    version: str = "1.0.0"

    # Network Configuration
    chains: Dict[int, ChainConfig] = field(default_factory=dict)

    # Database Configuration
    database: DatabaseConfig = None
    redis: RedisConfig = None

    # Mode-specific Configuration
    guardian: GuardianConfig = field(default_factory=GuardianConfig)
    attack: AttackConfig = field(default_factory=AttackConfig)

    # System Configuration
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)

    # External Services
    tenderly_access_key: Optional[str] = None
    discord_webhook_url: Optional[str] = None
    telegram_bot_token: Optional[str] = None

    @classmethod
    def from_env(cls) -> "MevGuardianConfig":
        """Create configuration from environment variables"""

        # Core settings
        mode = OperatingMode(os.getenv("MODE", "guardian"))
        debug = os.getenv("DEBUG", "false").lower() == "true"

        # Database
        database = DatabaseConfig(
            url=os.getenv(
                "DATABASE_URL", "postgresql://user:pass@localhost/mev_guardian"
            ),
            pool_size=int(os.getenv("DB_POOL_SIZE", "20")),
            echo=debug,
        )

        # Redis
        redis = RedisConfig(
            url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "100")),
        )

        # Chains
        chains = {}

        # Ethereum Mainnet
        if eth_rpc := os.getenv("RPC_URL_ETHEREUM"):
            chains[1] = ChainConfig(
                chain_id=1,
                name="ethereum",
                rpc_url=eth_rpc,
                ws_url=os.getenv("WS_URL_ETHEREUM"),
                flashbots_relay="https://relay.flashbots.net",
            )

        # Polygon
        if polygon_rpc := os.getenv("RPC_URL_POLYGON"):
            chains[137] = ChainConfig(
                chain_id=137,
                name="polygon",
                rpc_url=polygon_rpc,
                ws_url=os.getenv("WS_URL_POLYGON"),
                block_time=2.0,
            )

        # Arbitrum
        if arbitrum_rpc := os.getenv("RPC_URL_ARBITRUM"):
            chains[42161] = ChainConfig(
                chain_id=42161,
                name="arbitrum",
                rpc_url=arbitrum_rpc,
                ws_url=os.getenv("WS_URL_ARBITRUM"),
                block_time=0.25,
            )

        # Guardian configuration
        guardian = GuardianConfig(
            threat_confidence_threshold=float(
                os.getenv("THREAT_DETECTION_THRESHOLD", "0.8")
            ),
            simulation_fork_provider=os.getenv("SIMULATION_FORK_PROVIDER", "tenderly"),
            honeypot_scan_interval=int(os.getenv("HONEYPOT_SCAN_INTERVAL", "30")),
        )

        # Attack configuration
        attack = AttackConfig(
            profit_threshold_eth=float(os.getenv("MEV_PROFIT_THRESHOLD", "0.01")),
            max_gas_price_gwei=int(os.getenv("MAX_GAS_PRICE_GWEI", "150")),
            mev_protection_enabled=os.getenv("MEV_PROTECTION_ENABLED", "true").lower()
            == "true",
        )

        # Monitoring
        monitoring = MonitoringConfig(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            prometheus_enabled=os.getenv("PROMETHEUS_ENABLED", "true").lower()
            == "true",
        )

        # Security
        security = SecurityConfig(
            api_key_required=os.getenv("API_KEY_REQUIRED", "true").lower() == "true",
            jwt_secret_key=os.getenv("JWT_SECRET_KEY"),
            private_key=os.getenv("PRIVATE_KEY"),
            use_kms=os.getenv("USE_KMS", "false").lower() == "true",
            kms_key_id=os.getenv("KMS_KEY_ID"),
        )

        return cls(
            mode=mode,
            debug=debug,
            chains=chains,
            database=database,
            redis=redis,
            guardian=guardian,
            attack=attack,
            monitoring=monitoring,
            security=security,
            tenderly_access_key=os.getenv("TENDERLY_ACCESS_KEY"),
            discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL"),
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
        )

    @classmethod
    def from_yaml(cls, file_path: str) -> "MevGuardianConfig":
        """Load configuration from YAML file"""
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        # Convert nested dicts to dataclasses
        if "chains" in data:
            chains = {}
            for chain_id, chain_data in data["chains"].items():
                chains[int(chain_id)] = ChainConfig(**chain_data)
            data["chains"] = chains

        if "database" in data:
            data["database"] = DatabaseConfig(**data["database"])

        if "redis" in data:
            data["redis"] = RedisConfig(**data["redis"])

        if "guardian" in data:
            data["guardian"] = GuardianConfig(**data["guardian"])

        if "attack" in data:
            data["attack"] = AttackConfig(**data["attack"])

        if "monitoring" in data:
            data["monitoring"] = MonitoringConfig(**data["monitoring"])

        if "security" in data:
            data["security"] = SecurityConfig(**data["security"])

        return cls(**data)

    def to_yaml(self, file_path: str) -> None:
        """Save configuration to YAML file"""
        # Convert dataclasses to dicts for serialization
        data = {
            "mode": self.mode.value,
            "debug": self.debug,
            "version": self.version,
            "chains": (
                {
                    str(k): {
                        "chain_id": v.chain_id,
                        "name": v.name,
                        "rpc_url": v.rpc_url,
                        "ws_url": v.ws_url,
                        "block_time": v.block_time,
                        "gas_multiplier": v.gas_multiplier,
                        "flashbots_relay": v.flashbots_relay,
                        "enabled": v.enabled,
                    }
                    for k, v in self.chains.items()
                }
                if self.chains
                else {}
            ),
            "database": (
                {
                    "url": self.database.url,
                    "pool_size": self.database.pool_size,
                    "max_overflow": self.database.max_overflow,
                    "echo": self.database.echo,
                }
                if self.database
                else {}
            ),
            "redis": (
                {
                    "url": self.redis.url,
                    "max_connections": self.redis.max_connections,
                    "decode_responses": self.redis.decode_responses,
                }
                if self.redis
                else {}
            ),
        }

        with open(file_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, indent=2)

    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []

        # Check required fields based on mode
        if self.mode in [OperatingMode.GUARDIAN, OperatingMode.HYBRID]:
            if not self.chains:
                errors.append(
                    "At least one chain configuration required for Guardian mode"
                )

        if self.mode in [OperatingMode.ATTACK, OperatingMode.HYBRID]:
            if not self.security.private_key and not self.security.use_kms:
                errors.append(
                    "Private key or KMS configuration required for Attack mode"
                )

        # Validate chain configurations
        for chain_id, chain in self.chains.items():
            if not chain.rpc_url:
                errors.append(f"RPC URL required for chain {chain_id}")

        # Validate database
        if not self.database or not self.database.url:
            errors.append("Database configuration required")

        # Validate redis
        if not self.redis or not self.redis.url:
            errors.append("Redis configuration required")

        return errors

    def get_enabled_chains(self) -> Dict[int, ChainConfig]:
        """Get only enabled chain configurations"""
        return {k: v for k, v in self.chains.items() if v.enabled}


# Global configuration instance
config: Optional[MevGuardianConfig] = None


def load_config(config_file: Optional[str] = None) -> MevGuardianConfig:
    """Load configuration from file or environment"""
    global config

    if config_file and os.path.exists(config_file):
        config = MevGuardianConfig.from_yaml(config_file)
    else:
        config = MevGuardianConfig.from_env()

    # Validate configuration
    errors = config.validate()
    if errors:
        raise ValueError(
            f"Configuration validation failed: {
                ', '.join(errors)}"
        )

    return config


def get_config() -> MevGuardianConfig:
    """Get the global configuration instance"""
    global config
    if config is None:
        config = load_config()
    return config
