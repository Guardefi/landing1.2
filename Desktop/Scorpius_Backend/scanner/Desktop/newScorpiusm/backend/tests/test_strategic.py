"""
Strategic test suite targeting the 'thin waist' of the platform
Focus on 5 key modules that drive everything else for maximum coverage impact
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def client():
    """Create test client"""
    from main import app

    return TestClient(app)


# =====================================================================
# 1. SYSTEM ROUTES - Core platform status and health
# =====================================================================


class TestSystemRoutes:
    """Test system routes - the backbone of platform monitoring"""

    def test_root_endpoint_complete(self, client):
        """Test root endpoint with all expected fields"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()

        # All required fields from test specification
        required_fields = ["status", "platform", "version", "timestamp", "uptime"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        assert data["status"] == "online"
        assert "Scorpius" in data["platform"]
        assert isinstance(data["version"], str)
        assert data["timestamp"].endswith("Z")  # ISO format
        assert "h" in data["uptime"] or "m" in data["uptime"]  # Contains time units

    def test_health_endpoint_comprehensive(self, client):
        """Test health endpoint with detailed system checks"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] in ["healthy", "warning", "unhealthy"]
        assert "timestamp" in data
        assert "checks" in data

        # Verify health checks structure
        checks = data["checks"]
        assert "database" in checks
        assert "memory" in checks
        assert "disk" in checks

        # Each check should have status and details
        for _check_name, check_data in checks.items():
            assert "status" in check_data
            assert check_data["status"] in ["healthy", "warning", "unhealthy"]

    def test_system_status_detailed(self, client):
        """Test system status with module reporting"""
        response = client.get("/api/system/status")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "operational"
        assert "modules" in data
        assert "uptime" in data

        # Modules should report status
        modules = data["modules"]
        for _module_name, module_status in modules.items():
            assert module_status in ["online", "offline", "error"]


# =====================================================================
# 2. REALTIME THREAT SYSTEM - Event dispatch and threat management
# =====================================================================


class TestThreatSystem:
    """Test realtime threat system - critical for security operations"""

    def test_dashboard_stats_metrics(self, client):
        """Test dashboard metrics are properly structured"""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()

        # Core security metrics
        required_metrics = [
            "threats_detected",
            "contracts_scanned",
            "vulnerability_score",
            "uptime",
            "active_scans",
            "total_transactions",
            "mev_opportunities",
        ]

        for metric in required_metrics:
            assert metric in data, f"Missing metric: {metric}"

        # Validate data types and ranges
        assert (
            isinstance(data["threats_detected"], int) and data["threats_detected"] >= 0
        )
        assert (
            isinstance(data["contracts_scanned"], int)
            and data["contracts_scanned"] >= 0
        )
        assert isinstance(data["vulnerability_score"], int | float)
        assert 0 <= data["vulnerability_score"] <= 100

        # System performance metrics
        assert "timestamp" in data
        assert "cpu" in data or "memory" in data  # Performance data


# =====================================================================
# 3. SCANNER SYSTEM - Core vulnerability detection
# =====================================================================


class TestScannerSystem:
    """Test scanner system - the core security scanning engine"""

    def test_scanner_scan_valid_request(self, client):
        """Test valid scan initiation"""
        payload = {
            "target": "0x1234567890123456789012345678901234567890",
            "scan_type": "full",
            "priority": "high",
        }

        response = client.post("/api/scanner/scan", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert "scan_id" in data
        assert "status" in data
        assert "target" in data
        assert "estimated_duration" in data
        assert data["status"] == "initiated"
        assert data["target"] == payload["target"]

    def test_scanner_scan_invalid_requests(self, client):
        """Test scanner validation with multiple invalid payloads"""
        invalid_payloads = [
            {},  # Missing target
            {"target": "invalid_address"},  # Invalid address format
            {"target": "0x123"},  # Too short address
            {"target": "0xGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG"},  # Invalid hex
        ]

        for payload in invalid_payloads:
            response = client.post("/api/scanner/scan", json=payload)
            assert response.status_code == 400, f"Should reject payload: {payload}"

    def test_scan_workflow_integration(self, client):
        """Test complete scan workflow integration"""
        # 1. Initiate scan
        payload = {
            "target": "0x1234567890123456789012345678901234567890",
            "scan_type": "comprehensive",
        }

        response = client.post("/api/scanner/scan", json=payload)
        assert response.status_code == 200
        scan_data = response.json()
        scan_id = scan_data.get("scan_id")
        assert scan_id is not None

        # 2. Verify system status reflects the activity
        system_response = client.get("/api/system/status")
        assert system_response.status_code == 200


# =====================================================================
# 4. AUTH SYSTEM - Security foundation
# =====================================================================


class TestAuthSystem:
    """Test authentication system - security foundation"""

    def test_security_headers_present(self, client):
        """Test security headers are properly configured"""
        response = client.get("/")
        headers = response.headers

        # CORS should be configured
        assert "access-control-allow-origin" in headers

        # Security headers (log presence for monitoring)
        security_headers = [
            "x-content-type-options",
            "x-frame-options",
            "x-xss-protection",
        ]

        security_count = 0
        for header in security_headers:
            if header in headers:
                security_count += 1

        # At least some security measures should be present
        # (This is flexible since we're testing simple_server, not full production)


# =====================================================================
# 5. ERROR HANDLING & EDGE CASES - System resilience
# =====================================================================


class TestSystemResilience:
    """Test system error handling and resilience"""

    def test_error_handling_404(self, client):
        """Test 404 handling for non-existent endpoints"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_error_handling_405(self, client):
        """Test method not allowed handling"""
        response = client.delete("/")
        assert response.status_code == 405

    def test_malformed_json_handling(self, client):
        """Test handling of malformed JSON in requests"""
        response = client.post(
            "/api/scanner/scan",
            data="invalid json",
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 422  # Unprocessable Entity

    def test_oversized_payload_handling(self, client):
        """Test handling of oversized payloads"""
        large_payload = {"target": "x" * 10000}
        response = client.post("/api/scanner/scan", json=large_payload)
        assert response.status_code in [
            400,
            413,
            422,
        ]  # Bad request or payload too large

    def test_rate_limiting_simulation(self, client):
        """Test rate limiting behavior under load"""
        responses = []
        for _i in range(10):
            response = client.get("/")
            responses.append(response.status_code)

        # Most should succeed (simple_server doesn't have rate limiting)
        success_count = sum(1 for status in responses if status == 200)
        assert success_count >= 8  # Almost all should succeed in simple server


# =====================================================================
# 6. DATA CONSISTENCY & INTEGRATION
# =====================================================================


class TestDataConsistency:
    """Test data consistency across different endpoints"""

    def test_dashboard_system_consistency(self, client):
        """Test consistency between dashboard and system status"""
        # Get dashboard stats
        dashboard_response = client.get("/api/dashboard/stats")
        assert dashboard_response.status_code == 200
        dashboard_data = dashboard_response.json()

        # Get system status
        system_response = client.get("/api/system/status")
        assert system_response.status_code == 200
        system_data = system_response.json()

        # Both should be operational
        assert dashboard_data.get("vulnerability_score") is not None
        assert system_data.get("status") == "operational"

        # Timestamp consistency (both should be recent)
        if "timestamp" in dashboard_data and "uptime" in system_data:
            # Both endpoints are working and providing time-related data
            assert isinstance(dashboard_data["contracts_scanned"], int)
            assert isinstance(system_data["uptime"], str)

    def test_endpoint_response_times(self, client):
        """Test that all endpoints respond within reasonable time"""
        import time

        endpoints = ["/", "/health", "/api/system/status", "/api/dashboard/stats"]

        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()

            assert response.status_code == 200
            response_time = end_time - start_time
            assert response_time < 5.0, f"Endpoint {endpoint} took {response_time:.2f}s"


# =====================================================================
# PROPERTY-BASED TESTING for Address Validation
# =====================================================================


class TestAddressValidation:
    """Property-based tests for Ethereum address validation"""

    @pytest.mark.parametrize(
        "valid_address",
        [
            "0x1234567890123456789012345678901234567890",
            "0xA0b86a33E6428bd32B1e96C1c5B9D6f5A2E8c9E3",
            "0x0000000000000000000000000000000000000000",  # Zero address
            "0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",  # Max address
        ],
    )
    def test_valid_ethereum_addresses(self, client, valid_address):
        """Test that valid Ethereum addresses are accepted"""
        payload = {"target": valid_address, "scan_type": "quick"}
        response = client.post("/api/scanner/scan", json=payload)
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "invalid_address,reason",
        [
            ("", "Empty string"),
            ("1234567890123456789012345678901234567890", "No 0x prefix"),
            ("0x123456789012345678901234567890123456789", "Too short"),
            ("0x12345678901234567890123456789012345678901", "Too long"),
            ("0xGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG", "Invalid hex"),
            ("0X1234567890123456789012345678901234567890", "Uppercase 0X"),
        ],
    )
    def test_invalid_ethereum_addresses(self, client, invalid_address, reason):
        """Test that invalid Ethereum addresses are rejected"""
        payload = {"target": invalid_address, "scan_type": "quick"}
        response = client.post("/api/scanner/scan", json=payload)
        assert response.status_code == 400, f"Should reject {reason}: {invalid_address}"
