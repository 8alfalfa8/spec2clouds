# src/models/sheet_context.py
"""
シート処理コンテキストモデルを定義するモジュール
SheetContextクラスを提供
"""
from dataclasses import dataclass
from typing import Optional, Tuple, List
import pandas as pd


@dataclass
class SheetContext:
    """
    シート処理コンテキスト
    1シート処理中の中間データを保持する
    """

    file_name: str
    sheet_name: str
    raw_df: pd.DataFrame

    template_id: str = ''

    col_range: Optional[Tuple[int, int]] = None
    row_range: Optional[Tuple[int, int]] = None

    valid_cols: Optional[List[int]] = None

    flat_columns: Optional[List[str]] = None
    data_df: Optional[pd.DataFrame] = None
    column_depths: Optional[List[int]] = None
    valid_multi_index: Optional[pd.Index] = None
