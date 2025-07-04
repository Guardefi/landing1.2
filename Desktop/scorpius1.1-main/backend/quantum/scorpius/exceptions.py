"""
Scorpius Enterprise Exceptions
"""


class ScorpiusError(Exception):
    """Base exception for Scorpius platform."""

    pass


class LicenseError(ScorpiusError):
    """License validation errors."""

    pass


class ConfigurationError(ScorpiusError):
    """Configuration related errors."""

    pass


class InitializationError(ScorpiusError):
    """Module initialization errors."""

    pass


class EngineError(ScorpiusError):
    """Engine operation errors."""

    pass
