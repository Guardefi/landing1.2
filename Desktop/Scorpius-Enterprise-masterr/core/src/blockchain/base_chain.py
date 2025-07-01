"""
Base blockchain connection interface
"""

import logging
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any

from ..core.types import ChainType

logger = logging.getLogger(__name__)


class BaseChain(ABC):
    """Abstract base class for blockchain connections."""

    def __init__(self, chain_type: ChainType, rpc_url: str, private_key: str = ""):
        self.chain_type = chain_type
        self.rpc_url = rpc_url
        self.private_key = private_key
        self.connected = False
        self.logger = logging.getLogger(f"Chain.{chain_type.value}")

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the blockchain."""
        pass

    @abstractmethod
    async def disconnect(self):
        """Disconnect from the blockchain."""
        pass

    @abstractmethod
    async def get_block_number(self) -> int:
        """Get the current block number."""
        pass

    @abstractmethod
    async def get_transaction_receipt(self, tx_hash: str) -> dict[str, Any] | None:
        """Get transaction receipt."""
        pass

    @abstractmethod
    async def get_balance(
        self, address: str, token_address: str | None = None
    ) -> Decimal:
        """Get account balance."""
        pass

    @abstractmethod
    async def send_transaction(self, transaction_data: dict[str, Any]) -> str:
        """Send a transaction."""
        pass

    @abstractmethod
    async def estimate_gas(self, transaction_data: dict[str, Any]) -> int:
        """Estimate gas for a transaction."""
        pass

    @abstractmethod
    async def get_gas_price(self) -> int:
        """Get current gas price."""
        pass

    async def health_check(self) -> bool:
        """Check if the chain connection is healthy."""
        try:
            block_number = await self.get_block_number()
            return block_number > 0
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    def __str__(self) -> str:
        return f"{self.chain_type.value} Chain ({self.rpc_url})"
