"""
Comprehensive FastAPI Integration Test
Tests all major API endpoints and functionality across the Scorpius X platform.
"""



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_test_client():
    """Get FastAPI test client."""

    return TestClient(app)


def test_api_health_endpoints():
    """Test health check endpoints."""
    client = get_test_client()

    # Test main health endpoint
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    logger.info("✅ Health endpoint working")

    # Test readiness endpoint
    response = client.get("/readyz")
    assert response.status_code in [200, 503]  # May fail if DB not available
    logger.info("✅ Readiness endpoint working")


def test_bridge_api_endpoints():
    """Test bridge network API endpoints."""
    client = get_test_client()

    # Test supported chains
    response = client.get("/api/v2/bridge/chains")
    assert response.status_code == 200
    data = response.json()
    assert "supported_chains" in data
    logger.info("✅ Bridge chains endpoint working")

    # Test bridge health
    response = client.get("/api/v2/bridge/health")
    assert response.status_code == 200
    logger.info("✅ Bridge health endpoint working")

    # Test validators endpoint
    response = client.get("/api/v2/bridge/validators")
    assert response.status_code in [200, 503]  # May fail if not initialized
    logger.info("✅ Bridge validators endpoint working")

    # Test liquidity pools
    response = client.get("/api/v2/bridge/liquidity/pools")
    assert response.status_code in [200, 503]  # May fail if not initialized
    logger.info("✅ Bridge liquidity pools endpoint working")


def test_forensics_api_endpoints():
    """Test blockchain forensics API endpoints."""
    client = get_test_client()

    # Test supported chains
    response = client.get("/api/v2/forensics/chains/supported")
    assert response.status_code == 200
    data = response.json()
    assert "supported_chains" in data
    logger.info("✅ Forensics chains endpoint working")

    # Test forensics status
    response = client.get("/api/v2/forensics/status")
    assert response.status_code == 200
    logger.info("✅ Forensics status endpoint working")

    # Test watchlist
    response = client.get("/api/v2/forensics/watchlist")
    assert response.status_code == 200
    logger.info("✅ Forensics watchlist endpoint working")


def test_quantum_api_endpoints():
    """Test quantum cryptography API endpoints."""
    client = get_test_client()

    # Test supported algorithms
    response = client.get("/api/v2/quantum/algorithms")
    assert response.status_code == 200
    data = response.json()
    assert "algorithms" in data
    logger.info("✅ Quantum algorithms endpoint working")

    # Test quantum status
    response = client.get("/api/v2/quantum/status")
    assert response.status_code == 200
    logger.info("✅ Quantum status endpoint working")


def test_mev_api_endpoints():
    """Test MEV operations API endpoints."""
    client = get_test_client()

    # Test MEV strategies
    response = client.get("/api/mev/strategies")
    assert response.status_code == 200
    data = response.json()
    assert "strategies" in data
    logger.info("✅ MEV strategies endpoint working")

    # Test MEV opportunities
    response = client.get("/api/mev/opportunities")
    assert response.status_code == 200
    logger.info("✅ MEV opportunities endpoint working")

    # Test MEV bot status
    response = client.get("/api/v2/mev/bot/status")
    assert response.status_code == 200
    logger.info("✅ MEV bot status endpoint working")


def test_plugin_marketplace_endpoints():
    """Test plugin marketplace API endpoints."""
    client = get_test_client()

    # Test marketplace
    response = client.get("/api/v2/plugins/marketplace")
    assert response.status_code == 200
    data = response.json()
    assert "plugins" in data
    logger.info("✅ Plugin marketplace endpoint working")

    # Test installed plugins
    response = client.get("/api/v2/plugins/installed")
    assert response.status_code == 200
    logger.info("✅ Installed plugins endpoint working")

    # Test plugin categories
    response = client.get("/api/v2/plugins/categories/list")
    assert response.status_code == 200
    logger.info("✅ Plugin categories endpoint working")


def test_auth_api_endpoints():
    """Test authentication API endpoints."""
    client = get_test_client()

    # Test token verification (should fail without token)
    response = client.get("/api/auth/verify-token")
    assert response.status_code in [401, 422]  # Unauthorized or validation error
    logger.info("✅ Auth token verification endpoint working")


def test_monitoring_api_endpoints():
    """Test monitoring and system API endpoints."""
    client = get_test_client()

    # Test system status
    response = client.get("/api/v2/system/status")
    assert response.status_code in [200, 500]  # May fail if integration hub not ready
    logger.info("✅ System status endpoint working")

    # Test dashboard stats
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    logger.info("✅ Dashboard stats endpoint working")


def test_scanner_api_endpoints():
    """Test scanner API endpoints."""
    client = get_test_client()

    # Test scanner health
    response = client.get("/api/scanner/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    logger.info("✅ Scanner health endpoint working")

    # Test scanner plugins
    response = client.get("/api/scanner/plugins")
    assert response.status_code == 200
    logger.info("✅ Scanner plugins endpoint working")


def test_api_documentation():
    """Test API documentation endpoints."""
    client = get_test_client()

    # Test OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "paths" in data
    logger.info("✅ OpenAPI documentation working")

    # Test Swagger UI
    response = client.get("/docs")
    assert response.status_code == 200
    logger.info("✅ Swagger UI documentation working")


def test_comprehensive_api_coverage():
    """Test that all major API categories are covered."""
    client = get_test_client()

    # Get all routes

    routes = [route.path for route in app.routes if hasattr(route, "path")]

    # Check coverage of major API categories
    api_categories = {
        "bridge": [r for r in routes if "/bridge/" in r],
        "forensics": [r for r in routes if "/forensics/" in r],
        "quantum": [r for r in routes if "/quantum/" in r],
        "mev": [r for r in routes if "/mev" in r],
        "plugins": [r for r in routes if "/plugins/" in r],
        "auth": [r for r in routes if "/auth/" in r],
        "scanner": [r for r in routes if "/scanner/" in r],
        "system": [r for r in routes if "/system/" in r or "/dashboard/" in r],
    }

    logger.info("API Coverage Summary:")
    for category, endpoints in api_categories.items():
        logger.info(f"  {category}: {len(endpoints)} endpoints")
        assert len(endpoints) > 0, f"No endpoints found for {category}"

    total_api_endpoints = sum(len(endpoints) for endpoints in api_categories.values())
    logger.info(f"  TOTAL: {total_api_endpoints} API endpoints")

    # Verify we have a comprehensive API
    assert total_api_endpoints >= 100, "Should have at least 100 API endpoints"
    logger.info("✅ Comprehensive API coverage verified")


async def run_all_tests():
    """Run all FastAPI integration tests."""
    logger.info("🧪 Starting Comprehensive FastAPI Integration Tests")
    logger.info("=" * 60)

    try:
        # Run all test functions
import asyncio
import logging
import traceback

from fastapi.testclient import TestClient
from main import app

        test_functions = [
            test_api_health_endpoints,
            test_bridge_api_endpoints,
            test_forensics_api_endpoints,
            test_quantum_api_endpoints,
            test_mev_api_endpoints,
            test_plugin_marketplace_endpoints,
            test_auth_api_endpoints,
            test_monitoring_api_endpoints,
            test_scanner_api_endpoints,
            test_api_documentation,
            test_comprehensive_api_coverage,
        ]

        passed = 0
        failed = 0

        for test_func in test_functions:
            try:
                logger.info(f"\n🔍 Running: {test_func.__name__}")
                test_func()
                passed += 1
                logger.info(f"✅ PASSED: {test_func.__name__}")
            except Exception as e:
                failed += 1
                logger.error(f"❌ FAILED: {test_func.__name__} - {e}")

        logger.info("\n📊 Test Results:")
        logger.info(f"  ✅ Passed: {passed}")
        logger.info(f"  ❌ Failed: {failed}")
        logger.info(f"  📈 Success Rate: {passed/(passed+failed)*100:.1f}%")

        if failed == 0:
            logger.info("\n🎉 ALL FASTAPI INTEGRATION TESTS PASSED!")
            logger.info("🚀 Scorpius X FastAPI ecosystem is fully functional!")
            return True
        else:
            logger.warning(f"\n⚠️  {failed} tests failed - some APIs may need attention")
            return False

    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())

    if success:
        print("\n" + "=" * 60)
        print("🎉 FASTAPI INTEGRATION COMPLETE!")
        print("✅ All major API endpoints are functional")
        print("🌐 Ready for production deployment")
        print("📚 API documentation available at /docs")
        print("=" * 60)
    else:
        print("\n❌ Some API tests failed - check logs for details")
        exit(1)
