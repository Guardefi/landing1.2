"""
Simple test script for Scorpius Bridge Network
"""



# Add backend path to sys.path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)


async def test_bridge_types():
    """Test basic bridge types and enums."""
    print("🔧 Testing Scorpius Bridge Network Types...")

    # Test chain types
    print(f"Supported chains: {[chain.value for chain in ChainType]}")

    # Test bridge types
    print(f"Bridge types: {[bridge.value for bridge in BridgeType]}")

    # Test creating a bridge transfer
    transfer = BridgeTransfer.create_new(
        from_chain=ChainType.ETHEREUM,
        to_chain=ChainType.POLYGON,
        asset="USDC",
        amount=Decimal("100.0"),
        sender_address="0x1234567890123456789012345678901234567890",
        receiver_address="0x0987654321098765432109876543210987654321",
        user_id="test_user_123",
    )

    print(f"Created transfer: {transfer.id}")
    print(f"Progress: {transfer.get_progress_percentage()}%")
    print(f"Expired: {transfer.is_expired()}")
    print(f"Can retry: {transfer.can_retry()}")

    print("✅ Bridge types test completed successfully!")


async def test_settings():
    """Test configuration settings."""
    print("🔧 Testing Bridge Settings...")

    print(f"Environment: {settings.environment}")
    print(f"Database URL: {settings.database_url}")
    print(f"Supported chains: {settings.supported_chains}")
    print(f"Min transfer amount: {settings.min_transfer_amount}")
    print(f"Max transfer amount: {settings.max_transfer_amount}")
    print(f"Bridge fee percentage: {settings.base_bridge_fee_percentage}")

    print("✅ Settings test completed successfully!")


async def test_api_router():
    """Test that the API router is properly configured."""
    print("🔧 Testing API Router...")

    print(f"Router prefix: {bridge_router.prefix}")
    print(f"Router tags: {bridge_router.tags}")
    print(f"Number of routes: {len(bridge_router.routes)}")

    # List all routes
    for route in bridge_router.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            print(f"  - {route.methods} {route.path}")

    print("✅ API router test completed successfully!")


async def main():
    """Run all tests."""
    print("🚀 Starting Scorpius Bridge Network Tests...")
    print("=" * 50)

    try:
        await test_bridge_types()
        print()
import asyncio
import os
import sys
import traceback
from decimal import Decimal

from scorpius_bridge import bridge_router, settings
from scorpius_bridge.core.types import BridgeTransfer, BridgeType, ChainType

        await test_settings()
        print()

        await test_api_router()
        print()

        print("=" * 50)
        print("🎉 All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
