"""
Core module for API Gateway
Provides basic orchestrator and config functionality
"""

import os
from typing import Optional, Dict, Any, List, ClassVar
from pydantic import BaseModel

# =============================================================================
# CONFIGURATION
# =============================================================================

class SecurityConfig:
    """Security configuration"""
    def __init__(self):
        self.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")

class RedisConfig:
    """Redis configuration"""
    def __init__(self):
        self.url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.max_connections = int(os.getenv("REDIS_MAX_CONNECTIONS", "10"))
        self.socket_timeout = int(os.getenv("REDIS_SOCKET_TIMEOUT", "5"))

class Config:
    """Configuration for the API Gateway"""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.database_url = os.getenv("DATABASE_URL", "postgresql://localhost:5432/scorpius")
        self.jwt_secret = os.getenv("JWT_SECRET", "default-secret-key")
        self.jwt_algorithm = "HS256"
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Nested configurations
        self.security = SecurityConfig()
        self.redis = RedisConfig()

def get_config() -> Config:
    """Get the global configuration instance"""
    return Config()

# =============================================================================
# TYPES
# =============================================================================

class ServiceStatus(BaseModel):
    """Service status enumeration"""
    HEALTHY: ClassVar[str] = "healthy"
    UNHEALTHY: ClassVar[str] = "unhealthy"
    UNKNOWN: ClassVar[str] = "unknown"

class ServiceInfo(BaseModel):
    """Information about a service"""
    name: str
    url: str
    status: str = ServiceStatus.UNKNOWN
    last_check: Optional[str] = None
    response_time: Optional[float] = None

class HealthCheckResult(BaseModel):
    """Result of a health check"""
    service: str
    status: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None

# =============================================================================
# ORCHESTRATOR
# =============================================================================

class CoreOrchestrator:
    """Basic orchestrator for managing services"""
    
    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.config = get_config()
    
    def register_service(self, name: str, url: str) -> None:
        """Register a service"""
        self.services[name] = ServiceInfo(name=name, url=url)
    
    def get_service(self, name: str) -> Optional[ServiceInfo]:
        """Get service information"""
        return self.services.get(name)
    
    def get_all_services(self) -> Dict[str, ServiceInfo]:
        """Get all registered services"""
        return self.services.copy()
    
    def get_services(self) -> Dict[str, ServiceInfo]:
        """Get all registered services (alias for get_all_services)"""
        return self.get_all_services()
    
    def health_check(self, service_name: str) -> HealthCheckResult:
        """Perform a health check on a service"""
        service = self.get_service(service_name)
        if not service:
            return HealthCheckResult(
                service=service_name,
                status=ServiceStatus.UNKNOWN,
                timestamp="",
                details={"error": "Service not found"}
            )
        
        # Simple health check - just return healthy for now
        return HealthCheckResult(
            service=service_name,
            status=ServiceStatus.HEALTHY,
            timestamp="",
            details={"url": service.url}
        )

# Global orchestrator instance
_orchestrator: Optional[CoreOrchestrator] = None

def get_orchestrator() -> CoreOrchestrator:
    """Get the global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = CoreOrchestrator()
    return _orchestrator

# Re-export for convenience
__all__ = [
    'get_orchestrator',
    'get_config',
    'Config',
    'ServiceInfo',
    'ServiceStatus',
    'HealthCheckResult',
    'CoreOrchestrator'
] 