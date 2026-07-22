# src/main.py
"""
メイン実行モジュール
設定ファイルを読み込み、全Excelファイルを処理する
"""

from collections import defaultdict
import json
import os
import sys
import glob
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from zoneinfo import ZoneInfo
from datetime import datetime, timezone as dt_timezone

import pandas as pd
import yaml

from .core import ExcelReader, HeaderProcessor, DataProcessor, ConfigValidator
from .output import TemplateEngine, TemplateBuilder, JsonGenerator
from .utils import sanitize_filename
from .utils.string_utils import apply_replace_rules
from .models.sheet_context import SheetContext

from .normalizer import ExpectedNormalizer, AwsNormalizer
from .collector import AwsCollector
from .comparator import Comparator
from .comparator.report_generator import ReportGenerator

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class Spec2Clouds:
    """Excel解析のメインクラス"""

    def __init__(self, config_path: str, debug: bool = False):
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)

        self.config = ConfigValidator.load_and_validate(
            config_path,
            exit_on_error=True
        )

        self.input_dir = self.config['input']['directory']
        self.file_pattern = self.config['input'].get('file_pattern', '*.xlsx')

        self.output_dir = self.config['output']['directory']
        self.file_prefix = self.config['output'].get('file_prefix', 'result')
        self.combine_all = self.config['output'].get('combine_all', False)

        self.target_sheets = self.config.get('target_sheets', [])

        template_config = self.config.get('template', {})

        self.auto_generate = template_config.get('auto_generate', True)
        self.auto_generate_only = template_config.get('auto_generate_only', False)
        self.template_dir = template_config.get('directory', 'templates')

        self.debug = debug

        self.header_proc = HeaderProcessor(self.config.get('header', {}))
        self.data_proc = DataProcessor(self.config.get('data', {}))

        self.template_engine = TemplateEngine(
            template_config,
            enable_hot_reload=debug
        )

        self.template_builder = TemplateBuilder(
            overwrite_existing=debug
        )

        os.makedirs(self.output_dir, exist_ok=True)

        if self.auto_generate:
            os.makedirs(self.template_dir, exist_ok=True)

        # 比較関連
        compare_config = self.config.get('compare', {})

        self.timezone_str = compare_config.get('timezone', 'Asia/Tokyo')
        try:
            self.timezone = ZoneInfo(self.timezone_str)
        except Exception:
            logger.warning(f"Invalid timezone '{self.timezone_str}', falling back to UTC")
            self.timezone = dt_timezone.utc

        self.compare_enabled = compare_config.get('enabled', False)
        self.show_extra_resources = compare_config.get('show_extra_resources', True)
        if self.compare_enabled:
            self.aws_collector = AwsCollector(
                region_name=compare_config['aws'].get('region', 'ap-northeast-1'),
                profile_name=compare_config['aws'].get('profile', None)
            )
            self.expected_normalizer = ExpectedNormalizer()
            self.aws_normalizer = AwsNormalizer()
            self.comparator = Comparator()
            self.compare_template_ids = compare_config.get('resources', [])
            self.report_generator = ReportGenerator(
                output_dir=self.output_dir,
                show_extra=self.show_extra_resources
                )

        # AWS アカウント ID の取得（比較機能の有無にかかわらず）
        self.account_id = self._get_aws_account_id()

        # --- 置換ルールの読み込み ---
        self.replace_rules = self._load_replace_rules(config_path)

        self.json_gen = JsonGenerator(
            self.template_engine,
            env=self.config.get('env', ''),
            normalize_config=self.config.get('normalize', {}),
            json_config=self.config.get('json', {}),
            replace_rules=self.replace_rules,
        )

    # ============================================================
    # Replace Rules
    # ============================================================
    def _load_replace_rules(self, config_path: str) -> Dict[str, list]:
        """settings.yaml の replace_rules.mapping に基づき各テンプレートの置換ルールを読み込む"""
        replace_config = self.config.get('replace_rules', {})
        mapping = replace_config.get('mapping', {})
        rules = {}
        base_dir = os.path.dirname(config_path)  # config ディレクトリ
        for tid, filename in mapping.items():
            path = os.path.join(base_dir, filename)
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        rule_list = yaml.safe_load(f)
                        if isinstance(rule_list, list):
                            rules[tid] = rule_list
                            logger.debug(f"Loaded {len(rule_list)} replacement rules for template {tid}")
                        else:
                            logger.warning(f"Invalid format in {path}: expected a list")
                except Exception as e:
                    logger.warning(f"Failed to load replacement rules from {path}: {e}")
            else:
                logger.warning(f"Replacement rule file not found: {path}")
        return rules

    # ============================================================
    # Environment Token Utility
    # ============================================================
    def _env_long_to_short(self, env: str) -> str:
        mapping = {"prd": "P", "reh": "R", "stg": "S", "dev": "D"}
        return mapping.get(env.lower(), "")

    # ============================================================
    # AWS Account ID Utility
    # ============================================================

    def _get_aws_account_id(self) -> str:
        try:
            import boto3
            compare_config = self.config.get('compare', {})
            aws_config = compare_config.get('aws', {})
            session = boto3.Session(
                region_name=aws_config.get('region', 'ap-northeast-1'),
                profile_name=aws_config.get('profile', None)
            )
            sts = session.client('sts')
            return sts.get_caller_identity()['Account']
        except Exception as e:
            logger.warning(f"Failed to get AWS account ID: {e}")
            return None   # 置換しない場合はNoneが適切

    # ============================================================
    # File Search
    # ============================================================

    def find_excel_files(self) -> List[str]:
        pattern = os.path.join(self.input_dir, self.file_pattern)
        return sorted(glob.glob(pattern))

    # ============================================================
    # Template ID
    # ============================================================

    def _get_template_id(
        self,
        reader: ExcelReader,
        sheet_name: str
    ) -> str:
        """
        Template ID取得責務
        """
        id_cell = self.config['template'].get('id_cell', 'A1')

        value = reader.get_cell_value(sheet_name, id_cell)

        return str(value).strip() if value is not None else ''

    # ============================================================
    # Context Load
    # ============================================================

    def _load_sheet_context(
        self,
        reader: ExcelReader,
        sheet_name: str,
        file_name: str
    ) -> SheetContext:
        """
        シート読み込み＋Template ID取得
        """
        raw_df = reader.read_sheet(sheet_name)

        template_id = self._get_template_id(reader, sheet_name)

        return SheetContext(
            file_name=file_name,
            sheet_name=sheet_name,
            raw_df=raw_df,
            template_id=template_id
        )

    # ============================================================
    # Analyze Sheet
    # ============================================================

    def _analyze_sheet_structure(
        self,
        context: SheetContext
    ) -> SheetContext:
        raw_df = context.raw_df

        col_range = self.header_proc.find_column_range(raw_df)

        valid_cols = self.data_proc.filter_columns(raw_df, col_range)

        if not valid_cols:
            raise ValueError("No valid columns found")

        multi_idx, _ = self.header_proc.build(raw_df, col_range)

        valid_multi_idx = self._filter_multi_index(
            multi_idx,
            col_range,
            valid_cols
        )

        data_start_row = (
            self.data_proc.data_start_row
            if self.data_proc.data_start_row is not None
            else self.header_proc.data_start_row
        )

        row_range = self.data_proc.find_row_range(
            raw_df,
            data_start_row,
            col_range
        )

        data_df = self.data_proc.extract(
            raw_df,
            row_range,
            valid_cols
        )

        flat_columns = HeaderProcessor.flatten_columns_parent_only(valid_multi_idx)

        data_df.columns = flat_columns

        context.col_range = col_range
        context.row_range = row_range
        context.valid_cols = valid_cols
        context.flat_columns = flat_columns
        context.data_df = data_df
        context.original_multi_index = valid_multi_idx

        # build の戻り値を受け取る
        multi_idx, hierarchy = self.header_proc.build(raw_df, col_range)
        valid_multi_idx = self._filter_multi_index(multi_idx, col_range, valid_cols)

        # 各有効列の深さを計算
        col_start = col_range[0]
        depths = []
        for c in valid_cols:
            relative_idx = c - col_start
            depths.append(hierarchy.get(relative_idx, 1))   # 最低 1

        context.valid_multi_index = valid_multi_idx
        context.column_depths = depths

        return context

    # ============================================================
    # Template Generate
    # ============================================================

    def _build_template_if_needed(
        self,
        context: SheetContext
    ) -> None:
        if not self.auto_generate:
            return

        if not context.template_id:
            return

        self.template_builder.build_and_save(
            context.flat_columns,
            context.template_id,
            self.template_dir
        )

    # ============================================================
    # JSON Generate
    # ============================================================

    def _generate_json(
        self,
        context: SheetContext
    ) -> List[Dict[str, Any]]:
        if self.auto_generate_only:
            return []

        if not context.template_id:
            return context.data_df.to_dict('records')

        return self.json_gen.generate(
            context.template_id,
            context.data_df,
            source_file=context.file_name,
            source_sheet=context.sheet_name,
            original_df=context.raw_df,
            data_processor=self.data_proc,
            row_start=context.row_range[0],
            flat_columns=context.flat_columns,
            column_depths=context.column_depths,
            original_columns=context.valid_multi_index     # ★ MultiIndex そのもの
        )

    # ============================================================
    # Utility
    # ============================================================

    def _filter_multi_index(
        self,
        index: pd.Index,
        col_range: tuple,
        valid_cols: List[int]
    ) -> pd.Index:
        start, _ = col_range

        rel_indices = [c - start for c in valid_cols]

        if isinstance(index, pd.MultiIndex):
            arrays = [
                index.get_level_values(lv)[rel_indices]
                for lv in range(index.nlevels)
            ]
            return pd.MultiIndex.from_arrays(arrays)

        return index[rel_indices]

    # ============================================================
    # Process Sheet
    # ============================================================

    def process_sheet(
        self,
        reader: ExcelReader,
        sheet_name: str,
        file_name: str
    ) -> List[Dict[str, Any]]:
        logger.info(f"Processing sheet: {sheet_name}")

        context = self._load_sheet_context(
            reader,
            sheet_name,
            file_name
        )

        if context.raw_df.empty:
            logger.warning(f"Empty sheet skipped: {sheet_name}")
            return []

        context = self._analyze_sheet_structure(context)

        self._build_template_if_needed(context)

        return self._generate_json(context)

    # ============================================================
    # Process File
    # ============================================================

    def process_file(self, file_path: str, json_out_dir: str) -> List[Dict[str, Any]]:
        file_name = os.path.basename(file_path)
        reader = ExcelReader(file_path)

        target_sheets = [
            s for s in reader.get_sheet_names()
            if s in self.target_sheets
        ]

        file_results = []

        for sheet_name in target_sheets:
            try:
                results = self.process_sheet(
                    reader,
                    sheet_name,
                    file_name
                )

                if results:
                    safe_sheet = sanitize_filename(sheet_name)
                    out_path = os.path.join(
                        json_out_dir,
                        f"{self.file_prefix}_{safe_sheet}.json"
                    )
                    self.json_gen.save(results, out_path)
                    file_results.extend(results)

            except Exception as e:
                logger.error(
                    f"Error processing sheet {sheet_name}: {e}",
                    exc_info=self.debug
                )

        if file_results:
            out_path = os.path.join(
                json_out_dir,
                f"{self.file_prefix}_all.json"
            )
            self.json_gen.save(file_results, out_path)

        return file_results

    # ============================================================
    # Run
    # ============================================================

    def run(self) -> None:
        files = self.find_excel_files()
        if not files:
            logger.warning("No Excel files found")
            return

        # ★ 実行開始日時（秒まで）を取得
        exec_start = datetime.now().strftime("%Y%m%d%H%M%S")
        env = self.config.get('env', 'dev') or 'unknown'
        run_folder_name = f"{env}-{exec_start}"

        all_results = []

        # ★ combined の下に env-日時 フォルダを作成
        combined_run_dir = os.path.join(self.output_dir, 'combined', run_folder_name)
        os.makedirs(combined_run_dir, exist_ok=True)

        for file_path in files:
            try:
                start_time = datetime.now(self.timezone)
                safe_name = sanitize_filename(os.path.basename(file_path))

                # ファイル名フォルダの下に 環境-実行日時 フォルダを作成
                file_output_dir = os.path.join(self.output_dir, safe_name)
                run_dir = os.path.join(file_output_dir, run_folder_name)
                json_dir = os.path.join(run_dir, 'json')
                reports_dir = os.path.join(run_dir, 'reports')

                os.makedirs(json_dir, exist_ok=True)
                os.makedirs(reports_dir, exist_ok=True)

                # ファイル処理（JSON出力先を新しい json_dir に変更）
                file_results = self.process_file(file_path, json_dir)
                all_results.extend(file_results)

                # ファイル単位の比較を実行（reports_dir を新しい場所に）
                if self.compare_enabled and file_results:
                    self._run_comparison_for_file(
                        start_time,
                        file_results,
                        os.path.basename(file_path), reports_dir
                    )

            except Exception as e:
                logger.error(
                    f"Failed to process {file_path}: {e}",
                    exc_info=self.debug
                )

        # 全体統合JSONを combined/ に保存
        if self.combine_all and all_results:
            out_path = os.path.join(combined_run_dir, f"{self.file_prefix}_combined_all.json")
            self.json_gen.save(all_results, out_path)

    def _run_comparison_for_file(self, start_time, file_records: List[Dict], file_name: str, reports_dir: str):
        """ファイル単位の比較を実行し、レポートを生成する"""
        # レコードをテンプレートIDでグループ化
        records_by_tid = defaultdict(list)
        for rec in file_records:
            tid = rec.get("_template_id")
            if tid:
                records_by_tid[tid].append(rec)

        all_resource_results = {}
        for template_id in records_by_tid.keys():
            # フィルタ: 空リストなら全テンプレートを処理、指定があればそれだけ処理
            if self.compare_template_ids and template_id not in self.compare_template_ids:
                continue
            try:
                # 専用メソッドでリソースタイプを解決
                resource_type = ExpectedNormalizer.get_resource_type(template_id)
                if not resource_type or resource_type == "unknown":
                    logger.warning(f"No resource type mapped for template {template_id}")
                    continue

                # テンプレートIDに属するレコードをシート名でグループ化
                sheet_groups = defaultdict(list)
                for rec in records_by_tid[template_id]:
                    # 直接フィールドを優先。テンプレート由来の source.sheet はフォールバック
                    sheet = rec.get('_source_sheet') or rec.get('source', {}).get('sheet', '')
                    if not sheet:
                        sheet = f"__unknown_{template_id}__"  # フォールバック
                    sheet_groups[sheet].append(rec)

                # シートごとに比較を実行
                for sheet_name, sheet_records in sheet_groups.items():
                    exp_resources = self.expected_normalizer.normalize(sheet_records, template_id)
                    valid_exp = [r for r in exp_resources if r.meta.get('_enabled', True)]
                    invalid_exp = [r for r in exp_resources if not r.meta.get('_enabled', True)]

                    raw_aws = self.aws_collector.collect(resource_type)
                    act_resources = self.aws_normalizer.normalize(raw_aws, resource_type)

                    # テンプレートの比較キーに存在しないプロパティを削除
                    comparison_keys = ExpectedNormalizer.COMPARISON_KEYS_MAP.get(resource_type, [])
                    if comparison_keys:
                        for act_res in act_resources:
                            act_res.properties = {k: v for k, v in act_res.properties.items() if k in comparison_keys}

                    if template_id in self.replace_rules and self.replace_rules[template_id]:
                        for act_res in act_resources:
                            # apply_replace_rules は辞書を再帰的に処理する
                            act_res.properties = apply_replace_rules(
                                act_res.properties,
                                self.replace_rules[template_id],
                            )

                    # テンプレートデータのキーを取得
                    template = self.template_engine.load(template_id)  # テンプレートJSONを読み込み
                    allowed_keys = list(template.get('data', {}).keys())

                    result = self.comparator.compare(
                        valid_exp,
                        act_resources,
                        allowed_keys=allowed_keys,
                        invalid_exp=invalid_exp,
                        )
                    result['resource_type'] = resource_type
                    result['template_id'] = template_id
                    result['invalid_resources'] = invalid_exp
                    result['sheet_name'] = sheet_name

                    all_resource_results[sheet_name] = result

            except Exception as e:
                logger.error(f"Comparison failed for {template_id}: {e}", exc_info=self.debug)

        end_time = datetime.now(self.timezone)
        # 同じタイムゾーンを持つオブジェクト同士なので、そのまま引き算が可能です
        duration = end_time - start_time
        execution_time_str = str(duration)  # 例: "0:01:23.456789" または日を跨ぐと "1 day, 0:05:20"
        meta_info = {
            "execution_start": start_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "execution_end": end_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "execution_time": execution_time_str,
            "region": self.aws_collector.session.region_name,                                # AWSアカウントID
            "account_id": self.account_id or "Unknown",                                      # AWSアカウントID
            "source": f"[Excel file] {file_name}",                                           # Excelファイル名
            "env": self.config.get('env', ''),                                               # 環境
        }

        if all_resource_results:
            # 統合レポート生成
            md_content = self.report_generator.generate_file_report_markdown(
                all_resource_results,
                file_name,
                meta_info,
                show_extra=self.show_extra_resources)

            md_path = os.path.join(reports_dir, "compare_report.md")

            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)

            # 機械可読サマリ
            summary_path = os.path.join(reports_dir, "compare_summary.json")
            summary = {
                "file": file_name,
                "execution_time": meta_info["execution_start"],
                "resources": {}
            }
            for sheet_name, res in all_resource_results.items():
                summary["resources"][sheet_name] = {
                    "matched": len(res.get('matched', [])),
                    "modified": len(res.get('modified', [])),
                    "missing": len(res.get('missing', [])),
                    "extra": len(res.get('extra', [])) if self.show_extra_resources else 'hidden',
                }
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

            logger.info(f"Comparison report saved to {reports_dir}")

def main():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        'config',
        nargs='?',
        default='config/settings.yaml'
    )

    parser.add_argument(
        '--debug',
        action='store_true'
    )

    args = parser.parse_args()

    spec2Clouds_obj = Spec2Clouds(
        args.config,
        debug=args.debug
    )

    spec2Clouds_obj.run()

if __name__ == '__main__':
    main()
