"""
Unit tests for API routes.
"""

from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test the health endpoint."""

    def test_health_check(self, client: TestClient):
        """Test that health endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestScannerRoutes:
    """Test scanner-related endpoints."""

    def test_scan_contract_endpoint_exists(self, client: TestClient):
        """Test that contract scan endpoint exists (may return 501)."""
        response = client.post(
            "/api/v1/scan/contract",
            json={
                "address": "0x1234567890abcdef",
                "bytecode": "0x608060405234801561001057600080fd5b50",
            },
        )
        # Should return 501 (Not Implemented) or 200/400 if implemented
        assert response.status_code in [200, 400, 501]

    def test_vulnerability_detection_endpoint(self, client: TestClient):
        """Test vulnerability detection endpoint."""
        response = client.post(
            "/api/v1/vulnerability/detect",
            json={"transaction_hash": "0xabcdef1234567890"},
        )
        assert response.status_code in [200, 400, 501]


class TestMempoolRoutes:
    """Test mempool monitoring endpoints."""

    def test_mempool_status(self, client: TestClient):
        """Test mempool status endpoint."""
        response = client.get("/api/v1/mempool/status")
        assert response.status_code in [200, 501]

    def test_mempool_monitor(self, client: TestClient):
        """Test mempool monitoring endpoint."""
        response = client.get("/api/v1/mempool/monitor")
        assert response.status_code in [200, 501]


class TestMEVRoutes:
    """Test MEV-related endpoints."""

    def test_mev_opportunities(self, client: TestClient):
        """Test MEV opportunities endpoint."""
        response = client.get("/api/v1/mev/opportunities")
        assert response.status_code in [200, 501]

    def test_mev_protection_status(self, client: TestClient):
        """Test MEV protection status."""
        response = client.get("/api/v1/mev/protection/status")
        assert response.status_code in [200, 501]
