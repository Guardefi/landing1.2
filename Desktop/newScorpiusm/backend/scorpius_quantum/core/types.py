"""
Core types and enums for quantum cryptography.
"""

import secrets
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class QuantumAlgorithm(Enum):
    """Quantum-resistant algorithm types."""

    LATTICE_BASED = "lattice_based"
    HASH_BASED = "hash_based"
    CODE_BASED = "code_based"
    MULTIVARIATE = "multivariate"
    ISOGENY_BASED = "isogeny_based"
    SYMMETRIC = "symmetric"


class SecurityLevel(Enum):
    """Security levels against quantum attacks."""

    LEVEL_1 = 1  # Equivalent to AES-128
    LEVEL_3 = 3  # Equivalent to AES-192
    LEVEL_5 = 5  # Equivalent to AES-256


class KeyStatus(Enum):
    """Key lifecycle status."""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    COMPROMISED = "compromised"


class OperationStatus(Enum):
    """Operation execution status."""

    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    TIMEOUT = "timeout"


@dataclass
class QuantumKey:
    """Quantum-resistant cryptographic key."""

    algorithm: QuantumAlgorithm
    security_level: SecurityLevel
    public_key: bytes
    private_key: bytes | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    creation_time: datetime = field(default_factory=datetime.now)
    expiry_time: datetime | None = None
    usage_count: int = 0
    max_usage: int | None = None
    status: KeyStatus = KeyStatus.ACTIVE
    key_id: str = field(default_factory=lambda: secrets.token_hex(16))

    def is_expired(self) -> bool:
        """Check if key is expired."""
        if self.expiry_time:
            return datetime.now() > self.expiry_time
        return False

    def is_overused(self) -> bool:
        """Check if key has exceeded usage limit."""
        if self.max_usage:
            return self.usage_count >= self.max_usage
        return False

    def is_valid(self) -> bool:
        """Check if key is valid for use."""
        return (
            self.status == KeyStatus.ACTIVE
            and not self.is_expired()
            and not self.is_overused()
        )

    def increment_usage(self) -> None:
        """Increment usage counter."""
        self.usage_count += 1


@dataclass
class QuantumSignature:
    """Quantum-resistant digital signature."""

    algorithm: QuantumAlgorithm
    signature: bytes
    public_key: bytes
    message_hash: bytes
    timestamp: datetime = field(default_factory=datetime.now)
    verification_data: dict[str, Any] = field(default_factory=dict)
    signature_id: str = field(default_factory=lambda: secrets.token_hex(16))


@dataclass
class QuantumEncryptionResult:
    """Result of quantum-resistant encryption."""

    algorithm: QuantumAlgorithm
    ciphertext: bytes
    public_key: bytes
    nonce: bytes
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    encryption_id: str = field(default_factory=lambda: secrets.token_hex(16))


@dataclass
class QuantumChannel:
    """Quantum communication channel information."""

    channel_id: str
    alice_id: str
    bob_id: str
    shared_key: bytes
    key_length: int
    error_rate: float
    efficiency: float
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "active"


@dataclass
class PerformanceMetrics:
    """Performance monitoring metrics."""

    operation_type: str
    algorithm: QuantumAlgorithm
    security_level: SecurityLevel
    execution_time: float
    memory_usage: int
    cpu_usage: float
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    error_message: str | None = None
