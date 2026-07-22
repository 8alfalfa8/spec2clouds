# src/comparator/report_generator.py
"""
比較結果をMarkdown形式でレポート生成するモジュール
レポート生成のためのReportGeneratorクラスを提供
"""
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, List

from ..models.resource import NormalizedResource


class ReportGenerator:
    """比較レポートをエビデンス用に生成"""

    def __init__(self, output_dir: str = "output", show_extra: bool = True):
        self.output_dir = output_dir
        self.show_extra = show_extra
        os.makedirs(output_dir, exist_ok=True)

    def generate_file_report_markdown(self, all_results: dict, file_name: str, meta_info: dict, show_extra: bool = True) -> str:
        """ファイル単位の統合Markdownレポートを生成"""
        lines = []
        lines.append(f"# 検証結果比較レポート: {file_name}")
        lines.append("")
        lines.append("## 1. 実行情報")
        lines.append("")
        lines.append(f"- **実行開始日時**: {meta_info.get('execution_start', '')}")
        lines.append(f"- **実行終了日時**: {meta_info.get('execution_end', '')}")
        lines.append(f"- **実行時間**: {meta_info.get('execution_time', '')}")
        lines.append(f"- **環境**: {meta_info.get('env', 'N/A')}")
        lines.append(f"- **AWS リージョン**: {meta_info.get('region', '')}")
        lines.append(f"- **AWS アカウントID**: {meta_info.get('account_id', 'N/A')}")
        lines.append(f"- **期待値ソース**: {meta_info.get('source', '')}")
        lines.append("---")

        lines.append("## 2. 全体サマリ")
        lines.append("")
        header = "| シート | AWSサービス | 不一致(NG) | 実環境未存在 |"
        if show_extra:
            header += " 期待値未定義 |"
        header += " 対象外 | 一致(OK) | 合計 |"
        lines.append(header)
        sep = "|--------|---------------|--------|--------------|"
        if show_extra:
            sep += "--------------|"
        sep += "--------|------|------|"
        lines.append(sep)

        total_matched = 0
        total_modified = 0
        total_missing = 0
        total_extra = 0
        total_invalid = 0
        total_sum = 0

        for rtype, result in all_results.items():
            matched = len(result['matched'])
            modified = len(result['modified'])
            missing = len(result['missing'])
            extra = len(result['extra']) if self.show_extra else '非表示'
            invalid = len(result.get('invalid_resources', []))
            # 行の合計（表示対象のみ）
            row_sum = matched + modified + missing + (extra if show_extra else 0) + invalid
            if isinstance(extra, int): total_extra += extra
            sheet_name = result.get('sheet_name', rtype)
            resource_type_display = result.get('resource_type', rtype)   # ★ リソースタイプを表示
            sheet_name_escaped = self._escape_markdown_cell(sheet_name)
            resource_type_escaped = self._escape_markdown_cell(resource_type_display)
            row = f"| {sheet_name_escaped} | {resource_type_escaped} | {modified} | {missing} |"
            if show_extra:
                row += f" {extra} |"
            else:
                row += " |" if show_extra else ""  # 空セルにする？実際には列自体を省略するので、このセルは不要
            row += f" {invalid} | {matched} | {row_sum} |"
            lines.append(row)

            #lines.append(f"| {sheet_name_escaped} | {matched} | {modified} | {missing} | {extra} | {invalid} | {resource_type_escaped} |")

            total_matched += matched
            total_modified += modified
            total_missing += missing
            total_extra += extra if show_extra else 0
            total_invalid += invalid
            total_sum += row_sum

        total = f"| **合計** | **-** | **{total_modified}** | **{total_missing}** |"
        if show_extra:
            row += f" {total_extra} |"
        else:
            row += " |" if show_extra else ""
        total += f" **{total_invalid}** | **{total_matched}** | **{total_sum}** |"
        lines.append(total)
        # lines.append(f"| **合計** | **{total_matched}** | **{total_modified}** | **{total_missing}** | **{total_extra if self.show_extra else '非表示'}** | **{total_invalid}** | |")
        lines.append("")
        lines.append("---")
        lines.append("")

        for rtype, result in all_results.items():
            sheet_name = result.get('sheet_name', rtype)
            invalid_res = result.get('invalid_resources', [])
            resource_type_display = result.get('resource_type', rtype)   # ★ リソースタイプを表示
            lines.append(f"## ◆ シート: {sheet_name}")
            lines.append(f"### AWSサービス: {resource_type_display}")    # ★ ここも修正
            lines.append("")
            # ステータスサマリ
            lines.append("### ステータスサマリ")
            lines.append("")
            lines.append("| 状態 | 件数 |")
            lines.append("|------|------|")
            lines.append(f"| 不一致(NG) | {len(result['modified'])} |")
            lines.append(f"| 実環境未存在 (期待値のみ) | {len(result['missing'])} |")
            if show_extra:
                lines.append(f"| 実環境のみ (期待値なし) | {len(result['extra'])} |")
            lines.append(f"| 対象外 (無効行) | {len(invalid_res)} |")
            lines.append(f"| 一致(OK) | {len(result['matched'])} |")
            # ★ 合計行
            extra_count = len(result['extra']) if show_extra else 0
            total_status = len(result['matched']) + len(result['modified']) + len(result['missing']) + extra_count + len(invalid_res)
            lines.append(f"| **合計** | **{total_status}** |")
            lines.append("")
            lines.append("---")
            lines.append("")

            # 不一致リソース詳細
            lines.append("### 不一致(NG)リソース詳細")
            if result['modified']:
                for mod in self._sort_by_source_row(result['modified']):
                    lines.append(f"#### リソース識別子: {mod['identifier']}")
                    # ★ 出典行
                    meta = mod.get('meta', {})
                    source_str = self._format_meta(meta)
                    if source_str:
                        lines.append(f"**出典**: {source_str}")
                    lines.append("")
                    lines.append("| プロパティ | 期待値 | 実績値 | 判定 |")
                    lines.append("|------------|--------|--------|------|")

                    exp_keys = list(mod.get('expected_props', {}).keys())
                    act_keys = list(mod.get('actual_props', {}).keys())
                    ordered_keys = exp_keys + [k for k in act_keys if k not in exp_keys]
                    diff_keys = {diff['key'] for diff in mod['differences']}
                    for key in ordered_keys:
                        exp_val = mod['expected_props'].get(key, '(なし)')
                        act_val = mod['actual_props'].get(key, '(なし)')
                        mark = "❌" if key in diff_keys else "✅"
                        lines.append(f"| {key} | {self._format_value(exp_val)} | {self._format_value(act_val)} | {mark} |")
                    lines.append("")
            else:
                lines.append("*不一致(NG)リソースはありませんでした*")
            lines.append("")
            lines.append("---")
            lines.append("")

            # 実環境未存在
            lines.append("### 実環境未存在リソース一覧")
            if result['missing']:
                # lines.append("| 識別子 | リソースタイプ | 出典 |")
                # lines.append("|--------|----------------|------|")
                lines.append("| 識別子 | 出典 |")
                lines.append("|--------|------|")
                for r in self._sort_by_source_row(result['missing']):
                    source = self._format_meta(r)
                    identifier = self._format_identifier(r)   # ★ 整形済み識別子を使用
                    identifier = self._escape_markdown_cell(identifier)
                    resource_type = self._escape_markdown_cell(r.resource_type)
                    source = self._escape_markdown_cell(source)
                    # lines.append(f"| {identifier} | {resource_type} | {source} |")
                    lines.append(f"| {identifier} | {source} |")
            else:
                lines.append("*実環境未存在リソースはありませんでした*")
            lines.append("")
            lines.append("---")
            lines.append("")

            # 期待値未定義
            if self.show_extra:
                lines.append("### 期待値未定義リソース一覧")
                if result['extra']:
                    # lines.append("| 識別子 | リソースタイプ |")
                    # lines.append("|--------|----------------|")
                    lines.append("| 識別子 |")
                    lines.append("|--------|")
                    for r in result['extra']:
                        identifier = self._escape_markdown_cell(r.identifier)
                        resource_type = self._escape_markdown_cell(r.resource_type)
                        # lines.append(f"| {identifier} | {resource_type} |")
                        lines.append(f"| {identifier} |")
                else:
                    lines.append("*期待値未定義リソースはありませんでした*")
                lines.append("")
                lines.append("---")
                lines.append("")


            # 対象外行
            lines.append("### 対象外リソース（無効行）一覧")
            if invalid_res:
                # lines.append("| 識別子 | リソースタイプ | 出典 |")
                # lines.append("|--------|----------------|------|")
                lines.append("| 識別子 | 出典 |")
                lines.append("|--------|------|")
                for r in self._sort_by_source_row(invalid_res):
                    source = self._format_meta(r)
                    identifier = self._escape_markdown_cell(r.identifier)
                    resource_type = self._escape_markdown_cell(r.resource_type)
                    source = self._escape_markdown_cell(source)
                    # lines.append(f"| {identifier} | {resource_type} | {source} |")
                    lines.append(f"| {identifier} | {source} |")
            else:
                lines.append("*対象外（無効行）リソースはありませんでした*")
            lines.append("")
            lines.append("---")
            lines.append("")

            # 一致リソース詳細
            lines.append("### 一致(OK)リソース詳細")
            if result['matched']:
                for m in self._sort_by_source_row(result['matched']):
                    lines.append(f"#### リソース識別子: {m['identifier']}")
                    # ★ 出典行
                    meta = m.get('meta', {})
                    source_str = self._format_meta(meta)
                    if source_str:
                        lines.append(f"**出典**: {source_str}")
                    lines.append("")
                    lines.append("| プロパティ | 期待値 | 実績値 | 判定 |")
                    lines.append("|------------|--------|--------|------|")
                    # テンプレート項目順に
                    exp_keys = list(m['expected_props'].keys())
                    act_keys = list(m['actual_props'].keys())
                    ordered_keys = exp_keys + [k for k in act_keys if k not in exp_keys]
                    for key in ordered_keys:
                        exp_val = m['expected_props'].get(key)
                        act_val = m['actual_props'].get(key)
                        lines.append(f"| {key} | {self._format_value(exp_val)} | {self._format_value(act_val)} | ✅ |")
                    lines.append("")
            else:
                lines.append("*一致(OK)リソースはありませんでした*")
            lines.append("")
            lines.append("---")
            lines.append("")

        lines.append(f"*レポート生成日時: {meta_info.get('execution_end', '')}*")
        return "\n".join(lines)

    def _format_meta(self, resource) -> str:
        """メタ情報から出典文字列を生成（NormalizedResource または dict 対応）"""
        if hasattr(resource, 'meta'):
            meta = resource.meta
        else:
            # resource が辞書の場合、直接 meta とみなす
            meta = resource

        file = meta.get("_source_file", "")
        sheet = meta.get("_source_sheet", "")
        row = meta.get("_source_row", "")
        parts = [file, sheet]
        if row:
            parts.append(f"データ部の第 {row} 行目")
        return " / ".join(filter(None, parts))

    def _format_value(self, value) -> str:
        if value is None:
            return "(なし)"
        if isinstance(value, bool):
            return "True" if value else "False"
        s = str(value)
        s_stripped = s.strip()
        # JSON文字列の処理
        if s_stripped and (s_stripped[0] == '{' or s_stripped[0] == '['):
            try:
                obj = json.loads(s)
                s = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
                # HTML特殊文字をエスケープ（<, >, &）
                s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                # Markdownテーブルのパイプもエスケープ
                s = s.replace("|", "\\|")
                return f"`{s}`"
            except (json.JSONDecodeError, TypeError):
                pass
        # 通常の文字列も必ずエスケープ
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        s = s.replace("|", "\\|")
        return s

    def add_expected_resources_section(self, expected_resources: List[NormalizedResource]) -> str:
        """期待値リソースの一覧をMarkdownテーブルで返す"""
        if not expected_resources:
            return "\n## 期待値リソース一覧\n\n*期待値が1件も抽出されませんでした*\n"
        lines = ["## 期待値リソース一覧", ""]
        #lines.append("| 識別子 | リソースタイプ | 主なプロパティ |")
        # lines.append("|--------|----------------|----------------|")
        lines.append("| 識別子 | 主なプロパティ |")
        lines.append("|--------|----------------|")
        for r in expected_resources:
            props_summary = ", ".join(
                f"{k}={self._format_value(v)}" for k, v in sorted(r.properties.items())
            )
            id_status = r.meta.get('_identifier_status', '')
            status_note = '⚠️ ID未検出' if id_status == 'MISSING' else ''
            # lines.append(f"| {r.identifier} {status_note} | {r.resource_type} | {props_summary} |")
            lines.append(f"| {r.identifier} {status_note} | {props_summary} |")
        lines.append("")
        return "\n".join(lines)

    def _sort_by_source_row(self, items, default=0):
        """出典行でソート（数値昇順）"""
        def get_row(item):
            # item が NormalizedResource の場合
            if hasattr(item, 'meta'):
                meta = item.meta
            # item が辞書（matched/modified）の場合
            elif isinstance(item, dict):
                meta = item.get('meta', {})
            else:
                return default
            try:
                return int(meta.get('_source_row', default))
            except (ValueError, TypeError):
                return default
        return sorted(items, key=get_row)

    @staticmethod
    def _format_identifier(resource: NormalizedResource) -> str:
        """識別子を表示用に整形（不明な場合はマークを付ける）"""
        identifier = str(resource.identifier)
        if identifier.startswith("unknown-"):
            return f"(識別子なし: {identifier})"
        return identifier

    @staticmethod
    def _escape_markdown_cell(text: str) -> str:
        """Markdownテーブルセルのためにパイプ文字をエスケープする"""
        return str(text).replace("|", "\\|")
