"""
Test suite for Scorpius Enterprise Platform
"""

import asyncio
import os
import sys
from unittest.mock import Mock, patch
import httpx

import pytest

# Add the parent directory to the path so we can import scorpius
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


class TestScorpiusEnterprise:
    """Test suite for Scorpius Enterprise features."""

    @pytest.mark.asyncio
    async def test_platform_initialization(self):
        """Test platform initialization."""
        from scorpius import initialize_scorpius

        # Test initialization with valid license
        success = await initialize_scorpius(license_key="TEST-LICENSE-KEY")

        assert success == True

    @pytest.mark.asyncio
    async def test_engine_functionality(self):
        """Test core engine functionality."""
        from scorpius import get_engine, initialize_scorpius

        # Initialize platform
        await initialize_scorpius(license_key="TEST-LICENSE-KEY")
        engine = get_engine()

        # Test quantum encryption
        result = await engine.quantum_encrypt(
            message=b"test message", algorithm="lattice_based", security_level=3
        )

        assert "encrypted_data" in result
        assert result["algorithm"] == "lattice_based"
        assert result["security_level"] == 3

        # Test security scan
        scan_result = await engine.security_scan(
            target="test-target", scan_type="comprehensive"
        )

        assert "target" in scan_result
        assert scan_result["target"] == "test-target"

        # Test analytics report
        report = await engine.generate_analytics_report(
            report_type="security", timeframe="24h"
        )

        assert "report_type" in report
        assert report["report_type"] == "security"

    @pytest.mark.asyncio
    async def test_platform_status(self):
        """Test platform status reporting."""
        from scorpius import get_engine, initialize_scorpius

        # Initialize platform
        await initialize_scorpius(license_key="TEST-LICENSE-KEY")
        engine = get_engine()

        # Get platform status
        status = await engine.get_platform_status()

        assert "platform_version" in status
        assert "uptime_seconds" in status
        assert "total_modules" in status
        assert "active_modules" in status
        assert "overall_health" in status
        assert "is_enterprise" in status
        assert status["is_enterprise"] == True


class TestConfiguration:
    """Test configuration management."""

    def test_config_creation(self):
        """Test configuration creation."""
        from scorpius.core.config import ScorpiusConfig

        config = ScorpiusConfig()

        assert config.log_level == "INFO"
        assert config.enable_clustering == False
        assert config.quantum_config.default_algorithm == "lattice_based"
        assert config.security_config.enable_ai_detection == True

    def test_config_from_dict(self):
        """Test configuration creation from dictionary."""
        from scorpius.core.config import ScorpiusConfig

        config_data = {
            "log_level": "DEBUG",
            "enable_clustering": True,
            "quantum_config": {
                "default_algorithm": "hash_based",
                "default_security_level": 5,
            },
        }

        config = ScorpiusConfig._create_from_dict(config_data)

        assert config.log_level == "DEBUG"
        assert config.enable_clustering == True
        assert config.quantum_config.default_algorithm == "hash_based"
        assert config.quantum_config.default_security_level == 5


class TestLicenseManager:
    """Test license management."""

    @pytest.mark.asyncio
    async def test_license_validation(self):
        """Test license validation."""
        from scorpius.core.licensing import LicenseManager

        license_manager = LicenseManager()

        # Test valid license
        valid = await license_manager.validate_license("VALID-LICENSE-KEY-12345")
        assert valid == True

        # Test invalid license
        invalid = await license_manager.validate_license("INVALID")
        assert invalid == False

        # Test None license (development mode)
        dev_mode = await license_manager.validate_license(None)
        assert dev_mode == True

    @pytest.mark.asyncio
    async def test_license_server_responses(self, monkeypatch):
        """Test validation against external license server."""
        from scorpius.core.licensing import LicenseManager

        async def mock_post(self, url, json=None, **kwargs):
            class MockResponse:
                def __init__(self, data):
                    self.status_code = 200
                    self._data = data

                def json(self):
                    return self._data

            if json and json.get("license_key") == "VALID-SERVER-KEY":
                return MockResponse({"valid": True, "info": {"type": "enterprise", "expires": "2099-01-01T00:00:00", "features": ["quantum"]}})
            return MockResponse({"valid": False})

        monkeypatch.setenv("LICENSE_SERVER_URL", "https://license.test/validate")
        monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

        manager = LicenseManager()

        valid = await manager.validate_license("VALID-SERVER-KEY")
        assert valid is True
        assert manager.license_info["type"] == "enterprise"

        invalid = await manager.validate_license("BAD-SERVER-KEY")
        assert invalid is False


class TestHealthChecker:
    """Test health monitoring."""

    @pytest.mark.asyncio
    async def test_module_health_check(self):
        """Test module health checking."""
        from scorpius.core.health import HealthChecker

        health_checker = HealthChecker()

        # Test healthy module
        healthy_module = {"status": "initialized"}
        health_score = await health_checker.check_module_health(healthy_module)
        assert health_score == 1.0

        # Test unhealthy module
        unhealthy_module = {"status": "error"}
        health_score = await health_checker.check_module_health(unhealthy_module)
        assert health_score == 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
