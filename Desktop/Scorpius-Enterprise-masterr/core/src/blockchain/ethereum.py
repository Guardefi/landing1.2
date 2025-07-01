"""
Ethereum blockchain connection implementation
"""

import asyncio
import logging
from decimal import Decimal
from typing import Any

from ..core.types import ChainType
from .base_chain import BaseChain

try:
    from eth_account import Account
    from web3 import Web3
    from web3.middleware import geth_poa_middleware

    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    Web3 = None
    Account = None


logger = logging.getLogger(__name__)


class EthereumChain(BaseChain):
    """Ethereum blockchain connection."""

    def __init__(self, chain_type: ChainType, rpc_url: str, private_key: str = ""):
        super().__init__(chain_type, rpc_url, private_key)
        self.w3: Web3 | None = None
        self.account = None

        if not WEB3_AVAILABLE:
            self.logger.warning("Web3.py not available. Install with: pip install web3")

    async def connect(self) -> bool:
        """Connect to Ethereum node."""
        try:
            if not WEB3_AVAILABLE:
                self.logger.error("Web3.py not available")
                return False

            # Initialize Web3 connection
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))

            # Add PoA middleware for testnets
            if self.chain_type in [ChainType.BSC, ChainType.POLYGON]:
                self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

            # Test connection
            if not self.w3.is_connected():
                self.logger.error(f"Failed to connect to {self.chain_type.value}")
                return False

            # Initialize account if private key provided
            if self.private_key:
                self.account = Account.from_key(self.private_key)
                self.logger.info(f"Initialized account: {self.account.address}")

            self.connected = True
            self.logger.info(f"Connected to {self.chain_type.value} at {self.rpc_url}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to {self.chain_type.value}: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Disconnect from Ethereum node."""
        self.w3 = None
        self.account = None
        self.connected = False
        self.logger.info(f"Disconnected from {self.chain_type.value}")

    async def get_block_number(self) -> int:
        """Get current block number."""
        if not self.w3:
            raise ConnectionError("Not connected to blockchain")

        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            block_number = await loop.run_in_executor(
                None, lambda: self.w3.eth.block_number
            )
            return block_number

        except Exception as e:
            self.logger.error(f"Failed to get block number: {e}")
            raise e from e

    async def get_transaction_receipt(self, tx_hash: str) -> dict[str, Any] | None:
        """Get transaction receipt."""
        if not self.w3:
            raise ConnectionError("Not connected to blockchain")

        try:
            loop = asyncio.get_event_loop()
            receipt = await loop.run_in_executor(
                None, lambda: self.w3.eth.get_transaction_receipt(tx_hash)
            )

            # Convert to dict and handle special types
            return dict(receipt) if receipt else None

        except Exception as e:
            self.logger.error(f"Failed to get transaction receipt {tx_hash}: {e}")
            return None

    async def get_balance(
        self, address: str, token_address: str | None = None
    ) -> Decimal:
        """Get account balance (ETH or ERC20 token)."""
        if not self.w3:
            raise ConnectionError("Not connected to blockchain")

        try:
            loop = asyncio.get_event_loop()

            if token_address:
                # Get ERC20 token balance
                # This is a simplified implementation
                # In production, use proper contract ABI
                balance_wei = 0  # Placeholder
            else:
                # Get ETH balance
                balance_wei = await loop.run_in_executor(
                    None, lambda: self.w3.eth.get_balance(address)
                )

            # Convert from wei to ether
            balance_eth = self.w3.from_wei(balance_wei, "ether")
            return Decimal(str(balance_eth))

        except Exception as e:
            self.logger.error(f"Failed to get balance for {address}: {e}")
            return Decimal("0")

    async def send_transaction(self, transaction_data: dict[str, Any]) -> str:
        """Send a transaction."""
        if not self.w3 or not self.account:
            raise ConnectionError("Not connected or no account configured")

        try:
            # Add default gas parameters if not provided
            if "gas" not in transaction_data:
                transaction_data["gas"] = await self.estimate_gas(transaction_data)

            if "gasPrice" not in transaction_data:
                transaction_data["gasPrice"] = await self.get_gas_price()

            if "nonce" not in transaction_data:
                loop = asyncio.get_event_loop()
                nonce = await loop.run_in_executor(
                    None,
                    lambda: self.w3.eth.get_transaction_count(self.account.address),
                )
                transaction_data["nonce"] = nonce

            # Sign transaction
            signed_txn = self.account.sign_transaction(transaction_data)

            # Send transaction
            loop = asyncio.get_event_loop()
            tx_hash = await loop.run_in_executor(
                None,
                lambda: self.w3.eth.send_raw_transaction(signed_txn.rawTransaction),
            )

            tx_hash_hex = tx_hash.hex()
            self.logger.info(f"Transaction sent: {tx_hash_hex}")
            return tx_hash_hex

        except Exception as e:
            self.logger.error(f"Failed to send transaction: {e}")
            raise e from e

    async def estimate_gas(self, transaction_data: dict[str, Any]) -> int:
        """Estimate gas for a transaction."""
        if not self.w3:
            raise ConnectionError("Not connected to blockchain")

        try:
            loop = asyncio.get_event_loop()
            gas_estimate = await loop.run_in_executor(
                None, lambda: self.w3.eth.estimate_gas(transaction_data)
            )

            # Add 20% buffer for safety
            return int(gas_estimate * 1.2)

        except Exception as e:
            self.logger.error(f"Failed to estimate gas: {e}")
            # Return reasonable default
            return 21000

    async def get_gas_price(self) -> int:
        """Get current gas price."""
        if not self.w3:
            raise ConnectionError("Not connected to blockchain")

        try:
            loop = asyncio.get_event_loop()
            gas_price = await loop.run_in_executor(None, lambda: self.w3.eth.gas_price)
            return gas_price

        except Exception as e:
            self.logger.error(f"Failed to get gas price: {e}")
            # Return reasonable default (20 gwei)
            return 20_000_000_000

    async def wait_for_transaction_receipt(
        self, tx_hash: str, timeout: int = 120, poll_latency: float = 0.5
    ) -> dict[str, Any] | None:
        """Wait for transaction to be mined."""
        if not self.w3:
            raise ConnectionError("Not connected to blockchain")

        try:
            loop = asyncio.get_event_loop()
            receipt = await loop.run_in_executor(
                None,
                lambda: self.w3.eth.wait_for_transaction_receipt(
                    tx_hash, timeout=timeout, poll_latency=poll_latency
                ),
            )

            return dict(receipt) if receipt else None

        except Exception as e:
            self.logger.error(f"Failed to wait for transaction {tx_hash}: {e}")
            return None

    async def get_transaction_confirmations(self, tx_hash: str) -> int:
        """Get number of confirmations for a transaction."""
        try:
            receipt = await self.get_transaction_receipt(tx_hash)
            if not receipt:
                return 0

            current_block = await self.get_block_number()
            tx_block = receipt.get("blockNumber", 0)

            return max(0, current_block - tx_block + 1)

        except Exception as e:
            self.logger.error(f"Failed to get confirmations for {tx_hash}: {e}")
            return 0
