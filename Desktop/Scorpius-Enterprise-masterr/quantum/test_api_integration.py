"""
API Test Script for Scorpius Enterprise Platform
Tests FastAPI endpoints and WebSocket connections for React dashboard integration.
"""

import asyncio
import json
from datetime import datetime

import aiohttp
import websockets

# API Configuration
API_BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"
AUTH_TOKEN = "demo-token"


async def test_rest_endpoints():
    """Test REST API endpoints."""
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}

    async with aiohttp.ClientSession() as session:
        print("🔍 Testing REST API Endpoints...")

        # Test health endpoint
        try:
            async with session.get(f"{API_BASE_URL}/health") as response:
                data = await response.json()
                print(f"✅ Health Check: {data['status']}")
        except Exception as e:
            print(f"❌ Health Check failed: {e}")

        # Test platform status
        try:
            async with session.get(
                f"{API_BASE_URL}/status", headers=headers
            ) as response:
                data = await response.json()
                print(f"✅ Platform Status: {data.get('overall_health', 'N/A')}% health")
        except Exception as e:
            print(f"❌ Platform Status failed: {e}")

        # Test dashboard stats
        try:
            async with session.get(
                f"{API_BASE_URL}/dashboard/stats", headers=headers
            ) as response:
                data = await response.json()
                print(
                    f"✅ Dashboard Stats: {data.get('total_encryptions_today', 0)} encryptions today"
                )
        except Exception as e:
            print(f"❌ Dashboard Stats failed: {e}")

        # Test quantum encryption
        try:
            encrypt_data = {
                "message": "Hello, Quantum World!",
                "algorithm": "lattice_based",
                "security_level": 3,
            }
            async with session.post(
                f"{API_BASE_URL}/quantum/encrypt", json=encrypt_data, headers=headers
            ) as response:
                data = await response.json()
                print(f"✅ Quantum Encryption: {data.get('status', 'unknown')}")
        except Exception as e:
            print(f"❌ Quantum Encryption failed: {e}")

        # Test security scan
        try:
            scan_data = {"target": "192.168.1.1", "scan_type": "quick"}
            async with session.post(
                f"{API_BASE_URL}/security/scan", json=scan_data, headers=headers
            ) as response:
                data = await response.json()
                print(f"✅ Security Scan: {data.get('threats_found', 0)} threats found")
        except Exception as e:
            print(f"❌ Security Scan failed: {e}")

        # Test analytics metrics
        try:
            async with session.get(
                f"{API_BASE_URL}/analytics/metrics", headers=headers
            ) as response:
                data = await response.json()
                print(f"✅ Analytics Metrics: Retrieved performance data")
        except Exception as e:
            print(f"❌ Analytics Metrics failed: {e}")


async def test_websocket_connection():
    """Test WebSocket connections."""
    print("\n🔌 Testing WebSocket Connections...")

    try:
        # Test dashboard WebSocket
        uri = f"{WS_BASE_URL}/ws/dashboard"
        async with websockets.connect(uri) as websocket:
            print("✅ Dashboard WebSocket connected")

            # Send subscription message
            subscribe_msg = {
                "type": "subscribe",
                "events": ["security_scan", "quantum_operation", "threat_notification"],
            }
            await websocket.send(json.dumps(subscribe_msg))

            # Wait for confirmation
            response = await websocket.recv()
            data = json.loads(response)
            print(f"✅ Subscription confirmed: {data.get('type')}")

            # Send ping
            await websocket.send(json.dumps({"type": "ping"}))
            response = await websocket.recv()
            data = json.loads(response)
            print(f"✅ Ping response: {data.get('type')}")

    except Exception as e:
        print(f"❌ Dashboard WebSocket failed: {e}")

    try:
        # Test metrics WebSocket
        uri = f"{WS_BASE_URL}/ws/metrics"
        async with websockets.connect(uri) as websocket:
            print("✅ Metrics WebSocket connected")

            # Wait for a metrics update
            response = await asyncio.wait_for(websocket.recv(), timeout=10)
            data = json.loads(response)
            print(f"✅ Metrics received: {data.get('type')}")

    except asyncio.TimeoutError:
        print("⚠️ Metrics WebSocket timeout (expected)")
    except Exception as e:
        print(f"❌ Metrics WebSocket failed: {e}")


async def test_dashboard_specific_endpoints():
    """Test dashboard-specific endpoints."""
    print("\n📊 Testing Dashboard-Specific Endpoints...")

    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}

    async with aiohttp.ClientSession() as session:
        # Test activity log
        try:
            async with session.get(
                f"{API_BASE_URL}/dashboard/activity?limit=5", headers=headers
            ) as response:
                data = await response.json()
                print(f"✅ Activity Log: {len(data)} entries retrieved")
        except Exception as e:
            print(f"❌ Activity Log failed: {e}")

        # Test system resources
        try:
            async with session.get(
                f"{API_BASE_URL}/dashboard/resources", headers=headers
            ) as response:
                data = await response.json()
                print(f"✅ System Resources: CPU {data.get('cpu_usage_percent', 0)}%")
        except Exception as e:
            print(f"❌ System Resources failed: {e}")

        # Test alerts
        try:
            async with session.get(
                f"{API_BASE_URL}/dashboard/alerts?limit=3", headers=headers
            ) as response:
                data = await response.json()
                print(f"✅ Alerts: {len(data)} alerts retrieved")
        except Exception as e:
            print(f"❌ Alerts failed: {e}")

        # Test quick action
        try:
            action_data = {"action": "system_health_check", "parameters": {}}
            async with session.post(
                f"{API_BASE_URL}/dashboard/quick-action",
                json=action_data,
                headers=headers,
            ) as response:
                data = await response.json()
                print(f"✅ Quick Action: {data.get('action')} executed")
        except Exception as e:
            print(f"❌ Quick Action failed: {e}")

        # Test dashboard config
        try:
            async with session.get(
                f"{API_BASE_URL}/dashboard/config", headers=headers
            ) as response:
                data = await response.json()
                print(f"✅ Dashboard Config: Role {data.get('role', 'unknown')}")
        except Exception as e:
            print(f"❌ Dashboard Config failed: {e}")


async def main():
    """Run all API tests."""
    print("🚀 Scorpius Enterprise API Test Suite")
    print("=" * 50)

    # Basic REST endpoints
    await test_rest_endpoints()

    # Dashboard-specific endpoints
    await test_dashboard_specific_endpoints()

    # WebSocket connections
    await test_websocket_connection()

    print("\n" + "=" * 50)
    print("✨ API test suite completed!")
    print("\n📝 For React integration:")
    print("- Use axios or fetch for REST API calls")
    print("- Use WebSocket API for real-time updates")
    print("- Include 'Authorization: Bearer demo-token' header")
    print("- API docs available at: http://localhost:8000/docs")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
