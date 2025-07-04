// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title Create2Deployer
 * @notice Deploy contracts with CREATE2
 * @dev Try to find address collision
 */
contract Create2Deployer {
    function deploy(bytes32 salt, bytes memory bytecode) external returns (address) {
        address addr;
        assembly {
            addr := create2(0, add(bytecode, 0x20), mload(bytecode), salt)
        }
        require(addr != address(0), "Create2: Failed");
        return addr;
    }
    
    function computeAddress(bytes32 salt) external view returns (address) {
        bytes memory bytecode = type(DummyContract).creationCode;
        return computeAddress(salt, keccak256(bytecode));
    }
    
    function computeAddress(bytes32 salt, bytes32 bytecodeHash) public view returns (address) {
        return address(uint160(uint(keccak256(abi.encodePacked(
            bytes1(0xff),
            address(this),
            salt,
            bytecodeHash
        )))));
    }
}

contract DummyContract {
    uint256 public value = 42;
}
