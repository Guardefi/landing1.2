"""
Flash Loan Attack Detection Strategy
Detects vulnerabilities to flash loan-based price manipulation and arbitrage attacks
"""

import re
from typing import Any, Dict, List, Optional

from core.models import VulnerabilityFinding

from .base import BaseStrategy, StrategyContext


class FlashLoanAttackStrategy(BaseStrategy):
    """Strategy for detecting flash loan attack vulnerabilities"""

    def __init__(self):
        super().__init__(
            name="flash_loan_attack",
            description="Detects vulnerabilities to flash loan attacks and price manipulations",
        )

        # Price oracle vulnerability patterns
        self.oracle_patterns = [
            r"\.getPrice\s*\(",  # Price queries
            r"\.latestAnswer\s*\(",  # Chainlink price feeds
            r"\.getReserves\s*\(",  # Uniswap reserves
            r"reserveToken0|reserveToken1",  # Direct reserve access
            r"balanceOf\s*\([^)]*\)\s*/\s*balanceOf",  # Balance ratio calculations
            r"token0\.balanceOf|token1\.balanceOf",  # Direct token balance queries
        ]

        # Flash loan vulnerable patterns
        self.flash_loan_patterns = [
            r"flashLoan\s*\(",  # Flash loan calls
            r"borrow\s*\(",  # Borrowing mechanisms
            r"swap\s*\(",  # DEX swaps
            r"price\s*\*\s*amount",  # Price calculations
            r"amountOut\s*=.*getAmountOut",  # AMM calculations
        ]

        # Vulnerable DeFi patterns
        self.defi_patterns = [
            r"liquidate\s*\(",  # Liquidation functions
            r"mint\s*\(",  # Minting functions
            r"redeem\s*\(",  # Redemption functions
            r"compound|aave|uniswap|sushiswap",  # DeFi protocol references
            r"governance|vote|proposal",  # Governance mechanisms
        ]

        # Protection mechanisms
        self.protection_patterns = [
            r"TWAP|timeWeighted",  # Time-weighted average price
            r"priceOracle.*require",  # Price validation
            r"slippage.*protection",  # Slippage protection
            r"maxPriceDeviation",  # Price deviation limits
            r"cooldown|timelock",  # Time delays
        ]

    async def analyze(self, context: StrategyContext) -> List[VulnerabilityFinding]:
        """Analyze for flash loan attack vulnerabilities"""
        findings = []

        if not context.source_code:
            self.logger.warning("No source code available for flash loan analysis")
            return findings

        # Analyze price oracle vulnerabilities
        oracle_findings = await self._analyze_price_oracles(context)
        findings.extend(oracle_findings)

        # Analyze flash loan vulnerable functions
        flash_loan_findings = await self._analyze_flash_loan_vulnerabilities(context)
        findings.extend(flash_loan_findings)

        # Analyze DeFi protocol vulnerabilities
        defi_findings = await self._analyze_defi_vulnerabilities(context)
        findings.extend(defi_findings)

        return findings

    async def _analyze_price_oracles(
        self, context: StrategyContext
    ) -> List[VulnerabilityFinding]:
        """Analyze price oracle manipulation vulnerabilities"""
        findings = []
        source_code = context.source_code

        # Find functions that use price oracles
        oracle_functions = self._find_functions_with_patterns(
            source_code, self.oracle_patterns
        )

        for func_info in oracle_functions:
            vulnerability = await self._analyze_oracle_function(func_info, source_code)
            if vulnerability:
                findings.append(vulnerability)

        return findings

    async def _analyze_flash_loan_vulnerabilities(
        self, context: StrategyContext
    ) -> List[VulnerabilityFinding]:
        """Analyze flash loan specific vulnerabilities"""
        findings = []
        source_code = context.source_code

        # Check for flash loan integration without proper protection
        has_flash_loan = any(
            re.search(pattern, source_code, re.IGNORECASE)
            for pattern in self.flash_loan_patterns
        )

        if has_flash_loan:
            # Check for protection mechanisms
            has_protection = any(
                re.search(pattern, source_code, re.IGNORECASE)
                for pattern in self.protection_patterns
            )

            if not has_protection:
                finding = self.create_finding(
                    title="Unprotected Flash Loan Integration",
                    description="Contract integrates flash loans without adequate protection mechanisms. "
                    "This could allow attackers to manipulate prices or exploit economic vulnerabilities.",
                    severity="High",
                    confidence=0.8,
                    exploit_scenario=self._generate_flash_loan_exploit_scenario(),
                    remediation=self._generate_flash_loan_remediation(),
                )
                findings.append(finding)

        return findings

    async def _analyze_defi_vulnerabilities(
        self, context: StrategyContext
    ) -> List[VulnerabilityFinding]:
        """Analyze DeFi-specific vulnerabilities"""
        findings = []
        source_code = context.source_code

        # Look for governance vulnerabilities
        governance_findings = await self._analyze_governance_vulnerabilities(
            source_code
        )
        findings.extend(governance_findings)

        # Look for liquidation vulnerabilities
        liquidation_findings = await self._analyze_liquidation_vulnerabilities(
            source_code
        )
        findings.extend(liquidation_findings)

        return findings

    def _find_functions_with_patterns(
        self, source_code: str, patterns: List[str]
    ) -> List[Dict[str, Any]]:
        """Find functions containing specific patterns"""
        functions = []

        # Find function definitions
        function_pattern = r"function\s+(\w+)\s*\([^)]*\)\s*([^{]*)\s*\{([^}]+)\}"

        for match in re.finditer(function_pattern, source_code, re.DOTALL):
            func_name = match.group(1)
            func_modifiers = match.group(2)
            func_body = match.group(3)

            # Check if function contains any of the patterns
            has_pattern = any(
                re.search(pattern, func_body, re.IGNORECASE) for pattern in patterns
            )

            if has_pattern:
                functions.append(
                    {
                        "name": func_name,
                        "modifiers": func_modifiers,
                        "body": func_body,
                        "full_match": match.group(0),
                        "start_pos": match.start(),
                        "end_pos": match.end(),
                    }
                )

        return functions

    async def _analyze_oracle_function(
        self, func_info: Dict[str, Any], source_code: str
    ) -> Optional[VulnerabilityFinding]:
        """Analyze a function for oracle manipulation vulnerabilities"""
        func_body = func_info["body"]
        func_name = func_info["name"]

        vulnerability_score = 0
        vulnerability_details = []

        # Check for direct price queries without TWAP
        if re.search(r"\.getPrice\s*\(|\.latestAnswer\s*\(", func_body, re.IGNORECASE):
            if not re.search(r"TWAP|timeWeighted|average", func_body, re.IGNORECASE):
                vulnerability_score += 2
                vulnerability_details.append(
                    "Uses spot price without time-weighted average"
                )

        # Check for direct reserve access
        if re.search(r"\.getReserves\s*\(|reserveToken", func_body, re.IGNORECASE):
            vulnerability_score += 1
            vulnerability_details.append("Accesses AMM reserves directly")

        # Check for balance-based price calculations
        if re.search(r"balanceOf.*balanceOf", func_body, re.IGNORECASE):
            vulnerability_score += 2
            vulnerability_details.append("Calculates prices based on token balances")

        # Check for lack of price validation
        if not re.search(
            r"require.*price|assert.*price|price.*require", func_body, re.IGNORECASE
        ):
            vulnerability_score += 1
            vulnerability_details.append("No price validation mechanisms")

        if vulnerability_score > 0:
            severity = "Critical" if vulnerability_score >= 3 else "High"
            confidence = min(0.9, 0.4 + (vulnerability_score * 0.15))

            return self.create_finding(
                title=f"Price Oracle Manipulation in {func_name}",
                description=f"Function {func_name} is vulnerable to price oracle manipulation attacks. "
                + f"Vulnerability indicators: {'; '.join(vulnerability_details)}",
                severity=severity,
                confidence=confidence,
                affected_functions=[func_name],
                exploit_scenario=self._generate_oracle_exploit_scenario(func_name),
                remediation=self._generate_oracle_remediation(func_name),
            )

        return None

    async def _analyze_governance_vulnerabilities(
        self, source_code: str
    ) -> List[VulnerabilityFinding]:
        """Analyze governance-related vulnerabilities"""
        findings = []

        # Check for governance functions
        governance_pattern = r"function\s+(\w*(?:vote|proposal|govern)\w*)\s*\([^)]*\)\s*([^{]*)\s*\{([^}]+)\}"

        for match in re.finditer(
            governance_pattern, source_code, re.IGNORECASE | re.DOTALL
        ):
            func_name = match.group(1)
            func_body = match.group(3)

            # Check for flash loan governance attacks
            if re.search(r"balanceOf|getVotes", func_body, re.IGNORECASE):
                finding = self.create_finding(
                    title=f"Flash Loan Governance Attack in {func_name}",
                    description=f"Governance function {func_name} may be vulnerable to flash loan attacks "
                    "where attackers can temporarily acquire voting power to manipulate decisions.",
                    severity="High",
                    confidence=0.7,
                    affected_functions=[func_name],
                    exploit_scenario=self._generate_governance_exploit_scenario(
                        func_name
                    ),
                    remediation="Implement time delays, snapshot voting, or minimum holding periods",
                )
                findings.append(finding)

        return findings

    async def _analyze_liquidation_vulnerabilities(
        self, source_code: str
    ) -> List[VulnerabilityFinding]:
        """Analyze liquidation-related vulnerabilities"""
        findings = []

        # Check for liquidation functions
        liquidation_pattern = (
            r"function\s+(\w*liquidat\w*)\s*\([^)]*\)\s*([^{]*)\s*\{([^}]+)\}"
        )

        for match in re.finditer(
            liquidation_pattern, source_code, re.IGNORECASE | re.DOTALL
        ):
            func_name = match.group(1)
            func_body = match.group(3)

            # Check for price-based liquidation without protection
            if re.search(r"price|getPrice|oracle", func_body, re.IGNORECASE):
                if not re.search(r"TWAP|delay|protection", func_body, re.IGNORECASE):
                    finding = self.create_finding(
                        title=f"Flash Loan Liquidation Attack in {func_name}",
                        description=f"Liquidation function {func_name} uses price oracles that could be "
                        "manipulated via flash loans to trigger unfair liquidations.",
                        severity="High",
                        confidence=0.8,
                        affected_functions=[func_name],
                        exploit_scenario=self._generate_liquidation_exploit_scenario(
                            func_name
                        ),
                        remediation="Use time-weighted prices and implement liquidation delays",
                    )
                    findings.append(finding)

        return findings

    def _generate_flash_loan_exploit_scenario(self) -> str:
        """Generate flash loan exploit scenario"""
        return """
        Flash Loan Attack Scenario:
        1. Attacker takes a large flash loan from a lending protocol
        2. Uses borrowed funds to manipulate AMM prices by making large swaps
        3. Exploits the manipulated prices in the target contract
        4. Extracts profit and repays the flash loan
        5. Keeps the remaining profit from the price manipulation
        
        This attack can drain funds, manipulate governance, or cause unfair liquidations.
        """

    def _generate_oracle_exploit_scenario(self, func_name: str) -> str:
        """Generate oracle manipulation exploit scenario"""
        return f"""
        Oracle Manipulation Attack on {func_name}:
        1. Attacker identifies price oracle dependency in {func_name}
        2. Takes flash loan to manipulate the underlying price source
        3. Calls {func_name} while prices are manipulated
        4. Extracts value based on manipulated prices
        5. Restores original prices and repays flash loan
        
        This can lead to arbitrary value extraction or protocol manipulation.
        """

    def _generate_governance_exploit_scenario(self, func_name: str) -> str:
        """Generate governance attack scenario"""
        return f"""
        Flash Loan Governance Attack on {func_name}:
        1. Attacker flash loans governance tokens or underlying assets
        2. Temporarily gains significant voting power
        3. Uses {func_name} to pass malicious proposals or votes
        4. Executes the proposal before repaying the flash loan
        5. Profits from the governance manipulation
        
        This can compromise protocol governance and fund security.
        """

    def _generate_liquidation_exploit_scenario(self, func_name: str) -> str:
        """Generate liquidation attack scenario"""
        return f"""
        Flash Loan Liquidation Attack on {func_name}:
        1. Attacker identifies positions near liquidation threshold
        2. Flash loans large amounts to manipulate asset prices
        3. Triggers {func_name} with manipulated prices
        4. Liquidates positions at unfavorable rates
        5. Restores prices and repays loan, keeping liquidation profits
        
        This can cause unfair liquidations and user fund loss.
        """

    def _generate_flash_loan_remediation(self) -> str:
        """Generate flash loan protection remediation"""
        return """
        Flash Loan Protection Measures:
        1. Implement time-weighted average prices (TWAP) instead of spot prices
        2. Add price deviation limits and validation
        3. Use multiple oracle sources for price verification
        4. Implement transaction delays for sensitive operations
        5. Add slippage protection mechanisms
        6. Consider using Chainlink or other secure oracle networks
        7. Implement reentrancy guards for critical functions
        """

    def _generate_oracle_remediation(self, func_name: str) -> str:
        """Generate oracle protection remediation"""
        return f"""
        Oracle Protection for {func_name}:
        1. Replace spot price queries with TWAP implementations
        2. Add price freshness checks and staleness protection
        3. Implement circuit breakers for large price movements
        4. Use multiple oracle sources and take median/average
        5. Add admin controls for emergency price overrides
        6. Implement gradual price updates instead of instant changes
        7. Consider using decentralized oracle networks
        """
