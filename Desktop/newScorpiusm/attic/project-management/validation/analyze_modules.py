#!/usr/bin/env python3
"""Simple test for backend class structure."""

import os
import sys

# Add the parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def check_module_classes(module_name, file_path):
    """Check what classes are available in a module."""
    try:
        print(f"  📦 Checking {module_name}...")
        import importlib.util

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        classes = [
            name
            for name in dir(module)
            if not name.startswith("_")
            and hasattr(getattr(module, name), "__class__")
            and type(getattr(module, name)).__name__ == "type"
        ]

        print(
            f"    Classes: {', '.join(classes[:5])}{'...' if len(classes) > 5 else ''}"
        )
        return classes
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return []


try:
    print("🔍 Analyzing backend module structure...")

    modules = [
        ("advanced_monitoring_dashboard", "backend/advanced_monitoring_dashboard.py"),
        ("ai_trading_engine", "backend/ai_trading_engine.py"),
        ("blockchain_bridge_network", "backend/blockchain_bridge_network.py"),
        ("enterprise_analytics_platform", "backend/enterprise_analytics_platform.py"),
        ("distributed_computing_engine", "backend/distributed_computing_engine.py"),
        ("elite_security_engine", "backend/elite_security_engine.py"),
        ("realtime_threat_system", "backend/realtime_threat_system.py"),
        ("integration_hub", "backend/integration_hub.py"),
    ]

    for module_name, file_path in modules:
        check_module_classes(module_name, file_path)

    print("\n✅ Module structure analysis complete!")

except Exception as e:
    print(f"\n❌ Analysis failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
