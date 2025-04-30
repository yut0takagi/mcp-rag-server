# Python MCP Server Boilerplate

Python MCP Server Boilerplateは、Model Context Protocol (MCP)に準拠したPythonサーバーを簡単に作成するためのテンプレートリポジトリです。

## 概要

このプロジェクトは、MCPサーバーの基本的な実装を提供し、独自のツールを簡単に追加できるようにします。Model Context Protocol (MCP)は、LLMとサーバー間の通信プロトコルで、LLMに外部APIやサービスへのアクセス、リアルタイムデータの取得、アプリケーションやローカルシステムの制御などの機能を提供します。

## 機能

- **MCPサーバーの基本実装**
  - JSON-RPC over stdioベースで動作
  - ツールの登録と実行のためのメカニズム
  - エラーハンドリングとロギング

- **サンプルツール**
  - システム情報を取得するツール
  - 現在の日時を取得するツール
  - エコーツール（入力されたテキストをそのまま返す）

- **拡張性**
  - 独自のツールを簡単に追加可能
  - 外部モジュールからのツール登録をサポート

## インストール

### 依存関係のインストール

```bash
# uvがインストールされていない場合は先にインストール
# pip install uv

# 依存関係のインストール
uv sync
```

## 使い方

### MCPサーバーの起動

#### uvを使用する場合（推奨）

```bash
uv run python -m src.main
```

オプションを指定する場合：

```bash
uv run python -m src.main --name "my-mcp-server" --version "1.0.0" --description "My MCP Server"
```

#### 通常のPythonを使用する場合

```bash
python -m src.main
```

オプションを指定する場合：

```bash
python -m src.main --name "my-mcp-server" --version "1.0.0" --description "My MCP Server"
```

### Cline/Cursorでの設定

Cline/CursorなどのAIツールでMCPサーバーを使用するには、`mcp_settings.json`ファイルに以下のような設定を追加します：

```json
"my-mcp-server": {
  "command": "uv",
  "args": [
    "run",
    "--directory",
    "/path/to/mcp-server-python-boilerplate",
    "python",
    "-m",
    "src.main"
  ],
  "env": {},
  "disabled": false,
  "alwaysAllow": []
}
```

`/path/to/mcp-server-python-boilerplate`は、このリポジトリのインストールディレクトリに置き換えてください。

## 独自のツールの追加方法

### 1. 直接ツールを追加する

`src/example_tool.py`を参考に、独自のツールを実装します。

```python
def register_my_tools(server):
    # ツールの登録
    server.register_tool(
        name="my_tool",
        description="My custom tool",
        input_schema={
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Parameter 1",
                },
            },
            "required": ["param1"],
        },
        handler=my_tool_handler,
    )

def my_tool_handler(params):
    # ツールの実装
    param1 = params.get("param1", "")

    # 処理を実装
    result = f"Processed: {param1}"

    return {
        "content": [
            {
                "type": "text",
                "text": result,
            }
        ]
    }
```

`src/main.py`に以下のコードを追加して、ツールを登録します：

```python
from .my_tools import register_my_tools

# MCPサーバーの作成
server = MCPServer()

# サンプルツールの登録
register_example_tools(server)

# 独自のツールの登録
register_my_tools(server)
```

### 2. 外部モジュールとして追加する

別のPythonモジュールにツールを実装し、コマンドライン引数で指定することもできます：

```bash
python -m src.main --module myapp.tools
```

この場合、`myapp/tools.py`には以下のような関数を実装します：

```python
def register_tools(server):
    # ツールの登録
    server.register_tool(...)
```

## MCPツールの使用方法

### get_system_info

システム情報を取得します。

```json
{
  "jsonrpc": "2.0",
  "method": "get_system_info",
  "params": {},
  "id": 1
}
```

### get_current_time

現在の日時を取得します。

```json
{
  "jsonrpc": "2.0",
  "method": "get_current_time",
  "params": {
    "format": "%Y-%m-%d %H:%M:%S"
  },
  "id": 2
}
```

### echo

入力されたテキストをそのまま返します。

```json
{
  "jsonrpc": "2.0",
  "method": "echo",
  "params": {
    "text": "Hello, MCP!"
  },
  "id": 3
}
```

## MCPサーバーの開発ガイド

### 1. ツールの設計

ツールを設計する際は、以下の点を考慮してください：

- ツールの目的と機能を明確にする
- 入力パラメータとその型を定義する
- 出力フォーマットを決定する
- エラーケースを考慮する

### 2. ツールの実装

ツールを実装する際は、以下のパターンに従ってください：

```python
def my_tool_handler(params):
    try:
        # パラメータの取得と検証
        param1 = params.get("param1")
        if not param1:
            raise ValueError("param1 is required")

        # 処理の実装
        result = process_data(param1)

        # 結果の返却
        return {
            "content": [
                {
                    "type": "text",
                    "text": result,
                }
            ]
        }
    except Exception as e:
        # エラーハンドリング
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error: {str(e)}",
                }
            ],
            "isError": True,
        }
```

### 3. ツールの登録

ツールを登録する際は、以下のパターンに従ってください：

```python
server.register_tool(
    name="my_tool",                # ツール名
    description="My custom tool",  # ツールの説明
    input_schema={                 # 入力スキーマ
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Parameter 1",
            },
        },
        "required": ["param1"],
    },
    handler=my_tool_handler,       # ハンドラ関数
)
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。
