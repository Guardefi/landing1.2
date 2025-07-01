"""
Scorpius Core SDK for service registration and communication
"""

from .service_registration import (
    ServiceRegistrationConfig,
    register_service,
    unregister_service,
)

__all__ = [
    "register_service",
    "unregister_service",
    "ServiceRegistrationConfig"]
