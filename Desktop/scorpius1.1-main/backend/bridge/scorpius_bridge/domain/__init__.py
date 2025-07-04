"""Domain layer for Scorpius Bridge.

This module contains pure business logic without external dependencies.
Domain objects, value objects, and business rules live here.
"""

from .errors import (
    DomainError,
    InsufficientLiquidityError,
    InvalidTransferError,
    SecurityViolationError,
)

# Import specific items to avoid import issues
from .events import (
    BridgeTransferCompleted,
    BridgeTransferInitiated,
    DomainEvent,
    LiquidityAdded,
    ValidatorJoined,
)
from .models.bridge_tx import BridgeTransaction
from .models.liquidity_pool import LiquidityPool
from .models.validator import ValidatorNode
from .policy import SecurityPolicy, TransferPolicy

__all__ = [
    # Events
    "DomainEvent",
    "BridgeTransferInitiated",
    "BridgeTransferCompleted",
    "LiquidityAdded",
    "ValidatorJoined",
    # Models
    "BridgeTransaction",
    "ValidatorNode",
    "LiquidityPool",
    # Policies
    "TransferPolicy",
    "SecurityPolicy",
    # Errors
    "DomainError",
    "InvalidTransferError",
    "InsufficientLiquidityError",
    "SecurityViolationError",
]
