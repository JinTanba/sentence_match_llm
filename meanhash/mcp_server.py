from typing import Any, Optional, Dict
import httpx
import os
from mcp.server.fastmcp import FastMCP
from core import SemID
from blockchain_integration import BlockchainConnector, SemIDBlockchainDeployer

# Initialize FastMCP server
mcp = FastMCP("meanhash")

# SemIDインスタンスをグローバルに作成（モデルロードを一度だけ）
semid_instance = SemID()
private_key = os.getenv("BLOCKCHAIN_PRIVATE_KEY")

# ブロックチェーンコネクタ（環境変数から設定）
blockchain_connector: Optional[BlockchainConnector] = None
deployer: Optional[SemIDBlockchainDeployer] = None

def get_blockchain_connector() -> BlockchainConnector:
    """Get or create blockchain connector from environment variables"""
    global blockchain_connector

    if blockchain_connector is None:
        rpc_url = "https://eth-sepolia.g.alchemy.com/v2/xCvVMlO5hVjJ6_w5uJ4EQjSZ0RKiI7ym"
        factory_address = "0x35B586834b11dCa235B1007Faa312AA523aB6802"

        if not rpc_url:
            raise ValueError("BLOCKCHAIN_RPC_URL environment variable not set")

        try:
            blockchain_connector = BlockchainConnector(
                rpc_url=rpc_url,
                private_key=private_key,
                factory_address=factory_address
            )
        except Exception as e:
            raise ValueError(f"Failed to connect to blockchain: {e}")

    return blockchain_connector

def get_deployer() -> SemIDBlockchainDeployer:
    """Get or create SemID blockchain deployer"""
    global deployer

    if deployer is None:
        connector = get_blockchain_connector()
        deployer = SemIDBlockchainDeployer(semid_instance, connector)

    return deployer


@mcp.tool()
def calc_semid_int(text: str) -> int:
    """
    Calculate the Semantic ID (SemID) of the given text.
    Returns a 24-bit semantic ID as an integer.

    Args:
        text: Input text to generate SemID for

    Returns:
        Integer representation of the 24-bit SemID
    """
    try:
        return semid_instance.id24(text)
    except Exception as e:
        raise ValueError(f"Error calculating SemID: {str(e)}")


@mcp.tool()
def calc_semid(text: str) -> str:
    """
    Calculate the Semantic ID (SemID) of the given text.
    Returns a 24-bit semantic ID in hexadecimal format.

    Args:
        text: Input text to generate SemID for

    Returns:
        Hexadecimal representation of the 24-bit SemID
    """
    try:
        return semid_instance.id_hex(text)
    except Exception as e:
        return f"Error: {str(e)}"




@mcp.tool()
def calc_semid_bytes(text: str) -> str:
    """
    Calculate the Semantic ID (SemID) of the given text.
    Returns a 24-bit semantic ID as bytes in hex format.

    Args:
        text: Input text to generate SemID for

    Returns:
        Hexadecimal string of the 3-byte SemID
    """
    try:
        return semid_instance.id_bytes(text).hex()
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def compare_semid_texts(text1: str, text2: str) -> dict:
    """
    Compare two texts by their Semantic IDs and return similarity information.

    Args:
        text1: First text to compare
        text2: Second text to compare

    Returns:
        Dictionary containing SemIDs and their comparison
    """
    try:
        id1 = semid_instance.id24(text1)
        id2 = semid_instance.id24(text2)
        hex1 = semid_instance.id_hex(text1)
        hex2 = semid_instance.id_hex(text2)

        # Calculate Hamming distance between the 24-bit IDs
        hamming_distance = (id1 ^ id2).bit_count()

        return {
            "text1": text1,
            "text2": text2,
            "semid1": id1,
            "semid2": id2,
            "hex1": hex1,
            "hex2": hex2,
            "hamming_distance": hamming_distance,
            "max_distance": 24,
            "similarity_score": 1.0 - (hamming_distance / 24.0)
        }
    except Exception as e:
        return {"error": str(e)}


# ===== Blockchain Integration Tools =====

@mcp.tool()
def blockchain_status() -> Dict[str, Any]:
    """
    Get the current blockchain connection status and configuration.

    Returns:
        Dictionary containing connection status, chain info, and account details
    """
    try:
        connector = get_blockchain_connector()

        status = {
            "connected": connector.w3.is_connected(),
            "chain_id": connector.w3.eth.chain_id,
            "factory_configured": connector.factory_address is not None,
            "account_configured": connector.account is not None,
        }

        if connector.account:
            balance = connector.w3.from_wei(
                connector.w3.eth.get_balance(connector.account.address), 'ether'
            )
            status.update({
                "account_address": connector.account.address,
                "account_balance": float(balance),
            })

        if connector.factory_address:
            status["factory_address"] = connector.factory_address

        return status

    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }


@mcp.tool()
def predict_contract_address(text: str) -> Dict[str, Any]:
    """
    Predict the contract address that would be deployed for the given text using SemID.

    Args:
        text: Input text to generate SemID and predict address for

    Returns:
        Dictionary containing SemID info and predicted contract address
    """
    try:
        connector = get_blockchain_connector()

        # Generate SemID and convert to 32-byte salt
        semid_value = semid_instance.id24(text)
        salt = semid_value.to_bytes(32, 'big')

        predicted_address = connector.compute_address(salt)
        is_deployed = connector.is_contract_deployed(predicted_address)

        return {
            "text": text,
            "semid": semid_value,
            "semid_hex": semid_instance.id_hex(text),
            "salt": salt.hex(),
            "predicted_address": predicted_address,
            "is_deployed": is_deployed
        }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def deploy_contract_from_text(
    text: str,
    data: Optional[str] = "",
    decode_info: Optional[str] = "",
    arbitrary_info: Optional[str] = "",
    gas_limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generate SemID from text and deploy a KnowledgeContract using Create2.

    Args:
        text: Input text to generate SemID for deployment
        data: Hex-encoded binary data to store in contract (optional)
        decode_info: String describing how to decode the data (optional)
        arbitrary_info: Additional string info (optional, uses text if empty)
        gas_limit: Gas limit for deployment transaction (optional)

    Returns:
        Dictionary containing deployment result information
    """
    try:
        deployer_instance = get_deployer()

        # Convert hex data to bytes if provided
        data_bytes = bytes.fromhex(data) if data else b""

        result = deployer_instance.deploy_from_text(
            text=text,
            data=data_bytes,
            decode_info=decode_info,
            arbitrary_info=arbitrary_info,
            gas_limit=gas_limit
        )

        return result

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_contract_info(address: str) -> Dict[str, Any]:
    """
    Get information from a deployed KnowledgeContract.

    Args:
        address: Contract address to query

    Returns:
        Dictionary containing contract data, decode info, and arbitrary info
    """
    try:
        connector = get_blockchain_connector()
        contract_info = connector.get_contract_info(address)

        return contract_info

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def configure_blockchain_connection(
    rpc_url: str,
    private_key: Optional[str] = None,
    factory_address: Optional[str] = None
) -> Dict[str, str]:
    """
    Configure the blockchain connection with new parameters.

    Args:
        rpc_url: Blockchain RPC endpoint URL
        private_key: Private key for transaction signing (optional)
        factory_address: Create2Factory contract address (optional)

    Returns:
        Dictionary containing configuration status
    """
    global blockchain_connector, deployer

    try:
        blockchain_connector = BlockchainConnector(
            rpc_url=rpc_url,
            private_key=private_key,
            factory_address=factory_address
        )

        deployer = SemIDBlockchainDeployer(semid_instance, blockchain_connector)

        response = {"status": "configured", "rpc_url": rpc_url}
        if factory_address:
            response["factory_address"] = factory_address
        if private_key:
            response["account"] = blockchain_connector.account.address if blockchain_connector.account else None

        return response

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def deploy_contract_from_semid(
    semid: int,
    data: Optional[str] = "",
    decode_info: Optional[str] = "",
    arbitrary_info: Optional[str] = "",
    gas_limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Deploy a KnowledgeContract using a provided SemID value.

    Args:
        semid: 24-bit SemID integer value
        data: Hex-encoded binary data to store in contract (optional)
        decode_info: String describing how to decode the data (optional)
        arbitrary_info: Additional string info (optional)
        gas_limit: Gas limit for deployment transaction (optional)

    Returns:
        Dictionary containing deployment result information
    """
    try:
        connector = get_blockchain_connector()

        if not connector.account:
            return {"error": "Private key not configured - cannot deploy contracts"}

        if not connector.factory_address:
            return {"error": "Factory address not configured"}

        # Convert SemID to 32-byte salt
        if semid < 0 or semid > 0xFFFFFF:  # 24-bit max
            return {"error": "SemID must be a 24-bit value (0-16777215)"}

        salt = semid.to_bytes(32, 'big')
        data_bytes = bytes.fromhex(data) if data else b""

        # Deploy contract
        tx_hash, deployed_address = connector.deploy_contract(
            salt=salt,
            data=data_bytes,
            decode_info=decode_info,
            arbitrary_info=arbitrary_info,
            gas_limit=gas_limit
        )

        return {
            "semid": semid,
            "semid_hex": semid.to_bytes(3, 'big').hex(),
            "salt": salt.hex(),
            "deployed_address": deployed_address,
            "transaction_hash": tx_hash,
            "data": data,
            "decode_info": decode_info,
            "arbitrary_info": arbitrary_info
        }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def find_contract_by_text(text: str) -> Dict[str, Any]:
    """
    Find an existing KnowledgeContract deployed with the SemID of the given text.

    Args:
        text: Input text to find contract for

    Returns:
        Dictionary containing contract info if found, or deployment prediction if not found
    """
    try:
        connector = get_blockchain_connector()

        # Generate SemID and predict address
        semid_value = semid_instance.id24(text)
        salt = semid_value.to_bytes(32, 'big')
        predicted_address = connector.compute_address(salt)

        # Check if contract exists
        if connector.is_contract_deployed(predicted_address):
            # Get contract info
            contract_info = connector.get_contract_info(predicted_address)
            return {
                "found": True,
                "text": text,
                "semid": semid_value,
                "semid_hex": semid_instance.id_hex(text),
                "contract_address": predicted_address,
                "contract_info": contract_info
            }
        else:
            return {
                "found": False,
                "text": text,
                "semid": semid_value,
                "semid_hex": semid_instance.id_hex(text),
                "predicted_address": predicted_address,
                "message": "Contract not found. Use deploy_contract_from_text to deploy it."
            }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def find_similar_contracts(text: str, max_distance: int = 3, sample_size: int = 1000) -> Dict[str, Any]:
    """
    Find KnowledgeContracts deployed with similar SemIDs (within Hamming distance).
    Uses sampling approach for efficiency.

    Args:
        text: Input text to find similar contracts for
        max_distance: Maximum Hamming distance to search (default: 3)
        sample_size: Number of random SemIDs to sample for search (default: 1000)

    Returns:
        Dictionary containing similar contracts found
    """
    try:
        import random
        connector = get_blockchain_connector()

        # Generate base SemID
        base_semid = semid_instance.id24(text)
        results = []

        # Sample random SemIDs and check for deployed contracts within distance
        checked_semids = set()
        random.seed(base_semid)  # Deterministic sampling based on base SemID

        for _ in range(sample_size):
            # Generate a random SemID
            candidate_semid = random.randint(0, 2**24 - 1)

            if candidate_semid in checked_semids:
                continue
            checked_semids.add(candidate_semid)

            # Check Hamming distance
            distance = (candidate_semid ^ base_semid).bit_count()
            if distance <= max_distance and distance > 0:
                salt = candidate_semid.to_bytes(32, 'big')
                predicted_address = connector.compute_address(salt)

                if connector.is_contract_deployed(predicted_address):
                    try:
                        contract_info = connector.get_contract_info(predicted_address)
                        results.append({
                            "semid": candidate_semid,
                            "semid_hex": candidate_semid.to_bytes(3, 'big').hex(),
                            "hamming_distance": distance,
                            "contract_address": predicted_address,
                            "contract_info": contract_info
                        })

                        # Limit results to prevent too many responses
                        if len(results) >= 10:
                            break
                    except Exception:
                        # Skip if contract info can't be retrieved
                        continue

            if len(results) >= 10:
                break

        return {
            "search_text": text,
            "base_semid": base_semid,
            "base_semid_hex": semid_instance.id_hex(text),
            "max_distance": max_distance,
            "sample_size": sample_size,
            "found_contracts": results,
            "total_found": len(results),
            "note": f"Sampled {len(checked_semids)} SemIDs, found {len(results)} similar contracts"
        }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def update_contract_data(
    contract_address: str,
    new_data: str,
    new_decode_info: str,
    new_arbitrary_info: str
) -> Dict[str, Any]:
    """
    Update data in an existing KnowledgeContract (requires ownership).

    Args:
        contract_address: Address of the contract to update
        new_data: New hex-encoded binary data
        new_decode_info: New decode information string
        new_arbitrary_info: New arbitrary information string

    Returns:
        Dictionary containing update transaction result
    """
    try:
        connector = get_blockchain_connector()

        if not connector.account:
            return {"error": "Private key not configured - cannot update contracts"}

        # Note: This would require a contract with update functionality
        # For now, this is a placeholder as the current KnowledgeContract
        # doesn't have update functions after initialization

        return {
            "error": "Update functionality not implemented in current contract version. " +
                    "The KnowledgeContract is immutable after initialization."
        }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def batch_deploy_from_texts(
    texts: list,
    base_data: Optional[str] = "",
    base_decode_info: Optional[str] = "",
    gas_limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Deploy multiple KnowledgeContracts from a list of texts.

    Args:
        texts: List of text strings to deploy contracts for
        base_data: Base hex-encoded data for all contracts (optional)
        base_decode_info: Base decode info for all contracts (optional)
        gas_limit: Gas limit for each deployment (optional)

    Returns:
        Dictionary containing batch deployment results
    """
    try:
        deployer_instance = get_deployer()
        results = []

        for i, text in enumerate(texts):
            try:
                # Use text-specific arbitrary info
                arbitrary_info = text if not base_data else f"Entry {i+1}: {text[:50]}..."

                data_bytes = bytes.fromhex(base_data) if base_data else b""

                result = deployer_instance.deploy_from_text(
                    text=text,
                    data=data_bytes,
                    decode_info=base_decode_info,
                    arbitrary_info=arbitrary_info,
                    gas_limit=gas_limit
                )

                results.append({
                    "index": i,
                    "text": text,
                    "success": True,
                    "result": result
                })

            except Exception as e:
                results.append({
                    "index": i,
                    "text": text,
                    "success": False,
                    "error": str(e)
                })

        successful = sum(1 for r in results if r["success"])

        return {
            "total_texts": len(texts),
            "successful_deployments": successful,
            "failed_deployments": len(texts) - successful,
            "results": results
        }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_semid_contract_stats() -> Dict[str, Any]:
    """
    Get statistics about SemID-based contract deployments.

    Returns:
        Dictionary containing deployment statistics and patterns
    """
    try:
        connector = get_blockchain_connector()

        # This would require indexing deployed contracts
        # For now, return basic stats
        stats = {
            "factory_address": connector.factory_address,
            "chain_id": connector.w3.eth.chain_id,
            "account_address": connector.account.address if connector.account else None,
            "network_name": "Sepolia" if connector.w3.eth.chain_id == 11155111 else f"Chain {connector.w3.eth.chain_id}",
            "note": "Full statistics require contract indexing which is not implemented yet"
        }

        if connector.account:
            balance = connector.w3.from_wei(
                connector.w3.eth.get_balance(connector.account.address), 'ether'
            )
            stats["account_balance"] = float(balance)

        return stats

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_semid_knowledge_graph(
    texts: list,
    similarity_threshold: float = 0.8
) -> Dict[str, Any]:
    """
    Create a knowledge graph based on SemID similarities between texts.

    Args:
        texts: List of text strings to analyze
        similarity_threshold: Minimum similarity score (0.0-1.0) to create links

    Returns:
        Dictionary containing knowledge graph structure
    """
    try:
        nodes = []
        links = []

        # Create nodes
        for i, text in enumerate(texts):
            semid = semid_instance.id24(text)
            semid_hex = semid_instance.id_hex(text)

            nodes.append({
                "id": i,
                "text": text,
                "semid": semid,
                "semid_hex": semid_hex,
                "text_length": len(text)
            })

        # Create links based on similarity
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                text1, text2 = texts[i], texts[j]
                id1 = semid_instance.id24(text1)
                id2 = semid_instance.id24(text2)

                hamming_distance = (id1 ^ id2).bit_count()
                similarity = 1.0 - (hamming_distance / 24.0)

                if similarity >= similarity_threshold:
                    links.append({
                        "source": i,
                        "target": j,
                        "similarity": similarity,
                        "hamming_distance": hamming_distance,
                        "semid1": id1,
                        "semid2": id2
                    })

        return {
            "nodes": nodes,
            "links": links,
            "total_nodes": len(nodes),
            "total_links": len(links),
            "similarity_threshold": similarity_threshold,
            "average_similarity": sum(l["similarity"] for l in links) / len(links) if links else 0
        }

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run()
