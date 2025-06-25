"""
Arithmetic Overflow/Underflow Detection Strategy
Detects integer overflow and underflow vulnerabilities
"""

import re
from typing import List, Optional

from .base import BaseStrategy, StrategyContext
from core.models import VulnerabilityFinding


class ArithmeticOverflowStrategy(BaseStrategy):
    """Strategy for detecting arithmetic overflow/underflow vulnerabilities"""
    
    def __init__(self):
        super().__init__(
            name="arithmetic_overflow",
            description="Detects integer overflow and underflow vulnerabilities"
        )
        
        # Unsafe arithmetic patterns
        self.unsafe_arithmetic_patterns = [
            r'(\w+)\s*\+\s*(\w+)(?!\s*<=|\s*<|\s*>=|\s*>)',  # Addition without bounds check
            r'(\w+)\s*\*\s*(\w+)(?!\s*<=|\s*<|\s*>=|\s*>)',  # Multiplication without bounds check
            r'(\w+)\s*-\s*(\w+)(?!\s*<=|\s*<|\s*>=|\s*>)',  # Subtraction without bounds check
            r'(\w+)\s*\*\*\s*(\w+)',  # Exponentiation
            r'(\w+)\s*<<\s*(\w+)',  # Left shift
        ]
        
        # Safe math library patterns
        self.safe_math_patterns = [
            r'SafeMath\.',
            r'\.add\s*\(',
            r'\.sub\s*\(',
            r'\.mul\s*\(',
            r'\.div\s*\(',
            r'using\s+SafeMath',
            r'checked\s*\{',  # Solidity 0.8+ checked arithmetic
        ]
        
        # Vulnerable contexts
        self.vulnerable_contexts = [
            r'balances\[[^\]]+\]\s*[\+\-\*]=',  # Balance updates
            r'totalSupply\s*[\+\-\*]=',  # Supply changes
            r'allowances\[[^\]]+\]\[[^\]]+\]\s*[\+\-\*]=',  # Allowance updates
            r'for\s*\([^;]*;\s*[^;]*[\+\-\*]=',  # Loop counters
        ]
    
    async def analyze(self, context: StrategyContext) -> List[VulnerabilityFinding]:
        """Analyze for arithmetic overflow/underflow vulnerabilities"""
        findings = []
        
        if not context.source_code:
            self.logger.warning("No source code available for arithmetic analysis")
            return findings
        
        # Check Solidity version for automatic overflow protection
        solidity_version = self._detect_solidity_version(context.source_code)
        has_automatic_protection = self._has_automatic_overflow_protection(solidity_version)
        
        if has_automatic_protection:
            # Check for unchecked blocks in Solidity 0.8+
            unchecked_findings = await self._analyze_unchecked_blocks(context)
            findings.extend(unchecked_findings)
        else:
            # Analyze pre-0.8 contracts
            overflow_findings = await self._analyze_unsafe_arithmetic(context)
            findings.extend(overflow_findings)
        
        # Check for specific vulnerable patterns regardless of version
        pattern_findings = await self._analyze_vulnerable_patterns(context)
        findings.extend(pattern_findings)
        
        return findings
    
    def _detect_solidity_version(self, source_code: str) -> Optional[str]:
        """Detect Solidity version from pragma statement"""
        pragma_pattern = r'pragma\s+solidity\s+([^;]+);'
        match = re.search(pragma_pattern, source_code, re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        return None
    
    def _has_automatic_overflow_protection(self, version: Optional[str]) -> bool:
        """Check if Solidity version has automatic overflow protection"""
        if not version:
            return False
        
        # Solidity 0.8.0+ has automatic overflow protection
        if re.search(r'\^?0\.8\.|>=\s*0\.8\.|>\s*0\.7\.', version):
            return True
        
        return False
    
    async def _analyze_unchecked_blocks(self, context: StrategyContext) -> List[VulnerabilityFinding]:
        """Analyze unchecked blocks in Solidity 0.8+"""
        findings = []
        source_code = context.source_code
        
        # Find unchecked blocks
        unchecked_pattern = r'unchecked\s*\{([^}]+)\}'
        
        for match in re.finditer(unchecked_pattern, source_code, re.DOTALL):
            unchecked_content = match.group(1)
            
            # Check for arithmetic operations in unchecked blocks
            has_arithmetic = any(
                re.search(pattern, unchecked_content)
                for pattern in self.unsafe_arithmetic_patterns
            )
            
            if has_arithmetic:
                # Check if operations are in vulnerable contexts
                is_vulnerable = any(
                    re.search(pattern, unchecked_content)
                    for pattern in self.vulnerable_contexts
                )
                
                if is_vulnerable:
                    finding = self.create_finding(
                        title="Dangerous Unchecked Arithmetic Operations",
                        description="Unchecked block contains arithmetic operations that could "
                                   "overflow or underflow. While unchecked blocks are useful for "
                                   "gas optimization, they must be used carefully to avoid vulnerabilities.",
                        severity="Medium",
                        confidence=0.7,
                        exploit_scenario=self._generate_unchecked_exploit_scenario(),
                        remediation=self._generate_unchecked_remediation()
                    )
                    findings.append(finding)
        
        return findings
    
    async def _analyze_unsafe_arithmetic(self, context: StrategyContext) -> List[VulnerabilityFinding]:
        """Analyze unsafe arithmetic in pre-0.8 Solidity"""
        findings = []
        source_code = context.source_code
        
        # Check if SafeMath is used
        uses_safe_math = any(
            re.search(pattern, source_code, re.IGNORECASE)
            for pattern in self.safe_math_patterns
        )
        
        if not uses_safe_math:
            # Find arithmetic operations
            for pattern in self.unsafe_arithmetic_patterns:
                matches = list(re.finditer(pattern, source_code))
                
                if matches:
                    # Check if operations are in vulnerable contexts
                    vulnerable_operations = []
                    
                    for match in matches:
                        operation_context = self._get_operation_context(source_code, match.start())
                        
                        if self._is_vulnerable_context(operation_context):
                            vulnerable_operations.append({
                                'operation': match.group(0),
                                'context': operation_context[:100]  # First 100 chars for context
                            })
                    
                    if vulnerable_operations:
                        finding = self.create_finding(
                            title="Unsafe Arithmetic Operations",
                            description=f"Contract uses unsafe arithmetic operations without SafeMath "
                                       f"protection. Found {len(vulnerable_operations)} potentially "
                                       f"vulnerable operations. This could lead to integer overflow/underflow.",
                            severity="High",
                            confidence=0.8,
                            exploit_scenario=self._generate_overflow_exploit_scenario(),
                            remediation=self._generate_overflow_remediation()
                        )
                        findings.append(finding)
                        break  # Only report once per contract
        
        return findings
    
    async def _analyze_vulnerable_patterns(self, context: StrategyContext) -> List[VulnerabilityFinding]:
        """Analyze specific vulnerable patterns"""
        findings = []
        source_code = context.source_code
        
        # Check for multiplication before division (precision loss)
        mult_div_pattern = r'(\w+\s*\*\s*\w+)\s*/\s*\w+'
        
        for match in re.finditer(mult_div_pattern, source_code):
            finding = self.create_finding(
                title="Multiplication Before Division",
                description="Performing multiplication before division can lead to precision "
                           "loss and unexpected results. Consider reordering operations or "
                           "using higher precision arithmetic.",
                severity="Low",
                confidence=0.6,
                exploit_scenario="Precision loss could lead to incorrect calculations in financial operations",
                remediation="Reorder operations to perform division last or use fixed-point arithmetic"
            )
            findings.append(finding)
            break  # Only report once
        
        # Check for large exponentiation
        exp_pattern = r'(\w+)\s*\*\*\s*(\w+)'
        
        for match in re.finditer(exp_pattern, source_code):
            base, exponent = match.groups()
            
            finding = self.create_finding(
                title="Potential Exponentiation Overflow",
                description=f"Exponentiation operation {base}**{exponent} could cause overflow "
                           f"for large values. Consider adding bounds checking.",
                severity="Medium",
                confidence=0.5,
                exploit_scenario="Large exponents could cause arithmetic overflow and unexpected behavior",
                remediation="Add bounds checking for base and exponent values"
            )
            findings.append(finding)
        
        return findings
    
    def _get_operation_context(self, source_code: str, position: int) -> str:
        """Get context around an arithmetic operation"""
        start = max(0, position - 200)
        end = min(len(source_code), position + 200)
        return source_code[start:end]
    
    def _is_vulnerable_context(self, context: str) -> bool:
        """Check if the context indicates a vulnerable operation"""
        return any(
            re.search(pattern, context, re.IGNORECASE)
            for pattern in self.vulnerable_contexts
        )
    
    def _generate_overflow_exploit_scenario(self) -> str:
        """Generate overflow exploit scenario"""
        return """
        Integer Overflow/Underflow Exploit:
        1. Attacker identifies arithmetic operations without SafeMath
        2. Attacker crafts inputs to cause integer overflow/underflow
        3. For overflow: Large values wrap around to small values
        4. For underflow: Small values wrap around to large values
        5. This can lead to:
           - Balance manipulation (negative balance becomes large positive)
           - Token minting exploits (overflow in supply calculations)
           - Logic bypass (loop counters wrapping around)
           - Financial losses due to incorrect calculations
        """
    
    def _generate_overflow_remediation(self) -> str:
        """Generate overflow remediation advice"""
        return """
        Integer Overflow/Underflow Protection:
        1. Use SafeMath library for all arithmetic operations
        2. Upgrade to Solidity 0.8+ for automatic overflow protection
        3. Add explicit bounds checking for critical calculations
        4. Use require() statements to validate input ranges
        5. Consider using OpenZeppelin's SafeCast for type conversions
        6. Test edge cases with maximum and minimum values
        7. Use static analysis tools to identify arithmetic vulnerabilities
        """
    
    def _generate_unchecked_exploit_scenario(self) -> str:
        """Generate unchecked block exploit scenario"""
        return """
        Unchecked Block Exploit:
        1. Attacker identifies unchecked arithmetic operations
        2. Despite Solidity 0.8+ automatic protection, unchecked blocks bypass it
        3. Attacker crafts inputs to cause overflow/underflow in unchecked code
        4. Vulnerable operations execute without revert on overflow
        5. This can lead to the same issues as pre-0.8 overflow vulnerabilities
        """
    
    def _generate_unchecked_remediation(self) -> str:
        """Generate unchecked block remediation advice"""
        return """
        Unchecked Block Safety:
        1. Only use unchecked blocks when overflow/underflow is impossible
        2. Add explicit bounds checking before unchecked operations
        3. Document why each unchecked block is safe
        4. Consider the performance vs security trade-off
        5. Test unchecked operations thoroughly with edge cases
        6. Use unchecked blocks sparingly and only for gas optimization
        """
