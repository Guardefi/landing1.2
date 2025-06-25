"""
Consensus Engine
Implements consensus mechanisms for bridge operations.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum

from ..config.settings import settings
from ..core.types import BridgeTransfer
from .node import ValidatorNode

logger = logging.getLogger(__name__)


class ConsensusType(Enum):
    """Types of consensus mechanisms."""

    SIMPLE_MAJORITY = "simple_majority"
    WEIGHTED_MAJORITY = "weighted_majority"
    BYZANTINE_FAULT_TOLERANT = "byzantine_fault_tolerant"


@dataclass
class ConsensusResult:
    """Result of consensus process."""

    reached: bool
    votes_for: int
    votes_against: int
    total_validators: int
    consensus_type: ConsensusType
    timestamp: datetime
    participants: list[str]


class ConsensusEngine:
    """Consensus engine for bridge operations."""

    def __init__(self, consensus_type: ConsensusType = ConsensusType.WEIGHTED_MAJORITY):
        self.consensus_type = consensus_type
        self.threshold = settings.consensus_threshold

    async def reach_consensus(
        self,
        transfer: BridgeTransfer,
        validators: list[ValidatorNode],
    ) -> ConsensusResult:
        """Reach consensus on a bridge transfer."""
        try:
            # Filter active and healthy validators
            active_validators = [v for v in validators if v.is_healthy()]

            if len(active_validators) < settings.min_validators:
                logger.warning(
                    f"Not enough active validators: {len(active_validators)} < {settings.min_validators}"
                )
                return ConsensusResult(
                    reached=False,
                    votes_for=0,
                    votes_against=0,
                    total_validators=len(active_validators),
                    consensus_type=self.consensus_type,
                    timestamp=datetime.now(UTC),
                    participants=[],
                )

            # Gather votes from validators
            votes = await self._gather_votes(transfer, active_validators)

            # Calculate consensus based on type
            consensus_reached = await self._calculate_consensus(
                votes, active_validators
            )

            votes_for = sum(1 for vote in votes if vote)
            votes_against = len(votes) - votes_for
            participants = [v.validator_id for v in active_validators]

            result = ConsensusResult(
                reached=consensus_reached,
                votes_for=votes_for,
                votes_against=votes_against,
                total_validators=len(active_validators),
                consensus_type=self.consensus_type,
                timestamp=datetime.now(UTC),
                participants=participants,
            )

            logger.info(
                f"Consensus for transfer {transfer.transfer_id}: "
                f"reached={consensus_reached}, votes={votes_for}/{len(votes)}"
            )

            return result

        except Exception as e:
            logger.error(f"Consensus error for transfer {transfer.transfer_id}: {e}")
            return ConsensusResult(
                reached=False,
                votes_for=0,
                votes_against=0,
                total_validators=0,
                consensus_type=self.consensus_type,
                timestamp=datetime.now(UTC),
                participants=[],
            )

    async def _gather_votes(
        self,
        transfer: BridgeTransfer,
        validators: list[ValidatorNode],
    ) -> list[bool]:
        """Gather votes from all validators."""
        tasks = [validator.validate_transfer(transfer) for validator in validators]

        # Set timeout for validation
        timeout = 30.0  # 30 seconds

        try:
            votes = await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout)
            return votes
        except TimeoutError:
            logger.warning(f"Validation timeout for transfer {transfer.transfer_id}")
            # Return False votes for timeout
            return [False] * len(validators)

    async def _calculate_consensus(
        self,
        votes: list[bool],
        validators: list[ValidatorNode],
    ) -> bool:
        """Calculate if consensus is reached based on consensus type."""
        if not votes:
            return False

        if self.consensus_type == ConsensusType.SIMPLE_MAJORITY:
            return await self._simple_majority(votes)
        elif self.consensus_type == ConsensusType.WEIGHTED_MAJORITY:
            return await self._weighted_majority(votes, validators)
        elif self.consensus_type == ConsensusType.BYZANTINE_FAULT_TOLERANT:
            return await self._byzantine_fault_tolerant(votes)
        else:
            logger.error(f"Unknown consensus type: {self.consensus_type}")
            return False

    async def _simple_majority(self, votes: list[bool]) -> bool:
        """Simple majority consensus."""
        positive_votes = sum(votes)
        return positive_votes > len(votes) // 2

    async def _weighted_majority(
        self,
        votes: list[bool],
        validators: list[ValidatorNode],
    ) -> bool:
        """Weighted majority based on validator voting power."""
        total_power = sum(v.get_voting_power() for v in validators)
        positive_power = sum(
            v.get_voting_power() for i, v in enumerate(validators) if votes[i]
        )

        if total_power == 0:
            return False

        consensus_ratio = positive_power / total_power
        return consensus_ratio >= self.threshold

    async def _byzantine_fault_tolerant(self, votes: list[bool]) -> bool:
        """Byzantine fault tolerant consensus (2/3 majority)."""
        positive_votes = sum(votes)
        required_votes = (len(votes) * 2) // 3 + 1
        return positive_votes >= required_votes
