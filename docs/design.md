# 要件・設計書

## 1. 要件定義

### 1.1 基本情報
- ソフトウェア名称: MCP RAG Server
- リポジトリ名: mcp-rag-server

### 1.2 プロジェクト概要

本プロジェクトは、Model Context Protocol (MCP)に準拠したRAG（Retrieval-Augmented Generation）機能を持つPythonサーバーを提供することを目的とする。マークダウンファイルをデータソースとして、multilingual-e5-largeモデルを使用してインデックス化し、ベクトル検索によって関連情報を取得する機能を提供する。

### 1.3 機能要件

#### 1.3.1 MCPサーバーの基本実装
- JSON-RPC over stdioベースで動作
- ツールの登録と実行のためのメカニズム
- エラーハンドリングとロギング

#### 1.3.2 RAG機能
- マークダウンファイルの読み込みと解析
- multilingual-e5-largeモデルを使用したエンベディング生成
- PostgreSQLのpgvectorを使用したベクトルデータベース
- ベクトル検索による関連情報の取得

#### 1.3.3 ツール
- マークダウンファイルのインデックス化ツール
- ベクトル検索ツール
- データベース管理ツール（オプション）

### 1.4 非機能要件

- 迅速なレスポンス
- シンプルな構成とメンテナンス性重視
- 拡張性の高い設計

### 1.5 制約条件

- Python 3.10以上で動作
- JSON-RPC over stdioベースで動作
- PostgreSQLとpgvectorエクステンションが必要

### 1.6 開発環境

- 言語: Python
- 外部ライブラリ:
  - `mcp[cli]` (Model Context Protocol)
  - `python-dotenv`
  - `psycopg2-binary` (PostgreSQL接続)
  - `sentence-transformers` (エンベディング生成)
  - `markdown` (マークダウン解析)
  - `numpy` (ベクトル操作)

### 1.7 成果物

- Python製MCPサーバー
- RAG機能の実装
- README / 利用手順
- 設計書

## 2. システム設計

### 2.1 システム概要設計

#### 2.1.1 システムアーキテクチャ
```
[MCPクライアント(Cline, Cursor)] <-> [MCPサーバー (Python)] <-> [PostgreSQL (pgvector)]
                                                              <-> [マークダウンファイル]
                                                              <-> [multilingual-e5-large]
```

#### 2.1.2 主要コンポーネント
- **MCPサーバー**
  - JSON-RPC over stdioをリッスン
  - ツールの登録と実行を管理
- **ドキュメント管理**
  - マークダウンファイルの読み込みと解析
  - チャンク分割
- **エンベディング生成**
  - multilingual-e5-largeモデルを使用
  - テキストからベクトル表現を生成
- **ベクトルデータベース**
  - PostgreSQLとpgvectorを使用
  - ベクトルの保存と検索

### 2.2 詳細設計

#### 2.2.1 クラス設計

##### `MCPServer`
```python
class MCPServer:
    def register_tool(name: str, description: str, input_schema: Dict[str, Any], handler: Callable) -> None
    def start(server_name: str, version: str, description: str) -> None
    def _handle_tools_call(params: Dict[str, Any], request_id: Any) -> None
```

##### `DocumentProcessor`
```python
class DocumentProcessor:
    def read_markdown(file_path: str) -> str
    def split_into_chunks(text: str, chunk_size: int, overlap: int) -> List[str]
    def process_directory(directory_path: str) -> List[Dict[str, Any]]
```

##### `EmbeddingGenerator`
```python
class EmbeddingGenerator:
    def __init__(model_name: str)
    def generate_embedding(text: str) -> List[float]
    def generate_embeddings(texts: List[str]) -> List[List[float]]
```

##### `VectorDatabase`
```python
class VectorDatabase:
    def __init__(connection_params: Dict[str, Any])
    def initialize_database() -> None
    def insert_document(document_id: str, content: str, embedding: List[float], metadata: Dict[str, Any]) -> None
    def search(query_embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]
    def delete_document(document_id: str) -> None
    def clear_database() -> None
```

##### `RAGService`
```python
class RAGService:
    def __init__(document_processor: DocumentProcessor, embedding_generator: EmbeddingGenerator, vector_database: VectorDatabase)
    def index_documents(directory_path: str) -> Dict[str, Any]
    def search(query: str, limit: int = 5) -> List[Dict[str, Any]]
```

#### 2.2.2 データベーススキーマ

```sql
-- ドキュメントテーブル
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    document_id TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    file_path TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding vector(1024),  -- multilingual-e5-largeの次元数
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- インデックス
CREATE INDEX idx_documents_embedding ON documents USING ivfflat (embedding vector_cosine_ops);
```

### 2.3 インターフェース設計

#### 2.3.1 MCPツール

##### `index_documents`
マークダウンファイルをインデックス化するツール

- 入力パラメータ:
  - `directory_path`: インデックス化するマークダウンファイルが含まれるディレクトリのパス
  - `chunk_size` (オプション): チャンクサイズ（デフォルト: 500）
  - `chunk_overlap` (オプション): チャンクオーバーラップ（デフォルト: 100）

- 出力:
  - インデックス化されたドキュメント数
  - 処理時間
  - 成功/失敗のステータス

##### `search`
ベクトル検索を行うツール

- 入力パラメータ:
  - `query`: 検索クエリ
  - `limit` (オプション): 返す結果の数（デフォルト: 5）

- 出力:
  - 検索結果のリスト（関連度順）
    - ドキュメントID
    - コンテンツ
    - ファイルパス
    - 関連度スコア

##### `clear_index`
インデックスをクリアするツール

- 入力パラメータ: なし

- 出力:
  - 成功/失敗のステータス

### 2.4 セキュリティ設計

- 環境変数で機密情報を管理（`.env`）
  - PostgreSQL接続情報
- 外部からの直接アクセスは制限（ローカル環境前提）

### 2.5 テスト設計

- 単体テスト
  - 各コンポーネントの機能テスト
  - MCPサーバーの基本機能テスト
- 統合テスト
  - RAG機能の統合テスト
  - MCPリクエストを模擬した動作確認

### 2.6 開発環境・依存関係

- Python 3.10+
- PostgreSQL 14+（pgvectorエクステンション付き）
- 必要なPythonパッケージ:
  - `mcp[cli]`
  - `python-dotenv`
  - `psycopg2-binary`
  - `sentence-transformers`
  - `markdown`
  - `numpy`

### 2.7 開発工程

| フェーズ | 内容 | 期間 |
|---------|------|------|
| 要件定義 | 本仕様書作成 | 第1週 |
| 設計 | アーキテクチャ・モジュール設計 | 第1週 |
| 実装 | 各モジュールの開発 | 第2週 |
| テスト | 単体・統合テスト | 第3週 |
| リリース | ドキュメント整備・デプロイ対応 | 第3週 |

## 3. 実装ガイド

### 3.1 PostgreSQLとpgvectorのセットアップ

#### 3.1.1 Dockerを使用する場合

```bash
# pgvectorを含むPostgreSQLコンテナを起動
docker run --name postgres-pgvector -e POSTGRES_PASSWORD=password -p 5432:5432 -d pgvector/pgvector:pg14
```

#### 3.1.2 既存のPostgreSQLにpgvectorをインストールする場合

```bash
# pgvectorエクステンションをインストール
CREATE EXTENSION vector;
```

### 3.2 環境変数の設定

`.env`ファイルに以下の環境変数を設定:

```
# PostgreSQL接続情報
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=ragdb

# マークダウンファイルのディレクトリ
MARKDOWN_DIR=./data/markdown

# エンベディングモデル
EMBEDDING_MODEL=intfloat/multilingual-e5-large
```

### 3.3 実装の流れ

1. 基本的なMCPサーバーの実装
2. ドキュメント処理コンポーネントの実装
3. エンベディング生成コンポーネントの実装
4. ベクトルデータベースコンポーネントの実装
5. RAGサービスの実装
6. MCPツールの実装と登録
7. テストとデバッグ

### 3.4 使用例

#### 3.4.1 インデックス化

```json
{
  "jsonrpc": "2.0",
  "method": "index_documents",
  "params": {
    "directory_path": "./data/markdown",
    "chunk_size": 500,
    "chunk_overlap": 100
  },
  "id": 1
}
```

#### 3.4.2 検索

```json
{
  "jsonrpc": "2.0",
  "method": "search",
  "params": {
    "query": "Pythonのジェネレータとは何ですか？",
    "limit": 5
  },
  "id": 2
}
```

#### 3.4.3 インデックスのクリア

```json
{
  "jsonrpc": "2.0",
  "method": "clear_index",
  "params": {},
  "id": 3
}
