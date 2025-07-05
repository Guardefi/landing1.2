"""
Time Machine Database Models for Exploit Replay System
Defines all database models for blockchain exploit replay functionality.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    DECIMAL,
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class SessionStatus(str, Enum):
    """Replay session status enumeration"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class VMBackend(str, Enum):
    """Virtual Machine backend types"""

    ANVIL = "anvil"
    HARDHAT = "hardhat"
    GETH = "geth"
    ERIGON = "erigon"
    BESU = "besu"


class FrameType(str, Enum):
    """Timeline frame types for forensic analysis"""

    OPCODE = "opcode"
    CALL = "call"
    DELEGATECALL = "delegatecall"
    STATICCALL = "staticcall"
    CREATE = "create"
    CREATE2 = "create2"
    REVERT = "revert"
    LOG = "log"
    STORAGE_WRITE = "storage_write"
    STORAGE_READ = "storage_read"
    BALANCE_CHANGE = "balance_change"
    TRANSFER = "transfer"
    SUICIDE = "suicide"


class AnalysisType(str, Enum):
    """Analysis plugin types"""

    VULNERABILITY_SCAN = "vulnerability_scan"
    EXPLOIT_DETECTION = "exploit_detection"
    PATTERN_MATCHING = "pattern_matching"
    FINANCIAL_IMPACT = "financial_impact"
    MEV_ANALYSIS = "mev_analysis"
    COMPLIANCE_CHECK = "compliance_check"
    INVARIANT_VIOLATION = "invariant_violation"


class TimestampMixin:
    """Mixin for adding timestamp fields to models"""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Exploit(Base, TimestampMixin):
    """Historical exploits database model"""

    __tablename__ = "exploits"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    chain = Column(String(50), nullable=False, index=True)
    block_number = Column(Integer, nullable=False, index=True)
    transaction_hashes = Column(JSON, nullable=False)  # List of transaction hashes
    vulnerability_type = Column(String(100), nullable=False, index=True)
    severity = Column(String(20), nullable=False)  # critical, high, medium, low
    description = Column(Text)
    affected_contracts = Column(JSON)  # List of contract addresses
    attack_vector = Column(Text)
    financial_impact = Column(DECIMAL(30, 18))  # Loss amount in native token
    financial_impact_usd = Column(DECIMAL(20, 2))  # Loss amount in USD
    tags = Column(JSON)  # List of searchable tags
    exploit_metadata = Column(JSON)  # Additional exploit-specific data

    # MEV and advanced analysis
    mev_type = Column(String(50))  # sandwich, arbitrage, liquidation, etc.
    gas_optimization_score = Column(DECIMAL(5, 2))
    complexity_score = Column(Integer)  # 1-10 complexity rating

    # Attribution and tracking
    attacker_addresses = Column(JSON)  # Known attacker addresses
    victim_addresses = Column(JSON)  # Victim addresses
    related_exploits = Column(JSON)  # Related exploit IDs

    # Compliance and reporting
    reported_to_authorities = Column(Boolean, default=False)
    disclosure_status = Column(String(50))  # undisclosed, partial, full
    cve_id = Column(String(20))  # CVE identifier if applicable

    # Relationships
    replay_sessions = relationship(
        "ReplaySession", back_populates="exploit", cascade="all, delete-orphan"
    )
    forensic_reports = relationship(
        "ForensicReport", back_populates="exploit", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_exploit_chain_block", "chain", "block_number"),
        Index("idx_exploit_severity_type", "severity", "vulnerability_type"),
    )


class ReplaySession(Base, TimestampMixin):
    """Enhanced replay sessions for tracking exploit replays"""

    __tablename__ = "replay_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exploit_id = Column(String(36), ForeignKey("exploits.id"), nullable=True)
    session_type = Column(
        String(50), nullable=False
    )  # exploit, transaction, custom, batch, forensic
    fork_block = Column(Integer, nullable=False)
    chain = Column(String(50), nullable=False)
    vm_backend = Column(String(20), default=VMBackend.ANVIL)
    status = Column(String(50), default=SessionStatus.PENDING)

    # Configuration and parameters
    parameters = Column(JSON)  # Session configuration parameters
    vm_config = Column(JSON)  # VM-specific configuration
    debug_config = Column(JSON)  # Debug and tracing configuration

    # Results and analysis
    results = Column(JSON)  # Replay results and analysis
    timeline_events = Column(JSON)  # Compressed timeline events
    state_diffs = Column(JSON)  # State differences
    error_message = Column(Text)

    # Performance metrics
    execution_time = Column(Integer)  # Execution time in milliseconds
    memory_usage = Column(Integer)  # Peak memory usage in MB
    cpu_usage = Column(DECIMAL(5, 2))  # CPU usage percentage
    blocks_processed = Column(Integer)
    transactions_processed = Column(Integer)

    # User and organizational tracking
    user_id = Column(String(255), nullable=True)
    organization_id = Column(String(255), nullable=True)
    project_id = Column(String(255), nullable=True)

    # Branching and forking
    parent_session_id = Column(String(36), ForeignKey("replay_sessions.id"))
    branch_id = Column(String(36))
    snapshot_id = Column(String(255))

    # Bookmarks and annotations
    bookmarks = Column(JSON)  # User-defined bookmarks
    annotations = Column(JSON)  # User annotations and notes

    # Export and sharing
    export_bundle_id = Column(String(36))
    is_public = Column(Boolean, default=False)
    access_permissions = Column(JSON)

    # Relationships
    exploit = relationship("Exploit", back_populates="replay_sessions")
    transaction_traces = relationship(
        "TransactionTrace", back_populates="session", cascade="all, delete-orphan"
    )
    child_sessions = relationship(
        "ReplaySession", backref="parent_session", remote_side=[id]
    )
    analysis_results = relationship(
        "AnalysisResult", back_populates="session", cascade="all, delete-orphan"
    )
    timeline_frames = relationship(
        "TimelineFrame", back_populates="session", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_session_status_created", "status", "created_at"),
        Index("idx_session_user_project", "user_id", "project_id"),
        Index("idx_session_chain_block", "chain", "fork_block"),
    )


class Transaction(Base, TimestampMixin):
    """Enhanced blockchain transactions model"""

    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hash = Column(String(66), nullable=False, unique=True, index=True)
    block_number = Column(Integer, nullable=False, index=True)
    block_hash = Column(String(66), nullable=False)
    transaction_index = Column(Integer, nullable=False)

    # Basic transaction fields
    from_address = Column(String(42), nullable=False, index=True)
    to_address = Column(String(42), index=True)
    value = Column(DECIMAL(30, 18), nullable=False)
    gas_limit = Column(Integer, nullable=False)
    gas_used = Column(Integer)
    gas_price = Column(DECIMAL(30, 18))
    max_fee_per_gas = Column(DECIMAL(30, 18))  # EIP-1559
    max_priority_fee_per_gas = Column(DECIMAL(30, 18))  # EIP-1559
    nonce = Column(Integer, nullable=False)
    input_data = Column(Text)
    status = Column(Boolean)
    chain = Column(String(50), nullable=False, index=True)

    # Enhanced transaction data
    transaction_type = Column(Integer)  # 0=legacy, 1=EIP-2930, 2=EIP-1559
    access_list = Column(JSON)  # EIP-2930 access list
    raw_transaction = Column(JSON)  # Complete transaction object

    # MEV and analysis data
    mev_type = Column(String(50))  # Type of MEV if detected
    is_mev = Column(Boolean, default=False)
    arbitrage_profit = Column(DECIMAL(30, 18))
    sandwich_attack = Column(Boolean, default=False)

    # Function call analysis
    function_selector = Column(String(10))  # First 4 bytes of input data
    function_name = Column(String(255))
    decoded_params = Column(JSON)

    # Risk and security metrics
    risk_score = Column(Integer)  # 0-100 risk assessment
    suspicious_patterns = Column(JSON)  # List of detected suspicious patterns

    # Performance metrics
    execution_time_ms = Column(Integer)
    storage_writes = Column(Integer)
    storage_reads = Column(Integer)
    internal_calls = Column(Integer)

    # Relationships
    transaction_traces = relationship(
        "TransactionTrace", back_populates="transaction", cascade="all, delete-orphan"
    )
    storage_changes = relationship(
        "StorageChange", back_populates="transaction", cascade="all, delete-orphan"
    )
    event_logs = relationship(
        "EventLog", back_populates="transaction", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_tx_from_to", "from_address", "to_address"),
        Index("idx_tx_block_index", "block_number", "transaction_index"),
        Index("idx_tx_function_selector", "function_selector"),
    )


class TimelineFrame(Base, TimestampMixin):
    """Individual timeline frames for detailed forensic analysis"""

    __tablename__ = "timeline_frames"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(
        String(36), ForeignKey("replay_sessions.id"), nullable=False, index=True
    )
    frame_sequence = Column(Integer, nullable=False)  # Order in timeline
    frame_type = Column(String(30), nullable=False)

    # Execution context
    block_number = Column(Integer, nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    transaction_index = Column(Integer, nullable=False)
    call_depth = Column(Integer, default=0)

    # EVM execution state
    pc = Column(Integer)  # Program counter
    opcode = Column(String(20))
    opcode_cost = Column(Integer)
    gas_remaining = Column(Integer)
    gas_used = Column(Integer)

    # Stack, Memory, Storage
    stack_data = Column(JSON)  # Stack state
    memory_data = Column(JSON)  # Memory state (compressed)
    storage_changes = Column(JSON)  # Storage modifications

    # Call context
    caller_address = Column(String(42))
    callee_address = Column(String(42))
    call_value = Column(DECIMAL(30, 18))
    call_data = Column(Text)
    return_data = Column(Text)

    # Events and logs
    events_emitted = Column(JSON)  # Events emitted in this frame

    # Error handling
    error_type = Column(String(50))
    error_message = Column(Text)
    revert_reason = Column(Text)

    # Bookmarks and annotations
    is_bookmark = Column(Boolean, default=False)
    bookmark_name = Column(String(255))
    user_annotations = Column(JSON)

    # Analysis flags
    is_suspicious = Column(Boolean, default=False)
    vulnerability_flags = Column(JSON)
    mev_opportunity = Column(Boolean, default=False)

    # Relationships
    session = relationship("ReplaySession", back_populates="timeline_frames")

    __table_args__ = (
        Index("idx_frame_session_sequence", "session_id", "frame_sequence"),
        Index("idx_frame_tx_depth", "transaction_hash", "call_depth"),
        Index("idx_frame_opcode_bookmark", "opcode", "is_bookmark"),
    )


class StorageChange(Base, TimestampMixin):
    """Storage slot changes for differential analysis"""

    __tablename__ = "storage_changes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_hash = Column(
        String(66), ForeignKey("transactions.hash"), nullable=False, index=True
    )
    contract_address = Column(String(42), nullable=False, index=True)
    storage_slot = Column(String(66), nullable=False)

    # Storage change data
    old_value = Column(String(66))
    new_value = Column(String(66))
    change_type = Column(String(20))  # set, delete, create

    # Context information
    opcode = Column(String(20))  # SSTORE, SLOAD, etc.
    gas_cost = Column(Integer)
    call_depth = Column(Integer)

    # Semantic analysis
    slot_name = Column(String(255))  # Decoded slot name if known
    slot_type = Column(String(100))  # mapping, array, struct, etc.
    decoded_old_value = Column(Text)  # Human-readable old value
    decoded_new_value = Column(Text)  # Human-readable new value

    # Security implications
    is_critical = Column(Boolean, default=False)
    security_impact = Column(String(50))  # none, low, medium, high, critical
    invariant_violation = Column(Boolean, default=False)

    # Relationships
    transaction = relationship("Transaction", back_populates="storage_changes")

    __table_args__ = (
        Index("idx_storage_contract_slot", "contract_address", "storage_slot"),
        Index("idx_storage_critical", "is_critical", "security_impact"),
    )


class EventLog(Base, TimestampMixin):
    """Event logs for comprehensive event analysis"""

    __tablename__ = "event_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_hash = Column(
        String(66), ForeignKey("transactions.hash"), nullable=False, index=True
    )
    log_index = Column(Integer, nullable=False)

    # Event data
    contract_address = Column(String(42), nullable=False, index=True)
    topics = Column(JSON, nullable=False)  # Array of topics
    data = Column(Text)  # Event data

    # Decoded event information
    event_signature = Column(String(255))
    event_name = Column(String(255))
    decoded_params = Column(JSON)  # Decoded event parameters

    # Analysis metadata
    is_suspicious = Column(Boolean, default=False)
    anomaly_score = Column(DECIMAL(5, 2))  # 0-100 anomaly score
    pattern_matches = Column(JSON)  # Matched suspicious patterns

    # Relationships
    transaction = relationship("Transaction", back_populates="event_logs")

    __table_args__ = (
        Index("idx_event_contract_signature", "contract_address", "event_signature"),
        Index("idx_event_suspicious", "is_suspicious", "anomaly_score"),
    )


class ForensicReport(Base, TimestampMixin):
    """Comprehensive forensic analysis reports"""

    __tablename__ = "forensic_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exploit_id = Column(String(36), ForeignKey("exploits.id"), nullable=False)
    session_id = Column(String(36), ForeignKey("replay_sessions.id"), nullable=True)

    # Report metadata
    report_type = Column(
        String(50), nullable=False
    )  # incident, vulnerability, compliance
    title = Column(String(255), nullable=False)
    executive_summary = Column(Text)

    # Technical analysis
    technical_details = Column(JSON)  # Detailed technical findings
    attack_timeline = Column(JSON)  # Chronological attack sequence
    root_cause_analysis = Column(JSON)  # Root cause identification
    impact_assessment = Column(JSON)  # Financial and operational impact

    # Evidence and artifacts
    evidence_hashes = Column(JSON)  # Hash of evidence files
    transaction_traces = Column(JSON)  # Key transaction traces
    code_snippets = Column(JSON)  # Relevant code sections
    screenshots = Column(JSON)  # UI screenshots if applicable

    # Recommendations
    immediate_actions = Column(JSON)  # Immediate mitigation steps
    long_term_fixes = Column(JSON)  # Long-term security improvements
    prevention_measures = Column(JSON)  # Future prevention strategies

    # Compliance and legal
    regulatory_implications = Column(JSON)  # Regulatory considerations
    legal_actions = Column(JSON)  # Legal actions taken/recommended
    disclosure_timeline = Column(JSON)  # Disclosure schedule

    # Review and approval
    analyst_id = Column(String(255))
    reviewer_id = Column(String(255))
    approved_by = Column(String(255))
    approval_date = Column(DateTime)
    report_status = Column(
        String(20), default="draft"
    )  # draft, review, approved, published

    # Distribution
    confidentiality_level = Column(
        String(20), default="internal"
    )  # public, internal, confidential, restricted
    distribution_list = Column(JSON)  # Who has access to this report

    # Relationships
    exploit = relationship("Exploit", back_populates="forensic_reports")
    session = relationship("ReplaySession")

    __table_args__ = (
        Index("idx_report_status_type", "report_status", "report_type"),
        Index("idx_report_analyst_date", "analyst_id", "created_at"),
    )


class AnalysisResult(Base, TimestampMixin):
    """Enhanced analysis results from exploit replays and plugins"""

    __tablename__ = "analysis_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("replay_sessions.id"), nullable=False)
    analysis_type = Column(String(100), nullable=False)
    plugin_name = Column(String(100))  # Analysis plugin that generated this result
    plugin_version = Column(String(20))

    # Analysis metadata
    severity = Column(String(20), nullable=False)
    confidence_score = Column(DECIMAL(5, 2))  # 0-100 confidence score
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # Technical details
    affected_contracts = Column(JSON)  # Contract addresses affected
    affected_functions = Column(JSON)  # Function signatures affected
    code_patterns = Column(JSON)  # Identified code patterns
    vulnerability_class = Column(String(100))  # CWE classification

    # Recommendations and mitigation
    recommendations = Column(JSON)  # Mitigation recommendations
    patches = Column(JSON)  # Suggested code patches
    gas_optimization = Column(JSON)  # Gas optimization suggestions

    # Evidence and proof
    proof_of_concept = Column(JSON)  # PoC exploit code
    test_cases = Column(JSON)  # Test cases demonstrating the issue
    related_transactions = Column(JSON)  # Related transaction hashes

    # Impact assessment
    financial_impact = Column(DECIMAL(30, 18))
    risk_rating = Column(String(20))  # low, medium, high, critical
    exploitability_score = Column(Integer)  # 1-10 exploitability rating

    # Compliance and standards
    cwe_ids = Column(JSON)  # Common Weakness Enumeration IDs
    owasp_categories = Column(JSON)  # OWASP categories
    compliance_violations = Column(JSON)  # Regulatory compliance violations

    # Resolution tracking
    status = Column(
        String(20), default="open"
    )  # open, in_progress, resolved, false_positive
    assigned_to = Column(String(255))
    resolution_notes = Column(Text)
    resolved_at = Column(DateTime)

    # Relationships
    session = relationship("ReplaySession", back_populates="analysis_results")

    __table_args__ = (
        Index("idx_analysis_severity_confidence", "severity", "confidence_score"),
        Index("idx_analysis_type_status", "analysis_type", "status"),
        Index("idx_analysis_plugin", "plugin_name", "plugin_version"),
    )


class StateSnapshot(Base, TimestampMixin):
    """Enhanced blockchain state snapshots"""

    __tablename__ = "state_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    snapshot_id = Column(String(255), nullable=False, unique=True, index=True)
    session_id = Column(String(36), ForeignKey("replay_sessions.id"), nullable=True)

    # Block context
    block_number = Column(Integer, nullable=False, index=True)
    block_hash = Column(String(66), nullable=False)
    block_timestamp = Column(Integer, nullable=False)
    chain = Column(String(50), nullable=False)

    # Snapshot content
    addresses = Column(JSON)  # Addresses included in snapshot
    state_data = Column(JSON)  # Compressed state data
    storage_location = Column(String(500))  # External storage location
    compression_type = Column(String(20), default="gzip")

    # Metadata and checksums
    snapshot_size = Column(Integer)  # Size in bytes
    checksum = Column(String(64))  # SHA-256 checksum
    state_root = Column(String(66))  # Merkle state root

    # Snapshot hierarchy
    parent_snapshot_id = Column(String(255))
    is_differential = Column(Boolean, default=False)
    diff_data = Column(JSON)  # Differential data if applicable

    # Usage tracking
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime)

    # Retention and cleanup
    retention_policy = Column(String(50))  # temporary, archive, permanent
    expires_at = Column(DateTime)
    is_archived = Column(Boolean, default=False)

    __table_args__ = (
        Index("idx_snapshot_block_chain", "block_number", "chain"),
        Index("idx_snapshot_retention", "retention_policy", "expires_at"),
    )


class ContractAnalysis(Base, TimestampMixin):
    """Contract-specific analysis and metadata"""

    __tablename__ = "contract_analysis"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_address = Column(String(42), nullable=False, unique=True, index=True)
    chain = Column(String(50), nullable=False)

    # Contract metadata
    contract_name = Column(String(255))
    compiler_version = Column(String(50))
    optimization_enabled = Column(Boolean)
    creation_transaction = Column(String(66))
    creation_block = Column(Integer)
    creator_address = Column(String(42))

    # Code analysis
    source_code = Column(Text)
    bytecode = Column(Text)
    abi = Column(JSON)
    function_signatures = Column(JSON)

    # Security analysis
    vulnerability_scan_results = Column(JSON)
    security_score = Column(Integer)  # 0-100 security rating
    last_audit_date = Column(DateTime)
    audit_reports = Column(JSON)

    # Pattern recognition
    design_patterns = Column(JSON)  # Detected design patterns
    anti_patterns = Column(JSON)  # Detected anti-patterns
    code_complexity = Column(Integer)  # Cyclomatic complexity

    # Usage statistics
    total_transactions = Column(Integer, default=0)
    unique_callers = Column(Integer, default=0)
    total_value_handled = Column(DECIMAL(30, 18), default=0)

    # Classification
    contract_type = Column(String(50))  # token, defi, nft, dao, etc.
    business_logic = Column(JSON)  # Business logic description
    dependencies = Column(JSON)  # Contract dependencies

    # Risk assessment
    risk_factors = Column(JSON)  # Identified risk factors
    compliance_status = Column(JSON)  # Regulatory compliance status
    incident_history = Column(JSON)  # Historical incidents

    __table_args__ = (
        Index("idx_contract_type_score", "contract_type", "security_score"),
        Index("idx_contract_chain_created", "chain", "creation_block"),
    )


# Model utility functions
def create_exploit_record(
    name: str,
    chain: str,
    block_number: int,
    transaction_hashes: list,
    vulnerability_type: str,
    severity: str,
    **kwargs,
) -> dict[str, Any]:
    """Create exploit record data"""
    return {
        "name": name,
        "chain": chain,
        "block_number": block_number,
        "transaction_hashes": transaction_hashes,
        "vulnerability_type": vulnerability_type,
        "severity": severity,
        **kwargs,
    }


def create_replay_session_record(
    session_type: str,
    fork_block: int,
    chain: str,
    parameters: dict[str, Any],
    exploit_id: str | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
    """Create replay session record data"""
    return {
        "exploit_id": exploit_id,
        "session_type": session_type,
        "fork_block": fork_block,
        "chain": chain,
        "parameters": parameters,
        "user_id": user_id,
        "status": SessionStatus.PENDING,
    }


# Enhanced utility functions
def create_forensic_session(
    exploit_id: str,
    fork_block: int,
    chain: str,
    analysis_config: Dict[str, Any],
    user_id: str = None,
) -> Dict[str, Any]:
    """Create a comprehensive forensic replay session"""
    return {
        "exploit_id": exploit_id,
        "session_type": "forensic",
        "fork_block": fork_block,
        "chain": chain,
        "vm_backend": VMBackend.ANVIL,
        "parameters": {
            "enable_tracing": True,
            "trace_level": "detailed",
            "capture_storage": True,
            "capture_memory": True,
            "analysis_plugins": analysis_config.get("plugins", []),
            "debug_mode": True,
        },
        "debug_config": {
            "breakpoints": analysis_config.get("breakpoints", []),
            "watch_addresses": analysis_config.get("watch_addresses", []),
            "monitor_functions": analysis_config.get("monitor_functions", []),
        },
        "user_id": user_id,
        "status": SessionStatus.PENDING,
    }


def create_timeline_bookmark(
    frame_sequence: int, name: str, description: str = "", tags: List[str] = None
) -> Dict[str, Any]:
    """Create a timeline bookmark for important moments"""
    return {
        "frame_sequence": frame_sequence,
        "name": name,
        "description": description,
        "tags": tags or [],
        "created_at": datetime.utcnow().isoformat(),
        "bookmark_id": str(uuid.uuid4()),
    }


def create_analysis_patch(
    patch_type: str,
    target_address: str,
    parameters: Dict[str, Any],
    description: str = "",
) -> Dict[str, Any]:
    """Create a standardized analysis patch"""
    patch_id = str(uuid.uuid4())

    base_patch = {
        "patch_id": patch_id,
        "type": patch_type,
        "address": target_address,
        "description": description,
        "created_at": datetime.utcnow().isoformat(),
    }

    # Merge parameters based on patch type
    if patch_type == "storage":
        base_patch.update(
            {"slot": parameters.get("slot"), "value": parameters.get("value")}
        )
    elif patch_type == "balance":
        base_patch.update({"value": parameters.get("balance")})
    elif patch_type == "code":
        base_patch.update({"bytecode": parameters.get("bytecode")})
    elif patch_type == "gas_price":
        base_patch.update({"gas_price": parameters.get("gas_price")})

    return base_patch


# Known historical exploits database
HISTORICAL_EXPLOITS = {
    "dao_hack_2016": {
        "name": "The DAO Hack",
        "chain": "ethereum",
        "block_number": 1718497,
        "transaction_hashes": [
            "0x0ec3f2488a93839524add10ea229e773f6bc891b4eb4794c3337d4495263790b"
        ],
        "vulnerability_type": "reentrancy",
        "severity": "critical",
        "description": "The DAO hack that led to Ethereum Classic fork",
        "affected_contracts": ["0xbb9bc244d798123fde783fcc1c72d3bb8c189413"],
        "attack_vector": "Recursive call exploitation via withdrawBalance",
        "financial_impact": 3600000.0,  # 3.6M ETH
        "tags": ["reentrancy", "dao", "historic", "hard_fork"],
    },
    "parity_wallet_hack_2017": {
        "name": "Parity Wallet Hack",
        "chain": "ethereum",
        "block_number": 4041179,
        "transaction_hashes": [
            "0x9dbf0326a03a2a3719c27be4fa69aacc9857fd231a8d9dcaede4bb083def75ec"
        ],
        "vulnerability_type": "access_control",
        "severity": "critical",
        "description": "Parity multisig wallet vulnerability",
        "affected_contracts": ["0x863df6bfa4469f3ead0be8f9f2aae51c91a907b4"],
        "financial_impact": 153000.0,  # 153K ETH
        "tags": ["multisig", "parity", "access_control"],
    },
    "bzx_flashloan_2020": {
        "name": "bZx Flash Loan Attack",
        "chain": "ethereum",
        "block_number": 9484688,
        "transaction_hashes": [
            "0xb5c8bd9430b6cc87a0e2fe110ece6bf527fa4f170a4bc8cd032f768fc5219838"
        ],
        "vulnerability_type": "flashloan_manipulation",
        "severity": "high",
        "description": "Flash loan price manipulation attack on bZx",
        "financial_impact": 1193.0,  # $954K at the time
        "tags": ["flashloan", "defi", "oracle_manipulation", "bzx"],
    },
}


# Extended historical exploits with forensic metadata
ENHANCED_HISTORICAL_EXPLOITS = {
    "dao_hack_2016": {
        **{
            "name": "The DAO Hack",
            "chain": "ethereum",
            "block_number": 1718497,
            "transaction_hashes": [
                "0x0ec3f2488a93839524add10ea229e773f6bc891b4eb4794c3337d4495263790b"
            ],
            "vulnerability_type": "reentrancy",
            "severity": "critical",
            "description": "The DAO hack that led to Ethereum Classic fork",
            "affected_contracts": ["0xbb9bc244d798123fde783fcc1c72d3bb8c189413"],
            "attack_vector": "Recursive call exploitation via withdrawBalance",
            "financial_impact": 3600000.0,
            "tags": ["reentrancy", "dao", "historic", "hard_fork"],
        },
        "forensic_metadata": {
            "attack_timeline": [
                {
                    "step": 1,
                    "description": "Attacker creates malicious contract",
                    "block": 1718496,
                },
                {
                    "step": 2,
                    "description": "Calls withdrawBalance recursively",
                    "block": 1718497,
                },
                {"step": 3, "description": "Drains DAO funds", "block": 1718498},
            ],
            "key_opcodes": ["CALL", "SSTORE", "SLOAD"],
            "vulnerability_pattern": "check_effects_interactions_violation",
            "mitigation_patterns": ["reentrancy_guard", "pull_payment"],
            "forensic_bookmarks": [
                {"name": "Initial malicious call", "tx_index": 0, "frame": 42},
                {"name": "Reentrancy trigger", "tx_index": 0, "frame": 156},
                {"name": "Fund drainage", "tx_index": 0, "frame": 289},
            ],
        },
    },
    "flash_loan_attack_2020": {
        **{
            "name": "bZx Flash Loan Attack #1",
            "chain": "ethereum",
            "block_number": 9484688,
            "transaction_hashes": [
                "0xb5c8bd9430b6cc87a0e2fe110ece6bf527fa4f170a4bc8cd032f768fc5219838"
            ],
            "vulnerability_type": "flashloan_manipulation",
            "severity": "high",
            "description": "Flash loan price manipulation attack",
            "financial_impact": 1193.0,
            "tags": ["flashloan", "defi", "oracle_manipulation", "bzx"],
        },
        "forensic_metadata": {
            "mev_analysis": {
                "mev_type": "arbitrage",
                "profit_extracted": 1193.0,
                "gas_optimization_score": 87.5,
                "front_running_protection": False,
            },
            "oracle_manipulation": {
                "manipulated_pairs": ["ETH/BTC"],
                "price_deviation_percent": 15.7,
                "manipulation_duration_blocks": 1,
            },
            "defi_protocol_interactions": [
                {"protocol": "Compound", "action": "borrow"},
                {"protocol": "Kyber", "action": "swap"},
                {"protocol": "bZx", "action": "exploit"},
            ],
        },
    },
}
