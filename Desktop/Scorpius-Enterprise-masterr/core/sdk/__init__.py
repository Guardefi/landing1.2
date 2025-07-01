"""
Scorpius Core SDK for service registration and communication
"""

from .service_registration import register_service, unregister_service, ServiceRegistrationConfig

__all__ = ["register_service", "unregister_service", "ServiceRegistrationConfig"]
