#!/usr/bin/env python3
"""
Scorpius Enterprise Platform Demo
Demonstrates the enterprise-grade quantum security platform.
"""

import asyncio
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def main():
    """Main demo function."""
    print("🦂 SCORPIUS ENTERPRISE QUANTUM SECURITY PLATFORM")
    print("=" * 60)
    print()

    try:
        # Import the enterprise module
        from scorpius import get_engine, initialize_scorpius

        print("📋 Initializing Scorpius Enterprise Platform...")

        # Initialize with enterprise configuration
        success = await initialize_scorpius(
            config_path="config/enterprise.yml",
            license_key="ENTERPRISE-DEMO-LICENSE-KEY-12345678",
        )

        if not success:
            print("❌ Failed to initialize Scorpius platform")
            return

        print("✅ Scorpius Enterprise Platform initialized successfully!")
        print()

        # Get the main engine
        engine = get_engine()

        # Demonstrate platform status
        print("🔍 Platform Status:")
        print("-" * 20)
        status = await engine.get_platform_status()
        print(f"Platform Version: {status['platform_version']}")
        print(f"Uptime: {status['uptime_seconds']:.2f} seconds")
        print(f"Total Modules: {status['total_modules']}")
        print(f"Active Modules: {status['active_modules']}")
        print(f"Overall Health: {status['overall_health']:.2f}")
        print(f"Enterprise Edition: {status['is_enterprise']}")
        print(f"License Valid: {status['license_valid']}")
        print()

        # Display module details
        print("📊 Module Details:")
        print("-" * 20)
        for module in status["modules"]:
            print(f"  {module['name'].upper()}:")
            print(f"    Version: {module['version']}")
            print(f"    Status: {module['status']}")
            print(f"    Health: {module['health_score']:.2f}")
            print(f"    Uptime: {module['uptime']:.2f}s")
            print()

        # Demonstrate quantum encryption
        print("🔐 Quantum Encryption Demo:")
        print("-" * 30)

        test_message = (
            b"This is a secret message that needs quantum-resistant protection!"
        )
        print(f"Original Message: {test_message.decode()}")

        encryption_result = await engine.quantum_encrypt(
            message=test_message, algorithm="lattice_based", security_level=3
        )

        print("Encryption Result:")
        print(json.dumps(encryption_result, indent=2, default=str))
        print()

        # Demonstrate security scanning
        print("🛡️ Security Scan Demo:")
        print("-" * 25)

        scan_result = await engine.security_scan(
            target="0x1234567890abcdef1234567890abcdef12345678",
            scan_type="comprehensive",
        )

        print("Security Scan Result:")
        print(json.dumps(scan_result, indent=2, default=str))
        print()

        # Demonstrate analytics reporting
        print("📈 Analytics Report Demo:")
        print("-" * 27)

        analytics_result = await engine.generate_analytics_report(
            report_type="security", timeframe="24h"
        )

        print("Analytics Report:")
        print(json.dumps(analytics_result, indent=2, default=str))
        print()

        print("🎉 Demo completed successfully!")
        print()
        print("Enterprise Features Available:")
        print("✅ Quantum-resistant cryptography")
        print("✅ AI-powered security scanning")
        print("✅ Real-time analytics")
        print("✅ Enterprise monitoring")
        print("✅ High availability support")
        print("✅ Clustering capabilities")
        print("✅ Comprehensive logging")
        print("✅ License management")
        print()

    except ImportError as e:
        print(f"❌ Failed to import Scorpius module: {e}")
        print("Please ensure the enterprise module is properly installed:")
        print("  pip install -e .[enterprise,quantum]")

    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        logging.exception("Demo error details:")


if __name__ == "__main__":
    asyncio.run(main())
