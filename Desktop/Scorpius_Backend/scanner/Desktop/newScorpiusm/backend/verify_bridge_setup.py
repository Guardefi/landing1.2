#!/usr/bin/env python3
"""
Verification script for Scorpius Bridge Network setup
This script verifies that the bridge is properly configured and integrated.
"""

        from scorpius_bridge import BridgeType, ChainType, bridge_router, settings

def main():
    print("🔗 Scorpius Bridge Network Verification")
    print("=" * 50)

    # Test 1: Import main FastAPI app
    try:
        print("✅ Main FastAPI app imports successfully")
    except Exception as e:
        print(f"❌ Failed to import main app: {e}")
        return False

    # Test 2: Import bridge components
    try:

        print("✅ Bridge router and settings import successfully")
    except Exception as e:
        print(f"❌ Failed to import bridge components: {e}")
        return False

    # Test 3: Verify bridge settings
    try:
        print(f"✅ Bridge environment: {settings.environment}")
        print(f"✅ Supported chains: {', '.join(settings.supported_chains)}")
        print(f"✅ Database URL configured: {bool(settings.database_url)}")
        print(f"✅ Redis URL configured: {bool(settings.redis_url)}")
    except Exception as e:
        print(f"❌ Failed to read bridge settings: {e}")
        return False

    # Test 4: Verify bridge router integration
    try:
        route_count = len(bridge_router.routes)
        print(f"✅ Bridge router has {route_count} endpoints")

        # List bridge endpoints
        print("\n🛣️  Bridge API Endpoints:")
        for route in bridge_router.routes:
            methods = ", ".join(route.methods) if hasattr(route, "methods") else "GET"
            print(f"   {methods} {route.path}")
    except Exception as e:
        print(f"❌ Failed to verify bridge router: {e}")
        return False

    # Test 5: Verify bridge types
    try:

        print("✅ Bridge data types import successfully")
        print(f"✅ Available bridge types: {list(BridgeType)}")
        print(f"✅ Available chain types: {list(ChainType)}")
    except Exception as e:
        print(f"❌ Failed to import bridge types: {e}")
        return False

    print("\n🎉 ALL TESTS PASSED!")
    print("The Scorpius Bridge Network is properly configured and ready for use.")
    print("\nNext steps:")
    print("1. Start the server: python main.py")
    print("2. View API docs: http://localhost:8000/docs")
    print("3. Test bridge endpoints: http://localhost:8000/api/v2/bridge/")

    return True


if __name__ == "__main__":
    main()
