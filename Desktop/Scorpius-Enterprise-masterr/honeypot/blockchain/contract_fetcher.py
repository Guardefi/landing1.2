import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import aiohttp
from blockchain.web3_client import Web3Client

from config.settings import settings

# Configure logger
logger = logging.getLogger("blockchain.contract_fetcher")


class ContractFetcher:
    def __init__(self):
        self.web3_client = Web3Client()
        self.session = None
        self.api_keys = {
            # Chain ID to API key mappings
            1: settings.ETHERSCAN_API_KEY,  # Ethereum Mainnet
            56: settings.BSCSCAN_API_KEY,  # Binance Smart Chain
        }
        self.explorer_urls = {
            # Chain ID to explorer API URL mappings
            1: "https://api.etherscan.io/api",  # Etherscan
            56: "https://api.bscscan.com/api",  # BscScan
        }

    async def initialize(self):
        """Initialize the contract fetcher"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        await self.web3_client.initialize()

    async def fetch_contract_details(
        self, address: str, chain_id: int = 1
    ) -> Dict[str, Any]:
        """
        Fetch comprehensive contract details from blockchain and explorers

        Args:
            address: Contract address
            chain_id: Blockchain network ID (1=Ethereum, 56=BSC)

        Returns:
            Dictionary with contract details
        """
        if self.session is None:
            await self.initialize()

        tasks = [
            self._fetch_onchain_data(address, chain_id),
            self._fetch_abi_and_source(address, chain_id),
            self._fetch_transactions(address, chain_id),
            self._fetch_token_metadata(address, chain_id),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine results
        contract_data = results[0] if not isinstance(results[0], Exception) else {}

        # Add ABI and source code
        if not isinstance(results[1], Exception):
            contract_data.update(results[1])
        else:
            logger.warning(f"Error fetching ABI/source: {results[1]}")
            contract_data["abi"] = []
            contract_data["source_code"] = ""

        # Add transactions
        if not isinstance(results[2], Exception):
            contract_data["transactions"] = results[2]
        else:
            logger.warning(f"Error fetching transactions: {results[2]}")
            contract_data["transactions"] = []

        # Add token metadata if available
        if not isinstance(results[3], Exception) and results[3]:
            contract_data["token_metadata"] = results[3]

        return contract_data

    async def _fetch_onchain_data(self, address: str, chain_id: int) -> Dict[str, Any]:
        """Fetch contract data directly from the blockchain"""
        try:
            # Get basic contract data from web3 client
            contract_data = await self.web3_client.get_contract_data(address, chain_id)
            return contract_data

        except Exception as e:
            logger.error(f"Error fetching onchain data: {e}")
            raise

    async def _fetch_abi_and_source(
        self, address: str, chain_id: int
    ) -> Dict[str, Any]:
        """Fetch contract ABI and source code from blockchain explorer"""
        if chain_id not in self.explorer_urls:
            return {"abi": [], "source_code": ""}

        explorer_url = self.explorer_urls[chain_id]
        api_key = self.api_keys.get(chain_id, "")

        try:
            # Fetch contract ABI
            params = {
                "module": "contract",
                "action": "getabi",
                "address": address,
                "apikey": api_key,
            }

            async with self.session.get(explorer_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["status"] == "1":
                        abi = json.loads(data["result"])
                    else:
                        abi = []
                else:
                    abi = []

            # Fetch source code
            params = {
                "module": "contract",
                "action": "getsourcecode",
                "address": address,
                "apikey": api_key,
            }

            async with self.session.get(explorer_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["status"] == "1" and data["result"]:
                        source_code = data["result"][0].get("SourceCode", "")
                        contract_name = data["result"][0].get("ContractName", "")
                        compiler_version = data["result"][0].get("CompilerVersion", "")
                    else:
                        source_code = ""
                        contract_name = ""
                        compiler_version = ""
                else:
                    source_code = ""
                    contract_name = ""
                    compiler_version = ""

            return {
                "abi": abi,
                "source_code": source_code,
                "contract_name": contract_name,
                "compiler_version": compiler_version,
            }

        except Exception as e:
            logger.error(f"Error fetching ABI/source: {e}")
            return {"abi": [], "source_code": ""}

    async def _fetch_transactions(
        self, address: str, chain_id: int, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Fetch recent transactions for the contract"""
        if chain_id not in self.explorer_urls:
            return []

        explorer_url = self.explorer_urls[chain_id]
        api_key = self.api_keys.get(chain_id, "")

        try:
            # Fetch normal transactions
            params = {
                "module": "account",
                "action": "txlist",
                "address": address,
                "startblock": 0,
                "endblock": 99999999,
                "page": 1,
                "offset": limit,
                "sort": "desc",
                "apikey": api_key,
            }

            async with self.session.get(explorer_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["status"] == "1":
                        transactions = data["result"]
                    else:
                        transactions = []
                else:
                    transactions = []

            return transactions

        except Exception as e:
            logger.error(f"Error fetching transactions: {e}")
            return []

    async def _fetch_token_metadata(
        self, address: str, chain_id: int
    ) -> Optional[Dict[str, Any]]:
        """Fetch token metadata if contract is an ERC20/ERC721 token"""
        if chain_id not in self.explorer_urls:
            return None

        explorer_url = self.explorer_urls[chain_id]
        api_key = self.api_keys.get(chain_id, "")

        try:
            # Check if it's a token
            params = {
                "module": "token",
                "action": "tokeninfo",
                "contractaddress": address,
                "apikey": api_key,
            }

            async with self.session.get(explorer_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["status"] == "1" and data["result"]:
                        return data["result"][0]

            return None

        except Exception as e:
            logger.error(f"Error fetching token metadata: {e}")
            return None

    async def close(self):
        """Close all connections"""
        if self.session:
            await self.session.close()
        await self.web3_client.close()
