"""
SCORPIUS AI BLOCKCHAIN FORENSICS
Advanced AI-powered blockchain forensics and investigation platform.
Provides comprehensive tools for transaction analysis, pattern recognition, and compliance.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import re
from collections import defaultdict, Counter
import statistics
import networkx as nx

# For AI/ML functionality (mock implementations to avoid import errors)
class MockMLModel:
    """Mock ML model for demonstration."""
    def __init__(self, model_type: str):
        self.model_type = model_type
        self.is_trained = False
    
    def predict(self, data):
        # Mock prediction
        return {"confidence": 0.85, "classification": "suspicious"}
    
    def fit(self, X, y):
        self.is_trained = True

class ForensicsEventType(Enum):
    """Types of forensics events."""
    SUSPICIOUS_TRANSACTION = "suspicious_transaction"
    MONEY_LAUNDERING = "money_laundering"
    MIXER_USAGE = "mixer_usage"
    EXCHANGE_DEPOSIT = "exchange_deposit"
    HIGH_FREQUENCY_TRADING = "high_frequency_trading"
    SMART_CONTRACT_EXPLOIT = "smart_contract_exploit"
    PHISHING_SCAM = "phishing_scam"
    PONZI_SCHEME = "ponzi_scheme"
    FLASH_LOAN_ATTACK = "flash_loan_attack"
    FRONT_RUNNING = "front_running"

class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class ComplianceStandard(Enum):
    """Compliance standards."""
    AML = "anti_money_laundering"
    KYC = "know_your_customer"
    FATF = "financial_action_task_force"
    OFAC = "office_foreign_assets_control"
    EU_5AMLD = "eu_5th_anti_money_laundering_directive"
    TRAVEL_RULE = "travel_rule"

@dataclass
class ForensicsAlert:
    """Forensics investigation alert."""
    id: str
    event_type: ForensicsEventType
    risk_level: RiskLevel
    confidence: float
    description: str
    transaction_hashes: List[str]
    addresses_involved: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    evidence: Dict[str, Any] = field(default_factory=dict)
    compliance_violations: List[ComplianceStandard] = field(default_factory=list)
    follow_up_required: bool = False
    investigator_notes: str = ""

@dataclass
class TransactionPattern:
    """Detected transaction pattern."""
    pattern_type: str
    description: str
    addresses: List[str]
    transactions: List[str]
    time_span: timedelta
    frequency: float
    total_value: float
    risk_indicators: List[str]
    confidence: float

@dataclass
class AddressProfile:
    """Comprehensive address profile."""
    address: str
    label: Optional[str] = None
    category: Optional[str] = None
    risk_score: float = 0.0
    transaction_count: int = 0
    total_volume: float = 0.0
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    connected_addresses: Set[str] = field(default_factory=set)
    known_services: List[str] = field(default_factory=list)
    compliance_flags: List[str] = field(default_factory=list)
    behavioral_patterns: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InvestigationCase:
    """Forensics investigation case."""
    case_id: str
    title: str
    description: str
    investigator: str
    status: str
    priority: RiskLevel
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    alerts: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    suspects: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    notes: str = ""

class AIForensicsEngine:
    """AI-powered forensics analysis engine."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize AI models
        self.anomaly_detector = MockMLModel("anomaly_detection")
        self.pattern_recognizer = MockMLModel("pattern_recognition")
        self.risk_classifier = MockMLModel("risk_classification")
        self.clustering_model = MockMLModel("clustering")
        self.graph_analyzer = MockMLModel("graph_analysis")
        
        # Training data cache
        self.training_data = {
            "suspicious_patterns": [],
            "normal_patterns": [],
            "known_addresses": {}
        }
    
    async def analyze_transaction_anomalies(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalous transactions using AI."""
        anomalies = []
        
        for tx in transactions:
            # Extract features for ML model
            features = self._extract_transaction_features(tx)
            
            # AI anomaly detection
            anomaly_score = self.anomaly_detector.predict(features)
            
            if anomaly_score["confidence"] > 0.7:
                anomalies.append({
                    "transaction_hash": tx["hash"],
                    "anomaly_score": anomaly_score["confidence"],
                    "anomaly_type": anomaly_score.get("classification", "unknown"),
                    "features": features,
                    "explanation": self._generate_anomaly_explanation(features, anomaly_score)
                })
        
        return anomalies
    
    async def detect_money_laundering_patterns(self, address_graph: Dict[str, Any]) -> List[TransactionPattern]:
        """Detect money laundering patterns using graph analysis."""
        patterns = []
        
        # Build transaction graph
        G = nx.DiGraph()
        
        for addr, data in address_graph.items():
            G.add_node(addr, **data)
            
            for tx in data.get("transactions", []):
                if "to_address" in tx:
                    G.add_edge(addr, tx["to_address"], **tx)
        
        # Detect common money laundering patterns
        
        # 1. Layering pattern (multiple hops)
        layering_patterns = await self._detect_layering_pattern(G)
        patterns.extend(layering_patterns)
        
        # 2. Smurfing pattern (splitting large amounts)
        smurfing_patterns = await self._detect_smurfing_pattern(G)
        patterns.extend(smurfing_patterns)
        
        # 3. Round-trip transactions
        roundtrip_patterns = await self._detect_roundtrip_pattern(G)
        patterns.extend(roundtrip_patterns)
        
        # 4. Mixer/Tumbler usage
        mixer_patterns = await self._detect_mixer_usage(G)
        patterns.extend(mixer_patterns)
        
        return patterns
    
    async def _detect_layering_pattern(self, graph: nx.DiGraph) -> List[TransactionPattern]:
        """Detect layering money laundering pattern."""
        patterns = []
        
        # Find paths with multiple hops and decreasing amounts
        for start_node in graph.nodes():
            paths = nx.single_source_shortest_path(graph, start_node, cutoff=5)
            
            for end_node, path in paths.items():
                if len(path) >= 4:  # At least 3 hops
                    # Analyze the path for layering characteristics
                    path_data = self._analyze_transaction_path(graph, path)
                    
                    if self._is_layering_pattern(path_data):
                        patterns.append(TransactionPattern(
                            pattern_type="layering",
                            description="Multi-hop transaction pattern with decreasing amounts",
                            addresses=path,
                            transactions=path_data["transaction_hashes"],
                            time_span=path_data["time_span"],
                            frequency=path_data["frequency"],
                            total_value=path_data["total_value"],
                            risk_indicators=["multiple_hops", "amount_splitting", "rapid_succession"],
                            confidence=0.8
                        ))
        
        return patterns
    
    async def _detect_smurfing_pattern(self, graph: nx.DiGraph) -> List[TransactionPattern]:
        """Detect smurfing (structuring) pattern."""
        patterns = []
        
        # Look for addresses receiving multiple small amounts just below reporting thresholds
        threshold = 10000  # Example threshold
        
        for node in graph.nodes():
            incoming_edges = list(graph.in_edges(node, data=True))
            
            if len(incoming_edges) >= 5:  # Multiple incoming transactions
                amounts = [edge[2].get("amount", 0) for edge in incoming_edges]
                
                # Check if most amounts are just below threshold
                below_threshold = [amt for amt in amounts if 7000 <= amt <= threshold]
                
                if len(below_threshold) >= 3:
                    time_window = self._get_transaction_time_window(incoming_edges)
                    
                    if time_window <= timedelta(days=7):  # Within a week
                        patterns.append(TransactionPattern(
                            pattern_type="smurfing",
                            description="Multiple transactions just below reporting threshold",
                            addresses=[node] + [edge[0] for edge in incoming_edges],
                            transactions=[edge[2].get("hash", "") for edge in incoming_edges],
                            time_span=time_window,
                            frequency=len(below_threshold) / time_window.days if time_window.days > 0 else len(below_threshold),
                            total_value=sum(below_threshold),
                            risk_indicators=["amount_structuring", "threshold_avoidance", "multiple_sources"],
                            confidence=0.85
                        ))
        
        return patterns
    
    async def _detect_roundtrip_pattern(self, graph: nx.DiGraph) -> List[TransactionPattern]:
        """Detect round-trip transaction patterns."""
        patterns = []
        
        # Find cycles in the graph
        try:
            cycles = list(nx.simple_cycles(graph))
            
            for cycle in cycles:
                if len(cycle) >= 2:
                    # Analyze the cycle for round-trip characteristics
                    cycle_data = self._analyze_cycle(graph, cycle)
                    
                    if cycle_data["is_roundtrip"]:
                        patterns.append(TransactionPattern(
                            pattern_type="roundtrip",
                            description="Circular transaction pattern returning to origin",
                            addresses=cycle,
                            transactions=cycle_data["transaction_hashes"],
                            time_span=cycle_data["time_span"],
                            frequency=1.0,
                            total_value=cycle_data["total_value"],
                            risk_indicators=["circular_flow", "value_preservation", "obfuscation"],
                            confidence=0.9
                        ))
        
        except nx.NetworkXError:
            # Handle cases where cycle detection fails
            pass
        
        return patterns
    
    async def _detect_mixer_usage(self, graph: nx.DiGraph) -> List[TransactionPattern]:
        """Detect cryptocurrency mixer/tumbler usage."""
        patterns = []
        
        # Known mixer patterns
        mixer_indicators = [
            "tornado.cash", "mixer", "tumbler", "blender",
            "coinjoin", "wasabi", "samourai"
        ]
        
        for node in graph.nodes():
            node_data = graph.nodes[node]
            
            # Check if address is labeled as a mixer
            is_mixer = any(indicator in str(node_data.get("label", "")).lower() 
                          for indicator in mixer_indicators)
            
            if is_mixer or self._has_mixer_characteristics(graph, node):
                # Analyze transactions to/from mixer
                in_edges = list(graph.in_edges(node, data=True))
                out_edges = list(graph.out_edges(node, data=True))
                
                if len(in_edges) >= 3 and len(out_edges) >= 3:
                    all_addresses = [edge[0] for edge in in_edges] + [edge[1] for edge in out_edges]
                    all_transactions = [edge[2].get("hash", "") for edge in in_edges + out_edges]
                    
                    patterns.append(TransactionPattern(
                        pattern_type="mixer_usage",
                        description="Cryptocurrency mixer/tumbler usage detected",
                        addresses=list(set(all_addresses)),
                        transactions=all_transactions,
                        time_span=self._get_transaction_time_window(in_edges + out_edges),
                        frequency=len(all_transactions),
                        total_value=sum(edge[2].get("amount", 0) for edge in in_edges),
                        risk_indicators=["mixer_service", "privacy_tool", "obfuscation"],
                        confidence=0.95
                    ))
        
        return patterns
    
    def _extract_transaction_features(self, transaction: Dict[str, Any]) -> Dict[str, float]:
        """Extract features from transaction for ML analysis."""
        return {
            "amount": float(transaction.get("value", 0)),
            "gas_price": float(transaction.get("gasPrice", 0)),
            "gas_used": float(transaction.get("gasUsed", 0)),
            "hour_of_day": datetime.fromisoformat(transaction.get("timestamp", "2023-01-01")).hour,
            "day_of_week": datetime.fromisoformat(transaction.get("timestamp", "2023-01-01")).weekday(),
            "is_contract_call": 1.0 if transaction.get("to", "").startswith("0x") and len(transaction.get("input", "")) > 2 else 0.0,
            "input_data_size": len(transaction.get("input", "")),
            "transaction_fee": float(transaction.get("gasUsed", 0)) * float(transaction.get("gasPrice", 0))
        }
    
    def _generate_anomaly_explanation(self, features: Dict[str, float], anomaly_result: Dict[str, Any]) -> str:
        """Generate human-readable explanation for anomaly detection."""
        explanations = []
        
        if features["amount"] > 1000000:  # Large amount
            explanations.append("Unusually large transaction amount")
        
        if features["gas_price"] > 100000000000:  # High gas price
            explanations.append("Extremely high gas price (possible front-running)")
        
        if features["hour_of_day"] < 3 or features["hour_of_day"] > 23:
            explanations.append("Transaction during unusual hours")
        
        if features["input_data_size"] > 10000:
            explanations.append("Large input data size")
        
        return "; ".join(explanations) if explanations else "Pattern deviates from normal transaction behavior"
    
    def _analyze_transaction_path(self, graph: nx.DiGraph, path: List[str]) -> Dict[str, Any]:
        """Analyze a transaction path for characteristics."""
        transaction_hashes = []
        amounts = []
        timestamps = []
        
        for i in range(len(path) - 1):
            edge_data = graph.get_edge_data(path[i], path[i + 1], {})
            transaction_hashes.append(edge_data.get("hash", ""))
            amounts.append(edge_data.get("amount", 0))
            if "timestamp" in edge_data:
                timestamps.append(datetime.fromisoformat(edge_data["timestamp"]))
        
        time_span = max(timestamps) - min(timestamps) if timestamps else timedelta(0)
        
        return {
            "transaction_hashes": transaction_hashes,
            "amounts": amounts,
            "time_span": time_span,
            "total_value": sum(amounts),
            "frequency": len(amounts) / max(time_span.total_seconds() / 3600, 1)  # per hour
        }
    
    def _is_layering_pattern(self, path_data: Dict[str, Any]) -> bool:
        """Determine if path exhibits layering characteristics."""
        amounts = path_data["amounts"]
        
        if len(amounts) < 3:
            return False
        
        # Check for decreasing amounts (characteristic of layering)
        decreasing_trend = sum(amounts[i] > amounts[i + 1] for i in range(len(amounts) - 1))
        
        # Check for rapid succession
        rapid_succession = path_data["time_span"] <= timedelta(hours=24)
        
        # Check for significant amount splitting
        total_input = amounts[0] if amounts else 0
        total_output = amounts[-1] if amounts else 0
        value_preservation = 0.7 <= (total_output / total_input) <= 1.0 if total_input > 0 else False
        
        return decreasing_trend >= len(amounts) // 2 and rapid_succession and value_preservation
    
    def _get_transaction_time_window(self, edges: List[Tuple]) -> timedelta:
        """Get time window for a set of transactions."""
        timestamps = []
        
        for edge in edges:
            if len(edge) > 2 and "timestamp" in edge[2]:
                timestamps.append(datetime.fromisoformat(edge[2]["timestamp"]))
        
        return max(timestamps) - min(timestamps) if timestamps else timedelta(0)
    
    def _analyze_cycle(self, graph: nx.DiGraph, cycle: List[str]) -> Dict[str, Any]:
        """Analyze a cycle for round-trip characteristics."""
        transaction_hashes = []
        total_value = 0
        timestamps = []
        
        for i in range(len(cycle)):
            next_node = cycle[(i + 1) % len(cycle)]
            edge_data = graph.get_edge_data(cycle[i], next_node, {})
            
            transaction_hashes.append(edge_data.get("hash", ""))
            total_value += edge_data.get("amount", 0)
            
            if "timestamp" in edge_data:
                timestamps.append(datetime.fromisoformat(edge_data["timestamp"]))
        
        time_span = max(timestamps) - min(timestamps) if timestamps else timedelta(0)
        
        # A round-trip should preserve most of the value
        is_roundtrip = len(cycle) >= 2 and time_span <= timedelta(days=30)
        
        return {
            "is_roundtrip": is_roundtrip,
            "transaction_hashes": transaction_hashes,
            "total_value": total_value,
            "time_span": time_span
        }
    
    def _has_mixer_characteristics(self, graph: nx.DiGraph, node: str) -> bool:
        """Check if node has characteristics of a mixer service."""
        in_edges = list(graph.in_edges(node, data=True))
        out_edges = list(graph.out_edges(node, data=True))
        
        # Mixers typically have:
        # 1. Many inputs and outputs
        # 2. Similar amounts in and out
        # 3. Temporal clustering of transactions
        
        if len(in_edges) < 10 or len(out_edges) < 10:
            return False
        
        # Check for amount homogeneity
        in_amounts = [edge[2].get("amount", 0) for edge in in_edges]
        out_amounts = [edge[2].get("amount", 0) for edge in out_edges]
        
        # Standard deviation should be low for mixers (similar amounts)
        in_std = statistics.stdev(in_amounts) if len(in_amounts) > 1 else float('inf')
        out_std = statistics.stdev(out_amounts) if len(out_amounts) > 1 else float('inf')
        
        in_mean = statistics.mean(in_amounts) if in_amounts else 0
        out_mean = statistics.mean(out_amounts) if out_amounts else 0
        
        # Low coefficient of variation indicates similar amounts
        in_cv = in_std / in_mean if in_mean > 0 else float('inf')
        out_cv = out_std / out_mean if out_mean > 0 else float('inf')
        
        return in_cv < 0.3 and out_cv < 0.3

class BlockchainForensicsEngine:
    """
    Main blockchain forensics investigation platform.
    Combines AI analysis with traditional forensics techniques.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize AI engine
        self.ai_engine = AIForensicsEngine()
        
        # Data storage
        self.alerts: Dict[str, ForensicsAlert] = {}
        self.cases: Dict[str, InvestigationCase] = {}
        self.address_profiles: Dict[str, AddressProfile] = {}
        self.known_addresses: Dict[str, Dict[str, Any]] = {}
        
        # Compliance rules
        self.compliance_rules = self._load_compliance_rules()
        
        # Performance tracking
        self.analysis_stats = {
            "total_investigations": 0,
            "alerts_generated": 0,
            "patterns_detected": 0,
            "compliance_violations": 0,
            "average_investigation_time": 0.0
        }
    
    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Load compliance rules and thresholds."""
        return {
            "transaction_reporting_threshold": 10000,
            "suspicious_activity_threshold": 5000,
            "high_frequency_threshold": 100,  # transactions per hour
            "mixer_risk_score": 0.8,
            "exchange_deposit_monitoring": True,
            "sanctions_screening": True,
            "travel_rule_threshold": 1000
        }
    
    async def investigate_address(self, address: str, depth: int = 3) -> Dict[str, Any]:
        """
        Comprehensive address investigation.
        
        Args:
            address: Blockchain address to investigate
            depth: Investigation depth (number of hops)
            
        Returns:
            Investigation results
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting investigation for address: {address}")
            
            # Build address profile
            profile = await self._build_address_profile(address, depth)
            
            # Perform AI analysis
            anomalies = await self._analyze_address_anomalies(address, profile)
            
            # Check compliance violations
            compliance_issues = await self._check_compliance_violations(address, profile)
            
            # Detect patterns
            patterns = await self._detect_address_patterns(address, profile)
            
            # Calculate risk score
            risk_score = await self._calculate_risk_score(profile, anomalies, compliance_issues, patterns)
            
            # Generate alerts if necessary
            alerts = await self._generate_alerts(address, risk_score, anomalies, compliance_issues, patterns)
            
            investigation_time = time.time() - start_time
            
            # Update statistics
            self.analysis_stats["total_investigations"] += 1
            self.analysis_stats["average_investigation_time"] = (
                (self.analysis_stats["average_investigation_time"] * (self.analysis_stats["total_investigations"] - 1) + investigation_time) /
                self.analysis_stats["total_investigations"]
            )
            
            results = {
                "address": address,
                "investigation_id": f"inv_{int(time.time())}_{hash(address) % 10000}",
                "profile": profile.__dict__ if isinstance(profile, AddressProfile) else profile,
                "risk_score": risk_score,
                "anomalies": anomalies,
                "compliance_issues": compliance_issues,
                "patterns": [p.__dict__ if hasattr(p, '__dict__') else p for p in patterns],
                "alerts": [alert.id for alert in alerts],
                "investigation_time": investigation_time,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Investigation completed for {address} in {investigation_time:.2f}s")
            return results
            
        except Exception as e:
            self.logger.error(f"Investigation failed for {address}: {e}")
            raise
    
    async def _build_address_profile(self, address: str, depth: int) -> AddressProfile:
        """Build comprehensive address profile."""
        # Mock implementation - in reality, this would query blockchain data
        profile = AddressProfile(
            address=address,
            label=self.known_addresses.get(address, {}).get("label"),
            category=self.known_addresses.get(address, {}).get("category"),
            transaction_count=150,
            total_volume=50000.0,
            first_seen=datetime.now() - timedelta(days=365),
            last_seen=datetime.now() - timedelta(days=1),
            connected_addresses={"0x123...", "0x456...", "0x789..."},
            known_services=["exchange", "defi_protocol"],
            compliance_flags=[],
            behavioral_patterns={}
        )
        
        # Store profile
        self.address_profiles[address] = profile
        
        return profile
    
    async def _analyze_address_anomalies(self, address: str, profile: AddressProfile) -> List[Dict[str, Any]]:
        """Analyze address for anomalous behavior."""
        # Mock transaction data
        transactions = [
            {
                "hash": f"0x{i:064x}",
                "value": 1000 + i * 100,
                "gasPrice": 20000000000,
                "gasUsed": 21000,
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
                "to": f"0x{(i*2):040x}",
                "input": "0x"
            }
            for i in range(20)
        ]
        
        anomalies = await self.ai_engine.analyze_transaction_anomalies(transactions)
        return anomalies
    
    async def _check_compliance_violations(self, address: str, profile: AddressProfile) -> List[Dict[str, Any]]:
        """Check for compliance violations."""
        violations = []
        
        # Check transaction reporting threshold
        if profile.total_volume > self.compliance_rules["transaction_reporting_threshold"]:
            violations.append({
                "type": "reporting_threshold_exceeded",
                "standard": ComplianceStandard.AML.value,
                "description": f"Total volume ${profile.total_volume:,.2f} exceeds reporting threshold",
                "severity": "medium"
            })
        
        # Check for sanctions screening
        if self.compliance_rules["sanctions_screening"]:
            is_sanctioned = await self._check_sanctions_list(address)
            if is_sanctioned:
                violations.append({
                    "type": "sanctions_violation",
                    "standard": ComplianceStandard.OFAC.value,
                    "description": "Address appears on sanctions list",
                    "severity": "critical"
                })
        
        # Check high-frequency trading
        if profile.transaction_count > self.compliance_rules["high_frequency_threshold"]:
            violations.append({
                "type": "high_frequency_activity",
                "standard": ComplianceStandard.AML.value,
                "description": f"{profile.transaction_count} transactions exceed frequency threshold",
                "severity": "low"
            })
        
        return violations
    
    async def _detect_address_patterns(self, address: str, profile: AddressProfile) -> List[TransactionPattern]:
        """Detect patterns associated with address."""
        # Mock address graph data
        address_graph = {
            address: {
                "transactions": [
                    {
                        "hash": f"0x{i:064x}",
                        "to_address": f"0x{(i*2):040x}",
                        "amount": 1000 + i * 100,
                        "timestamp": (datetime.now() - timedelta(days=i)).isoformat()
                    }
                    for i in range(10)
                ]
            }
        }
        
        patterns = await self.ai_engine.detect_money_laundering_patterns(address_graph)
        return patterns
    
    async def _calculate_risk_score(self, profile: AddressProfile, anomalies: List[Dict[str, Any]],
                                   compliance_issues: List[Dict[str, Any]], patterns: List[TransactionPattern]) -> float:
        """Calculate comprehensive risk score."""
        base_score = 0.0
        
        # Risk factors
        volume_factor = min(profile.total_volume / 100000, 1.0) * 0.2  # Max 0.2 for volume
        
        anomaly_factor = len(anomalies) * 0.1  # 0.1 per anomaly
        
        compliance_factor = sum(
            0.3 if issue["severity"] == "critical" else
            0.2 if issue["severity"] == "high" else
            0.1 if issue["severity"] == "medium" else
            0.05 for issue in compliance_issues
        )
        
        pattern_factor = sum(p.confidence * 0.15 for p in patterns)  # Weighted by confidence
        
        # Service risk (exchanges are lower risk, mixers are higher)
        service_factor = 0.0
        if "mixer" in profile.known_services or "tumbler" in profile.known_services:
            service_factor = 0.4
        elif "exchange" in profile.known_services:
            service_factor = -0.1  # Reduce risk for known exchanges
        
        total_score = min(base_score + volume_factor + anomaly_factor + compliance_factor + pattern_factor + service_factor, 1.0)
        
        # Update profile
        profile.risk_score = total_score
        
        return total_score
    
    async def _generate_alerts(self, address: str, risk_score: float, anomalies: List[Dict[str, Any]],
                              compliance_issues: List[Dict[str, Any]], patterns: List[TransactionPattern]) -> List[ForensicsAlert]:
        """Generate alerts based on analysis results."""
        alerts = []
        
        # High risk score alert
        if risk_score >= 0.7:
            alert = ForensicsAlert(
                id=f"alert_{int(time.time())}_{len(self.alerts)}",
                event_type=ForensicsEventType.SUSPICIOUS_TRANSACTION,
                risk_level=RiskLevel.HIGH if risk_score >= 0.8 else RiskLevel.MEDIUM,
                confidence=risk_score,
                description=f"High-risk address detected (risk score: {risk_score:.2f})",
                transaction_hashes=[],
                addresses_involved=[address],
                evidence={
                    "risk_score": risk_score,
                    "anomaly_count": len(anomalies),
                    "compliance_violations": len(compliance_issues),
                    "pattern_count": len(patterns)
                },
                compliance_violations=[ComplianceStandard.AML],
                follow_up_required=True
            )
            
            self.alerts[alert.id] = alert
            alerts.append(alert)
            self.analysis_stats["alerts_generated"] += 1
        
        # Pattern-specific alerts
        for pattern in patterns:
            if pattern.confidence >= 0.8:
                alert = ForensicsAlert(
                    id=f"alert_{int(time.time())}_{len(self.alerts)}",
                    event_type=ForensicsEventType.MONEY_LAUNDERING if pattern.pattern_type == "layering" else ForensicsEventType.MIXER_USAGE,
                    risk_level=RiskLevel.HIGH,
                    confidence=pattern.confidence,
                    description=f"{pattern.pattern_type.title()} pattern detected: {pattern.description}",
                    transaction_hashes=pattern.transactions,
                    addresses_involved=pattern.addresses,
                    evidence={"pattern": pattern.__dict__},
                    compliance_violations=[ComplianceStandard.AML, ComplianceStandard.FATF],
                    follow_up_required=True
                )
                
                self.alerts[alert.id] = alert
                alerts.append(alert)
                self.analysis_stats["alerts_generated"] += 1
                self.analysis_stats["patterns_detected"] += 1
        
        # Compliance violation alerts
        for violation in compliance_issues:
            if violation["severity"] in ["critical", "high"]:
                alert = ForensicsAlert(
                    id=f"alert_{int(time.time())}_{len(self.alerts)}",
                    event_type=ForensicsEventType.SUSPICIOUS_TRANSACTION,
                    risk_level=RiskLevel.CRITICAL if violation["severity"] == "critical" else RiskLevel.HIGH,
                    confidence=0.95,
                    description=f"Compliance violation: {violation['description']}",
                    transaction_hashes=[],
                    addresses_involved=[address],
                    evidence={"violation": violation},
                    compliance_violations=[ComplianceStandard(violation["standard"])],
                    follow_up_required=True
                )
                
                self.alerts[alert.id] = alert
                alerts.append(alert)
                self.analysis_stats["alerts_generated"] += 1
                self.analysis_stats["compliance_violations"] += 1
        
        return alerts
    
    async def _check_sanctions_list(self, address: str) -> bool:
        """Check if address is on sanctions list."""
        # Mock implementation
        sanctioned_patterns = ["0x123", "0x666", "0xdead"]
        return any(pattern in address.lower() for pattern in sanctioned_patterns)
    
    async def create_investigation_case(self, title: str, description: str, investigator: str,
                                       priority: RiskLevel = RiskLevel.MEDIUM) -> str:
        """Create new investigation case."""
        case_id = f"case_{int(time.time())}_{len(self.cases)}"
        
        case = InvestigationCase(
            case_id=case_id,
            title=title,
            description=description,
            investigator=investigator,
            status="open",
            priority=priority
        )
        
        self.cases[case_id] = case
        
        self.logger.info(f"Created investigation case: {case_id}")
        return case_id
    
    async def add_evidence_to_case(self, case_id: str, evidence_type: str, evidence_data: Dict[str, Any]) -> bool:
        """Add evidence to investigation case."""
        if case_id not in self.cases:
            return False
        
        case = self.cases[case_id]
        case.evidence[evidence_type] = evidence_data
        case.updated_at = datetime.now()
        
        # Add to timeline
        case.timeline.append({
            "timestamp": datetime.now().isoformat(),
            "action": "evidence_added",
            "type": evidence_type,
            "description": f"Added {evidence_type} evidence"
        })
        
        return True
    
    async def generate_investigation_report(self, case_id: str) -> Dict[str, Any]:
        """Generate comprehensive investigation report."""
        if case_id not in self.cases:
            raise ValueError("Case not found")
        
        case = self.cases[case_id]
        
        # Collect all related alerts
        case_alerts = [self.alerts[alert_id] for alert_id in case.alerts if alert_id in self.alerts]
        
        # Generate summary statistics
        total_addresses = len(set(
            addr for alert in case_alerts 
            for addr in alert.addresses_involved
        ))
        
        total_transactions = len(set(
            tx for alert in case_alerts 
            for tx in alert.transaction_hashes
        ))
        
        risk_levels = [alert.risk_level.value for alert in case_alerts]
        avg_risk = sum(risk_levels) / len(risk_levels) if risk_levels else 0
        
        report = {
            "case_id": case_id,
            "title": case.title,
            "investigator": case.investigator,
            "status": case.status,
            "priority": case.priority.value,
            "created_at": case.created_at.isoformat(),
            "updated_at": case.updated_at.isoformat(),
            "summary": {
                "total_alerts": len(case_alerts),
                "total_addresses": total_addresses,
                "total_transactions": total_transactions,
                "average_risk_level": avg_risk,
                "compliance_violations": len(set(
                    violation.value for alert in case_alerts 
                    for violation in alert.compliance_violations
                ))
            },
            "alerts": [alert.__dict__ for alert in case_alerts],
            "evidence": case.evidence,
            "timeline": case.timeline,
            "recommendations": await self._generate_recommendations(case, case_alerts),
            "next_steps": await self._suggest_next_steps(case, case_alerts)
        }
        
        return report
    
    async def _generate_recommendations(self, case: InvestigationCase, alerts: List[ForensicsAlert]) -> List[str]:
        """Generate investigation recommendations."""
        recommendations = []
        
        high_risk_alerts = [alert for alert in alerts if alert.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
        
        if high_risk_alerts:
            recommendations.append("Prioritize investigation of high-risk alerts")
            recommendations.append("Consider filing Suspicious Activity Report (SAR)")
        
        if any(ComplianceStandard.OFAC in alert.compliance_violations for alert in alerts):
            recommendations.append("Immediately freeze assets and contact compliance team")
            recommendations.append("Report to relevant authorities within required timeframe")
        
        pattern_types = set()
        for alert in alerts:
            if "pattern" in alert.evidence:
                pattern_types.add(alert.evidence["pattern"].get("pattern_type", ""))
        
        if "layering" in pattern_types:
            recommendations.append("Investigate upstream and downstream transaction flows")
            recommendations.append("Look for additional layering patterns in related addresses")
        
        if "mixer_usage" in pattern_types:
            recommendations.append("Enhanced due diligence required for mixer-related transactions")
            recommendations.append("Consider risk rating escalation")
        
        return recommendations
    
    async def _suggest_next_steps(self, case: InvestigationCase, alerts: List[ForensicsAlert]) -> List[str]:
        """Suggest next investigative steps."""
        next_steps = []
        
        if case.status == "open":
            next_steps.append("Review all evidence and assign severity levels")
            next_steps.append("Expand investigation to connected addresses")
        
        addresses_to_investigate = set()
        for alert in alerts:
            addresses_to_investigate.update(alert.addresses_involved)
        
        if len(addresses_to_investigate) > 5:
            next_steps.append("Prioritize address investigation based on risk scores")
        else:
            next_steps.append("Conduct deep investigation of all involved addresses")
        
        if any(alert.follow_up_required for alert in alerts):
            next_steps.append("Schedule follow-up analysis for flagged transactions")
        
        next_steps.append("Document findings and prepare preliminary report")
        next_steps.append("Coordinate with legal and compliance teams as needed")
        
        return next_steps
    
    async def get_forensics_statistics(self) -> Dict[str, Any]:
        """Get comprehensive forensics statistics."""
        stats = self.analysis_stats.copy()
        
        # Add current state statistics
        stats.update({
            "active_cases": len([case for case in self.cases.values() if case.status == "open"]),
            "total_cases": len(self.cases),
            "total_alerts": len(self.alerts),
            "high_risk_alerts": len([alert for alert in self.alerts.values() if alert.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]),
            "address_profiles": len(self.address_profiles),
            "known_addresses": len(self.known_addresses)
        })
        
        # Alert distribution by type
        alert_types = Counter(alert.event_type.value for alert in self.alerts.values())
        stats["alert_distribution"] = dict(alert_types)
        
        # Risk level distribution
        risk_levels = Counter(alert.risk_level.value for alert in self.alerts.values())
        stats["risk_distribution"] = dict(risk_levels)
        
        # Compliance violations by standard
        compliance_violations = Counter()
        for alert in self.alerts.values():
            for violation in alert.compliance_violations:
                compliance_violations[violation.value] += 1
        stats["compliance_violations_by_standard"] = dict(compliance_violations)
        
        return stats

# Global forensics engine
forensics_engine = BlockchainForensicsEngine()

async def initialize_blockchain_forensics(config: Optional[Dict] = None) -> bool:
    """Initialize the blockchain forensics engine."""
    global forensics_engine
    
    try:
        forensics_engine = BlockchainForensicsEngine(config)
        logging.info("Blockchain forensics engine initialized")
        return True
    except Exception as e:
        logging.error(f"Failed to initialize forensics engine: {e}")
        return False

if __name__ == "__main__":
    # Example usage and testing
    async def test_forensics():
        """Test blockchain forensics functionality."""
        print("Testing Blockchain Forensics...")
        
        # Initialize engine
        await initialize_blockchain_forensics()
        
        # Investigate suspicious address
        address = "0x1234567890abcdef1234567890abcdef12345678"
        results = await forensics_engine.investigate_address(address, depth=2)
        print(f"Investigation results: Risk score {results['risk_score']:.2f}")
        print(f"Anomalies detected: {len(results['anomalies'])}")
        print(f"Compliance issues: {len(results['compliance_issues'])}")
        print(f"Patterns found: {len(results['patterns'])}")
        
        # Create investigation case
        case_id = await forensics_engine.create_investigation_case(
            "Suspicious Transaction Investigation",
            "Investigation of high-risk address with potential money laundering indicators",
            "investigator_001",
            RiskLevel.HIGH
        )
        print(f"Created case: {case_id}")
        
        # Add evidence
        await forensics_engine.add_evidence_to_case(case_id, "address_analysis", results)
        
        # Generate report
        report = await forensics_engine.generate_investigation_report(case_id)
        print(f"Report generated with {len(report['recommendations'])} recommendations")
        
        # Get statistics
        stats = await forensics_engine.get_forensics_statistics()
        print(f"Forensics stats: {stats}")
    
    # Run test if executed directly
    asyncio.run(test_forensics())
