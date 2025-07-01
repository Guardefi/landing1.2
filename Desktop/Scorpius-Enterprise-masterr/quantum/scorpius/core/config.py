"""
Enterprise Configuration Management
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


@dataclass
class QuantumConfig:
    """Quantum cryptography configuration."""

    default_algorithm: str = "lattice_based"
    default_security_level: int = 3
    key_rotation_interval: int = 86400  # 24 hours
    enable_quantum_key_distribution: bool = True
    lattice_parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityConfig:
    """Security engine configuration."""

    enable_ai_detection: bool = True
    enable_mev_protection: bool = True
    enable_formal_verification: bool = True
    threat_intelligence_feeds: list = field(default_factory=list)
    ai_model_path: Optional[str] = None


@dataclass
class AnalyticsConfig:
    """Analytics engine configuration."""

    retention_days: int = 365
    enable_real_time_analytics: bool = True
    export_formats: list = field(default_factory=lambda: ["json", "csv", "pdf"])
    dashboard_refresh_interval: int = 30


@dataclass
class IntegrationConfig:
    """Integration hub configuration."""

    enable_workflows: bool = True
    max_concurrent_workflows: int = 10
    workflow_timeout: int = 300
    enable_event_streaming: bool = True


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""

    enable_health_checks: bool = True
    health_check_interval: int = 30
    enable_metrics_collection: bool = True
    metrics_retention_days: int = 30
    alert_endpoints: list = field(default_factory=list)


@dataclass
class ScorpiusConfig:
    """Main Scorpius platform configuration."""

    # Module configurations
    quantum_config: QuantumConfig = field(default_factory=QuantumConfig)
    security_config: SecurityConfig = field(default_factory=SecurityConfig)
    analytics_config: AnalyticsConfig = field(default_factory=AnalyticsConfig)
    integration_config: IntegrationConfig = field(default_factory=IntegrationConfig)
    monitoring_config: MonitoringConfig = field(default_factory=MonitoringConfig)

    # Platform settings
    log_level: str = "INFO"
    log_file: Optional[str] = None
    data_directory: str = "./scorpius_data"
    temp_directory: str = "/tmp/scorpius"

    # Enterprise features
    enable_clustering: bool = False
    cluster_nodes: list = field(default_factory=list)
    enable_high_availability: bool = False
    backup_schedule: str = "0 2 * * *"  # Daily at 2 AM

    @classmethod
    def load(cls, config_path: Optional[str] = None, **overrides) -> "ScorpiusConfig":
        """Load configuration from file with overrides."""

        # Default config
        config_data = {}

        # Load from environment variables
        config_data.update(cls._load_from_env())

        # Load from file
        if config_path:
            config_data.update(cls._load_from_file(config_path))

        # Apply overrides
        config_data.update(overrides)

        return cls._create_from_dict(config_data)

    @staticmethod
    def _load_from_env() -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}

        # Map environment variables to config
        env_mapping = {
            "SCORPIUS_LOG_LEVEL": ("log_level", str),
            "SCORPIUS_LOG_FILE": ("log_file", str),
            "SCORPIUS_DATA_DIR": ("data_directory", str),
            "SCORPIUS_ENABLE_CLUSTERING": ("enable_clustering", bool),
            "SCORPIUS_QUANTUM_ALGORITHM": ("quantum_config.default_algorithm", str),
            "SCORPIUS_SECURITY_LEVEL": ("quantum_config.default_security_level", int),
        }

        for env_var, (config_key, config_type) in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                if config_type == bool:
                    value = value.lower() in ("true", "1", "yes", "on")
                elif config_type == int:
                    value = int(value)

                # Handle nested config keys
                if "." in config_key:
                    parts = config_key.split(".")
                    current = config
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = value
                else:
                    config[config_key] = value

        return config

    @staticmethod
    def _load_from_file(config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(path, "r") as f:
            if path.suffix.lower() in (".yml", ".yaml"):
                return yaml.safe_load(f) or {}
            elif path.suffix.lower() == ".json":
                return json.load(f) or {}
            else:
                raise ValueError(f"Unsupported config file format: {path.suffix}")

    @classmethod
    def _create_from_dict(cls, data: Dict[str, Any]) -> "ScorpiusConfig":
        """Create configuration instance from dictionary."""

        # Extract nested configurations
        quantum_data = data.pop("quantum_config", {})
        security_data = data.pop("security_config", {})
        analytics_data = data.pop("analytics_config", {})
        integration_data = data.pop("integration_config", {})
        monitoring_data = data.pop("monitoring_config", {})

        return cls(
            quantum_config=QuantumConfig(**quantum_data),
            security_config=SecurityConfig(**security_data),
            analytics_config=AnalyticsConfig(**analytics_data),
            integration_config=IntegrationConfig(**integration_data),
            monitoring_config=MonitoringConfig(**monitoring_data),
            **data,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "quantum_config": self.quantum_config.__dict__,
            "security_config": self.security_config.__dict__,
            "analytics_config": self.analytics_config.__dict__,
            "integration_config": self.integration_config.__dict__,
            "monitoring_config": self.monitoring_config.__dict__,
            "log_level": self.log_level,
            "log_file": self.log_file,
            "data_directory": self.data_directory,
            "temp_directory": self.temp_directory,
            "enable_clustering": self.enable_clustering,
            "cluster_nodes": self.cluster_nodes,
            "enable_high_availability": self.enable_high_availability,
            "backup_schedule": self.backup_schedule,
        }

    def save(self, config_path: str) -> None:
        """Save configuration to file."""
        path = Path(config_path)

        with open(path, "w") as f:
            if path.suffix.lower() in (".yml", ".yaml"):
                yaml.dump(self.to_dict(), f, default_flow_style=False)
            elif path.suffix.lower() == ".json":
                json.dump(self.to_dict(), f, indent=2)
            else:
                raise ValueError(f"Unsupported config file format: {path.suffix}")
