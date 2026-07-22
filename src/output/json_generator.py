# src/output/json_generator.py
"""
JSON生成モジュール
テンプレートエンジンを使用してDataFrame行データをJSONへ変換する
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional

import pandas as pd

from .template_engine import TemplateEngine
from ..utils import normalize_text, is_empty_value
from collections import OrderedDict

logger = logging.getLogger(__name__)


class JsonGenerator:
    """DataFrame行データをJSONへ変換する"""

    _ENV_MAP_LONG = {
        "prd": "prd",
        "reh": "reh",
        "stg": "stg",
        "dev": "dev",
    }

    _ENV_MAP_SHORT = {
        "prd": "P",
        "reh": "R",
        "stg": "S",
        "dev": "D",
    }

    def __init__(
        self,
        template_engine: TemplateEngine,
        env: str = "",
        normalize_config: Optional[dict] = None,
        json_config: Optional[Dict[str, list]] = None,
        account_id: Optional[str] = None,          # 後方互換のため残す（任意）
        replace_rules: Optional[Dict[str, list]] = None,
    ):
        self.engine = template_engine
        self.env = str(env).strip().lower()

        normalize_config = normalize_config or {}

        self.unicode_form = normalize_config.get("unicode_form", "")
        self.regex_escape = normalize_config.get("regex_escape", False)

        self.account_id = account_id                     # 追加
        self.replace_rules = replace_rules or {}
        self.key_value_mappings = json_config.get("key_value_mappings", {})
        self.parse_json_child_paths = set(json_config.get("parse_json_child_paths", []))
        self.preserve_string_paths = set(json_config.get("preserve_string_paths", []))

    # ============================================================
    # Public API
    # ============================================================

    def generate(
        self,
        template_id: str,
        df: pd.DataFrame,
        source_file: str = "",
        source_sheet: str = "",
        original_df: Optional[pd.DataFrame] = None,
        data_processor: Optional[Any] = None,
        row_start: int = 0,
        flat_columns: Optional[List[str]] = None,
        column_depths: Optional[List[int]] = None,
        original_columns: Optional[pd.Index] = None
    ) -> List[Dict[str, Any]]:
        """
        DataFrame全行をJSON化
        """
        template = self.engine.load(template_id)

        results = []
        skipped = 0

        for idx, (_, row) in enumerate(df.iterrows()):
            original_row_index = row_start + idx

            # ★ 行の全セル値をリスト化
            row_values = [row.iloc[j] for j in range(len(row))]

            rendered = self._generate_single_row(
                template=template,
                row_values=row_values,
                row_index=original_row_index + 1,
                source_file=source_file,
                source_sheet=source_sheet,
                template_id=template_id,
                flat_columns=flat_columns,
                column_depths=column_depths,
                original_columns=original_columns
            )

            # 行有効判定
            if data_processor and original_df is not None:
                row_validity = data_processor.is_row_valid(
                    original_df,
                    original_row_index
                )

                if row_validity is not None:
                    if (
                        data_processor.skip_invalid_rows
                        and row_validity == data_processor.invalid_output_value
                    ):
                        skipped += 1
                        continue

                    rendered[data_processor.invalid_output_field] = row_validity

            # 行有効判定の後にテンプレートIDを追加（必要に応じて）
            rendered["_template_id"] = template_id
            # ★ 強制的にソースメタデータを注入
            rendered["_source_file"] = source_file
            rendered["_source_sheet"] = source_sheet
            rendered["_row_index"] = idx + 1  # 1ベースの行インデックス
            results.append(rendered)

        if skipped:
            logger.info(f"Skipped {skipped} invalid rows")

        return results

    def generate_single(
        self,
        template_id: str,
        row_data: Dict[str, Any],
        source_file: str = "",
        source_sheet: str = "",
        row_index: int = 0
    ) -> Dict[str, Any]:
        """
        単一行JSON生成
        """
        df = pd.DataFrame([row_data])

        results = self.generate(
            template_id=template_id,
            df=df,
            source_file=source_file,
            source_sheet=source_sheet,
            row_start=row_index
        )

        return results[0] if results else {}

    def save(
        self,
        data: List[Dict[str, Any]],
        output_path: str
    ) -> None:
        """
        JSONファイル保存
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved: {output_path}")

        except IOError as e:
            logger.error(f"Failed to save {output_path}: {e}")
            raise

    # ============================================================
    # Internal Processing
    # ============================================================

    def _generate_single_row(
        self,
        template: Dict[str, Any],
        row_values: list,               # ★ 行の値リスト（列順）
        row_index: int,
        source_file: str,
        source_sheet: str,
        template_id: str,
        flat_columns: List[str],
        column_depths: List[int],       # ★ 各列の深さ（1=単一階層, 2以上=多階層）
        original_columns: pd.Index      # ★ 有効列の MultiIndex
    ) -> Dict[str, Any]:
        # 1. 単一階層の列だけを vars_dict に追加
        vars_dict = {}
        for i, depth in enumerate(column_depths):
            if depth == 1:
                col_name = flat_columns[i]
                raw_val = row_values[i]
                vars_dict[col_name] = self._normalize_preserve_env_tokens(raw_val)

        # 2. 多階層列だけ JSON 化
        nested_vars = self._nest_columns_from_values(
            row_values, flat_columns, column_depths, original_columns, template_id
        )

        # 3. マージ
        vars_dict.update(nested_vars)

        # 4. メタ情報を追加
        vars_dict.update({
            "_row_index": row_index,
            "_source_file": source_file,
            "_source_sheet": source_sheet,
            "_env": self.env,
        })

        # 5. テンプレートレンダリング
        rendered = self.engine.render(template, vars_dict)

        # 6. env置換とカスタム置換
        rendered = self._replace_env_tokens_recursive(rendered)
        rendered = self._apply_custom_replacements(rendered, template_id)

        return rendered

    # 追加: カスタム置換ルールの適用
    def _apply_custom_replacements(self, value: Any, template_id: str) -> Any:
        if template_id not in self.replace_rules:
            return value

        rules = self.replace_rules[template_id]
        if not rules:
            return value

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

        return self._traverse_and_replace(value, replace_text)

    # 追加: 再帰的に文字列を置換するユーティリティ
    def _traverse_and_replace(self, obj, func):
        if isinstance(obj, dict):
            return {k: self._traverse_and_replace(v, func) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._traverse_and_replace(item, func) for item in obj]
        elif isinstance(obj, str):
            return func(obj)
        else:
            return obj

    # ============================================================
    # Variable Dictionary Construction
    # ============================================================
    def _build_vars_dict(self, row: pd.Series, row_index: int,
                        source_file: str, source_sheet: str,
                        template_id: str) -> Dict[str, Any]:
        # 生のセル値
        raw_vars = {
            k: self._normalize_preserve_env_tokens(v)
            for k, v in row.to_dict().items()
        }

        # テンプレートごとの置換ルールをセル値文字列に適用（辞書全体を置換するのではなく、各文字列に）
        if template_id in self.replace_rules:
            rules = self.replace_rules[template_id]
            def replace_string(s):
                if not isinstance(s, str):
                    return s
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

            raw_vars = {
                k: replace_string(v) for k, v in raw_vars.items()
            }

        # 環境トークン置換
        vars_dict = {
            k: self._replace_env_tokens(v) for k, v in raw_vars.items()
        }

        vars_dict.update({
            "_row_index": row_index + 1,       # 1始まりに
            "_source_file": source_file,
            "_source_sheet": source_sheet,
            "_env": self.env,
        })
        return vars_dict

    # ============================================================
    # Environment Replace
    # ============================================================

    def _replace_env_tokens(self, value: Any) -> Any:
        """
        文字列内の環境プレースホルダ置換
        """
        if not isinstance(value, str):
            return value

        if self.env not in self._ENV_MAP_LONG:
            return value

        value = value.replace(
            "{prd|reh|stg|dev}",
            self._ENV_MAP_LONG[self.env]
        )

        value = value.replace(
            "{P|R|S|D}",
            self._ENV_MAP_SHORT[self.env]
        )

        return value

    # JSON全体を再帰走査してenv token置換
    def _replace_env_tokens_recursive(self, value: Any) -> Any:
        """
        JSON全体を再帰走査してenv token置換
        """
        if isinstance(value, dict):
            return {
                k: self._replace_env_tokens_recursive(v)
                for k, v in value.items()
            }

        if isinstance(value, list):
            return [
                self._replace_env_tokens_recursive(v)
                for v in value
            ]

        return self._replace_env_tokens(value)

    # ============================================================
    # Normalization
    # ============================================================

    def _normalize_text(self, value: Any) -> Any:
        """
        Excel文字列正規化
        """
        if not isinstance(value, str):
            return value

        return normalize_text(
            value,
            unicode_form=self.unicode_form,
            regex_escape=self.regex_escape,
            strip=True
        )

    # 追加: env token を保護したまま normalize するユーティリティS
    def _normalize_preserve_env_tokens(self, value: Any) -> Any:
        """
        env token を保護したまま normalize する
        """
        if not isinstance(value, str):
            return value

        placeholders = {
            '{prd|reh|stg|dev}': '__ENV_LONG__',
            '{P|R|S|D}': '__ENV_SHORT__',
        }

        # 退避
        for token, ph in placeholders.items():
            value = value.replace(token, ph)

        # normalize
        value = normalize_text(
            value,
            unicode_form=self.unicode_form,
            regex_escape=self.regex_escape,
            strip=True
        )

        # 復元
        for token, ph in placeholders.items():
            value = value.replace(ph, token)

        return value

    def _nest_columns_from_values(
        self,
        row_values: list,
        flat_columns: List[str],
        column_depths: List[int],
        original_columns: pd.Index,
        template_id: str
    ) -> Dict[str, Any]:
        nested = {}
        seen = set()
        unique_parents = [flat_columns[i] for i in range(len(flat_columns))
                        if not (flat_columns[i] in seen or seen.add(flat_columns[i]))]

        for parent in unique_parents:
            children = []  # (original_index, child_names, row_value)
            for i in range(len(flat_columns)):
                if flat_columns[i] == parent and column_depths[i] > 1:
                    col_tuple = original_columns[i]
                    depth = column_depths[i] if column_depths else None

                    if isinstance(col_tuple, tuple):
                        if depth is not None:
                            child_names = col_tuple[1:depth]
                        else:
                            child_names = col_tuple[1:]
                    else:
                        child_names = ()

                    children.append((i, child_names, row_values[i]))

            if not children:
                continue

            def apply_replacements(value):
                if not isinstance(value, str):
                    return value
                s = self._normalize_preserve_env_tokens(value)
                s = self._replace_env_tokens(s)
                if template_id in self.replace_rules:
                    s = self._apply_custom_replacements(s, template_id)
                return s

            pairs = []
            i = 0
            while i < len(children):
                idx, child_names, raw_val = children[i]
                val = apply_replacements(raw_val)

                # キー列判定
                key_label = None
                key_value = None
                for name in child_names:
                    name_str = str(name)
                    if ':' in name_str:
                        key_label, key_value = name_str.split(':', 1)
                        break

                if key_label is not None:
                    # 直後の列をデータ列として扱う
                    if i + 1 < len(children):
                        next_idx, next_child_names, next_raw = children[i + 1]
                        next_is_key = any(':' in str(n) for n in next_child_names)
                        if not next_is_key:
                            next_val = apply_replacements(next_raw)
                            # データ列の一意なラベルは Level 2 にある
                            data_key = "Value"
                            if len(next_child_names) > 1:
                                l2 = str(next_child_names[1]).strip()
                                if l2:
                                    data_key = l2
                            elif len(next_child_names) > 0:
                                l1 = str(next_child_names[0]).strip()
                                if l1 and ':' not in l1:
                                    data_key = l1
                            if not is_empty_value(next_val):
                                entry = OrderedDict()
                                entry[key_label] = key_value
                                entry[data_key] = str(next_val)
                                pairs.append(entry)
                            i += 2
                            continue
                        else:
                            if not is_empty_value(val):
                                entry = OrderedDict()
                                entry[key_label] = key_value
                                entry[self._extract_data_key(child_names)] = str(val)
                                pairs.append(entry)
                            i += 1
                            continue
                    else:
                        if not is_empty_value(val):
                            entry = OrderedDict()
                            entry[key_label] = key_value
                            entry[self._extract_data_key(child_names)] = str(val)
                            pairs.append(entry)
                        i += 1
                        continue
                else:
                    i += 1

            segments = self._split_object_segments(children)

            has_nested_plain = any(
                len(self._clean_child_path(child_names)) > 1
                and not any(self._is_key_marker(name) for name in self._clean_child_path(child_names))
                for _, child_names, _ in children
            )

            if len(segments) > 1 or has_nested_plain:
                objects = []

                for segment in segments:
                    obj = OrderedDict()

                    for idx, child_names, raw_val in segment:
                        path = self._clean_child_path(child_names)
                        if not path:
                            continue

                        val = apply_replacements(raw_val)

                        if any(self._is_key_marker(name) for name in path):
                            self._ensure_key_value_container(obj, path)

                            if not is_empty_value(val):
                                self._assign_key_value(obj, path, val, parent_key=parent)

                            continue

                        if is_empty_value(val):
                            continue

                        # print(f"path============== {path}")
                        self._assign_nested_value(obj, path, val, parent_key=parent)

                    if self._has_meaningful_value(obj):
                        objects.append(obj)

                nested[parent] = json.dumps(
                    objects,
                    ensure_ascii=False,
                    sort_keys=False
                ) if objects else ""

                continue

            if pairs:
                nested[parent] = json.dumps(pairs, ensure_ascii=False, sort_keys=False)
            else:
                # フラットオブジェクトとして処理
                child_dict = {}
                for idx, child_names, raw_val in children:
                    val = apply_replacements(raw_val)
                    if is_empty_value(val):
                        continue
                    key_label = None
                    key_value = None
                    for name in child_names:
                        name_str = str(name)
                        if ':' in name_str:
                            key_label, key_value = name_str.split(':', 1)
                            break
                    if key_label is not None:
                        child_dict[key_label] = str(val)
                    else:
                        child_key = "_".join(str(n) for n in child_names if n)
                        if not child_key:
                            child_key = "value"
                        child_dict[child_key] = str(val)
                if child_dict:
                    nested[parent] = json.dumps(child_dict, ensure_ascii=False, sort_keys=False)
                else:
                    nested[parent] = ""

        return nested

    def _extract_data_key(self, child_names, default: str = "Value") -> str:
        """
        Key:xxx の値名をヘッダー階層から取得する。
        例: ('aaa:bbb', 'ccc', 'Value') -> 'ccc'
        """
        seen_key = False

        for name in child_names:
            name_str = str(name).strip()
            if not name_str:
                continue

            if ':' in name_str:
                seen_key = True
                continue

            if seen_key and name_str != default:
                return name_str

        return default

    def _has_key_marker(self, child_names) -> bool:
        return any(':' in str(name) for name in child_names)

    def _extract_plain_key(self, child_names) -> str:
        for name in reversed(child_names):
            name_str = str(name).strip()
            if not name_str:
                continue
            if ':' in name_str:
                continue
            if name_str == "Value":
                continue
            return name_str
        return ""

    def _is_mixed_object_group(self, children) -> bool:
        has_key_value = False
        has_plain = False

        for _, child_names, _ in children:
            if self._has_key_marker(child_names):
                has_key_value = True
            elif self._extract_plain_key(child_names):
                has_plain = True

        return has_key_value and has_plain

    def _coerce_json_scalar(self, value: Any) -> Any:
        if not isinstance(value, str):
            return value

        s = value.strip()

        if s.lower() == "true":
            return True
        if s.lower() == "false":
            return False

        try:
            if s.isdigit() or (s.startswith("-") and s[1:].isdigit()):
                return int(s)
            return float(s)
        except ValueError:
            return value

    def _is_key_marker(self, name: Any) -> bool:
        return ':' in str(name)

    def _split_key_marker(self, name: Any) -> tuple:
        left, right = str(name).split(':', 1)
        return left.strip(), right.strip()

    def _clean_child_path(self, child_names) -> list:
        path = []
        prev = None

        for name in child_names:
            name_str = str(name).strip()
            if not name_str:
                continue
            if name_str == prev:
                continue
            path.append(name_str)
            prev = name_str

        return path

    def _split_object_segments(self, children):
        segments = []
        current = []
        seen_scalar_roots = set()

        for child in children:
            _, child_names, _ = child
            path = self._clean_child_path(child_names)

            root = path[0] if path else ""
            is_scalar_root = bool(root) and not self._is_key_marker(root) and len(path) == 1

            if current and is_scalar_root and root in seen_scalar_roots:
                segments.append(current)
                current = []
                seen_scalar_roots = set()

            current.append(child)

            if is_scalar_root:
                seen_scalar_roots.add(root)

        if current:
            segments.append(current)

        return segments

    def _assign_nested_value(self, obj: dict, path: list, value: Any, parent_key: str = "") -> None:
        cur = obj
        for key in path[:-1]:
            logger.debug(f"key=================={key}")
            cur = cur.setdefault(key, OrderedDict())

        parsed_value = self._maybe_parse_json_by_path(value, path)

        # ★ 修正: 親キーがある場合は結合してパスを判定 (例: Metrics.MetricStat.Period)
        full_path_list = [parent_key] if parent_key else []
        full_path_list.extend(path)
        full_path_str = ".".join(str(p).strip() for p in full_path_list if str(p).strip())

        if isinstance(parsed_value, str) and full_path_str not in self.preserve_string_paths:
            parsed_value = self._coerce_json_scalar(parsed_value)

        cur[path[-1]] = parsed_value

    def _assign_key_value(self, obj: dict, path: list, value: Any, parent_key: str = "") -> None:
        marker_index = next(
            i for i, name in enumerate(path)
            if self._is_key_marker(name)
        )

        container_path = path[:marker_index]
        marker = path[marker_index]

        marker_label, marker_value = self._split_key_marker(marker)
        container_name = container_path[-1] if container_path else ""
        mapping = self._get_key_value_mapping(container_name)
        key_name = mapping.get("key_field") or marker_label

        value_key = self._extract_value_key_from_path(path, marker_index)
        if not value_key:
            value_key = mapping.get("value_field") or "Value"

        # ★ 修正: 多階層用のフルパスを構築 (例: Metrics.AccountId)
        full_path_list = []
        if parent_key:
            full_path_list.append(parent_key)
        full_path_list.extend(path[:marker_index])
        full_path_list.append(value_key)
        full_path_str = ".".join(str(p).strip() for p in full_path_list if str(p).strip())

        cur = obj
        for key in container_path[:-1]:
            cur = cur.setdefault(key, OrderedDict())

        if container_name:
            arr = cur.setdefault(container_name, [])
        else:
            arr = cur.setdefault(marker_label, [])

        entry = OrderedDict()
        entry[key_name] = marker_value

        # ★ 修正: フルパスが退避リストにあれば型キャストをスキップして文字列のままにする
        if full_path_str in self.preserve_string_paths:
            entry[value_key] = str(value)
        else:
            entry[value_key] = self._coerce_json_scalar(str(value))

        arr.append(entry)

    def _ensure_key_value_container(self, obj: dict, path: list) -> None:
        marker_index = next(
            i for i, name in enumerate(path)
            if self._is_key_marker(name)
        )

        container_path = path[:marker_index]
        if not container_path:
            return

        cur = obj
        for key in container_path[:-1]:
            cur = cur.setdefault(key, OrderedDict())

        cur.setdefault(container_path[-1], [])

    def _has_meaningful_value(self, obj: Any) -> bool:
        if isinstance(obj, dict):
            return any(self._has_meaningful_value(v) for v in obj.values())

        if isinstance(obj, list):
            return any(self._has_meaningful_value(v) for v in obj)

        return not is_empty_value(obj)

    def _get_key_value_mapping(self, container_name: str) -> dict:
        mappings = self.key_value_mappings or {}

        return (
            mappings.get(container_name)
            or mappings.get("*")
            or {"key_field": "Key", "value_field": "Value"}
        )

    def _extract_value_key_from_path(self, path: list, marker_index: int) -> str:
        for name in path[marker_index + 1:]:
            name_str = str(name).strip()
            if name_str and not self._is_key_marker(name_str):
                return name_str
        return ""

    def _path_to_string(self, path: list) -> str:
        return ".".join(str(p).strip() for p in path if str(p).strip())

    def _maybe_parse_json_by_path(self, value: Any, path: list) -> Any:
        if not isinstance(value, str):
            return value

        path_str = self._path_to_string(path)
        if path_str not in self.parse_json_child_paths:
            return value

        s = value.strip()

        if not (
            (s.startswith("{") and s.endswith("}"))
            or (s.startswith("[") and s.endswith("]"))
        ):
            return value

        try:
            return json.loads(s)
        except json.JSONDecodeError:
            return value
