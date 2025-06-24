"""
Backend API Test Script
Simple script to test the modular backend endpoints
"""



# Backend URL
BASE_URL = "http://localhost:8001"


def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health Check: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False


def test_login():
    """Test login endpoint"""
    try:
        data = {"username": "demo", "password": "demo"}
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
        print(f"\nLogin Test: {response.status_code}")
        result = response.json()
        print(json.dumps(result, indent=2))

        if response.status_code == 200 and result.get("success"):
            return result["data"]["accessToken"]
        return None
    except Exception as e:
        print(f"Login test failed: {e}")
        return None


def test_dashboard_stats(token):
    """Test dashboard stats endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)
        print(f"\nDashboard Stats: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Dashboard stats retrieved successfully")
            print(f"Threats detected: {result['data'].get('threatsDetected', 'N/A')}")
            print(f"Active scans: {result['data'].get('activeScans', 'N/A')}")
        else:
            print(response.text)
        return response.status_code == 200
    except Exception as e:
        print(f"Dashboard stats test failed: {e}")
        return False


def test_scanner_analyze(token):
    """Test scanner analyze endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "contractAddress": "0x1234567890123456789012345678901234567890",
            "scanType": "full",
        }
        response = requests.post(
            f"{BASE_URL}/api/scanner/analyze", json=data, headers=headers
        )
        print(f"\nScanner Analyze: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Scanner analysis completed successfully")
            print(
                f"Security score: {result['data']['results'].get('securityScore', 'N/A')}"
            )
        else:
            print(response.text)
        return response.status_code == 200
    except Exception as e:
        print(f"Scanner analyze test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Testing Scorpius Backend API...")
    print("=" * 50)
import json

import requests

    # Test health endpoint
    if not test_health():
        print("❌ Health check failed!")
        return

    # Test login
    token = test_login()
    if not token:
        print("❌ Login failed!")
        return

    print("✅ Login successful!")

    # Test authenticated endpoints
    success_count = 0
    total_tests = 2

    if test_dashboard_stats(token):
        print("✅ Dashboard stats test passed!")
        success_count += 1
    else:
        print("❌ Dashboard stats test failed!")

    if test_scanner_analyze(token):
        print("✅ Scanner analyze test passed!")
        success_count += 1
    else:
        print("❌ Scanner analyze test failed!")

    print("\n" + "=" * 50)
    print(
        f"🎯 Test Results: {success_count}/{total_tests} authenticated endpoints passed"
    )

    if success_count == total_tests:
        print("🎉 All tests passed! The modular backend is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the implementation.")


if __name__ == "__main__":
    main()
