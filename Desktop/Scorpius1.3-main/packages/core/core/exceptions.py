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
    pass


class ConfigError(ScorpiusError):
    """Configuration-related errors"""
    pass


class DatabaseError(ScorpiusError):
    """Database-related errors"""
    pass


class SecurityError(ScorpiusError):
    """Security-related errors"""
    pass


class ValidationError(ScorpiusError):
    """Data validation errors"""
    pass


class DependencyError(ServiceError):
    """Service dependency errors"""
    pass


class HealthCheckError(ServiceError):
    """Health check errors"""
    pass
