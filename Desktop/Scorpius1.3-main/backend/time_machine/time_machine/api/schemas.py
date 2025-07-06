"""
API Schema Definitions using Pydantic
Request and response models for the Time Machine API.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

from ..core.models import FrameType, PatchType, SessionType, VMBackend


class JobStatusEnum(str, Enum):
    """Job status enumeration for API."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Request Models


class ReplayRequest(BaseModel):
    """Request model for replay operations."""

    name: Optional[str] = Field(None, description="Human-readable name for the replay")
    description: Optional[str] = Field(
        None, description="Description of the replay purpose"
    )
    block_number: Optional[int] = Field(
        None, description="Specific block number to replay"
    )
    tx_hash: Optional[str] = Field(
        None, description="Specific transaction hash to replay"
    )
    from_block: Optional[int] = Field(None, description="Start block for range replay")
    to_block: Optional[int] = Field(None, description="End block for range replay")
    vm_backend: VMBackend = Field(VMBackend.ANVIL, description="VM backend to use")
    patches: List[Dict[str, Any]] = Field(
        default_factory=list, description="State patches to apply"
    )
    fork_url: Optional[str] = Field(None, description="Blockchain RPC URL to fork from")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @validator("tx_hash")
    def validate_tx_hash(cls, v):
        if v and not v.startswith("0x"):
            raise ValueError("Transaction hash must start with 0x")
        return v

    @validator("from_block", "to_block", "block_number")
    def validate_block_numbers(cls, v):
        if v is not None and v < 0:
            raise ValueError("Block numbers must be non-negative")
        return v


class PatchRequest(BaseModel):
    """Request model for applying patches."""

    branch_id: str = Field(..., description="Target branch ID")
    patches: List[Dict[str, Any]] = Field(..., description="Patches to apply")
    conflict_resolution: str = Field("fail", description="Conflict resolution strategy")
    validation_level: str = Field("strict", description="Validation level")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class DiffRequest(BaseModel):
    """Request model for generating diffs."""

    from_branch_id: str = Field(..., description="Source branch ID")
    to_branch_id: str = Field(..., description="Target branch ID")
    format: str = Field("json", description="Output format")
    include_unchanged: bool = Field(False, description="Include unchanged items")
    max_depth: int = Field(10, description="Maximum nesting depth to analyze")


class ForensicSessionRequest(BaseModel):
    """Request model for creating forensic sessions."""

    name: str = Field(..., description="Session name")
    session_type: SessionType = Field(..., description="Type of forensic session")
    description: Optional[str] = Field(None, description="Session description")
    analyst: Optional[str] = Field(None, description="Analyst name")
    target_contracts: List[str] = Field(
        default_factory=list, description="Target contract addresses"
    )
    target_transactions: List[str] = Field(
        default_factory=list, description="Target transaction hashes"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class BookmarkRequest(BaseModel):
    """Request model for adding bookmarks."""

    session_id: str = Field(..., description="Forensic session ID")
    name: str = Field(..., description="Bookmark name")
    block_number: int = Field(..., description="Block number")
    tx_index: int = Field(0, description="Transaction index")
    description: Optional[str] = Field(None, description="Bookmark description")
    tags: List[str] = Field(default_factory=list, description="Bookmark tags")


class FindingRequest(BaseModel):
    """Request model for adding findings."""

    session_id: str = Field(..., description="Forensic session ID")
    title: str = Field(..., description="Finding title")
    severity: str = Field(..., description="Finding severity")
    description: str = Field(..., description="Finding description")
    evidence: List[str] = Field(default_factory=list, description="Evidence list")
    recommendations: List[str] = Field(
        default_factory=list, description="Recommendations"
    )


class AnalysisRequest(BaseModel):
    """Request model for running analysis plugins."""

    branch_id: str = Field(..., description="Branch to analyze")
    session_type: SessionType = Field(..., description="Analysis session type")
    plugins: Optional[List[str]] = Field(None, description="Specific plugins to run")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Analysis parameters"
    )


# Response Models


class ReplayResponse(BaseModel):
    """Response model for replay operations."""

    job_id: str
    branch_id: str
    status: JobStatusEnum
    name: Optional[str] = None
    description: Optional[str] = None
    vm_backend: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PatchResponse(BaseModel):
    """Response model for patch operations."""

    original_branch_id: str
    new_branch_id: str
    patches_applied: int
    conflicts_detected: int
    conflicts_resolved: int
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DiffResponse(BaseModel):
    """Response model for diff operations."""

    diff_id: str
    from_branch_id: str
    to_branch_id: str
    format: str
    storage_changes: Dict[str, Dict[str, Any]]
    balance_changes: Dict[str, Dict[str, Any]]
    code_changes: Dict[str, Dict[str, Any]]
    nonce_changes: Dict[str, Dict[str, Any]]
    summary: Dict[str, int]
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BranchInfo(BaseModel):
    """Branch information model."""

    branch_id: str
    name: str
    description: Optional[str] = None
    parent_branch_id: Optional[str] = None
    snapshot_id: str
    block_number: int
    tx_index: int
    patches_applied: int
    created_at: datetime
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class JobInfo(BaseModel):
    """Job information model."""

    job_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    status: JobStatusEnum
    vm_backend: str
    block_number: Optional[int] = None
    tx_hash: Optional[str] = None
    from_block: Optional[int] = None
    to_block: Optional[int] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ForensicSessionInfo(BaseModel):
    """Forensic session information model."""

    session_id: str
    name: str
    session_type: SessionType
    description: Optional[str] = None
    analyst: Optional[str] = None
    target_contracts: List[str]
    target_transactions: List[str]
    bookmarks_count: int
    findings_count: int
    created_at: datetime
    last_updated: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TimelineEventResponse(BaseModel):
    """Timeline event response model."""

    frame_id: str
    frame_type: FrameType
    block_number: int
    tx_index: int
    gas_used: Optional[int] = None
    gas_limit: Optional[int] = None
    opcode: Optional[str] = None
    pc: Optional[int] = None
    depth: int = 0
    address: Optional[str] = None
    caller: Optional[str] = None
    value: Optional[str] = None
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    stack: List[str] = Field(default_factory=list)
    memory: Dict[str, str] = Field(default_factory=dict)
    storage: Dict[str, str] = Field(default_factory=dict)
    logs: List[Dict[str, Any]] = Field(default_factory=list)
    error: Optional[str] = None
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SnapshotInfo(BaseModel):
    """Snapshot information model."""

    snapshot_id: str
    branch_id: str
    block_number: int
    content_hash: str
    created_at: datetime
    size_bytes: int
    disk_size_bytes: Optional[int] = None
    incremental: bool = False
    parent_snapshot_id: Optional[str] = None
    compressed: bool = True


class AnalysisResult(BaseModel):
    """Analysis result model."""

    plugin_name: str
    plugin_version: Optional[str] = None
    analysis_type: str
    results: Dict[str, Any]
    execution_time_ms: Optional[float] = None
    status: str
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EngineStats(BaseModel):
    """Engine statistics model."""

    total_branches: int
    active_jobs: int
    forensic_sessions: int
    registered_plugins: int
    vm_backend: str
    storage_stats: Dict[str, Any] = Field(default_factory=dict)
    uptime_seconds: Optional[float] = None


class MacroInfo(BaseModel):
    """Macro information model."""

    name: str
    description: str
    parameters: List[str] = Field(default_factory=list)
    template: Dict[str, Any] = Field(default_factory=dict)


class ValidationResult(BaseModel):
    """Validation result model."""

    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Error Models


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None


class ValidationError(BaseModel):
    """Validation error model."""

    field: str
    message: str
    invalid_value: Optional[Any] = None


# WebSocket Models


class WSMessage(BaseModel):
    """WebSocket message model."""

    type: str
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    session_id: Optional[str] = None


class WSTimelineEvent(BaseModel):
    """WebSocket timeline event model."""

    event_type: str = "timeline_event"
    branch_id: str
    event: TimelineEventResponse


class WSJobStatus(BaseModel):
    """WebSocket job status update model."""

    event_type: str = "job_status"
    job_id: str
    status: JobStatusEnum
    message: Optional[str] = None
    progress: Optional[float] = None


class WSAnalysisUpdate(BaseModel):
    """WebSocket analysis update model."""

    event_type: str = "analysis_update"
    session_id: str
    plugin_name: str
    status: str
    progress: Optional[float] = None
    result: Optional[Dict[str, Any]] = None


# Export Models


class ExportRequest(BaseModel):
    """Export request model."""

    branch_id: str = Field(..., description="Branch to export")
    format: str = Field("json", description="Export format")
    include_snapshots: bool = Field(True, description="Include snapshot data")
    include_metadata: bool = Field(True, description="Include metadata")
    compression: bool = Field(True, description="Compress export")


class ExportResponse(BaseModel):
    """Export response model."""

    export_id: str
    branch_id: str
    format: str
    file_path: Optional[str] = None
    download_url: Optional[str] = None
    size_bytes: int
    created_at: datetime
    expires_at: Optional[datetime] = None


# Bulk Operations


class BulkPatchRequest(BaseModel):
    """Bulk patch request model."""

    patches: List[PatchRequest]
    parallel_execution: bool = Field(False, description="Execute patches in parallel")
    stop_on_error: bool = Field(True, description="Stop execution on first error")


class BulkPatchResponse(BaseModel):
    """Bulk patch response model."""

    total_requests: int
    successful_patches: int
    failed_patches: int
    results: List[Union[PatchResponse, ErrorResponse]]
    execution_time_ms: float
