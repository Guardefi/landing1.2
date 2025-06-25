"""
Validator Manager
Manages validator nodes, registration, and coordination.
"""

import asyncio
import logging
from datetime import UTC, datetime

from ..config.settings import settings
from ..core.types import BridgeTransfer, ValidatorStatus
from .consensus import ConsensusEngine, ConsensusResult, ConsensusType
from .node import ValidatorNode

logger = logging.getLogger(__name__)


class ValidatorManager:
    """Manages validator nodes in the bridge network."""

    def __init__(self):
        self.validators: dict[str, ValidatorNode] = {}
        self.consensus_engine = ConsensusEngine(ConsensusType.WEIGHTED_MAJORITY)
        self._heartbeat_task: asyncio.Task | None = None

    async def register_validator(
        self,
        validator_id: str,
        address: str,
        stake_amount: float,
        public_key: str,
    ) -> bool:
        """Register a new validator."""
        try:
            if validator_id in self.validators:
                logger.warning(f"Validator {validator_id} already registered")
                return False

            # Validate stake amount
            if stake_amount <= 0:
                logger.error(f"Invalid stake amount for validator {validator_id}")
                return False

            validator = ValidatorNode(
                validator_id=validator_id,
                address=address,
                stake_amount=stake_amount,
                public_key=public_key,
            )

            self.validators[validator_id] = validator
            await validator.start()

            logger.info(f"Validator {validator_id} registered successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to register validator {validator_id}: {e}")
            return False

    async def unregister_validator(self, validator_id: str) -> bool:
        """Unregister a validator."""
        try:
            if validator_id not in self.validators:
                logger.warning(f"Validator {validator_id} not found")
                return False

            validator = self.validators[validator_id]
            await validator.stop()
            del self.validators[validator_id]

            logger.info(f"Validator {validator_id} unregistered successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to unregister validator {validator_id}: {e}")
            return False

    async def validate_transfer(self, transfer: BridgeTransfer) -> ConsensusResult:
        """Validate a bridge transfer using consensus."""
        try:
            active_validators = self.get_active_validators()

            if len(active_validators) < settings.min_validators:
                logger.error(
                    f"Not enough active validators: {len(active_validators)} < {settings.min_validators}"
                )
                return ConsensusResult(
                    reached=False,
                    votes_for=0,
                    votes_against=0,
                    total_validators=len(active_validators),
                    consensus_type=self.consensus_engine.consensus_type,
                    timestamp=datetime.now(UTC),
                    participants=[],
                )

            result = await self.consensus_engine.reach_consensus(
                transfer, active_validators
            )

            logger.info(
                f"Transfer validation completed: "
                f"transfer_id={transfer.transfer_id}, consensus={result.reached}"
            )

            return result

        except Exception as e:
            logger.error(f"Transfer validation failed: {e}")
            return ConsensusResult(
                reached=False,
                votes_for=0,
                votes_against=0,
                total_validators=0,
                consensus_type=self.consensus_engine.consensus_type,
                timestamp=datetime.now(UTC),
                participants=[],
            )

    def get_active_validators(self) -> list[ValidatorNode]:
        """Get list of active validators."""
        return [v for v in self.validators.values() if v.is_healthy()]

    def get_validator_count(self) -> dict[str, int]:
        """Get validator count by status."""
        counts = {
            "total": len(self.validators),
            "active": 0,
            "inactive": 0,
            "slashed": 0,
        }

        for validator in self.validators.values():
            if validator.status == ValidatorStatus.ACTIVE and validator.is_healthy():
                counts["active"] += 1
            elif validator.status == ValidatorStatus.SLASHED:
                counts["slashed"] += 1
            else:
                counts["inactive"] += 1

        return counts

    async def get_network_stats(self) -> dict:
        """Get comprehensive network statistics."""
        validator_counts = self.get_validator_count()
        active_validators = self.get_active_validators()

        total_stake = sum(v.stake_amount for v in self.validators.values())
        active_stake = sum(v.stake_amount for v in active_validators)

        avg_reputation = (
            sum(v.metrics.reputation_score for v in active_validators)
            / len(active_validators)
            if active_validators
            else 0.0
        )

        return {
            "validator_counts": validator_counts,
            "total_stake": total_stake,
            "active_stake": active_stake,
            "average_reputation": avg_reputation,
            "consensus_threshold": settings.consensus_threshold,
            "min_validators": settings.min_validators,
            "network_health": self._calculate_network_health(),
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def _calculate_network_health(self) -> float:
        """Calculate overall network health score (0.0 to 1.0)."""
        if not self.validators:
            return 0.0

        active_validators = self.get_active_validators()

        # Health factors
        validator_ratio = len(active_validators) / len(self.validators)
        min_validator_ratio = min(1.0, len(active_validators) / settings.min_validators)

        avg_reputation = (
            sum(v.metrics.reputation_score for v in active_validators)
            / len(active_validators)
            if active_validators
            else 0.0
        )

        # Weighted health score
        health = (
            validator_ratio * 0.4 + min_validator_ratio * 0.4 + avg_reputation * 0.2
        )

        return min(1.0, max(0.0, health))

    async def start_heartbeat_monitoring(self) -> None:
        """Start heartbeat monitoring for all validators."""
        if self._heartbeat_task:
            return

        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("Heartbeat monitoring started")

    async def stop_heartbeat_monitoring(self) -> None:
        """Stop heartbeat monitoring."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None
            logger.info("Heartbeat monitoring stopped")

    async def _heartbeat_loop(self) -> None:
        """Periodic heartbeat monitoring loop."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute

                for validator in self.validators.values():
                    if validator.status == ValidatorStatus.ACTIVE:
                        heartbeat = await validator.heartbeat()
                        logger.debug(
                            f"Heartbeat from {validator.validator_id}: {heartbeat}"
                        )

                        # Check if validator became unhealthy
                        if not validator.is_healthy():
                            logger.warning(
                                f"Validator {validator.validator_id} became unhealthy"
                            )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat monitoring error: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
