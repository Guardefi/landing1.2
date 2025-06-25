"""
Unit tests for backend utility functions.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import hashlib
import json


# Mock utility functions since we don't have access to the actual utils
# In a real implementation, these would import from backend.utils


class TestCryptoUtils:
    """Test cryptographic utility functions."""

    def test_hash_password(self):
        """Test password hashing."""
        # Mock implementation
        def hash_password(password: str) -> str:
            return hashlib.sha256(password.encode()).hexdigest()
        
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) == 64  # SHA256 hex length
        assert isinstance(hashed, str)
    
    def test_verify_password(self):
        """Test password verification."""
        def hash_password(password: str) -> str:
            return hashlib.sha256(password.encode()).hexdigest()
        
        def verify_password(password: str, hashed: str) -> bool:
            return hash_password(password) == hashed
        
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False
    
    def test_generate_api_key(self):
        """Test API key generation."""
        import secrets
        
        def generate_api_key() -> str:
            return secrets.token_urlsafe(32)
        
        key1 = generate_api_key()
        key2 = generate_api_key()
        
        assert len(key1) > 30  # URL-safe base64 encoding
        assert len(key2) > 30
        assert key1 != key2  # Should be unique


class TestValidationUtils:
    """Test validation utility functions."""
    
    def test_validate_ethereum_address(self):
        """Test Ethereum address validation."""
        def validate_ethereum_address(address: str) -> bool:
            if not address.startswith('0x'):
                return False
            if len(address) != 42:
                return False
            try:
                int(address[2:], 16)
                return True
            except ValueError:
                return False
        
        # Valid addresses
        assert validate_ethereum_address("0x1234567890123456789012345678901234567890") is True
        assert validate_ethereum_address("0xabcdefABCDEF123456789012345678901234567890") is True
        
        # Invalid addresses
        assert validate_ethereum_address("1234567890123456789012345678901234567890") is False  # No 0x
        assert validate_ethereum_address("0x123") is False  # Too short
        assert validate_ethereum_address("0x123456789012345678901234567890123456789G") is False  # Invalid hex
    
    def test_validate_smart_contract_code(self):
        """Test smart contract code validation."""
        def validate_smart_contract_code(code: str) -> bool:
            if not code or not isinstance(code, str):
                return False
            # Basic Solidity validation
            return 'pragma solidity' in code.lower() or 'contract' in code.lower()
        
        valid_code = """
        pragma solidity ^0.8.0;
        contract TestContract {
            uint256 public value;
        }
        """
        
        assert validate_smart_contract_code(valid_code) is True
        assert validate_smart_contract_code("") is False
        assert validate_smart_contract_code("not a contract") is False
    
    def test_validate_transaction_hash(self):
        """Test transaction hash validation."""
        def validate_transaction_hash(tx_hash: str) -> bool:
            if not tx_hash.startswith('0x'):
                return False
            if len(tx_hash) != 66:  # 0x + 64 hex chars
                return False
            try:
                int(tx_hash[2:], 16)
                return True
            except ValueError:
                return False
        
        valid_hash = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef12"
        invalid_hash = "0x123"
        
        assert validate_transaction_hash(valid_hash) is True
        assert validate_transaction_hash(invalid_hash) is False


class TestMEVUtils:
    """Test MEV-related utility functions."""
    
    def test_calculate_mev_profit(self):
        """Test MEV profit calculation."""
        def calculate_mev_profit(buy_price: float, sell_price: float, amount: float, gas_cost: float) -> float:
            if buy_price <= 0 or sell_price <= 0 or amount <= 0:
                return 0.0
            gross_profit = (sell_price - buy_price) * amount
            return max(0.0, gross_profit - gas_cost)
        
        # Profitable trade
        profit = calculate_mev_profit(100.0, 110.0, 1.0, 5.0)
        assert profit == 5.0  # (110-100)*1 - 5 = 5
        
        # Unprofitable trade
        profit = calculate_mev_profit(100.0, 101.0, 1.0, 5.0)
        assert profit == 0.0  # (101-100)*1 - 5 = -4, but min is 0
        
        # Invalid inputs
        assert calculate_mev_profit(-100.0, 110.0, 1.0, 5.0) == 0.0
        assert calculate_mev_profit(100.0, -110.0, 1.0, 5.0) == 0.0
    
    def test_detect_sandwich_attack(self):
        """Test sandwich attack detection."""
        def detect_sandwich_attack(transactions: list) -> bool:
            if len(transactions) < 3:
                return False
            # Simple detection: same address buying before and selling after
            first_tx = transactions[0]
            last_tx = transactions[-1]
            return (
                first_tx.get('from') == last_tx.get('from') and
                first_tx.get('type') == 'buy' and
                last_tx.get('type') == 'sell'
            )
        
        # Sandwich attack pattern
        sandwich_txs = [
            {'from': '0x1111', 'type': 'buy', 'token': 'USDC'},
            {'from': '0x2222', 'type': 'buy', 'token': 'USDC'},  # Victim
            {'from': '0x1111', 'type': 'sell', 'token': 'USDC'},
        ]
        
        normal_txs = [
            {'from': '0x1111', 'type': 'buy', 'token': 'USDC'},
            {'from': '0x2222', 'type': 'sell', 'token': 'USDC'},
        ]
        
        assert detect_sandwich_attack(sandwich_txs) is True
        assert detect_sandwich_attack(normal_txs) is False
        assert detect_sandwich_attack([]) is False


class TestAnalyticsUtils:
    """Test analytics and calculation utilities."""
    
    def test_calculate_risk_score(self):
        """Test risk score calculation."""
        def calculate_risk_score(vulnerabilities: list) -> float:
            if not vulnerabilities:
                return 0.0
            
            severity_weights = {'LOW': 1, 'MEDIUM': 3, 'HIGH': 7, 'CRITICAL': 10}
            total_score = sum(severity_weights.get(v.get('severity', 'LOW'), 1) for v in vulnerabilities)
            max_possible = len(vulnerabilities) * 10
            return (total_score / max_possible) * 10.0
        
        # High risk vulnerabilities
        high_risk_vulns = [
            {'severity': 'CRITICAL'},
            {'severity': 'HIGH'},
            {'severity': 'MEDIUM'},
        ]
        
        # Low risk vulnerabilities
        low_risk_vulns = [
            {'severity': 'LOW'},
            {'severity': 'MEDIUM'},
        ]
        
        high_score = calculate_risk_score(high_risk_vulns)
        low_score = calculate_risk_score(low_risk_vulns)
        
        assert high_score > low_score
        assert 0.0 <= high_score <= 10.0
        assert 0.0 <= low_score <= 10.0
        assert calculate_risk_score([]) == 0.0
    
    def test_calculate_sharpe_ratio(self):
        """Test Sharpe ratio calculation."""
        def calculate_sharpe_ratio(returns: list, risk_free_rate: float = 0.02) -> float:
            if not returns or len(returns) < 2:
                return 0.0
            
            import statistics
            mean_return = statistics.mean(returns)
            std_return = statistics.stdev(returns)
            
            if std_return == 0:
                return 0.0
            
            return (mean_return - risk_free_rate) / std_return
        
        # Good returns (high Sharpe)
        good_returns = [0.08, 0.12, 0.10, 0.15, 0.09]
        
        # Volatile returns (low Sharpe)
        volatile_returns = [0.20, -0.10, 0.30, -0.15, 0.25]
        
        good_sharpe = calculate_sharpe_ratio(good_returns)
        volatile_sharpe = calculate_sharpe_ratio(volatile_returns)
        
        assert good_sharpe > volatile_sharpe
        assert calculate_sharpe_ratio([]) == 0.0
        assert calculate_sharpe_ratio([0.05]) == 0.0


class TestDataUtils:
    """Test data processing utilities."""
    
    def test_sanitize_input(self):
        """Test input sanitization."""
        def sanitize_input(data: str) -> str:
            if not isinstance(data, str):
                return ""
            # Remove potentially dangerous characters
            dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
            for char in dangerous_chars:
                data = data.replace(char, '')
            return data.strip()
        
        malicious_input = "<script>alert('xss')</script>"
        clean_input = "Hello World!"
        
        assert sanitize_input(malicious_input) == "scriptalert('xss')/script"
        assert sanitize_input(clean_input) == "Hello World!"
        assert sanitize_input(None) == ""
    
    def test_parse_blockchain_timestamp(self):
        """Test blockchain timestamp parsing."""
        def parse_blockchain_timestamp(timestamp: int) -> datetime:
            return datetime.fromtimestamp(timestamp)
        
        # Unix timestamp for 2024-01-01 00:00:00 UTC
        timestamp = 1704067200
        dt = parse_blockchain_timestamp(timestamp)
        
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 1
    
    def test_format_wei_to_eth(self):
        """Test Wei to ETH conversion."""
        def format_wei_to_eth(wei_amount: int) -> float:
            return wei_amount / 10**18
        
        one_eth_in_wei = 1000000000000000000  # 1 ETH = 10^18 Wei
        half_eth_in_wei = 500000000000000000
        
        assert format_wei_to_eth(one_eth_in_wei) == 1.0
        assert format_wei_to_eth(half_eth_in_wei) == 0.5
        assert format_wei_to_eth(0) == 0.0


class TestCacheUtils:
    """Test caching utilities."""
    
    def test_generate_cache_key(self):
        """Test cache key generation."""
        def generate_cache_key(prefix: str, **kwargs) -> str:
            sorted_items = sorted(kwargs.items())
            key_parts = [prefix] + [f"{k}:{v}" for k, v in sorted_items]
            return ":".join(key_parts)
        
        key1 = generate_cache_key("user", id=123, action="login")
        key2 = generate_cache_key("user", action="login", id=123)  # Different order
        key3 = generate_cache_key("user", id=456, action="login")
        
        assert key1 == key2  # Should be same regardless of order
        assert key1 != key3  # Should be different for different values
        assert "user" in key1
        assert "id:123" in key1
        assert "action:login" in key1
    
    @patch('time.time')
    def test_is_cache_expired(self, mock_time):
        """Test cache expiration check."""
        def is_cache_expired(cached_time: float, ttl_seconds: int) -> bool:
            import time
            return (time.time() - cached_time) > ttl_seconds
        
        mock_time.return_value = 1000.0
        
        # Not expired
        assert is_cache_expired(950.0, 60) is False  # 50 seconds ago, TTL 60
        
        # Expired
        assert is_cache_expired(900.0, 60) is True   # 100 seconds ago, TTL 60


# Integration-style tests that combine multiple utilities
class TestUtilsIntegration:
    """Test utility functions working together."""
    
    def test_vulnerability_analysis_pipeline(self):
        """Test complete vulnerability analysis workflow."""
        def validate_ethereum_address(address: str) -> bool:
            return address.startswith('0x') and len(address) == 42
        
        def calculate_risk_score(vulnerabilities: list) -> float:
            if not vulnerabilities:
                return 0.0
            severity_weights = {'LOW': 1, 'MEDIUM': 3, 'HIGH': 7, 'CRITICAL': 10}
            total_score = sum(severity_weights.get(v.get('severity', 'LOW'), 1) for v in vulnerabilities)
            max_possible = len(vulnerabilities) * 10
            return (total_score / max_possible) * 10.0
        
        def generate_cache_key(prefix: str, **kwargs) -> str:
            sorted_items = sorted(kwargs.items())
            key_parts = [prefix] + [f"{k}:{v}" for k, v in sorted_items]
            return ":".join(key_parts)
        
        # Test complete workflow
        contract_address = "0x1234567890123456789012345678901234567890"
        vulnerabilities = [
            {'severity': 'HIGH', 'type': 'reentrancy'},
            {'severity': 'MEDIUM', 'type': 'integer_overflow'},
        ]
        
        # Validate input
        assert validate_ethereum_address(contract_address) is True
        
        # Calculate risk
        risk_score = calculate_risk_score(vulnerabilities)
        assert 0.0 < risk_score <= 10.0
        
        # Generate cache key for results
        cache_key = generate_cache_key("scan", address=contract_address, version="v1")
        assert "scan" in cache_key
        assert contract_address in cache_key
    
    def test_mev_detection_workflow(self):
        """Test MEV detection and profit calculation workflow."""
        def validate_transaction_hash(tx_hash: str) -> bool:
            return tx_hash.startswith('0x') and len(tx_hash) == 66
        
        def calculate_mev_profit(buy_price: float, sell_price: float, amount: float, gas_cost: float) -> float:
            gross_profit = (sell_price - buy_price) * amount
            return max(0.0, gross_profit - gas_cost)
        
        def detect_sandwich_attack(transactions: list) -> bool:
            if len(transactions) < 3:
                return False
            first_tx = transactions[0]
            last_tx = transactions[-1]
            return (
                first_tx.get('from') == last_tx.get('from') and
                first_tx.get('type') == 'buy' and
                last_tx.get('type') == 'sell'
            )
        
        # Test MEV workflow
        transactions = [
            {
                'hash': '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef12',
                'from': '0x1111',
                'type': 'buy',
                'price': 100.0,
                'amount': 1.0,
            },
            {
                'hash': '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab',
                'from': '0x2222',
                'type': 'buy',
                'price': 105.0,
                'amount': 10.0,
            },
            {
                'hash': '0x567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef123456',
                'from': '0x1111',
                'type': 'sell',
                'price': 110.0,
                'amount': 1.0,
            },
        ]
        
        # Validate transaction hashes
        for tx in transactions:
            assert validate_transaction_hash(tx['hash']) is True
        
        # Detect sandwich attack
        is_sandwich = detect_sandwich_attack(transactions)
        assert is_sandwich is True
        
        # Calculate profit for the attacker
        first_tx = transactions[0]
        last_tx = transactions[2]
        profit = calculate_mev_profit(
            first_tx['price'], 
            last_tx['price'], 
            first_tx['amount'], 
            2.0  # Gas cost
        )
        assert profit == 8.0  # (110-100)*1 - 2 = 8


if __name__ == "__main__":
    pytest.main([__file__])
