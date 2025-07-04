"""
Analytics Module
"""

from enum import Enum


class AnalyticsType(Enum):
    """Types of analytics reports."""

    SECURITY = "security"
    PERFORMANCE = "performance"
    USAGE = "usage"
    COMPLIANCE = "compliance"


class TimeFrame(Enum):
    """Time frames for analytics."""

    HOUR = "1h"
    DAY = "24h"
    WEEK = "7d"
    MONTH = "30d"
    YEAR = "365d"
