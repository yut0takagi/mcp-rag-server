# MCP RAG Server

MCP RAG Serverは、Model Context Protocol (MCP)に準拠したRAG（Retrieval-Augmented Generation）機能を持つPythonサーバーです。マークダウンファイルをデータソースとして、multilingual-e5-largeモデルを使用してインデックス化し、ベクトル検索によって関連情報を取得する機能を提供します。

## 概要

このプロジェクトは、MCPサーバーの基本的な実装に加えて、RAG機能を提供します。マークダウンファイルをインデックス化し、自然言語クエリに基づいて関連情報を検索することができます。

## 機能

- **MCPサーバーの基本実装**
  - JSON-RPC over stdioベースで動作
  - ツールの登録と実行のためのメカニズム
  - エラーハンドリングとロギング

- **RAG機能**
  - マークダウンファイルの読み込みと解析
  - multilingual-e5-largeモデルを使用したエンベディング生成
  - PostgreSQLのpgvectorを使用したベクトルデータベース
  - ベクトル検索による関連情報の取得

- **ツール**
  - マークダウンファイルのインデックス化ツール
  - ベクトル検索ツール
  - インデックス管理ツール

## 前提条件

- Python 3.10以上
- PostgreSQL 14以上（pgvectorエクステンション付き）

## インストール

### 依存関係のインストール

```bash
# uvがインストールされていない場合は先にインストール
# pip install uv

# 依存関係のインストール
uv sync
```

### PostgreSQLとpgvectorのセットアップ

#### Dockerを使用する場合

```bash
# pgvectorを含むPostgreSQLコンテナを起動
docker run --name postgres-pgvector -e POSTGRES_PASSWORD=password -p 5432:5432 -d pgvector/pgvector:pg14
```

#### データベースの作成

PostgreSQLコンテナを起動した後、以下のコマンドでデータベースを作成します：

```bash
# ragdbデータベースの作成
docker exec -it postgres-pgvector psql -U postgres -c "CREATE DATABASE ragdb;"
```

#### 既存のPostgreSQLにpgvectorをインストールする場合

```sql
-- pgvectorエクステンションをインストール
CREATE EXTENSION vector;
```

### 環境変数の設定

`.env`ファイルを作成し、以下の環境変数を設定します：

```
# PostgreSQL接続情報
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=ragdb

# エンベディングモデル
EMBEDDING_MODEL=intfloat/multilingual-e5-large
```

## 使い方

### MCPサーバーの起動

#### uvを使用する場合（推奨）

```bash
uv run python -m src.main
```

オプションを指定する場合：

```bash
uv run python -m src.main --name "my-rag-server" --version "1.0.0" --description "My RAG Server"
```

#### 通常のPythonを使用する場合

```bash
python -m src.main
```

### Cline/Cursorでの設定

Cline/CursorなどのAIツールでMCPサーバーを使用するには、`mcp_settings.json`ファイルに以下のような設定を追加します：

```json
"mcp-rag-server": {
  "command": "uv",
  "args": [
    "run",
    "--directory",
    "/path/to/mcp-rag-server",
    "python",
    "-m",
    "src.main"
  ],
  "cwd": "/path/to/mcp-rag-server",
  "env": {
    "POSTGRES_HOST": "localhost",
    "POSTGRES_PORT": "5432",
    "POSTGRES_USER": "postgres",
    "POSTGRES_PASSWORD": "password",
    "POSTGRES_DB": "ragdb",
    "EMBEDDING_MODEL": "intfloat/multilingual-e5-large"
  },
  "disabled": false,
  "alwaysAllow": []
}
```

`/path/to/mcp-rag-server`は、このリポジトリのインストールディレクトリに置き換えてください。

## RAGツールの使用方法

### index_documents

マークダウンファイルをインデックス化します。

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

### search

ベクトル検索を行います。

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

### clear_index

インデックスをクリアします。

```json
{
  "jsonrpc": "2.0",
  "method": "clear_index",
  "params": {},
  "id": 3
}
```

### get_document_count

インデックス内のドキュメント数を取得します。

```json
{
  "jsonrpc": "2.0",
  "method": "get_document_count",
  "params": {},
  "id": 4
}
```

## 使用例

1. マークダウンファイルを `data/markdown` ディレクトリに配置します。
2. `index_documents` ツールを使用してマークダウンファイルをインデックス化します。
3. `search` ツールを使用して検索を行います。

## ディレクトリ構造

```
mcp-rag-server/
├── data/
│   └── markdown/  # マークダウンファイルを配置するディレクトリ
├── docs/
│   └── design.md  # 設計書
├── logs/          # ログファイル
├── src/
│   ├── __init__.py
│   ├── document_processor.py  # ドキュメント処理モジュール
│   ├── embedding_generator.py # エンベディング生成モジュール
│   ├── example_tool.py        # サンプルツールモジュール
│   ├── main.py                # メインエントリーポイント
│   ├── mcp_server.py          # MCPサーバーモジュール
│   ├── rag_service.py         # RAGサービスモジュール
│   ├── rag_tools.py           # RAGツールモジュール
│   └── vector_database.py     # ベクトルデータベースモジュール
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_document_processor.py
│   ├── test_embedding_generator.py
│   ├── test_example_tool.py
│   ├── test_mcp_server.py
│   ├── test_rag_service.py
│   ├── test_rag_tools.py
│   └── test_vector_database.py
├── .env           # 環境変数設定ファイル
├── .gitignore
├── LICENSE
├── pyproject.toml
└── README.md
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。
