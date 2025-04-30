"""
ドキュメント処理モジュール

マークダウンファイルの読み込みと解析、チャンク分割を行います。
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional


class DocumentProcessor:
    """
    ドキュメント処理クラス

    マークダウンファイルの読み込みと解析、チャンク分割を行います。

    Attributes:
        logger: ロガー
    """

    def __init__(self):
        """
        DocumentProcessorのコンストラクタ
        """
        # ロガーの設定
        self.logger = logging.getLogger("document_processor")
        self.logger.setLevel(logging.INFO)

    def read_markdown(self, file_path: str) -> str:
        """
        マークダウンファイルを読み込みます。

        Args:
            file_path: マークダウンファイルのパス

        Returns:
            マークダウンファイルの内容

        Raises:
            FileNotFoundError: ファイルが見つからない場合
            IOError: ファイルの読み込みに失敗した場合
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.logger.info(f"マークダウンファイル '{file_path}' を読み込みました")
            return content
        except FileNotFoundError:
            self.logger.error(f"マークダウンファイル '{file_path}' が見つかりません")
            raise
        except IOError as e:
            self.logger.error(f"マークダウンファイル '{file_path}' の読み込みに失敗しました: {str(e)}")
            raise

    def split_into_chunks(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """
        テキストをチャンクに分割します。

        Args:
            text: 分割するテキスト
            chunk_size: チャンクサイズ（文字数）
            overlap: チャンク間のオーバーラップ（文字数）

        Returns:
            チャンクのリスト
        """
        if not text:
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + chunk_size, text_length)

            # 文の途中で切らないように調整
            if end < text_length:
                # 次の改行または句点を探す
                next_newline = text.find("\n", end)
                next_period = text.find("。", end)

                if next_newline != -1 and (next_period == -1 or next_newline < next_period):
                    end = next_newline + 1  # 改行を含める
                elif next_period != -1:
                    end = next_period + 1  # 句点を含める

            chunks.append(text[start:end])
            start = end - overlap if end - overlap > start else end

            # 終了条件
            if start >= text_length:
                break

        self.logger.info(f"テキストを {len(chunks)} チャンクに分割しました")
        return chunks

    def process_file(self, file_path: str, chunk_size: int = 500, overlap: int = 100) -> List[Dict[str, Any]]:
        """
        マークダウンファイルを処理します。

        Args:
            file_path: マークダウンファイルのパス
            chunk_size: チャンクサイズ（文字数）
            overlap: チャンク間のオーバーラップ（文字数）

        Returns:
            処理結果のリスト（各要素はチャンク情報を含む辞書）
        """
        try:
            # ファイルを読み込む
            content = self.read_markdown(file_path)

            # チャンクに分割
            chunks = self.split_into_chunks(content, chunk_size, overlap)

            # 結果を作成
            results = []
            for i, chunk in enumerate(chunks):
                document_id = f"{Path(file_path).stem}_{i}"
                results.append(
                    {
                        "document_id": document_id,
                        "content": chunk,
                        "file_path": file_path,
                        "chunk_index": i,
                    }
                )

            self.logger.info(f"マークダウンファイル '{file_path}' を処理しました（{len(results)} チャンク）")
            return results

        except Exception as e:
            self.logger.error(f"マークダウンファイル '{file_path}' の処理中にエラーが発生しました: {str(e)}")
            raise

    def process_directory(self, directory_path: str, chunk_size: int = 500, overlap: int = 100) -> List[Dict[str, Any]]:
        """
        ディレクトリ内のマークダウンファイルを処理します。

        Args:
            directory_path: マークダウンファイルが含まれるディレクトリのパス
            chunk_size: チャンクサイズ（文字数）
            overlap: チャンク間のオーバーラップ（文字数）

        Returns:
            処理結果のリスト（各要素はチャンク情報を含む辞書）
        """
        results = []
        directory = Path(directory_path)

        if not directory.exists() or not directory.is_dir():
            self.logger.error(f"ディレクトリ '{directory_path}' が見つからないか、ディレクトリではありません")
            raise FileNotFoundError(f"ディレクトリ '{directory_path}' が見つからないか、ディレクトリではありません")

        # マークダウンファイルを検索
        markdown_files = list(directory.glob("**/*.md"))
        self.logger.info(
            f"ディレクトリ '{directory_path}' 内に {len(markdown_files)} 個のマークダウンファイルが見つかりました"
        )

        # 各ファイルを処理
        for file_path in markdown_files:
            try:
                file_results = self.process_file(str(file_path), chunk_size, overlap)
                results.extend(file_results)
            except Exception as e:
                self.logger.error(f"ファイル '{file_path}' の処理中にエラーが発生しました: {str(e)}")
                # エラーが発生しても処理を続行
                continue

        self.logger.info(
            f"ディレクトリ '{directory_path}' 内のマークダウンファイルを処理しました（合計 {len(results)} チャンク）"
        )
        return results
