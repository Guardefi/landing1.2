"""
Test the FastAPI application endpoints
"""

import pytest
from fastapi.testclient import TestClient
import json

# Import the app after setting test environment
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app import app

client = TestClient(app)


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test health check returns success"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "reporting"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"


class TestMetrics:
    """Test metrics endpoint"""
    
    def test_metrics(self):
        """Test metrics endpoint returns data"""
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "reports_generated_total" in data
        assert "signatures_created_total" in data
        assert "audit_entries_total" in data
        assert "service_uptime_seconds" in data


class TestPDFReports:
    """Test PDF report generation endpoints"""
    
    def test_generate_pdf_without_auth(self, sample_pdf_request):
        """Test PDF generation without authentication fails"""
        response = client.post("/v1/reports/pdf", json=sample_pdf_request)
        assert response.status_code == 403
    
    def test_generate_pdf_with_invalid_auth(self, sample_pdf_request):
        """Test PDF generation with invalid API key fails"""
        headers = {"X-API-Key": "invalid_key"}
        response = client.post("/v1/reports/pdf", json=sample_pdf_request, headers=headers)
        assert response.status_code == 401
    
    def test_generate_pdf_with_auth(self, sample_pdf_request, mock_api_key):
        """Test PDF generation with valid authentication"""
        headers = {"Authorization": f"Bearer {mock_api_key}"}
        response = client.post("/v1/reports/pdf", json=sample_pdf_request, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "report_id" in data
        assert data["status"] == "processing"
        assert "message" in data
    
    def test_generate_pdf_invalid_data(self, mock_api_key):
        """Test PDF generation with invalid request data"""
        headers = {"Authorization": f"Bearer {mock_api_key}"}
        invalid_request = {"title": "Test", "data": {}}  # Missing required fields
        response = client.post("/v1/reports/pdf", json=invalid_request, headers=headers)
        assert response.status_code == 422  # Validation error


class TestSARIFReports:
    """Test SARIF report generation endpoints"""
    
    def test_generate_sarif_without_auth(self, sample_sarif_request):
        """Test SARIF generation without authentication fails"""
        response = client.post("/v1/reports/sarif", json=sample_sarif_request)
        assert response.status_code == 403
    
    def test_generate_sarif_with_auth(self, sample_sarif_request, mock_api_key):
        """Test SARIF generation with valid authentication"""
        headers = {"Authorization": f"Bearer {mock_api_key}"}
        response = client.post("/v1/reports/sarif", json=sample_sarif_request, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "report_id" in data
        assert data["status"] == "processing"
        assert "message" in data
    
    def test_generate_sarif_invalid_data(self, mock_api_key):
        """Test SARIF generation with invalid request data"""
        headers = {"Authorization": f"Bearer {mock_api_key}"}
        invalid_request = {"title": "Test", "scan_results": []}  # Empty scan results
        response = client.post("/v1/reports/sarif", json=invalid_request, headers=headers)
        assert response.status_code == 422  # Validation error


class TestReportStatus:
    """Test report status endpoints"""
    
    def test_report_status_without_auth(self):
        """Test report status without authentication fails"""
        response = client.get("/v1/reports/test-id/status")
        assert response.status_code == 403
    
    def test_report_status_not_found(self, mock_api_key):
        """Test report status for non-existent report"""
        headers = {"Authorization": f"Bearer {mock_api_key}"}
        response = client.get("/v1/reports/non-existent-id/status", headers=headers)
        assert response.status_code == 404


class TestReportDownload:
    """Test report download endpoints"""
    
    def test_download_without_auth(self):
        """Test report download without authentication fails"""
        response = client.get("/v1/reports/test-id/download")
        assert response.status_code == 403
    
    def test_download_not_found(self, mock_api_key):
        """Test download for non-existent report"""
        headers = {"Authorization": f"Bearer {mock_api_key}"}
        response = client.get("/v1/reports/non-existent-id/download", headers=headers)
        assert response.status_code == 404


class TestSignatureInfo:
    """Test signature information endpoints"""
    
    def test_signature_info_without_auth(self):
        """Test signature info without authentication fails"""
        response = client.get("/v1/reports/test-id/signature")
        assert response.status_code == 403
    
    def test_signature_info_not_found(self, mock_api_key):
        """Test signature info for non-existent report"""
        headers = {"Authorization": f"Bearer {mock_api_key}"}
        response = client.get("/v1/reports/non-existent-id/signature", headers=headers)
        assert response.status_code == 404
