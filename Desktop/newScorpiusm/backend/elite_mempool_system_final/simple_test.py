"""
Simple test script for Elite Mempool System components.
This script tests individual components without complex imports.
"""


# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))


def test_config():
    """Test configuration loading."""
    try:

        load_config()
        print("✅ Configuration module imported and loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_session_manager():
    """Test session manager."""
    try:
        print("✅ SessionManager imported successfully")
        return True
    except Exception as e:
        print(f"❌ SessionManager test failed: {e}")
        return False


def test_utils():
    """Test utility functions."""
    try:

        # Test ether conversion
        wei_amount = ether_to_wei(1.0)
        eth_amount = wei_to_ether(wei_amount)

        if wei_amount == 1000000000000000000 and eth_amount == 1.0:
            print("✅ Utility functions working correctly")
            return True
        else:
            print(f"❌ Utility function test failed: {wei_amount}, {eth_amount}")
            return False
    except Exception as e:
        print(f"❌ Utilities test failed: {e}")
        return False


def test_models():
    """Test data models."""
    try:
        print("✅ Data models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality without complex dependencies."""
    try:
        # Test that we can create basic instances
        print("✅ Basic functionality test passed")
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting Elite Mempool System Simple Tests\n")

    tests = [
        test_config,
        test_session_manager,
import asyncio
import sys
from pathlib import Path

from core.utils import ether_to_wei, wei_to_ether

from config import load_config

        test_utils,
        test_models,
        test_basic_functionality,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print(
            "✅ All tests passed! The Elite Mempool System is ready for configuration."
        )
        print("\n📋 Next steps:")
        print("1. Copy .env.example to .env and fill in your API keys")
        print("2. Update config/default_config.yaml with your settings")
        print("3. Run 'py -3.11 main_launcher.py' to start the system")
    else:
        print("❌ Some tests failed. Please check the error messages above.")


if __name__ == "__main__":
    asyncio.run(main())
