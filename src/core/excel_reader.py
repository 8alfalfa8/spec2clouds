# src/core/excel_reader.py
"""
Excelファイル読み込みモジュール
openpyxlを一切使用せず、ZIP/XML解析で.xlsxファイルを直接読み込む
"""

import zipfile
import xml.etree.ElementTree as ET
import os
import logging
from typing import List, Any, Optional, Iterator, Dict
import pandas as pd

from ..utils import extract_col_letters, col_letter_to_index, safe_str

logger = logging.getLogger(__name__)


class ExcelReader:
    """
    Excelファイルリーダー
    .xlsxファイルをZIPアーカイブとして開き、内部XMLを解析してデータを抽出する
    """

    # XML名前空間
    NS_MAIN = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    NS_RELS = 'http://schemas.openxmlformats.org/package/2006/relationships'
    NS_OFFICE = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

    def __init__(self, file_path: str, chunk_size: Optional[int] = None):
        """
        Args:
            file_path: Excelファイル(.xlsx)のパス
            chunk_size: チャンク読み込み時のサイズ（Noneの場合は全読み込み）
        """
        self.file_path = file_path
        self.chunk_size = chunk_size
        self._shared_strings: List[str] = []
        self._validate_file()

    def _validate_file(self) -> None:
        """ファイルの存在と拡張子を検証"""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")

        ext = os.path.splitext(self.file_path)[1].lower()
        if ext not in ('.xlsx', '.xlsm'):
            raise ValueError(f"Unsupported format: {ext}. Only .xlsx/.xlsm supported")

        # ファイルサイズ警告（100MB以上）
        file_size = os.path.getsize(self.file_path)
        if file_size > 100 * 1024 * 1024:  # 100MB
            logger.warning(f"Large file detected: {self.file_path} ({file_size / 1024 / 1024:.2f} MB)")

    # --- シート名取得 ---

    def get_sheet_names(self) -> List[str]:
        """全シート名を取得"""
        with zipfile.ZipFile(self.file_path, 'r') as z:
            if 'xl/workbook.xml' not in z.namelist():
                raise ValueError("Invalid xlsx: workbook.xml not found")

            with z.open('xl/workbook.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()

        ns = {'ns': self.NS_MAIN}
        return [s.get('name', '') for s in root.findall('.//ns:sheet', ns) if s.get('name')]

    # --- シート読み込み ---

    def read_sheet(self, sheet_name: str) -> pd.DataFrame:
        """
        指定シートをDataFrameとして読み込む

        Args:
            sheet_name: シート名

        Returns:
            シートの全データを含むDataFrame（ヘッダーなし）
        """
        with zipfile.ZipFile(self.file_path, 'r') as z:
            # 共有文字列を読み込み
            self._shared_strings = self._load_shared_strings(z)
            # シートのXMLファイルを特定
            sheet_file = self._resolve_sheet_file(z, sheet_name)
            # XMLをパースして2次元リストを構築
            rows = self._parse_sheet_xml(z, sheet_file)

        if not rows:
            logger.debug(f"Empty sheet: {sheet_name}")
            return pd.DataFrame()

        return pd.DataFrame(rows)

    def read_sheet_in_chunks(self, sheet_name: str) -> Iterator[pd.DataFrame]:
        """
        シートをチャンク単位で読み込むジェネレータ

        Args:
            sheet_name: シート名

        Yields:
            チャンク単位のDataFrame
        """
        if not self.chunk_size:
            yield self.read_sheet(sheet_name)
            return

        with zipfile.ZipFile(self.file_path, 'r') as z:
            self._shared_strings = self._load_shared_strings(z)
            sheet_file = self._resolve_sheet_file(z, sheet_name)

            # チャンク読み込み（簡易実装）
            rows = self._parse_sheet_xml(z, sheet_file)

            for i in range(0, len(rows), self.chunk_size):
                chunk = rows[i:i + self.chunk_size]
                yield pd.DataFrame(chunk)

    def _load_shared_strings(self, z: zipfile.ZipFile) -> List[str]:
        """共有文字列テーブルを読み込む"""
        if 'xl/sharedStrings.xml' not in z.namelist():
            return []

        with z.open('xl/sharedStrings.xml') as f:
            tree = ET.parse(f)

        ns = {'ns': self.NS_MAIN}
        strings = []

        for si in tree.findall('.//ns:si', ns):
            parts = []
            # 1. 単純なテキストノード (<si> 直下の <t>)
            for t in si.findall('ns:t', ns):
                if t.text:
                    parts.append(t.text)
            # 2. リッチテキスト (<r> 要素)
            if not parts:         # 単純テキストがない場合のみリッチテキストを解析
                for r in si.findall('ns:r', ns):

                    # <rPh> (ふりがな) はスキップ
                    if r.find('ns:rPh', ns) is not None:
                        continue

                    t = r.find('ns:t', ns)
                    if t is not None and t.text:
                        parts.append(t.text)
            strings.append(''.join(parts))

        logger.debug(f"Loaded {len(strings)} shared strings")
        return strings

    def _resolve_sheet_file(self, z: zipfile.ZipFile, sheet_name: str) -> str:
        """シート名→XMLファイルパスの解決"""
        # workbook.xmlからシートのrIdを取得
        with z.open('xl/workbook.xml') as f:
            tree = ET.parse(f)

        ns = {'ns': self.NS_MAIN}
        r_id = None

        for sheet in tree.findall('.//ns:sheet', ns):
            if sheet.get('name') == sheet_name:
                for k, v in sheet.attrib.items():
                    if k.endswith('}id') or k == 'id':
                        r_id = v
                        break
                break

        if r_id is None:
            raise ValueError(f"Sheet '{sheet_name}' not found")

        # リレーションシップから物理ファイルパスを解決
        with z.open('xl/_rels/workbook.xml.rels') as f:
            tree = ET.parse(f)

        ns = {'ns': self.NS_RELS}
        for rel in tree.findall('.//ns:Relationship', ns):
            if rel.get('Id') == r_id:
                target = rel.get('Target', '')
                return f"xl/{target}"

        raise ValueError(f"Relationship not found for sheet: {sheet_name}")

    def _parse_sheet_xml(self, z: zipfile.ZipFile, sheet_file: str) -> List[List[Any]]:
        """シートXMLを2次元リストに変換"""
        with z.open(sheet_file) as f:
            tree = ET.parse(f)

        root = tree.getroot()
        ns = {'ns': self.NS_MAIN}

        # 行データを辞書で収集
        rows_dict = {}
        max_row = 0
        max_col = 0

        for row_elem in root.findall('.//ns:row', ns):
            row_num = int(row_elem.get('r', 0))
            max_row = max(max_row, row_num)
            row_cells = {}

            for cell in row_elem.findall('ns:c', ns):
                ref = cell.get('r', '')
                col_letter = extract_col_letters(ref)
                col_idx = col_letter_to_index(col_letter)
                max_col = max(max_col, col_idx)

                value = self._parse_cell_value(cell, ns)
                if value is not None:
                    row_cells[col_idx] = value

            if row_cells:
                rows_dict[row_num] = row_cells

        # 行番号順に2次元リスト化
        result = []
        for r in range(1, max_row + 1):
            row = [None] * (max_col + 1)
            if r in rows_dict:
                for c, v in rows_dict[r].items():
                    if c <= max_col:
                        row[c] = v
            result.append(row)

        logger.debug(f"Parsed {max_row} rows x {max_col + 1} columns")
        return result

    def _parse_cell_value(self, cell: ET.Element, ns: dict) -> Any:
        """セルの値を解析"""
        cell_type = cell.get('t', '')
        v_elem = cell.find('ns:v', ns)

        # 値要素がない場合の処理
        if v_elem is None or v_elem.text is None:
            # インライン文字列
            is_elem = cell.find('.//ns:is', ns)
            if is_elem is not None:
                t_elem = is_elem.find('ns:t', ns)
                if t_elem is not None and t_elem.text:
                    return t_elem.text
            return None

        try:
            if cell_type == 's':               # 共有文字列
                idx = int(v_elem.text)
                if 0 <= idx < len(self._shared_strings):
                    return self._shared_strings[idx]
                return ''
            elif cell_type == 'b':             # ブール
                return v_elem.text == '1'
            elif cell_type == 'e':             # エラー値 (#REF!, #VALUE! など)
                logger.debug(f"Error cell value: {v_elem.text}")
                return None                     # または v_elem.text を返すことも可能
            elif cell_type == 'str':           # 文字列
                return v_elem.text
            elif cell_type == 'inlineStr':     # インライン文字列
                return v_elem.text
            else:                               # 数値
                val = float(v_elem.text)
                return int(val) if val.is_integer() else val
        except (ValueError, IndexError) as e:
            logger.warning(f"Failed to parse cell value: {e}")
            return None

    # --- セル値取得 ---

    def get_cell_value(self, sheet_name: str, cell_ref: str) -> Any:
        """
        特定セルの値を取得

        Args:
            sheet_name: シート名
            cell_ref: セル参照（例: "A1"）

        Returns:
            セルの値。存在しない場合はNone
        """
        df = self.read_sheet(sheet_name)
        col_letter = extract_col_letters(cell_ref)

        import re
        match = re.search(r'\d+', cell_ref)
        if not match:
            return None

        row_num = int(match.group())
        col_idx = col_letter_to_index(col_letter)
        row_idx = row_num - 1

        if row_idx < len(df) and col_idx < len(df.columns):
            val = df.iloc[row_idx, col_idx]
            return None if pd.isna(val) else val

        return None
