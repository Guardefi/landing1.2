#!/usr/bin/env python3
"""
Security Testing Suite for Scorpius Enterprise Platform
Comprehensive security tests including authentication, authorization, 
input validation, and vulnerability assessments.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List

import aiohttp
import jwt
import pytest
import requests
import structlog

# Configure logging
logger = structlog.get_logger("security_tests")


class SecurityTestSuite:
    """Main security testing class."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.admin_token = None
        self.user_token = None

    def setup(self):
        """Setup test environment."""
        # Get admin token
        self.admin_token = self._authenticate("admin", "admin123")

        # Create test user and get token
        self._create_test_user()
        self.user_token = self._authenticate("testuser", "testpass123")

    def _authenticate(self, username: str, password: str) -> str:
        """Authenticate and return JWT token."""
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password},
        )

        if response.status_code == 200:
            return response.json()["access_token"]
        return None

    def _create_test_user(self):
        """Create a test user for testing."""
        if not self.admin_token:
            return

        headers = {"Authorization": f"Bearer {self.admin_token}"}
        user_data = {
            "username": "testuser",
            "password": "testpass123",
            "email": "test@example.com",
            "roles": ["user"],
        }

        self.session.post(
            f"{self.base_url}/auth/register", json=user_data, headers=headers
        )


class AuthenticationTests(SecurityTestSuite):
    """Authentication security tests."""

    def test_brute_force_protection(self):
        """Test brute force protection on login."""
        logger.info("Testing brute force protection")

        # Attempt multiple failed logins
        failed_attempts = 0
        for i in range(10):
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"username": "admin", "password": "wrongpassword"},
            )

            if response.status_code == 429:  # Rate limited
                logger.info("Rate limiting triggered", attempts=i + 1)
                break
            elif response.status_code == 401:
                failed_attempts += 1

        assert failed_attempts <= 5, "Brute force protection not working"

    def test_jwt_token_validation(self):
        """Test JWT token validation."""
        logger.info("Testing JWT token validation")

        # Test with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = self.session.get(
            f"{self.base_url}/api/scanner/scans", headers=headers
        )
        assert response.status_code == 401

        # Test with expired token
        expired_token = jwt.encode(
            {
                "sub": "testuser",
                "exp": datetime.utcnow() - timedelta(hours=1),
                "iat": datetime.utcnow() - timedelta(hours=2),
            },
            "secret",
            algorithm="HS256",
        )

        headers = {"Authorization": f"Bearer {expired_token}"}
        response = self.session.get(
            f"{self.base_url}/api/scanner/scans", headers=headers
        )
        assert response.status_code == 401

    def test_token_refresh(self):
        """Test token refresh mechanism."""
        logger.info("Testing token refresh")

        # Get refresh token
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json={"username": "admin", "password": "admin123"},
        )

        assert response.status_code == 200
        tokens = response.json()
        refresh_token = tokens.get("refresh_token")

        if refresh_token:
            # Use refresh token to get new access token
            refresh_response = self.session.post(
                f"{self.base_url}/auth/refresh", json={"refresh_token": refresh_token}
            )
            assert refresh_response.status_code == 200

    def test_password_complexity(self):
        """Test password complexity requirements."""
        logger.info("Testing password complexity")

        weak_passwords = ["123456", "password", "abc123", "qwerty", "admin"]

        headers = {"Authorization": f"Bearer {self.admin_token}"}

        for weak_pass in weak_passwords:
            user_data = {
                "username": f"weakuser_{weak_pass}",
                "password": weak_pass,
                "email": f"weak_{weak_pass}@example.com",
            }

            response = self.session.post(
                f"{self.base_url}/auth/register", json=user_data, headers=headers
            )
            assert response.status_code in [
                400,
                422,
            ], f"Weak password accepted: {weak_pass}"


class AuthorizationTests(SecurityTestSuite):
    """Authorization and RBAC tests."""

    def test_role_based_access(self):
        """Test role-based access control."""
        logger.info("Testing RBAC")

        # Test admin-only endpoints with user token
        user_headers = {"Authorization": f"Bearer {self.user_token}"}

        admin_endpoints = ["/admin/plugins", "/admin/users", "/admin/system/config"]

        for endpoint in admin_endpoints:
            response = self.session.get(
                f"{self.base_url}{endpoint}", headers=user_headers
            )
            assert response.status_code in [
                403,
                404,
            ], f"Unauthorized access to {endpoint}"

    def test_tenant_isolation(self):
        """Test multi-tenant data isolation."""
        logger.info("Testing tenant isolation")

        # Create resources for different tenants
        tenant1_headers = {
            "Authorization": f"Bearer {self.admin_token}",
            "X-Tenant-ID": "tenant1",
        }
        tenant2_headers = {
            "Authorization": f"Bearer {self.admin_token}",
            "X-Tenant-ID": "tenant2",
        }

        # Create scan for tenant1
        scan_data = {
            "contract_address": "0x1234567890123456789012345678901234567890",
            "scan_type": "quick",
        }

        response1 = self.session.post(
            f"{self.base_url}/api/scanner/scan", json=scan_data, headers=tenant1_headers
        )

        if response1.status_code in [200, 202]:
            scan_id = response1.json().get("scan_id")

            # Try to access scan from tenant2
            response2 = self.session.get(
                f"{self.base_url}/api/scanner/scan/{scan_id}", headers=tenant2_headers
            )
            assert response2.status_code in [403, 404], "Tenant isolation violated"


class InputValidationTests(SecurityTestSuite):
    """Input validation and sanitization tests."""

    def test_sql_injection(self):
        """Test SQL injection protection."""
        logger.info("Testing SQL injection protection")

        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO users (username) VALUES ('hacker'); --",
            "' UNION SELECT * FROM users WHERE '1'='1",
        ]

        headers = {"Authorization": f"Bearer {self.user_token}"}

        for payload in sql_payloads:
            # Test various endpoints with SQL injection payloads
            endpoints = [
                f"/api/scanner/scans?search={payload}",
                f"/api/bridge/transfers?status={payload}",
                f"/api/mempool/pending?min_gas_price={payload}",
            ]

            for endpoint in endpoints:
                response = self.session.get(
                    f"{self.base_url}{endpoint}", headers=headers
                )
                # Should not return 500 (server error)
                assert (
                    response.status_code != 500
                ), f"SQL injection possible at {endpoint}"

    def test_xss_protection(self):
        """Test XSS protection."""
        logger.info("Testing XSS protection")

        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
        ]

        headers = {"Authorization": f"Bearer {self.user_token}"}

        for payload in xss_payloads:
            # Test POST endpoints that accept user input
            test_data = {"name": payload, "description": payload, "comment": payload}

            endpoints = ["/api/scanner/scan", "/api/bridge/simulate"]

            for endpoint in endpoints:
                response = self.session.post(
                    f"{self.base_url}{endpoint}", json=test_data, headers=headers
                )

                # Check response doesn't contain unescaped script tags
                if response.status_code == 200:
                    response_text = response.text.lower()
                    assert (
                        "<script>" not in response_text
                    ), f"XSS vulnerability at {endpoint}"

    def test_command_injection(self):
        """Test command injection protection."""
        logger.info("Testing command injection protection")

        command_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& whoami",
            "`id`",
            "$(id)",
        ]

        headers = {"Authorization": f"Bearer {self.user_token}"}

        for payload in command_payloads:
            test_data = {
                "contract_address": f"0x1234567890123456789012345678901234567890{payload}",
                "scan_type": "quick",
            }

            response = self.session.post(
                f"{self.base_url}/api/scanner/scan", json=test_data, headers=headers
            )

            # Should return validation error, not server error
            assert response.status_code in [
                400,
                422,
            ], f"Command injection possible: {payload}"

    def test_file_upload_security(self):
        """Test file upload security."""
        logger.info("Testing file upload security")

        # Test malicious file types
        malicious_files = [
            ("test.php", "<?php system($_GET['cmd']); ?>", "application/x-php"),
            (
                "test.jsp",
                '<% Runtime.getRuntime().exec(request.getParameter("cmd")); %>',
                "application/x-jsp",
            ),
            ("test.exe", b"\x4d\x5a\x90\x00", "application/x-executable"),
            ("test.sh", "#!/bin/bash\nrm -rf /", "application/x-sh"),
        ]

        headers = {"Authorization": f"Bearer {self.user_token}"}

        for filename, content, content_type in malicious_files:
            files = {"file": (filename, content, content_type)}

            # Try uploading to various endpoints that might accept files
            endpoints = ["/api/scanner/upload", "/api/admin/import"]

            for endpoint in endpoints:
                response = self.session.post(
                    f"{self.base_url}{endpoint}", files=files, headers=headers
                )

                # Should reject malicious files
                assert response.status_code in [
                    400,
                    415,
                    422,
                ], f"Malicious file accepted: {filename}"


class NetworkSecurityTests(SecurityTestSuite):
    """Network and protocol security tests."""

    def test_rate_limiting(self):
        """Test rate limiting mechanisms."""
        logger.info("Testing rate limiting")

        headers = {"Authorization": f"Bearer {self.user_token}"}

        # Make rapid requests to trigger rate limiting
        responses = []
        for i in range(100):
            response = self.session.get(
                f"{self.base_url}/api/scanner/scans", headers=headers
            )
            responses.append(response.status_code)

            if response.status_code == 429:
                logger.info("Rate limiting triggered", request_number=i + 1)
                break

        # Should hit rate limit before 100 requests
        assert 429 in responses, "Rate limiting not working"

    def test_cors_policy(self):
        """Test CORS policy enforcement."""
        logger.info("Testing CORS policy")

        # Test preflight request with unauthorized origin
        headers = {
            "Origin": "https://evil.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        }

        response = self.session.options(
            f"{self.base_url}/api/scanner/scan", headers=headers
        )

        # Should not include Access-Control-Allow-Origin for unauthorized origin
        cors_header = response.headers.get("Access-Control-Allow-Origin")
        assert cors_header != "https://evil.com", "CORS policy violation"

    def test_security_headers(self):
        """Test security headers presence."""
        logger.info("Testing security headers")

        response = self.session.get(f"{self.base_url}/healthz")

        expected_headers = [
            "X-Frame-Options",
            "X-Content-Type-Options",
            "X-XSS-Protection",
            "Referrer-Policy",
            "Content-Security-Policy",
        ]

        for header in expected_headers:
            assert header in response.headers, f"Missing security header: {header}"

    async def test_tls_configuration(self):
        """Test TLS/SSL configuration."""
        logger.info("Testing TLS configuration")

        # This would require HTTPS endpoint
        if self.base_url.startswith("https://"):
            async with aiohttp.ClientSession() as session:
                try:
                    # Test with weak TLS version (should fail)
                    ssl_context = aiohttp.ClientSSLContext()
                    ssl_context.minimum_version = ssl.TLSVersion.SSLv3

                    async with session.get(self.base_url, ssl=ssl_context) as response:
                        assert False, "Weak TLS version accepted"

                except aiohttp.ClientConnectorError:
                    # Expected - should reject weak TLS
                    pass


class VulnerabilityTests(SecurityTestSuite):
    """Vulnerability assessment tests."""

    def test_information_disclosure(self):
        """Test for information disclosure vulnerabilities."""
        logger.info("Testing information disclosure")

        # Test error messages don't reveal sensitive info
        response = self.session.get(f"{self.base_url}/nonexistent")

        sensitive_keywords = [
            "traceback",
            "stack trace",
            "exception",
            "database",
            "postgresql",
            "redis",
            "secret",
            "password",
            "token",
        ]

        response_text = response.text.lower()
        for keyword in sensitive_keywords:
            assert keyword not in response_text, f"Information disclosure: {keyword}"

    def test_path_traversal(self):
        """Test path traversal vulnerabilities."""
        logger.info("Testing path traversal")

        path_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "....//....//....//etc//passwd",
        ]

        headers = {"Authorization": f"Bearer {self.user_token}"}

        for payload in path_payloads:
            # Test file access endpoints
            response = self.session.get(
                f"{self.base_url}/api/files/{payload}", headers=headers
            )

            # Should not return file contents
            assert response.status_code in [
                400,
                403,
                404,
            ], f"Path traversal possible: {payload}"

    def test_server_side_request_forgery(self):
        """Test SSRF vulnerabilities."""
        logger.info("Testing SSRF")

        ssrf_payloads = [
            "http://localhost:22",
            "http://127.0.0.1:6379",
            "http://169.254.169.254/metadata",
            "file:///etc/passwd",
        ]

        headers = {"Authorization": f"Bearer {self.user_token}"}

        for payload in ssrf_payloads:
            test_data = {"url": payload, "callback_url": payload}

            # Test endpoints that might make external requests
            endpoints = ["/api/scanner/webhook", "/api/bridge/validate"]

            for endpoint in endpoints:
                response = self.session.post(
                    f"{self.base_url}{endpoint}", json=test_data, headers=headers
                )

                # Should reject internal/file URLs
                assert response.status_code in [
                    400,
                    422,
                ], f"SSRF possible at {endpoint}: {payload}"


class CryptographyTests(SecurityTestSuite):
    """Cryptography and key management tests."""

    def test_jwt_algorithm_confusion(self):
        """Test JWT algorithm confusion attacks."""
        logger.info("Testing JWT algorithm confusion")

        # Try to create token with 'none' algorithm
        payload = {
            "sub": "admin",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
        }

        # Token with 'none' algorithm
        none_token = jwt.encode(payload, "", algorithm="none")

        headers = {"Authorization": f"Bearer {none_token}"}
        response = self.session.get(f"{self.base_url}/admin/plugins", headers=headers)

        assert response.status_code == 401, "JWT 'none' algorithm accepted"

    def test_weak_random_generation(self):
        """Test for weak random number generation."""
        logger.info("Testing random generation")

        # Request multiple tokens and check for patterns
        tokens = []
        for _ in range(10):
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"username": "admin", "password": "admin123"},
            )

            if response.status_code == 200:
                tokens.append(response.json()["access_token"])

        # Tokens should be unique
        assert len(set(tokens)) == len(tokens), "Non-unique tokens generated"

        # Basic entropy check (tokens should have good variation)
        if len(tokens) >= 2:
            # Simple check - tokens shouldn't be sequential or have obvious patterns
            for i in range(len(tokens) - 1):
                # Decode tokens and compare
                token1 = jwt.decode(tokens[i], options={"verify_signature": False})
                token2 = jwt.decode(tokens[i + 1], options={"verify_signature": False})

                # IAT (issued at) should be different
                assert token1.get("iat") != token2.get("iat"), "Identical IAT values"


# Test runner
def run_security_tests(base_url: str = "http://localhost:8000"):
    """Run all security tests."""
    logger.info("Starting security test suite", base_url=base_url)

    test_classes = [
        AuthenticationTests,
        AuthorizationTests,
        InputValidationTests,
        NetworkSecurityTests,
        VulnerabilityTests,
        CryptographyTests,
    ]

    results = {}

    for test_class in test_classes:
        logger.info("Running test class", class_name=test_class.__name__)

        try:
            tester = test_class(base_url)
            tester.setup()

            # Get all test methods
            test_methods = [
                method
                for method in dir(tester)
                if method.startswith("test_") and callable(getattr(tester, method))
            ]

            class_results = {}

            for method_name in test_methods:
                try:
                    logger.info("Running test", method=method_name)
                    method = getattr(tester, method_name)

                    if asyncio.iscoroutinefunction(method):
                        asyncio.run(method())
                    else:
                        method()

                    class_results[method_name] = "PASS"
                    logger.info("Test passed", method=method_name)

                except Exception as e:
                    class_results[method_name] = f"FAIL: {str(e)}"
                    logger.error("Test failed", method=method_name, error=str(e))

            results[test_class.__name__] = class_results

        except Exception as e:
            results[test_class.__name__] = {"setup_error": str(e)}
            logger.error(
                "Test class setup failed", class_name=test_class.__name__, error=str(e)
            )

    # Generate report
    logger.info("Security test suite completed")

    total_tests = sum(
        len(class_results)
        for class_results in results.values()
        if isinstance(class_results, dict)
    )
    passed_tests = sum(
        1
        for class_results in results.values()
        if isinstance(class_results, dict)
        for result in class_results.values()
        if result == "PASS"
    )

    logger.info(
        "Test results summary",
        total_tests=total_tests,
        passed_tests=passed_tests,
        failed_tests=total_tests - passed_tests,
    )

    return results


if __name__ == "__main__":
    import sys

    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    results = run_security_tests(base_url)

    # Print results in JSON format
    print(json.dumps(results, indent=2))
