// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../src/Create2CalcDeploy.sol";

contract DeployKnowledgeContract is Script {
    // Deployed Create2Factory address on Sepolia
    address constant FACTORY_ADDRESS = 0x35B586834b11dCa235B1007Faa312AA523aB6802;

    function run() external {
        // Start broadcasting transactions
        vm.startBroadcast();

        // Get the deployed factory
        Create2Factory factory = Create2Factory(FACTORY_ADDRESS);

        // Example 1: Deploy with SemID as salt
        // Using a simple salt for demonstration (normally this would be generated from text)
        bytes32 salt = keccak256(abi.encodePacked("Hello SemID World"));

        // Sample data to store
        bytes memory data = abi.encodePacked(uint256(12345));
        string memory decodeInfo = "uint256";
        string memory arbitraryInfo = "Sample knowledge entry using SemID";

        console.log("Deploying KnowledgeContract with salt:", vm.toString(salt));
        console.log("Data:", vm.toString(data));
        console.log("Decode Info:", decodeInfo);
        console.log("Arbitrary Info:", arbitraryInfo);

        // Deploy and initialize the contract
        address deployedAddress = factory.deployAndInitialize(
            salt,
            data,
            decodeInfo,
            arbitraryInfo
        );

        console.log("KnowledgeContract deployed at:", deployedAddress);

        // Verify the deployment by predicting the address
        address predictedAddress = factory.computeCreate2Address(salt);
        console.log("Predicted address:", predictedAddress);
        console.log("Addresses match:", deployedAddress == predictedAddress);

        // Stop broadcasting
        vm.stopBroadcast();
    }
}
