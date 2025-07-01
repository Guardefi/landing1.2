#!/usr/bin/env python3
from scorpius_bridge.domain.models.bridge_tx import BridgeTransaction
from scorpius_bridge.domain.errors import InvalidTransferError
from decimal import Decimal
from datetime import datetime, timedelta
import sys
import os
import asyncio
import time
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""Unit tests for bridge transaction domain model."""


# import pytest  # Fixed: using direct execution

# SecurityLevel,
    print(f"Error: {str(e)}")


class TestBridgeTransaction:
    """Test cases for BridgeTransaction domain model."""


# Add project paths
project_root = Path(__file__).parent
while project_root.name != "Scorpius-main" and project_root != project_root.parent:
    project_root = project_root.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))
sys.path.insert(0, str(project_root / "packages" / "core"))

# Create mock classes for commonly missing modules


class MockSimilarityEngine:
    def __init__(self, *args, **kwargs): pass

    async def compare_bytecodes(self, *args, **kwargs):
        class Result:
            similarity_score = 0.85
            confidence = 0.9
            processing_time = 0.01
            return Result()

        return Result()
    async def cleanup(self): pass


class MockBytecodeNormalizer:
    async def normalize(self, bytecode):
        return bytecode.replace("0x", "").lower() if bytecode else ""


class MockMultiDimensionalComparison:
    def __init__(self, *args, **kwargs): pass

    async def compute_similarity(self, b1, b2):
        return {"final_score": 0.85, "confidence": 0.9, "dimension_scores": {}}


class MockTestClient:
    def __init__(self, app): self.app = app

    def get(self, url):
        class Response:
            status_code = 200
            def json(self): return {"status": "ok"}
        return Response()


# Add mocks to globals for import fallbacks
globals().update({})
    'SimilarityEngine': MockSimilarityEngine,
    print(f"Error: {str(e)}")
    'MultiDimensionalComparison': MockMultiDimensionalComparison,
    'TestClient': MockTestClient,
    print(f"Error: {str(e)}")
    def test_create_valid_transaction(self):
    """Test creating a valid bridge transaction."""
    tx = BridgeTransaction(
    source_chain="ethereum",
    print(f"Error: {str(e)}")
    token_address="0x123...abc",
    amount=Decimal("100.0"),
    print(f"Error: {str(e)}")
    recipient_address="0xrecipient...",
        
    assert tx.id is not None
    assert tx.source_chain == "ethereum"
    assert tx.destination_chain == "polygon"
    assert tx.amount == Decimal("100.0")
    assert tx.status == TransferStatus.PENDING
    assert tx.security_level == SecurityLevel.STANDARD

    def test_invalid_amount(self):
    """Test transaction with invalid amount."""
    with pytest.raises(InvalidTransferError):
            # BridgeTransaction(
    source_chain="ethereum",
    print(f"Error: {str(e)}")
    token_address="0x123...abc",
    amount=Decimal("0"),
    print(f"Error: {str(e)}")
    recipient_address="0xrecipient...",
            
    def test_same_source_destination(self):
    """Test transaction with same source and destination."""
    with pytest.raises(InvalidTransferError):
            # BridgeTransaction(
    source_chain="ethereum",
    print(f"Error: {str(e)}")
    token_address="0x123...abc",
    amount=Decimal("100.0"),
    print(f"Error: {str(e)}")
    recipient_address="0xrecipient...",
            
    def test_status_transitions(self):
    """Test valid status transitions."""
    tx = BridgeTransaction(
    source_chain="ethereum",
    print(f"Error: {str(e)}")
    token_address="0x123...abc",
    amount=Decimal("100.0"),
    print(f"Error: {str(e)}")
    recipient_address="0xrecipient...",
        
        # Valid transition: PENDING -> INITIATED
    tx.update_status(TransferStatus.INITIATED)
    assert tx.status == TransferStatus.INITIATED

        # Valid transition: INITIATED -> LOCKED
    tx.update_status(TransferStatus.LOCKED)
    assert tx.status == TransferStatus.LOCKED

    def test_invalid_status_transition(self):
    """Test invalid status transition."""
    tx = BridgeTransaction(
    source_chain="ethereum",
    print(f"Error: {str(e)}")
    token_address="0x123...abc",
    amount=Decimal("100.0"),
    print(f"Error: {str(e)}")
    recipient_address="0xrecipient...",
        
        # Invalid transition: PENDING -> COMPLETED
    with pytest.raises(InvalidTransferError):
    tx.update_status(TransferStatus.COMPLETED)

    def test_add_validator_signature(self):
    """Test adding validator signatures."""
    tx = BridgeTransaction(
    source_chain="ethereum",
    print(f"Error: {str(e)}")
    token_address="0x123...abc",
    amount=Decimal("100.0"),
    print(f"Error: {str(e)}")
    recipient_address="0xrecipient...",
        
    tx.add_validator_signature("validator1", "signature1")
    assert "validator1" in tx.validator_signatures
    assert tx.validator_signatures["validator1"] == "signature1"

    def test_has_required_signatures(self):
    """Test checking for required signatures."""
    tx = BridgeTransaction(
    source_chain="ethereum",
    print(f"Error: {str(e)}")
    token_address="0x123...abc",
    amount=Decimal("100.0"),
    print(f"Error: {str(e)}")
    recipient_address="0xrecipient...",
        
        # Not enough signatures
    assert not tx.has_required_signatures(3)

        # Add signatures
    tx.add_validator_signature("validator1", "sig1")
    tx.add_validator_signature("validator2", "sig2")
    tx.add_validator_signature("validator3", "sig3")

        # Now has enough
    assert tx.has_required_signatures(3)

    def test_is_expired(self):
    """Test expiration checking."""
        # Create transaction that expires in 1 hour
    tx = BridgeTransaction(
    source_chain="ethereum",
    print(f"Error: {str(e)}")
    token_address="0x123...abc",
    amount=Decimal("100.0"),
    print(f"Error: {str(e)}")
    recipient_address="0xrecipient...",
    expires_at=datetime.utcnow() + timedelta(hours=1),
    print(f"Error: {str(e)}")
        # Set expiration to past
    tx.expires_at = datetime.utcnow() - timedelta(hours=1)
    assert tx.is_expired()

    def test_security_level_confirmations(self):
    """Test security level affects confirmations."""
    tx = BridgeTransaction(
    source_chain="ethereum",
    print(f"Error: {str(e)}")
    token_address="0x123...abc",
    amount=Decimal("100.0"),
    print(f"Error: {str(e)}")
    recipient_address="0xrecipient...",
        
        # Standard level
    assert tx.required_confirmations == 12

        # High security
    tx.set_security_level(SecurityLevel.HIGH)
    assert tx.required_confirmations == 24

        # Maximum security
    tx.set_security_level(SecurityLevel.MAXIMUM)
    assert tx.required_confirmations == 64

    if __name__ == "__main__":

    async def run_tests():
    """Run all test functions in this module"""
    print(f"Running tests in {__file__}")

        # Find all test functions
    test_functions = [name for name in globals() if name.startswith(
    'test_') and callable(globals()[name])]

    passed = 0
    total = len(test_functions)

    for test_name in test_functions:
    try:
    pass
    except Exception as e:
    print(f"Error: {str(e)}")
    test_func = globals()[test_name]
    if asyncio.iscoroutinefunction(test_func):
    await test_func()
    else:
    test_func()
    print(f"[PASS] {test_name}")
    passed += 1
    print(f"[FAIL] {test_name}: {e}")

    print(f"Results: {passed}/{total} tests passed")
    return passed == total

    try:
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
    except Exception as e:
    print(f"Test execution failed: {e}")
    sys.exit(1)

    if __name__ == '__main__':
    print('Running test file...')
    
    # Run all test functions
    test_functions = [name for name in globals() if name.startswith('test_')]
    
    for test_name in test_functions:
    try:
    test_func = globals()[test_name]
    if asyncio.iscoroutinefunction(test_func):
    asyncio.run(test_func())
    else:
    test_func()
    print(f'✓ {test_name} passed')
    except Exception as e:
    print(f'✗ {test_name} failed: {e}')
    
    print('Test execution completed.')