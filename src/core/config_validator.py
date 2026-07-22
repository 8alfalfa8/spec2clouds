# src/core/config_validator.py
"""
設定ファイルの内容を検証し、エラーを収集するモジュール
ConfigValidatorクラスを提供
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class ConfigValidator:
    """設定ファイルのバリデータ（シングルトン）"""

    _instance = None
    _valid_envs = ['prd', 'reh', 'stg', 'dev', 'p', 'r', 's', 'd', '']
    _valid_unicode_forms = ['NFC', 'NFKC', 'NFD', 'NFKD']

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def validate(self, config: Dict[str, Any]) -> List[str]:
        """
        設定を検証し、エラーリストを返す

        Args:
            config: 設定辞書

        Returns:
            エラーメッセージのリスト（空の場合はエラーなし）
        """
        errors = []

        # 必須フィールドのチェック
        errors.extend(self._validate_required_fields(config))

        # 各セクションの検証
        errors.extend(self._validate_env(config.get('env', '')))
        errors.extend(self._validate_input(config.get('input', {})))
        errors.extend(self._validate_output(config.get('output', {})))
        errors.extend(self._validate_template(config.get('template', {})))
        errors.extend(self._validate_header(config.get('header', {})))
        errors.extend(self._validate_data(config.get('data', {})))
        errors.extend(self._validate_normalize(config.get('normalize', {})))
        errors.extend(self._validate_target_sheets(config.get('target_sheets', [])))

        return errors

    def _validate_required_fields(self, config: Dict[str, Any]) -> List[str]:
        """必須フィールドの検証"""
        errors = []

        required = ['input', 'output']
        for field in required:
            if field not in config:
                errors.append(f"Missing required field: '{field}'")

        return errors

    def _validate_env(self, env: str) -> List[str]:
        """env設定の検証"""
        errors = []

        if not isinstance(env, str):
            errors.append(f"env must be a string, got: {type(env).__name__}")
            return errors

        env_lower = env.lower()
        if env_lower not in self._valid_envs:
            errors.append(
                f"env '{env}' is invalid. "
                f"Valid values: {', '.join(self._valid_envs[:-1])} or empty string"
            )

        return errors

    def _validate_input(self, input_config: Dict[str, Any]) -> List[str]:
        """input設定の検証"""
        errors = []

        directory = input_config.get('directory', 'input')
        if not isinstance(directory, str):
            errors.append(f"input.directory must be a string, got: {type(directory).__name__}")
        elif not os.path.exists(directory):
            errors.append(f"Input directory '{directory}' does not exist")

        file_pattern = input_config.get('file_pattern', '*.xlsx')
        if not isinstance(file_pattern, str):
            errors.append(f"input.file_pattern must be a string, got: {type(file_pattern).__name__}")

        return errors

    def _validate_output(self, output_config: Dict[str, Any]) -> List[str]:
        """output設定の検証"""
        errors = []

        directory = output_config.get('directory', 'output')
        if not isinstance(directory, str):
            errors.append(f"output.directory must be a string, got: {type(directory).__name__}")

        file_prefix = output_config.get('file_prefix', 'result')
        if not isinstance(file_prefix, str):
            errors.append(f"output.file_prefix must be a string, got: {type(file_prefix).__name__}")

        combine_all = output_config.get('combine_all', False)
        if not isinstance(combine_all, bool):
            errors.append(f"output.combine_all must be a boolean, got: {type(combine_all).__name__}")

        return errors

    def _validate_template(self, template_config: Dict[str, Any]) -> List[str]:
        """template設定の検証"""
        errors = []

        auto_generate = template_config.get('auto_generate', True)
        if not isinstance(auto_generate, bool):
            errors.append(f"template.auto_generate must be a boolean, got: {type(auto_generate).__name__}")

        auto_generate_only = template_config.get('auto_generate_only', False)
        if not isinstance(auto_generate_only, bool):
            errors.append(f"template.auto_generate_only must be a boolean, got: {type(auto_generate_only).__name__}")

        # テンプレートディレクトリの存在確認
        if auto_generate:
            directory = template_config.get('directory', 'templates')
            if not isinstance(directory, str):
                errors.append(f"template.directory must be a string, got: {type(directory).__name__}")
            elif not os.path.exists(directory):
                # 自動作成する場合は警告のみ
                logger.warning(f"Template directory '{directory}' does not exist, will be created")

        # マッピングの検証
        mapping = template_config.get('mapping', {})
        if not isinstance(mapping, dict):
            errors.append(f"template.mapping must be a dictionary, got: {type(mapping).__name__}")
        else:
            for tid, filename in mapping.items():
                if not isinstance(tid, str):
                    errors.append(f"Template ID must be a string, got: {type(tid).__name__}")
                if not isinstance(filename, str):
                    errors.append(f"Template filename for '{tid}' must be a string, got: {type(filename).__name__}")

        # id_cellの検証
        id_cell = template_config.get('id_cell', 'A1')
        if not isinstance(id_cell, str):
            errors.append(f"template.id_cell must be a string, got: {type(id_cell).__name__}")

        return errors

    def _validate_header(self, header_config: Dict[str, Any]) -> List[str]:
        """header設定の検証"""
        errors = []

        start_row = header_config.get('start_row', 1)
        if not isinstance(start_row, int) or start_row < 1:
            errors.append(f"header.start_row must be a positive integer >= 1, got: {start_row}")

        max_levels = header_config.get('max_levels', 3)
        if not isinstance(max_levels, int) or max_levels < 1:
            errors.append(f"header.max_levels must be an integer >= 1, got: {max_levels}")

        start_string = header_config.get('start_string', '')
        if not isinstance(start_string, str):
            errors.append(f"header.start_string must be a string, got: {type(start_string).__name__}")

        end_string = header_config.get('end_string', '')
        if not isinstance(end_string, str):
            errors.append(f"header.end_string must be a string, got: {type(end_string).__name__}")

        fill_empty_cells = header_config.get('fill_empty_cells', True)
        if not isinstance(fill_empty_cells, bool):
            errors.append(f"header.fill_empty_cells must be a boolean, got: {type(fill_empty_cells).__name__}")

        return errors

    def _validate_data(self, data_config: Dict[str, Any]) -> List[str]:
        """data設定の検証"""
        errors = []

        # data_start_row
        data_start_row = data_config.get('data_start_row', '')
        if data_start_row not in (None, ''):
            try:
                int_val = int(data_start_row)
                if int_val < 1:
                    errors.append(f"data.data_start_row must be >= 1, got: {int_val}")
            except (ValueError, TypeError):
                errors.append(f"data.data_start_row must be an integer, got: {data_start_row}")

        # column_control
        col_ctrl = data_config.get('column_control', {})
        if col_ctrl:
            row = col_ctrl.get('row', 0)
            if row:
                if not isinstance(row, int) or row < 1:
                    errors.append(f"data.column_control.row must be >= 1, got: {row}")

            exclude_value = col_ctrl.get('exclude_value', '0')
            if not isinstance(exclude_value, str):
                errors.append(f"data.column_control.exclude_value must be a string, got: {type(exclude_value).__name__}")

        # invalid_row_control
        inv_ctrl = data_config.get('invalid_row_control', {})
        if inv_ctrl:
            column = inv_ctrl.get('column', '')
            if column and not isinstance(column, str):
                errors.append(f"data.invalid_row_control.column must be a string, got: {type(column).__name__}")

        return errors

    def _validate_normalize(self, normalize_config: Dict[str, Any]) -> List[str]:
        """normalize設定の検証"""
        errors = []

        unicode_form = normalize_config.get('unicode_form', 'NFKC')
        if unicode_form and unicode_form not in self._valid_unicode_forms:
            errors.append(
                f"normalize.unicode_form '{unicode_form}' is invalid. "
                f"Valid: {', '.join(self._valid_unicode_forms)}"
            )

        regex_escape = normalize_config.get('regex_escape', True)
        if not isinstance(regex_escape, bool):
            errors.append(f"normalize.regex_escape must be a boolean, got: {type(regex_escape).__name__}")

        return errors

    def _validate_target_sheets(self, target_sheets: List[str]) -> List[str]:
        """target_sheets設定の検証"""
        errors = []

        if not isinstance(target_sheets, list):
            errors.append(f"target_sheets must be a list, got: {type(target_sheets).__name__}")
            return errors

        # 重複チェック
        if len(target_sheets) != len(set(target_sheets)):
            errors.append("Duplicate entries found in target_sheets")

        # 各シート名の検証
        for sheet in target_sheets:
            if not isinstance(sheet, str):
                errors.append(f"target_sheets entry must be a string, got: {type(sheet).__name__}")

        return errors

    @classmethod
    def load_and_validate(
        cls,
        config_path: str,
        exit_on_error: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        設定を読み込み、検証する

        Args:
            config_path: 設定ファイルのパス
            exit_on_error: エラー時に終了するか

        Returns:
            検証済みの設定辞書（エラー時はNone）
        """
        import yaml

        if not os.path.exists(config_path):
            error_msg = f"Config file not found: {config_path}"
            if exit_on_error:
                print(error_msg)
                sys.exit(1)
            logger.error(error_msg)
            return None

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            error_msg = f"Failed to parse config file: {e}"
            if exit_on_error:
                print(error_msg)
                sys.exit(1)
            logger.error(error_msg)
            return None

        validator = cls()
        errors = validator.validate(config)

        if errors:
            print("\n" + "=" * 60)
            print("CONFIGURATION VALIDATION FAILED")
            print("=" * 60)
            for error in errors:
                print(f"  ❌ {error}")
            print("=" * 60)

            if exit_on_error:
                print("\nPlease fix the configuration and try again.")
                sys.exit(1)
            else:
                print("\nContinuing with warnings...\n")
                logger.warning(f"Config validation found {len(errors)} issues")

        return config
