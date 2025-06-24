"""
Scorpius Quantum Cryptography Platform
Advanced quantum-resistant cryptographic implementations.
"""

import logging
from typing import Optional

from .config import QuantumConfig
from .core.engine import QuantumCryptographyEngine
from .core.types import QuantumAlgorithm, SecurityLevel
from .exceptions import *

__version__ = "1.0.0"
__all__ = [
    "QuantumCryptographyEngine",
    "QuantumAlgorithm",
    "SecurityLevel",
    "QuantumConfig",
    "initialize_quantum_platform",
    "get_quantum_engine",
]

# Global engine instance
_quantum_engine: QuantumCryptographyEngine | None = None


async def initialize_quantum_platform(config: QuantumConfig | None = None) -> bool:
    """
    Initialize the quantum cryptography platform.

    Args:
        config: Optional configuration. If None, loads from environment.

    Returns:
        True if initialization successful
    """
    global _quantum_engine

    try:
        if config is None:
            config = QuantumConfig.from_env()

        # Setup logging
        log_level = getattr(logging, config.log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            filename=config.log_file,
        )

        # Initialize engine
        _quantum_engine = QuantumCryptographyEngine(config)

        logging.info("Scorpius Quantum Cryptography Platform initialized")
        return True

    except Exception as e:
        logging.error(f"Failed to initialize quantum platform: {e}")
        return False


def get_quantum_engine() -> QuantumCryptographyEngine:
    """Get the global quantum engine instance."""
    if _quantum_engine is None:
        raise RuntimeError(
            "Quantum platform not initialized. Call initialize_quantum_platform() first."
        )
    return _quantum_engine


def is_initialized() -> bool:
    """Check if the quantum platform is initialized."""
    return _quantum_engine is not None


async def shutdown_quantum_platform() -> None:
    """Shutdown the quantum platform and cleanup resources."""
    global _quantum_engine

    if _quantum_engine is not None:
        await _quantum_engine.cleanup()
        _quantum_engine = None
        logging.info("Quantum platform shutdown complete")


# Convenience functions for quick access
async def quick_generate_keypair(
    algorithm: QuantumAlgorithm = QuantumAlgorithm.LATTICE_BASED,
    security_level: SecurityLevel = SecurityLevel.LEVEL_3,
) -> tuple[str, str]:
    """Quick keypair generation with default engine."""
    engine = get_quantum_engine()
    return await engine.generate_keypair(algorithm, security_level)


async def quick_encrypt(message: bytes, public_key_id: str) -> str:
    """Quick encryption with default engine."""
    engine = get_quantum_engine()
    return await engine.encrypt_message(message, public_key_id)
