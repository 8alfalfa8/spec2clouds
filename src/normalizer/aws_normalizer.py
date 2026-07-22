# src/normalizer/aws_normalizer.py
"""
AWSから収集したリソースを比較用の正規化リソースに変換するモジュール
AwsNormalizerクラスを提供
"""
import json
import logging
from typing import List, Dict, Any

from ..utils.string_utils import normalize_bool_value
from ..models.resource import NormalizedResource

logger = logging.getLogger(__name__)

class AwsNormalizer:

    def normalize(self, raw_resources: List[Dict[str, Any]], resource_type: str) -> List[NormalizedResource]:
        normalizer_map = {
            "ec2": self._normalize_ec2,
        }
        normalizer = normalizer_map.get(resource_type.lower())
        if not normalizer:
            raise NotImplementedError(f"Normalizer for {resource_type} not implemented")
        return normalizer(raw_resources)

    def _normalize_ec2(self, instances: List[Dict]) -> List[NormalizedResource]:
        result = []
        for inst in instances:
            instance_name = inst.get("InstanceName", "")
            logger.debug(f"ec2_name=================={instance_name}")
            instance_id = inst.get("InstanceId", "")
            if not instance_id:
                continue

            # プロパティ抽出
            #name = ""
            #for tag in inst.get("Tags", []):
            #    if tag["Key"] == "Name":
            #        name = tag["Value"]
            #        break

            # タグ情報のフラット化
            tags = inst.get("Tags", [])
            tag_keys = ["severity", "Severity", "Name", "SystemName"]
            tags = [tag for tag in tags if tag.get("Key") in tag_keys]
            # キーでソート（比較の順序依存を排除）
            tags_sorted = sorted(tags, key=lambda t: t.get("Key", ""))
            tags_str = json.dumps(tags_sorted, ensure_ascii=False, separators=(',', ':'))

            properties = {
                "InstanceName": instance_name,
                "AvailabilityZone": inst.get("Placement", {}).get("AvailabilityZone", ""),
                "AMI-ID": inst.get("ImageId", ""),
                "InstanceType": inst.get("InstanceType", ""),
                "KeyName": inst.get("KeyName", ""),
                "VPCID": inst.get("VpcId", ""),
                "SubnetID": inst.get("SubnetId", ""),
                "EbsOptimized": inst.get("EbsOptimized", ""),
                "IamInstanceProfile": inst.get("IamInstanceProfile", {}),
                "Monitoring": inst.get("Monitoring", []),
                "PrivateDnsNameOptions": inst.get("PrivateDnsNameOptions", {}),
                "SourceDestCheck":inst.get("SourceDestCheck", ""),
                "Tags": tags_str
            }
            # 注意: Excel側の期待値フォーマットに合わせて調整が必要です。
            # Excel テンプレートEC2では PrivateIP は "10.192.0.53, 10.192.0.144" のように複数IPが含まれています。
            # AWSからも同様の文字列に整形します。

            resource = NormalizedResource(
                resource_type="ec2",
                identifier=instance_name,
                properties=properties,
                #meta={"Name": instance_name}
                meta={}
            )
            result.append(resource)

        logger.info(f"Normalized {len(result)} EC2 instances")
        return result
