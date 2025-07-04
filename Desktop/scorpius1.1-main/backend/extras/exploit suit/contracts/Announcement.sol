
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Announcement {
    event SecurityUpgrade(address indexed oldVault, address indexed newVault, string message);
    
    function announceUpgrade(address oldVault, address newVault) external {
        emit SecurityUpgrade(
            oldVault,
            newVault,
            "CRITICAL: Security vulnerability found. Migrate to new vault immediately!"
        );
    }
}
