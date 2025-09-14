// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Script.sol";
import "../src/Create2CalcDeploy.sol";

contract DeployFactory is Script {
    function run() external {
        // Start broadcasting transactions
        vm.startBroadcast();

        // Deploy the Create2Factory contract
        Create2Factory factory = new Create2Factory();

        // Log the deployed address
        console.log("Create2Factory deployed at:", address(factory));

        // Stop broadcasting
        vm.stopBroadcast();
    }
}
