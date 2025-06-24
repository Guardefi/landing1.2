"""
Validator Node Implementation
Individual validator node for bridge consensus and validation.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from ..config.settings import settings
from ..core.types import BridgeTransfer, TransferStatus, ValidatorStatus

logger = logging.getLogger(__name__)


@dataclass
class ValidatorMetrics:
    """Metrics for validator performance."""

    uptime_percentage: float
    total_validations: int
    successful_validations: int
    failed_validations: int
    average_response_time_ms: float
    last_seen: datetime
    reputation_score: float


class ValidatorNode:
    """Individual validator node in the bridge network."""

    def __init__(
        self,
        validator_id: str,
        address: str,
        stake_amount: float,
        public_key: str,
    ):
        self.validator_id = validator_id
        self.address = address
        self.stake_amount = stake_amount
        self.public_key = public_key
        self.status = ValidatorStatus.INACTIVE
        self.metrics = ValidatorMetrics(
            uptime_percentage=100.0,
            total_validations=0,
            successful_validations=0,
            failed_validations=0,
            average_response_time_ms=0.0,
            last_seen=datetime.now(UTC),
            reputation_score=1.0,
        )
        self._last_heartbeat = datetime.now(UTC)

    async def validate_transfer(self, transfer: BridgeTransfer) -> bool:
        """Validate a bridge transfer."""
        try:
            start_time = datetime.now(UTC)

            # Perform validation checks
            validation_result = await self._perform_validation(transfer)

            # Update metrics
            end_time = datetime.now(UTC)
            response_time = (end_time - start_time).total_seconds() * 1000

            self.metrics.total_validations += 1
            if validation_result:
                self.metrics.successful_validations += 1
            else:
                self.metrics.failed_validations += 1

            # Update average response time
            total_time = (
                self.metrics.average_response_time_ms
                * (self.metrics.total_validations - 1)
                + response_time
            )
            self.metrics.average_response_time_ms = (
                total_time / self.metrics.total_validations
            )

            logger.info(
                f"Validator {self.validator_id} validated transfer {transfer.transfer_id}: {validation_result}"
            )

            return validation_result

        except Exception as e:
            logger.error(f"Validation error for validator {self.validator_id}: {e}")
            self.metrics.failed_validations += 1
            return False

    async def _perform_validation(self, transfer: BridgeTransfer) -> bool:
        """Perform actual validation logic."""
        # Check transfer amount limits
        if transfer.amount < settings.min_transfer_amount:
            logger.warning(f"Transfer amount {transfer.amount} below minimum")
            return False

        if transfer.amount > settings.max_transfer_amount:
            logger.warning(f"Transfer amount {transfer.amount} above maximum")
            return False
        # Check if chains are supported
        if transfer.from_chain.value not in settings.supported_chains:
            logger.warning(f"Source chain {transfer.from_chain.value} not supported")
            return False

        if transfer.to_chain.value not in settings.supported_chains:
            logger.warning(f"Destination chain {transfer.to_chain.value} not supported")
            return False
        # Check transfer timeout
        if transfer.status in [TransferStatus.FAILED, TransferStatus.CANCELLED]:
            logger.warning(
                f"Transfer {transfer.id} is in invalid status: {transfer.status.value}"
            )
            return False

        # Simulate blockchain verification (in production, verify on-chain)
        await asyncio.sleep(0.1)  # Simulate network call

        return True

    async def start(self) -> None:
        """Start the validator node."""
        self.status = ValidatorStatus.ACTIVE
        self._last_heartbeat = datetime.now(UTC)
        logger.info(f"Validator {self.validator_id} started")

    async def stop(self) -> None:
        """Stop the validator node."""
        self.status = ValidatorStatus.INACTIVE
        logger.info(f"Validator {self.validator_id} stopped")

    async def heartbeat(self) -> dict:
        """Send heartbeat signal."""
        self._last_heartbeat = datetime.now(UTC)
        self.metrics.last_seen = self._last_heartbeat

        return {
            "validator_id": self.validator_id,
            "status": self.status.value,
            "timestamp": self._last_heartbeat.isoformat(),
            "metrics": {
                "uptime_percentage": self.metrics.uptime_percentage,
                "total_validations": self.metrics.total_validations,
                "reputation_score": self.metrics.reputation_score,
            },
        }

    def is_healthy(self) -> bool:
        """Check if validator is healthy."""
        if self.status != ValidatorStatus.ACTIVE:
            return False

        # Check if last heartbeat was recent (within 5 minutes)
        time_since_heartbeat = datetime.now(UTC) - self._last_heartbeat
        return time_since_heartbeat.total_seconds() < 300

    def get_voting_power(self) -> float:
        """Get voting power based on stake and reputation."""
        base_power = self.stake_amount
        reputation_multiplier = max(0.1, min(2.0, self.metrics.reputation_score))
        return base_power * reputation_multiplier
