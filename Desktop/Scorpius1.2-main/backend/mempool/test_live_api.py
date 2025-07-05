#!/usr/bin/env python3
"""
Test Live API Server
Start the FastAPI server briefly to test it can serve requests.
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path

import requests

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


async def test_live_server():
    """Test the API server by starting it and making requests"""
    print("🚀 Starting FastAPI server for testing...")

    # Start server in background
    server_process = None
    try:
        # Start the server process
        server_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "api.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
                "--log-level",
                "warning",  # Reduce log noise
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(Path(__file__).parent),
        )

        print("⏳ Waiting for server to start...")
        await asyncio.sleep(3)  # Give server time to start

        # Test endpoints
        base_url = "http://127.0.0.1:8000"

        tests = [
            ("Root Endpoint", f"{base_url}/"),
            ("Health Check", f"{base_url}/health"),
            ("Detailed Health", f"{base_url}/health/detailed"),
            ("Metrics", f"{base_url}/metrics"),
        ]

        print("\n📡 Testing API endpoints...")
        results = []

        for test_name, url in tests:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {test_name}: {response.status_code}")
                    results.append(True)
                else:
                    print(f"⚠️  {test_name}: {response.status_code}")
                    results.append(False)
            except requests.exceptions.RequestException as e:
                print(f"❌ {test_name}: Connection failed - {e}")
                results.append(False)

        print(f"\n📊 Live server test: {sum(results)}/{len(results)} endpoints working")

        return all(results)

    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False

    finally:
        # Clean up server process
        if server_process:
            print("\n🛑 Stopping test server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait()


def main():
    """Run live server test"""
    print("🔍 Elite Mempool System - Live API Server Test")
    print("=" * 60)

    try:
        result = asyncio.run(test_live_server())

        if result:
            print("🎉 Live API server test completed successfully!")
            print("✅ The FastAPI server can start and serve requests.")
            return 0
        else:
            print("⚠️  Some endpoints failed. Server may have issues.")
            return 1

    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
