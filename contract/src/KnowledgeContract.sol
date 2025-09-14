// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title ChildContract
 * @notice A contract intended to be deployed via Create2. It stores arbitrary bytes data
 *         along with information on how to decode it, plus an arbitrary string.
 * @dev The constructor has no arguments so that it can be deployed via Create2 without parameters.
 */
contract KnowledgeContract {
    // We store whether the contract has been initialized to prevent re-initialization.
    bool private _initialized;

    // Arbitrary binary data
    bytes private _data;

    // Information describing how to decode the above bytes
    string private _decodeInfo;

    // Additional arbitrary string (for labeling, notes, etc.)
    string private goalData;

    /**
     * @dev The constructor must remain empty (no arguments) for Create2 deployment.
     */
    constructor() {
        // No arguments
    }

    /**
     * @notice Initialize the contract with arbitrary data and decoding info.
     * @param data Arbitrary bytes that you want to store.
     * @param decodeInfo A string describing how to decode `data` (e.g., "uint256", "(address,uint256)", etc.).
     * @param arbitraryInfo Another user-defined string that can store a label, note, or any other info.
     */
    function initialize(bytes memory data, string memory decodeInfo, string memory arbitraryInfo) external {
        require(!_initialized, "ChildContract: Already initialized");
        _initialized = true;

        _data = data;
        
        _decodeInfo = decodeInfo;
        goalData = arbitraryInfo;
    }

    /**
     * @notice Retrieve the raw bytes stored.
     */
    function getData() external view returns (bytes memory) {
        return _data;
    }

    /**
     * @notice Retrieve the string that describes how to decode the stored bytes.
     */
    function getDecodeInfo() external view returns (string memory) {
        return _decodeInfo;
    }

    /**
     * @notice Retrieve the arbitrary string that was stored.
     */
    function getArbitraryInfo() external view returns (string memory) {
        return goalData;
    }
}
