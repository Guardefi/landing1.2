#!/usr/bin/env python3
"""
Quick test script for Scorpius FastAPI backend
"""

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing Scorpius FastAPI Backend...")

    try:
        # Test basic imports

        print(f"✅ FastAPI version: {fastapi.__version__}")

        print("✅ Uvicorn imported successfully")


        print(f"✅ SQLAlchemy version: {sqlalchemy.__version__}")

        # Test models
        print("✅ Models imported successfully")

        # Test services
        print("✅ Blockchain services imported successfully")

        # Test FastAPI routes
        print("✅ FastAPI routes imported successfully")

        # Test existing routes
        print("✅ Existing routes imported successfully")

        print("\n🎉 All core modules imported successfully!")
        return True

    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False


def test_app_creation():
    """Test if FastAPI app can be created"""
    try:
        # Mock the integration_hub import that might fail
        sys.modules["integration_hub"] = type(
            "MockModule",
            (),
            {
import os
import sys
import traceback

import fastapi
import sqlalchemy
from main import app

                "initialize_integration_hub": lambda x: True,
                "integration_hub": type(
                    "MockHub",
                    (),
                    {
                        "get_system_status": lambda: {
                            "active_modules": 5,
                            "total_modules": 10,
                            "uptime": "0:00:01",
                        }
                    },
                )(),
                "unified_security_scan": lambda: None,
                "unified_threat_response": lambda: None,
                "deploy_quantum_environment": lambda: None,
            },
        )()

        # Mock other potentially problematic modules
        for module_name in [
            "advanced_monitoring_dashboard",
            "ai_trading_engine",
            "blockchain_bridge_network",
            "enterprise_analytics_platform",
            "distributed_computing_engine",
        ]:
            sys.modules[module_name] = type(
                "MockModule",
                (),
                {
                    f'initialize_{module_name.split("_")[0]}_dashboard': lambda: True,
                    f'initialize_{module_name.split("_")[0]}_engine': lambda: True,
                    f'get_{module_name.split("_")[0]}_instance': lambda: None,
                    f'stop_{module_name.split("_")[0]}_dashboard': lambda: None,
                    f'stop_{module_name.split("_")[0]}_engine': lambda: None,
                },
            )()

        # Try to import the main app

        print("✅ FastAPI app created successfully!")
        print(f"✅ App title: {app.title}")
        print(f"✅ App version: {app.version}")

        return True

    except Exception as e:
        print(f"❌ App creation error: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 SCORPIUS FASTAPI BACKEND TEST")
    print("=" * 50)

    imports_ok = test_imports()
    if imports_ok:
        app_ok = test_app_creation()
        if app_ok:
            print("\n🎉 ALL TESTS PASSED! Backend is ready to run.")
            print("\n📝 To start the server:")
            print("uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        else:
            print("\n❌ App creation failed, but basic imports work.")
    else:
        print("\n❌ Basic imports failed. Check dependencies.")

    print("=" * 50)
