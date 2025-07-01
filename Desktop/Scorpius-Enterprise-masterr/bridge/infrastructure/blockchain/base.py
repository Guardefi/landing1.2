"""Base blockchain client interface and factory.

Abstract base classes and factory for blockchain clients.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict, Optional


class BlockchainClient(ABC):
    """Abstract base class for blockchain clients."""

    def __init__(self, rpc_url: str, chain_id: int):
        self.rpc_url = rpc_url
        self.chain_id = chain_id

    @abstractmethod
    async def get_balance(
        self, address: str, token_address: Optional[str] = None
    ) -> Decimal:
        """Get balance for an address."""
        pass

    @abstractmethod
    async def get_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get transaction details."""
        pass

    @abstractmethod
    async def get_block_number(self) -> int:
        """Get current block number."""
        pass

    @abstractmethod
    async def estimate_gas_fee(self) -> Decimal:
        """Estimate current gas fees."""
        pass

    @abstractmethod
    async def execute_transfer(
        self, token_address: str, recipient: str, amount: Decimal, transfer_id: str
    ) -> str:
        """Execute a transfer and return transaction hash."""
        pass

    @abstractmethod
    async def get_confirmations(self, tx_hash: str) -> int:
        """Get number of confirmations for a transaction."""
        pass

    @abstractmethod
    async def is_transaction_confirmed(
        self, tx_hash: str, required_confirmations: int
    ) -> bool:
        """Check if transaction has enough confirmations."""
        pass


class BlockchainClientFactory:
    """Factory for creating blockchain clients."""

    _clients: Dict[str, type] = {}

    @classmethod
    def register_client(cls, chain_name: str, client_class: type):
        """Register a blockchain client class."""
        cls._clients[chain_name.lower()] = client_class

    @classmethod
    def create_client(
        cls, chain_name: str, rpc_url: str, chain_id: int, **kwargs
    ) -> BlockchainClient:
        """Create a blockchain client for the specified chain."""
        chain_name_lower = chain_name.lower()

        if chain_name_lower not in cls._clients:
            raise ValueError(f"Unsupported blockchain: {chain_name}")

        client_class = cls._clients[chain_name_lower]
        return client_class(rpc_url, chain_id, **kwargs)

    @classmethod
    def get_supported_chains(cls) -> list[str]:
        """Get list of supported blockchain names."""
        return list(cls._clients.keys())
