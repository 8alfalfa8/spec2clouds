# src/comparator/comparator.py
"""
比較モジュール
期待値と実測値のリストを比較し、差分を抽出する
Comparatorクラスを提供
"""

import ast
import json
import logging
from typing import List, Dict, Any, Optional

from ..utils.string_utils import normalize_bool_value, normalize_json_string
from ..models.resource import NormalizedResource

logger = logging.getLogger(__name__)

class Comparator:
    def compare(self,
                expected: List[NormalizedResource],
                actual: List[NormalizedResource],
                allowed_keys: Optional[List[str]] = None,
                invalid_exp: Optional[List[str]] = None,
                ) -> Dict[str, Any]:
        """
        比較実行
        """

        # 許可キーが指定されていれば、両方のプロパティを制限
        if allowed_keys is not None:
            for exp in expected:
                exp.properties = {k: v for k, v in exp.properties.items() if k in allowed_keys}
            for act in actual:
                act.properties = {k: v for k, v in act.properties.items() if k in allowed_keys}

        exp_map = {r.identifier: r for r in expected}
        act_map = {r.identifier: r for r in actual}

        exp_ids = set(exp_map.keys())
        act_ids = set(act_map.keys())

        missing_ids = exp_ids - act_ids
        extra_ids = act_ids - exp_ids
        common_ids = exp_ids & act_ids

        missing = [exp_map[i] for i in missing_ids]
        extra = [act_map[i] for i in extra_ids]

        modified = []
        matched = []
        for i in common_ids:
            exp = exp_map[i]
            act = act_map[i]
            diffs = self._diff_properties(exp.properties, act.properties)
            if diffs:
                modified.append({
                    "identifier": i,
                    "resource_type": exp.resource_type,
                    "differences": diffs,
                    "expected_props": exp.properties,
                    "actual_props": act.properties,
                    "meta": exp.meta
                })
            else:
                # matched.append(exp)
                matched.append({
                    "identifier": i,
                    "resource_type": exp.resource_type,
                    "expected_props": exp.properties,
                    "actual_props": act.properties,
                    "meta": exp.meta
                })

        summary = {
            "expected_count": len(expected),
            "actual_count": len(actual),
        }

        logger.info(f"Comparison: {len(invalid_exp)} invalid, {len(missing)} missing, {len(extra)} extra, {len(modified)} modified, {len(matched)} matched")
        return {
            "missing": missing,
            "extra": extra,
            "modified": modified,
            "matched": matched,
            "summary": summary,
        }

    def _diff_properties(self, expected: Dict, actual: Dict) -> List[Dict]:
        diffs = []
        all_keys = set(expected.keys()) | set(actual.keys())
        for key in sorted(all_keys):
            exp_val = expected.get(key)
            act_val = actual.get(key)

            exp_val = normalize_bool_value(exp_val)
            act_val = normalize_bool_value(act_val)

            # 両方が文字列の場合、JSONとして正規化して比較を試みる
            if isinstance(exp_val, str) and isinstance(act_val, str):
                norm_exp = normalize_json_string(exp_val)
                norm_act = normalize_json_string(act_val)
                # JSONっぽい文字列かどうかを簡単に判定 ({ [ で始まる)
                if (exp_val.strip().startswith('{') or exp_val.strip().startswith('[')) or \
                (act_val.strip().startswith('{') or act_val.strip().startswith('[')):
                    try:

                        if norm_exp != norm_act:
                            diffs.append({
                                "key": key,
                                "expected": exp_val,
                                "actual": act_val
                            })
                        continue
                    except Exception:
                        pass  # パースエラーなら通常比較にフォールバック

            # 通常の文字列比較
            # 正準化した文字列を取得（型にかかわらずJSON形式の文字列に統一）
            canon_exp = self._canonicalize(exp_val)
            canon_act = self._canonicalize(act_val)
            if canon_exp != canon_act:
                diffs.append({
                    "key": key,
                    "expected": exp_val,
                    "actual": act_val
                })
        return diffs

    @staticmethod
    def _canonicalize(value) -> str:
        """あらゆる型の値を正準化したJSON文字列に変換"""
        if isinstance(value, (dict, list)):
            # オブジェクト内のすべての真偽値を文字列 "True"/"False" に統一
            normalized_obj = Comparator._recursive_normalize_bool(value)
            return json.dumps(normalized_obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        else:
            s = str(value)
            obj = None
            try:
                obj = json.loads(s)
            except (json.JSONDecodeError, ValueError):
                pass
            if obj is None:
                try:
                    obj = ast.literal_eval(s)
                except (ValueError, SyntaxError):
                    pass
            if obj is not None and isinstance(obj, (dict, list)):
                normalized_obj = Comparator._recursive_normalize_bool(obj)
                return json.dumps(normalized_obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
            else:
                # 構造化データでなければ normalize_bool_value だけ適用（例: "True" → "True"）
                return normalize_bool_value(s)

    @staticmethod
    def _recursive_normalize_bool(obj):
        """辞書・リストの末端まで再帰し、normalize_bool_value を適用"""
        if isinstance(obj, dict):
            return {k: Comparator._recursive_normalize_bool(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [Comparator._recursive_normalize_bool(item) for item in obj]
        else:
            # 末端の値（文字列・数値・真偽値など）に normalize_bool_value を適用
            return normalize_bool_value(obj)

    def generate_report(self, result: Dict) -> str:
        """テキストレポート生成"""
        lines = []
        lines.append("=" * 60)
        lines.append(" COMPARISON REPORT")
        lines.append("=" * 60)
        lines.append(f"Missing resources: {len(result['missing'])}")
        for r in result['missing']:
            lines.append(f"  - {r.resource_type}/{r.identifier}")
        lines.append(f"Extra resources: {len(result['extra'])}")
        for r in result['extra']:
            lines.append(f"  - {r.resource_type}/{r.identifier}")
        lines.append(f"Modified resources: {len(result['modified'])}")
        for mod in result['modified']:
            lines.append(f"  - {mod['identifier']}:")
            for diff in mod['differences']:
                lines.append(f"      {diff['key']}: expected={diff['expected']}, actual={diff['actual']}")
        lines.append(f"Matched resources: {len(result['matched'])}")
        lines.append("=" * 60)
        return "\n".join(lines)
