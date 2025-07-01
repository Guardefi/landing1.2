"""
Core Exceptions
--------------
Custom exceptions for the Scorpius platform.
"""


class ScorpiusError(Exception):
    """Base exception for all Scorpius errors"""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ServiceError(ScorpiusError):
    """Service-related errors"""


class ConfigError(ScorpiusError):
    """Configuration-related errors"""


class DatabaseError(ScorpiusError):
    """Database-related errors"""


class SecurityError(ScorpiusError):
    """Security-related errors"""


class ValidationError(ScorpiusError):
    """Data validation errors"""


class DependencyError(ServiceError):
    """Service dependency errors"""


class HealthCheckError(ServiceError):
    """Health check errors"""
