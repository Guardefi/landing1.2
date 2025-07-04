// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title CallbackReceiver
 * @notice Contract to test callback patterns
 * @dev Receives calls and logs them
 */
contract CallbackReceiver {
    bool public wasCalled;
    address public lastCaller;
    bytes public lastData;
    
    fallback() external payable {
        wasCalled = true;
        lastCaller = msg.sender;
        lastData = msg.data;
    }
    
    receive() external payable {
        wasCalled = true;
        lastCaller = msg.sender;
    }
    
    function reset() external {
        wasCalled = false;
        lastCaller = address(0);
        lastData = "";
    }
}
