"""
サンプルツールモジュール

MCPサーバーに登録するサンプルツールを提供します。
"""

import os
import json
import platform
from datetime import datetime
from typing import Dict, Any


def register_example_tools(server):
    """
    サンプルツールをMCPサーバーに登録します。

    Args:
        server: MCPサーバーのインスタンス
    """
    # システム情報ツールの登録
    server.register_tool(
        name="get_system_info",
        description="システム情報を取得します",
        input_schema={
            "type": "object",
            "properties": {},
            "required": [],
        },
        handler=get_system_info,
    )

    # 現在時刻ツールの登録
    server.register_tool(
        name="get_current_time",
        description="現在の日時を取得します",
        input_schema={
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "description": "日時のフォーマット（例: '%Y-%m-%d %H:%M:%S'）",
                },
            },
            "required": [],
        },
        handler=get_current_time,
    )

    # エコーツールの登録
    server.register_tool(
        name="echo",
        description="入力されたテキストをそのまま返します",
        input_schema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "エコーするテキスト",
                },
            },
            "required": ["text"],
        },
        handler=echo,
    )


def get_system_info(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    システム情報を取得します。

    Args:
        params: パラメータ（未使用）

    Returns:
        システム情報
    """
    system_info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
        "cpu_count": os.cpu_count(),
        "platform": platform.platform(),
    }

    return {
        "content": [
            {
                "type": "text",
                "text": f"システム情報:\n{json.dumps(system_info, indent=2, ensure_ascii=False)}",
            }
        ]
    }


def get_current_time(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    現在の日時を取得します。

    Args:
        params: パラメータ
            - format: 日時のフォーマット（オプション）

    Returns:
        現在の日時
    """
    time_format = params.get("format", "%Y-%m-%d %H:%M:%S")
    current_time = datetime.now().strftime(time_format)

    return {
        "content": [
            {
                "type": "text",
                "text": f"現在の日時: {current_time}",
            }
        ]
    }


def echo(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    入力されたテキストをそのまま返します。

    Args:
        params: パラメータ
            - text: エコーするテキスト

    Returns:
        入力されたテキスト
    """
    text = params.get("text", "")

    return {
        "content": [
            {
                "type": "text",
                "text": f"Echo: {text}",
            }
        ]
    }
