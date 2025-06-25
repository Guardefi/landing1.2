"""
Advanced Reentrancy Detection Strategy
Combines pattern analysis with simulation-based testing
"""

import re
from typing import Dict, Any, List, Optional

from .base import BaseStrategy, StrategyContext
from core.models import VulnerabilityFinding


class ReentrancyStrategy(BaseStrategy):
    """Advanced reentrancy vulnerability detection strategy"""
    
    def __init__(self):
        super().__init__(
            name="reentrancy",
            description="Detects reentrancy vulnerabilities using pattern analysis and simulation"
        )
        self.reentrancy_patterns = [
            r'\.call\s*\{[^}]*value\s*:[^}]*\}',  # Low-level call with value
            r'\.call\s*\([^)]*\)',  # Basic call pattern
            r'\.transfer\s*\(',  # Transfer calls
            r'\.send\s*\(',  # Send calls
            r'\.delegatecall\s*\(',  # Delegate calls
            r'external\s+.*payable',  # External payable functions
        ]
        
        self.state_change_patterns = [
            r'balances\[[^\]]+\]\s*=',  # Balance updates
            r'\.balanceOf\s*\(',  # Balance queries
            r'\.transfer\s*\(',  # Token transfers
            r'require\s*\(',  # Require statements
            r'assert\s*\(',  # Assert statements
        ]
        
        self.protection_patterns = [
            r'nonReentrant',  # OpenZeppelin modifier
            r'ReentrancyGuard',  # ReentrancyGuard usage
            r'_reentrancyGuard',  # Custom reentrancy guards
            r'mutex',  # Mutex patterns
            r'locked',  # Lock patterns
        ]
    
    async def analyze(self, context: StrategyContext) -> List[VulnerabilityFinding]:
        """Analyze for reentrancy vulnerabilities"""
        findings = []
        
        if not context.source_code:
            self.logger.warning("No source code available for reentrancy analysis")
            return findings
        
        # Pattern-based analysis
        pattern_findings = await self._pattern_analysis(context)
        findings.extend(pattern_findings)
        
        # Simulation-based testing (if simulation engine available)
        if context.simulation_engine and pattern_findings:
            simulation_findings = await self._simulation_analysis(context, pattern_findings)
            findings.extend(simulation_findings)
        
        return findings
    
    async def _pattern_analysis(self, context: StrategyContext) -> List[VulnerabilityFinding]:
        """Perform pattern-based reentrancy analysis"""
        findings = []
        source_code = context.source_code
        
        # Find functions with external calls
        functions_with_calls = self._find_functions_with_external_calls(source_code)
        
        for func_info in functions_with_calls:
            # Check for reentrancy vulnerability patterns
            vulnerability = await self._analyze_function_for_reentrancy(func_info, source_code)
            if vulnerability:
                findings.append(vulnerability)
        
        return findings
    
    def _find_functions_with_external_calls(self, source_code: str) -> List[Dict[str, Any]]:
        """Find functions that make external calls"""
        functions = []
        
        # Find function definitions
        function_pattern = r'function\s+(\w+)\s*\([^)]*\)\s*([^{]*)\s*\{([^}]+)\}'
        
        for match in re.finditer(function_pattern, source_code, re.DOTALL):
            func_name = match.group(1)
            func_modifiers = match.group(2)
            func_body = match.group(3)
            
            # Check if function makes external calls
            has_external_call = any(
                re.search(pattern, func_body, re.IGNORECASE)
                for pattern in self.reentrancy_patterns
            )
            
            if has_external_call:
                functions.append({
                    'name': func_name,
                    'modifiers': func_modifiers,
                    'body': func_body,
                    'full_match': match.group(0),
                    'start_pos': match.start(),
                    'end_pos': match.end()
                })
        
        return functions
    
    async def _analyze_function_for_reentrancy(
        self, 
        func_info: Dict[str, Any], 
        source_code: str
    ) -> Optional[VulnerabilityFinding]:
        """Analyze a specific function for reentrancy vulnerabilities"""
        func_body = func_info['body']
        func_name = func_info['name']
        
        # Check for protection mechanisms
        has_protection = any(
            re.search(pattern, func_info['modifiers'] + func_body, re.IGNORECASE)
            for pattern in self.protection_patterns
        )
        
        if has_protection:
            self.logger.debug(f"Function {func_name} has reentrancy protection")
            return None
        
        # Analyze call patterns and state changes
        external_calls = self._find_external_calls_in_function(func_body)
        state_changes = self._find_state_changes_in_function(func_body)
        
        # Check for vulnerable patterns
        vulnerability_score = 0
        vulnerability_details = []
        
        for call in external_calls:
            # Find state changes after this call
            call_pos = call['position']
            state_changes_after = [
                sc for sc in state_changes 
                if sc['position'] > call_pos
            ]
            
            if state_changes_after:
                vulnerability_score += 1
                vulnerability_details.append(
                    f"External call at position {call_pos} followed by state changes"
                )
        
        # Check for checks-effects-interactions pattern violation
        if self._violates_cei_pattern(func_body):
            vulnerability_score += 2
            vulnerability_details.append("Violates checks-effects-interactions pattern")
        
        # Create finding if vulnerability detected
        if vulnerability_score > 0:
            severity = "Critical" if vulnerability_score >= 2 else "High"
            confidence = min(0.9, 0.5 + (vulnerability_score * 0.2))
            
            return self.create_finding(
                title=f"Reentrancy Vulnerability in {func_name}",
                description=f"Function {func_name} is potentially vulnerable to reentrancy attacks. " +
                           f"Vulnerability indicators: {'; '.join(vulnerability_details)}",
                severity=severity,
                confidence=confidence,
                affected_functions=[func_name],
                exploit_scenario=self._generate_exploit_scenario(func_name, external_calls),
                remediation=self._generate_remediation_advice(func_name)
            )
        
        return None
    
    def _find_external_calls_in_function(self, func_body: str) -> List[Dict[str, Any]]:
        """Find external calls in function body"""
        calls = []
        
        for pattern in self.reentrancy_patterns:
            for match in re.finditer(pattern, func_body, re.IGNORECASE):
                calls.append({
                    'pattern': pattern,
                    'match': match.group(0),
                    'position': match.start(),
                    'type': self._classify_call_type(match.group(0))
                })
        
        return sorted(calls, key=lambda x: x['position'])
    
    def _find_state_changes_in_function(self, func_body: str) -> List[Dict[str, Any]]:
        """Find state changes in function body"""
        changes = []
        
        for pattern in self.state_change_patterns:
            for match in re.finditer(pattern, func_body, re.IGNORECASE):
                changes.append({
                    'pattern': pattern,
                    'match': match.group(0),
                    'position': match.start(),
                    'type': self._classify_state_change_type(match.group(0))
                })
        
        return sorted(changes, key=lambda x: x['position'])
    
    def _classify_call_type(self, call_text: str) -> str:
        """Classify the type of external call"""
        call_text_lower = call_text.lower()
        
        if 'delegatecall' in call_text_lower:
            return 'delegatecall'
        elif 'call{' in call_text_lower and 'value:' in call_text_lower:
            return 'call_with_value'
        elif 'call(' in call_text_lower:
            return 'low_level_call'
        elif 'transfer(' in call_text_lower:
            return 'transfer'
        elif 'send(' in call_text_lower:
            return 'send'
        else:
            return 'unknown'
    
    def _classify_state_change_type(self, change_text: str) -> str:
        """Classify the type of state change"""
        change_text_lower = change_text.lower()
        
        if 'balances[' in change_text_lower or 'balance' in change_text_lower:
            return 'balance_update'
        elif 'transfer(' in change_text_lower:
            return 'transfer'
        elif 'require(' in change_text_lower:
            return 'require_check'
        elif 'assert(' in change_text_lower:
            return 'assert_check'
        else:
            return 'unknown'
    
    def _violates_cei_pattern(self, func_body: str) -> bool:
        """Check if function violates checks-effects-interactions pattern"""
        # Simple heuristic: if there are state changes after external calls
        external_calls = self._find_external_calls_in_function(func_body)
        state_changes = self._find_state_changes_in_function(func_body)
        
        for call in external_calls:
            # Look for state changes after this call
            state_changes_after = [
                sc for sc in state_changes 
                if sc['position'] > call['position'] and sc['type'] == 'balance_update'
            ]
            if state_changes_after:
                return True
        
        return False
    
    def _generate_exploit_scenario(self, func_name: str, external_calls: List[Dict[str, Any]]) -> str:
        """Generate exploit scenario description"""
        scenario = f"An attacker could exploit the reentrancy vulnerability in {func_name} by:\n"
        scenario += "1. Creating a malicious contract with a fallback function\n"
        scenario += "2. Calling the vulnerable function to trigger an external call\n"
        scenario += "3. In the fallback function, recursively calling the vulnerable function\n"
        scenario += "4. Draining funds or manipulating state before the original call completes"
        
        return scenario
    
    def _generate_remediation_advice(self, func_name: str) -> str:
        """Generate remediation advice"""
        advice = f"To fix the reentrancy vulnerability in {func_name}:\n"
        advice += "1. Use the checks-effects-interactions pattern\n"
        advice += "2. Add ReentrancyGuard modifier from OpenZeppelin\n"
        advice += "3. Update state before making external calls\n"
        advice += "4. Consider using pull payment pattern\n"
        advice += "5. Use mutex/lock mechanisms for critical sections"
        
        return advice
    
    async def _simulation_analysis(
        self, 
        context: StrategyContext, 
        pattern_findings: List[VulnerabilityFinding]
    ) -> List[VulnerabilityFinding]:
        """Perform simulation-based reentrancy testing"""
        findings = []
        
        for finding in pattern_findings:
            if finding.affected_functions:
                # Generate test contract for each vulnerable function
                test_result = await self._test_reentrancy_with_simulation(
                    context, finding.affected_functions[0]
                )
                
                if test_result and test_result.get('exploitable'):
                    # Update confidence and add simulation evidence
                    finding.confidence = min(finding.confidence + 0.2, 1.0)
                    finding.description += f"\n\nSimulation Result: {test_result['description']}"
        
        return findings
    
    async def _test_reentrancy_with_simulation(
        self, 
        context: StrategyContext, 
        function_name: str
    ) -> Optional[Dict[str, Any]]:
        """Test specific function for reentrancy using simulation"""
        try:
            # Generate exploit contract
            exploit_contract = self._generate_exploit_contract(
                context.target.identifier, function_name
            )
            
            # Deploy and test using simulation engine
            simulation_result = await context.simulation_engine.run_forge_test(
                exploit_contract, f"test{function_name}Reentrancy"
            )
            
            if simulation_result.success and "EXPLOIT_SUCCESSFUL" in simulation_result.stdout:
                return {
                    'exploitable': True,
                    'description': f"Simulation confirmed reentrancy vulnerability in {function_name}",
                    'simulation_output': simulation_result.stdout
                }
            
            return {
                'exploitable': False,
                'description': f"Simulation test passed for {function_name}",
                'simulation_output': simulation_result.stdout
            }
            
        except Exception as e:
            self.logger.error(f"Simulation test failed for {function_name}: {e}")
            return None
    
    def _generate_exploit_contract(self, target_address: str, function_name: str) -> str:
        """Generate Solidity exploit contract for testing"""
        contract = f"""
        // SPDX-License-Identifier: MIT
        pragma solidity ^0.8.0;
        
        import "forge-std/Test.sol";
        
        interface ITarget {{
            function {function_name}() external payable;
            function balanceOf(address) external view returns (uint256);
        }}
        
        contract ReentrancyExploit is Test {{
            ITarget target;
            uint256 public callCount;
            uint256 public maxCalls = 3;
            
            function setUp() public {{
                target = ITarget({target_address});
            }}
            
            function test{function_name}Reentrancy() public {{
                uint256 initialBalance = address(this).balance;
                
                try target.{function_name}{{value: 1 ether}}() {{
                    if (callCount >= maxCalls) {{
                        console.log("EXPLOIT_SUCCESSFUL: Reentrancy vulnerability confirmed");
                        assertTrue(true);
                    }}
                }} catch {{
                    console.log("Function call failed - may not be vulnerable");
                }}
            }}
            
            fallback() external payable {{
                callCount++;
                if (callCount < maxCalls) {{
                    target.{function_name}{{value: 1 ether}}();
                }}
            }}
            
            receive() external payable {{
                callCount++;
                if (callCount < maxCalls) {{
                    target.{function_name}{{value: 1 ether}}();
                }}
            }}
        }}
        """
        return contract
