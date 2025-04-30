# MCP RAG Server

MCP RAG Serverは、Model Context Protocol (MCP)に準拠したRAG（Retrieval-Augmented Generation）機能を持つPythonサーバーです。マークダウン、テキスト、パワーポイント、PDFなど複数の形式のドキュメントをデータソースとして、multilingual-e5-largeモデルを使用してインデックス化し、ベクトル検索によって関連情報を取得する機能を提供します。

## 概要

このプロジェクトは、MCPサーバーの基本的な実装に加えて、RAG機能を提供します。複数形式のドキュメントをインデックス化し、自然言語クエリに基づいて関連情報を検索することができます。

## 機能

- **MCPサーバーの基本実装**
  - JSON-RPC over stdioベースで動作
  - ツールの登録と実行のためのメカニズム
  - エラーハンドリングとロギング

- **RAG機能**
  - 複数形式のドキュメント（マークダウン、テキスト、パワーポイント、PDF）の読み込みと解析
  - 階層構造を持つソースディレクトリに対応
  - markitdownライブラリを使用したパワーポイントやPDFからのマークダウン変換
  - multilingual-e5-largeモデルを使用したエンベディング生成
  - PostgreSQLのpgvectorを使用したベクトルデータベース
  - ベクトル検索による関連情報の取得
  - 差分インデックス化機能（新規・変更ファイルのみを処理）

- **ツール**
  - ベクトル検索ツール（MCP）
  - ドキュメント数取得ツール（MCP）
  - インデックス管理ツール（CLI）

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

# markitdownライブラリのインストール
uv pip install markitdown
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

# ドキュメントディレクトリ
SOURCE_DIR=./data/source
PROCESSED_DIR=./data/processed

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

### コマンドラインツール（CLI）の使用方法

インデックスのクリアとインデックス化を行うためのコマンドラインツールが用意されています。

#### ヘルプの表示

```bash
python -m src.cli --help
```

#### インデックスのクリア

```bash
python -m src.cli clear
```

#### ドキュメントのインデックス化

```bash
# デフォルト設定でインデックス化（./data/source ディレクトリ）
python -m src.cli index

# 特定のディレクトリをインデックス化
python -m src.cli index --directory ./path/to/documents

# チャンクサイズとオーバーラップを指定してインデックス化
python -m src.cli index --directory ./data/source --chunk-size 300 --chunk-overlap 50
# または短い形式で
python -m src.cli index -d ./data/source -s 300 -o 50

# 差分インデックス化（新規・変更ファイルのみを処理）
python -m src.cli index --incremental
# または短い形式で
python -m src.cli index -i
```

#### インデックス内のドキュメント数の取得

```bash
python -m src.cli count
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
    "SOURCE_DIR": "./data/source",
    "PROCESSED_DIR": "./data/processed",
    "EMBEDDING_MODEL": "intfloat/multilingual-e5-large"
  },
  "disabled": false,
  "alwaysAllow": []
}
```

`/path/to/mcp-rag-server`は、このリポジトリのインストールディレクトリに置き換えてください。

## RAGツールの使用方法

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
  "id": 1
}
```

### get_document_count

インデックス内のドキュメント数を取得します。

```json
{
  "jsonrpc": "2.0",
  "method": "get_document_count",
  "params": {},
  "id": 2
}
```

## 使用例

1. ドキュメントファイルを `data/source` ディレクトリに配置します。サポートされるファイル形式は以下の通りです：
   - マークダウン（.md, .markdown）
   - テキスト（.txt）
   - パワーポイント（.ppt, .pptx）
   - Word（.doc, .docx）
   - PDF（.pdf）

2. CLIコマンドを使用してドキュメントをインデックス化します：
   ```bash
   # 初回は全件インデックス化
   python -m src.cli index
   
   # 以降は差分インデックス化で効率的に更新
   python -m src.cli index -i
   ```

3. MCPサーバーを起動します：
   ```bash
   uv run python -m src.main
   ```

4. `search`ツールを使用して検索を行います。

## ディレクトリ構造

```
mcp-rag-server/
├── data/
│   ├── source/        # 原稿ファイル（階層構造対応）
│   │   ├── markdown/  # マークダウンファイル
│   │   ├── docs/      # ドキュメントファイル
│   │   └── slides/    # プレゼンテーションファイル
│   └── processed/     # 処理済みファイル（テキスト抽出済み）
│       └── file_registry.json  # 処理済みファイルの情報（差分インデックス用）
├── docs/
│   └── design.md      # 設計書
├── logs/              # ログファイル
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
