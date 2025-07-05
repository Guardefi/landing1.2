"""Validator Node domain model.

Core entity representing a validator in the bridge network.
Contains pure business logic without external dependencies.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from ..errors import SecurityViolationError, ValidatorError


class ValidatorStatus(Enum):
    """Status of a validator node."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    JOINING = "joining"
    LEAVING = "leaving"
    SLASHED = "slashed"
    SUSPENDED = "suspended"


@dataclass
class ValidatorPerformance:
    """Validator performance metrics."""

    total_validations: int = 0
    successful_validations: int = 0
    failed_validations: int = 0
    response_time_avg: float = 0.0
    uptime_percentage: float = 100.0
    last_activity: Optional[datetime] = None

    @property
    def success_rate(self) -> float:
        """Calculate validation success rate."""
        if self.total_validations == 0:
            return 0.0
        return (self.successful_validations / self.total_validations) * 100.0


@dataclass
class ValidatorNode:
    """Core validator node entity."""

    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    address: str = ""
    public_key: str = ""

    # Status and timing
    status: ValidatorStatus = ValidatorStatus.JOINING
    joined_at: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)

    # Staking
    stake_amount: Decimal = Decimal("0")
    minimum_stake: Decimal = Decimal("1000")
    slashed_amount: Decimal = Decimal("0")

    # Reputation and performance
    reputation_score: float = 100.0
    performance: ValidatorPerformance = field(default_factory=ValidatorPerformance)

    # Network participation
    supported_chains: List[str] = field(default_factory=list)
    commission_rate: float = 0.05  # 5% default commission

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate validator after initialization."""
        self._validate()

    def _validate(self) -> None:
        """Validate validator business rules."""
        if not self.address:
            raise ValidatorError("Validator address is required")

        if not self.public_key:
            raise ValidatorError("Validator public key is required")

        if self.stake_amount < self.minimum_stake:
            raise ValidatorError(
                f"Stake amount {self.stake_amount} below minimum {self.minimum_stake}"
            )

        if not 0 <= self.commission_rate <= 1:
            raise ValidatorError("Commission rate must be between 0 and 1")

    def activate(self) -> None:
        """Activate validator if conditions are met."""
        if self.status != ValidatorStatus.JOINING:
            raise ValidatorError(
                f"Cannot activate validator with status {self.status.value}"
            )

        if self.stake_amount < self.minimum_stake:
            raise ValidatorError("Insufficient stake to activate")

        self.status = ValidatorStatus.ACTIVE
        self.last_seen = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate validator."""
        if self.status not in [ValidatorStatus.ACTIVE, ValidatorStatus.JOINING]:
            raise ValidatorError(
                f"Cannot deactivate validator with status {self.status.value}"
            )

        self.status = ValidatorStatus.INACTIVE
        self.last_seen = datetime.utcnow()

    def slash(self, amount: Decimal, reason: str) -> None:
        """Slash validator for misbehavior."""
        if amount <= 0:
            raise ValidatorError("Slash amount must be positive")

        if amount > self.stake_amount:
            amount = self.stake_amount

        self.slashed_amount += amount
        self.stake_amount -= amount
        self.reputation_score = max(0, self.reputation_score - 10)

        # Auto-suspend if stake falls below minimum
        if self.stake_amount < self.minimum_stake:
            self.status = ValidatorStatus.SLASHED

        # Add to metadata for audit trail
        if "slash_history" not in self.metadata:
            self.metadata["slash_history"] = []

        self.metadata["slash_history"].append(
            {
                "amount": str(amount),
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
                "remaining_stake": str(self.stake_amount),
            }
        )

    def add_stake(self, amount: Decimal) -> None:
        """Add stake to validator."""
        if amount <= 0:
            raise ValidatorError("Stake amount must be positive")

        self.stake_amount += amount

        # Reactivate if was slashed and now meets minimum
        if (
            self.status == ValidatorStatus.SLASHED
            and self.stake_amount >= self.minimum_stake
        ):
            self.status = ValidatorStatus.INACTIVE

    def record_validation(self, success: bool, response_time: float) -> None:
        """Record a validation attempt."""
        self.performance.total_validations += 1

        if success:
            self.performance.successful_validations += 1
            # Improve reputation slightly for successful validations
            self.reputation_score = min(100, self.reputation_score + 0.1)
        else:
            self.performance.failed_validations += 1
            # Decrease reputation for failed validations
            self.reputation_score = max(0, self.reputation_score - 1)

        # Update average response time
        if self.performance.total_validations == 1:
            self.performance.response_time_avg = response_time
        else:
            self.performance.response_time_avg = (
                self.performance.response_time_avg
                * (self.performance.total_validations - 1)
                + response_time
            ) / self.performance.total_validations

        self.performance.last_activity = datetime.utcnow()
        self.last_seen = datetime.utcnow()

    def is_online(self, timeout_minutes: int = 10) -> bool:
        """Check if validator is considered online."""
        if not self.last_seen:
            return False

        timeout = timedelta(minutes=timeout_minutes)
        return datetime.utcnow() - self.last_seen <= timeout

    def calculate_voting_power(self) -> float:
        """Calculate voting power based on stake and reputation."""
        base_power = float(self.stake_amount)
        reputation_multiplier = self.reputation_score / 100.0

        return base_power * reputation_multiplier

    def supports_chain(self, chain: str) -> bool:
        """Check if validator supports a specific chain."""
        return chain.lower() in [c.lower() for c in self.supported_chains]

    def add_supported_chain(self, chain: str) -> None:
        """Add support for a new chain."""
        if not self.supports_chain(chain):
            self.supported_chains.append(chain.lower())

    def remove_supported_chain(self, chain: str) -> None:
        """Remove support for a chain."""
        self.supported_chains = [
            c for c in self.supported_chains if c.lower() != chain.lower()
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "address": self.address,
            "public_key": self.public_key,
            "status": self.status.value,
            "joined_at": self.joined_at.isoformat(),
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "stake_amount": str(self.stake_amount),
            "minimum_stake": str(self.minimum_stake),
            "slashed_amount": str(self.slashed_amount),
            "reputation_score": self.reputation_score,
            "performance": {
                "total_validations": self.performance.total_validations,
                "successful_validations": self.performance.successful_validations,
                "failed_validations": self.performance.failed_validations,
                "success_rate": self.performance.success_rate,
                "response_time_avg": self.performance.response_time_avg,
                "uptime_percentage": self.performance.uptime_percentage,
                "last_activity": (
                    self.performance.last_activity.isoformat()
                    if self.performance.last_activity
                    else None
                ),
            },
            "supported_chains": self.supported_chains,
            "commission_rate": self.commission_rate,
            "voting_power": self.calculate_voting_power(),
            "is_online": self.is_online(),
            "metadata": self.metadata,
        }
