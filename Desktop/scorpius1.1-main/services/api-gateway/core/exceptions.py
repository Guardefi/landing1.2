"""
Core exceptions module
Defines standard exceptions used across Scorpius services
"""

class ServiceError(Exception):
    """Base exception for service-related errors"""
    pass

class ConfigError(Exception):
    """Exception raised for configuration errors"""
    pass

class AuthenticationError(Exception):
    """Exception raised for authentication failures"""
    pass

class AuthorizationError(Exception):
    """Exception raised for authorization failures"""
    pass

class ValidationError(Exception):
    """Exception raised for validation failures"""
    pass

class DatabaseError(Exception):
    """Exception raised for database-related errors"""
    pass

class RedisError(Exception):
    """Exception raised for Redis-related errors"""
    pass

class NetworkError(Exception):
    """Exception raised for network-related errors"""
    pass

__all__ = [
    'ServiceError',
    'ConfigError',
    'AuthenticationError',
    'AuthorizationError',
    'ValidationError',
    'DatabaseError',
    'RedisError',
    'NetworkError'
] 