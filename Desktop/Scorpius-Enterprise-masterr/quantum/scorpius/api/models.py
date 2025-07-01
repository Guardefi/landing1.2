"""
Pydantic models for Scorpius Enterprise API
Defines request/response models for FastAPI endpoints.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

# ============================================================================
# ENUMS
# ============================================================================


class QuantumAlgorithmEnum(str, Enum):
    """Quantum-resistant algorithms."""

    LATTICE_BASED = "lattice_based"
    HASH_BASED = "hash_based"
    CODE_BASED = "code_based"
    MULTIVARIATE = "multivariate"


class SecurityLevelEnum(int, Enum):
    """Security levels."""

    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5


class ScanTypeEnum(str, Enum):
    """Security scan types."""

    QUICK = "quick"
    COMPREHENSIVE = "comprehensive"
    AI_ENHANCED = "ai_enhanced"
    DEEP = "deep"


class ThreatLevelEnum(str, Enum):
    """Threat levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReportTypeEnum(str, Enum):
    """Analytics report types."""

    SECURITY = "security"
    PERFORMANCE = "performance"
    USAGE = "usage"
    COMPLIANCE = "compliance"


# ============================================================================
# HEALTH AND STATUS MODELS
# ============================================================================


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: datetime
    version: str


class ModuleStatus(BaseModel):
    """Individual module status."""

    name: str
    version: str
    status: str
    health_score: float
    last_check: datetime
    error_count: int
    uptime: float


class PlatformStatusResponse(BaseModel):
    """Platform status response."""

    platform_version: str
    uptime_seconds: float
    total_modules: int
    active_modules: int
    overall_health: float
    modules: List[ModuleStatus]
    is_enterprise: bool
    license_valid: bool


# ============================================================================
# QUANTUM CRYPTOGRAPHY MODELS
# ============================================================================


class QuantumEncryptRequest(BaseModel):
    """Request to encrypt data with quantum-resistant cryptography."""

    message: str = Field(..., description="Message to encrypt")
    algorithm: QuantumAlgorithmEnum = Field(default=QuantumAlgorithmEnum.LATTICE_BASED)
    security_level: SecurityLevelEnum = Field(default=SecurityLevelEnum.LEVEL_3)


class QuantumEncryptResponse(BaseModel):
    """Response from quantum encryption."""

    encrypted_data: str
    algorithm: str
    security_level: int
    timestamp: str
    status: str


class KeyGenerationRequest(BaseModel):
    """Request to generate quantum-resistant keys."""

    algorithm: QuantumAlgorithmEnum = Field(default=QuantumAlgorithmEnum.LATTICE_BASED)
    security_level: SecurityLevelEnum = Field(default=SecurityLevelEnum.LEVEL_3)
    key_type: str = Field(
        default="encryption", description="Type of key: encryption, signature"
    )


class KeyGenerationResponse(BaseModel):
    """Response from key generation."""

    key_id: str
    algorithm: str
    security_level: int
    public_key: str
    created_at: str
    key_type: Optional[str] = None


# ============================================================================
# SECURITY MODELS
# ============================================================================


class SecurityScanRequest(BaseModel):
    """Request to perform security scan."""

    target: str = Field(..., description="Target to scan (address, contract, etc.)")
    scan_type: ScanTypeEnum = Field(default=ScanTypeEnum.COMPREHENSIVE)
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SecurityScanResponse(BaseModel):
    """Response from security scan."""

    target: str
    scan_type: str
    status: str
    threats_found: Optional[int] = 0
    risk_level: Optional[str] = "low"
    scan_duration: Optional[float] = None
    findings: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    timestamp: str


class ThreatAlert(BaseModel):
    """Threat alert model."""

    id: str
    level: ThreatLevelEnum
    title: str
    description: str
    detected_at: str
    source: str
    status: str = "active"
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


# ============================================================================
# ANALYTICS MODELS
# ============================================================================


class AnalyticsReportRequest(BaseModel):
    """Request to generate analytics report."""

    report_type: ReportTypeEnum
    timeframe: str = Field(default="24h", description="Time range: 1h, 24h, 7d, 30d")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    format: str = Field(default="json", description="Output format: json, csv, pdf")


class AnalyticsReportResponse(BaseModel):
    """Response from analytics report generation."""

    report_type: str
    timeframe: str
    generated_at: str
    status: str
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    download_url: Optional[str] = None


class MetricsResponse(BaseModel):
    """Platform metrics response."""

    quantum_operations: Dict[str, Union[int, float]]
    security_scans: Dict[str, Union[int, float]]
    performance: Dict[str, Union[int, float]]
    timestamp: str


# ============================================================================
# CONFIGURATION MODELS
# ============================================================================


class ConfigResponse(BaseModel):
    """Platform configuration response."""

    platform_version: str
    enterprise_edition: bool
    features: Dict[str, bool]
    limits: Dict[str, Union[int, float]]


# ============================================================================
# WEBSOCKET MODELS
# ============================================================================


class WebSocketMessage(BaseModel):
    """Base WebSocket message."""

    type: str
    timestamp: str
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DashboardUpdate(BaseModel):
    """Dashboard update message."""

    type: str = "dashboard_update"
    metric_name: str
    metric_value: Union[int, float, str]
    timestamp: str


class ThreatNotification(BaseModel):
    """Real-time threat notification."""

    type: str = "threat_notification"
    threat_id: str
    level: ThreatLevelEnum
    title: str
    description: str
    timestamp: str


class OperationStatus(BaseModel):
    """Operation status update."""

    type: str = "operation_status"
    operation_id: str
    operation_type: str
    status: str
    progress: Optional[float] = None
    timestamp: str


# ============================================================================
# ERROR MODELS
# ============================================================================


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: str
    timestamp: str
    request_id: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    """Validation error response."""

    error: str = "validation_error"
    detail: str
    errors: List[Dict[str, Any]]
    timestamp: str


# ============================================================================
# PAGINATION MODELS
# ============================================================================


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=1000)


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""

    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# AUDIT MODELS
# ============================================================================


class AuditLog(BaseModel):
    """Audit log entry."""

    id: str
    user_id: str
    action: str
    resource: str
    timestamp: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AuditLogResponse(BaseModel):
    """Audit log response."""

    logs: List[AuditLog]
    total: int
    page: int
    page_size: int
