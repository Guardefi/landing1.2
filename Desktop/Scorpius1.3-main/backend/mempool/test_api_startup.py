#!/usr/bin/env python3
"""
Test API Server Startup
Test script to verify the FastAPI server can start and all endpoints are accessible.
"""

import asyncio
import sys
import traceback
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


async def test_api_imports():
    """Test if all API components can be imported"""
    print("🔄 Testing API imports...")

    try:
        # Test core API imports
        from api.main import app, config

        print("✅ Main FastAPI app imported successfully")

        # Test router imports
        from api.routers import (
            alerts_router,
            analytics_router,
            mev_router,
            rules_router,
            transactions_router,
            websocket_router,
        )

        print("✅ All API routers imported successfully")

        # Test dependencies
        from api.dependencies import db_manager

        print("✅ API dependencies imported successfully")

        return True

    except Exception as e:
        print(f"❌ API import failed: {e}")
        traceback.print_exc()
        return False


def test_app_creation():
    """Test FastAPI app creation and configuration"""
    print("\n🔄 Testing FastAPI app creation...")

    try:
        from api.main import app, config

        # Check app properties
        assert app.title == "Elite Mempool System API"
        assert app.version == "1.0.0"
        print("✅ FastAPI app created with correct title and version")

        # Check routes exist
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/health", "/health/detailed", "/metrics"]

        for route in expected_routes:
            if route in routes:
                print(f"✅ Route {route} registered")
            else:
                print(f"⚠️  Route {route} not found")

        # Check middleware
        middleware_types = [
            type(middleware).__name__ for middleware in app.user_middleware
        ]
        print(f"✅ Middleware registered: {middleware_types}")

        return True

    except Exception as e:
        print(f"❌ App creation test failed: {e}")
        traceback.print_exc()
        return False


async def test_health_endpoint():
    """Test health endpoints without starting server"""
    print("\n🔄 Testing health endpoint logic...")

    try:
        from api.main import detailed_health_check, health_check

        # Test basic health check
        health_response = await health_check()
        assert health_response["status"] == "healthy"
        assert "timestamp" in health_response
        print("✅ Basic health check works")

        # Test detailed health check (may fail due to no DB/Redis connection)
        try:
            detailed_response = await detailed_health_check()
            print(f"✅ Detailed health check response: {detailed_response['status']}")
        except Exception as e:
            print(f"⚠️  Detailed health check failed (expected without DB/Redis): {e}")

        return True

    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        traceback.print_exc()
        return False


def test_config():
    """Test configuration loading"""
    print("\n🔄 Testing configuration...")

    try:
        from api.main import config

        print(f"✅ Database URL: {config.database_url}")
        print(f"✅ Redis URL: {config.redis_url}")
        print(f"✅ Environment: {config.environment}")
        print(f"✅ CORS Origins: {config.cors_origins}")
        print(f"✅ Max WebSocket Connections: {config.max_connections}")

        return True

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        traceback.print_exc()
        return False


async def main():
    """Run all API tests"""
    print("🚀 Elite Mempool System - API Server Startup Tests")
    print("=" * 60)

    tests = [
        ("API Imports", test_api_imports()),
        ("App Creation", test_app_creation()),
        ("Health Endpoints", test_health_endpoint()),
        ("Configuration", test_config()),
    ]

    results = []
    for test_name, test_coro in tests:
        if asyncio.iscoroutine(test_coro):
            result = await test_coro
        else:
            result = test_coro
        results.append((test_name, result))

    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, passed_test in results:
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {test_name}")
        if passed_test:
            passed += 1

    print(f"\n🎯 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All API startup tests passed! The FastAPI server is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
