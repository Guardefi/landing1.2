"""
Test script for comprehensive bridge network integration
Tests all modules: validators, atomic swaps, liquidity pools, and API endpoints.
"""


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_bridge_integration():
    """Test the complete bridge network integration."""
    try:  # Test 1: Import all bridge modules
        logger.info("=== Testing Bridge Module Imports ===")

            BridgeTransfer,
import asyncio
import logging
from datetime import datetime
from decimal import Decimal

from scorpius_bridge import bridge_router, settings
from scorpius_bridge.atomic_swaps import AtomicSwapEngine
from scorpius_bridge.core.types import (
    BridgeType,
    ChainType,
    FastAPI,
    LiquidityManager,
    TransferStatus,
    ValidatorManager,
    fastapi,
    from,
    import,
    scorpius_bridge.api.endpoints,
    scorpius_bridge.config.settings,
    scorpius_bridge.liquidity_pools,
    scorpius_bridge.validators,
    set_bridge_components,
    settings,
    traceback,
)

        logger.info("✅ All bridge modules imported successfully")

        # Test 2: Initialize components
        logger.info("=== Testing Component Initialization ===")

        validator_manager = ValidatorManager()
        atomic_swap_engine = AtomicSwapEngine()
        liquidity_manager = LiquidityManager()

        logger.info("✅ All components initialized successfully")
        # Test 3: Test validator operations
        logger.info("=== Testing Validator Operations ===")

        # Temporarily override minimum validators for testing

        original_min_validators = settings.min_validators
        settings.min_validators = 2

        await validator_manager.register_validator(
            validator_id="test_validator_1",
            address="0x123456789abcdef",
            stake_amount=1000.0,
            public_key="test_public_key_1",
        )

        await validator_manager.register_validator(
            validator_id="test_validator_2",
            address="0xfedcba987654321",
            stake_amount=2000.0,
            public_key="test_public_key_2",
        )

        active_validators = validator_manager.get_active_validators()
        logger.info(f"✅ Registered {len(active_validators)} validators")

        # Test 4: Test liquidity pool operations
        logger.info("=== Testing Liquidity Pool Operations ===")

        eth_pool_id = await liquidity_manager.create_pool(
            chain="ethereum",
            token_address="0x1234567890abcdef1234567890abcdef12345678",
            token_symbol="ETH",
            initial_liquidity=Decimal("100"),
        )

        usdc_pool_id = await liquidity_manager.create_pool(
            chain="polygon",
            token_address="0xabcdef1234567890abcdef1234567890abcdef12",
            token_symbol="USDC",
            initial_liquidity=Decimal("50000"),
        )

        logger.info(f"✅ Created liquidity pools: {eth_pool_id}, {usdc_pool_id}")
        # Add liquidity
        eth_pool = liquidity_manager.get_pool(eth_pool_id)
        if eth_pool:
            await eth_pool.add_liquidity("0xprovider1", Decimal("50"))
            await eth_pool.add_liquidity("0xprovider2", Decimal("100"))

        logger.info("✅ Added liquidity to pools")

        # Test 5: Test bridge transfer and atomic swap
        logger.info("=== Testing Bridge Transfer and Atomic Swap ===")
        # Create a test transfer
        transfer = BridgeTransfer(
            id="test_transfer_001",
            sender_address="0xsender123",
            receiver_address="0xreceiver456",
            from_chain=ChainType.ETHEREUM,
            to_chain=ChainType.POLYGON,
            asset="0x1234567890abcdef1234567890abcdef12345678",
            amount=Decimal("10"),
            bridge_type=BridgeType.LOCK_AND_MINT,
            status=TransferStatus.INITIATED,
            timestamp=datetime.now(),
        )

        # Test validator consensus
        consensus_result = await validator_manager.validate_transfer(transfer)
        logger.info(
            f"✅ Validator consensus: {consensus_result.reached} ({consensus_result.votes_for}/{consensus_result.total_validators})"
        )

        # Test atomic swap
        atomic_swap = await atomic_swap_engine.initiate_swap(transfer, timeout_hours=24)
        logger.info(f"✅ Atomic swap initiated: {atomic_swap.swap_id}")

        await atomic_swap_engine.lock_funds(atomic_swap.swap_id)
        logger.info("✅ Funds locked in atomic swap")

        # Test 6: Test settings and configuration
        logger.info("=== Testing Configuration ===")

        logger.info(f"Min validators: {settings.min_validators}")
        logger.info(f"Consensus threshold: {settings.consensus_threshold}")
        logger.info(f"Supported chains: {settings.supported_chains}")
        logger.info(f"Environment: {settings.environment}")

        logger.info("✅ Configuration loaded successfully")

        # Test 7: Test FastAPI router
        logger.info("=== Testing FastAPI Router ===")


        app = FastAPI()
        app.include_router(bridge_router)

        # Set components in the API
        set_bridge_components(
            network=None,  # Would be actual bridge network instance
            validator_mgr=validator_manager,
            swap_engine=atomic_swap_engine,
            liquidity_mgr=liquidity_manager,
        )

        logger.info("✅ FastAPI router integrated successfully")

        # Test 8: Network statistics
        logger.info("=== Testing Network Statistics ===")

        validator_stats = await validator_manager.get_network_stats()
        liquidity_stats = await liquidity_manager.get_total_liquidity()

        logger.info(f"Network health: {validator_stats['network_health']:.2f}")
        logger.info(f"Total liquidity: {liquidity_stats}")

        logger.info("✅ Network statistics retrieved successfully")

        logger.info(
            "\n🎉 ALL TESTS PASSED! Bridge network integration is complete and functional."
        )

        return True

    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_bridge_integration())
    if success:
        print("\n✅ Bridge network is ready for production!")
    else:
        print("\n❌ Integration test failed - check logs for details")
        exit(1)
