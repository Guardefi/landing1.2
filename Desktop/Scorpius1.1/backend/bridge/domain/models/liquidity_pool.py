"""Liquidity Pool domain model.

Core entity representing a liquidity pool for cross-chain transfers.
Contains pure business logic without external dependencies.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from ..errors import InsufficientLiquidityError, InvalidTransferError


class PoolStatus(Enum):
    """Status of a liquidity pool."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    DRAINING = "draining"
    EMERGENCY = "emergency"


@dataclass
class LiquidityPosition:
    """Individual liquidity provider position."""

    provider_address: str = ""
    amount: Decimal = Decimal("0")
    provided_at: datetime = field(default_factory=datetime.utcnow)
    shares: Decimal = Decimal("0")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "provider_address": self.provider_address,
            "amount": str(self.amount),
            "provided_at": self.provided_at.isoformat(),
            "shares": str(self.shares),
        }


@dataclass
class PoolMetrics:
    """Pool performance and utilization metrics."""

    total_volume: Decimal = Decimal("0")
    daily_volume: Decimal = Decimal("0")
    total_fees_collected: Decimal = Decimal("0")
    utilization_rate: float = 0.0
    avg_transfer_size: Decimal = Decimal("0")
    transfer_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_volume": str(self.total_volume),
            "daily_volume": str(self.daily_volume),
            "total_fees_collected": str(self.total_fees_collected),
            "utilization_rate": self.utilization_rate,
            "avg_transfer_size": str(self.avg_transfer_size),
            "transfer_count": self.transfer_count,
        }


@dataclass
class LiquidityPool:
    """Core liquidity pool entity."""

    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""

    # Pool configuration
    source_chain: str = ""
    destination_chain: str = ""
    token_address: str = ""
    token_symbol: str = ""

    # Liquidity
    total_liquidity: Decimal = Decimal("0")
    available_liquidity: Decimal = Decimal("0")
    reserved_liquidity: Decimal = Decimal("0")

    # Positions
    positions: List[LiquidityPosition] = field(default_factory=list)
    total_shares: Decimal = Decimal("0")

    # Pool parameters
    fee_rate: float = 0.003  # 0.3% default fee
    min_liquidity: Decimal = Decimal("1000")
    max_liquidity: Decimal = Decimal("10000000")

    # Status and timing
    status: PoolStatus = PoolStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Metrics
    metrics: PoolMetrics = field(default_factory=PoolMetrics)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate pool after initialization."""
        self._validate()
        self._update_available_liquidity()

    def _validate(self) -> None:
        """Validate pool business rules."""
        if not self.source_chain or not self.destination_chain:
            raise InvalidTransferError("Source and destination chains are required")

        if self.source_chain == self.destination_chain:
            raise InvalidTransferError(
                "Source and destination chains cannot be the same"
            )

        if not self.token_address:
            raise InvalidTransferError("Token address is required")

        if not 0 <= self.fee_rate <= 1:
            raise InvalidTransferError("Fee rate must be between 0 and 1")

    def _update_available_liquidity(self) -> None:
        """Update available liquidity calculation."""
        self.available_liquidity = self.total_liquidity - self.reserved_liquidity
        self.updated_at = datetime.utcnow()

    def add_liquidity(self, provider_address: str, amount: Decimal) -> Decimal:
        """Add liquidity to the pool and return shares issued."""
        if amount <= 0:
            raise InvalidTransferError("Liquidity amount must be positive")

        if self.status not in [PoolStatus.ACTIVE, PoolStatus.INACTIVE]:
            raise InvalidTransferError(
                f"Cannot add liquidity to pool with status {self.status.value}"
            )

        # Calculate shares to issue
        if self.total_shares == 0:
            # Initial liquidity - shares equal to amount
            shares = amount
        else:
            # Subsequent liquidity - proportional shares
            shares = (amount * self.total_shares) / self.total_liquidity

        # Create or update position
        existing_position = None
        for position in self.positions:
            if position.provider_address == provider_address:
                existing_position = position
                break

        if existing_position:
            existing_position.amount += amount
            existing_position.shares += shares
        else:
            new_position = LiquidityPosition(
                provider_address=provider_address,
                amount=amount,
                shares=shares,
            )
            self.positions.append(new_position)

        # Update pool totals
        self.total_liquidity += amount
        self.total_shares += shares
        self._update_available_liquidity()

        # Activate pool if it was inactive and now meets minimum
        if (
            self.status == PoolStatus.INACTIVE
            and self.total_liquidity >= self.min_liquidity
        ):
            self.status = PoolStatus.ACTIVE

        return shares

    def remove_liquidity(self, provider_address: str, shares: Decimal) -> Decimal:
        """Remove liquidity from pool and return amount withdrawn."""
        if shares <= 0:
            raise InvalidTransferError("Share amount must be positive")

        # Find provider position
        position = None
        for p in self.positions:
            if p.provider_address == provider_address:
                position = p
                break

        if not position:
            raise InvalidTransferError("Provider has no position in this pool")

        if shares > position.shares:
            raise InvalidTransferError("Insufficient shares to withdraw")

        # Calculate amount to withdraw
        withdrawal_amount = (shares * self.total_liquidity) / self.total_shares

        if withdrawal_amount > self.available_liquidity:
            raise InsufficientLiquidityError(
                "Insufficient available liquidity for withdrawal"
            )

        # Update position
        position.shares -= shares
        position.amount -= withdrawal_amount

        # Remove position if shares are zero
        if position.shares == 0:
            self.positions.remove(position)

        # Update pool totals
        self.total_liquidity -= withdrawal_amount
        self.total_shares -= shares
        self._update_available_liquidity()

        # Deactivate pool if below minimum liquidity
        if self.total_liquidity < self.min_liquidity:
            self.status = PoolStatus.INACTIVE

        return withdrawal_amount

    def reserve_liquidity(self, amount: Decimal) -> None:
        """Reserve liquidity for a pending transfer."""
        if amount <= 0:
            raise InvalidTransferError("Reserve amount must be positive")

        if amount > self.available_liquidity:
            raise InsufficientLiquidityError(
                f"Insufficient liquidity: requested {amount}, available {self.available_liquidity}"
            )

        self.reserved_liquidity += amount
        self._update_available_liquidity()

    def release_liquidity(self, amount: Decimal) -> None:
        """Release reserved liquidity back to available pool."""
        if amount <= 0:
            raise InvalidTransferError("Release amount must be positive")

        if amount > self.reserved_liquidity:
            raise InvalidTransferError("Cannot release more than reserved amount")

        self.reserved_liquidity -= amount
        self._update_available_liquidity()

    def execute_transfer(self, amount: Decimal) -> Decimal:
        """Execute transfer and collect fees."""
        if amount <= 0:
            raise InvalidTransferError("Transfer amount must be positive")

        if self.status != PoolStatus.ACTIVE:
            raise InvalidTransferError(
                f"Pool is not active (status: {self.status.value})"
            )

        # Calculate fee
        fee_amount = amount * Decimal(str(self.fee_rate))
        net_amount = amount - fee_amount

        # Check if we have enough reserved liquidity
        if net_amount > self.reserved_liquidity:
            raise InsufficientLiquidityError(
                "Insufficient reserved liquidity for transfer"
            )

        # Execute transfer
        self.reserved_liquidity -= net_amount
        self.total_liquidity -= net_amount
        self._update_available_liquidity()

        # Update metrics
        self.metrics.total_volume += amount
        self.metrics.total_fees_collected += fee_amount
        self.metrics.transfer_count += 1

        # Update average transfer size
        self.metrics.avg_transfer_size = self.metrics.total_volume / Decimal(
            str(self.metrics.transfer_count)
        )

        return net_amount

    def get_provider_position(
        self, provider_address: str
    ) -> Optional[LiquidityPosition]:
        """Get liquidity position for a specific provider."""
        for position in self.positions:
            if position.provider_address == provider_address:
                return position
        return None

    def calculate_share_value(self, shares: Decimal) -> Decimal:
        """Calculate the value of shares in terms of underlying token."""
        if self.total_shares == 0:
            return Decimal("0")

        return (shares * self.total_liquidity) / self.total_shares

    def get_utilization_rate(self) -> float:
        """Calculate current utilization rate of the pool."""
        if self.total_liquidity == 0:
            return 0.0

        return float(self.reserved_liquidity / self.total_liquidity)

    def pause(self) -> None:
        """Pause pool operations."""
        if self.status == PoolStatus.ACTIVE:
            self.status = PoolStatus.PAUSED
            self.updated_at = datetime.utcnow()

    def unpause(self) -> None:
        """Resume pool operations."""
        if self.status == PoolStatus.PAUSED:
            self.status = PoolStatus.ACTIVE
            self.updated_at = datetime.utcnow()

    def emergency_stop(self) -> None:
        """Emergency stop all pool operations."""
        self.status = PoolStatus.EMERGENCY
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "source_chain": self.source_chain,
            "destination_chain": self.destination_chain,
            "token_address": self.token_address,
            "token_symbol": self.token_symbol,
            "total_liquidity": str(self.total_liquidity),
            "available_liquidity": str(self.available_liquidity),
            "reserved_liquidity": str(self.reserved_liquidity),
            "total_shares": str(self.total_shares),
            "fee_rate": self.fee_rate,
            "min_liquidity": str(self.min_liquidity),
            "max_liquidity": str(self.max_liquidity),
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "utilization_rate": self.get_utilization_rate(),
            "provider_count": len(self.positions),
            "metrics": self.metrics.to_dict(),
            "metadata": self.metadata,
        }
