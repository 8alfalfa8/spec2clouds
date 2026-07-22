# src/utils/excel_utils.py
"""Excel関連ユーティリティ"""

import re
from typing import Optional


def extract_col_letters(cell_ref: str) -> str:
    """
    セル参照から列文字を抽出

    Args:
        cell_ref: セル参照（例: "AB12", "C5"）

    Returns:
        列文字列（例: "AB", "C"）

    Examples:
        >>> extract_col_letters("AB12")
        'AB'
        >>> extract_col_letters("C5")
        'C'
    """
    match = re.match(r'([A-Za-z]+)', cell_ref)
    return match.group(1) if match else ''


def col_letter_to_index(letters: str) -> int:
    """
    列文字列を0ベースのインデックスに変換

    Args:
        letters: 列文字列（例: "A", "Z", "AA"）

    Returns:
        0ベースの列インデックス

    Examples:
        >>> col_letter_to_index("A")
        0
        >>> col_letter_to_index("Z")
        25
        >>> col_letter_to_index("AA")
        26
    """
    idx = 0
    for ch in letters.upper():
        idx = idx * 26 + (ord(ch) - ord('A') + 1)
    return idx - 1


def parse_cell_range(range_str: str) -> tuple[Optional[str], Optional[int]]:
    """
    セル範囲文字列を解析

    Args:
        range_str: セル範囲（例: "A1:B10", "A:A", "1:10"）

    Returns:
        (開始セル, 終了セル) または (None, None)
    """
    if not range_str:
        return None, None

    parts = range_str.split(':')
    if len(parts) == 1:
        return parts[0], None

    return parts[0], parts[1]
