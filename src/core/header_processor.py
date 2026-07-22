# src/core/header_processor.py
"""
ヘッダー処理モジュール
混在階層（1〜N階層）のヘッダーを解析し、pandas MultiIndexを構築する
"""

import pandas as pd
import logging
from typing import Tuple, List, Dict, Optional

from ..utils import index_to_excel_col, is_empty_value

logger = logging.getLogger(__name__)


class HeaderProcessor:
    """
    ヘッダー解析クラス
    - 列範囲の特定（開始/終了文字列条件）
    - 空セル補完（前方補充 + 上方補充）
    - MultiIndex構築
    - フラット列名生成
    """

    EXCEL_ROW_OFFSET = 1  # Excelの行番号は1始まり

    def __init__(self, config: dict):
        """
        Args:
            config: ヘッダー設定
                - start_row: 開始行（1始まり）
                - max_levels: 最大階層数
                - start_string: 開始列条件文字列
                - end_string: 終了列条件文字列
                - fill_empty_cells: 空セル補完フラグ
        """
        raw_start_row = config.get('start_row', 1)
        self.start_row = raw_start_row - self.EXCEL_ROW_OFFSET  # 0始まりに変換
        self.max_levels = config.get('max_levels', 1)
        self.start_string = config.get('start_string', '')
        self.end_string = config.get('end_string', '')
        self.fill_empty = config.get('fill_empty_cells', True)

        # 設定のバリデーション
        if self.start_row < 0:
            raise ValueError(f"header.start_row must be >= 1, got: {raw_start_row}")
        if self.max_levels < 1:
            raise ValueError(f"header.max_levels must be >= 1, got: {self.max_levels}")

    # ================================================================
    # 列範囲特定
    # ================================================================
    def find_column_range(self, df: pd.DataFrame) -> Tuple[int, int]:
        """
        ヘッダー列範囲を特定

        優先順位:
        1. start_string / end_string 指定時は文字列探索
        2. 未指定時は非空セル範囲自動判定

        Returns:
            (start_col, end_col_exclusive)
        """
        if df.empty or self.start_row >= len(df):
            logger.warning("Empty DataFrame or start_row out of range")
            return (0, 0)

        # ============================================================
        # 1. start_string/end_string による探索
        # ============================================================
        if self.start_string or self.end_string:
            start = None
            end = None

            for level in range(self.max_levels):
                row_idx = self.start_row + level
                if row_idx >= len(df):
                    break

                row = df.iloc[row_idx]

                for col_idx, val in enumerate(row):
                    cell_val = str(val).strip() if not is_empty_value(val) else ''

                    if start is None and self.start_string:
                        if cell_val == self.start_string:
                            start = col_idx
                            logger.debug(
                                f"Found start_string '{self.start_string}' "
                                f"at {index_to_excel_col(col_idx)}"
                            )

                    if self.end_string:
                        if cell_val == self.end_string:
                            # end = col_idx + 1  # 終了列は包含
                            end = col_idx      # 終了列は非包含
                            logger.debug(
                                f"Found end_string '{self.end_string}' "
                                f"at {index_to_excel_col(col_idx)}"
                            )

            # start/end補完
            if start is None:
                if self.start_string:
                    raise ValueError(
                        f"header.start_string '{self.start_string}' not found"
                    )
                start = 0

            if end is None:
                if self.end_string:
                    raise ValueError(
                        f"header.end_string '{self.end_string}' not found"
                    )
                end = len(df.columns)

            if end <= start:
                raise ValueError(
                    f"Invalid column range detected: start={start}, end={end}"
                )

            logger.info(
                f"Column range by marker: "
                f"{index_to_excel_col(start)}-{index_to_excel_col(end - 1)}"
            )

            return (start, end)

        # ============================================================
        # 2. 従来の自動判定
        # ============================================================
        start = None
        last_non_empty = None

        for level in range(self.max_levels):
            row_idx = self.start_row + level
            if row_idx >= len(df):
                break

            row = df.iloc[row_idx]

            for i, v in enumerate(row):
                if not is_empty_value(v):
                    if start is None:
                        start = i
                    last_non_empty = i

        if start is None:
            logger.warning("No non-empty cells found in header rows")
            return (0, 0)

        end = last_non_empty + 1

        logger.info(
            f"Column range auto-detected: "
            f"{index_to_excel_col(start)}-{index_to_excel_col(end - 1)}"
        )

        return (start, end)

    # ================================================================
    # MultiIndex構築
    # ================================================================

    def build(self, df: pd.DataFrame, col_range: Tuple[int, int]) -> Tuple[pd.Index, Dict[int, int]]:
        """
        MultiIndexを構築

        Args:
            df: 全データ
            col_range: (開始列, 終了列)

        Returns:
            (MultiIndex/Index, {列番号: 実際の階層数})
        """
        start, end = col_range
        if end <= start:
            logger.warning(f"Invalid column range: {start}-{end}")
            return pd.Index([]), {}

        # 1. ヘッダー行の生データ抽出
        raw_headers = self._extract_raw_headers(df, start, end)

        # 2. 各列の実効階層数を分析
        hierarchy = self._analyze_hierarchy(raw_headers)

        # 3. 空セル補完
        filled = self._fill_cells(raw_headers, hierarchy) if self.fill_empty else raw_headers

        # 4. 全空の階層を除去
        cleaned = self._remove_empty_levels(filled)

        # 5. MultiIndex生成
        index = self._create_index(cleaned)

        # 6. ログ出力
        self._log_structure(hierarchy, cleaned)

        return index, hierarchy

    def _extract_raw_headers(self, df: pd.DataFrame, start: int, end: int) -> List[List[str]]:
        """指定範囲のヘッダー行を文字列リストとして抽出"""
        headers = []
        for level in range(self.max_levels):
            row_idx = self.start_row + level
            if row_idx >= len(df):
                break

            row_data = []
            for col in range(start, end):
                if col < len(df.columns):
                    v = df.iloc[row_idx, col]
                    val = str(v).strip() if not is_empty_value(v) else ''
                    row_data.append(val)
                else:
                    row_data.append('')
            headers.append(row_data)

        return headers

    def _analyze_hierarchy(self, headers: List[List[str]]) -> Dict[int, int]:
        """各列の実際の階層数を分析"""
        if not headers:
            return {}

        n_cols = len(headers[0]) if headers else 0
        info = {}

        for c in range(n_cols):
            depth = 0
            for lv in range(len(headers)):
                if headers[lv][c] != '':
                    depth = lv + 1
            info[c] = max(1, depth)

        return info

    def _fill_cells(self, headers: List[List[str]], hierarchy: Dict[int, int]) -> List[List[str]]:
        if not headers:
            return headers

        filled = [row[:] for row in headers]
        n_levels = len(filled)
        n_cols = len(filled[0]) if filled else 0

        # --- 先頭行のラベルでグループ化 ---
        # ラベルが変わったら新しいグループを開始する（空を含む）
        groups = []
        if n_levels > 0 and n_cols > 0:
            top_row = filled[0]
            current_start = 0
            # 先頭列のラベル（空も考慮）
            current_label = top_row[0]
            for c in range(1, n_cols):
                # 空のセルはラベル変化なしと見なす（前のグループに含める）
                if top_row[c] != '' and top_row[c] != current_label:
                    # 新しいラベルが出現した → 前のグループを閉じて新しいグループを開始
                    groups.append((current_start, c - 1, current_label))
                    current_start = c
                    current_label = top_row[c]
            groups.append((current_start, n_cols - 1, current_label))
        else:
            groups.append((0, n_cols - 1, ''))

        # Step 1: グループ内前方補充（同一行内で、グループを越えない）
        for lv in range(n_levels):
            for start, end, label in groups:
                prev = ''
                for c in range(start, end + 1):
                    if filled[lv][c] == '' and prev != '':
                        filled[lv][c] = prev
                    elif filled[lv][c] != '':
                        prev = filled[lv][c]

        # Step 2: 上方補充（全列）
        for lv in range(1, n_levels):
            for c in range(n_cols):
                if filled[lv][c] == '':
                    filled[lv][c] = filled[lv - 1][c]

        #for lv, row in enumerate(filled):
        #    print(f"  Level {lv}: {row}")

        # _fill_cells の最後に追加（デバッグ用）
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Filled headers after grouping:")
            for lv, row in enumerate(filled):
                logger.debug(f"  Level {lv}: {row}")
        return filled

    def _remove_empty_levels(self, headers: List[List[str]]) -> List[List[str]]:
        """全列空の階層を除去"""
        return [lv for lv in headers if any(cell != '' for cell in lv)]

    def _create_index(self, headers: List[List[str]]) -> pd.Index:
        """MultiIndexまたはIndexを生成"""
        if not headers:
            return pd.Index([])

        if len(headers) == 1:
            # 1階層 → 単一Index
            return pd.Index(headers[0])
        else:
            # 2階層以上 → MultiIndex（列数を揃える）
            n_cols = len(headers[0])
            normalized = []
            for lv in headers:
                normalized.append(lv[:n_cols] + [''] * (n_cols - len(lv)))
            return pd.MultiIndex.from_arrays(normalized)

    def _log_structure(self, hierarchy: Dict[int, int], cleaned: List[List[str]]) -> None:
        """階層構造をログ出力"""
        if not hierarchy:
            return

        dist = {}
        for c, depth in hierarchy.items():
            dist.setdefault(depth, []).append(index_to_excel_col(c))

        logger.debug(f"Header structure ({len(cleaned)} effective levels):")
        for depth, cols in sorted(dist.items()):
            logger.debug(f"  {depth} level(s): {', '.join(cols)}")

    # ================================================================
    # ユーティリティ
    # ================================================================

    @property
    def data_start_row(self) -> int:
        """データ開始行（0始まり）"""
        return self.start_row + self.max_levels

    @staticmethod
    def flatten_columns(columns: pd.Index, sep: str = '_') -> List[str]:
        """
        MultiIndexをフラットな列名リストに変換
        ※ 空の列名には "Col_0" のような名前を付けず、空文字列のまま返します
        """
        if not isinstance(columns, pd.MultiIndex):
            # 空セルはそのまま空文字列に（Col_0 等は作らない）
            return [str(col) if not is_empty_value(col) else '' for col in columns]

        result = []
        for tup in columns:
            parts = []
            prev = None
            for p in tup:
                p_str = str(p).strip() if not is_empty_value(p) else ''
                if not p_str:
                    continue
                if prev == p_str:
                    continue
                parts.append(p_str)
                prev = p_str
            # parts が空の場合は空文字列を列名とする
            col_name = sep.join(parts) if parts else ''
            result.append(col_name)
        return result

    @staticmethod
    def flatten_columns_parent_only(columns: pd.Index) -> List[str]:
        """
        MultiIndex の最上位階層だけを列名として返す。
        例: [('EBS', 'Size'), ('EBS', 'Iops')] → ['EBS', 'EBS']
        """
        if isinstance(columns, pd.MultiIndex):
            return [str(columns.get_level_values(0)[i]) for i in range(len(columns))]
        else:
            return list(columns)
