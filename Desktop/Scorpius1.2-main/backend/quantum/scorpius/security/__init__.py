"""
Security Module
"""

from datetime import datetime
from enum import Enum


class ThreatLevel(Enum):
    """Security threat levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityAlert:
    """Represents a security alert."""

    def __init__(self, threat_level: ThreatLevel, message: str, source: str):
        self.threat_level = threat_level
        self.message = message
        self.source = source
        self.timestamp = datetime.now()

    def __str__(self):
        return f"SecurityAlert({self.threat_level.value}: {self.message})"
