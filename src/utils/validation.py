# src/utils/validation.py
"""バリデーションユーティリティ"""

import os
import re
from typing import Optional


def validate_file_path(file_path: str, extensions: Optional[list] = None) -> bool:
    """
    ファイルパスを検証

    Args:
        file_path: 検証対象のパス
        extensions: 許可する拡張子のリスト（例: ['.xlsx', '.xlsm']）

    Returns:
        有効なパスの場合はTrue
    """
    if not file_path or not isinstance(file_path, str):
        return False

    # パストラバーサル対策
    normalized = os.path.normpath(file_path)
    if '..' in normalized.split(os.sep):
        return False

    # 拡張子チェック
    if extensions:
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in extensions:
            return False

    return True


def validate_sheet_name(sheet_name: str) -> bool:
    """
    シート名を検証

    Args:
        sheet_name: 検証対象のシート名

    Returns:
        有効なシート名の場合はTrue
    """
    if not sheet_name or not isinstance(sheet_name, str):
        return False

    # Excelのシート名の制限
    # - 最大31文字
    # - 無効な文字: : \\ / ? * [ ] '
    if len(sheet_name) > 31:
        return False

    invalid_chars = r'[:\\/?*\[\]\']'
    if re.search(invalid_chars, sheet_name):
        return False

    return True


def sanitize_filename(filename: str, replacement: str = '_') -> str:
    """
    ファイル名を安全な文字列に変換

    Args:
        filename: 元のファイル名
        replacement: 無効文字の置換文字

    Returns:
        安全なファイル名
    """
    if not filename:
        return 'unknown'

    # 拡張子を除去
    base = os.path.splitext(filename)[0]

    # 無効な文字を置換
    invalid_chars = r'[<>:"/\\|?*]'
    safe = re.sub(invalid_chars, replacement, base)

    # 空白を置換
    safe = safe.replace(' ', replacement)

    # 連続するアンダースコアを単一に
    safe = re.sub(r'_+', replacement, safe)

    # 先頭と末尾のアンダースコアを除去
    safe = safe.strip(replacement)

    return safe or 'unknown'


def validate_template_id(template_id: str, allowed_pattern: str = r'^[a-zA-Z0-9_-]+$') -> bool:
    """
    テンプレートIDを検証

    Args:
        template_id: 検証対象のテンプレートID
        allowed_pattern: 許可する文字列のパターン

    Returns:
        有効なテンプレートIDの場合はTrue
    """
    if not template_id or not isinstance(template_id, str):
        return False

    # パストラバーサル対策
    if '..' in template_id or '/' in template_id or '\\' in template_id:
        return False

    return bool(re.match(allowed_pattern, template_id))
