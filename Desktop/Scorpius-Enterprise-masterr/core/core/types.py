"""
Core Types and Data Models
--------------------------
Shared type definitions for the Scorpius platform.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum


class ServiceStatus(Enum):
    """Service lifecycle status"""
    STOPPED = "stopped"
    STARTING = "starting" 
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class EventType(Enum):
    """Event types for the event bus"""
    SERVICE_STARTED = "service_started"
    SERVICE_STOPPED = "service_stopped"
    SERVICE_ERROR = "service_error"
    HEALTH_CHECK = "health_check"
    METRIC_UPDATE = "metric_update"
    SECURITY_ALERT = "security_alert"


@dataclass
class ServiceInfo:
    """Information about a registered service"""
    name: str
    module_path: str
    entry_point: str
    dependencies: List[str] = field(default_factory=list)
    health_check: Optional[Callable] = None
    status: ServiceStatus = ServiceStatus.STOPPED
    instance: Optional[Any] = None
    start_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass  
class EventMessage:
    """Event message for the event bus"""
    event_type: EventType
    source: str
    payload: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None


@dataclass
class HealthCheckResult:
    """Health check result"""
    service: str
    healthy: bool
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceMetrics:
    """Service metrics"""
    service: str
    cpu_percent: float
    memory_mb: float
    request_count: int
    error_count: int
    avg_response_time: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
