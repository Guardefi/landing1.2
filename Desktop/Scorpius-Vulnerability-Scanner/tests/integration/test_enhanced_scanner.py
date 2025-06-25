"""
Comprehensive Integration Test Suite for Enhanced Scorpius Scanner
Tests all new components and strategies
"""

import asyncio
import pytest
import os
from pathlib import Path
from typing import Dict, Any

# Test data - vulnerable contract examples
VULNERABLE_REENTRANCY_CONTRACT = '''
pragma solidity ^0.7.0;

contract VulnerableReentrancy {
    mapping(address => uint256) public balances;
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // Vulnerable: external call before state update
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] -= amount;  // State change after external call
    }
}
'''

VULNERABLE_ACCESS_CONTROL_CONTRACT = '''
pragma solidity ^0.7.0;

contract VulnerableAccessControl {
    address public owner;
    mapping(address => uint256) public balances;
    
    constructor() {
        owner = msg.sender;
    }
    
    // Vulnerable: no access control on critical function
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        payable(msg.sender).transfer(amount);
        balances[msg.sender] -= amount;
    }
    
    // Vulnerable: unprotected admin function
    function emergencyWithdraw() public {
        payable(msg.sender).transfer(address(this).balance);
    }
}
'''

VULNERABLE_ARITHMETIC_CONTRACT = '''
pragma solidity ^0.7.0;

contract VulnerableArithmetic {
    mapping(address => uint256) public balances;
    uint256 public totalSupply;
    
    function mint(address to, uint256 amount) public {
        // Vulnerable: no SafeMath, could overflow
        balances[to] += amount;
        totalSupply += amount;
    }
    
    function transfer(address to, uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // Vulnerable: potential underflow
        balances[msg.sender] -= amount;
        balances[to] += amount;
    }
}
'''

VULNERABLE_FLASH_LOAN_CONTRACT = '''
pragma solidity ^0.7.0;

interface IERC20 {
    function balanceOf(address) external view returns (uint256);
}

contract VulnerableFlashLoan {
    IERC20 token0;
    IERC20 token1;
    
    function getPrice() public view returns (uint256) {
        // Vulnerable: uses spot price from balances
        uint256 balance0 = token0.balanceOf(address(this));
        uint256 balance1 = token1.balanceOf(address(this));
        return balance1 * 1e18 / balance0;
    }
    
    function liquidate(address user) public {
        uint256 price = getPrice();
        // Vulnerable: uses manipulatable price for liquidation
        // ... liquidation logic
    }
}
'''


class TestEnhancedScanner:
    """Test suite for enhanced vulnerability scanner"""
    
    @pytest.fixture
    def scanner_config(self):
        """Configuration for testing"""
        return {
            "enable_simulation": False,  # Disable for unit tests
            "enable_ai_analysis": False,  # Disable AI for unit tests
            "parallel_execution": True,
            "anthropic_api_key": None,  # Will be mocked
            "anvil_path": "anvil",
            "forge_path": "forge"
        }
    
    @pytest.fixture
    async def enhanced_analyzer(self, scanner_config):
        """Create enhanced analyzer instance"""
        from ai.vulnerability_analyzer import EnhancedVulnerabilityAnalyzer
        from core.models import Target
        
        analyzer = EnhancedVulnerabilityAnalyzer(config=scanner_config)
        return analyzer
    
    @pytest.fixture
    def test_target(self):
        """Create test target"""
        from core.models import Target, TargetType
        
        return Target(
            identifier="0x1234567890123456789012345678901234567890",
            target_type=TargetType.CONTRACT.value,
            blockchain="ethereum"
        )
    
    @pytest.mark.asyncio
    async def test_reentrancy_strategy(self, enhanced_analyzer, test_target):
        """Test reentrancy detection strategy"""
        findings = await enhanced_analyzer.analyze_with_strategies_only(
            target=test_target,
            source_code=VULNERABLE_REENTRANCY_CONTRACT,
            enabled_strategies=["reentrancy"]
        )
        
        assert len(findings) > 0, "Should detect reentrancy vulnerability"
        
        reentrancy_finding = next(
            (f for f in findings if "reentrancy" in f.title.lower()), None
        )
        assert reentrancy_finding is not None, "Should find reentrancy vulnerability"
        assert reentrancy_finding.severity in ["Critical", "High"], "Should be high severity"
        assert "withdraw" in reentrancy_finding.affected_functions, "Should identify vulnerable function"
    
    @pytest.mark.asyncio
    async def test_access_control_strategy(self, enhanced_analyzer, test_target):
        """Test access control detection strategy"""
        findings = await enhanced_analyzer.analyze_with_strategies_only(
            target=test_target,
            source_code=VULNERABLE_ACCESS_CONTROL_CONTRACT,
            enabled_strategies=["access_control"]
        )
        
        assert len(findings) > 0, "Should detect access control vulnerabilities"
        
        # Should find multiple access control issues
        access_control_findings = [
            f for f in findings if "access control" in f.title.lower()
        ]
        assert len(access_control_findings) >= 2, "Should find multiple access control issues"
    
    @pytest.mark.asyncio
    async def test_arithmetic_overflow_strategy(self, enhanced_analyzer, test_target):
        """Test arithmetic overflow detection strategy"""
        findings = await enhanced_analyzer.analyze_with_strategies_only(
            target=test_target,
            source_code=VULNERABLE_ARITHMETIC_CONTRACT,
            enabled_strategies=["arithmetic_overflow"]
        )
        
        assert len(findings) > 0, "Should detect arithmetic vulnerabilities"
        
        arithmetic_finding = next(
            (f for f in findings if "arithmetic" in f.title.lower()), None
        )
        assert arithmetic_finding is not None, "Should find arithmetic vulnerability"
    
    @pytest.mark.asyncio
    async def test_flash_loan_strategy(self, enhanced_analyzer, test_target):
        """Test flash loan attack detection strategy"""
        findings = await enhanced_analyzer.analyze_with_strategies_only(
            target=test_target,
            source_code=VULNERABLE_FLASH_LOAN_CONTRACT,
            enabled_strategies=["flash_loan_attack"]
        )
        
        assert len(findings) > 0, "Should detect flash loan vulnerabilities"
        
        flash_loan_finding = next(
            (f for f in findings if "flash loan" in f.title.lower() or "oracle" in f.title.lower()), None
        )
        assert flash_loan_finding is not None, "Should find flash loan vulnerability"
    
    @pytest.mark.asyncio
    async def test_all_strategies_parallel(self, enhanced_analyzer, test_target):
        """Test running all strategies in parallel"""
        findings = await enhanced_analyzer.analyze_with_strategies_only(
            target=test_target,
            source_code=VULNERABLE_REENTRANCY_CONTRACT + VULNERABLE_ACCESS_CONTROL_CONTRACT,
            enabled_strategies=None  # Run all strategies
        )
        
        assert len(findings) > 0, "Should detect vulnerabilities with all strategies"
        
        # Should have findings from multiple strategies
        strategy_types = set(f.category for f in findings)
        assert len(strategy_types) > 1, "Should have findings from multiple strategies"
    
    @pytest.mark.asyncio
    async def test_strategy_manager_configuration(self, enhanced_analyzer):
        """Test strategy manager configuration"""
        # Test getting available strategies
        strategies = enhanced_analyzer.get_available_strategies()
        assert len(strategies) >= 4, "Should have at least 4 strategies"
        assert "reentrancy" in strategies
        assert "flash_loan_attack" in strategies
        assert "access_control" in strategies
        assert "arithmetic_overflow" in strategies
        
        # Test configuring strategies
        success = enhanced_analyzer.configure_strategy("reentrancy", enabled=False)
        assert success, "Should successfully configure strategy"
        
        # Test with invalid strategy
        success = enhanced_analyzer.configure_strategy("nonexistent", enabled=False)
        assert not success, "Should fail for nonexistent strategy"
    
    @pytest.mark.asyncio
    async def test_comprehensive_analysis_without_ai(self, enhanced_analyzer, test_target):
        """Test comprehensive analysis without AI components"""
        result = await enhanced_analyzer.analyze_comprehensive(
            target=test_target,
            source_code=VULNERABLE_REENTRANCY_CONTRACT,
            enable_simulation=False,
            enable_ai=False
        )
        
        assert result is not None, "Should return analysis result"
        assert len(result.vulnerabilities) > 0, "Should find vulnerabilities"
        assert len(result.strategy_findings) > 0, "Should have strategy findings"
        assert len(result.ai_analysis) == 0, "Should have no AI findings when disabled"
        assert result.risk_assessment is not None, "Should have risk assessment"
        assert result.exploit_prediction is not None, "Should have exploit prediction"
    
    def test_vulnerability_finding_creation(self):
        """Test vulnerability finding data structure"""
        from core.models import VulnerabilityFinding
        
        finding = VulnerabilityFinding(
            id="test_vuln_1",
            title="Test Vulnerability",
            description="A test vulnerability for validation",
            severity="High",
            confidence=0.9,
            category="test",
            affected_functions=["testFunction"],
            risk_score=7.5,
            exploit_scenario="Test exploit scenario",
            remediation="Test remediation advice"
        )
        
        assert finding.id == "test_vuln_1"
        assert finding.severity == "High"
        assert finding.confidence == 0.9
        assert "testFunction" in finding.affected_functions
    
    def test_simulation_config_creation(self):
        """Test simulation configuration"""
        from simulation import SimulationConfig
        
        config = SimulationConfig(
            anvil_path="anvil",
            forge_path="forge",
            port=8545,
            fork_url="https://eth-mainnet.alchemyapi.io/v2/test"
        )
        
        assert config.anvil_path == "anvil"
        assert config.port == 8545
        assert config.fork_url is not None


class TestPerformance:
    """Performance tests for the enhanced scanner"""
    
    @pytest.mark.asyncio
    async def test_parallel_vs_sequential_performance(self):
        """Test that parallel execution is faster than sequential"""
        from ai.vulnerability_analyzer import EnhancedVulnerabilityAnalyzer
        from core.models import Target, TargetType
        import time
        
        target = Target(
            identifier="0x1234567890123456789012345678901234567890",
            target_type=TargetType.CONTRACT.value,
            blockchain="ethereum"
        )
        
        large_contract = VULNERABLE_REENTRANCY_CONTRACT + VULNERABLE_ACCESS_CONTROL_CONTRACT + VULNERABLE_ARITHMETIC_CONTRACT
        
        # Test parallel execution
        config_parallel = {"parallel_execution": True, "enable_simulation": False, "enable_ai_analysis": False}
        analyzer_parallel = EnhancedVulnerabilityAnalyzer(config=config_parallel)
        
        start_time = time.time()
        findings_parallel = await analyzer_parallel.analyze_with_strategies_only(
            target=target,
            source_code=large_contract
        )
        parallel_time = time.time() - start_time
        
        # Test sequential execution
        config_sequential = {"parallel_execution": False, "enable_simulation": False, "enable_ai_analysis": False}
        analyzer_sequential = EnhancedVulnerabilityAnalyzer(config=config_sequential)
        
        start_time = time.time()
        findings_sequential = await analyzer_sequential.analyze_with_strategies_only(
            target=target,
            source_code=large_contract
        )
        sequential_time = time.time() - start_time
        
        # Results should be similar
        assert len(findings_parallel) == len(findings_sequential), "Should find same number of vulnerabilities"
        
        # Parallel should be faster (or at least not significantly slower)
        # Allow some margin for test environment variations
        assert parallel_time <= sequential_time * 1.5, "Parallel execution should not be significantly slower"
        
        print(f"Parallel time: {parallel_time:.2f}s, Sequential time: {sequential_time:.2f}s")


if __name__ == "__main__":
    """Run tests directly"""
    pytest.main([__file__, "-v", "-s"])
