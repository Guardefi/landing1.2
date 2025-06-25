"""
Data models for mempool events.
"""
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class MempoolEventType(Enum):
    """Types of mempool events."""

    TRANSACTION = "transaction"
    CONTRACT_DEPLOYMENT = "contract_deployment"
    TOKEN_TRANSFER = "token_transfer"
    DEX_SWAP = "dex_swap"
    ARBITRAGE = "arbitrage"
    LIQUIDATION = "liquidation"
    MEV_BUNDLE = "mev_bundle"
    UNKNOWN = "unknown"


class MempoolEventSeverity(Enum):
    """Severity levels for mempool events."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MempoolEvent:
    """
    Represents a mempool event with comprehensive metadata.
    """

    tx_hash: str
    from_address: str
    contract_address: str | None = None
    gas_price: int = 0
    value: int = 0
    timestamp: float = field(default_factory=time.time)
    network_id: int = 1
    input_data: str = "0x"
    severity: MempoolEventSeverity = MempoolEventSeverity.INFO
    event_type: MempoolEventType = MempoolEventType.TRANSACTION
    raw_tx_data: dict[str, Any] = field(default_factory=dict)
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    decoded_function: str | None = None
    decoded_params: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    gas_limit: int | None = None
    nonce: int | None = None
    to_address: str | None = None
    block_number: int | None = None
    transaction_index: int | None = None
    max_fee_per_gas: int | None = None
    max_priority_fee_per_gas: int | None = None

    def __post_init__(self):
        """Validate the data after initialization."""
        if not self.tx_hash or not self.tx_hash.startswith("0x"):
            raise ValueError("Invalid transaction hash") from None
        if not self.from_address or not self.from_address.startswith("0x"):
            raise ValueError("Invalid from_address") from None
        if self.gas_price < 0:
            raise ValueError("Gas price cannot be negative") from None
        if self.value < 0:
            raise ValueError("Value cannot be negative") from None
        if self.network_id <= 0:
            raise ValueError("Network ID must be positive") from None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        data = asdict(self)
        # Convert enums to their values
        data["severity"] = self.severity.value
        data["event_type"] = self.event_type.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MempoolEvent":
        """Create instance from dictionary."""
        # Convert enum values back to enums
        if "severity" in data and isinstance(data["severity"], str):
            data["severity"] = MempoolEventSeverity(data["severity"])
        if "event_type" in data and isinstance(data["event_type"], str):
            data["event_type"] = MempoolEventType(data["event_type"])

        return cls(**data)

    @property
    def age_seconds(self) -> float:
        """Get the age of this event in seconds."""
        return time.time() - self.timestamp

    @property
    def is_contract_call(self) -> bool:
        """Check if this is a contract call (has input data)."""
        return len(self.input_data) > 2  # More than just '0x'

    @property
    def gas_price_gwei(self) -> float:
        """Get gas price in Gwei."""
        return self.gas_price / 1e9

    def add_tag(self, tag: str) -> None:
        """
        Add a tag to the event if not already present.

        Args:
            tag: Tag to add
        """
        if tag not in self.tags:
            self.tags.append(tag)


import time
from dataclasses import asdict
