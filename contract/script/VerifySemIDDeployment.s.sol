// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../src/KnowledgeContract.sol";

contract VerifySemIDDeployment is Script {
    // Deployed KnowledgeContract address using SemID
    address constant KNOWLEDGE_CONTRACT = 0x16746175F413e9EDCE093918E3C43fE3d1c8428e;

    function run() external view {
        // Get the deployed KnowledgeContract
        KnowledgeContract knowledge = KnowledgeContract(KNOWLEDGE_CONTRACT);

        console.log("Verifying SemID-based KnowledgeContract at:", KNOWLEDGE_CONTRACT);
        console.log("=====================================");

        // Read stored data
        bytes memory data = knowledge.getData();
        string memory decodeInfo = knowledge.getDecodeInfo();
        string memory arbitraryInfo = knowledge.getArbitraryInfo();

        console.log("Stored Data (hex):", vm.toString(data));
        console.log("Decode Info:", decodeInfo);
        console.log("Arbitrary Info:", arbitraryInfo);

        // Decode the data as (uint256 year, uint256 confidence, uint256 category)
        if (data.length == 96) { // 3 * 32 bytes
            (uint256 year, uint256 confidence, uint256 category) = abi.decode(data, (uint256, uint256, uint256));
            console.log("Decoded Data:");
            console.log("  Year:", year);
            console.log("  Confidence:", confidence);
            console.log("  Category:", category);
        }

        console.log("=====================================");
        console.log("SemID-based deployment verification complete!");
        console.log("This contract was deployed using salt generated from:");
        console.log("'This is a knowledge base entry about artificial intelligence and machine learning.'");
    }
}
