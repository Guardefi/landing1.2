"""
Scheduler System Data Models
Defines SQLAlchemy models for job scheduling, execution history, and resource monitoring
"""

from datetime import UTC, datetime
from enum import Enum as PyEnum
from typing import Any

from core.db import Base
from pydantic import BaseModel, Field
from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum

# ─── Enums ──────────────────────────────────────────────────────────────────


class JobType(PyEnum):
    """Types of jobs that can be scheduled"""

    SCAN = "scan"
    MONITOR = "monitor"
    REPORT = "report"
    BACKUP = "backup"
    ANALYSIS = "analysis"
    MAINTENANCE = "maintenance"


class JobStatus(PyEnum):
    """Status of scheduled jobs"""

    ACTIVE = "active"
    PAUSED = "paused"
    FAILED = "failed"
    DISABLED = "disabled"
    MAINTENANCE = "maintenance"


class JobPriority(PyEnum):
    """Priority levels for job execution"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ExecutionStatus(PyEnum):
    """Status of individual job executions"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ClusterStatus(PyEnum):
    """Status of compute clusters"""

    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


# ─── Database Models ────────────────────────────────────────────────────────


class ScheduledJob(Base):
    """Scheduled job configuration and metadata"""

    __tablename__ = "scheduled_jobs"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    job_type = Column(Enum(JobType), nullable=False)
    category = Column(String, nullable=False)

    # Scheduling
    schedule = Column(String, nullable=False)  # Cron expression
    priority = Column(Enum(JobPriority), default=JobPriority.NORMAL)
    status = Column(Enum(JobStatus), default=JobStatus.ACTIVE)

    # Resource allocation
    resource = Column(String, nullable=False)  # Target cluster/resource
    estimated_cost = Column(Float, default=0.0)
    timeout_minutes = Column(Integer, default=60)

    # Execution tracking
    targets = Column(Integer, default=0)  # Number of items to process
    success_rate = Column(Float, default=0.0)  # Historical success rate
    average_duration = Column(Float, default=0.0)  # Average runtime in seconds

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    next_run = Column(DateTime)
    last_run = Column(DateTime)

    # Configuration
    config = Column(JSON)  # Job-specific configuration
    environment_vars = Column(JSON)  # Environment variables

    # Relationships
    executions = relationship("JobExecution", back_populates="job")


class JobExecution(Base):
    """Individual job execution records"""

    __tablename__ = "job_executions"

    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey("scheduled_jobs.id"), nullable=False)

    # Execution details
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_seconds = Column(Float)

    # Results
    items_processed = Column(Integer, default=0)
    items_failed = Column(Integer, default=0)
    errors = Column(JSON)  # List of error messages
    output = Column(Text)  # Execution output/logs

    # Resource usage
    cpu_usage = Column(Float)  # Average CPU usage %
    memory_usage = Column(Float)  # Peak memory usage GB
    disk_io = Column(Float)  # Disk I/O MB
    network_io = Column(Float)  # Network I/O MB

    # Cost tracking
    actual_cost = Column(Float, default=0.0)
    efficiency = Column(Float, default=0.0)  # Performance score 0-100

    # Metadata
    cluster_node = Column(String)
    environment = Column(String)
    version = Column(String)

    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    job = relationship("ScheduledJob", back_populates="executions")


class SystemMetrics(Base):
    """Real-time system metrics and monitoring data"""

    __tablename__ = "system_metrics"

    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))

    # Overall system metrics
    active_jobs = Column(Integer, default=0)
    queue_depth = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    avg_runtime = Column(Float, default=0.0)

    # Resource utilization
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    disk_io = Column(Float, default=0.0)
    network_io = Column(Float, default=0.0)

    # Cost metrics
    hourly_cost = Column(Float, default=0.0)
    daily_cost = Column(Float, default=0.0)
    monthly_cost = Column(Float, default=0.0)


class ComputeCluster(Base):
    """Compute cluster configuration and status"""

    __tablename__ = "compute_clusters"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    region = Column(String, nullable=False)

    # Configuration
    node_count = Column(Integer, default=1)
    node_type = Column(String)
    cpu_cores = Column(Integer)
    memory_gb = Column(Integer)
    storage_gb = Column(Integer)

    # Status
    status = Column(Enum(ClusterStatus), default=ClusterStatus.ONLINE)
    utilization = Column(Float, default=0.0)  # 0-100%
    active_jobs = Column(Integer, default=0)
    uptime = Column(Float, default=99.0)  # Uptime percentage

    # Cost
    cost_per_hour = Column(Float, default=0.0)

    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class ResourceUsage(Base):
    """Resource usage monitoring"""

    __tablename__ = "resource_usage"

    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))
    cluster_id = Column(String, ForeignKey("compute_clusters.id"))

    # Resource metrics
    resource_type = Column(String, nullable=False)  # CPU, Memory, Disk, Network
    current_usage = Column(Float, default=0.0)
    average_usage = Column(Float, default=0.0)
    peak_usage = Column(Float, default=0.0)
    unit = Column(String, default="")  # %, GB, MB/s, etc.

    # Capacity information
    total_capacity = Column(Float)
    available_capacity = Column(Float)

    # Trends
    trend = Column(String, default="stable")  # up, down, stable

    # Relationships
    cluster = relationship("ComputeCluster")


# ─── Pydantic Models ────────────────────────────────────────────────────────


class JobCreate(BaseModel):
    """Model for creating new scheduled jobs"""

    name: str = Field(..., description="Job name")
    description: str | None = Field(None, description="Job description")
    job_type: JobType = Field(..., description="Type of job")
    category: str = Field(..., description="Job category")
    schedule: str = Field(..., description="Cron expression for scheduling")
    priority: JobPriority = Field(JobPriority.NORMAL, description="Job priority")
    resource: str = Field(..., description="Target cluster or resource")
    estimated_cost: float = Field(0.0, description="Estimated cost per execution")
    timeout_minutes: int = Field(60, description="Execution timeout in minutes")
    targets: int = Field(0, description="Number of items to process")
    config: dict[str, Any] | None = Field(None, description="Job configuration")
    environment_vars: dict[str, str] | None = Field(
        None, description="Environment variables"
    )


class JobUpdate(BaseModel):
    """Model for updating scheduled jobs"""

    name: str | None = None
    description: str | None = None
    schedule: str | None = None
    priority: JobPriority | None = None
    status: JobStatus | None = None
    resource: str | None = None
    estimated_cost: float | None = None
    timeout_minutes: int | None = None
    targets: int | None = None
    config: dict[str, Any] | None = None
    environment_vars: dict[str, str] | None = None


class JobResponse(BaseModel):
    """Response model for scheduled job data"""

    id: str
    name: str
    description: str | None
    job_type: JobType
    category: str
    schedule: str
    priority: JobPriority
    status: JobStatus
    resource: str
    estimated_cost: float
    timeout_minutes: int
    targets: int
    success_rate: float
    average_duration: float
    created_at: datetime
    updated_at: datetime
    next_run: datetime | None
    last_run: datetime | None
    config: dict[str, Any] | None
    environment_vars: dict[str, str] | None

    class Config:
        from_attributes = True


class ExecutionResponse(BaseModel):
    """Response model for job execution data"""

    id: str
    job_id: str
    status: ExecutionStatus
    start_time: datetime | None
    end_time: datetime | None
    duration_seconds: float | None
    items_processed: int
    items_failed: int
    errors: list[str] | None
    cpu_usage: float | None
    memory_usage: float | None
    disk_io: float | None
    network_io: float | None
    actual_cost: float
    efficiency: float
    cluster_node: str | None
    environment: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class SystemMetricsResponse(BaseModel):
    """Response model for system metrics"""

    active_jobs: int
    queue_depth: int
    success_rate: float
    avg_runtime: float
    cpu_usage: float
    memory_usage: float
    disk_io: float
    network_io: float
    hourly_cost: float
    daily_cost: float
    monthly_cost: float
    timestamp: datetime

    class Config:
        from_attributes = True


class ClusterResponse(BaseModel):
    """Response model for compute cluster data"""

    id: str
    name: str
    region: str
    node_count: int
    node_type: str | None
    cpu_cores: int | None
    memory_gb: int | None
    storage_gb: int | None
    status: ClusterStatus
    utilization: float
    active_jobs: int
    uptime: float
    cost_per_hour: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResourceUsageResponse(BaseModel):
    """Response model for resource usage data"""

    resource_type: str
    current_usage: float
    average_usage: float
    peak_usage: float
    unit: str
    total_capacity: float | None
    available_capacity: float | None
    trend: str
    timestamp: datetime

    class Config:
        from_attributes = True


class SchedulerHealthResponse(BaseModel):
    """Health check response for scheduler system"""

    service: str = "CyberDefender Scheduler"
    status: str = "operational"
    version: str = "1.0.0"
    uptime: float
    active_jobs: int
    clusters_online: int
    total_executions_today: int
    timestamp: datetime
