# src/core/data_processor.py
"""
データ処理モジュール
データ行範囲の特定、列制御、データ抽出を行う
"""

import pandas as pd
import logging
from typing import Tuple, List, Dict, Any, Iterator, Optional

from ..utils import excel_col_to_index, is_empty_value, safe_str

logger = logging.getLogger(__name__)


class DataProcessor:
    """データ抽出と列制御を担当"""

    EXCEL_ROW_OFFSET = 1  # Excelの行番号は1始まり

    def __init__(self, config: dict):
        raw_start_row = config.get('data_start_row')

        if raw_start_row in (None, ''):
            self.data_start_row = None
        else:
            self.data_start_row = int(raw_start_row) - self.EXCEL_ROW_OFFSET

        # 終了判定文字列
        self.end_string = config.get('end_row_string', '')
        self.end_row_string = self.end_string   # 後方互換

        # 列制御
        ctrl = config.get('column_control', {})
        raw_control_row = ctrl.get('row', 0)
        self.control_row = raw_control_row - self.EXCEL_ROW_OFFSET if raw_control_row else -1
        self.exclude_value = str(ctrl.get('exclude_value', '0'))

        # 無効行制御
        self.invalid_row_control = config.get('invalid_row_control', {})
        self._init_invalid_row_control()

        # 設定検証
        self._validate_config()

        # 終了判定閾値
        self.empty_row_threshold = (
            config.get('termination', {})
                  .get('empty_row_threshold', 1)
        )

    def _init_invalid_row_control(self):
        """無効行制御設定の初期化"""
        self.invalid_row_column = self.invalid_row_control.get('column')
        self.invalid_row_value = str(
            self.invalid_row_control.get('invalid_value', '0')
        )
        self.invalid_output_field = self.invalid_row_control.get(
            'output_field', 'enabled'
        )
        self.valid_output_value = self.invalid_row_control.get(
            'valid_output', True
        )
        self.invalid_output_value = self.invalid_row_control.get(
            'invalid_output', False
        )
        self.skip_invalid_rows = self.invalid_row_control.get(
            'skip_invalid_rows', False
        )

    def _validate_config(self):
        """設定のバリデーション"""
        if self.control_row >= 0:
            logger.debug(f"Column control enabled on row {self.control_row + self.EXCEL_ROW_OFFSET}")

        if self.invalid_row_column:
            logger.debug(f"Invalid row control enabled on column {self.invalid_row_column}")

    # ================================================================
    # データ行範囲
    # ================================================================

    def find_row_range(
        self,
        df: pd.DataFrame,
        start_row: int,
        col_range: tuple
    ) -> tuple:
        """
        データ行範囲を特定する

        Returns:
            (start_row, end_row)
            end_row は exclusive
        """
        start_col, end_col = col_range

        end_row_string = self.end_row_string
        empty_threshold = self.empty_row_threshold

        last_valid_row = start_row - 1
        empty_count = 0

        for row_idx in range(start_row, len(df)):
            row_values = df.iloc[row_idx, start_col:end_col + 1]

            if end_row_string:
                # row_values の中から左端の非空セルの値を取得
                first_val = ''
                for val in row_values:
                    if not is_empty_value(val):
                        first_val = str(val).strip()
                        break
                if first_val and end_row_string in first_val:
                    break

            is_empty_row = all(
                is_empty_value(v)
                for v in row_values
            )

            if is_empty_row:
                empty_count += 1
                if empty_count >= empty_threshold:
                    break
                continue

            empty_count = 0
            last_valid_row = row_idx

        return (start_row, last_valid_row + 1)

    # ================================================================
    # 列制御
    # ================================================================

    def filter_columns(self, df: pd.DataFrame, col_range: Tuple[int, int]) -> List[int]:
        """
        制御行に基づき有効な列インデックスを抽出

        Args:
            df: 全データ
            col_range: (開始列, 終了列)

        Returns:
            有効な列インデックスのリスト（元のDataFrameでの列番号）
        """
        start, end = col_range

        if self.control_row < 0 or self.control_row >= len(df):
            # 制御行未指定 or 範囲外 → 全列有効
            logger.debug("No valid column control row, using all columns")
            return list(range(start, end))

        valid = []
        for c in range(start, end):
            if c < len(df.columns):
                v = df.iloc[self.control_row, c]
                val = safe_str(v)

                if val != self.exclude_value:
                    valid.append(c)
                else:
                    logger.debug(f"Excluded column {c} (value: '{val}')")

        logger.info(f"Valid columns: {len(valid)} out of {end - start}")
        return valid

    # ================================================================
    # データ抽出
    # ================================================================

    def extract(self, df: pd.DataFrame, row_range: Tuple[int, int],
                valid_cols: List[int]) -> pd.DataFrame:
        """
        指定範囲のデータを抽出

        Args:
            df: 全データ
            row_range: (開始行, 終了行)
            valid_cols: 有効列インデックスリスト

        Returns:
            抽出データ
        """
        r_start, r_end = row_range
        # 列が連続していない場合も考慮
        data = df.iloc[r_start:r_end, valid_cols].copy()
        data.reset_index(drop=True, inplace=True)

        logger.debug(f"Extracted {len(data)} rows x {len(data.columns)} columns")
        return data

    # ================================================================
    # 行有効性判定
    # ================================================================

    def is_row_valid(self, df: pd.DataFrame, row_idx: int) -> Optional[bool]:
        """
        行有効/無効判定

        Args:
            df: 全データ
            row_idx: 行インデックス（0始まり）

        Returns:
            True: 有効, False: 無効, None: 判定なし
        """
        if not self.invalid_row_column:
            return None

        col_idx = excel_col_to_index(self.invalid_row_column)

        if row_idx >= len(df) or col_idx >= len(df.columns):
            logger.warning(f"Row {row_idx + self.EXCEL_ROW_OFFSET} or column {self.invalid_row_column} out of range")
            return self.valid_output_value

        raw_val = df.iloc[row_idx, col_idx]
        normalized_val = self._normalize_compare_value(raw_val)
        normalized_invalid = self._normalize_compare_value(self.invalid_row_value)

        is_invalid = normalized_val == normalized_invalid
        result = self.invalid_output_value if is_invalid else self.valid_output_value

        if is_invalid:
            logger.debug(f"Row {row_idx + self.EXCEL_ROW_OFFSET} marked as invalid (value: '{normalized_val}')")

        return result

    @staticmethod
    def _normalize_compare_value(val) -> str:
        """比較用に値を正規化"""
        if pd.isna(val):
            return ''

        if isinstance(val, float) and val.is_integer():
            return str(int(val))

        return str(val).strip()

    def process_rows_with_validity(
        self,
        df: pd.DataFrame,
        start_row: int = 0
    ) -> Iterator[Tuple[int, Dict[str, Any], Optional[bool]]]:
        """
        行データと有効性を一緒に返すジェネレータ

        Args:
            df: データDataFrame
            start_row: 開始行番号（元のExcelでの行番号）

        Yields:
            (元の行番号, 行データの辞書, 有効性フラグ)
        """
        for idx in range(len(df)):
            original_row = start_row + idx
            is_valid = self.is_row_valid(df, idx)

            yield (original_row, df.iloc[idx].to_dict(), is_valid)
