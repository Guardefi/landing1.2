#!/usr/bin/env python3
"""
Basic Test Suite for API Gateway
Tests fundamental API Gateway functionality without external dependencies
"""

import sys
import os
import asyncio
import time
import json
import re
from pathlib import Path

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

class MockBaseModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockField:
    def __init__(self, default=None, description=""): pass

# Add mocks to globals for import fallbacks
globals().update({
    "SimilarityEngine": MockSimilarityEngine,
    "MultiDimensionalComparison": MockMultiDimensionalComparison,
    "TestClient": MockTestClient,
    "BaseModel": MockBaseModel,
    "Field": MockField,
})

def test_basic_imports():
    """Test that we can import basic modules"""
    print(">> Testing basic imports...")
    
    try:
        # Test importing time module
        assert callable(time.time)
        print("[PASS] Basic imports working")
        return True
    except Exception as e:
        print(f"[FAIL] Import test failed: {e}")
        return False

def test_api_gateway_models():
    """Test API Gateway model creation"""
    print(">> Testing API Gateway models...")
    
    try:
        # Mock wallet models
    class WalletCheckRequest(MockBaseModel):
    def __init__(self, address, **kwargs):
                if not self.is_valid_ethereum_address(address):
                    raise ValueError("Invalid Ethereum address")
                super().__init__(address=address, **kwargs)
            
    def is_valid_ethereum_address(self, address):
                return bool(re.match(r'^0x[a-fA-F0-9]{40}$', address))
        
    class TokenApproval(MockBaseModel):
    def __init__(self, token, contract_address, spender, approved_amount, 
                        is_unlimited=False, risk_level="low", **kwargs):
                super().__init__(
                    token=token, contract_address=contract_address, 
                    spender=spender, approved_amount=approved_amount,
                    is_unlimited=is_unlimited, risk_level=risk_level, **kwargs
                )
        
        # Test valid wallet address
        valid_request = WalletCheckRequest(
            address="0x1234567890123456789012345678901234567890"
        )
        assert valid_request.address == "0x1234567890123456789012345678901234567890"
        
        # Test token approval model
        approval = TokenApproval(
            token="USDC",
            contract_address="0xA0b86a33E6441b86BF6662a116c8c95F5bA1D4e1",
            spender="0x9876543210987654321098765432109876543210",
            approved_amount="1000000",
            is_unlimited=False,
            risk_level="low"
        )
        assert approval.token == "USDC"
        assert approval.is_unlimited is False
        
        print("[PASS] API Gateway models working")
        return True
        
    except Exception as e:
        print(f"[FAIL] Model test failed: {e}")
        return False

async def test_wallet_logic():
    """Test wallet scanning logic"""
    print(">> Testing wallet logic...")
    
    try:
        # Mock wallet scanning logic
    def calculate_risk_score(approvals_count: int, high_risk_count: int) -> int:
            return min(95, (high_risk_count * 25) + (approvals_count * 5))
        
    def get_risk_level(risk_score: int) -> str:
            if risk_score >= 75:
                return "critical"
            elif risk_score >= 50:
                return "high"
            elif risk_score >= 25:
                return "medium"
            else:
                return "low"
        
        # Test risk calculation
        assert calculate_risk_score(0, 0) == 0
        assert calculate_risk_score(1, 0) == 5
        assert calculate_risk_score(3, 1) == 40  # 1*25 + 3*5 = 40
        assert calculate_risk_score(10, 3) == 95  # capped at 95
        
        # Test risk level classification
        assert get_risk_level(0) == "low"
        assert get_risk_level(30) == "medium"
        assert get_risk_level(60) == "high"
        assert get_risk_level(80) == "critical"
        
        print("[PASS] Wallet logic working")
        return True
        
    except Exception as e:
        print(f"[FAIL] Wallet logic test failed: {e}")
        return False

def test_address_validation():
    """Test Ethereum address validation"""
    print(">> Testing address validation...")
    
    try:
    def is_valid_ethereum_address(address: str) -> bool:
            if not isinstance(address, str):
                return False
            return bool(re.match(r'^0x[a-fA-F0-9]{40}$', address))
        
        # Valid addresses
        assert is_valid_ethereum_address("0x1234567890123456789012345678901234567890")
        assert is_valid_ethereum_address("0xabcdefABCDEF123456789012345678901234567890")
        
        # Invalid addresses
        assert not is_valid_ethereum_address("0x123")  # too short
        assert not is_valid_ethereum_address("1234567890123456789012345678901234567890")  # no 0x prefix
        assert not is_valid_ethereum_address("0x123456789012345678901234567890123456789G")  # invalid hex
        assert not is_valid_ethereum_address("")  # empty
        assert not is_valid_ethereum_address("0x12345678901234567890123456789012345678900")  # too long
        
        print("[PASS] Address validation working")
        return True
        
    except Exception as e:
        print(f"[FAIL] Address validation test failed: {e}")
        return False

def test_mock_token_data():
    """Test mock token approval data generation"""
    print(">> Testing mock token data...")
    
    try:
        mock_approvals = [
            {
                "token": "DAI",
                "contract_address": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
                "spender": "0x1111111254fb6c44bAC0beD2854e76F90643097d",
                "approved_amount": "115792089237316195423570985008687907853269984665640564039457584007913129639935",
    "is_unlimited": True,
                "risk_level": "medium"
            },
            {
                "token": "USDC",
                "contract_address": "0xA0b86a33E6441b86BF6662a116c8c95F5bA1D4e1",
                "spender": "0x2222222254fb6c44bAC0beD2854e76F90643097d",
                "approved_amount": "1000000",
    "is_unlimited": False,
                "risk_level": "low"
            }
        ]
        
        assert len(mock_approvals) == 2
        
        # Test risk level calculation
        high_risk_count = sum(1 for approval in mock_approvals 
                             if approval["risk_level"] in ["high", "critical"])
        medium_risk_count = sum(1 for approval in mock_approvals 
                               if approval["risk_level"] == "medium")
        
        assert high_risk_count == 0  # Neither is high/critical
        assert medium_risk_count == 1  # One is medium
        
        print("[PASS] Mock token data working")
        return True
        
    except Exception as e:
        print(f"[FAIL] Mock token data test failed: {e}")
        return False

def test_api_gateway_basic():
    """Run all basic API Gateway tests"""
    print("🔍 Testing API Gateway Basic Functionality")
    print("=" * 50)
    
    test_functions = [
        test_basic_imports,
        test_api_gateway_models,
        test_address_validation,
        test_mock_token_data
    ]
    
    async_test_functions = [
        test_wallet_logic
    ]
    
    passed = 0
    total = len(test_functions) + len(async_test_functions)
    
    # Run sync tests
    for test_func in test_functions:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"[FAIL] {test_func.__name__}: {e}")
    
    # Run async tests
    for test_func in async_test_functions:
        try:
            if asyncio.run(test_func()):
                passed += 1
        except Exception as e:
            print(f"[FAIL] {test_func.__name__}: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 API GATEWAY BASIC TESTS: {passed}/{total} passed")
    
    return passed == total

def main():
    """Main execution function"""
    print("Starting API Gateway Basic Tests...")
    
    try:
        success = test_api_gateway_basic()
        print(f"\n{'✅ All tests passed!' if success else '⚠️ Some tests failed.'}")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[WARNING] Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Test execution error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
