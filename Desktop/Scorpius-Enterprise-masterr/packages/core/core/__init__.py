"""
Scorpius Core Library
====================

Core utilities and orchestration for the Scorpius Enterprise Platform.
"""

__version__ = "0.1.0"
__author__ = "Scorpius Team"
__email__ = "team@scorpius.dev"

from .config import Config, get_config

# Core exports
from .orchestrator_new import CoreOrchestrator
from .orchestrator_new import orchestrator as get_orchestrator
from .types import ServiceInfo, ServiceStatus

__all__ = [
    "CoreOrchestrator",
    "get_orchestrator",
    "Config",
    "get_config",
    "ServiceInfo",
    "ServiceStatus",
]
