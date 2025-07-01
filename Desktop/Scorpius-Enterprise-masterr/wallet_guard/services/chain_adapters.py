"""
Chain Adapters for multi-blockchain support
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ..models import ChainEnum, TokenTypeEnum


class BaseChainAdapter(ABC):
    """Base class for blockchain adapters"""

    def __init__(self, rpc_url: str, chain_id: int):
        self.rpc_url = rpc_url
        self.chain_id = chain_id

    @abstractmethod
    async def get_token_approvals(self, wallet_address: str) -> List[Dict[str, Any]]:
        """Get all token approvals for a wallet"""
        pass

    @abstractmethod
    async def check_drainer_signatures(
        self, wallet_address: str
    ) -> List[Dict[str, Any]]:
        """Check for known drainer signatures"""
        pass

    @abstractmethod
    async def detect_spoofed_approvals(
        self, wallet_address: str
    ) -> List[Dict[str, Any]]:
        """Detect spoofed approval attempts"""
        pass

    @abstractmethod
    async def build_revoke_transaction(
        self,
        wallet_address: str,
        spender_address: str,
        token_address: str,
        token_type: TokenTypeEnum,
    ) -> Dict[str, Any]:
        """Build revoke approval transaction"""
        pass


class EthereumAdapter(BaseChainAdapter):
    """Ethereum blockchain adapter"""

    async def get_token_approvals(self, wallet_address: str) -> List[Dict[str, Any]]:
        """Get ERC-20/721/1155 approvals for Ethereum"""
        # Mock implementation - in production this would query the blockchain
        await asyncio.sleep(0.1)  # Simulate network delay
        return [
            {
                "spender_address": "0x1234567890123456789012345678901234567890",
                "token_address": "0xA0b86a33E6441E7e04b5f1A0e1a5b85E1e2e3F8C",
                "token_type": "erc20",
                "approved_amount": "115792089237316195423570985008687907853269984665640564039457584007913129639935",
                "risk_level": "high",
                "risk_reasons": ["Unlimited approval", "Unknown spender"],
            }
        ]

    async def check_drainer_signatures(
        self, wallet_address: str
    ) -> List[Dict[str, Any]]:
        """Check for drainer function signatures"""
        await asyncio.sleep(0.1)
        return []

    async def detect_spoofed_approvals(
        self, wallet_address: str
    ) -> List[Dict[str, Any]]:
        """Detect address spoofing attempts"""
        await asyncio.sleep(0.1)
        return []

    async def build_revoke_transaction(
        self,
        wallet_address: str,
        spender_address: str,
        token_address: str,
        token_type: TokenTypeEnum,
    ) -> Dict[str, Any]:
        """Build ERC-20 approve(spender, 0) transaction"""
        await asyncio.sleep(0.1)

        # ERC-20 approve(address,uint256) function signature
        function_sig = "0x095ea7b3"
        spender_padded = spender_address[2:].zfill(64)
        amount_padded = "0" * 64

        return {
            "to": token_address,
            "data": f"{function_sig}{spender_padded}{amount_padded}",
            "value": "0",
            "gas_limit": "50000",
            "gas_price": "20000000000",  # 20 Gwei
        }


class BSCAdapter(BaseChainAdapter):
    """Binance Smart Chain adapter"""

    async def get_token_approvals(self, wallet_address: str) -> List[Dict[str, Any]]:
        await asyncio.sleep(0.1)
        return []

    async def check_drainer_signatures(
        self, wallet_address: str
    ) -> List[Dict[str, Any]]:
        await asyncio.sleep(0.1)
        return []

    async def detect_spoofed_approvals(
        self, wallet_address: str
    ) -> List[Dict[str, Any]]:
        await asyncio.sleep(0.1)
        return []

    async def build_revoke_transaction(
        self,
        wallet_address: str,
        spender_address: str,
        token_address: str,
        token_type: TokenTypeEnum,
    ) -> Dict[str, Any]:
        await asyncio.sleep(0.1)
        return {
            "to": token_address,
            "data": "0x095ea7b3" + spender_address[2:].zfill(64) + "0" * 64,
            "value": "0",
            "gas_limit": "50000",
            "gas_price": "5000000000",  # 5 Gwei (BSC)
        }


class ArbitrumAdapter(BaseChainAdapter):
    """Arbitrum adapter"""

    async def get_token_approvals(self, wallet_address: str) -> List[Dict[str, Any]]:
        await asyncio.sleep(0.1)
        return []

    async def check_drainer_signatures(
        self, wallet_address: str
    ) -> List[Dict[str, Any]]:
        await asyncio.sleep(0.1)
        return []

    async def detect_spoofed_approvals(
        self, wallet_address: str
    ) -> List[Dict[str, Any]]:
        await asyncio.sleep(0.1)
        return []

    async def build_revoke_transaction(
        self,
        wallet_address: str,
        spender_address: str,
        token_address: str,
        token_type: TokenTypeEnum,
    ) -> Dict[str, Any]:
        await asyncio.sleep(0.1)
        return {
            "to": token_address,
            "data": "0x095ea7b3" + spender_address[2:].zfill(64) + "0" * 64,
            "value": "0",
            "gas_limit": "50000",
            "gas_price": "100000000",  # 0.1 Gwei (Arbitrum)
        }


class BaseAdapter(BaseChainAdapter):
    """Base Chain adapter"""

    async def get_token_approvals(self, wallet_address: str) -> List[Dict[str, Any]]:
        await asyncio.sleep(0.1)
        return []

    async def check_drainer_signatures(
        self, wallet_address: str
    ) -> List[Dict[str, Any]]:
        await asyncio.sleep(0.1)
        return []

    async def detect_spoofed_approvals(
        self, wallet_address: str
    ) -> List[Dict[str, Any]]:
        await asyncio.sleep(0.1)
        return []

    async def build_revoke_transaction(
        self,
        wallet_address: str,
        spender_address: str,
        token_address: str,
        token_type: TokenTypeEnum,
    ) -> Dict[str, Any]:
        await asyncio.sleep(0.1)
        return {
            "to": token_address,
            "data": "0x095ea7b3" + spender_address[2:].zfill(64) + "0" * 64,
            "value": "0",
            "gas_limit": "50000",
            "gas_price": "1000000000",  # 1 Gwei (Base)
        }


class ChainAdapterFactory:
    """Factory for creating chain adapters"""

    _adapters: Dict[ChainEnum, BaseChainAdapter] = {}

    @classmethod
    async def initialize(cls):
        """Initialize all chain adapters"""
        cls._adapters = {
            ChainEnum.ETHEREUM: EthereumAdapter(
                "https://eth-mainnet.alchemyapi.io/v2/demo", 1
            ),
            ChainEnum.BSC: BSCAdapter("https://bsc-dataseed.binance.org/", 56),
            ChainEnum.ARBITRUM: ArbitrumAdapter("https://arb1.arbitrum.io/rpc", 42161),
            ChainEnum.BASE: BaseAdapter("https://mainnet.base.org", 8453),
        }

    @classmethod
    async def cleanup(cls):
        """Cleanup adapter resources"""
        cls._adapters.clear()

    @classmethod
    def get_adapter(cls, chain: ChainEnum) -> BaseChainAdapter:
        """Get adapter for specific chain"""
        adapter = cls._adapters.get(chain)
        if not adapter:
            raise ValueError(f"Adapter not found for chain: {chain}")
        return adapter
