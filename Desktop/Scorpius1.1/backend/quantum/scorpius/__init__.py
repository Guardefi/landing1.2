"""
SCORPIUS ENTERPRISE QUANTUM SECURITY PLATFORM
============================================

Enterprise-grade quantum-resistant cryptography and blockchain security platform.
"""

__version__ = "2.0.0"
__enterprise_edition__ = True

import asyncio
import logging
import os
from typing import Any, Dict, Optional

from .core.config import ScorpiusConfig
from .core.engine import ScorpiusEngine
from .core.licensing import LicenseManager
from .core.monitoring import EnterpriseMonitoring
from .exceptions import LicenseError, ScorpiusError

# Global instances
_scorpius_engine: Optional[ScorpiusEngine] = None
_monitoring: Optional[EnterpriseMonitoring] = None
_license_manager: Optional[LicenseManager] = None


async def initialize_scorpius(
    config_path: Optional[str] = None,
    license_key: Optional[str] = None,
    **config_overrides,
) -> bool:
    """
    Initialize Scorpius Enterprise Platform.

    Args:
        config_path: Path to configuration file
        license_key: Enterprise license key
        **config_overrides: Configuration overrides

    Returns:
        True if initialization successful
    """
    global _scorpius_engine, _monitoring, _license_manager

    try:
        # Initialize license manager first
        _license_manager = LicenseManager()
        if not await _license_manager.validate_license(license_key):
            raise LicenseError("Invalid or expired enterprise license")

        # Load configuration
        config = ScorpiusConfig.load(config_path, **config_overrides)

        # Initialize monitoring
        _monitoring = EnterpriseMonitoring(config.monitoring_config)
        await _monitoring.start()

        # Initialize main engine
        _scorpius_engine = ScorpiusEngine(config)
        await _scorpius_engine.initialize()

        # Register shutdown handlers
        import atexit

        atexit.register(lambda: asyncio.create_task(shutdown_scorpius()))

        logging.info(f"Scorpius Enterprise v{__version__} initialized successfully")
        return True

    except Exception as e:
        logging.error(f"Failed to initialize Scorpius: {e}")
        return False


async def shutdown_scorpius():
    """Gracefully shutdown Scorpius platform."""
    global _scorpius_engine, _monitoring

    if _scorpius_engine:
        await _scorpius_engine.shutdown()

    if _monitoring:
        await _monitoring.stop()

    logging.info("Scorpius platform shutdown complete")


def get_engine() -> ScorpiusEngine:
    """Get the global Scorpius engine instance."""
    if _scorpius_engine is None:
        raise ScorpiusError(
            "Scorpius not initialized. Call initialize_scorpius() first."
        )
    return _scorpius_engine


from .analytics import AnalyticsType, TimeFrame
from .integration import IntegrationHub

# Convenience exports
from .quantum import QuantumAlgorithm, QuantumKey, SecurityLevel
from .security import SecurityAlert, ThreatLevel

__all__ = [
    "initialize_scorpius",
    "shutdown_scorpius",
    "get_engine",
    "ScorpiusEngine",
    "QuantumAlgorithm",
    "SecurityLevel",
    "ThreatLevel",
    "AnalyticsType",
    "IntegrationHub",
]
