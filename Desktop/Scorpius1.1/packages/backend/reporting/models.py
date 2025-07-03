"""
Scorpius Reporting Service - Data Models
Pydantic models for request/response validation and data structures
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from uuid import UUID


class ReportStatus(str, Enum):
    """Report generation status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportType(str, Enum):
    """Report type enumeration"""
    PDF = "pdf"
    SARIF = "sarif"


class ReportRequest(BaseModel):
    """Base report request"""
    title: str = Field(..., description="Report title")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class PDFReportRequest(ReportRequest):
    """PDF report generation request"""
    data: Dict[str, Any] = Field(..., description="Report data")
    template: Optional[str] = Field(default="default", description="PDF template to use")
    include_signature: bool = Field(default=True, description="Include cryptographic signature")
    watermark: Optional[str] = Field(None, description="Optional watermark text")
    
    @validator('data')
    def validate_data(cls, v):
        if not v:
            raise ValueError("Report data cannot be empty")
        return v


class ScanResult(BaseModel):
    """Individual scan result for SARIF report"""
    rule_id: str = Field(..., description="Rule identifier")
    level: str = Field(..., description="Finding level (error, warning, info)")
    message: str = Field(..., description="Finding message")
    locations: List[Dict[str, Any]] = Field(default_factory=list, description="Finding locations")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional properties")


class ToolInfo(BaseModel):
    """Tool information for SARIF report"""
    name: str = Field(..., description="Tool name")
    version: str = Field(..., description="Tool version")
    organization: Optional[str] = Field(None, description="Tool organization")
    url: Optional[str] = Field(None, description="Tool URL")


class SARIFReportRequest(ReportRequest):
    """SARIF report generation request"""
    scan_results: List[ScanResult] = Field(..., description="Scan results")
    tool_info: ToolInfo = Field(..., description="Tool information")
    run_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Run metadata")
    include_signature: bool = Field(default=True, description="Include cryptographic signature")
    
    @validator('scan_results')
    def validate_scan_results(cls, v):
        if not v:
            raise ValueError("Scan results cannot be empty")
        return v


class ReportResponse(BaseModel):
    """Report generation response"""
    report_id: str = Field(..., description="Unique report identifier")
    status: ReportStatus = Field(..., description="Report generation status")
    message: str = Field(..., description="Status message")
    estimated_completion: Optional[str] = Field(None, description="Estimated completion time")
    download_url: Optional[str] = Field(None, description="Download URL when completed")


class SignatureInfo(BaseModel):
    """Cryptographic signature information"""
    algorithm: str = Field(..., description="Signature algorithm")
    timestamp: str = Field(..., description="Signature timestamp")
    certificate_fingerprint: str = Field(..., description="Certificate fingerprint")
    public_key_hash: Optional[str] = Field(None, description="Public key hash")


class AuditEntry(BaseModel):
    """Audit trail entry"""
    event_id: str = Field(..., description="Unique event identifier")
    event_type: str = Field(..., description="Event type")
    timestamp: str = Field(..., description="Event timestamp")
    user_id: str = Field(..., description="User identifier")
    details: Dict[str, Any] = Field(..., description="Event details")


class ReportMetadata(BaseModel):
    """Report metadata stored in QLDB"""
    report_id: str = Field(..., description="Report identifier")
    document_hash: str = Field(..., description="Document hash")
    document_type: str = Field(..., description="Document type")
    created_at: str = Field(..., description="Creation timestamp")
    created_by: str = Field(..., description="Creator user ID")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")


class HealthCheck(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    timestamp: str = Field(..., description="Check timestamp")
    version: str = Field(..., description="Service version")
    dependencies: Optional[Dict[str, str]] = Field(default_factory=dict, description="Dependency status")


class MetricsResponse(BaseModel):
    """Metrics response"""
    reports_generated_total: int = Field(default=0, description="Total reports generated")
    signatures_created_total: int = Field(default=0, description="Total signatures created")
    audit_entries_total: int = Field(default=0, description="Total audit entries")
    service_uptime_seconds: float = Field(default=0.0, description="Service uptime in seconds")
    active_reports: int = Field(default=0, description="Currently processing reports")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Error details")
    timestamp: str = Field(..., description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier")


class ReportListResponse(BaseModel):
    """Report list response"""
    reports: List[Dict[str, Any]] = Field(..., description="Report list")
    total: int = Field(..., description="Total number of reports")
    page: int = Field(default=1, description="Current page")
    per_page: int = Field(default=10, description="Reports per page")


class BatchReportRequest(BaseModel):
    """Batch report generation request"""
    reports: List[Dict[str, Any]] = Field(..., description="List of report requests")
    batch_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Batch metadata")
    
    @validator('reports')
    def validate_reports(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Reports list cannot be empty")
        if len(v) > 50:  # Limit batch size
            raise ValueError("Batch size cannot exceed 50 reports")
        return v


class BatchReportResponse(BaseModel):
    """Batch report generation response"""
    batch_id: str = Field(..., description="Batch identifier")
    report_ids: List[str] = Field(..., description="Individual report identifiers")
    status: str = Field(..., description="Batch status")
    message: str = Field(..., description="Status message")
    estimated_completion: Optional[str] = Field(None, description="Estimated completion time")
