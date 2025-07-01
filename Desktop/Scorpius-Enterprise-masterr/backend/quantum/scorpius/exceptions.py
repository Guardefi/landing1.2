"""
Scorpius Enterprise Exceptions
"""


class ScorpiusError(Exception):
    """Base exception for Scorpius platform."""


class LicenseError(ScorpiusError):
    """License validation errors."""


class ConfigurationError(ScorpiusError):
    """Configuration related errors."""


class InitializationError(ScorpiusError):
    """Module initialization errors."""


class EngineError(ScorpiusError):
    """Engine operation errors."""
