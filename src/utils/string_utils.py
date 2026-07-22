# src/utils/string_utils.py
"""文字列操作ユーティリティ"""

import math
import re
import unicodedata
import json
import ast
from typing import Any, Optional

def is_empty_value(val: Any) -> bool:
    """
    空の値かどうかを判定（NaN, None, 空文字対応）

    Args:
        val: 判定対象の値

    Returns:
        空の値の場合はTrue
    """
    if val is None:
        return True

    # NaN判定（pandasなしでも可能）
    if isinstance(val, float) and math.isnan(val):
        return True

    if isinstance(val, str) and val.strip() == '':
        return True

    # pandasのNaNオブジェクト対応
    if hasattr(val, '__class__') and 'pandas' in str(val.__class__):
        try:
            import pandas as pd
            return pd.isna(val)
        except ImportError:
            pass

    return False


def safe_str(val: Any, default: str = '') -> str:
    """
    安全に文字列変換（NaN/None対応）

    Args:
        val: 変換対象の値
        default: 空の場合のデフォルト値

    Returns:
        変換された文字列
    """
    return default if is_empty_value(val) else str(val)


def normalize_text(
    value: Any,
    unicode_form: Optional[str] = 'NFKC',
    regex_escape: bool = False,
    strip: bool = True
) -> Any:
    """
    テキストの正規化

    Args:
        value: 正規化対象の値
        unicode_form: Unicode正規化形式（Noneの場合はスキップ）
        regex_escape: 正規表現エスケープを行うか
        strip: 前後の空白を削除するか

    Returns:
        正規化された値（文字列以外はそのまま）
    """
    if not isinstance(value, str):
        return value

    # Unicode正規化
    if unicode_form:
        try:
            value = unicodedata.normalize(unicode_form, value)
        except ValueError:
            pass  # 無効な正規化形式の場合はスキップ

    # 特殊文字の置換
    replacements = {
        '”': '"',
        '“': '"',
        '’': "'",
        '‘': "'",
        '／': '/',
        '＼': '\\',
        '〜': '~',
        '―': '-',
        '–': '-',
        '　': ' ',
        '\u00A0': ' ',  # ノーブレークスペース
        '\u3000': ' ',  # 全角スペース
    }

    for src, dst in replacements.items():
        value = value.replace(src, dst)

    # 前後の空白削除
    if strip:
        value = value.strip()

    # 正規表現エスケープ
    if regex_escape:
        value = re.escape(value)

    return value


def excel_col_to_index(col_ref: str) -> int:
    """
    Excel列文字列を0ベースのインデックスに変換

    Args:
        col_ref: 列文字列（例: "A", "Z", "AA"）

    Returns:
        0ベースの列インデックス

    Examples:
        >>> excel_col_to_index("A")
        0
        >>> excel_col_to_index("Z")
        25
        >>> excel_col_to_index("AA")
        26
    """
    idx = 0
    for ch in col_ref.upper():
        idx = idx * 26 + (ord(ch) - ord('A') + 1)
    return idx - 1


def index_to_excel_col(idx: int) -> str:
    """
    0ベースのインデックスをExcel列文字列に変換

    Args:
        idx: 0ベースの列インデックス

    Returns:
        Excel列文字列

    Examples:
        >>> index_to_excel_col(0)
        'A'
        >>> index_to_excel_col(25)
        'Z'
        >>> index_to_excel_col(26)
        'AA'
    """
    if idx < 0:
        raise ValueError(f"Index must be >= 0, got: {idx}")

    result = ''
    n = idx + 1
    while n > 0:
        n -= 1
        result = chr(n % 26 + 65) + result
        n //= 26
    return result

def normalize_json_string(json_str: str) -> str:
    """
    JSON文字列またはPythonリテラル（シングルクォート可）をパースし、
    キーをソート＋配列要素をソートしてから最小化した文字列を返す。
    パースできない場合は元の文字列を返す。
    """
    if not isinstance(json_str, str):
        return json_str

    obj = None
    # 1. 標準の JSON としてパース
    try:
        obj = json.loads(json_str)
    except (json.JSONDecodeError, ValueError):
        pass

    # 2. JSON パースに失敗したら Python リテラルとして評価（シングルクォート対応）
    if obj is None:
        try:
            obj = ast.literal_eval(json_str)
            # Python の True/False/None を含む可能性があるが、
            # 以降の json.dumps で true/false/null に変換されるため問題なし
        except (ValueError, SyntaxError):
            pass

    if obj is not None and isinstance(obj, (dict, list)):
        normalized_obj = _deep_normalize(obj)
        # キーをソート、インデント無し、空白無しで再シリアライズ
        normalized = json.dumps(
            normalized_obj,
            sort_keys=True,
            ensure_ascii=False,
            separators=(',', ':'))
        return normalized
    else:
        # パースできない、または dict/list でない場合は元の文字列を返す
        return json_str

def _deep_normalize(obj):
    """
    再帰的にJSON構造を正規化する（dictキー順、listソート）
    """
    if isinstance(obj, dict):
        # 辞書はキーでソート
        return {k: _deep_normalize(v) for k, v in sorted(obj.items())}
    elif isinstance(obj, list):
        # リスト内の各要素を正規化し、その文字列表現でソート
        normalized_items = [_deep_normalize(item) for item in obj]
        try:
            # ソート用のキー：各要素を最小JSON化した文字列
            normalized_items.sort(
                key=lambda x: json.dumps(
                    x, sort_keys=True, ensure_ascii=False, separators=(',', ':')
                )
            )
        except TypeError:
            # 比較不能な型が混在する場合はそのまま
            pass
        return normalized_items
    elif isinstance(obj, str):
        # 文字列がさらにJSON/Pythonリテラルとしてパース可能なら再帰的に正規化
        try:
            # まず JSON
            inner_obj = json.loads(obj)
            if isinstance(inner_obj, (dict, list)):
                normalized_inner = _deep_normalize(inner_obj)
                return json.dumps(normalized_inner, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        except (json.JSONDecodeError, TypeError):
            pass
        try:
            # 次に Python リテラル
            inner_obj = ast.literal_eval(obj)
            if isinstance(inner_obj, (dict, list)):
                normalized_inner = _deep_normalize(inner_obj)
                return json.dumps(normalized_inner, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        except (ValueError, SyntaxError, TypeError):
            pass
        return obj
    else:
        return obj

def apply_replace_rules(data: Any, rules: list) -> Any:
    """
    辞書・リストを再帰的に走査し、文字列に対して置換ルールを適用する
    """
    def replace_text(s: str) -> str:
        for rule in rules:
            source = rule.get('source', '')
            condition = rule.get('condition', 'partial')
            replacement = rule.get('replacement', '')
            if condition == 'exact':
                if s == source:
                    return replacement
            else:  # partial
                s = s.replace(source, replacement)
        return s

    if isinstance(data, dict):
        return {k: apply_replace_rules(v, rules) for k, v in data.items()}
    elif isinstance(data, list):
        return [apply_replace_rules(item, rules) for item in data]
    elif isinstance(data, str):
        return replace_text(data)
    else:
        return data

def normalize_bool_value(value):
    """
    bool または文字列 'true'/'false'（大文字小文字不問）を
    'True' / 'False' に統一する。
    それ以外の型・値はそのまま返す。
    """
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.lower() == "true":
            return "True"
        if stripped.lower() == "false":
            return "False"
    return value
