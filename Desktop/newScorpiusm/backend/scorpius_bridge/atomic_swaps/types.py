"""
Atomic Swap Types
Data structures for atomic swap operations.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum


class SwapStatus(Enum):
    """Status of an atomic swap."""

    INITIATED = "initiated"
    LOCKED = "locked"
    REVEALED = "revealed"
    COMPLETED = "completed"
    REFUNDED = "refunded"
    EXPIRED = "expired"
    FAILED = "failed"


@dataclass
class AtomicSwap:
    """Atomic swap data structure."""

    swap_id: str
    initiator_address: str
    participant_address: str
    source_chain: str
    destination_chain: str
    source_amount: Decimal
    destination_amount: Decimal
    source_token: str
    destination_token: str
    hash_lock: str
    secret: str | None
    timeout_block: int
    refund_timeout_block: int
    status: SwapStatus
    created_at: datetime
    updated_at: datetime
    source_tx_hash: str | None = None
    destination_tx_hash: str | None = None
    refund_tx_hash: str | None = None
