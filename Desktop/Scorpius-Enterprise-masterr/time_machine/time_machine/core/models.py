"""
Time Machine Core Models and Data Structures
"""

import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional, Union


class VMBackend(str, Enum):
    """Virtual Machine backends for replay execution."""

    ANVIL = "anvil"
    HARDHAT = "hardhat"
    GETH = "geth"


class FrameType(str, Enum):
    """Types of execution frames in timeline events."""

    OPCODE = "opcode"
    CALL = "call"
    REVERT = "revert"
    LOG = "log"
    STORAGE_WRITE = "storage_write"
    BALANCE_CHANGE = "balance_change"
    CODE_CHANGE = "code_change"


class JobStatus(str, Enum):
    """Replay job status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SessionType(str, Enum):
    """Forensic session types."""

    EXPLOIT_ANALYSIS = "exploit_analysis"
    MEV_INVESTIGATION = "mev_investigation"
    COMPLIANCE_AUDIT = "compliance_audit"
    VULNERABILITY_RESEARCH = "vulnerability_research"
    TRANSACTION_TRACE = "transaction_trace"


class PatchType(str, Enum):
    """State patch types."""

    STORAGE = "storage"
    BALANCE = "balance"
    CODE = "code"
    NONCE = "nonce"
    HEADER = "header"


@dataclass
class ReplayJob:
    """Replay job configuration and metadata."""

    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    block_number: Optional[int] = None
    tx_hash: Optional[str] = None
    from_block: Optional[int] = None
    to_block: Optional[int] = None
    vm_backend: VMBackend = VMBackend.ANVIL
    patches: List[Dict[str, Any]] = field(default_factory=list)
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "job_id": self.job_id,
            "name": self.name,
            "description": self.description,
            "block_number": self.block_number,
            "tx_hash": self.tx_hash,
            "from_block": self.from_block,
            "to_block": self.to_block,
            "vm_backend": self.vm_backend.value,
            "patches": self.patches,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


@dataclass
class TimelineEvent:
    """Individual execution event in the blockchain timeline."""

    frame_id: str
    frame_type: FrameType
    block_number: int
    tx_index: int
    gas_used: Optional[int] = None
    gas_limit: Optional[int] = None
    opcode: Optional[str] = None
    pc: Optional[int] = None  # Program counter
    depth: int = 0
    address: Optional[str] = None
    caller: Optional[str] = None
    value: Optional[str] = None
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    stack: List[str] = field(default_factory=list)
    memory: Dict[str, str] = field(default_factory=dict)
    storage: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "frame_id": self.frame_id,
            "frame_type": self.frame_type.value,
            "block_number": self.block_number,
            "tx_index": self.tx_index,
            "gas_used": self.gas_used,
            "gas_limit": self.gas_limit,
            "opcode": self.opcode,
            "pc": self.pc,
            "depth": self.depth,
            "address": self.address,
            "caller": self.caller,
            "value": self.value,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "stack": self.stack,
            "memory": self.memory,
            "storage": self.storage,
            "logs": self.logs,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class Branch:
    """Execution branch with state snapshots and patches."""

    branch_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    parent_branch_id: Optional[str] = None
    snapshot_id: str = ""
    block_number: int = 0
    tx_index: int = 0
    patches_applied: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "branch_id": self.branch_id,
            "name": self.name,
            "description": self.description,
            "parent_branch_id": self.parent_branch_id,
            "snapshot_id": self.snapshot_id,
            "block_number": self.block_number,
            "tx_index": self.tx_index,
            "patches_applied": self.patches_applied,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
            "tags": self.tags,
        }


@dataclass
class Patch:
    """State patch definition."""

    patch_type: PatchType
    target_address: str
    patch_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    key: Optional[str] = None  # storage slot for storage patches
    value: str = ""
    description: str = ""
    validation_rules: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "patch_id": self.patch_id,
            "patch_type": self.patch_type.value,
            "target_address": self.target_address,
            "key": self.key,
            "value": self.value,
            "description": self.description,
            "validation_rules": self.validation_rules,
            "metadata": self.metadata,
        }


@dataclass
class Diff:
    """Difference between two execution states."""

    from_branch: str
    to_branch: str
    diff_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    storage_changes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    balance_changes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    code_changes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    nonce_changes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    log_changes: List[Dict[str, Any]] = field(default_factory=list)
    gas_changes: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "diff_id": self.diff_id,
            "from_branch": self.from_branch,
            "to_branch": self.to_branch,
            "storage_changes": self.storage_changes,
            "balance_changes": self.balance_changes,
            "code_changes": self.code_changes,
            "nonce_changes": self.nonce_changes,
            "log_changes": self.log_changes,
            "gas_changes": self.gas_changes,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class ForensicSession:
    """Forensic analysis session with bookmarks and findings."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    session_type: SessionType = SessionType.EXPLOIT_ANALYSIS
    description: str = ""
    target_contracts: List[str] = field(default_factory=list)
    target_transactions: List[str] = field(default_factory=list)
    bookmarks: List[Dict[str, Any]] = field(default_factory=list)
    findings: List[Dict[str, Any]] = field(default_factory=list)
    timeline_annotations: List[Dict[str, Any]] = field(default_factory=list)
    compliance_checks: List[Dict[str, Any]] = field(default_factory=list)
    mev_analysis: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    analyst: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_bookmark(
        self,
        name: str,
        block_number: int,
        tx_index: int,
        description: str = "",
        tags: List[str] = None,
    ):
        """Add a bookmark to the session."""
        bookmark = {
            "id": str(uuid.uuid4()),
            "name": name,
            "block_number": block_number,
            "tx_index": tx_index,
            "description": description,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
        }
        self.bookmarks.append(bookmark)
        self.last_updated = datetime.now()

    def add_finding(
        self,
        title: str,
        severity: str,
        description: str,
        evidence: List[str] = None,
        recommendations: List[str] = None,
    ):
        """Add a finding to the session."""
        finding = {
            "id": str(uuid.uuid4()),
            "title": title,
            "severity": severity,
            "description": description,
            "evidence": evidence or [],
            "recommendations": recommendations or [],
            "created_at": datetime.now().isoformat(),
        }
        self.findings.append(finding)
        self.last_updated = datetime.now()


@dataclass
class StateManipulation:
    """State manipulation operation for testing scenarios."""

    manipulation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    target_addresses: List[str] = field(default_factory=list)
    operations: List[Dict[str, Any]] = field(default_factory=list)
    pre_conditions: List[str] = field(default_factory=list)
    post_conditions: List[str] = field(default_factory=list)
    rollback_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class AnalysisPlugin(ABC):
    """Abstract base class for analysis plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description."""
        pass

    @abstractmethod
    async def analyze(
        self, events: List[TimelineEvent], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze timeline events and return results."""
        pass

    @abstractmethod
    async def supports_session_type(self, session_type: SessionType) -> bool:
        """Check if plugin supports the given session type."""
        pass


# Utility functions for working with models


def serialize_to_json(obj: Any) -> str:
    """Serialize dataclass objects to JSON."""
    if hasattr(obj, "to_dict"):
        return json.dumps(obj.to_dict(), indent=2)
    return json.dumps(obj, default=str, indent=2)


def create_forensic_session(
    name: str, session_type: SessionType, analyst: str = "", description: str = ""
) -> ForensicSession:
    """Create a new forensic session."""
    return ForensicSession(
        name=name,
        session_type=session_type,
        description=description,
        analyst=analyst,
    )


def create_exploit_patch(
    contract_address: str, slot: str, value: str, description: str = ""
) -> Patch:
    """Create a storage patch for exploit testing."""
    return Patch(
        patch_type=PatchType.STORAGE,
        target_address=contract_address,
        key=slot,
        value=value,
        description=description or f"Patch storage slot {slot} in {contract_address}",
    )


def create_balance_patch(address: str, balance: str, description: str = "") -> Patch:
    """Create a balance patch."""
    return Patch(
        patch_type=PatchType.BALANCE,
        target_address=address,
        value=balance,
        description=description or f"Set balance for {address}",
    )


def create_bookmark(
    name: str,
    block_number: int,
    tx_index: int = 0,
    description: str = "",
    tags: List[str] = None,
) -> Dict[str, Any]:
    """Create a timeline bookmark."""
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "block_number": block_number,
        "tx_index": tx_index,
        "description": description,
        "tags": tags or [],
        "created_at": datetime.now().isoformat(),
    }
