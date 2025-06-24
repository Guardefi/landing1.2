"""
Atomic Swap Engine
Handles atomic swap operations between chains.
"""

import asyncio
import hashlib
import logging
import secrets
from datetime import UTC, datetime

from ..core.types import BridgeTransfer
from .types import AtomicSwap, SwapStatus

logger = logging.getLogger(__name__)


class AtomicSwapEngine:
    """Engine for managing atomic swaps."""

    def __init__(self):
        self.active_swaps: dict[str, AtomicSwap] = {}

    async def initiate_swap(
        self,
        transfer: BridgeTransfer,
        timeout_hours: int = 24,
    ) -> AtomicSwap:
        """Initiate an atomic swap for a bridge transfer."""
        try:
            # Generate secret and hash lock
            secret = self._generate_secret()
            hash_lock = self._generate_hash_lock(secret)

            # Calculate timeout blocks (simplified - in production use actual block numbers)
            timeout_block = int(datetime.now(UTC).timestamp()) + (timeout_hours * 3600)
            refund_timeout_block = timeout_block + 3600  # 1 hour buffer for refund
            swap = AtomicSwap(
                swap_id=transfer.id,
                initiator_address=transfer.sender_address,
                participant_address=transfer.receiver_address,
                source_chain=transfer.from_chain.value,
                destination_chain=transfer.to_chain.value,
                source_amount=transfer.amount,
                destination_amount=transfer.amount,  # 1:1 for now
                source_token=transfer.asset,
                destination_token=transfer.asset,  # Same token for now
                hash_lock=hash_lock,
                secret=secret,  # Keep secret for now (in production, only initiator knows)
                timeout_block=timeout_block,
                refund_timeout_block=refund_timeout_block,
                status=SwapStatus.INITIATED,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )

            self.active_swaps[swap.swap_id] = swap

            logger.info(f"Atomic swap initiated: {swap.swap_id}")
            return swap

        except Exception as e:
            logger.error(f"Failed to initiate atomic swap: {e}")
            raise e from e

    async def lock_funds(self, swap_id: str) -> bool:
        """Lock funds on the source chain."""
        try:
            if swap_id not in self.active_swaps:
                logger.error(f"Swap {swap_id} not found")
                return False

            swap = self.active_swaps[swap_id]

            if swap.status != SwapStatus.INITIATED:
                logger.error(f"Swap {swap_id} not in INITIATED status: {swap.status}")
                return False

            # Simulate locking funds on source chain
            await self._simulate_lock_transaction(swap)

            swap.status = SwapStatus.LOCKED
            swap.updated_at = datetime.now(UTC)

            logger.info(f"Funds locked for swap {swap_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to lock funds for swap {swap_id}: {e}")
            return False

    async def reveal_secret(self, swap_id: str, secret: str) -> bool:
        """Reveal secret to complete the swap."""
        try:
            if swap_id not in self.active_swaps:
                logger.error(f"Swap {swap_id} not found")
                return False

            swap = self.active_swaps[swap_id]

            if swap.status != SwapStatus.LOCKED:
                logger.error(f"Swap {swap_id} not in LOCKED status: {swap.status}")
                return False

            # Verify secret matches hash lock
            if not self._verify_secret(secret, swap.hash_lock):
                logger.error(f"Invalid secret for swap {swap_id}")
                return False

            # Simulate claiming funds on destination chain
            await self._simulate_claim_transaction(swap, secret)

            swap.status = SwapStatus.REVEALED
            swap.updated_at = datetime.now(UTC)

            logger.info(f"Secret revealed for swap {swap_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to reveal secret for swap {swap_id}: {e}")
            return False

    async def complete_swap(self, swap_id: str) -> bool:
        """Complete the atomic swap."""
        try:
            if swap_id not in self.active_swaps:
                logger.error(f"Swap {swap_id} not found")
                return False

            swap = self.active_swaps[swap_id]

            if swap.status != SwapStatus.REVEALED:
                logger.error(f"Swap {swap_id} not in REVEALED status: {swap.status}")
                return False

            # Simulate final completion
            await self._simulate_completion(swap)

            swap.status = SwapStatus.COMPLETED
            swap.updated_at = datetime.now(UTC)

            logger.info(f"Atomic swap completed: {swap_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to complete swap {swap_id}: {e}")
            return False

    async def refund_swap(self, swap_id: str) -> bool:
        """Refund an expired swap."""
        try:
            if swap_id not in self.active_swaps:
                logger.error(f"Swap {swap_id} not found")
                return False

            swap = self.active_swaps[swap_id]

            # Check if refund is allowed
            current_time = int(datetime.now(UTC).timestamp())
            if current_time < swap.refund_timeout_block:
                logger.error(f"Refund not yet allowed for swap {swap_id}")
                return False

            if swap.status not in [SwapStatus.LOCKED, SwapStatus.EXPIRED]:
                logger.error(f"Cannot refund swap {swap_id} in status {swap.status}")
                return False

            # Simulate refund transaction
            await self._simulate_refund_transaction(swap)

            swap.status = SwapStatus.REFUNDED
            swap.updated_at = datetime.now(UTC)

            logger.info(f"Atomic swap refunded: {swap_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to refund swap {swap_id}: {e}")
            return False

    async def check_timeout(self, swap_id: str) -> bool:
        """Check if a swap has timed out."""
        if swap_id not in self.active_swaps:
            return False

        swap = self.active_swaps[swap_id]
        current_time = int(datetime.now(UTC).timestamp())

        if current_time > swap.timeout_block:
            swap.status = SwapStatus.EXPIRED
            swap.updated_at = datetime.now(UTC)
            logger.info(f"Swap {swap_id} has expired")
            return True

        return False

    def get_swap(self, swap_id: str) -> AtomicSwap | None:
        """Get swap by ID."""
        return self.active_swaps.get(swap_id)

    def get_active_swaps(self) -> list[AtomicSwap]:
        """Get all active swaps."""
        return list(self.active_swaps.values())

    def _generate_secret(self) -> str:
        """Generate a random secret."""
        return secrets.token_hex(32)

    def _generate_hash_lock(self, secret: str) -> str:
        """Generate hash lock from secret."""
        return hashlib.sha256(secret.encode()).hexdigest()

    def _verify_secret(self, secret: str, hash_lock: str) -> bool:
        """Verify secret matches hash lock."""
        return self._generate_hash_lock(secret) == hash_lock

    async def _simulate_lock_transaction(self, swap: AtomicSwap) -> None:
        """Simulate locking funds on source chain."""
        await asyncio.sleep(0.1)  # Simulate network delay
        swap.source_tx_hash = f"0x{secrets.token_hex(32)}"
        logger.debug(f"Simulated lock transaction: {swap.source_tx_hash}")

    async def _simulate_claim_transaction(self, swap: AtomicSwap, secret: str) -> None:
        """Simulate claiming funds on destination chain."""
        await asyncio.sleep(0.1)  # Simulate network delay
        swap.destination_tx_hash = f"0x{secrets.token_hex(32)}"
        logger.debug(f"Simulated claim transaction: {swap.destination_tx_hash}")

    async def _simulate_completion(self, swap: AtomicSwap) -> None:
        """Simulate swap completion."""
        await asyncio.sleep(0.05)  # Simulate finalization
        logger.debug(f"Simulated completion for swap {swap.swap_id}")

    async def _simulate_refund_transaction(self, swap: AtomicSwap) -> None:
        """Simulate refund transaction."""
        await asyncio.sleep(0.1)  # Simulate network delay
        swap.refund_tx_hash = f"0x{secrets.token_hex(32)}"
        logger.debug(f"Simulated refund transaction: {swap.refund_tx_hash}")
