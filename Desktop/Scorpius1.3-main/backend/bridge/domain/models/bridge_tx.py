"""Bridge Transaction domain model.

Core entity representing a cross-chain bridge transaction.
Contains pure business logic without external dependencies.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, Optional

from ..errors import InvalidTransferError, SecurityViolationError


class TransferStatus(Enum):
    """Status of a bridge transfer."""

    PENDING = "pending"
    INITIATED = "initiated"
    LOCKED = "locked"
    VALIDATED = "validated"
    MINTED = "minted"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class SecurityLevel(Enum):
    """Security levels for transfers."""

    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"
    QUANTUM_RESISTANT = "quantum_resistant"


@dataclass
class BridgeTransaction:
    """Core bridge transaction entity."""

    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Transfer details
    source_chain: str = ""
    destination_chain: str = ""
    token_address: str = ""
    amount: Decimal = Decimal("0")
    sender_address: str = ""
    recipient_address: str = ""

    # Status and timing
    status: TransferStatus = TransferStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    # Security
    security_level: SecurityLevel = SecurityLevel.STANDARD
    required_confirmations: int = 12
    validator_signatures: Dict[str, str] = field(default_factory=dict)

    # Transaction hashes
    source_tx_hash: Optional[str] = None
    destination_tx_hash: Optional[str] = None

    # Fees
    bridge_fee: Decimal = Decimal("0")
    gas_fee: Decimal = Decimal("0")

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate transaction after initialization."""
        if not self.expires_at:
            self.expires_at = self.created_at + timedelta(hours=24)

        self._validate()

    def _validate(self) -> None:
        """Validate transaction business rules."""
        if self.amount <= 0:
            raise InvalidTransferError("Transfer amount must be positive")

        if not self.source_chain or not self.destination_chain:
            raise InvalidTransferError("Source and destination chains are required")

        if self.source_chain == self.destination_chain:
            raise InvalidTransferError(
                "Source and destination chains cannot be the same"
            )

        if not self.sender_address or not self.recipient_address:
            raise InvalidTransferError("Sender and recipient addresses are required")

    def update_status(self, new_status: TransferStatus) -> None:
        """Update transaction status with validation."""
        if not self._can_transition_to(new_status):
            raise InvalidTransferError(
                f"Cannot transition from {self.status.value} to {new_status.value}"
            )

        self.status = new_status
        self.updated_at = datetime.utcnow()

    def _can_transition_to(self, new_status: TransferStatus) -> bool:
        """Check if status transition is valid."""
        valid_transitions = {
            TransferStatus.PENDING: [
                TransferStatus.INITIATED,
                TransferStatus.CANCELLED,
            ],
            TransferStatus.INITIATED: [TransferStatus.LOCKED, TransferStatus.FAILED],
            TransferStatus.LOCKED: [TransferStatus.VALIDATED, TransferStatus.FAILED],
            TransferStatus.VALIDATED: [TransferStatus.MINTED, TransferStatus.FAILED],
            TransferStatus.MINTED: [TransferStatus.COMPLETED, TransferStatus.FAILED],
            TransferStatus.COMPLETED: [],
            TransferStatus.FAILED: [],
            TransferStatus.CANCELLED: [],
            TransferStatus.DISPUTED: [TransferStatus.FAILED, TransferStatus.COMPLETED],
        }

        return new_status in valid_transitions.get(self.status, [])

    def add_validator_signature(self, validator_id: str, signature: str) -> None:
        """Add a validator signature."""
        if not validator_id or not signature:
            raise InvalidTransferError("Validator ID and signature are required")

        self.validator_signatures[validator_id] = signature
        self.updated_at = datetime.utcnow()

    def has_required_signatures(self, min_signatures: int) -> bool:
        """Check if transaction has minimum required signatures."""
        return len(self.validator_signatures) >= min_signatures

    def is_expired(self) -> bool:
        """Check if transaction has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def calculate_total_fee(self) -> Decimal:
        """Calculate total fees for the transaction."""
        return self.bridge_fee + self.gas_fee

    def set_security_level(self, level: SecurityLevel) -> None:
        """Set security level and adjust confirmations accordingly."""
        self.security_level = level

        # Adjust required confirmations based on security level
        confirmation_map = {
            SecurityLevel.STANDARD: 12,
            SecurityLevel.HIGH: 24,
            SecurityLevel.MAXIMUM: 64,
            SecurityLevel.QUANTUM_RESISTANT: 128,
        }

        self.required_confirmations = confirmation_map[level]
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "source_chain": self.source_chain,
            "destination_chain": self.destination_chain,
            "token_address": self.token_address,
            "amount": str(self.amount),
            "sender_address": self.sender_address,
            "recipient_address": self.recipient_address,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "security_level": self.security_level.value,
            "required_confirmations": self.required_confirmations,
            "source_tx_hash": self.source_tx_hash,
            "destination_tx_hash": self.destination_tx_hash,
            "bridge_fee": str(self.bridge_fee),
            "gas_fee": str(self.gas_fee),
            "metadata": self.metadata,
        }
