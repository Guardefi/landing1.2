"""Domain policies for Scorpius Bridge.

Business rules and invariants that govern the behavior of the system.
These policies are pure business logic without external dependencies.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List

from .errors import (
    InsufficientLiquidityError,
    InvalidTransferError,
    SecurityViolationError,
)
from .models.bridge_tx import BridgeTransaction, SecurityLevel, TransferStatus
from .models.liquidity_pool import LiquidityPool, PoolStatus
from .models.validator import ValidatorNode, ValidatorStatus


class TransferPolicy:
    """Policies governing bridge transfers."""

    @staticmethod
    def validate_transfer_amount(
        amount: Decimal, min_amount: Decimal, max_amount: Decimal
    ) -> None:
        """Validate transfer amount against limits."""
        if amount < min_amount:
            raise InvalidTransferError(f"Amount {amount} below minimum {min_amount}")

        if amount > max_amount:
            raise InvalidTransferError(f"Amount {amount} exceeds maximum {max_amount}")

    @staticmethod
    def calculate_bridge_fee(
        amount: Decimal, base_fee_rate: float, security_level: SecurityLevel
    ) -> Decimal:
        """Calculate bridge fee based on amount and security level."""
        base_fee = amount * Decimal(str(base_fee_rate))

        # Security level multipliers
        multipliers = {
            SecurityLevel.STANDARD: Decimal("1.0"),
            SecurityLevel.HIGH: Decimal("1.5"),
            SecurityLevel.MAXIMUM: Decimal("2.0"),
            SecurityLevel.QUANTUM_RESISTANT: Decimal("3.0"),
        }

        return base_fee * multipliers[security_level]

    @staticmethod
    def determine_required_validators(
        amount: Decimal, security_level: SecurityLevel, available_validators: int
    ) -> int:
        """Determine number of validators required for a transfer."""
        base_requirements = {
            SecurityLevel.STANDARD: 3,
            SecurityLevel.HIGH: 5,
            SecurityLevel.MAXIMUM: 7,
            SecurityLevel.QUANTUM_RESISTANT: 10,
        }

        required = base_requirements[security_level]

        # For very large amounts, require more validators
        if amount > Decimal("1000000"):  # $1M+
            required += 2
        elif amount > Decimal("100000"):  # $100K+
            required += 1

        return min(required, available_validators)

    @staticmethod
    def can_execute_transfer(
        transaction: BridgeTransaction, pool: LiquidityPool
    ) -> bool:
        """Check if a transfer can be executed given current pool state."""
        if transaction.status != TransferStatus.VALIDATED:
            return False

        if pool.status != PoolStatus.ACTIVE:
            return False

        # Check if pool has enough liquidity (including fees)
        total_required = transaction.amount + transaction.bridge_fee
        return pool.available_liquidity >= total_required


class SecurityPolicy:
    """Security policies and risk management rules."""

    @staticmethod
    def assess_transfer_risk(
        transaction: BridgeTransaction, sender_history: List[Dict[str, Any]] = None
    ) -> SecurityLevel:
        """Assess risk level for a transfer and recommend security level."""
        sender_history = sender_history or []

        # High-value transfers require higher security
        if transaction.amount > Decimal("1000000"):
            return SecurityLevel.QUANTUM_RESISTANT
        elif transaction.amount > Decimal("100000"):
            return SecurityLevel.MAXIMUM
        elif transaction.amount > Decimal("10000"):
            return SecurityLevel.HIGH

        # Check sender history for suspicious patterns
        recent_transfers = [
            tx
            for tx in sender_history
            if datetime.fromisoformat(tx.get("created_at", "2020-01-01"))
            > datetime.utcnow() - timedelta(hours=24)
        ]

        if len(recent_transfers) > 10:  # Too many transfers
            return SecurityLevel.HIGH

        total_recent_amount = sum(
            Decimal(tx.get("amount", "0")) for tx in recent_transfers
        )

        if total_recent_amount > Decimal("50000"):  # High volume
            return SecurityLevel.HIGH

        return SecurityLevel.STANDARD

    @staticmethod
    def validate_validator_eligibility(validator: ValidatorNode) -> bool:
        """Check if validator is eligible to participate in consensus."""
        if validator.status != ValidatorStatus.ACTIVE:
            return False

        if validator.reputation_score < 50:  # Minimum reputation
            return False

        if validator.stake_amount < validator.minimum_stake:
            return False

        # Check if validator is responsive
        if not validator.is_online():
            return False

        return True

    @staticmethod
    def calculate_consensus_threshold(validator_count: int) -> float:
        """Calculate consensus threshold based on validator count."""
        # Byzantine fault tolerance: need > 2/3 for safety
        base_threshold = 2 / 3

        # For smaller validator sets, require higher percentage
        if validator_count < 5:
            return 0.8  # 80%
        elif validator_count < 10:
            return 0.75  # 75%

        return base_threshold

    @staticmethod
    def should_slash_validator(
        validator: ValidatorNode, offense_type: str, offense_severity: int
    ) -> tuple[bool, Decimal]:
        """Determine if validator should be slashed and by how much."""
        slash_rates = {
            "unavailability": Decimal("0.01"),  # 1%
            "invalid_signature": Decimal("0.05"),  # 5%
            "double_signing": Decimal("0.1"),  # 10%
            "malicious_behavior": Decimal("0.2"),  # 20%
        }

        base_rate = slash_rates.get(offense_type, Decimal("0.01"))

        # Adjust based on severity (1-10 scale)
        severity_multiplier = Decimal(str(offense_severity)) / Decimal("10")
        slash_amount = validator.stake_amount * base_rate * severity_multiplier

        # Don't slash more than 50% of stake at once
        max_slash = validator.stake_amount * Decimal("0.5")
        slash_amount = min(slash_amount, max_slash)

        return slash_amount > 0, slash_amount


class LiquidityPolicy:
    """Policies governing liquidity pools and provision."""

    @staticmethod
    def calculate_optimal_pool_size(
        daily_volume: Decimal, volatility: float, utilization_target: float = 0.8
    ) -> Decimal:
        """Calculate optimal pool size based on volume and volatility."""
        # Base liquidity should handle target utilization
        base_liquidity = daily_volume / Decimal(str(utilization_target))

        # Add buffer for volatility (higher volatility = larger buffer)
        volatility_buffer = base_liquidity * Decimal(str(volatility))

        return base_liquidity + volatility_buffer

    @staticmethod
    def validate_liquidity_provision(
        pool: LiquidityPool, amount: Decimal, provider_address: str
    ) -> None:
        """Validate liquidity provision against pool rules."""
        if pool.status not in [PoolStatus.ACTIVE, PoolStatus.INACTIVE]:
            raise InvalidTransferError(
                f"Cannot add liquidity to pool with status {pool.status.value}"
            )

        # Check if would exceed maximum pool size
        if pool.total_liquidity + amount > pool.max_liquidity:
            raise InvalidTransferError("Would exceed maximum pool liquidity")

        # Check for concentration risk (no single provider > 50%)
        total_after_addition = pool.total_liquidity + amount
        existing_position = pool.get_provider_position(provider_address)
        provider_total = amount + (
            existing_position.amount if existing_position else Decimal("0")
        )

        concentration = provider_total / total_after_addition
        if concentration > Decimal("0.5"):
            raise SecurityViolationError(
                "Single provider cannot own more than 50% of pool"
            )

    @staticmethod
    def calculate_impermanent_loss(
        initial_price: Decimal,
        current_price: Decimal,
        pool_fee_rate: float,
        time_held_days: int,
    ) -> Decimal:
        """Calculate estimated impermanent loss for LP position."""
        # Simplified impermanent loss calculation
        price_ratio = current_price / initial_price

        # IL = 2 * sqrt(price_ratio) / (1 + price_ratio) - 1
        sqrt_ratio = price_ratio.sqrt()
        il = 2 * sqrt_ratio / (1 + price_ratio) - 1

        # Factor in fees earned to offset IL
        estimated_fees = (
            Decimal(str(pool_fee_rate)) * Decimal(str(time_held_days)) / Decimal("365")
        )

        return max(Decimal("0"), abs(il) - estimated_fees)

    @staticmethod
    def should_rebalance_pool(pool: LiquidityPool) -> bool:
        """Determine if pool needs rebalancing."""
        utilization = pool.get_utilization_rate()

        # Rebalance if utilization is too high or too low
        if utilization > 0.9 or utilization < 0.1:
            return True

        # Check if pool is below minimum liquidity
        if pool.total_liquidity < pool.min_liquidity:
            return True

        return False
