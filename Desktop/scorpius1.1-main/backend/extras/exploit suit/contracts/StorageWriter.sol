
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract StorageWriter {
    function writeSlot(uint256 slot, uint256 value) external {
        assembly {
            sstore(slot, value)
        }
    }
}
