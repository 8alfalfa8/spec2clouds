# src/normalizer/expected_normalizer.py
"""
期待値データセットを生成するモジュール
ExpectedNormalizerクラスを提供
"""
import logging
from typing import List, Dict, Any

from ..utils.string_utils import normalize_bool_value
from ..models.resource import NormalizedResource

logger = logging.getLogger(__name__)

class ExpectedNormalizer:
    """期待値データセットを生成"""

    # テンプレートID → リソースタイプ マッピング
    TEMPLATE_TYPE_MAP = {
        "EC2": "ec2",
    }

    # リソースタイプ毎の識別子フィールド名
    ID_FIELD_MAP = {
        "ec2": "InstanceName",
    }

    # 各リソースタイプで比較対象とするプロパティのキーセット（Excel側）
    COMPARISON_KEYS_MAP = {
        "ec2": [
            "InstanceName",
            "AvailabilityZone",
            "AMI-ID",
            "InstanceType",
            "KeyName",
            "VPCID",
            "SubnetID",
            "EbsOptimized",
            "IamInstanceProfile",
            "Monitoring",
            "PrivateDnsNameOptions",
            "SourceDestCheck",
            "Tags",
        ],
    }

    def normalize(self, raw_data: List[Dict[str, Any]], template_id: str) -> List[NormalizedResource]:
        resource_type = self.get_resource_type(template_id)
        results = []
        for idx, row in enumerate(raw_data):
            if row.get("_template_id") != template_id:
                continue
            resource = self._normalize_single(row, resource_type)
            if resource:
                results.append(resource)
        return results

    def _normalize_single(self, record: Dict[str, Any], resource_type: str) -> NormalizedResource:
        # テンプレートベースの JSON 構造に対応: data と source を分離
        data = record.get("data", {})
        source = record.get("source", {})

        # 識別子の探索
        id_field = self.ID_FIELD_MAP.get(resource_type)
        identifier = self._find_value_in_dict(data, id_field)

        # フォールバック: Name が見つからない場合は他のキーを試みる
        if not identifier:
            fallback_keys = ["Name", "InstanceId", "DBInstanceIdentifier", "BucketName"]
            for key in fallback_keys:
                identifier = self._find_value_in_dict(data, key)
                if identifier:
                    break

        if not identifier:
            # 最終フォールバック: 行番号を使うが、メタ情報に警告を残す
            row_idx = source.get("row_index", "?")
            identifier = f"unknown-{row_idx}"
            id_status = "MISSING"
        else:
            id_status = "OK"

        # ★ プロパティのキー一覧を取得（テンプレート順を保証）
        #prop_keys = self.COMPARISON_KEYS_MAP.get(resource_type)
        #if not prop_keys:
        # data の全キーをテンプレート定義順に使う
        prop_keys = list(data.keys())

        properties = {}
        for key in prop_keys:
            val = self._find_value_in_dict(data, key)
            if val is not None:
                val = normalize_bool_value(val)
                properties[key] = val

        # メタ情報
        meta = {
            '_source_file': record.get('_source_file') or source.get("file", ""),
            '_source_sheet': record.get('_source_sheet') or source.get("sheet", ""),
            '_source_row': record.get('_row_index') or source.get("row_index", ""),
            '_identifier_status': id_status,
            '_enabled': record.get('enabled', True)
        }

        return NormalizedResource(
            resource_type=resource_type,
            identifier=str(identifier),
            properties=properties,
            meta=meta
        )

    @staticmethod
    def _find_value_in_dict(data: Dict[str, Any], target_key: str, fallback_key: str = None) -> Any:
        """data 辞書内で柔軟にキーを検索して値を返す"""
        # 1. 完全一致
        if target_key in data:
            return data[target_key]
        # 2. 大文字小文字を無視
        for k in data:
            if k.lower() == target_key.lower():
                return data[k]
        # 3. 部分一致 (例: "InstanceId_0" → "InstanceId")
        for k in data:
            if target_key.lower() in k.lower():
                return data[k]
        # 4. fallback_key を試す
        if fallback_key:
            if fallback_key in data:
                return data[fallback_key]
            for k in data:
                if fallback_key.lower() in k.lower():
                    return data[k]
        return None

    # テンプレートIDからリソースタイプを推測するロジック
    @staticmethod
    def get_resource_type(template_id: str) -> str:
        """
        テンプレートIDをリソースタイプ文字列に変換する。
        完全一致を優先し、なければ部分一致（大文字小文字無視）を試みる。
        """
        if not template_id:
            return "unknown"
        # 1. 完全一致
        if template_id in ExpectedNormalizer.TEMPLATE_TYPE_MAP:
            return ExpectedNormalizer.TEMPLATE_TYPE_MAP[template_id]
        # 2. 部分一致
        tid_lower = template_id.lower()
        if 'ec2' in tid_lower:
            return 'ec2'
        return 'unknown'
