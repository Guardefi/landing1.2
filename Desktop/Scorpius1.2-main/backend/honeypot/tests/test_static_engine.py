"""
Tests for the static analysis engine
"""
import pytest
from core.engines.static_engine import StaticEngine


def test_static_engine_init():
    """Test static engine initialization"""
    engine = StaticEngine()
    assert engine is not None
    assert len(engine.patterns) > 0
    assert "hidden_state_manipulation" in engine.patterns
    assert "malicious_fallback" in engine.patterns


def test_analyze_benign_contract(sample_contract_data):
    """Test analyzing a benign contract"""
    engine = StaticEngine()

    # Simple Storage is a benign contract
    results = engine.analyze(sample_contract_data)

    assert results is not None
    assert "confidence" in results
    assert results["confidence"] < 0.3  # Should have low confidence of being honeypot
    assert len(results["techniques"]) == 0
    assert results["patterns_detected"] == 0


def test_analyze_honeypot_contract():
    """Test analyzing a contract with honeypot characteristics"""
    engine = StaticEngine()

    # Create contract data with honeypot characteristics
    contract_data = {
        "address": "0x1234567890123456789012345678901234567890",
        "chain_id": 1,
        "bytecode": "0x608060405260043610610041576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806341c0e1b514610046575b600080fd5b34801561005257600080fd5b5061005b61005d565b005b6000339050600073ffffffffffffffffffffffffffffffffffffffff168173ffffffffffffffffffffffffffffffffffffffff1614156100cf57600060405180807f4f6e6c79206f776e657220697320616c6c6f77656420746f2063616c6c20746881526020017f697320737566756e6374696f6e2e000000000000000000000000000000000000815250602e0190506040518091039020fd5b3373ffffffffffffffffffffffffffffffffffffffff16ff00a165627a7a7230582032c59f0247a959ee08569c8456e1b35a213a36088625adeb369ffa1a46228e3e0029",
        "source_code": """
        pragma solidity ^0.4.23;
        
        contract HoneyPot {
            function withdraw() public {
                address sender = msg.sender;
                if (sender == address(0)) {
                    revert("Only owner is allowed to call this function.");
                }
                selfdestruct(msg.sender);
            }
            
            function() payable public {
                // Fallback function to receive funds
            }
        }
        """,
        "contract_name": "HoneyPot",
        "transactions": [
            {
                "hash": "0xabc123",
                "from": "0xabcdef1234567890abcdef1234567890abcdef12",
                "to": "0x1234567890123456789012345678901234567890",
                "value": "1000000000000000000",
                "input": "0x",
                "blockNumber": "14000000",
            }
        ],
    }

    results = engine.analyze(contract_data)

    assert results is not None
    assert "confidence" in results
    assert (
        results["confidence"] > 0.5
    )  # Should have higher confidence of being honeypot
    assert len(results["techniques"]) > 0
    assert (
        "malicious_fallback" in results["techniques"]
        or "selfdestruct" in results["techniques"]
    )
    assert results["patterns_detected"] > 0


def test_analyze_missing_bytecode():
    """Test analyzing a contract with missing bytecode"""
    engine = StaticEngine()

    # Create contract data with missing bytecode
    contract_data = {
        "address": "0x1234567890123456789012345678901234567890",
        "chain_id": 1,
        "bytecode": None,
        "source_code": None,
    }

    results = engine.analyze(contract_data)

    assert results is not None
    assert "confidence" in results
    assert results["confidence"] == 0
    assert len(results["techniques"]) == 0
    assert results["patterns_detected"] == 0
    assert "error" in results


def test_analyze_complex_patterns():
    """Test analyzing complex bytecode patterns"""
    engine = StaticEngine()

    # Contract with balance checking patterns
    complex_bytecode = "0x608060405260043610610057576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806327e235e31461005c57806353a04b45146100b3578063aa8c217c146100c8575b600080fd5b34801561006857600080fd5b5061009d600480360381019080803573ffffffffffffffffffffffffffffffffffffffff1690602001909291905050506100f3565b6040518082815260200191505060405180910390f35b3480156100bf57600080fd5b506100c661010b565b005b3480156100d457600080fd5b506100dd61020b565b6040518082815260200191505060405180910390f35b60006020528060005260406000206000915090505481565b60003390506000600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054141561015957600080fd5b3073ffffffffffffffffffffffffffffffffffffffff1631600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020541015156101b957600080fd5b600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020543073ffffffffffffffffffffffffffffffffffffffff163103905080600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055505050565b60003073ffffffffffffffffffffffffffffffffffffffff163190509056fea165627a7a72305820ed097651c27c2e30ac14c7a3307a215d41651d135431e8ad8c1665b4cc42b9d70029"

    contract_data = {
        "address": "0x1234567890123456789012345678901234567890",
        "chain_id": 1,
        "bytecode": complex_bytecode,
        "source_code": """
        pragma solidity ^0.4.24;
        
        contract ComplexHoneypot {
            mapping(address => uint256) public balances;
            
            function withdraw() public {
                address sender = msg.sender;
                require(balances[msg.sender] > 0);
                require(address(this).balance >= balances[msg.sender]);
                uint amount = balances[msg.sender] - address(this).balance;
                balances[msg.sender] = amount;
            }
            
            function getBalance() public view returns (uint) {
                return address(this).balance;
            }
        }
        """,
    }

    results = engine.analyze(contract_data)

    assert results is not None
    assert results["confidence"] > 0
    assert "balance_checking" in results["techniques"]


def test_source_code_analysis():
    """Test analyzing source code patterns"""
    engine = StaticEngine()

    contract_data = {
        "address": "0x1234567890123456789012345678901234567890",
        "bytecode": "0x...",
        "source_code": """
        pragma solidity ^0.6.0;
        
        contract HiddenTransfer {
            address payable private owner;
            
            constructor() public {
                owner = msg.sender;
            }
            
            function deposit() public payable {
                // Just receive ETH
            }
            
            function withdraw() public {
                require(tx.origin == msg.sender);
                uint fee = address(this).balance / 10;
                owner.transfer(fee);
                msg.sender.transfer(address(this).balance);
            }
        }
        """,
    }

    results = engine.analyze(contract_data)

    assert results is not None
    assert "tx.origin" in results["techniques"]


def test_abi_analysis():
    """Test analyzing ABI for suspicious patterns"""
    engine = StaticEngine()

    contract_data = {
        "address": "0x1234567890123456789012345678901234567890",
        "bytecode": "0x...",
        "abi": [
            {
                "constant": False,
                "inputs": [],
                "name": "deposit",
                "outputs": [],
                "payable": True,
                "stateMutability": "payable",
                "type": "function",
            },
            {
                "constant": False,
                "inputs": [],
                "name": "withdraw",
                "outputs": [],
                "payable": False,
                "stateMutability": "nonpayable",
                "type": "function",
            },
            {
                "constant": False,
                "inputs": [],
                "name": "collectFees",
                "outputs": [],
                "payable": False,
                "stateMutability": "nonpayable",
                "type": "function",
            },
        ],
    }

    results = engine.analyze(contract_data)

    assert results is not None
    assert results["confidence"] > 0
