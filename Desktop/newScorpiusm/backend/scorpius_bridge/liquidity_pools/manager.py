"""
Liquidity Manager
Manages multiple liquidity pools across chains.
"""

import logging
from decimal import Decimal

from .pool import LiquidityPool

logger = logging.getLogger(__name__)


class LiquidityManager:
    """Manages liquidity pools for the bridge network."""

    def __init__(self):
        self.pools: dict[str, LiquidityPool] = {}

    async def create_pool(
        self,
        chain: str,
        token_address: str,
        token_symbol: str,
        initial_liquidity: Decimal = Decimal("0"),
    ) -> str:
        """Create a new liquidity pool."""
        try:
            pool_id = f"{chain}_{token_symbol}_{token_address[:8]}"

            if pool_id in self.pools:
                logger.warning(f"Pool {pool_id} already exists")
                return pool_id

            pool = LiquidityPool(
                pool_id=pool_id,
                chain=chain,
                token_address=token_address,
                token_symbol=token_symbol,
                initial_liquidity=initial_liquidity,
            )

            self.pools[pool_id] = pool
            logger.info(f"Created liquidity pool: {pool_id}")
            return pool_id

        except Exception as e:
            logger.error(f"Failed to create pool: {e}")
            raise e from e

    def get_pool(self, pool_id: str) -> LiquidityPool | None:
        """Get a liquidity pool by ID."""
        return self.pools.get(pool_id)

    def get_pools_by_chain(self, chain: str) -> list[LiquidityPool]:
        """Get all pools for a specific chain."""
        return [pool for pool in self.pools.values() if pool.chain == chain]

    def get_pools_by_token(self, token_symbol: str) -> list[LiquidityPool]:
        """Get all pools for a specific token."""
        return [
            pool for pool in self.pools.values() if pool.token_symbol == token_symbol
        ]

    async def get_total_liquidity(self) -> dict[str, Decimal]:
        """Get total liquidity across all pools."""
        totals: dict[str, Decimal] = {}

        for pool in self.pools.values():
            if pool.token_symbol not in totals:
                totals[pool.token_symbol] = Decimal("0")
            totals[pool.token_symbol] += pool.total_liquidity

        return totals

    async def check_liquidity_availability(
        self, chain: str, token_symbol: str, amount: Decimal
    ) -> bool:
        """Check if sufficient liquidity is available."""
        pools = [
            pool
            for pool in self.pools.values()
            if pool.chain == chain and pool.token_symbol == token_symbol
        ]

        if not pools:
            return False

        total_available = sum(pool.available_liquidity for pool in pools)
        return total_available >= amount

    def get_all_pools(self) -> list[LiquidityPool]:
        """Get all liquidity pools."""
        return list(self.pools.values())
