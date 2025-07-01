#!/usr/bin/env python3
import pytest
from typing import AsyncGenerator, Generator
import tempfile
import shutil
import sys
import os
import asyncio
import time
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
# Test configuration for Scorpius Reporting Service
"""


# Set test environment
os.environ["ENVIRONMENT"] = "testing"
os.environ["DEBUG"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"
os.environ["SECRET_KEY"] = "test_secret_key"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def temp_dir() -> AsyncGenerator[str, None]:
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
async def mock_cert_files(temp_dir: str) -> dict:
    """Create mock certificate files for testing."""
    cert_dir = os.path.join(temp_dir, "certs")
    os.makedirs(cert_dir, exist_ok=True)

    # Mock certificate content
    cert_content = """-----BEGIN CERTIFICATE-----"""
# MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwJKuZRwIGJ7w1VQbVBpr
...mock certificate content...
-----END CERTIFICATE-----"""

    key_content = """-----BEGIN PRIVATE KEY-----"""
# MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDAkq5lHAgYnvDV
...mock private key content...
-----END PRIVATE KEY-----"""

    cert_path = os.path.join(cert_dir, "signing.crt")
    key_path = os.path.join(cert_dir, "signing.key")

    with open(cert_path, "w") as f:
        f.write(cert_content)

    with open(key_path, "w") as f:
        f.write(key_content)

    return {"cert_path": cert_path, "key_path": key_path, "cert_dir": cert_dir}


@pytest.fixture
def sample_pdf_request():
    """Sample PDF report request for testing."""
    return {
        "title": "Test Security Report",
        "data": {
            "executive_summary": {
    "total_issues": 10,
    "critical": 1,
    "high": 3,
    "medium": 4,
    "low": 2,
            ],
            "findings": [
                {
                    "id": "TEST-001",
                    "severity": "critical",
                    "title": "Test SQL Injection",
                    "description": "Test vulnerability description",
                ]
            },
        ],
        "template": "default",
        "metadata": {"analyst": "Test User", "client": "Test Client"},
    ]


@pytest.fixture
def sample_sarif_request():
    """Sample SARIF report request for testing."""
    return {
        "title": "Test SARIF Report",
        "scan_results": [
            {
                "rule_id": "CWE-79",
                "level": "error",
                "message": "Potential XSS vulnerability",
                "locations": [{"file_path": "test.js", "line": 42, "column": 15]],
            ]
        },
        "tool_info": {
            "name": "Test Scanner",
            "version": "1.0.0",
            "organization": "Test Org",
        ],
        "run_metadata": {"scan_type": "static_analysis"},
    ]


@pytest.fixture
def mock_api_key():
    """Mock API key for testing."""
    return "test_admin"


if __name__ == '__main__':
    print('Running test file...')

    # Run all test functions
    test_functions = [name for name in globals() if name.startswith('test_')]
    passed = 0
    failed = 0

    for test_name in test_functions:
        try:
            test_func = globals()[test_name]
            if asyncio.iscoroutinefunction(test_func):
                asyncio.run(test_func())
            else:
                test_func()
            print(f'✓ {test_name} passed')
            passed += 1
        except Exception as e:
            print(f'✗ {test_name} failed: {e}')
            failed += 1

    print(f'\nTest results: {passed} passed, {failed} failed')
    """