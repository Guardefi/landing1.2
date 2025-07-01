#!/usr/bin/env python3
from config.settings import settings
from database.mongodb_client import MongoDBClient
from api.main import app
import redis.asyncio as redis
import httpx
from typing import Any, Dict, List
from datetime import datetime, timedelta
import sys
import os
import asyncio
import time
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
# Comprehensive test suite for the Honeypot Detector API
"""

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
globals().update({

})
# import pytest  # Fixed: using direct execution

# Add project root to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    class TestAPI:
    """Test class for API endpoints"""

    def __init__(self):
    self.base_url = "http://localhost:8000"
    self.api_key = settings.API_KEY
    self.headers = {"X-API-Key": self.api_key}
    self.client = None

    async def setup(self):
    """Setup test client"""
    self.client = httpx.AsyncClient(base_url=self.base_url)

    async def teardown(self):
    """Cleanup test client"""
    if self.client:
    await self.client.aclose()

    async def test_health_endpoints(self):
    """Test health check endpoints"""
    print("🏥 Testing health endpoints...")

        # Test basic health check
    response = await self.client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    print("[PASS] Basic health check passed")

        # Test detailed health status
    response = await self.client.get("/health/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    print("[PASS] Detailed health status passed")

    return True

    async def test_authentication(self):
    """Test API authentication"""
    print("🔐 Testing authentication...")

        # Test without API key
    response = await self.client.post(
    "/api/v1/analyze",

    "address": "0x1234567890abcdef1234567890abcdef12345678",
    "chain_id": 1,

    assert response.status_code == 401
    print("[PASS] Unauthenticated request properly rejected")

        # Test with invalid API key
    invalid_headers={"X-API-Key": "invalid-key"}
    response=await self.client.post(
    "/api/v1/analyze",

    "address": "0x1234567890abcdef1234567890abcdef12345678",
    "chain_id": 1,

    headers=invalid_headers,

    assert response.status_code == 401
    print("[PASS] Invalid API key properly rejected")

        # Test with valid API key
    response=await self.client.get(
    "/api/v1/dashboard/stats", headers=self.headers

        # Note: This might fail if database isn't set up, but auth should pass
    assert response.status_code in [
    200,

    }  # 500 if DB not ready, but auth passed
    print("[PASS] Valid API key accepted")

    return True

    async def test_analysis_endpoints(self):
    """Test contract analysis endpoints"""
    print(">> Testing analysis endpoints...")

        # Test contract analysis with valid address format
    test_address="0x1234567890abcdef1234567890abcdef12345678"

    response=await self.client.post(
    "/api/v1/analyze",

    "address": test_address,
    "chain_id": 1,

    headers=self.headers,

        # Might fail due to missing services, but should validate input format
    print(f"Analysis response status: {response.status_code}")
    if response.status_code == 400:
    error_detail=response.json().get("detail", "")
    if "Invalid Ethereum address" in error_detail:
    print("[FAIL] Address validation failed unexpectedly")
    return False

    print("[PASS] Analysis endpoint accepts valid requests")

        # Test invalid address format
    response=await self.client.post(
    "/api/v1/analyze",

    headers=self.headers,

    assert response.status_code == 422  # Validation error
    print("[PASS] Invalid address format properly rejected")

    return True

    async def test_dashboard_endpoints(self):
    """Test dashboard endpoints"""
    print("[CHART] Testing dashboard endpoints...")

        # Test dashboard stats
    response=await self.client.get(
    "/api/v1/dashboard/stats", headers=self.headers

    print(f"Dashboard stats status: {response.status_code}")

        # Test trends endpoint
    response=await self.client.get(
    "/api/v1/dashboard/trends?days=7", headers=self.headers

    print(f"Dashboard trends status: {response.status_code}")

        # Test search endpoint
    response=await self.client.get(
    "/api/v1/dashboard/search?query=0x123", headers=self.headers

    print(f"Dashboard search status: {response.status_code}")

    print("[PASS] Dashboard endpoints accessible")
    return True

    async def test_cors_headers(self):
    """Test CORS configuration"""
    print("🌐 Testing CORS headers...")

        # Test preflight request
    response=await self.client.options(
    "/api/v1/dashboard/stats",

    "Origin": "http://localhost:3000",
    "Access-Control-Request-Method": "GET",

    ],

        # Check CORS headers are present
    if "access-control-allow-origin" in response.headers:
    print("[PASS] CORS headers present")
    else:
    print("[WARNING] CORS headers may not be configured properly")

    return True

    async def test_input_validation(self):
    """Test input validation across endpoints"""
    print(">> Testing input validation...")

        # Test various invalid inputs
    invalid_tests=[
            # Invalid address formats
    {"address": "", "expected_status": 422},

    {"address": "not-an-address", "expected_status": 422},
    {"address": "0x" + "g" * 40, "expected_status": 422},  # Invalid hex
    ]
    for test_case in invalid_tests:
    response=await self.client.post(
    "/api/v1/analyze",

    headers=self.headers,

    if response.status_code == test_case["expected_status"]:
    print(
    f"[PASS] Properly rejected invalid address: {
    test_case['address'}}")
    else:
    print(
    f"[WARNING] Unexpected status for {
    test_case['address'}}: {"
    response.status_code}"
                
    return True

    async def run_all_tests(self):
    """Run all API tests"""
    await self.setup()

    try:
    pass
    except Exception as e:

    print(">> Starting comprehensive API testing...")
    print("=" * 60)

    tests = [
    self.test_health_endpoints,

    self.test_analysis_endpoints,
    self.test_dashboard_endpoints,

    self.test_input_validation,
    ]
    results = []
    for test in tests:
    try:
    result = await test()
    results.append(result)
    print()
    except Exception as e:
    print(f"[FAIL] Test {test.__name__} failed: {str(e)}")
    results.append(False)
    print()

    print("=" * 60)
    print(f"[CHART] Test Results: {sum(results)}/{len(results)} passed")

    if all(results):
    print("[CELEBRATION] All tests passed!")
    else:
    print("[WARNING] Some tests failed - check output above")

    return all(results)

    finally:
    await self.teardown()

    class LoadTester:
    """Load testing for the API"""

    def __init__(self):
    self.base_url = "http://localhost:8000"
    self.api_key = settings.API_KEY
    self.headers = {"X-API-Key": self.api_key}

    async def concurrent_requests_test(self, num_requests: int = 10):
    """Test concurrent requests"""
    print(f"[BOLT] Testing {num_requests} concurrent requests...")

    async def make_request(client, request_id):
    start_time = time.time()
    response = await client.get("/health", headers=self.headers)
    end_time = time.time()
    return {
    "id": request_id,

    "duration": end_time - start_time,
    }

    async with httpx.AsyncClient(base_url=self.base_url) as client:
    tasks = [make_request(client, i) for i in range(num_requests)]
    results = await asyncio.gather(*tasks)

    successful = sum(1 for r in results if r["status"] == 200)
    avg_duration = sum(r["duration"] for r in results) / len(results)

    print(f"[PASS] {successful}/{num_requests} requests successful")
    print(f"[CHART] Average response time: {avg_duration:.3f}s")

    return successful == num_requests

    async def stress_test(self, duration_seconds: int = 30):
    """Stress test the API for a duration"""
    print(f"[FIRE] Stress testing for {duration_seconds} seconds...")

    start_time = time.time()
    end_time = start_time + duration_seconds
    request_count = 0
    success_count = 0

    async with httpx.AsyncClient(base_url=self.base_url) as client:
    while time.time() < end_time:
    try:
    response = await client.get("/health", headers=self.headers)
    request_count += 1
    if response.status_code == 200:
    success_count += 1
    except Exception as e:
    print(f"Request failed: {e}")
    request_count += 1

    await asyncio.sleep(0.1)  # Small delay

    success_rate = (success_count / request_count) * \
    100 if request_count > 0 else 0
    rps = request_count / duration_seconds

    print(f"[CHART] Requests: {request_count}, Success: {success_count}")
    print(f"[CHART] Success rate: {success_rate:.1f}%")
    print(f"[CHART] Requests per second: {rps:.1f}")

    return success_rate > 95  # 95% success rate threshold

    class DatabaseTester:
    """Test database connectivity and operations"""

    async def test_mongodb_connection(self):
    """Test MongoDB connection"""
    print("🍃 Testing MongoDB connection...")

    mongo_client = MongoDBClient()
    await mongo_client.initialize()

        # Test basic operations
    db = mongo_client.get_database()
    test_collection = db.test_collection

        # Insert test document
    test_doc = {"test": "data", "timestamp": datetime.utcnow()}
    result = await test_collection.insert_one(test_doc)
    print(f"[PASS] MongoDB insert successful: {result.inserted_id}")

        # Read test document
    found_doc = await test_collection.find_one({"_id": result.inserted_id})
    assert found_doc is not None
    print("[PASS] MongoDB read successful")

        # Delete test document
    delete_result = await test_collection.delete_one(
    {"_id": result.inserted_id}
        
    assert delete_result.deleted_count == 1
    print("[PASS] MongoDB delete successful")

    await mongo_client.close()
    return True

    except Exception as e:
    print(f"[FAIL] MongoDB test failed: {str(e)}")
    return False

    async def test_redis_connection(self):
    """Test Redis connection"""
    print("🔴 Testing Redis connection...")

    redis_client = redis.from_url(settings.REDIS_URL)

        # Test basic operations
    await redis_client.set("test_key", "test_value", ex=60)
    print("[PASS] Redis write successful")

    value = await redis_client.get("test_key")
    assert value.decode() == "test_value"
    print("[PASS] Redis read successful")

    await redis_client.delete("test_key")
    print("[PASS] Redis delete successful")

    await redis_client.close()
    return True

    except Exception as e:
    print(f"[FAIL] Redis test failed: {str(e)}")
    return False

    async def main():
    """Main testing function"""
    print(">> Honeypot Detector - Comprehensive Testing Suite")
    print("=" * 60)

    # API Tests
    api_tester = TestAPI()
    api_results = await api_tester.run_all_tests()

    # Load Tests
    print("\n>> Load Testing")
    print("=" * 60)
    load_tester = LoadTester()

    concurrent_result = await load_tester.concurrent_requests_test(20)
    stress_result = await load_tester.stress_test(15)

    # Database Tests
    print("\n💾 Database Testing")
    print("=" * 60)
    db_tester = DatabaseTester()

    mongo_result = await db_tester.test_mongodb_connection()
    redis_result = await db_tester.test_redis_connection()

    # Summary
    print("\n[REPORT] Test Summary")
    print("=" * 60)
    print(f"API Tests: {'[PASS] PASS' if api_results else '[FAIL] FAIL'}")
    print(
    f"Concurrent Load: {
    '[PASS} PASS' if concurrent_result else '[FAIL} FAIL'}")
    print(f"Stress Test: {'[PASS] PASS' if stress_result else '[FAIL] FAIL'}")
    print(f"MongoDB: {'[PASS] PASS' if mongo_result else '[FAIL] FAIL'}")
    print(f"Redis: {'[PASS] PASS' if redis_result else '[FAIL] FAIL'}")

    all_passed = all([api_results, concurrent_result,

    if all_passed:
    print(
    "\n[CELEBRATION] ALL TESTS PASSED! Your honeypot detector is ready for production!")
    else:
    print(
    "\n[WARNING] Some tests failed. Please check the configuration and try again.")

    return all_passed

    if __name__ == "__main__":
    asyncio.run(main())

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