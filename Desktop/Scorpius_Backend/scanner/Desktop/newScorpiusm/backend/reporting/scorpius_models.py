"""
Scorpius AI-Powered Vulnerability Scanner Models
Advanced smart contract security analysis powered by Claude AI
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from core.db import Base
from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text


class ScanType(str, Enum):
    """Types of vulnerability scans"""

    QUICK_SCAN = "quick_scan"
    DEEP_ANALYSIS = "deep_analysis"
    CUSTOM_EXPLOIT = "custom_exploit"
    AI_ASSISTED = "ai_assisted"
    SUPPLY_CHAIN = "supply_chain"
    CROSS_CHAIN = "cross_chain"


class VulnerabilityLevel(str, Enum):
    """Vulnerability severity levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ScanStatus(str, Enum):
    """Scan execution status"""

    PENDING = "pending"
    RUNNING = "running"
    ANALYZING = "analyzing"
    GENERATING_REPORT = "generating_report"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VulnerabilityType(str, Enum):
    """Types of vulnerabilities detected"""

    BACKDOOR = "backdoor"
    REENTRANCY = "reentrancy"
    ACCESS_CONTROL = "access_control"
    PROXY_TAMPERING = "proxy_tampering"
    ORACLE_MANIPULATION = "oracle_manipulation"
    CROSS_CHAIN_EXPLOIT = "cross_chain_exploit"
    SUPPLY_CHAIN_ATTACK = "supply_chain_attack"
    RACE_CONDITION = "race_condition"
    LIBRARY_DEPENDENCY = "library_dependency"
    UPGRADE_VULNERABILITY = "upgrade_vulnerability"
    DELEGATECALL_EXPLOIT = "delegatecall_exploit"
    FLASH_LOAN_ATTACK = "flash_loan_attack"
    SANDWICH_ATTACK = "sandwich_attack"
    MEV_VULNERABILITY = "mev_vulnerability"
    ADMIN_PRIVILEGE_ABUSE = "admin_privilege_abuse"


@dataclass
class ContractInfo:
    """Smart contract information"""

    address: str
    name: str | None = None
    verified: bool = False
    proxy: bool = False
    implementation: str | None = None
    balance: str = "0"
    tx_count: int = 0
    creation_block: int | None = None
    compiler_version: str | None = None
    optimization: bool = False


@dataclass
class VulnerabilityFinding:
    """Individual vulnerability finding"""

    vuln_type: VulnerabilityType
    severity: VulnerabilityLevel
    title: str
    description: str
    function_name: str | None = None
    function_signature: str | None = None
    line_number: int | None = None
    code_snippet: str | None = None
    exploit_code: str | None = None
    mitigation: str | None = None
    references: list[str] = None
    cve_id: str | None = None
    confidence: float = 0.0
    ai_analysis: str | None = None


@dataclass
class ScorpiusAnalysis:
    """AI analysis results"""

    model_used: str = "claude-3-opus"
    confidence_score: float = 0.0
    risk_assessment: str = ""
    attack_vectors: list[str] = None
    exploitation_complexity: str = "unknown"
    business_impact: str = ""
    recommendations: list[str] = None
    ai_reasoning: str = ""


class ScorpiusScan(Base):
    """Scorpius vulnerability scan record"""

    __tablename__ = "scorpius_scans"

    id = Column(String, primary_key=True)
    contract_address = Column(String, nullable=False, index=True)
    chain = Column(String, nullable=False, default="ethereum")
    scan_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default=ScanStatus.PENDING.value)

    # Contract information
    contract_info = Column(JSON, nullable=True)

    # Scan configuration
    scan_config = Column(JSON, nullable=True)
    ai_model = Column(String, default="claude-3-opus")

    # Results
    vulnerabilities_found = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)

    # Analysis results
    findings = Column(JSON, nullable=True)  # List of VulnerabilityFinding
    ai_analysis = Column(JSON, nullable=True)  # ScorpiusAnalysis

    # Execution details
    scan_duration = Column(Float, nullable=True)
    gas_analysis = Column(JSON, nullable=True)

    # Report
    report_html_path = Column(String, nullable=True)
    report_pdf_path = Column(String, nullable=True)
    report_json_path = Column(String, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    user_id = Column(String, nullable=True)

    # Additional context
    tags = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    source_code = Column(Text, nullable=True)
    bytecode = Column(Text, nullable=True)


@dataclass
class ScanRequest:
    """Request for Scorpius scan"""

    contract_address: str
    chain: str = "ethereum"
    scan_type: ScanType = ScanType.AI_ASSISTED
    deep_analysis: bool = True
    include_ai_analysis: bool = True
    generate_exploit_poc: bool = False
    check_supply_chain: bool = False
    analyze_dependencies: bool = True
    custom_patterns: list[str] | None = None
    ai_prompt_context: str | None = None


@dataclass
class ScanResponse:
    """Response from Scorpius scan"""

    scan_id: str
    status: ScanStatus
    message: str
    estimated_duration: int | None = None
    progress: float = 0.0


@dataclass
class ScanProgress:
    """Scan progress information"""

    scan_id: str
    status: ScanStatus
    progress: float
    current_stage: str
    stages_completed: list[str]
    estimated_remaining: int | None = None
    vulnerabilities_found: int = 0
    error_message: str | None = None
