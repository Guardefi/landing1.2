"""
Test configuration and fixtures for the honeypot detector tests
"""
import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add project root to path to allow imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from blockchain.contract_fetcher import ContractFetcher
from blockchain.web3_client import Web3Client
from core.analyzers.bytecode_analyzer import BytecodeAnalyzer
from core.analyzers.transaction_analyzer import TransactionAnalyzer
from core.engines.ml_engine import MLEngine
from core.engines.static_engine import StaticEngine
from core.engines.symbolic_engine import SymbolicEngine
from database.mongodb_client import MongoDBClient

from config.settings import Settings


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings():
    """Test settings with test database"""
    return Settings(
        DATABASE_NAME="test_honeypot_detector",
        MONGODB_URL="mongodb://localhost:27017",
        API_KEY="test_api_key",
        ETHEREUM_RPC_URL="https://eth-mainnet.mock-provider.io",
        BSC_RPC_URL="https://bsc.mock-provider.io",
        REDIS_URL="redis://localhost:6379/15",  # Use DB 15 for testing
        DEBUG=True,
    )


@pytest.fixture
async def mock_mongo_client():
    """Create a mocked MongoDB client"""
    with patch("database.mongodb_client.AsyncIOMotorClient") as mock_client:
        client = MongoDBClient()
        client.client = AsyncMock()
        client.client.__getitem__.return_value = AsyncMock()
        client.db = client.client[client.database_name]

        # Mock collection
        mock_collection = AsyncMock()
        client.db.__getitem__.return_value = mock_collection

        # Mock common operations
        mock_collection.find_one.return_value = None
        mock_collection.insert_one.return_value = AsyncMock(inserted_id="mock_id")
        mock_collection.find.return_value.to_list.return_value = []

        client.initialized = True
        yield client


@pytest.fixture
async def mock_web3_client():
    """Create a mocked Web3 client"""
    with patch("blockchain.web3_client.AsyncWeb3") as mock_web3:
        client = Web3Client()
        client.web3 = {1: AsyncMock(), 56: AsyncMock()}

        # Setup common mock responses
        for chain in client.web3.values():
            chain.eth.get_code = AsyncMock(return_value="0x1234")
            chain.eth.get_balance = AsyncMock(return_value=1000000000000000000)
            chain.eth.get_transaction_count = AsyncMock(return_value=10)

        client.initialized = True
        yield client


@pytest.fixture
async def mock_contract_fetcher(mock_web3_client):
    """Create a mocked contract fetcher"""
    fetcher = ContractFetcher()
    fetcher.web3_client = mock_web3_client
    fetcher.session = AsyncMock()

    # Mock response for aiohttp session
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={
            "status": "1",
            "result": [
                {
                    "SourceCode": "contract Test {}",
                    "ContractName": "Test",
                    "CompilerVersion": "0.8.0",
                }
            ],
        }
    )

    # Configure session context manager mock
    fetcher.session.get.return_value.__aenter__.return_value = mock_response

    fetcher.initialized = True
    yield fetcher


@pytest.fixture
def sample_contract_data():
    """Sample contract data for testing"""
    return {
        "address": "0x1234567890123456789012345678901234567890",
        "chain_id": 1,
        "bytecode": "0x608060405234801561001057600080fd5b50610150806100206000396000f3fe608060405234801561001057600080fd5b50600436106100365760003560e01c80632e64cec11461003b5780636057361d14610059575b600080fd5b610043610075565b60405161005091906100d9565b60405180910390f35b610073600480360381019061006e919061009d565b61007e565b005b60008054905090565b8060008190555050565b60008135905061009781610103565b92915050565b6000602082840312156100b3576100b26100fe565b5b60006100c184828501610088565b91505092915050565b6100d3816100f4565b82525050565b60006020820190506100ee60008301846100ca565b92915050565b6000819050919050565b600080fd5b61010c816100f4565b811461011757600080fd5b5056fea2646970667358221220223a3b39325558e7ee22ee1f48d0a0b5721487cd4cee89f01226f075261df92364736f6c63430008070033",
        "abi": [
            {
                "inputs": [],
                "name": "retrieve",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "num", "type": "uint256"}
                ],
                "name": "store",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function",
            },
        ],
        "source_code": "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.7;\n\ncontract SimpleStorage {\n    uint256 favoriteNumber;\n    \n    function store(uint256 num) public {\n        favoriteNumber = num;\n    }\n    \n    function retrieve() public view returns (uint256) {\n        return favoriteNumber;\n    }\n}",
        "contract_name": "SimpleStorage",
        "compiler_version": "0.8.7",
        "transactions": [
            {
                "hash": "0xabc123",
                "from": "0xabcdef1234567890abcdef1234567890abcdef12",
                "to": "0x1234567890123456789012345678901234567890",
                "value": "1000000000000000000",
                "input": "0x6057361d0000000000000000000000000000000000000000000000000000000000000001",
                "blockNumber": "14000000",
            }
        ],
        "is_token": False,
    }


@pytest.fixture
async def mock_ml_engine():
    """Create a mocked ML engine"""
    engine = MLEngine()
    engine.model = MagicMock()
    engine.model.predict_proba = MagicMock(return_value=[[0.8, 0.2]])
    engine.initialized = True
    yield engine


@pytest.fixture
def static_engine():
    """Create a static analysis engine"""
    return StaticEngine()


@pytest.fixture
async def mock_symbolic_engine():
    """Create a mocked symbolic execution engine"""
    engine = SymbolicEngine()
    engine.solver = MagicMock()
    engine.initialized = True
    yield engine


@pytest.fixture
def bytecode_analyzer():
    """Create a bytecode analyzer"""
    return BytecodeAnalyzer()


@pytest.fixture
def transaction_analyzer():
    """Create a transaction analyzer"""
    return TransactionAnalyzer()
