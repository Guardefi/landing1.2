#!/usr/bin/env python3
"""
Simple test runner for enterprise_main.py without pytest dependency conflicts
"""

import asyncio
import sys
import traceback

import httpx

# Import our application
from enterprise_main import app


async def test_health_endpoint():
    """Test the health check endpoint"""
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["service"] == "enterprise-command-router"
        print("✅ Health endpoint test passed")


async def test_readiness_endpoint():
    """Test the readiness check endpoint"""
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/readiness")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "dependencies" in data
        print("✅ Readiness endpoint test passed")


async def test_wallet_check_safe():
    """Test wallet check with safe wallet (mock)"""
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        payload = {
            "address": "0x742d35cc6484c512f2f5e2b1c3b85b07fcf77db2",
            "chain_id": 1,
            "include_approvals": True,
            "include_signatures": True,
        }

        response = await client.post("/api/v2/wallet/check", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["address"] == payload["address"].lower()
        assert data["chain_id"] == 1
        assert "risk_score" in data
        assert "risk_level" in data
        print("✅ Wallet check (safe) test passed")


async def test_wallet_check_risky():
    """Test wallet check with risky wallet pattern"""
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        payload = {
            "address": "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
            "chain_id": 1,
            "include_approvals": True,
            "include_signatures": True,
        }

        response = await client.post("/api/v2/wallet/check", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["address"] == payload["address"].lower()
        assert data["risk_score"] >= 0
        print("✅ Wallet check (risky) test passed")


async def test_wallet_check_invalid_address():
    """Test wallet check with invalid address (should fail)"""
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        payload = {
            "address": "invalid_address",
            "chain_id": 1,
            "include_approvals": True,
            "include_signatures": True,
        }

        response = await client.post("/api/v2/wallet/check", json=payload)

        assert response.status_code == 422  # Validation error
        print("✅ Wallet check (invalid address) test passed")


async def test_token_scan_safe():
    """Test token scan with safe token (mock)"""
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        payload = {
            "contract_address": "0x6b175474e89094c44da98b954eedeac495271d0f",  # DAI
            "chain_id": 1,
            "analysis_depth": "standard",
        }

        response = await client.post("/api/v2/scan/token", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["contract_address"] == payload["contract_address"].lower()
        assert data["is_verified"] is True
        print("✅ Token scan (safe) test passed")


async def test_token_scan_risky():
    """Test token scan with risky token pattern"""
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        payload = {
            "contract_address": "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
            "chain_id": 1,
            "analysis_depth": "deep",
        }

        response = await client.post("/api/v2/scan/token", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["is_verified"] is False
        assert data["risk_score"] > 50
        print("✅ Token scan (risky) test passed")


async def test_honeypot_assess_safe():
    """Test honeypot assessment with safe contract"""
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        payload = {
            "contract_address": "0x742d35cc6484c512f2f5e2b1c3b85b07fcf77db2",
            "chain_id": 1,
            "check_liquidity": True,
        }

        response = await client.post("/api/v2/honeypot/assess", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["is_honeypot"] is False
        assert data["confidence"] < 0.5
        print("✅ Honeypot assess (safe) test passed")


async def test_honeypot_assess_risky():
    """Test honeypot assessment with honeypot pattern"""
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        # Try with a proper format but honey pattern
        payload = {
            "contract_address": "0xhoneybeefhoneybeefhoneybeefhoneybeefhoney",
            "chain_id": 1,
            "check_liquidity": True,
        }

        response = await client.post("/api/v2/honeypot/assess", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["is_honeypot"] is True
        print("✅ Honeypot assess (risky) test passed")


async def test_wallet_revoke():
    """Test wallet approval revocation"""
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        payload = {
            "wallet_address": "0x742d35cc6484c512f2f5e2b1c3b85b07fcf77db2",
            "token_contract": "0x6b175474e89094c44da98b954eedeac495271d0f",
            "spender": "0x1111111254fb6c44bac0bed2854e76f90643097d",
            "chain_id": 1,
        }

        response = await client.post("/api/v2/wallet/revoke", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["status"] == "transaction_built"
        assert "transaction_hash" in data
        print("✅ Wallet revoke test passed")


async def test_batch_wallet_check():
    """Test batch wallet analysis"""
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        addresses = [
            "0x742d35cc6484c512f2f5e2b1c3b85b07fcf77db2",
            "0x6b175474e89094c44da98b954eedeac495271d0f",
        ]

        response = await client.post("/api/v2/batch/wallet-check", json=addresses)

        assert response.status_code == 200
        data = response.json()
        assert "batch_id" in data
        assert data["status"] == "processing"
        assert data["total_addresses"] == 2
        print("✅ Batch wallet check test passed")


async def test_metrics_endpoint():
    """Test metrics endpoint"""
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/api/v2/metrics")

        assert response.status_code == 200
        data = response.json()
        assert "requests_today" in data
        assert "success_rate" in data
        print("✅ Metrics endpoint test passed")


async def test_auth_context():
    """Test authentication context parsing"""
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        # Test with premium token
        headers = {"Authorization": "Bearer test_token_premium"}
        response = await client.post(
            "/api/v2/wallet/check",
            json={
                "address": "0x742d35cc6484c512f2f5e2b1c3b85b07fcf77db2",
                "chain_id": 1,
                "include_approvals": True,
                "include_signatures": True,
            },
            headers=headers,
        )

        assert response.status_code == 200
        print("✅ Auth context test passed")


async def run_all_tests():
    """Run all tests and report results"""
    tests = [
        test_health_endpoint,
        test_readiness_endpoint,
        test_wallet_check_safe,
        test_wallet_check_risky,
        test_wallet_check_invalid_address,
        test_token_scan_safe,
        test_token_scan_risky,
        test_honeypot_assess_safe,
        test_honeypot_assess_risky,
        test_wallet_revoke,
        test_batch_wallet_check,
        test_metrics_endpoint,
        test_auth_context,
    ]

    passed = 0
    failed = 0

    print(f"Running {len(tests)} tests...\n")

    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            traceback.print_exc()
            failed += 1
        print()

    print(f"\n{'='*50}")
    print(f"Test Results: {passed} passed, {failed} failed")
    print(f"Success rate: {passed/(passed+failed)*100:.1f}%")

    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print(f"⚠️  {failed} tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
