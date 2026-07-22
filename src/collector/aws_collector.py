# src/collector/aws_collector.py
"""
AWSから実績リソースを収集するモジュール
AwsCollectorクラスを提供
"""
import os
import boto3
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class AwsCollector:
    """AWSから実績リソースを収集"""

    def __init__(self, region_name: str = "ap-northeast-1", profile_name: str = None):
        session_kwargs = {"region_name": region_name}
        if profile_name:
            session_kwargs["profile_name"] = profile_name
        self.session = boto3.Session(**session_kwargs)

    def collect(self, resource_type: str) -> List[Dict[str, Any]]:
        collector_map = {
            "ec2": self._collect_ec2_instances,
        }
        collector = collector_map.get(resource_type.lower())
        if not collector:
            raise NotImplementedError(f"Collector for {resource_type} not implemented")
        return collector()

    def _collect_ec2_instances(self) -> List[Dict[str, Any]]:
        ec2 = self.session.client("ec2")
        paginator = ec2.get_paginator("describe_instances")
        instances = []

        for page in paginator.paginate():
            for reservation in page["Reservations"]:
                for inst in reservation["Instances"]:
                    # --- Nameタグの値を抽出してキーとして追加 ---
                    # タグが1つもない場合や、Nameタグがない場合は None または 空文字 になります
                    name_tag_value = None
                    if "Tags" in inst:
                        for tag in inst["Tags"]:
                            if tag["Key"] == "Name":
                                name_tag_value = tag["Value"]
                                break

                    # インスタンスの情報（辞書）に 'Name' キーを追加
                    inst["InstanceName"] = name_tag_value
                    # ------------------------------------------

                    logger.debug(f"EC2 instances=============== {inst}")
                    instances.append(inst)

        logger.info(f"Collected {len(instances)} EC2 instances")
        return instances
