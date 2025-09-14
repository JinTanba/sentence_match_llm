#!/usr/bin/env python3
"""
Test script for blockchain integration functionality

This script demonstrates how to use the SemID + Create2Factory integration.
Run this after setting up your blockchain environment variables.
"""

import os
import json
from gold import SemID
from blockchain_integration import BlockchainConnector, SemIDBlockchainDeployer

def test_semid_generation():
    """Test SemID generation"""
    print("=== Testing SemID Generation ===")

    semid = SemID()
    test_texts = [
        "Hello world",
        "This is a test message",
        "Machine learning is fascinating",
        "The weather is beautiful today"
    ]

    for text in test_texts:
        semid_val = semid.id24(text)
        semid_hex = semid.id_hex(text)
        print(f"Text: '{text}'")
        print(f"SemID: {semid_val} (0x{semid_hex})")
        print(f"Salt (32 bytes): 0x{semid_val.to_bytes(32, 'big').hex()}")
        print()

def test_blockchain_connection():
    """Test blockchain connection (requires environment variables)"""
    print("=== Testing Blockchain Connection ===")

    rpc_url = os.getenv("BLOCKCHAIN_RPC_URL")
    private_key = os.getenv("BLOCKCHAIN_PRIVATE_KEY")
    factory_address = os.getenv("CREATE2_FACTORY_ADDRESS")

    if not rpc_url:
        print("❌ BLOCKCHAIN_RPC_URL not set. Skipping blockchain tests.")
        return None

    try:
        print(f"Connecting to: {rpc_url}")
        connector = BlockchainConnector(
            rpc_url=rpc_url,
            private_key=private_key,
            factory_address=factory_address
        )

        print("✅ Connected to blockchain")
        print(f"Chain ID: {connector.w3.eth.chain_id}")

        if connector.account:
            balance = connector.w3.from_wei(
                connector.w3.eth.get_balance(connector.account.address), 'ether'
            )
            print(f"Account: {connector.account.address}")
            print(f"Balance: {balance} ETH")
        else:
            print("⚠️  No private key provided - read-only mode")

        if connector.factory_address:
            print(f"Factory Address: {connector.factory_address}")
        else:
            print("⚠️  No factory address provided")

        return connector

    except Exception as e:
        print(f"❌ Blockchain connection failed: {e}")
        return None

def test_address_prediction(connector, semid):
    """Test address prediction"""
    if not connector:
        return

    print("\n=== Testing Address Prediction ===")

    test_text = "This is a sample knowledge entry for testing."
    print(f"Test Text: '{test_text}'")

    try:
        # Generate SemID and salt
        semid_val = semid.id24(test_text)
        salt = semid_val.to_bytes(32, 'big')

        print(f"SemID: {semid_val}")
        print(f"Salt: 0x{salt.hex()}")

        # Compute predicted address
        predicted_address = connector.compute_address(salt)
        print(f"Predicted Address: {predicted_address}")

        # Check if already deployed
        is_deployed = connector.is_contract_deployed(predicted_address)
        print(f"Already Deployed: {is_deployed}")

    except Exception as e:
        print(f"❌ Address prediction failed: {e}")

def test_full_deployment(connector, semid):
    """Test full deployment (requires private key and factory)"""
    if not connector or not connector.account or not connector.factory_address:
        print("\n⚠️  Skipping deployment test - requires private key and factory address")
        return

    print("\n=== Testing Full Deployment ===")

    test_text = "This is my first knowledge base entry via SemID."
    test_data = b"Hello Blockchain World!"
    test_decode_info = "string"
    test_arbitrary_info = "Test entry from SemID system"

    try:
        deployer = SemIDBlockchainDeployer(semid, connector)

        print(f"Deploying with text: '{test_text}'")
        print(f"Data: {test_data.hex()}")
        print(f"Decode Info: {test_decode_info}")

        result = deployer.deploy_from_text(
            text=test_text,
            data=test_data,
            decode_info=test_decode_info,
            arbitrary_info=test_arbitrary_info,
            gas_limit=3000000
        )

        print("\n✅ Deployment Result:")
        print(json.dumps(result, indent=2, default=str))

        # Verify contract info
        if result["deployed_address"]:
            print(f"\n=== Verifying Contract at {result['deployed_address']} ===")
            contract_info = connector.get_contract_info(result["deployed_address"])
            print("Contract Data:", contract_info["data"])
            print("Decode Info:", contract_info["decode_info"])
            print("Arbitrary Info:", contract_info["arbitrary_info"])

    except Exception as e:
        print(f"❌ Deployment failed: {e}")

def main():
    """Main test function"""
    print("🚀 Testing SemID + Blockchain Integration\n")

    # Test SemID generation
    semid = SemID()
    test_semid_generation()

    # Test blockchain connection
    connector = test_blockchain_connection()

    if connector:
        # Test address prediction
        test_address_prediction(connector, semid)

        # Test full deployment
        test_full_deployment(connector, semid)

    print("\n🎉 Test completed!")

if __name__ == "__main__":
    main()
