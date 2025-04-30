"""
RAGサービスモジュール

ドキュメント処理、エンベディング生成、ベクトルデータベースを統合して、
インデックス化と検索の機能を提供します。
"""

import os
import time
import logging
from typing import List, Dict, Any

from .document_processor import DocumentProcessor
from .embedding_generator import EmbeddingGenerator
from .vector_database import VectorDatabase


class RAGService:
    """
    RAGサービスクラス

    ドキュメント処理、エンベディング生成、ベクトルデータベースを統合して、
    インデックス化と検索の機能を提供します。

    Attributes:
        document_processor: ドキュメント処理クラスのインスタンス
        embedding_generator: エンベディング生成クラスのインスタンス
        vector_database: ベクトルデータベースクラスのインスタンス
        logger: ロガー
    """

    def __init__(
        self, document_processor: DocumentProcessor, embedding_generator: EmbeddingGenerator, vector_database: VectorDatabase
    ):
        """
        RAGServiceのコンストラクタ

        Args:
            document_processor: ドキュメント処理クラスのインスタンス
            embedding_generator: エンベディング生成クラスのインスタンス
            vector_database: ベクトルデータベースクラスのインスタンス
        """
        # ロガーの設定
        self.logger = logging.getLogger("rag_service")
        self.logger.setLevel(logging.INFO)

        # コンポーネントの設定
        self.document_processor = document_processor
        self.embedding_generator = embedding_generator
        self.vector_database = vector_database

        # データベースの初期化
        try:
            self.vector_database.initialize_database()
        except Exception as e:
            self.logger.error(f"データベースの初期化に失敗しました: {str(e)}")
            raise

    def index_documents(self, directory_path: str, chunk_size: int = 500, chunk_overlap: int = 100) -> Dict[str, Any]:
        """
        ディレクトリ内のマークダウンファイルをインデックス化します。

        Args:
            directory_path: インデックス化するマークダウンファイルが含まれるディレクトリのパス
            chunk_size: チャンクサイズ（文字数）
            chunk_overlap: チャンク間のオーバーラップ（文字数）

        Returns:
            インデックス化の結果
                - document_count: インデックス化されたドキュメント数
                - processing_time: 処理時間（秒）
                - success: 成功したかどうか
                - error: エラーメッセージ（エラーが発生した場合）
        """
        start_time = time.time()
        document_count = 0

        try:
            # ディレクトリ内のマークダウンファイルを処理
            self.logger.info(f"ディレクトリ '{directory_path}' 内のマークダウンファイルをインデックス化しています...")
            chunks = self.document_processor.process_directory(directory_path, chunk_size, chunk_overlap)

            if not chunks:
                self.logger.warning(f"ディレクトリ '{directory_path}' 内にマークダウンファイルが見つかりませんでした")
                return {
                    "document_count": 0,
                    "processing_time": time.time() - start_time,
                    "success": True,
                    "message": f"ディレクトリ '{directory_path}' 内にマークダウンファイルが見つかりませんでした",
                }

            # チャンクのコンテンツからエンベディングを生成
            self.logger.info(f"{len(chunks)} チャンクのエンベディングを生成しています...")
            texts = [chunk["content"] for chunk in chunks]
            embeddings = self.embedding_generator.generate_embeddings(texts)

            # ドキュメントをデータベースに挿入
            self.logger.info(f"{len(chunks)} チャンクをデータベースに挿入しています...")
            documents = []
            for i, chunk in enumerate(chunks):
                documents.append(
                    {
                        "document_id": chunk["document_id"],
                        "content": chunk["content"],
                        "file_path": chunk["file_path"],
                        "chunk_index": chunk["chunk_index"],
                        "embedding": embeddings[i],
                        "metadata": {
                            "file_name": os.path.basename(chunk["file_path"]),
                            "directory": os.path.dirname(chunk["file_path"]),
                        },
                    }
                )

            self.vector_database.batch_insert_documents(documents)
            document_count = len(documents)

            processing_time = time.time() - start_time
            self.logger.info(f"インデックス化が完了しました（{document_count} ドキュメント、{processing_time:.2f} 秒）")

            return {
                "document_count": document_count,
                "processing_time": processing_time,
                "success": True,
                "message": f"{document_count} ドキュメントをインデックス化しました",
            }

        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"インデックス化中にエラーが発生しました: {str(e)}")

            return {"document_count": document_count, "processing_time": processing_time, "success": False, "error": str(e)}

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        ベクトル検索を行います。

        Args:
            query: 検索クエリ
            limit: 返す結果の数（デフォルト: 5）

        Returns:
            検索結果のリスト（関連度順）
                - document_id: ドキュメントID
                - content: コンテンツ
                - file_path: ファイルパス
                - similarity: 類似度
                - metadata: メタデータ
        """
        try:
            # クエリからエンベディングを生成
            self.logger.info(f"クエリ '{query}' のエンベディングを生成しています...")
            query_embedding = self.embedding_generator.generate_search_embedding(query)

            # ベクトル検索
            self.logger.info(f"クエリ '{query}' でベクトル検索を実行しています...")
            results = self.vector_database.search(query_embedding, limit)

            self.logger.info(f"検索結果: {len(results)} 件")
            return results

        except Exception as e:
            self.logger.error(f"検索中にエラーが発生しました: {str(e)}")
            raise

    def clear_index(self) -> Dict[str, Any]:
        """
        インデックスをクリアします。

        Returns:
            クリアの結果
                - deleted_count: 削除されたドキュメント数
                - success: 成功したかどうか
                - error: エラーメッセージ（エラーが発生した場合）
        """
        try:
            # データベースをクリア
            self.logger.info("インデックスをクリアしています...")
            deleted_count = self.vector_database.clear_database()

            self.logger.info(f"インデックスをクリアしました（{deleted_count} ドキュメントを削除）")
            return {"deleted_count": deleted_count, "success": True, "message": f"{deleted_count} ドキュメントを削除しました"}

        except Exception as e:
            self.logger.error(f"インデックスのクリア中にエラーが発生しました: {str(e)}")

            return {"deleted_count": 0, "success": False, "error": str(e)}

    def get_document_count(self) -> int:
        """
        インデックス内のドキュメント数を取得します。

        Returns:
            ドキュメント数
        """
        try:
            # ドキュメント数を取得
            count = self.vector_database.get_document_count()
            self.logger.info(f"インデックス内のドキュメント数: {count}")
            return count

        except Exception as e:
            self.logger.error(f"ドキュメント数の取得中にエラーが発生しました: {str(e)}")
            raise
