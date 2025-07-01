"""
Types and models for the Scorpius Core package.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ServiceStatus(str, Enum):
    """Service status enumeration."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"


class ServiceInfo(BaseModel):
    """Service information model."""

    name: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    status: ServiceStatus = Field(..., description="Service status")
    endpoint: str = Field(..., description="Service endpoint URL")
    health_check_url: str = Field(..., description="Health check endpoint")
    last_seen: Optional[datetime] = Field(None, description="Last health check time")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class HealthCheckResult(BaseModel):
    """Health check result model."""

    service_name: str = Field(..., description="Name of the service")
    status: ServiceStatus = Field(..., description="Health status")
    response_time_ms: Optional[float] = Field(
        None, description="Response time in milliseconds"
    )
    error_message: Optional[str] = Field(None, description="Error message if unhealthy")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Check timestamp"
    )
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Additional health details"
    )


class ScanRequest(BaseModel):
    """Smart contract scan request model."""

    contract_address: str = Field(..., description="Contract address to scan")
    blockchain: str = Field(default="ethereum", description="Blockchain network")
    scan_types: List[str] = Field(
        default_factory=list, description="Types of scans to perform"
    )
    priority: int = Field(default=1, description="Scan priority (1-5)")
    callback_url: Optional[str] = Field(None, description="Callback URL for results")


class ScanResult(BaseModel):
    """Smart contract scan result model."""

    scan_id: str = Field(..., description="Unique scan identifier")
    contract_address: str = Field(..., description="Scanned contract address")
    status: str = Field(..., description="Scan status")
    vulnerabilities: List[Dict[str, Any]] = Field(
        default_factory=list, description="Found vulnerabilities"
    )
    risk_score: float = Field(..., description="Overall risk score (0-100)")
    scan_duration_ms: int = Field(..., description="Scan duration in milliseconds")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Scan completion time"
    )


class AlertLevel(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SecurityAlert(BaseModel):
    """Security alert model."""

    alert_id: str = Field(..., description="Unique alert identifier")
    level: AlertLevel = Field(..., description="Alert severity level")
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Alert description")
    source_service: str = Field(..., description="Service that generated the alert")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Alert timestamp"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional alert data"
    )
