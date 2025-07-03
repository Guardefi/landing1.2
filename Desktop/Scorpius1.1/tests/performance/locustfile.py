#!/usr/bin/env python3
"""
Locust Performance Testing for Scorpius Enterprise Platform
Comprehensive load testing scenarios for all microservices.
"""

import json
import random
import time
from datetime import datetime
from typing import Any, Dict

import structlog
from locust import HttpUser, between, events, task
from locust.runners import MasterRunner

# Configure logging
logger = structlog.get_logger("performance_tests")


class ScorpiusUser(HttpUser):
    """Base user class with authentication and common utilities."""

    wait_time = between(1, 3)

    def on_start(self):
        """Setup method called when user starts."""
        self.auth_token = None
        self.user_id = f"test_user_{random.randint(1000, 9999)}"
        self.tenant_id = f"tenant_{random.randint(1, 10)}"

        # Authenticate
        self.authenticate()

        # Set headers
        self.client.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": "Locust Performance Test",
                "X-Tenant-ID": self.tenant_id,
            }
        )

        if self.auth_token:
            self.client.headers.update({"Authorization": f"Bearer {self.auth_token}"})

    def authenticate(self):
        """Authenticate user and get JWT token."""
        try:
            response = self.client.post(
                "/auth/login",
                json={
                    "username": "admin",
                    "password": "admin123",
                    "tenant_id": self.tenant_id,
                },
            )

            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                logger.info("Authentication successful", user_id=self.user_id)
            else:
                logger.error(
                    "Authentication failed",
                    status_code=response.status_code,
                    response=response.text,
                )

        except Exception as e:
            logger.error("Authentication error", error=str(e))

    def make_authenticated_request(
        self, method: str, url: str, **kwargs
    ) -> Dict[str, Any]:
        """Make an authenticated API request."""
        if not self.auth_token:
            self.authenticate()

        response = getattr(self.client, method.lower())(url, **kwargs)

        # Handle token expiration
        if response.status_code == 401:
            self.authenticate()
            if self.auth_token:
                response = getattr(self.client, method.lower())(url, **kwargs)

        return response


class APIGatewayUser(ScorpiusUser):
    """Test API Gateway and orchestrator functionality."""

    weight = 3

    @task(10)
    def health_check(self):
        """Test health endpoints."""
        endpoints = ["/healthz", "/readyz", "/health"]
        endpoint = random.choice(endpoints)

        with self.client.get(endpoint, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(5)
    def metrics_endpoint(self):
        """Test metrics endpoint."""
        with self.client.get("/metrics", catch_response=True) as response:
            if response.status_code == 200 and "prometheus" in response.headers.get(
                "content-type", ""
            ):
                response.success()
            else:
                response.failure("Metrics endpoint failed")

    @task(3)
    def plugin_management(self):
        """Test plugin management endpoints."""
        # List plugins
        response = self.make_authenticated_request("GET", "/admin/plugins")

        if response.status_code == 200:
            plugins = response.json().get("plugins", {})

            # Randomly activate/deactivate a plugin
            if plugins:
                plugin_name = random.choice(list(plugins.keys()))
                action = random.choice(["activate", "deactivate"])

                self.make_authenticated_request(
                    "POST", f"/admin/plugins/{plugin_name}/{action}"
                )

    @task(2)
    def websocket_connection(self):
        """Test WebSocket connections."""
        try:
            # This would need websocket support in locust
            # For now, we'll simulate the connection attempt
            pass
        except Exception as e:
            logger.warning("WebSocket test skipped", error=str(e))


class ScannerServiceUser(ScorpiusUser):
    """Test Scanner microservice functionality."""

    weight = 2

    @task(8)
    def scan_contract(self):
        """Test contract scanning."""
        contract_addresses = [
            "0x1234567890123456789012345678901234567890",
            "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
            "0x9876543210987654321098765432109876543210",
        ]

        scan_request = {
            "contract_address": random.choice(contract_addresses),
            "scan_type": random.choice(["quick", "deep", "comprehensive"]),
            "include_bytecode": random.choice([True, False]),
        }

        response = self.make_authenticated_request(
            "POST", "/api/scanner/scan", json=scan_request
        )

        if response.status_code in [200, 202]:
            scan_id = response.json().get("scan_id")
            if scan_id:
                # Check scan status
                time.sleep(random.uniform(0.5, 2.0))
                self.make_authenticated_request(
                    "GET", f"/api/scanner/scan/{scan_id}/status"
                )

    @task(3)
    def get_scan_history(self):
        """Test scan history retrieval."""
        params = {"limit": random.randint(10, 50), "offset": random.randint(0, 100)}

        self.make_authenticated_request("GET", "/api/scanner/scans", params=params)

    @task(2)
    def vulnerability_report(self):
        """Test vulnerability reporting."""
        self.make_authenticated_request("GET", "/api/scanner/vulnerabilities")


class BridgeServiceUser(ScorpiusUser):
    """Test Bridge microservice functionality."""

    weight = 2

    @task(5)
    def get_supported_chains(self):
        """Test supported chains endpoint."""
        self.make_authenticated_request("GET", "/api/bridge/chains")

    @task(3)
    def simulate_transfer(self):
        """Test bridge transfer simulation."""
        transfer_request = {
            "from_chain": "ethereum",
            "to_chain": "polygon",
            "token_address": "0x1234567890123456789012345678901234567890",
            "amount": str(random.uniform(0.1, 10.0)),
            "recipient": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
        }

        response = self.make_authenticated_request(
            "POST", "/api/bridge/simulate", json=transfer_request
        )

        if response.status_code == 200:
            simulation = response.json()
            logger.info(
                "Bridge simulation completed",
                gas_cost=simulation.get("gas_cost"),
                duration=simulation.get("estimated_duration"),
            )

    @task(2)
    def get_transfer_history(self):
        """Test transfer history."""
        params = {
            "limit": random.randint(10, 50),
            "status": random.choice(["pending", "completed", "failed", "all"]),
        }

        self.make_authenticated_request("GET", "/api/bridge/transfers", params=params)


class MempoolServiceUser(ScorpiusUser):
    """Test Mempool microservice functionality."""

    weight = 1

    @task(8)
    def get_pending_transactions(self):
        """Test pending transactions retrieval."""
        params = {
            "limit": random.randint(50, 200),
            "min_gas_price": random.randint(20, 100),
        }

        self.make_authenticated_request("GET", "/api/mempool/pending", params=params)

    @task(3)
    def analyze_transaction(self):
        """Test transaction analysis."""
        tx_hash = f"0x{''.join(random.choices('0123456789abcdef', k=64))}"

        self.make_authenticated_request("GET", f"/api/mempool/analyze/{tx_hash}")

    @task(2)
    def get_gas_predictions(self):
        """Test gas price predictions."""
        self.make_authenticated_request("GET", "/api/mempool/gas-predictions")


class MEVServiceUser(ScorpiusUser):
    """Test MEV microservice functionality."""

    weight = 1

    @task(5)
    def get_opportunities(self):
        """Test MEV opportunities."""
        params = {
            "strategy": random.choice(["arbitrage", "sandwich", "liquidation"]),
            "min_profit": random.randint(100, 1000),
        }

        self.make_authenticated_request("GET", "/api/mev/opportunities", params=params)

    @task(3)
    def simulate_strategy(self):
        """Test strategy simulation."""
        strategy_request = {
            "type": "arbitrage",
            "tokens": ["ETH", "USDC"],
            "amount": str(random.uniform(1.0, 100.0)),
        }

        self.make_authenticated_request(
            "POST", "/api/mev/simulate", json=strategy_request
        )


class HoneypotServiceUser(ScorpiusUser):
    """Test Honeypot microservice functionality."""

    weight = 1

    @task(6)
    def check_contract(self):
        """Test honeypot detection."""
        contract_address = f"0x{''.join(random.choices('0123456789abcdef', k=40))}"

        self.make_authenticated_request(
            "GET", f"/api/honeypot/check/{contract_address}"
        )

    @task(3)
    def get_detected_honeypots(self):
        """Test detected honeypots list."""
        params = {
            "limit": random.randint(20, 100),
            "severity": random.choice(["high", "medium", "low", "all"]),
        }

        self.make_authenticated_request("GET", "/api/honeypot/detected", params=params)


# Test scenarios for different load patterns
class NormalLoadUser(ScorpiusUser):
    """Simulate normal user load patterns."""

    weight = 5
    wait_time = between(2, 8)

    tasks = {
        APIGatewayUser.health_check: 3,
        ScannerServiceUser.scan_contract: 2,
        BridgeServiceUser.get_supported_chains: 2,
        MempoolServiceUser.get_pending_transactions: 2,
        HoneypotServiceUser.check_contract: 1,
    }


class HighLoadUser(ScorpiusUser):
    """Simulate high load stress testing."""

    weight = 2
    wait_time = between(0.5, 2)

    tasks = {
        APIGatewayUser.health_check: 10,
        ScannerServiceUser.scan_contract: 5,
        BridgeServiceUser.simulate_transfer: 3,
        MempoolServiceUser.analyze_transaction: 3,
        MEVServiceUser.get_opportunities: 2,
    }


class BurstLoadUser(ScorpiusUser):
    """Simulate burst load patterns."""

    weight = 1
    wait_time = between(0, 1)

    @task
    def burst_requests(self):
        """Make multiple rapid requests."""
        for _ in range(random.randint(3, 8)):
            self.client.get("/healthz")
            time.sleep(random.uniform(0.1, 0.3))


# Event handlers for monitoring and reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts."""
    logger.info(
        "Performance test started",
        target_host=environment.host,
        test_time=datetime.utcnow().isoformat(),
    )


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops."""
    logger.info("Performance test completed", test_time=datetime.utcnow().isoformat())


@events.request_failure.add_listener
def on_request_failure(
    request_type, name, response_time, response_length, exception, **kwargs
):
    """Log request failures."""
    logger.error(
        "Request failed",
        request_type=request_type,
        name=name,
        response_time=response_time,
        exception=str(exception),
    )


@events.request_success.add_listener
def on_request_success(request_type, name, response_time, response_length, **kwargs):
    """Log successful requests (sample only)."""
    if random.random() < 0.01:  # Log 1% of successful requests
        logger.info(
            "Request succeeded",
            request_type=request_type,
            name=name,
            response_time=response_time,
        )


# Custom WebUI for real-time monitoring during tests
from locust.web import WebUI


def custom_stats_handler(environment, request, **kwargs):
    """Custom stats endpoint for external monitoring."""
    stats = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_count": environment.runner.user_count,
        "total_requests": sum(
            environment.stats.entries.values(), key=lambda x: x.num_requests
        ),
        "failure_ratio": environment.stats.total.fail_ratio,
        "avg_response_time": environment.stats.total.avg_response_time,
        "rps": environment.stats.total.total_rps,
    }

    return json.dumps(stats, indent=2)


# Register custom endpoint
if hasattr(WebUI, "app"):

    @WebUI.app.route("/custom-stats")
    def custom_stats():
        return custom_stats_handler(WebUI.environment, None)
