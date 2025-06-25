"""
MevGuardian Core Types and Data Structures
Enterprise-grade type definitions for both Attack and Guardian modes
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import uuid


class OperatingMode(Enum):
    """System operating modes"""
    GUARDIAN = "guardian"
    ATTACK = "attack" 
    HYBRID = "hybrid"


class ThreatType(Enum):
    """Types of detected threats"""
    SANDWICH_ATTACK = "sandwich_attack"
    ORACLE_MANIPULATION = "oracle_manipulation"
    FLASH_LOAN_EXPLOIT = "flash_loan_exploit"
    LIQUIDATION_ATTACK = "liquidation_attack"
    GOVERNANCE_ATTACK = "governance_attack"
    HONEYPOT = "honeypot"
    RUGPULL = "rugpull"
    BRIDGE_EXPLOIT = "bridge_exploit"
    UNKNOWN = "unknown"


class ThreatSeverity(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AttackPhase(Enum):
    """Phases of an attack"""
    PREPARATION = "preparation"
    EXECUTION = "execution"
    EXTRACTION = "extraction"
    CLEANUP = "cleanup"
    COMPLETED = "completed"


class StrategyType(Enum):
    """MEV strategy types"""
    FLASHLOAN_ARBITRAGE = "flashloan_arbitrage"
    SANDWICH_ATTACK = "sandwich_attack"
    LIQUIDATION_BOT = "liquidation_bot"
    CROSS_CHAIN_ARBITRAGE = "cross_chain_arbitrage"
    ORACLE_MANIPULATION = "oracle_manipulation"
    GOVERNANCE_ATTACK = "governance_attack"
    JIT_LIQUIDITY = "jit_liquidity"
    TWO_HOP_ARBITRAGE = "two_hop_arbitrage"


class SimulationStatus(Enum):
    """Simulation execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ChainInfo:
    """Blockchain network information"""
    chain_id: int
    name: str
    native_token: str
    block_time: float
    gas_token: str = "ETH"
    is_testnet: bool = False


@dataclass
class TokenInfo:
    """Token metadata"""
    address: str
    symbol: str
    name: str
    decimals: int
    chain_id: int
    is_verified: bool = False
    risk_score: Optional[float] = None


@dataclass
class TransactionData:
    """Raw transaction data from mempool or blocks"""
    hash: str
    from_address: str
    to_address: Optional[str]
    value: int
    gas_price: int
    gas_limit: int
    data: str
    nonce: int
    chain_id: int
    block_number: Optional[int] = None
    transaction_index: Optional[int] = None
    timestamp: Optional[datetime] = None
    max_fee_per_gas: Optional[int] = None
    max_priority_fee_per_gas: Optional[int] = None
    
    @property
    def value_eth(self) -> Decimal:
        """Transaction value in ETH"""
        return Decimal(self.value) / Decimal(10**18)
    
    @property
    def function_selector(self) -> str:
        """Function selector (first 4 bytes of data)"""
        return self.data[:10] if len(self.data) >= 10 else "0x"
    
    @property
    def is_contract_call(self) -> bool:
        """Check if transaction is a contract call"""
        return len(self.data) > 2


@dataclass
class ThreatDetection:
    """Detected security threat"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    threat_type: ThreatType = ThreatType.UNKNOWN
    severity: ThreatSeverity = ThreatSeverity.MEDIUM
    confidence: float = 0.0
    chain_id: int = 1
    
    # Threat Details
    title: str = ""
    description: str = ""
    affected_protocols: List[str] = field(default_factory=list)
    affected_tokens: List[str] = field(default_factory=list)
    
    # Financial Impact
    potential_loss_usd: Optional[float] = None
    extracted_value_usd: Optional[float] = None
    
    # Technical Details
    transaction_hashes: List[str] = field(default_factory=list)
    contract_addresses: List[str] = field(default_factory=list)
    block_numbers: List[int] = field(default_factory=list)
    
    # Attack Pattern
    attack_vector: Optional[str] = None
    exploit_method: Optional[str] = None
    
    # Timing
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "threat_type": self.threat_type.value,
            "severity": self.severity.value,
            "confidence": self.confidence,
            "chain_id": self.chain_id,
            "title": self.title,
            "description": self.description,
            "affected_protocols": self.affected_protocols,
            "affected_tokens": self.affected_tokens,
            "potential_loss_usd": self.potential_loss_usd,
            "extracted_value_usd": self.extracted_value_usd,
            "transaction_hashes": self.transaction_hashes,
            "contract_addresses": self.contract_addresses,
            "block_numbers": self.block_numbers,
            "attack_vector": self.attack_vector,
            "exploit_method": self.exploit_method,
            "detected_at": self.detected_at.isoformat(),
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "metadata": self.metadata,
            "tags": self.tags
        }


@dataclass
class AttackSimulation:
    """Attack simulation configuration and results"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    simulation_type: ThreatType = ThreatType.SANDWICH_ATTACK
    status: SimulationStatus = SimulationStatus.PENDING
    
    # Simulation Parameters
    target_protocol: str = ""
    target_transaction: Optional[str] = None
    fork_block_number: Optional[int] = None
    chain_id: int = 1
    
    # Attack Configuration
    attack_parameters: Dict[str, Any] = field(default_factory=dict)
    victim_transaction: Optional[TransactionData] = None
    
    # Results
    success: bool = False
    profit_extracted: Optional[float] = None
    gas_cost: Optional[float] = None
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timing
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Error Handling
    error_message: Optional[str] = None
    error_trace: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Simulation duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "simulation_type": self.simulation_type.value,
            "status": self.status.value,
            "target_protocol": self.target_protocol,
            "target_transaction": self.target_transaction,
            "fork_block_number": self.fork_block_number,
            "chain_id": self.chain_id,
            "attack_parameters": self.attack_parameters,
            "success": self.success,
            "profit_extracted": self.profit_extracted,
            "gas_cost": self.gas_cost,
            "execution_trace": self.execution_trace,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "error_message": self.error_message,
            "metadata": self.metadata
        }


@dataclass
class HoneypotDetection:
    """Honeypot smart contract detection"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    contract_address: str = ""
    chain_id: int = 1
    
    # Detection Details
    honeypot_type: str = "unknown"  # "transfer_tax", "gas_grief", "revert_trap", etc.
    confidence: float = 0.0
    risk_score: float = 0.0
    
    # Contract Analysis
    token_symbol: Optional[str] = None
    token_name: Optional[str] = None
    creator_address: Optional[str] = None
    creation_block: Optional[int] = None
    
    # Behavioral Patterns
    failed_transactions: int = 0
    total_transactions: int = 0
    max_gas_used: Optional[int] = None
    
    # Financial Impact
    estimated_victims: int = 0
    total_funds_trapped: Optional[float] = None
    
    # Detection Methods
    detection_methods: List[str] = field(default_factory=list)
    bytecode_similarity: Optional[float] = None
    
    # Timing
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "contract_address": self.contract_address,
            "chain_id": self.chain_id,
            "honeypot_type": self.honeypot_type,
            "confidence": self.confidence,
            "risk_score": self.risk_score,
            "token_symbol": self.token_symbol,
            "token_name": self.token_name,
            "creator_address": self.creator_address,
            "creation_block": self.creation_block,
            "failed_transactions": self.failed_transactions,
            "total_transactions": self.total_transactions,
            "max_gas_used": self.max_gas_used,
            "estimated_victims": self.estimated_victims,
            "total_funds_trapped": self.total_funds_trapped,
            "detection_methods": self.detection_methods,
            "bytecode_similarity": self.bytecode_similarity,
            "detected_at": self.detected_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class MEVOpportunity:
    """MEV opportunity detected by traditional strategies"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    strategy_type: StrategyType = StrategyType.FLASHLOAN_ARBITRAGE
    chain_id: int = 1
    
    # Financial Details
    estimated_profit: float = 0.0
    gas_cost_estimate: int = 0
    confidence_score: float = 0.0
    
    # Execution Data
    execution_data: Dict[str, Any] = field(default_factory=dict)
    target_transaction: Optional[str] = None
    victim_transaction: Optional[TransactionData] = None
    
    # Timing
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expiry: Optional[datetime] = None
    block_number: Optional[int] = None
    
    # Status
    executed: bool = False
    execution_result: Optional[Dict[str, Any]] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """Check if opportunity has expired"""
        if self.expiry:
            return datetime.now(timezone.utc) > self.expiry
        return False
    
    @property
    def net_profit(self) -> float:
        """Calculate net profit after gas costs"""
        gas_cost_eth = self.gas_cost_estimate / 10**18
        return self.estimated_profit - gas_cost_eth
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "strategy_type": self.strategy_type.value,
            "chain_id": self.chain_id,
            "estimated_profit": self.estimated_profit,
            "gas_cost_estimate": self.gas_cost_estimate,
            "confidence_score": self.confidence_score,
            "execution_data": self.execution_data,
            "target_transaction": self.target_transaction,
            "discovered_at": self.discovered_at.isoformat(),
            "expiry": self.expiry.isoformat() if self.expiry else None,
            "block_number": self.block_number,
            "executed": self.executed,
            "execution_result": self.execution_result,
            "net_profit": self.net_profit,
            "is_expired": self.is_expired,
            "metadata": self.metadata
        }


@dataclass
class ForensicAnalysis:
    """Forensic analysis of past attacks or incidents"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: Optional[str] = None
    attack_type: ThreatType = ThreatType.UNKNOWN
    
    # Incident Details
    title: str = ""
    description: str = ""
    affected_protocols: List[str] = field(default_factory=list)
    
    # Financial Impact
    total_value_extracted: Optional[float] = None
    affected_users_count: Optional[int] = None
    
    # Technical Analysis
    attack_transactions: List[str] = field(default_factory=list)
    attack_timeline: List[Dict[str, Any]] = field(default_factory=list)
    root_cause: Optional[str] = None
    exploit_technique: Optional[str] = None
    
    # Attack Pattern
    attacker_addresses: List[str] = field(default_factory=list)
    attack_sequence: List[Dict[str, Any]] = field(default_factory=list)
    
    # Mitigation
    mitigation_strategies: List[str] = field(default_factory=list)
    prevention_recommendations: List[str] = field(default_factory=list)
    
    # Timing
    incident_start: Optional[datetime] = None
    incident_end: Optional[datetime] = None
    analysis_completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "attack_type": self.attack_type.value,
            "title": self.title,
            "description": self.description,
            "affected_protocols": self.affected_protocols,
            "total_value_extracted": self.total_value_extracted,
            "affected_users_count": self.affected_users_count,
            "attack_transactions": self.attack_transactions,
            "attack_timeline": self.attack_timeline,
            "root_cause": self.root_cause,
            "exploit_technique": self.exploit_technique,
            "attacker_addresses": self.attacker_addresses,
            "attack_sequence": self.attack_sequence,
            "mitigation_strategies": self.mitigation_strategies,
            "prevention_recommendations": self.prevention_recommendations,
            "incident_start": self.incident_start.isoformat() if self.incident_start else None,
            "incident_end": self.incident_end.isoformat() if self.incident_end else None,
            "analysis_completed_at": self.analysis_completed_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class SystemMetrics:
    """System performance and health metrics"""
    
    # Guardian Metrics
    threats_detected_total: int = 0
    threats_detected_last_hour: int = 0
    simulations_executed_total: int = 0
    honeypots_identified_total: int = 0
    
    # Attack Metrics  
    opportunities_found_total: int = 0
    opportunities_found_last_hour: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_profit_eth: float = 0.0
    
    # System Performance
    mempool_transactions_processed: int = 0
    average_processing_time_ms: float = 0.0
    active_websocket_connections: int = 0
    
    # Resource Usage
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    disk_usage_percent: float = 0.0
    
    # Network
    rpc_calls_per_minute: int = 0
    websocket_messages_per_minute: int = 0
    
    # Database
    active_db_connections: int = 0
    query_response_time_ms: float = 0.0
    
    # Timestamp
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "threats_detected_total": self.threats_detected_total,
            "threats_detected_last_hour": self.threats_detected_last_hour,
            "simulations_executed_total": self.simulations_executed_total,
            "honeypots_identified_total": self.honeypots_identified_total,
            "opportunities_found_total": self.opportunities_found_total,
            "opportunities_found_last_hour": self.opportunities_found_last_hour,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "total_profit_eth": self.total_profit_eth,
            "mempool_transactions_processed": self.mempool_transactions_processed,
            "average_processing_time_ms": self.average_processing_time_ms,
            "active_websocket_connections": self.active_websocket_connections,
            "cpu_usage_percent": self.cpu_usage_percent,
            "memory_usage_mb": self.memory_usage_mb,
            "disk_usage_percent": self.disk_usage_percent,
            "rpc_calls_per_minute": self.rpc_calls_per_minute,
            "websocket_messages_per_minute": self.websocket_messages_per_minute,
            "active_db_connections": self.active_db_connections,
            "query_response_time_ms": self.query_response_time_ms,
            "timestamp": self.timestamp.isoformat()
        }


# WebSocket Event Types
@dataclass
class WebSocketEvent:
    """Base class for WebSocket events"""
    event_type: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for WebSocket transmission"""
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }


@dataclass 
class ThreatDetectedEvent(WebSocketEvent):
    """WebSocket event for new threat detection"""
    event_type: str = "threat_detected"
    threat: Optional[ThreatDetection] = None
    
    def __post_init__(self):
        if self.threat:
            self.data = self.threat.to_dict()


@dataclass
class OpportunityFoundEvent(WebSocketEvent):
    """WebSocket event for new MEV opportunity"""
    event_type: str = "opportunity_found"
    opportunity: Optional[MEVOpportunity] = None
    
    def __post_init__(self):
        if self.opportunity:
            self.data = self.opportunity.to_dict()


@dataclass
class SimulationCompleteEvent(WebSocketEvent):
    """WebSocket event for completed simulation"""
    event_type: str = "simulation_complete"
    simulation: Optional[AttackSimulation] = None
    
    def __post_init__(self):
        if self.simulation:
            self.data = self.simulation.to_dict()


@dataclass
class SystemStatusEvent(WebSocketEvent):
    """WebSocket event for system status updates"""
    event_type: str = "system_status"
    metrics: Optional[SystemMetrics] = None
    
    def __post_init__(self):
        if self.metrics:
            self.data = self.metrics.to_dict()
