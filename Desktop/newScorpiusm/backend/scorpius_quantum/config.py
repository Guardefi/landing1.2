"""
Configuration for quantum cryptography engine.
"""

import os
from dataclasses import dataclass


@dataclass
class QuantumConfig:
    """Configuration for quantum cryptography engine."""

    # Security settings
    default_security_level: int = 3
    max_key_usage: int = 1000
    key_expiry_hours: int = 24

    # Performance settings
    enable_caching: bool = True
    max_cached_keys: int = 1000
    enable_performance_monitoring: bool = True

    # Logging
    log_level: str = "INFO"
    log_file: str | None = None

    # Storage
    key_storage_path: str | None = None
    use_secure_memory: bool = True

    # Algorithm preferences
    preferred_lattice_params: str = "moderate"  # conservative, moderate, aggressive
    enable_qkd_simulation: bool = True

    @classmethod
    def from_env(cls) -> "QuantumConfig":
        """Load configuration from environment variables."""
        return cls(
            default_security_level=int(os.getenv("QUANTUM_SECURITY_LEVEL", 3)),
            max_key_usage=int(os.getenv("QUANTUM_MAX_KEY_USAGE", 1000)),
            key_expiry_hours=int(os.getenv("QUANTUM_KEY_EXPIRY_HOURS", 24)),
            enable_caching=os.getenv("QUANTUM_ENABLE_CACHING", "true").lower()
            == "true",
            log_level=os.getenv("QUANTUM_LOG_LEVEL", "INFO"),
            log_file=os.getenv("QUANTUM_LOG_FILE"),
            key_storage_path=os.getenv("QUANTUM_KEY_STORAGE_PATH"),
            preferred_lattice_params=os.getenv("QUANTUM_LATTICE_PARAMS", "moderate"),
            enable_qkd_simulation=os.getenv("QUANTUM_ENABLE_QKD", "true").lower()
            == "true",
        )

    @classmethod
    def development(cls) -> "QuantumConfig":
        """Development configuration with faster, less secure defaults."""
        return cls(
            default_security_level=1,
            max_key_usage=100,
            key_expiry_hours=1,
            enable_caching=False,
            log_level="DEBUG",
            preferred_lattice_params="conservative",
        )

    @classmethod
    def production(cls) -> "QuantumConfig":
        """Production configuration with secure defaults."""
        return cls(
            default_security_level=5,
            max_key_usage=10000,
            key_expiry_hours=168,  # 1 week
            enable_caching=True,
            log_level="WARNING",
            preferred_lattice_params="aggressive",
            use_secure_memory=True,
        )
