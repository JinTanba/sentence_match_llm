// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../src/KnowledgeContract.sol";

contract VerifyDeployment is Script {
    // Deployed KnowledgeContract address
    address constant KNOWLEDGE_CONTRACT = 0x3b59A62ce671295a1e95AC0F0E2316495FF88522;

    function run() external view {
        // Get the deployed KnowledgeContract
        KnowledgeContract knowledge = KnowledgeContract(KNOWLEDGE_CONTRACT);

        console.log("Verifying KnowledgeContract at:", KNOWLEDGE_CONTRACT);
        console.log("=====================================");

        // Read stored data
        bytes memory data = knowledge.getData();
        string memory decodeInfo = knowledge.getDecodeInfo();
        string memory arbitraryInfo = knowledge.getArbitraryInfo();

        console.log("Stored Data (hex):", vm.toString(data));
        console.log("Decode Info:", decodeInfo);
        console.log("Arbitrary Info:", arbitraryInfo);

        // Try to decode the data as uint256
        if (data.length == 32) {
            uint256 decodedValue = abi.decode(data, (uint256));
            console.log("Decoded as uint256:", decodedValue);
        }

        console.log("=====================================");
        console.log("Verification complete!");
    }
}
