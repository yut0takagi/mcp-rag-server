"""
サンプルツールのテスト
"""

import platform
from datetime import datetime
from unittest.mock import MagicMock

from src.example_tool import get_system_info, get_current_time, echo, register_example_tools


def test_get_system_info():
    """システム情報取得ツールをテストします"""
    # ツールを実行
    result = get_system_info({})

    # 結果を確認
    assert "content" in result
    assert len(result["content"]) == 1
    assert result["content"][0]["type"] == "text"

    # システム情報が含まれていることを確認
    text = result["content"][0]["text"]
    assert "システム情報" in text
    assert platform.system() in text
    assert platform.python_version() in text


def test_get_current_time_default_format():
    """現在時刻取得ツール（デフォルトフォーマット）をテストします"""
    # ツールを実行
    result = get_current_time({})

    # 結果を確認
    assert "content" in result
    assert len(result["content"]) == 1
    assert result["content"][0]["type"] == "text"

    # 現在時刻が含まれていることを確認
    text = result["content"][0]["text"]
    assert "現在の日時" in text

    # デフォルトフォーマット（%Y-%m-%d %H:%M:%S）で日時が含まれていることを確認
    current_time = datetime.now().strftime("%Y-%m-%d")
    assert current_time in text


def test_get_current_time_custom_format():
    """現在時刻取得ツール（カスタムフォーマット）をテストします"""
    # カスタムフォーマットを指定
    custom_format = "%Y年%m月%d日"

    # ツールを実行
    result = get_current_time({"format": custom_format})

    # 結果を確認
    assert "content" in result
    assert len(result["content"]) == 1
    assert result["content"][0]["type"] == "text"

    # 現在時刻が含まれていることを確認
    text = result["content"][0]["text"]
    assert "現在の日時" in text

    # カスタムフォーマットで日時が含まれていることを確認
    current_time = datetime.now().strftime(custom_format)
    assert current_time in text


def test_echo():
    """エコーツールをテストします"""
    # テスト用のテキスト
    test_text = "Hello, MCP!"

    # ツールを実行
    result = echo({"text": test_text})

    # 結果を確認
    assert "content" in result
    assert len(result["content"]) == 1
    assert result["content"][0]["type"] == "text"

    # エコーされたテキストが含まれていることを確認
    text = result["content"][0]["text"]
    assert f"Echo: {test_text}" == text


def test_echo_empty():
    """エコーツール（空のテキスト）をテストします"""
    # ツールを実行（textパラメータなし）
    result = echo({})

    # 結果を確認
    assert "content" in result
    assert len(result["content"]) == 1
    assert result["content"][0]["type"] == "text"

    # 空のエコーが含まれていることを確認
    text = result["content"][0]["text"]
    assert "Echo: " == text


def test_register_example_tools():
    """サンプルツールの登録をテストします"""
    # モックサーバー
    mock_server = MagicMock()

    # サンプルツールを登録
    register_example_tools(mock_server)

    # register_toolが3回呼び出されていることを確認
    assert mock_server.register_tool.call_count == 3

    # 各ツールが登録されていることを確認
    tool_names = [args[1]["name"] for args in mock_server.register_tool.call_args_list]
    assert "get_system_info" in tool_names
    assert "get_current_time" in tool_names
    assert "echo" in tool_names
