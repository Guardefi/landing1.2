// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

interface IVulnerableVault {
    function withdraw() external;
    function emergencyWithdraw() external;
    function drain() external;
    function deposit() external payable;
    
    // Common vulnerable patterns we'll test
    function delegatecall(address target, bytes calldata data) external payable returns (bytes memory);
    function execute(address target, uint256 value, bytes calldata data) external payable returns (bytes memory);
    function owner() external view returns (address);
    function balance() external view returns (uint256);
}
