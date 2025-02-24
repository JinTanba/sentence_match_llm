// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "../src/GoalContract.sol";

/**
 * @title Create2Factory
 * @notice A factory that uses Create2 to deploy GoalContract deterministically.
 */
contract Create2Factory {
    event Deployed(address indexed addr, bytes32 indexed salt);

    /**
     * @dev Computes the deterministic address for a GoalContract deployed using this factory and a given salt.
     * @param salt The salt (hash) used for the Create2 deployment.
     * @return predictedAddress The computed address where the GoalContract will be deployed.
     */
    function computeCreate2Address(bytes32 salt) external view returns (address predictedAddress) {
        // Creation code of GoalContract
        bytes memory bytecode = type(GoalContract).creationCode;

        // Compute the keccak-256 for the final address:
        // keccak256(0xff, this, salt, keccak256(bytecode))[12..31]
        bytes32 hash = keccak256(
            abi.encodePacked(
                bytes1(0xff),
                address(this),
                salt,
                keccak256(bytecode)
            )
        );

        // Convert last 20 bytes of hash to an address
        predictedAddress = address(uint160(uint256(hash)));
    }

    /**
     * @dev Deploys GoalContract using Create2 at the address computed by `computeCreate2Address(salt)`.
     * @param salt The salt (hash) used for the Create2 deployment.
     * @return deployedAddress The address of the newly deployed GoalContract.
     */
    function deployWithCreate2(bytes32 salt) public returns (address deployedAddress) {
        bytes memory bytecode = type(GoalContract).creationCode;

        // Deploy the contract using Create2
        assembly {
            deployedAddress := create2(0, add(bytecode, 0x20), mload(bytecode), salt)
        }
        require(deployedAddress != address(0), "Create2: Failed on deploy");

        emit Deployed(deployedAddress, salt);
    }

    /**
     * @dev Convenience function: deploys the GoalContract and initializes it in one transaction.
     * @param salt The salt for Create2.
     * @param data Arbitrary bytes to store in the GoalContract.
     * @param decodeInfo A string describing how to decode `data`.
     * @param arbitraryInfo Another user-defined string.
     * @return deployedAddress The address of the newly deployed GoalContract.
     */
    function deployAndInitialize(
        bytes32 salt,
        bytes memory data,
        string memory decodeInfo,
        string memory arbitraryInfo
    ) external returns (address deployedAddress) {
        // 1) Deploy the contract via Create2
        deployedAddress = deployWithCreate2(salt);

        // 2) Immediately initialize it with the desired data
        GoalContract(deployedAddress).initialize(data, decodeInfo, arbitraryInfo);
    }
}
