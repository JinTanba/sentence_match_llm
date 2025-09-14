// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../src/Create2CalcDeploy.sol";

contract DeployWithSemID is Script {
    // Deployed Create2Factory address on Sepolia
    address constant FACTORY_ADDRESS = 0x35B586834b11dCa235B1007Faa312AA523aB6802;

    function run() external {
        // Start broadcasting transactions
        vm.startBroadcast();

        // Get the deployed factory
        Create2Factory factory = Create2Factory(FACTORY_ADDRESS);

        // Use SemID as salt - generated from: "This is a knowledge base entry about artificial intelligence and machine learning."
        bytes32 salt = 0x000000000000000000000000000000000000000000000000000000000022cd48;

        // Knowledge data about AI/ML
        bytes memory data = abi.encodePacked(
            uint256(2024),  // Year
            uint256(85),    // Confidence score
            uint256(42)     // Category ID
        );
        string memory decodeInfo = "(uint256 year, uint256 confidence, uint256 category)";
        string memory arbitraryInfo = "This is a knowledge base entry about artificial intelligence and machine learning.";

        console.log("Deploying KnowledgeContract with SemID salt");
        console.log("Salt:", vm.toString(salt));
        console.log("Original Text: This is a knowledge base entry about artificial intelligence and machine learning.");
        console.log("Data:", vm.toString(data));
        console.log("Decode Info:", decodeInfo);

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
