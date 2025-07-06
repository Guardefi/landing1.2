"""
Service registration script for Wallet Guard
"""

import asyncio
import logging
import os
import sys

# Add the packages/core directory to the Python path
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "packages", "core")
)

from sdk.service_registration import (
    ServiceRegistrationConfig,
    ServiceRoute,
    register_service,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def register_wallet_guard():
    """Register the wallet guard service with the orchestrator"""

    # Define service configuration
    config = ServiceRegistrationConfig(
        name="wallet_guard",
        version="1.0.0",
        url="http://wallet_guard:8085",
        health_path="/health",
        routes=[
            ServiceRoute(
                path="/wallet/check",
                method="POST",
                description="Check wallet for security risks and dangerous approvals",
            ),
            ServiceRoute(
                path="/wallet/revoke",
                method="POST",
                description="Generate revoke transactions for dangerous approvals",
            ),
            ServiceRoute(
                path="/health", method="GET", description="Health check endpoint"
            ),
            ServiceRoute(
                path="/metrics", method="GET", description="Prometheus metrics endpoint"
            ),
        ],
        capabilities=[
            "wallet_security_analysis",
            "approval_risk_detection",
            "transaction_generation",
            "multi_chain_support",
            "batch_processing",
        ],
        dependencies=["postgres", "redis"],
        metadata={
            "supported_chains": ["ethereum", "bsc", "arbitrum", "base"],
            "max_addresses_per_request": 25,
            "rate_limit": "60/minute",
            "timeout": 30,
        },
    )

    # Register with the gateway
    gateway_url = os.getenv("GATEWAY_URL", "http://api-gateway:8000")
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379")

    logger.info(f"Registering wallet_guard service with gateway at {gateway_url}")

    try:
        success = await register_service(
            config=config, gateway_url=gateway_url, redis_url=redis_url
        )

        if success:
            logger.info("Wallet Guard service registered successfully!")
            return True
        else:
            logger.error("Failed to register Wallet Guard service")
            return False

    except Exception as e:
        logger.error(f"Error registering service: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(register_wallet_guard())
