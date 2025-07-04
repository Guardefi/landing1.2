"""Domain errors for Scorpius Bridge.

Custom exceptions for business rule violations.
"""

from typing import Any, Dict, Optional


class DomainError(Exception):
    """Base class for all domain errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class InvalidTransferError(DomainError):
    """Raised when a transfer violates business rules."""

    pass


class InsufficientLiquidityError(DomainError):
    """Raised when there's insufficient liquidity for a transfer."""

    pass


class SecurityViolationError(DomainError):
    """Raised when security policies are violated."""

    pass


class ValidatorError(DomainError):
    """Raised when validator operations fail."""

    pass


class ConsensusError(DomainError):
    """Raised when consensus cannot be reached."""

    pass


class ChainInteractionError(DomainError):
    """Raised when blockchain interactions fail."""

    pass
