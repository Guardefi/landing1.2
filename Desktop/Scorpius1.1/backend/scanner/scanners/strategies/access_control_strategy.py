"""
Access Control Vulnerability Detection Strategy
Detects missing or improper access control mechanisms
"""

import re
from typing import Any, Dict, List, Optional

from core.models import VulnerabilityFinding

from .base import BaseStrategy, StrategyContext


class AccessControlStrategy(BaseStrategy):
    """Strategy for detecting access control vulnerabilities"""

    def __init__(self):
        super().__init__(
            name="access_control",
            description="Detects missing or insufficient access control on sensitive functions",
        )

        # Sensitive function patterns
        self.sensitive_patterns = [
            r"function\s+(\w*withdraw\w*)\s*\(",  # Withdrawal functions
            r"function\s+(\w*transfer\w*)\s*\(",  # Transfer functions
            r"function\s+(\w*mint\w*)\s*\(",  # Minting functions
            r"function\s+(\w*burn\w*)\s*\(",  # Burning functions
            r"function\s+(\w*admin\w*)\s*\(",  # Admin functions
            r"function\s+(\w*owner\w*)\s*\(",  # Owner functions
            r"function\s+(\w*pause\w*)\s*\(",  # Pause functions
            r"function\s+(\w*emergency\w*)\s*\(",  # Emergency functions
            r"function\s+(\w*upgrade\w*)\s*\(",  # Upgrade functions
            r"function\s+(\w*initialize\w*)\s*\(",  # Initialize functions
        ]

        # Access control modifiers
        self.access_control_modifiers = [
            r"onlyOwner",
            r"onlyAdmin",
            r"onlyRole",
            r"requireRole",
            r"hasRole",
            r"authorized",
            r"restricted",
            r"onlyGovernance",
            r"onlyManager",
        ]

        # Dangerous state changing patterns
        self.state_change_patterns = [
            r"balances\[[^\]]+\]\s*=",
            r"\.transfer\s*\(",
            r"\.transferFrom\s*\(",
            r"selfdestruct\s*\(",
            r"suicide\s*\(",
            r"delegatecall\s*\(",
        ]

    async def analyze(self, context: StrategyContext) -> List[VulnerabilityFinding]:
        """Analyze for access control vulnerabilities"""
        findings = []

        if not context.source_code:
            self.logger.warning("No source code available for access control analysis")
            return findings

        # Find unprotected sensitive functions
        unprotected_findings = await self._find_unprotected_functions(context)
        findings.extend(unprotected_findings)

        # Check for initialization vulnerabilities
        init_findings = await self._check_initialization_vulnerabilities(context)
        findings.extend(init_findings)

        # Check for role-based access control issues
        rbac_findings = await self._check_rbac_vulnerabilities(context)
        findings.extend(rbac_findings)

        return findings

    async def _find_unprotected_functions(
        self, context: StrategyContext
    ) -> List[VulnerabilityFinding]:
        """Find sensitive functions without proper access control"""
        findings = []
        source_code = context.source_code

        for pattern in self.sensitive_patterns:
            matches = re.finditer(pattern, source_code, re.IGNORECASE | re.DOTALL)

            for match in matches:
                func_name = match.group(1)

                # Extract the full function
                func_start = match.start()
                func_content = self._extract_function_content(source_code, func_start)

                if func_content:
                    # Check if function has access control
                    has_access_control = self._has_access_control(func_content)

                    if not has_access_control:
                        severity = self._determine_severity(func_name, func_content)

                        finding = self.create_finding(
                            title=f"Missing Access Control in {func_name}",
                            description=f"Function {func_name} performs sensitive operations without "
                            f"proper access control mechanisms. This could allow unauthorized "
                            f"users to execute privileged operations.",
                            severity=severity,
                            confidence=0.9,
                            affected_functions=[func_name],
                            exploit_scenario=self._generate_access_control_exploit(
                                func_name
                            ),
                            remediation=self._generate_access_control_remediation(
                                func_name
                            ),
                        )
                        findings.append(finding)

        return findings

    async def _check_initialization_vulnerabilities(
        self, context: StrategyContext
    ) -> List[VulnerabilityFinding]:
        """Check for initialization function vulnerabilities"""
        findings = []
        source_code = context.source_code

        # Find initialization functions
        init_pattern = (
            r"function\s+(initialize|init|setup)\s*\([^)]*\)\s*([^{]*)\s*\{([^}]+)\}"
        )

        for match in re.finditer(init_pattern, source_code, re.IGNORECASE | re.DOTALL):
            func_name = match.group(1)
            func_modifiers = match.group(2)
            func_body = match.group(3)

            vulnerability_issues = []

            # Check if function can be called multiple times
            if not re.search(
                r"initialized|_initialized|initializer", func_body, re.IGNORECASE
            ):
                vulnerability_issues.append("Function can be called multiple times")

            # Check if function has access control
            if not self._has_access_control(func_modifiers + func_body):
                vulnerability_issues.append("No access control protection")

            # Check for sensitive operations in initialization
            if any(
                re.search(pattern, func_body, re.IGNORECASE)
                for pattern in self.state_change_patterns
            ):
                vulnerability_issues.append("Performs sensitive state changes")

            if vulnerability_issues:
                finding = self.create_finding(
                    title=f"Vulnerable Initialization Function {func_name}",
                    description=f"Initialization function {func_name} has vulnerabilities: "
                    f"{'; '.join(vulnerability_issues)}. This could allow attackers "
                    f"to reinitialize the contract or front-run initialization.",
                    severity="High",
                    confidence=0.8,
                    affected_functions=[func_name],
                    exploit_scenario=self._generate_init_exploit(
                        func_name, vulnerability_issues
                    ),
                    remediation="Add proper initialization guards and access control",
                )
                findings.append(finding)

        return findings

    async def _check_rbac_vulnerabilities(
        self, context: StrategyContext
    ) -> List[VulnerabilityFinding]:
        """Check for role-based access control vulnerabilities"""
        findings = []
        source_code = context.source_code

        # Check for role assignment functions without proper protection
        role_assignment_pattern = (
            r"function\s+(\w*grant\w*|\w*assign\w*|\w*add\w*)\s*\([^)]*role[^)]*\)"
        )

        for match in re.finditer(role_assignment_pattern, source_code, re.IGNORECASE):
            func_name = match.group(1)
            func_start = match.start()
            func_content = self._extract_function_content(source_code, func_start)

            if func_content and not self._has_access_control(func_content):
                finding = self.create_finding(
                    title=f"Unprotected Role Assignment in {func_name}",
                    description=f"Function {func_name} can assign roles without proper access control. "
                    f"This could allow unauthorized privilege escalation.",
                    severity="Critical",
                    confidence=0.85,
                    affected_functions=[func_name],
                    exploit_scenario=f"Attacker calls {func_name} to grant themselves admin privileges",
                    remediation="Add proper access control to role assignment functions",
                )
                findings.append(finding)

        return findings

    def _extract_function_content(
        self, source_code: str, start_pos: int
    ) -> Optional[str]:
        """Extract the full content of a function starting from a position"""
        try:
            # Find the opening brace
            brace_pos = source_code.find("{", start_pos)
            if brace_pos == -1:
                return None

            # Count braces to find the closing brace
            brace_count = 1
            pos = brace_pos + 1

            while pos < len(source_code) and brace_count > 0:
                if source_code[pos] == "{":
                    brace_count += 1
                elif source_code[pos] == "}":
                    brace_count -= 1
                pos += 1

            if brace_count == 0:
                return source_code[start_pos:pos]

        except Exception as e:
            self.logger.debug(f"Error extracting function content: {e}")

        return None

    def _has_access_control(self, func_content: str) -> bool:
        """Check if function content has access control mechanisms"""
        for modifier in self.access_control_modifiers:
            if re.search(modifier, func_content, re.IGNORECASE):
                return True

        # Check for require statements with access control
        require_patterns = [
            r"require\s*\(\s*msg\.sender\s*==\s*owner",
            r"require\s*\(\s*hasRole\s*\(",
            r"require\s*\(\s*isAdmin\s*\(",
            r"require\s*\(\s*authorized\s*\(",
            r"require\s*\(\s*_msgSender\s*\(\s*\)\s*==\s*owner",
        ]

        for pattern in require_patterns:
            if re.search(pattern, func_content, re.IGNORECASE):
                return True

        return False

    def _determine_severity(self, func_name: str, func_content: str) -> str:
        """Determine severity based on function name and content"""
        func_name_lower = func_name.lower()
        func_content_lower = func_content.lower()

        # Critical functions
        if any(
            keyword in func_name_lower
            for keyword in ["withdraw", "transfer", "mint", "burn", "selfdestruct"]
        ):
            return "Critical"

        # High risk functions
        if any(
            keyword in func_name_lower
            for keyword in ["admin", "owner", "emergency", "pause", "upgrade"]
        ):
            return "High"

        # Check for dangerous operations in content
        if any(
            keyword in func_content_lower
            for keyword in ["selfdestruct", "delegatecall", "suicide"]
        ):
            return "Critical"

        return "Medium"

    def _generate_access_control_exploit(self, func_name: str) -> str:
        """Generate exploit scenario for access control vulnerability"""
        return f"""
        Access Control Exploit for {func_name}:
        1. Attacker identifies the unprotected function {func_name}
        2. Attacker calls the function directly without authorization
        3. Function executes privileged operations on behalf of attacker
        4. Attacker gains unauthorized access to sensitive functionality
        5. Potential outcomes: fund theft, privilege escalation, contract manipulation
        """

    def _generate_access_control_remediation(self, func_name: str) -> str:
        """Generate remediation advice for access control vulnerability"""
        return f"""
        Access Control Remediation for {func_name}:
        1. Add appropriate access control modifier (onlyOwner, onlyAdmin, etc.)
        2. Use OpenZeppelin's AccessControl or Ownable contracts
        3. Implement role-based access control for multiple privilege levels
        4. Add require statements to validate caller permissions
        5. Consider using multi-signature wallets for critical functions
        6. Implement time delays for sensitive operations
        7. Test access control thoroughly with different user roles
        """

    def _generate_init_exploit(self, func_name: str, issues: List[str]) -> str:
        """Generate exploit scenario for initialization vulnerability"""
        return f"""
        Initialization Exploit for {func_name}:
        1. Attacker identifies initialization vulnerability: {'; '.join(issues)}
        2. If no access control: Attacker calls {func_name} directly
        3. If multiple calls possible: Attacker calls function repeatedly
        4. If front-running possible: Attacker front-runs legitimate initialization
        5. Attacker gains control over contract initialization parameters
        6. Contract state is compromised from the start
        """
