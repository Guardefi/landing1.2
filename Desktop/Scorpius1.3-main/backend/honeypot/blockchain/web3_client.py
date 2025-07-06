import asyncio
from typing import Any, Dict, List, Optional

import aiohttp
from web3 import HTTPProvider, Web3

from config.settings import settings


class Web3Client:
    def __init__(self):
        self.providers = {}
        self.session = None
        self.initialized = False

    async def initialize(self):
        """Initialize Web3 connections for different chains"""
        self.session = aiohttp.ClientSession()

        # Initialize providers for different networks
        self.providers = {
            1: Web3(HTTPProvider(settings.ETHEREUM_RPC_URL)),  # Ethereum Mainnet
            56: Web3(HTTPProvider(settings.BSC_RPC_URL)),  # Binance Smart Chain
            # Add more chains as needed
        }

        self.initialized = True

    async def get_contract_data(
        self, address: str, chain_id: int = 1
    ) -> Dict[str, Any]:
        """Fetch comprehensive contract data including bytecode, ABI, and transactions"""
        if not self.initialized:
            await self.initialize()

        if chain_id not in self.providers:
            raise ValueError(f"Chain ID {chain_id} not supported")

        w3 = self.providers[chain_id]

        if not w3.is_address(address):
            raise ValueError(f"Invalid address format: {address}")

        try:
            # Get basic contract info
            checksum_address = w3.to_checksum_address(address)
            bytecode = await self._get_bytecode(w3, checksum_address)
            abi = await self._get_abi_from_explorer(chain_id, checksum_address)
            source_code = await self._get_source_code(chain_id, checksum_address)

            # Get transaction history
            transactions = await self._get_transactions(w3, checksum_address, limit=50)

            # Create contract instance if ABI is available
            contract = None
            if abi:
                contract = w3.eth.contract(address=checksum_address, abi=abi)

            # Get balance and other metadata
            balance = w3.eth.get_balance(checksum_address)
            code_size = (
                len(bytecode) // 2 - 1
                if bytecode.startswith("0x")
                else len(bytecode) // 2
            )

            return {
                "address": checksum_address,
                "chain_id": chain_id,
                "bytecode": bytecode,
                "abi": abi,
                "source_code": source_code,
                "balance": balance,
                "code_size": code_size,
                "transactions": transactions,
                "contract": contract,
            }

        except Exception as e:
            raise Exception(f"Error fetching contract data: {str(e)}")

    async def _get_bytecode(self, w3, address: str) -> str:
        """Get contract bytecode"""
        return w3.eth.get_code(address).hex()

    async def _get_abi_from_explorer(self, chain_id: int, address: str) -> List[Dict]:
        """Get contract ABI from blockchain explorer"""
        # In production, implement API calls to Etherscan, BSCScan, etc.
        # For now, return empty list as placeholder
        return []

    async def _get_source_code(self, chain_id: int, address: str) -> str:
        """Get contract source code from blockchain explorer if available"""
        # In production, implement API calls to Etherscan, BSCScan, etc.
        # For now, return empty string as placeholder
        return ""

    async def _get_transactions(self, w3, address: str, limit: int = 50) -> List[Dict]:
        """Get recent transactions involving the contract"""
        # In production, use event logs and transaction receipts
        # For now, return empty list as placeholder
        return []

    async def close(self):
        """Close all connections"""
        if self.session:
            await self.session.close()
