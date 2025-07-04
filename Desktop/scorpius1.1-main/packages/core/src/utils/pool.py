"""
Liquidity Pool Implementation
Individual liquidity pool for cross-chain tokens.
"""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


@dataclass
class PoolStats:
    """Statistics for a liquidity pool."""

    total_volume_24h: Decimal
    total_fees_24h: Decimal
    total_transactions_24h: int
    apy: Decimal
    utilization_rate: Decimal


class LiquidityPool:
    """Individual liquidity pool for bridge operations."""

    def __init__(
        self,
        pool_id: str,
        chain: str,
        token_address: str,
        token_symbol: str,
        initial_liquidity: Decimal = Decimal("0"),
    ):
        self.pool_id = pool_id
        self.chain = chain
        self.token_address = token_address
        self.token_symbol = token_symbol
        self.total_liquidity = initial_liquidity
        self.available_liquidity = initial_liquidity
        self.reserved_liquidity = Decimal("0")
        self.providers: dict[str, Decimal] = {}
        self.created_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
        self.stats = PoolStats(
            total_volume_24h=Decimal("0"),
            total_fees_24h=Decimal("0"),
            total_transactions_24h=0,
            apy=Decimal("0"),
            utilization_rate=Decimal("0"),
        )

    async def add_liquidity(self, provider_address: str, amount: Decimal) -> bool:
        """Add liquidity to the pool."""
        try:
            if amount <= 0:
                logger.error(f"Invalid liquidity amount: {amount}")
                return False

            # Add to provider's balance
            if provider_address in self.providers:
                self.providers[provider_address] += amount
            else:
                self.providers[provider_address] = amount

            # Update pool totals
            self.total_liquidity += amount
            self.available_liquidity += amount
            self.updated_at = datetime.now(UTC)

            self._update_utilization_rate()

            logger.info(
                f"Added {amount} {self.token_symbol} liquidity to pool {self.pool_id} "
                f"from {provider_address}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to add liquidity to pool {self.pool_id}: {e}")
            return False

    async def remove_liquidity(self, provider_address: str, amount: Decimal) -> bool:
        """Remove liquidity from the pool."""
        try:
            if amount <= 0:
                logger.error(f"Invalid liquidity amount: {amount}")
                return False

            if provider_address not in self.providers:
                logger.error(
                    f"Provider {provider_address} not found in pool {self.pool_id}"
                )
                return False

            provider_balance = self.providers[provider_address]
            if amount > provider_balance:
                logger.error(
                    f"Insufficient liquidity: requested {amount}, available {provider_balance}"
                )
                return False

            if amount > self.available_liquidity:
                logger.error(
                    f"Insufficient available liquidity: requested {amount}, "
                    f"available {self.available_liquidity}"
                )
                return False

            # Update provider's balance
            self.providers[provider_address] -= amount
            if self.providers[provider_address] == 0:
                del self.providers[provider_address]

            # Update pool totals
            self.total_liquidity -= amount
            self.available_liquidity -= amount
            self.updated_at = datetime.now(UTC)

            self._update_utilization_rate()

            logger.info(
                f"Removed {amount} {self.token_symbol} liquidity from pool {self.pool_id} "
                f"for {provider_address}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to remove liquidity from pool {self.pool_id}: {e}")
            return False

    async def reserve_liquidity(self, amount: Decimal) -> bool:
        """Reserve liquidity for a bridge transfer."""
        try:
            if amount <= 0:
                logger.error(f"Invalid reserve amount: {amount}")
                return False

            if amount > self.available_liquidity:
                logger.error(
                    f"Insufficient available liquidity: requested {amount}, "
                    f"available {self.available_liquidity}"
                )
                return False

            self.available_liquidity -= amount
            self.reserved_liquidity += amount
            self.updated_at = datetime.now(UTC)

            self._update_utilization_rate()

            logger.debug(
                f"Reserved {amount} {self.token_symbol} in pool {self.pool_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to reserve liquidity in pool {self.pool_id}: {e}")
            return False

    async def release_liquidity(self, amount: Decimal) -> bool:
        """Release reserved liquidity."""
        try:
            if amount <= 0:
                logger.error(f"Invalid release amount: {amount}")
                return False

            if amount > self.reserved_liquidity:
                logger.error(
                    f"Cannot release more than reserved: requested {amount}, "
                    f"reserved {self.reserved_liquidity}"
                )
                return False

            self.reserved_liquidity -= amount
            self.available_liquidity += amount
            self.updated_at = datetime.now(UTC)

            self._update_utilization_rate()

            logger.debug(
                f"Released {amount} {self.token_symbol} in pool {self.pool_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to release liquidity in pool {self.pool_id}: {e}")
            return False

    async def use_liquidity(self, amount: Decimal) -> bool:
        """Use reserved liquidity for a completed transfer."""
        try:
            if amount <= 0:
                logger.error(f"Invalid use amount: {amount}")
                return False

            if amount > self.reserved_liquidity:
                logger.error(
                    f"Cannot use more than reserved: requested {amount}, "
                    f"reserved {self.reserved_liquidity}"
                )
                return False

            self.reserved_liquidity -= amount
            self.total_liquidity -= amount
            self.updated_at = datetime.now(UTC)

            # Update stats
            self.stats.total_volume_24h += amount
            self.stats.total_transactions_24h += 1

            self._update_utilization_rate()

            logger.debug(f"Used {amount} {self.token_symbol} from pool {self.pool_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to use liquidity from pool {self.pool_id}: {e}")
            return False

    def get_provider_share(self, provider_address: str) -> Decimal:
        """Get provider's share of the pool."""
        if provider_address not in self.providers:
            return Decimal("0")

        if self.total_liquidity == 0:
            return Decimal("0")

        return self.providers[provider_address] / self.total_liquidity

    def get_pool_info(self) -> dict:
        """Get comprehensive pool information."""
        return {
            "pool_id": self.pool_id,
            "chain": self.chain,
            "token_address": self.token_address,
            "token_symbol": self.token_symbol,
            "total_liquidity": str(self.total_liquidity),
            "available_liquidity": str(self.available_liquidity),
            "reserved_liquidity": str(self.reserved_liquidity),
            "provider_count": len(self.providers),
            "stats": {
                "total_volume_24h": str(self.stats.total_volume_24h),
                "total_fees_24h": str(self.stats.total_fees_24h),
                "total_transactions_24h": self.stats.total_transactions_24h,
                "apy": str(self.stats.apy),
                "utilization_rate": str(self.stats.utilization_rate),
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def _update_utilization_rate(self) -> None:
        """Update the utilization rate."""
        if self.total_liquidity == 0:
            self.stats.utilization_rate = Decimal("0")
        else:
            self.stats.utilization_rate = self.reserved_liquidity / self.total_liquidity
