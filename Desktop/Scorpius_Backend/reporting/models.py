"""
Enterprise Reporting Models
===========================

Comprehensive data models for the enterprise reporting system including
Pydantic models for API requests/responses and SQLAlchemy models for database persistence.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text,
    create_engine, MetaData, Table
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

# SQLAlchemy Base
Base = declarative_base()
metadata = MetaData()


# === ENUMS ===

class SeverityLevel(str, Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityCategory(str, Enum):
    """Categories of vulnerabilities"""
    REENTRANCY = "reentrancy"
    ACCESS_CONTROL = "access_control"
    ARITHMETIC = "arithmetic"
    UNCHECKED_CALLS = "unchecked_calls"
    DENIAL_OF_SERVICE = "denial_of_service"
    FRONT_RUNNING = "front_running"
    TIME_MANIPULATION = "time_manipulation"
    SHORT_ADDRESS = "short_address"
    UNKNOWN = "unknown"


class FindingType(str, Enum):
    """Types of security findings"""
    VULNERABILITY = "vulnerability"
    WARNING = "warning"
    OPTIMIZATION = "optimization"
    INFORMATIONAL = "informational"


class ScanStatus(str, Enum):
    """Status of security scans"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ReportStatus(str, Enum):
    """Status of reports"""
    DRAFT = "draft"
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    PUBLISHED = "published"


class ReportFormat(str, Enum):
    """Supported report formats"""
    PDF = "pdf"
    HTML = "html"
    MARKDOWN = "markdown"
    SARIF = "sarif"
    CSV = "csv"
    JSON = "json"


# === CORE BUSINESS MODELS ===

class VulnerabilityFinding(BaseModel):
    """A security vulnerability finding"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    severity: SeverityLevel
    category: VulnerabilityCategory
    finding_type: FindingType = FindingType.VULNERABILITY
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    
    # Location information
    file_path: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    function_name: Optional[str] = None
    contract_name: Optional[str] = None
    
    # Technical details
    code_snippet: Optional[str] = None
    gas_estimate: Optional[int] = None
    impact: Optional[str] = None
    recommendation: Optional[str] = None
    references: List[str] = Field(default_factory=list)
    
    # Metadata
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    tool_name: Optional[str] = None
    rule_id: Optional[str] = None
    cwe_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Reentrancy in withdraw function",
                "description": "The withdraw function is vulnerable to reentrancy attacks",
                "severity": "high",
                "category": "reentrancy",
                "file_path": "/contracts/Bank.sol",
                "line_number": 45
            }
        }


class ContractInfo(BaseModel):
    """Information about a smart contract"""
    name: str
    file_path: str
    source_code: Optional[str] = None
    bytecode: Optional[str] = None
    abi: Optional[List[Dict[str, Any]]] = None
    compiler_version: Optional[str] = None
    optimization_enabled: Optional[bool] = None
    lines_of_code: Optional[int] = None
    complexity_score: Optional[float] = None


class ScanResult(BaseModel):
    """Complete scan result with all findings"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_name: str = Field(..., min_length=1, max_length=255)
    scan_type: str = Field(default="comprehensive")
    status: ScanStatus = ScanStatus.COMPLETED
    
    # Contract information
    contracts: List[ContractInfo] = Field(default_factory=list)
    total_lines: int = Field(default=0, ge=0)
    
    # Findings
    vulnerabilities: List[VulnerabilityFinding] = Field(default_factory=list)
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Metadata
    scanner_version: str = Field(default="1.0.0")
    scan_config: Dict[str, Any] = Field(default_factory=dict)
    
    # Computed properties
    @property
    def total_issues(self) -> int:
        return len(self.vulnerabilities)
    
    @property
    def critical_issues(self) -> int:
        return len([v for v in self.vulnerabilities if v.severity == SeverityLevel.CRITICAL])
    
    @property
    def high_issues(self) -> int:
        return len([v for v in self.vulnerabilities if v.severity == SeverityLevel.HIGH])
    
    @property
    def medium_issues(self) -> int:
        return len([v for v in self.vulnerabilities if v.severity == SeverityLevel.MEDIUM])
    
    @property
    def low_issues(self) -> int:
        return len([v for v in self.vulnerabilities if v.severity == SeverityLevel.LOW])
    
    @property
    def info_issues(self) -> int:
        return len([v for v in self.vulnerabilities if v.severity == SeverityLevel.INFO])
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ScanSummary(BaseModel):
    """Summary model for listing scans"""
    id: str
    project_name: str
    status: ScanStatus
    total_issues: int
    critical_issues: int
    high_issues: int
    created_at: datetime
    completed_at: datetime | None = None
    
    class Config:
        from_attributes = True


# === API REQUEST/RESPONSE MODELS ===

class ReportJobCreate(BaseModel):
    """Request model for creating report jobs"""
    scan_id: str
    formats: List[str] = Field(default=["html", "json"], description="Output formats")
    theme: str = Field(default="light_corporate", description="Theme to use")
    include_signature: bool = Field(default=False, description="Include digital signature")
    notify_webhook: bool = Field(default=False, description="Send webhook notification")
    webhook_url: Optional[str] = None
    custom_title: Optional[str] = None
    custom_template: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "scan_id": "scan-123",
                "formats": ["html", "json", "pdf"],
                "theme": "dark_pro",
                "include_signature": True,
                "custom_title": "Custom Security Report"
            }
        }


class ReportJobResponse(BaseModel):
    """Response model for report jobs"""
    id: str
    scan_id: str
    status: str
    formats: List[str]
    theme: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    download_urls: Dict[str, str] = Field(default_factory=dict)
    error_message: Optional[str] = None
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    
    class Config:
        from_attributes = True


class ReportTemplateCreate(BaseModel):
    """Request model for creating report templates"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    template_content: str = Field(..., description="Jinja2 template content")
    output_formats: List[str] = Field(..., description="Supported output formats")
    is_public: bool = Field(default=False, description="Public template")
    category: str = Field(default="custom", description="Template category")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Executive Summary Template",
                "description": "High-level summary for executives",
                "template_content": "<h1>{{ report_title }}</h1>...",
                "output_formats": ["html", "pdf"],
                "category": "executive"
            }
        }


class ReportTemplateResponse(BaseModel):
    """Response model for report templates"""
    id: str
    name: str
    description: Optional[str]
    output_formats: List[str]
    is_public: bool
    category: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    usage_count: int = 0
    
    class Config:
        from_attributes = True


class ReportExportRequest(BaseModel):
    """Request model for bulk report exports"""
    report_ids: List[str]
    export_format: str = Field(default="zip", description="Export format (zip, tar)")
    include_metadata: bool = Field(default=True)
    password_protect: bool = Field(default=False)
    password: Optional[str] = None


class ReportPublishRequest(BaseModel):
    """Request model for publishing reports"""
    report_id: str
    publish_settings: Dict[str, Any] = Field(default_factory=dict)
    access_level: str = "private"  # private, internal, public
    expiry_date: Optional[datetime] = None
    password_protected: bool = False
    password: Optional[str] = None


class ReportDiffRequest(BaseModel):
    """Request model for generating diff reports"""
    baseline_scan_id: str
    current_scan_id: str
    diff_type: str = Field(default="full", description="full, summary, or vulnerabilities_only")
    output_format: str = Field(default="html")
    include_charts: bool = Field(default=True)


class ReportDiffResponse(BaseModel):
    """Response model for report diff operations"""
    diff_id: str
    report_1_id: str
    report_2_id: str
    diff_summary: Dict[str, Any]
    detailed_diff: Dict[str, Any]
    generated_at: datetime
    status: str


class ScanRequest(BaseModel):
    """Request model for initiating scans"""
    project_name: str = Field(..., min_length=1, max_length=255)
    contract_files: List[str] = Field(..., description="List of contract file paths")
    scan_type: str = Field(default="comprehensive", description="Scan type")
    priority: str = Field(default="normal", description="Scan priority")
    webhook_url: Optional[str] = None
    custom_config: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_name": "DeFi Protocol v2",
                "contract_files": ["/contracts/Token.sol", "/contracts/Exchange.sol"],
                "scan_type": "comprehensive",
                "priority": "high"
            }
        }


# === DATABASE MODELS ===

class User(Base):
    """User database model"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)


class Report(Base):
    """Report database model"""
    __tablename__ = "reports"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    scan_id = Column(String(36), nullable=False)
    format = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default=ReportStatus.DRAFT.value)
    file_path = Column(String(1000), nullable=True)
    download_url = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(String(36), nullable=False)


class ReportJob(Base):
    """Database model for report generation jobs"""
    __tablename__ = "report_jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String(36), nullable=False)
    status = Column(String(50), default="pending")
    formats = Column(JSON, default=list)
    theme = Column(String(100), default="light_corporate")
    include_signature = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(String(36), nullable=False)
    download_urls = Column(JSON, default=dict)
    error_message = Column(Text, nullable=True)
    progress = Column(Float, default=0.0)


class ReportTemplate(Base):
    """Database model for report templates"""
    __tablename__ = "report_templates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    template_content = Column(Text, nullable=False)
    output_formats = Column(JSON, default=list)
    is_public = Column(Boolean, default=False)
    category = Column(String(100), default="custom")
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    created_by = Column(String(36), nullable=False)
    usage_count = Column(Integer, default=0)


class ReportAuditLog(Base):
    """Database model for report audit logs"""
    __tablename__ = "report_audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(36), nullable=False)
    action = Column(String(100), nullable=False)
    user_id = Column(String(36), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=func.now())
    details = Column(JSON, default=dict)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)


class AuditLog(Base):
    """General audit log model"""
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(36), nullable=False)
    action = Column(String(100), nullable=False)
    user_id = Column(String(36), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=func.now())
    changes = Column(JSON, default=dict)
    ip_address = Column(String(45), nullable=True)


# Additional models for compatibility with existing API
class ReportAccessLog(Base):
    """Access log for report downloads/views"""
    __tablename__ = "report_access_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(36), nullable=False)
    user_id = Column(String(36), nullable=False)
    access_type = Column(String(50), nullable=False)  # view, download, share
    timestamp = Column(DateTime(timezone=True), default=func.now())
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)


class ReportDiff(Base):
    """Database model for report diffs"""
    __tablename__ = "report_diffs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    baseline_scan_id = Column(String(36), nullable=False)
    current_scan_id = Column(String(36), nullable=False)
    diff_type = Column(String(50), default="full")
    output_format = Column(String(20), nullable=False)
    file_path = Column(String(1000), nullable=True)
    download_url = Column(String(1000), nullable=True)
    summary = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String(36), nullable=False)



