# Meanhash

Semantic ID generation using Golay codes with Blockchain Integration - テキストの意味的類似性を24ビットIDで表現し、Create2Factoryでブロックチェーン上にデプロイするシステム

## セットアップ

このプロジェクトは [uv](https://github.com/astral-sh/uv) を使用して依存関係を管理しています。

### 必要条件

- Python 3.13+
- uv

### インストール

```bash
# 仮想環境を作成して依存関係をインストール
uv sync
```

### ブロックチェーン設定

ブロックチェーン連携を使用するには、以下の環境変数を設定してください：

```bash
# 必須: RPC エンドポイント
export BLOCKCHAIN_RPC_URL="https://sepolia.infura.io/v3/YOUR_INFURA_KEY"

# 省略可能: トランザクション署名用の秘密鍵（設定しない場合は読み取り専用）
export BLOCKCHAIN_PRIVATE_KEY="your_private_key_here"

# 省略可能: デプロイ済みのCreate2Factoryコントラクトアドレス
export CREATE2_FACTORY_ADDRESS="0x..."

# 例: Sepoliaテストネットの場合
export BLOCKCHAIN_RPC_URL="https://sepolia.infura.io/v3/YOUR_INFURA_KEY"
export BLOCKCHAIN_PRIVATE_KEY="0x..."
export CREATE2_FACTORY_ADDRESS="0x1234567890123456789012345678901234567890"
```

**注意**: 秘密鍵は安全に管理してください。本番環境では決してコードにハードコーディングしないでください。

### 使用方法

```bash
# 仮想環境をアクティブ化
source .venv/bin/activate

# SemID の動作確認
python gold.py

# API サーバーを起動
python api.py

# MCP サーバーを起動
python mcp_server.py

# ブロックチェーン統合テストを実行
python test_blockchain_integration.py

# MCP クライアントから利用する場合（例: Claude Desktop）
# MCPサーバーが起動している状態で、Claude DesktopなどのMCPクライアントから利用可能

# MCPツールのテスト実行
python test_mcp_tools.py
```

## API エンドポイント

### SemID 生成
- `POST /semid` - テキストからSemIDを生成
- `POST /semid/hex` - 16進数形式のSemIDを生成
- `POST /semid/bytes` - バイト列形式のSemIDを生成
- `POST /semid/parts` - SemIDの各部分を取得（デバッグ用）
- `GET /health` - ヘルスチェック

### ブロックチェーン統合
- `POST /blockchain/configure` - ブロックチェーン接続を設定
- `POST /blockchain/deploy` - テキストからSemIDを生成し、Create2Factoryでコントラクトをデプロイ
- `GET /blockchain/status` - ブロックチェーン接続のステータスを取得
- `GET /blockchain/contract/{address}` - 指定されたアドレスのKnowledgeContract情報を取得
- `GET /blockchain/predict/{text}` - テキストからSemIDを生成し、予測されるコントラクトアドレスを計算

## MCP ツール

MCP (Model Context Protocol) を使用して、以下のツールを提供します：

### `calc_semid(text: str) -> str`
テキストから24ビットSemIDを16進数形式で生成します。

### `calc_semid_int(text: str) -> int`
テキストから24ビットSemIDを整数形式で生成します。

### `calc_semid_bytes(text: str) -> str`
テキストから24ビットSemIDをバイト列の16進数形式で生成します。

### `compare_semid_texts(text1: str, text2: str) -> dict`
2つのテキストのSemIDを比較し、ハミング距離と類似度を返します。

### ブロックチェーン統合ツール

#### `blockchain_status() -> dict`
ブロックチェーン接続のステータスと設定情報を取得します。

#### `predict_contract_address(text: str) -> dict`
テキストからSemIDを生成し、予測されるコントラクトアドレスを計算します。

#### `deploy_contract_from_text(text: str, data: str = "", decode_info: str = "", arbitrary_info: str = "", gas_limit: int = None) -> dict`
テキストからSemIDを生成し、Create2FactoryでKnowledgeContractをデプロイします。

#### `deploy_contract_from_semid(semid: int, data: str = "", decode_info: str = "", arbitrary_info: str = "", gas_limit: int = None) -> dict`
指定されたSemID値を使用してKnowledgeContractをデプロイします。

#### `get_contract_info(address: str) -> dict`
指定されたアドレスのKnowledgeContract情報を取得します。

#### `configure_blockchain_connection(rpc_url: str, private_key: str = None, factory_address: str = None) -> dict`
ブロックチェーン接続を新しいパラメータで設定します。

#### `find_contract_by_text(text: str) -> dict`
テキストからSemIDを生成し、対応するKnowledgeContractが存在するかを検索します。

#### `find_similar_contracts(text: str, max_distance: int = 3, sample_size: int = 1000) -> dict`
指定されたテキストに似たSemIDを持つKnowledgeContractを検索します。

#### `batch_deploy_from_texts(texts: list, base_data: str = "", base_decode_info: str = "", gas_limit: int = None) -> dict`
複数のテキストから一括でKnowledgeContractをデプロイします。

#### `get_semid_contract_stats() -> dict`
SemIDベースのコントラクトデプロイメントに関する統計情報を取得します。

#### `create_semid_knowledge_graph(texts: list, similarity_threshold: float = 0.8) -> dict`
複数のテキスト間のSemID類似度に基づいてナレッジグラフを作成します。

## 使用例

### 1. SemID の生成

```bash
# API サーバーを起動
python api.py

# 別のターミナルでテスト
curl -X POST "http://localhost:8000/semid" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test message."}'
```

### 2. ブロックチェーン統合

```bash
# ブロックチェーン設定
curl -X POST "http://localhost:8000/blockchain/configure" \
  -H "Content-Type: application/json" \
  -d '{
    "rpc_url": "https://sepolia.infura.io/v3/YOUR_KEY",
    "private_key": "YOUR_PRIVATE_KEY",
    "factory_address": "0x1234..."
  }'

# コントラクトデプロイ
curl -X POST "http://localhost:8000/blockchain/deploy" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is my knowledge base entry.",
    "data": "deadbeef",
    "decode_info": "bytes4",
    "arbitrary_info": "My first knowledge entry"
  }'

# アドレス予測
curl "http://localhost:8000/blockchain/predict/Sample%20text%20for%20prediction"

### 3. MCP ツールの使用例

MCPサーバーが起動している状態で、Claude DesktopなどのMCPクライアントから以下のようなツールを利用できます：

```
# SemID生成
calc_semid("Hello world")

# ブロックチェーン接続確認
blockchain_status()

# コントラクトアドレス予測
predict_contract_address("My knowledge base entry")

# コントラクトデプロイ
deploy_contract_from_text("Deploy this knowledge", "deadbeef", "bytes4", "My entry")

# コントラクト情報取得
get_contract_info("0x1234567890123456789012345678901234567890")

# 既存コントラクト検索
find_contract_by_text("My knowledge base entry")

# 類似コントラクト検索
find_similar_contracts("Machine learning is fascinating", 3, 1000)

# 一括デプロイ
batch_deploy_from_texts(["Text 1", "Text 2", "Text 3"])

# 統計情報取得
get_semid_contract_stats()

# ナレッジグラフ作成
create_semid_knowledge_graph(["AI", "Machine Learning", "Deep Learning"], 0.7)
```

## 開発

```bash
# 新しい依存関係を追加
uv add <package-name>

# 仮想環境を更新
uv sync
```

## 技術仕様

### SemID 生成
- **埋め込みモデル**: sentence-transformers/all-MiniLM-L6-v2
- **符号化方式**: Golay [24,12,8] 符号
- **ID長**: 24ビット (3バイト)
- **誤り訂正能力**: 半径3までの誤り訂正

### ブロックチェーン統合
- **コントラクト**: Create2Factory + KnowledgeContract
- **Create2 salt**: SemIDを32バイトに拡張した値
- **ネットワーク**: Ethereum互換チェーン (Ethereum, Polygon, BSC等)
- **Web3ライブラリ**: web3.py v6+
- **セキュリティ**: eth-accountを使用したトランザクション署名
