"""
Scorpius Bridge Network
Advanced cross-chain interoperability system with atomic swaps,
bridge validation, and secure multi-chain asset transfers.
"""

from .api.endpoints import router as bridge_router
from .api.endpoints import set_bridge_components
from .config.settings import settings
from .core.types import (
    BridgeTransfer,
    BridgeType,
    ChainType,
    SecurityLevel,
    TransferStatus,
    ValidatorNode,
)

__version__ = "1.0.0"
__all__ = [
    "bridge_router",
    "set_bridge_components",
    "settings",
    "BridgeTransfer",
    "BridgeType",
    "ChainType",
    "SecurityLevel",
    "TransferStatus",
    "ValidatorNode",
]
