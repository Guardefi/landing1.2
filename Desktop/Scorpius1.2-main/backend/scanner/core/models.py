"""Core data models for the Scorpius Vulnerability Scanner"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, IntEnum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID


class ScanStatus(Enum):
    """Enum representing the status of a vulnerability scan"""

    PENDING = "pending"  # Scan is queued but not yet started
    RUNNING = "running"  # Scan is currently running
    COMPLETED = "completed"  # Scan has finished successfully
    FAILED = "failed"  # Scan encountered an error
    CANCELLED = "cancelled"  # Scan was cancelled by user


class ScanType(Enum):
    """Types of vulnerability scans that can be performed"""

    STATIC = "static"  # Static analysis
    DYNAMIC = "dynamic"  # Dynamic analysis
    FUZZING = "fuzzing"  # Fuzzing-based testing
    VERIFICATION = "verification"  # Verification of known vulnerabilities
    FULL = "full"  # Complete scan with all available methods
    CUSTOM = "custom"  # Custom scan with user-defined parameters
    QUICK = "quick"  # Quick scan with minimal depth
    DEEP = "deep"  # Deep scan with maximum coverage
    AI_ASSISTED = "ai_assisted"  # AI-assisted vulnerability analysis
    BRIDGE = "bridge"  # Specialized scan for cross-chain bridges
    EXPLOIT_SIM = "exploit_sim"  # Simulation of potential exploits


class TargetType(Enum):
    """Types of targets that can be scanned"""

    CONTRACT = "contract"  # Smart contract
    PROTOCOL = "protocol"  # DeFi protocol
    BRIDGE = "bridge"  # Cross-chain bridge
    TOKEN = "token"  # Token contract
    DAO = "dao"  # DAO governance contract
    EXCHANGE = "exchange"  # Exchange contract
    WALLET = "wallet"  # Wallet contract
    LIBRARY = "library"  # Library contract
    PROXY = "proxy"  # Proxy contract
    FACTORY = "factory"  # Factory contract


class VulnerabilityLevel(IntEnum):
    """Severity levels for vulnerability findings"""

    INFO = 0  # Informational findings
    LOW = 1  # Low severity vulnerabilities
    MEDIUM = 2  # Medium severity vulnerabilities
    HIGH = 3  # High severity vulnerabilities
    CRITICAL = 4  # Critical severity vulnerabilities


@dataclass
class Target:
    """Represents a target for vulnerability scanning"""

    identifier: str  # Address, file path, or URL of the target
    name: Optional[str] = None  # Human-readable name of the target
    target_type: str = "contract"  # Type of target (contract, protocol, etc.)
    blockchain: Optional[str] = None  # Target blockchain (if applicable)
    source_code: Optional[Dict[str, Any]] = None  # Source code of the target
    bytecode: Optional[str] = None  # Bytecode of the target
    abi: Optional[Dict[str, Any]] = None  # ABI of the target
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "identifier": self.identifier,
            "name": self.name,
            "target_type": self.target_type,
            "blockchain": self.blockchain,
            "source_code": self.source_code,
            "bytecode": self.bytecode,
            "abi": self.abi,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Target":
        """Create from dictionary representation"""
        return cls(
            identifier=data["identifier"],
            name=data.get("name"),
            target_type=data.get("target_type", "contract"),
            blockchain=data.get("blockchain"),
            source_code=data.get("source_code"),
            bytecode=data.get("bytecode"),
            abi=data.get("abi"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ScanConfig:
    """Configuration options for a vulnerability scan"""

    timeout: int = 300  # Timeout for scan in seconds
    max_depth: int = 10  # Maximum recursion depth for analysis
    enabled_plugins: Optional[List[str]] = None  # List of plugins to enable
    disabled_plugins: Optional[List[str]] = None  # List of plugins to disable
    sandbox_enabled: bool = True  # Whether to use sandbox for execution
    ai_enabled: bool = True  # Whether to use AI-assisted analysis
    exploit_simulation_enabled: bool = False  # Whether to simulate exploits
    custom_options: Dict[str, Any] = field(default_factory=dict)  # Additional options

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "timeout": self.timeout,
            "max_depth": self.max_depth,
            "enabled_plugins": self.enabled_plugins,
            "disabled_plugins": self.disabled_plugins,
            "sandbox_enabled": self.sandbox_enabled,
            "ai_enabled": self.ai_enabled,
            "exploit_simulation_enabled": self.exploit_simulation_enabled,
            "custom_options": self.custom_options,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScanConfig":
        """Create from dictionary representation"""
        return cls(
            timeout=data.get("timeout", 300),
            max_depth=data.get("max_depth", 10),
            enabled_plugins=data.get("enabled_plugins"),
            disabled_plugins=data.get("disabled_plugins"),
            sandbox_enabled=data.get("sandbox_enabled", True),
            ai_enabled=data.get("ai_enabled", True),
            exploit_simulation_enabled=data.get("exploit_simulation_enabled", False),
            custom_options=data.get("custom_options", {}),
        )


@dataclass
class VulnerabilityFinding:
    """Represents a vulnerability finding"""

    # Core finding information
    vulnerability_type: str  # Type of vulnerability (e.g., "reentrancy", "overflow")
    title: str  # Short title of the finding
    description: str  # Detailed description of the vulnerability
    severity: VulnerabilityLevel  # Severity level
    confidence: float  # Confidence level (0.0 to 1.0)
    location: str  # Location of the vulnerability in the code

    # Additional metadata
    id: Optional[str] = None  # Unique identifier
    source: Optional[str] = None  # Plugin/scanner that found the vulnerability
    cwe_id: Optional[str] = None  # Common Weakness Enumeration ID
    cvss_score: Optional[float] = None  # CVSS score if applicable
    timestamp: Optional[str] = None  # When the finding was discovered
    snippet: Optional[str] = None  # Code snippet containing the vulnerability
    line_number: Optional[int] = None  # Line number of the vulnerability

    # Remediation information
    recommendation: Optional[str] = None  # Recommended fix
    references: List[str] = field(default_factory=list)  # Reference links
    tags: List[str] = field(default_factory=list)  # Tags for categorization

    # Additional details
    exploit_scenario: Optional[str] = None  # Example exploit scenario
    exploit_code: Optional[str] = None  # POC exploit code if generated
    proof: Optional[Dict[str, Any]] = None  # Proof of vulnerability
    false_positive_risk: Optional[float] = None  # Risk of false positive
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "vulnerability_type": self.vulnerability_type,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.name,
            "severity_value": self.severity.value,
            "confidence": self.confidence,
            "location": self.location,
            "source": self.source,
            "cwe_id": self.cwe_id,
            "cvss_score": self.cvss_score,
            "timestamp": self.timestamp,
            "snippet": self.snippet,
            "line_number": self.line_number,
            "recommendation": self.recommendation,
            "references": self.references,
            "tags": self.tags,
            "exploit_scenario": self.exploit_scenario,
            "exploit_code": self.exploit_code,
            "proof": self.proof,
            "false_positive_risk": self.false_positive_risk,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VulnerabilityFinding":
        """Create from dictionary representation"""
        severity_value = data.get("severity_value", VulnerabilityLevel.MEDIUM.value)
        severity_name = data.get("severity", VulnerabilityLevel.MEDIUM.name)

        # Try to parse severity from value or name
        try:
            severity = VulnerabilityLevel(severity_value)
        except ValueError:
            try:
                severity = VulnerabilityLevel[severity_name]
            except KeyError:
                severity = VulnerabilityLevel.MEDIUM

        return cls(
            id=data.get("id"),
            vulnerability_type=data["vulnerability_type"],
            title=data["title"],
            description=data["description"],
            severity=severity,
            confidence=data.get("confidence", 0.5),
            location=data["location"],
            source=data.get("source"),
            cwe_id=data.get("cwe_id"),
            cvss_score=data.get("cvss_score"),
            timestamp=data.get("timestamp"),
            snippet=data.get("snippet"),
            line_number=data.get("line_number"),
            recommendation=data.get("recommendation"),
            references=data.get("references", []),
            tags=data.get("tags", []),
            exploit_scenario=data.get("exploit_scenario"),
            exploit_code=data.get("exploit_code"),
            proof=data.get("proof"),
            false_positive_risk=data.get("false_positive_risk"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ScanResult:
    """Represents the result of a vulnerability scan"""

    # Core information
    id: str  # Unique identifier for the scan
    target: Target  # Target of the scan
    scan_type: ScanType  # Type of scan performed
    status: ScanStatus  # Current status of the scan
    start_time: str  # When the scan started (ISO format)

    # Results and progress
    findings: List[VulnerabilityFinding] = field(
        default_factory=list
    )  # Vulnerability findings
    progress: int = 0  # Progress percentage (0-100)
    end_time: Optional[str] = None  # When the scan ended (ISO format)
    duration: Optional[float] = None  # Duration in seconds

    # Configuration and metadata
    config: ScanConfig = field(default_factory=ScanConfig)  # Scan configuration
    error: Optional[str] = None  # Error message if the scan failed
    current_plugin: Optional[str] = None  # Currently running plugin
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "target": self.target.to_dict(),
            "scan_type": self.scan_type.value,
            "status": self.status.value,
            "start_time": self.start_time,
            "findings": [finding.to_dict() for finding in self.findings],
            "progress": self.progress,
            "end_time": self.end_time,
            "duration": self.duration,
            "config": self.config.to_dict(),
            "error": self.error,
            "current_plugin": self.current_plugin,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScanResult":
        """Create from dictionary representation"""
        target = Target.from_dict(data["target"])

        try:
            scan_type = ScanType(data["scan_type"])
        except ValueError:
            scan_type = ScanType.FULL

        try:
            status = ScanStatus(data["status"])
        except ValueError:
            status = ScanStatus.PENDING

        config = ScanConfig.from_dict(data.get("config", {}))

        findings = []
        for finding_data in data.get("findings", []):
            try:
                findings.append(VulnerabilityFinding.from_dict(finding_data))
            except Exception as e:
                # Skip invalid findings
                pass

        return cls(
            id=data["id"],
            target=target,
            scan_type=scan_type,
            status=status,
            start_time=data["start_time"],
            findings=findings,
            progress=data.get("progress", 0),
            end_time=data.get("end_time"),
            duration=data.get("duration"),
            config=config,
            error=data.get("error"),
            current_plugin=data.get("current_plugin"),
            metadata=data.get("metadata", {}),
        )
