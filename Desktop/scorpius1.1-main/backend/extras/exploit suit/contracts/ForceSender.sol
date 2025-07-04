// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title ForceSender
 * @notice Force send ETH via selfdestruct
 */
contract ForceSender {
    address payable public target;
    
    constructor() payable {
        require(msg.value > 0, "Send ETH");
    }
    
    function destroy(address payable _target) external {
        selfdestruct(_target);
    }
}
