"""
Blockchain Integration Module for SemID + Create2Factory

This module provides functionality to:
1. Connect to blockchain networks
2. Interact with Create2Factory contracts
3. Deploy KnowledgeContract instances using semantic IDs as salts
"""

import os
from typing import Optional, Dict, Any, Tuple
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_account.signers.local import LocalAccount
import json

# Create2Factory Contract ABI (extracted from Create2CalcDeploy.sol)
CREATE2_FACTORY_ABI = [
    {
        "inputs": [{"internalType": "bytes32", "name": "salt", "type": "bytes32"}],
        "name": "computeCreate2Address",
        "outputs": [{"internalType": "address", "name": "predictedAddress", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "salt", "type": "bytes32"}],
        "name": "deployWithCreate2",
        "outputs": [{"internalType": "address", "name": "deployedAddress", "type": "address"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "salt", "type": "bytes32"},
            {"internalType": "bytes", "name": "data", "type": "bytes"},
            {"internalType": "string", "name": "decodeInfo", "type": "string"},
            {"internalType": "string", "name": "arbitraryInfo", "type": "string"}
        ],
        "name": "deployAndInitialize",
        "outputs": [{"internalType": "address", "name": "deployedAddress", "type": "address"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "addr", "type": "address"},
            {"indexed": True, "internalType": "bytes32", "name": "salt", "type": "bytes32"}
        ],
        "name": "Deployed",
        "type": "event"
    }
]

# KnowledgeContract ABI (for verification)
KNOWLEDGE_CONTRACT_ABI = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [
            {"internalType": "bytes", "name": "data", "type": "bytes"},
            {"internalType": "string", "name": "decodeInfo", "type": "string"},
            {"internalType": "string", "name": "arbitraryInfo", "type": "string"}
        ],
        "name": "initialize",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getData",
        "outputs": [{"internalType": "bytes", "name": "", "type": "bytes"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getDecodeInfo",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getArbitraryInfo",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    }
]

class BlockchainConnector:
    """Blockchain connector for interacting with Create2Factory"""

    def __init__(self,
                 rpc_url: str,
                 private_key: Optional[str] = None,
                 factory_address: Optional[str] = None):
        """
        Initialize blockchain connector

        Args:
            rpc_url: RPC endpoint URL (e.g., "https://sepolia.infura.io/v3/YOUR_KEY")
            private_key: Private key for transaction signing (optional)
            factory_address: Create2Factory contract address (optional)
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

        # Add PoA middleware for networks like Polygon, BSC
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to {rpc_url}")

        self.account: Optional[LocalAccount] = None
        if private_key:
            self.account = Account.from_key(private_key)

        self.factory_address = factory_address
        self.factory_contract = None

        if factory_address:
            self._setup_factory_contract()

    def _setup_factory_contract(self):
        """Setup Create2Factory contract instance"""
        if not self.factory_address:
            raise ValueError("Factory address not provided")

        checksum_address = self.w3.to_checksum_address(self.factory_address)
        self.factory_contract = self.w3.eth.contract(
            address=checksum_address,
            abi=CREATE2_FACTORY_ABI
        )

    def set_factory_address(self, address: str):
        """Set the Create2Factory contract address"""
        self.factory_address = address
        self._setup_factory_contract()

    def compute_address(self, salt: bytes) -> str:
        """
        Compute the deterministic address for a KnowledgeContract

        Args:
            salt: 32-byte salt value

        Returns:
            Predicted contract address
        """
        if not self.factory_contract:
            raise ValueError("Factory contract not initialized")

        if len(salt) != 32:
            raise ValueError("Salt must be exactly 32 bytes")

        try:
            address = self.factory_contract.functions.computeCreate2Address(salt).call()
            return address
        except Exception as e:
            raise RuntimeError(f"Failed to compute address: {e}")

    def deploy_contract(self,
                       salt: bytes,
                       data: bytes = b"",
                       decode_info: str = "",
                       arbitrary_info: str = "",
                       gas_limit: Optional[int] = None) -> Tuple[str, str]:
        """
        Deploy KnowledgeContract using Create2

        Args:
            salt: 32-byte salt value
            data: Binary data to store
            decode_info: How to decode the data
            arbitrary_info: Additional string info
            gas_limit: Gas limit for transaction

        Returns:
            Tuple of (transaction_hash, deployed_address)
        """
        if not self.factory_contract or not self.account:
            raise ValueError("Factory contract and account must be initialized")

        if len(salt) != 32:
            raise ValueError("Salt must be exactly 32 bytes")

        try:
            # Estimate gas if not provided
            if gas_limit is None:
                gas_limit = 2000000  # Default gas limit

            # Build transaction
            if data or decode_info or arbitrary_info:
                # Use deployAndInitialize
                tx = self.factory_contract.functions.deployAndInitialize(
                    salt, data, decode_info, arbitrary_info
                ).build_transaction({
                    'from': self.account.address,
                    'gas': gas_limit,
                    'gasPrice': self.w3.eth.gas_price,
                    'nonce': self.w3.eth.get_transaction_count(self.account.address),
                })
            else:
                # Use deployWithCreate2 only
                tx = self.factory_contract.functions.deployWithCreate2(salt).build_transaction({
                    'from': self.account.address,
                    'gas': gas_limit,
                    'gasPrice': self.w3.eth.gas_price,
                    'nonce': self.w3.eth.get_transaction_count(self.account.address),
                })

            # Sign and send transaction
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            # Extract deployed address from Deployed event
            deployed_address = None
            for log in receipt.logs:
                try:
                    event = self.factory_contract.events.Deployed().process_log(log)
                    deployed_address = event.args.addr
                    break
                except:
                    continue

            if not deployed_address:
                # Fallback: compute address directly
                deployed_address = self.compute_address(salt)

            return tx_hash.hex(), deployed_address

        except Exception as e:
            raise RuntimeError(f"Failed to deploy contract: {e}")

    def get_contract_info(self, address: str) -> Dict[str, Any]:
        """
        Get information from a deployed KnowledgeContract

        Args:
            address: Contract address

        Returns:
            Dictionary with contract data
        """
        checksum_address = self.w3.to_checksum_address(address)
        contract = self.w3.eth.contract(
            address=checksum_address,
            abi=KNOWLEDGE_CONTRACT_ABI
        )

        try:
            data = contract.functions.getData().call()
            decode_info = contract.functions.getDecodeInfo().call()
            arbitrary_info = contract.functions.getArbitraryInfo().call()

            return {
                "address": address,
                "data": data.hex() if data else "",
                "decode_info": decode_info,
                "arbitrary_info": arbitrary_info
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get contract info: {e}")

    def is_contract_deployed(self, address: str) -> bool:
        """
        Check if a contract is already deployed at the given address

        Args:
            address: Contract address to check

        Returns:
            True if contract exists, False otherwise
        """
        checksum_address = self.w3.to_checksum_address(address)
        code = self.w3.eth.get_code(checksum_address)
        return len(code) > 0

class SemIDBlockchainDeployer:
    """Combined class for generating SemID and deploying to blockchain"""

    def __init__(self,
                 semid_instance,
                 blockchain_connector: BlockchainConnector):
        """
        Initialize SemID + Blockchain deployer

        Args:
            semid_instance: SemID instance for ID generation
            blockchain_connector: BlockchainConnector instance
        """
        self.semid = semid_instance
        self.blockchain = blockchain_connector

    def deploy_from_text(self,
                        text: str,
                        data: bytes = b"",
                        decode_info: str = "",
                        arbitrary_info: str = "",
                        gas_limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate SemID from text and deploy KnowledgeContract

        Args:
            text: Input text for SemID generation
            data: Binary data to store in contract
            decode_info: How to decode the data
            arbitrary_info: Additional string info (if empty, uses the input text)
            gas_limit: Gas limit for deployment

        Returns:
            Dictionary with deployment information
        """
        # Generate SemID and convert to 32-byte salt
        semid_value = self.semid.id24(text)
        salt = semid_value.to_bytes(32, 'big')  # Pad to 32 bytes

        # Compute predicted address
        predicted_address = self.blockchain.compute_address(salt)

        # Check if already deployed
        if self.blockchain.is_contract_deployed(predicted_address):
            # Get existing contract info
            contract_info = self.blockchain.get_contract_info(predicted_address)
            return {
                "text": text,
                "semid": semid_value,
                "semid_hex": self.semid.id_hex(text),
                "salt": salt.hex(),
                "predicted_address": predicted_address,
                "deployed_address": predicted_address,
                "already_deployed": True,
                "contract_info": contract_info,
                "transaction_hash": None
            }

        # Use text as arbitrary_info if not provided
        if not arbitrary_info:
            arbitrary_info = text

        # Deploy contract
        tx_hash, deployed_address = self.blockchain.deploy_contract(
            salt=salt,
            data=data,
            decode_info=decode_info,
            arbitrary_info=arbitrary_info,
            gas_limit=gas_limit
        )

        return {
            "text": text,
            "semid": semid_value,
            "semid_hex": self.semid.id_hex(text),
            "salt": salt.hex(),
            "predicted_address": predicted_address,
            "deployed_address": deployed_address,
            "already_deployed": False,
            "transaction_hash": tx_hash
        }
