# src/models/resource.py
"""
比較用の正規化リソースモデルを定義するモジュール
NormalizedResourceクラスを提供
"""
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class NormalizedResource:
    """比較用の正規化リソース"""
    resource_type: str
    identifier: str                 # 一意に識別するID（例: InstanceId）
    properties: Dict[str, Any] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)  # 比較しないメタ情報

    def __eq__(self, other):
        if not isinstance(other, NormalizedResource):
            return False
        return (self.resource_type == other.resource_type and
                self.identifier == other.identifier and
                self.properties == other.properties)

    def __hash__(self):
        return hash((self.resource_type, self.identifier))
