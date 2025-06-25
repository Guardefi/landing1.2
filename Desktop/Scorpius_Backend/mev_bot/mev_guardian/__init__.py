"""
MevGuardian - Enterprise-grade dual-mode MEV bot system.

This package provides both offensive (attack) and defensive (guardian) MEV capabilities,
transforming traditional profit-seeking MEV bots into proactive security instruments.
"""

from .config import MevGuardianConfig
from .types import (
    ThreatType,
    ThreatSeverity,
    Threat,
    SimulationResult,
    HoneypotResult,
    ForensicAnalysis,
    GuardianMetrics,
    WebSocketEvent,
    WebSocketEventType
)
from .guardian_engine import GuardianEngine
from .database import DatabaseManager, get_database_manager, close_database_manager
from .api import app

__version__ = "1.0.0"
__all__ = [
    "MevGuardianConfig",
    "ThreatType",
    "ThreatSeverity", 
    "Threat",
    "SimulationResult",
    "HoneypotResult",
    "ForensicAnalysis",
    "GuardianMetrics",
    "WebSocketEvent",
    "WebSocketEventType",
    "GuardianEngine",
    "DatabaseManager",
    "get_database_manager",
    "close_database_manager",
    "app"
]
