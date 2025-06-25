"""Domain layer for Scorpius Bridge.

This module contains pure business logic without external dependencies.
Domain objects, value objects, and business rules live here.
"""

# Import specific items to avoid import issues
from .events import (
    DomainEvent,
    BridgeTransferInitiated, 
    BridgeTransferCompleted,
    LiquidityAdded,
    ValidatorJoined,
)

from .models.bridge_tx import BridgeTransaction
from .models.validator import ValidatorNode
from .models.liquidity_pool import LiquidityPool

from .policy import TransferPolicy, SecurityPolicy

from .errors import (
    DomainError,
    InvalidTransferError,
    InsufficientLiquidityError,
    SecurityViolationError,
)

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
