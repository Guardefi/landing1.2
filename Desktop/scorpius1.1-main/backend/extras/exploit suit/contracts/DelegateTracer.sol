// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title DelegateTracer
 * @notice Contract to trace delegatecall execution
 * @dev Logs sender and data when called
 */
contract DelegateTracer {
    address public lastTarget;
    bytes public lastData;
    
    fallback() external payable {
        lastTarget = msg.sender;
        lastData = msg.data;
        
        // Return some data to avoid revert
        assembly {
            mstore(0, 1)
            return(0, 32)
        }
    }
}
