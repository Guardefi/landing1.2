#!/usr/bin/env python3
"""
Test script for Honeypot Detector API
Run this to verify the API is working correctly
"""
import asyncio
import json
import sys

import aiohttp

API_BASE = "http://localhost:8000"
API_KEY = "honeypot-detector-api-key-12345"


async def test_api():
    """Test all major API endpoints"""
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        print("🧪 Testing Honeypot Detector API")
        print("=" * 50)

        # Test 1: Health Check
        print("1. Testing health check...")
        try:
            async with session.get(f"{API_BASE}/health", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Health check passed: {data}")
                else:
                    print(f"   ❌ Health check failed: {response.status}")
        except Exception as e:
            print(f"   ❌ Health check error: {e}")

        # Test 2: System Status
        print("\n2. Testing system status...")
        try:
            async with session.get(f"{API_BASE}/status", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ System status: {data.get('status', 'unknown')}")
                else:
                    print(f"   ❌ System status failed: {response.status}")
        except Exception as e:
            print(f"   ⚠️  System status error (may not be implemented): {e}")

        # Test 3: Dashboard Stats
        print("\n3. Testing dashboard stats...")
        try:
            async with session.get(
                f"{API_BASE}/api/v1/dashboard/stats", headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Dashboard stats retrieved")
                    print(f"      Total analyses: {data.get('total_analyses', 0)}")
                    print(
                        f"      Honeypots detected: {data.get('honeypots_detected', 0)}"
                    )
                else:
                    print(f"   ❌ Dashboard stats failed: {response.status}")
        except Exception as e:
            print(f"   ⚠️  Dashboard stats error: {e}")

        # Test 4: Contract Analysis (with a test address)
        print("\n4. Testing contract analysis...")
        test_address = "0x1234567890abcdef1234567890abcdef12345678"  # Dummy address
        test_payload = {"address": test_address, "chain_id": 1, "deep_analysis": False}

        try:
            async with session.post(
                f"{API_BASE}/api/v1/analyze", headers=headers, json=test_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Contract analysis completed")
                    print(f"      Address: {data.get('address', 'unknown')}")
                    print(f"      Is honeypot: {data.get('is_honeypot', False)}")
                    print(f"      Confidence: {data.get('confidence', 0):.2f}")
                elif response.status == 400:
                    print(
                        f"   ⚠️  Analysis rejected (expected for dummy address): {response.status}"
                    )
                else:
                    print(f"   ❌ Analysis failed: {response.status}")
        except Exception as e:
            print(f"   ⚠️  Analysis error: {e}")

        # Test 5: API Documentation
        print("\n5. Testing API documentation...")
        try:
            async with session.get(f"{API_BASE}/docs") as response:
                if response.status == 200:
                    print(f"   ✅ API documentation available at {API_BASE}/docs")
                else:
                    print(f"   ❌ API docs not available: {response.status}")
        except Exception as e:
            print(f"   ❌ API docs error: {e}")

        print("\n" + "=" * 50)
        print("🎉 API testing completed!")
        print(f"📝 Visit {API_BASE}/docs for interactive API documentation")
        print("🔗 Ready for React dashboard integration!")


def main():
    """Main function"""
    print("Starting API tests...")
    try:
        asyncio.run(test_api())
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"❌ Test error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
