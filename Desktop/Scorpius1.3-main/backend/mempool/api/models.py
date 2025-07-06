"""
API Models

Pydantic models for request/response validation and documentation.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator


class AlertSeverity(str, Enum):
    """Alert severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status values"""

    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    DISMISSED = "dismissed"


class RuleStatus(str, Enum):
    """Rule status values"""

    ENABLED = "enabled"
    DISABLED = "disabled"


class TransactionStatus(str, Enum):
    """Transaction status values"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"


class PaginationParams(BaseModel):
    """Standard pagination parameters"""

    limit: int = Field(100, ge=1, le=1000, description="Number of items to return")
    offset: int = Field(0, ge=0, description="Number of items to skip")


class TransactionResponse(BaseModel):
    """Transaction data model"""

    hash: str = Field(..., description="Transaction hash")
    chain_id: int = Field(..., description="Blockchain chain ID")
    from_address: str = Field(..., alias="from", description="Sender address")
    to_address: Optional[str] = Field(None, alias="to", description="Recipient address")
    value: str = Field(..., description="Transaction value in wei")
    gas: str = Field(..., description="Gas limit")
    gas_price: str = Field(..., description="Gas price in wei")
    gas_used: Optional[str] = Field(None, description="Gas actually used")
    data: Optional[str] = Field(None, description="Transaction data")
    nonce: str = Field(..., description="Transaction nonce")
    timestamp: int = Field(..., description="Transaction timestamp")
    block_number: Optional[int] = Field(None, description="Block number")
    transaction_index: Optional[int] = Field(
        None, description="Transaction index in block"
    )
    status: TransactionStatus = Field(..., description="Transaction status")
    risk_score: Optional[float] = Field(
        None, ge=0, le=1, description="Risk assessment score"
    )
    mev_patterns: list[str] = Field(
        default_factory=list, description="Detected MEV patterns"
    )

    class Config:
        allow_population_by_field_name = True


class AlertResponse(BaseModel):
    """Alert data model"""

    id: UUID = Field(..., description="Unique alert identifier")
    rule_id: UUID = Field(..., description="ID of the rule that triggered this alert")
    transaction_hash: str = Field(..., description="Associated transaction hash")
    chain_id: int = Field(..., description="Blockchain chain ID")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    status: AlertStatus = Field(AlertStatus.PENDING, description="Alert status")
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Alert description")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional alert metadata"
    )
    created_at: datetime = Field(..., description="When the alert was created")
    updated_at: Optional[datetime] = Field(
        None, description="When the alert was last updated"
    )
    tags: list[str] = Field(default_factory=list, description="Alert tags")
    rule_name: Optional[str] = Field(None, description="Name of the triggering rule")


class RuleCondition(BaseModel):
    """Rule condition model"""

    type: str = Field(
        ..., description="Condition type (e.g., value_threshold, address_filter)"
    )
    field: Optional[str] = Field(None, description="Transaction field to evaluate")
    operator: Optional[str] = Field(
        None, description="Comparison operator (gt, lt, eq, in, etc.)"
    )
    value: Optional[Union[str, int, float, list]] = Field(
        None, description="Comparison value"
    )
    addresses: Optional[list[str]] = Field(
        None, description="List of addresses for address-based conditions"
    )
    chain_ids: Optional[list[int]] = Field(
        None, description="List of chain IDs for chain filtering"
    )

    @validator("type")
    def validate_condition_type(cls, v):
        valid_types = [
            "value_threshold",
            "gas_threshold",
            "address_whitelist",
            "address_blacklist",
            "chain_filter",
            "mev_pattern",
            "contract_interaction",
            "token_transfer",
            "time_window",
        ]
        if v not in valid_types:
            raise ValueError(f"Invalid condition type. Must be one of: {valid_types}")
        return v


class RuleAction(BaseModel):
    """Rule action model"""

    type: str = Field(
        ..., description="Action type (e.g., create_alert, webhook, email)"
    )
    severity: Optional[AlertSeverity] = Field(
        None, description="Alert severity for alert actions"
    )
    title: Optional[str] = Field(None, description="Alert title template")
    description: Optional[str] = Field(None, description="Alert description template")
    tags: Optional[list[str]] = Field(None, description="Tags to add to created alerts")
    metadata: Optional[dict[str, Any]] = Field(
        None, description="Additional action metadata"
    )
    webhook_url: Optional[str] = Field(
        None, description="Webhook URL for webhook actions"
    )
    email_recipients: Optional[list[str]] = Field(
        None, description="Email recipients for email actions"
    )

    @validator("type")
    def validate_action_type(cls, v):
        valid_types = ["create_alert", "webhook", "email", "slack", "discord"]
        if v not in valid_types:
            raise ValueError(f"Invalid action type. Must be one of: {valid_types}")
        return v


class RuleRequest(BaseModel):
    """Rule creation/update request"""

    name: str = Field(..., min_length=1, max_length=200, description="Rule name")
    description: str = Field(..., max_length=1000, description="Rule description")
    conditions: list[RuleCondition] = Field(
        ..., min_items=1, description="Rule conditions"
    )
    actions: list[RuleAction] = Field(..., min_items=1, description="Rule actions")
    enabled: bool = Field(True, description="Whether the rule is enabled")
    tags: Optional[list[str]] = Field(default_factory=list, description="Rule tags")
    priority: int = Field(5, ge=1, le=10, description="Rule priority (1-10)")


class RuleResponse(BaseModel):
    """Rule response model"""

    id: UUID = Field(..., description="Unique rule identifier")
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    conditions: list[RuleCondition] = Field(..., description="Rule conditions")
    actions: list[RuleAction] = Field(..., description="Rule actions")
    enabled: bool = Field(..., description="Whether the rule is enabled")
    tags: list[str] = Field(default_factory=list, description="Rule tags")
    priority: int = Field(..., description="Rule priority")
    created_at: datetime = Field(..., description="When the rule was created")
    updated_at: Optional[datetime] = Field(
        None, description="When the rule was last updated"
    )
    created_by: Optional[str] = Field(None, description="User who created the rule")
    updated_by: Optional[str] = Field(
        None, description="User who last updated the rule"
    )
    trigger_count: Optional[int] = Field(
        None, description="Number of times rule has triggered"
    )
    last_triggered: Optional[datetime] = Field(
        None, description="When rule last triggered"
    )


class MEVOpportunityResponse(BaseModel):
    """MEV opportunity response model"""

    id: UUID = Field(..., description="Unique opportunity identifier")
    transaction_hash: str = Field(..., description="Associated transaction hash")
    chain_id: int = Field(..., description="Blockchain chain ID")
    mev_type: str = Field(
        ..., description="Type of MEV (sandwich, arbitrage, liquidation, etc.)"
    )
    estimated_profit: str = Field(..., description="Estimated profit in wei")
    confidence_score: float = Field(
        ..., ge=0, le=1, description="Confidence in MEV detection"
    )
    block_number: int = Field(..., description="Block number")
    timestamp: datetime = Field(..., description="When opportunity was detected")
    involved_addresses: list[str] = Field(
        default_factory=list, description="Addresses involved in MEV"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional MEV metadata"
    )


class UserResponse(BaseModel):
    """User response model"""

    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username/email")
    role: str = Field(..., description="User role")
    permissions: list[str] = Field(default_factory=list, description="User permissions")
    is_active: bool = Field(..., description="Whether user account is active")
    created_at: Optional[datetime] = Field(
        None, description="When user account was created"
    )
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")


class SystemStatsResponse(BaseModel):
    """System statistics response"""

    total_transactions: int = Field(..., description="Total number of transactions")
    total_alerts: int = Field(..., description="Total number of alerts")
    active_rules: int = Field(..., description="Number of active rules")
    chains_monitored: int = Field(..., description="Number of chains being monitored")
    avg_processing_time_ms: float = Field(
        ..., description="Average processing time in milliseconds"
    )
    alerts_by_severity: dict[str, int] = Field(
        ..., description="Alert counts by severity"
    )
    top_chains_by_volume: list[dict[str, Any]] = Field(
        ..., description="Top chains by transaction volume"
    )
    uptime_percentage: float = Field(..., description="System uptime percentage")
    system_health_score: float = Field(..., description="Overall system health score")


class WebSocketMessage(BaseModel):
    """WebSocket message model"""

    type: str = Field(..., description="Message type")
    data: dict[str, Any] = Field(..., description="Message data")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Message timestamp"
    )
    client_id: Optional[str] = Field(None, description="Target client ID")


class NotificationSettings(BaseModel):
    """User notification settings"""

    email_enabled: bool = Field(True, description="Enable email notifications")
    webhook_enabled: bool = Field(False, description="Enable webhook notifications")
    slack_enabled: bool = Field(False, description="Enable Slack notifications")
    alert_severities: list[AlertSeverity] = Field(
        default_factory=lambda: [AlertSeverity.HIGH, AlertSeverity.CRITICAL],
        description="Alert severities to receive notifications for",
    )
    webhook_url: Optional[str] = Field(
        None, description="Webhook URL for notifications"
    )
    slack_webhook_url: Optional[str] = Field(None, description="Slack webhook URL")


class APIKeyRequest(BaseModel):
    """API key creation request"""

    name: str = Field(..., min_length=1, max_length=100, description="API key name")
    description: Optional[str] = Field(
        None, max_length=500, description="API key description"
    )
    permissions: list[str] = Field(..., description="API key permissions")
    expires_at: Optional[datetime] = Field(None, description="When the API key expires")


class APIKeyResponse(BaseModel):
    """API key response model"""

    id: UUID = Field(..., description="Unique API key identifier")
    name: str = Field(..., description="API key name")
    description: Optional[str] = Field(None, description="API key description")
    permissions: list[str] = Field(..., description="API key permissions")
    key_preview: str = Field(..., description="First few characters of the key")
    created_at: datetime = Field(..., description="When the API key was created")
    expires_at: Optional[datetime] = Field(None, description="When the API key expires")
    last_used: Optional[datetime] = Field(
        None, description="When the API key was last used"
    )
    is_active: bool = Field(..., description="Whether the API key is active")


class HealthCheckResponse(BaseModel):
    """Health check response model"""

    status: str = Field(..., description="Overall system status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="System version")
    uptime_seconds: int = Field(..., description="System uptime in seconds")
    checks: dict[str, Any] = Field(
        ..., description="Individual component health checks"
    )


class ErrorResponse(BaseModel):
    """Standard error response model"""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Error timestamp"
    )
    request_id: Optional[str] = Field(
        None, description="Request identifier for tracking"
    )


# Request/Response models for common operations
class BulkOperationRequest(BaseModel):
    """Bulk operation request"""

    ids: list[UUID] = Field(
        ..., min_items=1, max_items=100, description="List of IDs to operate on"
    )
    action: str = Field(..., description="Action to perform")
    parameters: Optional[dict[str, Any]] = Field(None, description="Action parameters")


class BulkOperationResponse(BaseModel):
    """Bulk operation response"""

    total_requested: int = Field(..., description="Total number of items requested")
    successful: int = Field(..., description="Number of successful operations")
    failed: int = Field(..., description="Number of failed operations")
    errors: list[dict[str, Any]] = Field(
        default_factory=list, description="List of errors encountered"
    )
    results: list[dict[str, Any]] = Field(
        default_factory=list, description="Operation results"
    )


class SearchRequest(BaseModel):
    """Search request model"""

    query: str = Field(..., min_length=1, description="Search query")
    filters: Optional[dict[str, Any]] = Field(None, description="Search filters")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: str = Field("desc", description="Sort order (asc/desc)")

    @validator("sort_order")
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError('Sort order must be "asc" or "desc"')
        return v


class SearchResponse(BaseModel):
    """Search response model"""

    query: str = Field(..., description="Original search query")
    total_results: int = Field(..., description="Total number of matching results")
    results: list[dict[str, Any]] = Field(..., description="Search results")
    facets: Optional[dict[str, Any]] = Field(
        None, description="Search facets/aggregations"
    )
    took_ms: int = Field(..., description="Time taken for search in milliseconds")
