# src/output/template_builder.py
"""
テンプレートビルダーモジュール
ExcelヘッダーからテンプレートJSONを生成
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional

from ..utils import sanitize_filename

logger = logging.getLogger(__name__)


class TemplateBuilder:
    """ExcelヘッダーからテンプレートJSONを生成"""

    def __init__(self, overwrite_existing: bool = False):
        """
        Args:
            overwrite_existing: 既存のテンプレートを上書きするか
        """
        self.overwrite_existing = overwrite_existing

    def build(self, columns: List[str]) -> Dict[str, Any]:
        """
        列名リストからテンプレートを構築

        Args:
            columns: フラット化された列名リスト

        Returns:
            テンプレート辞書
        """
        if not columns:
            logger.warning("No columns provided for template building")
            return self._get_empty_template()

        template = {
            "source": {
                "file": "{{$file}}",
                "sheet": "{{$sheet}}",
                "row_index": "{{$index}}",
                "env": "{{$env}}"
            },
            "data": {
                col: f"{{{{{col}}}}}" for col in columns if col
            }
        }

        # メタデータ追加
        template["_metadata"] = {
            "version": "1.0",
            "generated_by": "spec2cloud",
            "column_count": len(columns)
        }

        logger.debug(f"Built template with {len(columns)} columns")
        return template

    def _get_empty_template(self) -> Dict[str, Any]:
        """空のテンプレートを返す"""
        return {
            "source": {
                "file": "{{$file}}",
                "sheet": "{{$sheet}}",
                "row_index": "{{$index}}",
                "env": "{{$env}}"
            },
            "data": {},
            "_metadata": {
                "version": "1.0",
                "generated_by": "spec2cloud",
                "column_count": 0
            }
        }

    def save(self, template: Dict[str, Any], path: str) -> bool:
        """
        テンプレートをファイルに保存

        Args:
            template: テンプレート辞書
            path: 保存先パス

        Returns:
            保存した場合はTrue、スキップした場合はFalse
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # 既存ファイルのチェック
        if os.path.exists(path) and not self.overwrite_existing:
            logger.info(f"Template already exists, skipping: {path}")
            return False

        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(template, f, ensure_ascii=False, indent=2)
            logger.debug(f"Saved template: {path}")
            return True
        except IOError as e:
            logger.error(f"Failed to save template {path}: {e}")
            raise

    def build_and_save(self, columns: List[str], template_id: str,
                       template_dir: str) -> Optional[str]:
        """
        列名からテンプレートを構築して保存

        Args:
            columns: 列名リスト
            template_id: テンプレートID
            template_dir: テンプレート保存ディレクトリ

        Returns:
            保存したファイルパス、失敗時はNone
        """
        if not template_id:
            logger.warning("No template ID provided, skipping auto-generation")
            return None

        # 安全なファイル名を生成
        safe_id = sanitize_filename(template_id)
        file_path = os.path.join(template_dir, f"{safe_id}.json")

        # テンプレート構築
        template = self.build(columns)

        # 保存
        if self.save(template, file_path):
            return file_path

        return None
