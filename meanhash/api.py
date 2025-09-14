from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Tuple, Dict, Any
from gold import SemID
from blockchain_integration import BlockchainConnector, SemIDBlockchainDeployer
import os

app = FastAPI(
    title="SemID + Blockchain API",
    description="テキストのSemID（Semantic ID）を生成し、ブロックチェーン上のCreate2FactoryでコントラクトをデプロイするAPI",
    version="1.0.0"
)

# SemIDインスタンスをグローバルに作成（モデルロードを一度だけ）
semid_instance = SemID()

# ブロックチェーンコネクタ（環境変数から設定）
blockchain_connector: Optional[BlockchainConnector] = None
deployer: Optional[SemIDBlockchainDeployer] = None

def get_blockchain_connector() -> BlockchainConnector:
    """Get or create blockchain connector from environment variables"""
    global blockchain_connector

    if blockchain_connector is None:
        rpc_url = os.getenv("BLOCKCHAIN_RPC_URL")
        private_key = os.getenv("BLOCKCHAIN_PRIVATE_KEY")
        factory_address = os.getenv("CREATE2_FACTORY_ADDRESS")

        if not rpc_url:
            raise HTTPException(
                status_code=500,
                detail="Blockchain RPC URL not configured. Set BLOCKCHAIN_RPC_URL environment variable."
            )

        try:
            blockchain_connector = BlockchainConnector(
                rpc_url=rpc_url,
                private_key=private_key,
                factory_address=factory_address
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to blockchain: {e}")

    return blockchain_connector

def get_deployer() -> SemIDBlockchainDeployer:
    """Get or create SemID blockchain deployer"""
    global deployer

    if deployer is None:
        connector = get_blockchain_connector()
        deployer = SemIDBlockchainDeployer(semid_instance, connector)

    return deployer

class TextInput(BaseModel):
    text: str

class SemIDResponse(BaseModel):
    text: str
    semid: int
    semid_hex: str
    semid_bytes: str

class SemIDHexResponse(BaseModel):
    text: str
    semid_hex: str

class SemIDBytesResponse(BaseModel):
    text: str
    semid_bytes: str

class SemIDPartsResponse(BaseModel):
    text: str
    head0: int
    head1: int
    combined: int

class BlockchainConfig(BaseModel):
    rpc_url: str
    private_key: Optional[str] = None
    factory_address: Optional[str] = None

class DeployRequest(BaseModel):
    text: str
    data: Optional[str] = ""  # Hex-encoded bytes
    decode_info: Optional[str] = ""
    arbitrary_info: Optional[str] = ""
    gas_limit: Optional[int] = None

class DeployResponse(BaseModel):
    text: str
    semid: int
    semid_hex: str
    salt: str
    predicted_address: str
    deployed_address: str
    already_deployed: bool
    transaction_hash: Optional[str] = None
    contract_info: Optional[Dict[str, Any]] = None

@app.post("/semid", response_model=SemIDResponse)
async def get_semid(input_data: TextInput):
    """
    テキストからSemIDを生成します。

    - **text**: 入力テキスト
    """
    try:
        semid = semid_instance.id24(input_data.text)
        semid_hex = semid_instance.id_hex(input_data.text)
        semid_bytes = semid_instance.id_bytes(input_data.text).hex()

        return SemIDResponse(
            text=input_data.text,
            semid=semid,
            semid_hex=semid_hex,
            semid_bytes=semid_bytes
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/semid/hex", response_model=SemIDHexResponse)
async def get_semid_hex(input_data: TextInput):
    """
    テキストから16進数のSemIDを生成します。

    - **text**: 入力テキスト
    """
    try:
        semid_hex = semid_instance.id_hex(input_data.text)

        return SemIDHexResponse(
            text=input_data.text,
            semid_hex=semid_hex
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/semid/bytes", response_model=SemIDBytesResponse)
async def get_semid_bytes(input_data: TextInput):
    """
    テキストからバイト列のSemIDを生成します。

    - **text**: 入力テキスト
    """
    try:
        semid_bytes = semid_instance.id_bytes(input_data.text).hex()

        return SemIDBytesResponse(
            text=input_data.text,
            semid_bytes=semid_bytes
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/semid/parts", response_model=SemIDPartsResponse)
async def get_semid_parts(input_data: TextInput):
    """
    テキストからSemIDの各部分を取得します（デバッグ用）。

    - **text**: 入力テキスト
    """
    try:
        head0, head1, combined = semid_instance.id_parts(input_data.text)

        return SemIDPartsResponse(
            text=input_data.text,
            head0=head0,
            head1=head1,
            combined=combined
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}

# ===== ブロックチェーン統合エンドポイント =====

@app.post("/blockchain/configure", response_model=Dict[str, str])
async def configure_blockchain(config: BlockchainConfig):
    """
    ブロックチェーン接続を設定します。

    - **rpc_url**: ブロックチェーンRPCエンドポイントURL
    - **private_key**: トランザクション署名用の秘密鍵（オプション）
    - **factory_address**: Create2Factoryコントラクトアドレス（オプション）
    """
    global blockchain_connector, deployer

    try:
        blockchain_connector = BlockchainConnector(
            rpc_url=config.rpc_url,
            private_key=config.private_key,
            factory_address=config.factory_address
        )

        deployer = SemIDBlockchainDeployer(semid_instance, blockchain_connector)

        response = {"status": "configured", "rpc_url": config.rpc_url}
        if config.factory_address:
            response["factory_address"] = config.factory_address
        if config.private_key:
            response["account"] = blockchain_connector.account.address if blockchain_connector.account else None

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration failed: {e}")

@app.post("/blockchain/deploy", response_model=DeployResponse)
async def deploy_contract(deploy_request: DeployRequest):
    """
    テキストからSemIDを生成し、Create2FactoryでKnowledgeContractをデプロイします。

    - **text**: SemID生成用の入力テキスト
    - **data**: コントラクトに保存するバイナリデータ（16進数エンコード）
    - **decode_info**: データのデコード方法説明
    - **arbitrary_info**: 任意の文字列情報（空の場合はtextを使用）
    - **gas_limit**: ガスリミット（オプション）
    """
    try:
        deployer_instance = get_deployer()

        # Convert hex data to bytes if provided
        data_bytes = bytes.fromhex(deploy_request.data) if deploy_request.data else b""

        result = deployer_instance.deploy_from_text(
            text=deploy_request.text,
            data=data_bytes,
            decode_info=deploy_request.decode_info,
            arbitrary_info=deploy_request.arbitrary_info,
            gas_limit=deploy_request.gas_limit
        )

        return DeployResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deployment failed: {e}")

@app.get("/blockchain/status")
async def blockchain_status():
    """
    ブロックチェーン接続のステータスを取得します。
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
            status["account_address"] = connector.account.address
            status["account_balance"] = connector.w3.from_wei(
                connector.w3.eth.get_balance(connector.account.address), 'ether'
            )

        if connector.factory_address:
            status["factory_address"] = connector.factory_address

        return status

    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }

@app.get("/blockchain/contract/{address}")
async def get_contract_info(address: str):
    """
    指定されたアドレスのKnowledgeContract情報を取得します。

    - **address**: コントラクトアドレス
    """
    try:
        connector = get_blockchain_connector()
        contract_info = connector.get_contract_info(address)
        return contract_info

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get contract info: {e}")

@app.get("/blockchain/predict/{text}")
async def predict_address(text: str):
    """
    テキストからSemIDを生成し、予測されるコントラクトアドレスを計算します。

    - **text**: SemID生成用の入力テキスト
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
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 