#!/usr/bin/env python
"""
Python MCP Server Boilerplate

Model Context Protocol (MCP)に準拠したPythonサーバーのボイラープレート
"""

import sys
import argparse
import importlib
from dotenv import load_dotenv

from .mcp_server import MCPServer
from .example_tool import register_example_tools


def main():
    """
    メイン関数

    コマンドライン引数を解析し、MCPサーバーを起動します。
    """
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(
        description="Python MCP Server - Model Context Protocol (MCP)に準拠したPythonサーバーのボイラープレート"
    )
    parser.add_argument("--name", default="mcp-server-python", help="サーバー名")
    parser.add_argument("--version", default="0.1.0", help="サーバーバージョン")
    parser.add_argument("--description", default="Python MCP Server", help="サーバーの説明")
    parser.add_argument("--module", help="追加のツールモジュール（例: myapp.tools）")
    args = parser.parse_args()

    # 環境変数の読み込み
    load_dotenv()

    try:
        # MCPサーバーの作成
        server = MCPServer()

        # サンプルツールの登録
        register_example_tools(server)

        # 追加のツールモジュールがある場合は読み込む
        if args.module:
            try:
                module = importlib.import_module(args.module)
                if hasattr(module, "register_tools"):
                    module.register_tools(server)
                    print(f"モジュール '{args.module}' からツールを登録しました", file=sys.stderr)
                else:
                    print(f"警告: モジュール '{args.module}' に register_tools 関数が見つかりません", file=sys.stderr)
            except ImportError as e:
                print(f"警告: モジュール '{args.module}' の読み込みに失敗しました: {str(e)}", file=sys.stderr)

        # MCPサーバーの起動
        server.start(args.name, args.version, args.description)

    except KeyboardInterrupt:
        print("サーバーを終了します。", file=sys.stderr)
        sys.exit(0)

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
