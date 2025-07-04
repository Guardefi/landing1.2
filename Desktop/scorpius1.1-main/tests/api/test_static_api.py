import hashlib
import json

import pytest
import requests
from requests.exceptions import RequestException, ConnectionError

# Base URL for API tests
BASE_URL = "http://localhost:8000"

def is_backend_available():
    """Check if backend server is available"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        return response.status_code == 200
    except (RequestException, ConnectionError):
        return False

# Skip all tests if backend is not available
pytestmark = pytest.mark.skipif(
    not is_backend_available(),
    reason="Backend server not available at localhost:8000"
)


@pytest.mark.smoke_api
class TestStaticAPIs:
    """
    Static API test suite for backend-only fallback testing.
    These tests validate core API endpoints without frontend dependencies.
    """

    def test_health_endpoint(self):
        """Test the /api/health endpoint returns 200 and valid response."""
        response = requests.get(f"{BASE_URL}/api/health")

        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "ok", "up"]

        # Verify response time is reasonable
        assert response.elapsed.total_seconds() < 2.0

        print(f"Health check passed: {data}")

    def test_version_endpoint(self):
        """Test the /api/version endpoint returns version information."""
        response = requests.get(f"{BASE_URL}/api/version")

        assert response.status_code == 200

        data = response.json()
        required_fields = ["version", "build"]

        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Verify version format (semantic versioning)
        version = data["version"]
        assert isinstance(version, str)
        assert len(version.split(".")) >= 2  # At least major.minor

        print(f"Version info: {data}")

    @pytest.mark.parametrize(
        "invalid_address",
        [
            "",  # Empty string
            "invalid",  # Non-hex string
            "0x123",  # Too short
            "0x" + "z" * 40,  # Invalid hex characters
            "123" + "0" * 37,  # Missing 0x prefix
        ],
    )
    def test_wallet_check_invalid_addresses(self, invalid_address):
        """Test /api/wallet/check with various invalid addresses."""
        payload = {"address": invalid_address}
        response = requests.post(f"{BASE_URL}/api/wallet/check", json=payload)

        # Should return 400 for invalid addresses
        assert response.status_code == 400

        data = response.json()
        assert "error" in data or "message" in data

        print(f"Invalid address '{invalid_address}' correctly rejected: {data}")

    def test_wallet_check_valid_format(self):
        """Test /api/wallet/check with valid address format (but non-existent)."""
        # Valid format but likely non-existent address
        valid_address = "0x" + "0" * 40
        payload = {"address": valid_address}

        response = requests.post(f"{BASE_URL}/api/wallet/check", json=payload)

        # Should accept valid format, might return 404 or 200 with empty results
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            # Verify response structure
            expected_fields = ["address", "riskScore"]
            for field in expected_fields:
                assert field in data, f"Missing field: {field}"

        print(f"Valid address format test passed for: {valid_address}")

    def test_api_endpoints_cors_headers(self):
        """Test that API endpoints include proper CORS headers."""
        endpoints = ["/api/health", "/api/version"]

        for endpoint in endpoints:
            response = requests.options(f"{BASE_URL}{endpoint}")

            # Check for CORS headers
            headers = response.headers
            assert (
                "Access-Control-Allow-Origin" in headers or response.status_code == 405
            )

            print(f"CORS check for {endpoint}: {response.status_code}")

    def test_api_response_times(self):
        """Test that API endpoints respond within acceptable time limits."""
        endpoints = ["/api/health", "/api/version"]

        max_response_time = 3.0  # seconds

        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            response_time = response.elapsed.total_seconds()

            assert (
                response_time < max_response_time
            ), f"{endpoint} took {response_time}s (max: {max_response_time}s)"

            print(f"{endpoint} response time: {response_time:.3f}s")

    def test_api_content_types(self):
        """Test that API endpoints return proper content types."""
        endpoints = ["/api/health", "/api/version"]

        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")

            if response.status_code == 200:
                content_type = response.headers.get("Content-Type", "")
                assert (
                    "application/json" in content_type
                ), f"{endpoint} returned incorrect content type: {content_type}"

            print(f"{endpoint} content-type: {response.headers.get('Content-Type')}")


@pytest.mark.smoke_api
class TestAPIErrorHandling:
    """Test API error handling and edge cases."""

    def test_nonexistent_endpoint(self):
        """Test that non-existent endpoints return proper 404."""
        response = requests.get(f"{BASE_URL}/api/nonexistent")
        assert response.status_code == 404

    def test_malformed_json_request(self):
        """Test API handling of malformed JSON."""
        headers = {"Content-Type": "application/json"}
        malformed_json = '{"address": "0x123"'  # Missing closing brace

        response = requests.post(
            f"{BASE_URL}/api/wallet/check", data=malformed_json, headers=headers
        )

        assert response.status_code == 400

    def test_missing_required_fields(self):
        """Test API handling of requests with missing required fields."""
        # Empty payload
        response = requests.post(f"{BASE_URL}/api/wallet/check", json={})
        assert response.status_code == 400

        # Missing address field
        response = requests.post(
            f"{BASE_URL}/api/wallet/check", json={"wallet": "0x123"}
        )
        assert response.status_code == 400


def calculate_response_hash(response_data: dict[str, any]) -> str:
    """Calculate MD5 hash of response data for consistency testing."""
    json_str = json.dumps(response_data, sort_keys=True)
    return hashlib.md5(json_str.encode()).hexdigest()


@pytest.mark.smoke_api
class TestAPIConsistency:
    """Test API response consistency and stability."""

    def test_health_endpoint_consistency(self):
        """Test that health endpoint returns consistent structure."""
        responses = []

        # Make multiple requests
        for _ in range(3):
            response = requests.get(f"{BASE_URL}/api/health")
            if response.status_code == 200:
                responses.append(response.json())

        # All responses should have same keys
        if len(responses) > 1:
            keys_set = {frozenset(resp.keys()) for resp in responses}
            assert len(keys_set) == 1, "Health endpoint returned inconsistent structure"

        print(f"Health endpoint consistency check passed ({len(responses)} requests)")

    def test_version_endpoint_stability(self):
        """Test that version endpoint returns stable information."""
        response1 = requests.get(f"{BASE_URL}/api/version")
        response2 = requests.get(f"{BASE_URL}/api/version")

        if response1.status_code == 200 and response2.status_code == 200:
            # Version info should be identical
            assert response1.json() == response2.json()

            # Calculate hash for logging
            hash1 = calculate_response_hash(response1.json())
            hash2 = calculate_response_hash(response2.json())
            assert hash1 == hash2

            print(f"Version endpoint stability verified (hash: {hash1})")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "-m", "smoke_api"])
