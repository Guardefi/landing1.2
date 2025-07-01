// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title VulnerableContract
 * @dev A deliberately vulnerable contract for security testing purposes
 * WARNING: This contract contains multiple vulnerabilities and should NEVER be deployed to mainnet
 */
contract VulnerableContract {
    mapping(address => uint256) public balances;
    mapping(address => bool) public authorized;
    address public owner;
    bool private locked;
    
    event Deposit(address indexed user, uint256 amount);
    event Withdrawal(address indexed user, uint256 amount);
    event Transfer(address indexed from, address indexed to, uint256 amount);
    
    constructor() {
        owner = msg.sender;
        authorized[msg.sender] = true;
    }
    
    // VULNERABILITY 1: Reentrancy Attack
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // External call before state change (VULNERABLE)
        (bool success,) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        // State change after external call (VULNERABLE)
        balances[msg.sender] -= amount;
        
        emit Withdrawal(msg.sender, amount);
    }
    
    // VULNERABILITY 2: Integer Overflow/Underflow (pre-0.8.0 style)
    function unsafeAdd(uint256 a, uint256 b) external pure returns (uint256) {
        // This would overflow in older Solidity versions
        unchecked {
            return a + b;
        }
    }
    
    // VULNERABILITY 3: Access Control Issues
    function authorizeUser(address user) external {
        // Missing access control - anyone can authorize users
        authorized[user] = true;
    }
    
    // VULNERABILITY 4: Timestamp Dependence
    function timeLotteryBad() external view returns (bool) {
        // Using block.timestamp for randomness (VULNERABLE)
        return (block.timestamp % 2 == 0);
    }
    
    // VULNERABILITY 5: Unprotected Self-Destruct
    function destroy() external {
        // No access control on self-destruct (VULNERABLE)
        selfdestruct(payable(msg.sender));
    }
    
    // VULNERABILITY 6: Denial of Service with Failed Call
    function distributeRewards(address[] memory recipients) external {
        require(authorized[msg.sender], "Not authorized");
        
        uint256 reward = address(this).balance / recipients.length;
        
        for (uint i = 0; i < recipients.length; i++) {
            // If one transfer fails, all fail (VULNERABLE)
            (bool success,) = recipients[i].call{value: reward}("");
            require(success, "Transfer failed");
        }
    }
    
    // VULNERABILITY 7: Front-running
    function commitReveal(bytes32 commitment) external payable {
        require(msg.value > 0, "Must send ETH");
        // Predictable commitment scheme (VULNERABLE to front-running)
        balances[msg.sender] += msg.value;
    }
    
    // VULNERABILITY 8: Improper Input Validation
    function updateBalance(address user, uint256 newBalance) external {
        require(authorized[msg.sender], "Not authorized");
        // No validation of newBalance (VULNERABLE)
        balances[user] = newBalance;
    }
    
    // VULNERABILITY 9: State Variable Default Visibility
    uint256 private secretValue = 12345; // Still readable from blockchain
    
    function getSecret() external view returns (uint256) {
        return secretValue;
    }
    
    // VULNERABILITY 10: Unchecked External Calls
    function externalCall(address target, bytes memory data) external returns (bool) {
        require(authorized[msg.sender], "Not authorized");
        // Unchecked low-level call (VULNERABLE)
        (bool success,) = target.call(data);
        return success;
    }
    
    // VULNERABILITY 11: Oracle Manipulation Vulnerability
    function getPrice() external view returns (uint256) {
        // Simplified oracle that could be manipulated
        return address(this).balance * 100;
    }
    
    // VULNERABILITY 12: Flash Loan Attack Vulnerability
    function flashLoanVulnerable(uint256 amount) external {
        uint256 price = this.getPrice();
        require(price > 0, "Invalid price");
        
        // Vulnerable calculation based on manipulatable price
        uint256 tokens = (amount * 1000) / price;
        balances[msg.sender] += tokens;
    }
    
    // Deposit function
    function deposit() external payable {
        require(msg.value > 0, "Must send ETH");
        balances[msg.sender] += msg.value;
        emit Deposit(msg.sender, msg.value);
    }
    
    // Transfer function with potential vulnerabilities
    function transfer(address to, uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        require(to != address(0), "Invalid recipient");
        
        balances[msg.sender] -= amount;
        balances[to] += amount;
        
        emit Transfer(msg.sender, to, amount);
    }
    
    // Emergency withdrawal (vulnerable to reentrancy)
    function emergencyWithdraw() external {
        require(!locked, "Contract locked");
        locked = true;
        
        uint256 balance = balances[msg.sender];
        require(balance > 0, "No balance");
        
        // External call before state change (VULNERABLE)
        (bool success,) = msg.sender.call{value: balance}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] = 0;
        locked = false;
    }
    
    // View functions
    function getBalance(address user) external view returns (uint256) {
        return balances[user];
    }
    
    function isAuthorized(address user) external view returns (bool) {
        return authorized[user];
    }
    
    function getContractBalance() external view returns (uint256) {
        return address(this).balance;
    }
    
    // Fallback and receive functions
    receive() external payable {
        balances[msg.sender] += msg.value;
        emit Deposit(msg.sender, msg.value);
    }
    
    fallback() external payable {
        balances[msg.sender] += msg.value;
        emit Deposit(msg.sender, msg.value);
    }
} 