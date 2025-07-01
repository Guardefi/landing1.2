"""
Base Strategy Class for Vulnerability Detection
Provides common interface for all vulnerability detection strategies
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from core.models import Target, VulnerabilityFinding


@dataclass
class StrategyContext:
    """Context information for vulnerability strategies"""

    target: Target
    source_code: Optional[str] = None
    bytecode: Optional[str] = None
    transaction_history: Optional[List[Dict[str, Any]]] = None
    simulation_engine: Optional[Any] = None
    web3_provider: Optional[Any] = None
    block_number: Optional[int] = None


class BaseStrategy(ABC):
    """Base class for all vulnerability detection strategies"""

    def __init__(self, name: str, description: str):
        """Initialize the strategy"""
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"scorpius.strategy.{name}")
        self.enabled = True
        self.timeout = 300  # 5 minutes default timeout

    @abstractmethod
    async def analyze(self, context: StrategyContext) -> List[VulnerabilityFinding]:
        """
        Analyze the target for vulnerabilities

        Args:
            context: Strategy context with target and analysis data

        Returns:
            List of vulnerability findings
        """

    async def run_with_timeout(
        self, context: StrategyContext
    ) -> List[VulnerabilityFinding]:
        """Run the strategy with timeout protection"""
        try:
            return await asyncio.wait_for(self.analyze(context), timeout=self.timeout)
        except asyncio.TimeoutError:
            self.logger.warning(
                f"Strategy {self.name} timed out after {self.timeout} seconds"
            )
            return []
        except Exception as e:
            self.logger.error(f"Strategy {self.name} failed with error: {e}")
            return []

    def create_finding(
        self,
        title: str,
        description: str,
        severity: str,
        confidence: float = 0.8,
        category: Optional[str] = None,
        affected_functions: Optional[List[str]] = None,
        exploit_scenario: Optional[str] = None,
        remediation: Optional[str] = None,
        risk_score: Optional[float] = None,
    ) -> VulnerabilityFinding:
        """Helper method to create vulnerability findings"""
        # Convert string severity to VulnerabilityLevel enum
        from core.models import VulnerabilityLevel

        severity_map = {
            "Critical": VulnerabilityLevel.CRITICAL,
            "High": VulnerabilityLevel.HIGH,
            "Medium": VulnerabilityLevel.MEDIUM,
            "Low": VulnerabilityLevel.LOW,
            "Info": VulnerabilityLevel.INFO,
        }

        severity_enum = severity_map.get(severity, VulnerabilityLevel.MEDIUM)

        return VulnerabilityFinding(
            vulnerability_type=category or self.name,
            title=title,
            description=description,
            severity=severity_enum,
            confidence=confidence,
            location="contract",  # Default location
            source=self.name,
            recommendation=remediation or "",
            exploit_scenario=exploit_scenario or "",
            metadata={
                "risk_score": risk_score
                or self._calculate_risk_score(severity, confidence),
                "affected_functions": affected_functions or [],
            },
        )

    def _calculate_risk_score(self, severity: str, confidence: float) -> float:
        """Calculate risk score based on severity and confidence"""
        severity_scores = {
            "Critical": 9.0,
            "High": 7.0,
            "Medium": 5.0,
            "Low": 3.0,
            "Info": 1.0,
        }
        base_score = severity_scores.get(severity, 5.0)
        return base_score * confidence

    def is_enabled(self) -> bool:
        """Check if the strategy is enabled"""
        return self.enabled

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the strategy"""
        self.enabled = enabled

    def set_timeout(self, timeout: int) -> None:
        """Set the strategy timeout"""
        self.timeout = timeout
