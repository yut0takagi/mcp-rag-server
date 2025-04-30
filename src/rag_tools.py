"""
RAGツールモジュール

MCPサーバーに登録するRAG関連ツールを提供します。
"""

import os
from typing import Dict, Any

from .document_processor import DocumentProcessor
from .embedding_generator import EmbeddingGenerator
from .vector_database import VectorDatabase
from .rag_service import RAGService


def register_rag_tools(server, rag_service: RAGService):
    """
    RAG関連ツールをMCPサーバーに登録します。

    Args:
        server: MCPサーバーのインスタンス
        rag_service: RAGサービスのインスタンス
    """
    # インデックス化ツールの登録
    server.register_tool(
        name="index_documents",
        description="マークダウンファイルをインデックス化します",
        input_schema={
            "type": "object",
            "properties": {
                "directory_path": {
                    "type": "string",
                    "description": "インデックス化するマークダウンファイルが含まれるディレクトリのパス",
                },
                "chunk_size": {
                    "type": "integer",
                    "description": "チャンクサイズ（文字数）",
                    "default": 500,
                },
                "chunk_overlap": {
                    "type": "integer",
                    "description": "チャンク間のオーバーラップ（文字数）",
                    "default": 100,
                },
            },
            "required": ["directory_path"],
        },
        handler=lambda params: index_documents_handler(params, rag_service),
    )

    # 検索ツールの登録
    server.register_tool(
        name="search",
        description="ベクトル検索を行います",
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "検索クエリ",
                },
                "limit": {
                    "type": "integer",
                    "description": "返す結果の数（デフォルト: 5）",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
        handler=lambda params: search_handler(params, rag_service),
    )

    # インデックスクリアツールの登録
    server.register_tool(
        name="clear_index",
        description="インデックスをクリアします",
        input_schema={
            "type": "object",
            "properties": {},
            "required": [],
        },
        handler=lambda params: clear_index_handler(params, rag_service),
    )

    # ドキュメント数取得ツールの登録
    server.register_tool(
        name="get_document_count",
        description="インデックス内のドキュメント数を取得します",
        input_schema={
            "type": "object",
            "properties": {},
            "required": [],
        },
        handler=lambda params: get_document_count_handler(params, rag_service),
    )


def index_documents_handler(params: Dict[str, Any], rag_service: RAGService) -> Dict[str, Any]:
    """
    マークダウンファイルをインデックス化するハンドラ関数

    Args:
        params: パラメータ
            - directory_path: インデックス化するマークダウンファイルが含まれるディレクトリのパス
            - chunk_size: チャンクサイズ（文字数）（オプション）
            - chunk_overlap: チャンク間のオーバーラップ（文字数）（オプション）
        rag_service: RAGサービスのインスタンス

    Returns:
        インデックス化の結果
    """
    directory_path = params.get("directory_path")
    chunk_size = params.get("chunk_size", 500)
    chunk_overlap = params.get("chunk_overlap", 100)

    # ディレクトリパスの検証
    if not os.path.exists(directory_path):
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"エラー: ディレクトリ '{directory_path}' が見つかりません",
                }
            ],
            "isError": True,
        }

    if not os.path.isdir(directory_path):
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"エラー: '{directory_path}' はディレクトリではありません",
                }
            ],
            "isError": True,
        }

    try:
        # インデックス化を実行
        result = rag_service.index_documents(directory_path, chunk_size, chunk_overlap)

        if result["success"]:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"インデックス化が完了しました\n"
                        f"- ドキュメント数: {result['document_count']}\n"
                        f"- 処理時間: {result['processing_time']:.2f} 秒\n"
                        f"- メッセージ: {result.get('message', '')}",
                    }
                ]
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"インデックス化に失敗しました\n"
                        f"- エラー: {result.get('error', '不明なエラー')}\n"
                        f"- 処理時間: {result['processing_time']:.2f} 秒",
                    }
                ],
                "isError": True,
            }

    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"インデックス化中にエラーが発生しました: {str(e)}",
                }
            ],
            "isError": True,
        }


def search_handler(params: Dict[str, Any], rag_service: RAGService) -> Dict[str, Any]:
    """
    ベクトル検索を行うハンドラ関数

    Args:
        params: パラメータ
            - query: 検索クエリ
            - limit: 返す結果の数（デフォルト: 5）
        rag_service: RAGサービスのインスタンス

    Returns:
        検索結果
    """
    query = params.get("query")
    limit = params.get("limit", 5)

    if not query:
        return {
            "content": [
                {
                    "type": "text",
                    "text": "エラー: 検索クエリが指定されていません",
                }
            ],
            "isError": True,
        }

    try:
        # ドキュメント数を確認
        doc_count = rag_service.get_document_count()
        if doc_count == 0:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "インデックスにドキュメントが存在しません。先にindex_documentsツールを使用してドキュメントをインデックス化してください。",
                    }
                ],
                "isError": True,
            }

        # 検索を実行
        results = rag_service.search(query, limit)

        if not results:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"クエリ '{query}' に一致する結果が見つかりませんでした",
                    }
                ]
            }

        # 結果を整形
        content_items = [
            {
                "type": "text",
                "text": f"クエリ '{query}' の検索結果（{len(results)} 件）:",
            }
        ]

        for i, result in enumerate(results):
            file_name = os.path.basename(result["file_path"])
            similarity_percent = result["similarity"] * 100

            content_items.append(
                {
                    "type": "text",
                    "text": f"\n[{i + 1}] 類似度: {similarity_percent:.2f}%\nファイル: {file_name}\n\n{result['content']}",
                }
            )

        return {"content": content_items}

    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"検索中にエラーが発生しました: {str(e)}",
                }
            ],
            "isError": True,
        }


def clear_index_handler(params: Dict[str, Any], rag_service: RAGService) -> Dict[str, Any]:
    """
    インデックスをクリアするハンドラ関数

    Args:
        params: パラメータ（未使用）
        rag_service: RAGサービスのインスタンス

    Returns:
        クリアの結果
    """
    try:
        # インデックスをクリア
        result = rag_service.clear_index()

        if result["success"]:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"インデックスをクリアしました\n"
                        f"- 削除されたドキュメント数: {result['deleted_count']}\n"
                        f"- メッセージ: {result.get('message', '')}",
                    }
                ]
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"インデックスのクリアに失敗しました\n- エラー: {result.get('error', '不明なエラー')}",
                    }
                ],
                "isError": True,
            }

    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"インデックスのクリア中にエラーが発生しました: {str(e)}",
                }
            ],
            "isError": True,
        }


def get_document_count_handler(params: Dict[str, Any], rag_service: RAGService) -> Dict[str, Any]:
    """
    インデックス内のドキュメント数を取得するハンドラ関数

    Args:
        params: パラメータ（未使用）
        rag_service: RAGサービスのインスタンス

    Returns:
        ドキュメント数
    """
    try:
        # ドキュメント数を取得
        count = rag_service.get_document_count()

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"インデックス内のドキュメント数: {count}",
                }
            ]
        }

    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"ドキュメント数の取得中にエラーが発生しました: {str(e)}",
                }
            ],
            "isError": True,
        }


def create_rag_service_from_env() -> RAGService:
    """
    環境変数からRAGサービスを作成します。

    Returns:
        RAGサービスのインスタンス
    """
    # 環境変数から接続情報を取得
    postgres_host = os.environ.get("POSTGRES_HOST", "localhost")
    postgres_port = os.environ.get("POSTGRES_PORT", "5432")
    postgres_user = os.environ.get("POSTGRES_USER", "postgres")
    postgres_password = os.environ.get("POSTGRES_PASSWORD", "password")
    postgres_db = os.environ.get("POSTGRES_DB", "ragdb")

    embedding_model = os.environ.get("EMBEDDING_MODEL", "intfloat/multilingual-e5-large")

    # コンポーネントの作成
    document_processor = DocumentProcessor()
    embedding_generator = EmbeddingGenerator(model_name=embedding_model)
    vector_database = VectorDatabase(
        {
            "host": postgres_host,
            "port": postgres_port,
            "user": postgres_user,
            "password": postgres_password,
            "database": postgres_db,
        }
    )

    # RAGサービスの作成
    rag_service = RAGService(document_processor, embedding_generator, vector_database)

    return rag_service
