"""Domain events for Scorpius Bridge.

Events represent something that happened in the domain.
They are used for event-driven architecture and integration.
"""

import uuid
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict


@dataclass
class DomainEvent(ABC):
    """Base class for all domain events."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    aggregate_id: str = ""
    event_version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "aggregate_id": self.aggregate_id,
            "event_version": self.event_version,
            "event_type": self.__class__.__name__,
        }


@dataclass
class BridgeTransferInitiated(DomainEvent):
    """Event fired when a bridge transfer is initiated."""

    transfer_id: str = ""
    source_chain: str = ""
    destination_chain: str = ""
    amount: str = ""
    token: str = ""
    sender: str = ""
    recipient: str = ""


@dataclass
class BridgeTransferCompleted(DomainEvent):
    """Event fired when a bridge transfer is completed."""

    transfer_id: str = ""
    transaction_hash: str = ""
    final_amount: str = ""
    fees_paid: str = ""


@dataclass
class BridgeTransferFailed(DomainEvent):
    """Event fired when a bridge transfer fails."""

    transfer_id: str = ""
    error_code: str = ""
    error_message: str = ""


@dataclass
class LiquidityAdded(DomainEvent):
    """Event fired when liquidity is added to a pool."""

    pool_id: str = ""
    provider: str = ""
    amount: str = ""
    token: str = ""
    new_total_liquidity: str = ""


@dataclass
class LiquidityRemoved(DomainEvent):
    """Event fired when liquidity is removed from a pool."""

    pool_id: str = ""
    provider: str = ""
    amount: str = ""
    token: str = ""
    new_total_liquidity: str = ""


@dataclass
class ValidatorJoined(DomainEvent):
    """Event fired when a validator joins the network."""

    validator_id: str = ""
    validator_address: str = ""
    stake_amount: str = ""
    reputation_score: float = 0.0


@dataclass
class ValidatorSlashed(DomainEvent):
    """Event fired when a validator is slashed."""

    validator_id: str = ""
    slash_amount: str = ""
    reason: str = ""
    new_stake: str = ""


@dataclass
class ConsensusReached(DomainEvent):
    """Event fired when consensus is reached on a transaction."""

    transaction_id: str = ""
    validator_count: int = 0
    consensus_threshold: float = 0.0
    result: str = ""
