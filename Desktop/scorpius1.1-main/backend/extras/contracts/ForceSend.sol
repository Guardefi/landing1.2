// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract ForceSend {
    constructor() payable {}
    
    function go(address target) external {
        selfdestruct(payable(target));
    }
}
