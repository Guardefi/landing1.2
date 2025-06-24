"""
Focused test suite for key modules - targeting 75% coverage
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


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "timestamp" in data
    assert "uptime" in data


def test_health_endpoint(client):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "warning", "unhealthy"]
    assert "checks" in data


def test_system_status_endpoint(client):
    """Test system status endpoint"""
    response = client.get("/api/system/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "modules" in data


def test_dashboard_stats_endpoint(client):
    """Test dashboard stats endpoint"""
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "threats_detected" in data
    assert "contracts_scanned" in data


def test_scanner_scan_endpoint(client):
    """Test scanner scan endpoint"""
    payload = {
        "target": "0x1234567890123456789012345678901234567890",
        "scan_type": "full",
    }
    response = client.post("/api/scanner/scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "scan_id" in data or "scanId" in data
