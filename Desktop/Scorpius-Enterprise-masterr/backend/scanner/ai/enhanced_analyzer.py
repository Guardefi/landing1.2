"""
Enhanced AI-Powered Vulnerability Analysis Engine
Integrates Claude AI with advanced pattern recognition and exploit prediction
"""

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
from core.models import Target, VulnerabilityFinding

logger = logging.getLogger("scorpius.ai.enhanced_analyzer")


@dataclass
class ExploitPrediction:
    """Advanced exploit prediction metrics"""

    exploit_probability: float  # 0-1 probability an exploit will be developed
    time_to_exploit: int  # Estimated days until exploit development
    weaponization_likelihood: float  # Probability of weaponization
    mass_exploitation_risk: float  # Risk of mass exploitation
    underground_market_value: float  # Estimated value in exploit markets

    # Attack characteristics
    attack_complexity: str  # low, medium, high
    required_privileges: str  # none, low, high
    user_interaction: bool
    attack_vector: str  # network, adjacent, local, physical

    # Defensive considerations
    detection_difficulty: float
    mitigation_complexity: float
    false_positive_rate: float


@dataclass
class RiskAssessment:
    """Comprehensive risk assessment for vulnerabilities"""

    overall_score: float  # 0-10 scale
    exploitability_score: float  # How easy to exploit
    impact_score: float  # Potential damage
    likelihood_score: float  # Probability of exploitation
    urgency_score: float  # How quickly it should be fixed
    business_risk_score: float  # Business impact

    # Financial impact metrics
    estimated_loss_min: float
    estimated_loss_max: float
    estimated_loss_avg: float

    # Contextual factors
    asset_criticality: float
    network_exposure: float
    data_sensitivity: float

    # Temporal factors
    vulnerability_age: int  # Days since discovery
    patch_availability: bool
    known_exploits: bool
    active_exploitation: bool


class EnhancedAIAnalyzer:
    """Enhanced AI-powered vulnerability analyzer using Claude AI"""

    def __init__(self, api_key: Optional[str] = None, config: Dict[str, Any] = None):
        """Initialize the enhanced AI analyzer"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-5-sonnet-20241022"  # Latest model
        self.max_tokens = 8000
        self.config = config or {}

        # Vulnerability pattern database
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        self.exploit_database = self._load_exploit_database()

        if not self.api_key:
            logger.warning(
                "No Anthropic API key provided - AI analysis will be disabled"
            )

    def _load_vulnerability_patterns(self) -> Dict[str, Any]:
        """Load known vulnerability patterns for pattern matching"""
        patterns = {
            "reentrancy": {
                "patterns": [
                    "external call before state update",
                    "call.value() without reentrancy guard",
                    "transfer() in payable function without mutex",
                    "delegatecall with untrusted callee",
                ],
                "risk_multiplier": 2.5,
                "common_exploits": ["DAO attack", "cross-function reentrancy"],
            },
            "flash_loan_attack": {
                "patterns": [
                    "price oracle manipulation",
                    "single block arbitrage",
                    "governance token flash loan",
                    "AMM price manipulation",
                ],
                "risk_multiplier": 2.0,
                "common_exploits": ["Cream Finance", "bZx protocol"],
            },
            "access_control": {
                "patterns": [
                    "missing onlyOwner modifier",
                    "unprotected initialization",
                    "role-based access without checks",
                    "proxy admin functions",
                ],
                "risk_multiplier": 1.8,
                "common_exploits": [
                    "admin key compromise",
                    "initialization frontrunning",
                ],
            },
            "arithmetic_overflow": {
                "patterns": [
                    "unchecked arithmetic operations",
                    "SafeMath not used",
                    "integer underflow in token calculations",
                    "multiplication before division",
                ],
                "risk_multiplier": 1.5,
                "common_exploits": ["BEC token overflow", "SMT integer overflow"],
            },
            "oracle_manipulation": {
                "patterns": [
                    "single price oracle source",
                    "spot price usage",
                    "no TWAP implementation",
                    "flash loan oracle manipulation",
                ],
                "risk_multiplier": 2.2,
                "common_exploits": ["Harvest Finance", "Value DeFi"],
            },
        }
        return patterns

    def _load_exploit_database(self) -> Dict[str, Any]:
        """Load historical exploit data for prediction"""
        return {
            "recent_exploits": [
                {"type": "flash_loan", "date": "2024-01", "loss": 50000000},
                {"type": "reentrancy", "date": "2024-02", "loss": 25000000},
                {"type": "oracle_manipulation", "date": "2024-03", "loss": 75000000},
            ],
            "exploit_trends": {
                "flash_loan": {"frequency": 0.15, "avg_loss": 35000000},
                "reentrancy": {"frequency": 0.10, "avg_loss": 20000000},
                "oracle_manipulation": {"frequency": 0.12, "avg_loss": 45000000},
            },
        }

    async def analyze_contract_comprehensive(
        self,
        contract_address: str,
        source_code: Optional[str] = None,
        bytecode: Optional[str] = None,
        transaction_history: Optional[List[Dict]] = None,
        target: Optional[Target] = None,
    ) -> Tuple[List[VulnerabilityFinding], RiskAssessment, ExploitPrediction]:
        """
        Comprehensive AI analysis with enhanced risk assessment and exploit prediction

        Args:
            contract_address: Contract address to analyze
            source_code: Contract source code (if available)
            bytecode: Contract bytecode
            transaction_history: Historical transaction data
            target: Target information

        Returns:
            Tuple of (vulnerabilities, risk_assessment, exploit_prediction)
        """
        logger.info(f"Starting comprehensive AI analysis for {contract_address}")

        # Step 1: Pattern-based vulnerability detection
        pattern_vulnerabilities = await self._detect_pattern_vulnerabilities(
            source_code, bytecode, contract_address
        )

        # Step 2: AI-powered deep analysis
        ai_vulnerabilities = await self._ai_deep_analysis(
            contract_address, source_code, bytecode, transaction_history
        )

        # Step 3: Combine and deduplicate findings
        all_vulnerabilities = self._merge_vulnerability_findings(
            pattern_vulnerabilities, ai_vulnerabilities
        )

        # Step 4: Generate risk assessment
        risk_assessment = await self._generate_risk_assessment(
            all_vulnerabilities, target, transaction_history
        )

        # Step 5: Predict exploit development
        exploit_prediction = await self._predict_exploit_development(
            all_vulnerabilities, risk_assessment
        )

        logger.info(
            f"Analysis complete: {
                len(all_vulnerabilities)} vulnerabilities found"
        )
        return all_vulnerabilities, risk_assessment, exploit_prediction

    async def _detect_pattern_vulnerabilities(
        self, source_code: Optional[str], bytecode: Optional[str], address: str
    ) -> List[VulnerabilityFinding]:
        """Detect vulnerabilities using pattern matching"""
        vulnerabilities = []

        if not source_code and not bytecode:
            return vulnerabilities

        code_to_analyze = source_code or bytecode or ""

        for vuln_type, pattern_data in self.vulnerability_patterns.items():
            for pattern in pattern_data["patterns"]:
                if pattern.lower() in code_to_analyze.lower():
                    vulnerability = VulnerabilityFinding(
                        id=f"pattern_{vuln_type}_{len(vulnerabilities)}",
                        title=f"Potential {
                            vuln_type.replace(
                                '_', ' ').title()} Vulnerability",
                        description=f"Pattern detected: {pattern}",
                        severity=self._calculate_pattern_severity(vuln_type),
                        confidence=0.7,  # Pattern matching confidence
                        category=vuln_type,
                        affected_functions=[],
                        risk_score=pattern_data["risk_multiplier"] * 3.0,
                        exploit_scenario=f"Potential {vuln_type} exploit based on pattern analysis",
                        remediation=f"Review and fix {vuln_type} vulnerability pattern",
                    )
                    vulnerabilities.append(vulnerability)

        return vulnerabilities

    def _calculate_pattern_severity(self, vuln_type: str) -> str:
        """Calculate severity based on vulnerability type"""
        severity_map = {
            "reentrancy": "Critical",
            "flash_loan_attack": "High",
            "access_control": "High",
            "arithmetic_overflow": "Medium",
            "oracle_manipulation": "High",
        }
        return severity_map.get(vuln_type, "Medium")

    async def _ai_deep_analysis(
        self,
        contract_address: str,
        source_code: Optional[str],
        bytecode: Optional[str],
        transaction_history: Optional[List[Dict]],
    ) -> List[VulnerabilityFinding]:
        """Perform deep AI analysis using Claude"""
        if not self.api_key:
            logger.warning("No API key available for AI analysis")
            return []

        # Prepare analysis prompt
        analysis_prompt = self._build_analysis_prompt(
            contract_address, source_code, bytecode, transaction_history
        )

        try:
            vulnerabilities = await self._query_claude_for_vulnerabilities(
                analysis_prompt
            )
            return vulnerabilities
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return []

    def _build_analysis_prompt(
        self,
        contract_address: str,
        source_code: Optional[str],
        bytecode: Optional[str],
        transaction_history: Optional[List[Dict]],
    ) -> str:
        """Build comprehensive analysis prompt for Claude"""
        prompt = f"""
        Analyze this smart contract for security vulnerabilities:

        Contract Address: {contract_address}

        Source Code:
        {source_code[:4000] if source_code else 'Not available'}

        Bytecode:
        {bytecode[:2000] if bytecode else 'Not available'}

        Transaction History Summary:
        {json.dumps(transaction_history[:10], indent=2) if transaction_history else 'Not available'}

        Please provide a comprehensive security analysis focusing on:
        1. Reentrancy vulnerabilities
        2. Access control issues
        3. Arithmetic overflow/underflow
        4. Flash loan attack vectors
        5. Oracle manipulation risks
        6. Logic flaws and edge cases
        7. Gas optimization attacks
        8. Front-running vulnerabilities

        For each vulnerability found, provide:
        - Vulnerability type and severity
        - Specific location in code
        - Exploit scenario
        - Potential impact
        - Remediation steps
        - Confidence level (0-1)

        Format your response as JSON with the following structure:
        {{
            "vulnerabilities": [
                {{
                    "id": "unique_id",
                    "title": "Vulnerability Title",
                    "description": "Detailed description",
                    "severity": "Critical|High|Medium|Low",
                    "confidence": 0.9,
                    "category": "vulnerability_type",
                    "affected_functions": ["function1", "function2"],
                    "exploit_scenario": "How this could be exploited",
                    "remediation": "How to fix this",
                    "risk_score": 8.5
                }}
            ]
        }}
        """
        return prompt

    async def _query_claude_for_vulnerabilities(
        self, prompt: str
    ) -> List[VulnerabilityFinding]:
        """Query Claude AI for vulnerability analysis"""
        headers = {
            "x-api-key": self.api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_url, headers=headers, json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return self._parse_claude_response(result)
                else:
                    logger.error(f"Claude API error: {response.status}")
                    return []

    def _parse_claude_response(
        self, response: Dict[str, Any]
    ) -> List[VulnerabilityFinding]:
        """Parse Claude's response into VulnerabilityFinding objects"""
        try:
            content = response["content"][0]["text"]

            # Extract JSON from the response
            start_idx = content.find("{")
            end_idx = content.rfind("}") + 1
            json_str = content[start_idx:end_idx]

            data = json.loads(json_str)
            vulnerabilities = []

            for vuln_data in data.get("vulnerabilities", []):
                vulnerability = VulnerabilityFinding(
                    id=vuln_data.get("id", f"ai_vuln_{len(vulnerabilities)}"),
                    title=vuln_data.get("title", "Unknown Vulnerability"),
                    description=vuln_data.get("description", ""),
                    severity=vuln_data.get("severity", "Medium"),
                    confidence=vuln_data.get("confidence", 0.5),
                    category=vuln_data.get("category", "unknown"),
                    affected_functions=vuln_data.get("affected_functions", []),
                    risk_score=vuln_data.get("risk_score", 5.0),
                    exploit_scenario=vuln_data.get("exploit_scenario", ""),
                    remediation=vuln_data.get("remediation", ""),
                )
                vulnerabilities.append(vulnerability)

            return vulnerabilities

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse Claude response: {e}")
            return []

    def _merge_vulnerability_findings(
        self,
        pattern_vulns: List[VulnerabilityFinding],
        ai_vulns: List[VulnerabilityFinding],
    ) -> List[VulnerabilityFinding]:
        """Merge and deduplicate vulnerability findings"""
        all_vulns = pattern_vulns + ai_vulns

        # Simple deduplication based on title similarity
        unique_vulns = []
        seen_titles = set()

        for vuln in all_vulns:
            title_key = vuln.title.lower().replace(" ", "_")
            if title_key not in seen_titles:
                unique_vulns.append(vuln)
                seen_titles.add(title_key)

        return unique_vulns

    async def _generate_risk_assessment(
        self,
        vulnerabilities: List[VulnerabilityFinding],
        target: Optional[Target],
        transaction_history: Optional[List[Dict]],
    ) -> RiskAssessment:
        """Generate comprehensive risk assessment"""

        # Calculate base scores
        severity_weights = {"Critical": 10, "High": 7, "Medium": 4, "Low": 2}
        total_score = sum(severity_weights.get(v.severity, 2) for v in vulnerabilities)
        avg_confidence = (
            sum(v.confidence for v in vulnerabilities) / len(vulnerabilities)
            if vulnerabilities
            else 0
        )

        # Calculate financial impact estimates
        base_loss = 100000  # Base loss estimate
        loss_multiplier = 1 + (total_score / 10)
        estimated_loss_min = base_loss * loss_multiplier * 0.5
        estimated_loss_max = base_loss * loss_multiplier * 5.0
        estimated_loss_avg = base_loss * loss_multiplier * 2.0

        return RiskAssessment(
            overall_score=min(
                total_score / len(vulnerabilities) if vulnerabilities else 0, 10
            ),
            exploitability_score=avg_confidence * 10,
            impact_score=total_score / 2,
            likelihood_score=self._calculate_likelihood_score(vulnerabilities),
            urgency_score=self._calculate_urgency_score(vulnerabilities),
            business_risk_score=self._calculate_business_risk(vulnerabilities, target),
            estimated_loss_min=estimated_loss_min,
            estimated_loss_max=estimated_loss_max,
            estimated_loss_avg=estimated_loss_avg,
            asset_criticality=8.0,  # Default high criticality
            network_exposure=7.0,
            data_sensitivity=6.0,
            vulnerability_age=0,  # New scan
            patch_availability=False,
            known_exploits=any(
                "exploit" in v.description.lower() for v in vulnerabilities
            ),
            active_exploitation=False,
        )

    def _calculate_likelihood_score(
        self, vulnerabilities: List[VulnerabilityFinding]
    ) -> float:
        """Calculate likelihood of exploitation"""
        if not vulnerabilities:
            return 0.0

        # Base likelihood on vulnerability types and historical data
        likelihood = 0.0
        for vuln in vulnerabilities:
            vuln_type = vuln.category.lower()
            if vuln_type in self.exploit_database["exploit_trends"]:
                likelihood += self.exploit_database["exploit_trends"][vuln_type][
                    "frequency"
                ]

        return min(likelihood / len(vulnerabilities) * 10, 10.0)

    def _calculate_urgency_score(
        self, vulnerabilities: List[VulnerabilityFinding]
    ) -> float:
        """Calculate urgency score based on severity and exploitability"""
        if not vulnerabilities:
            return 0.0

        severity_urgency = {"Critical": 10, "High": 8, "Medium": 5, "Low": 2}
        urgency_scores = [severity_urgency.get(v.severity, 2) for v in vulnerabilities]
        return sum(urgency_scores) / len(urgency_scores)

    def _calculate_business_risk(
        self, vulnerabilities: List[VulnerabilityFinding], target: Optional[Target]
    ) -> float:
        """Calculate business risk score"""
        base_risk = 5.0

        # Increase risk for critical vulnerabilities
        critical_count = sum(1 for v in vulnerabilities if v.severity == "Critical")
        high_count = sum(1 for v in vulnerabilities if v.severity == "High")

        risk_adjustment = (critical_count * 2) + (high_count * 1.5)
        return min(base_risk + risk_adjustment, 10.0)

    async def _predict_exploit_development(
        self,
        vulnerabilities: List[VulnerabilityFinding],
        risk_assessment: RiskAssessment,
    ) -> ExploitPrediction:
        """Predict likelihood and timeline of exploit development"""

        # Base exploit probability on vulnerability severity and type
        exploit_prob = 0.0
        weaponization_likelihood = 0.0

        for vuln in vulnerabilities:
            if vuln.severity == "Critical":
                exploit_prob += 0.8
                weaponization_likelihood += 0.7
            elif vuln.severity == "High":
                exploit_prob += 0.6
                weaponization_likelihood += 0.5
            elif vuln.severity == "Medium":
                exploit_prob += 0.3
                weaponization_likelihood += 0.2

        # Normalize probabilities
        exploit_prob = min(
            exploit_prob / len(vulnerabilities) if vulnerabilities else 0, 1.0
        )
        weaponization_likelihood = min(
            weaponization_likelihood / len(vulnerabilities) if vulnerabilities else 0,
            1.0,
        )

        # Estimate time to exploit development
        time_to_exploit = max(30 - (risk_assessment.overall_score * 3), 1)

        return ExploitPrediction(
            exploit_probability=exploit_prob,
            time_to_exploit=int(time_to_exploit),
            weaponization_likelihood=weaponization_likelihood,
            mass_exploitation_risk=exploit_prob * 0.7,
            underground_market_value=risk_assessment.estimated_loss_avg * 0.1,
            attack_complexity="medium",
            required_privileges="none",
            user_interaction=False,
            attack_vector="network",
            detection_difficulty=0.6,
            mitigation_complexity=0.7,
            false_positive_rate=0.1,
        )
