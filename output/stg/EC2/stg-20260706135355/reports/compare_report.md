# 検証結果比較レポート: EC2.xlsx

## 1. 実行情報

- **実行開始日時**: 2026-07-06 13:53:55 JST
- **実行終了日時**: 2026-07-06 13:54:00 JST
- **実行時間**: 0:00:05.144973
- **環境**: stg
- **AWS リージョン**: ap-northeast-1
- **AWS アカウントID**: 00XXXXXXXXXX
- **期待値ソース**: [Excel file] EC2.xlsx
---
## 2. 全体サマリ

| シート | AWSサービス | 一致(OK) | 不一致(NG) | 実環境未存在 | 対象外 | 合計 |
|--------|---------------|------|--------|--------------|--------|------|
| EC2 | ec2 | 3 | 1 | 0 | 0 |  4 |
| **合計** | **-** | **3** | **1** | **0** | **0** | **4** |

---

## ◆ シート: EC2
### AWSサービス: ec2

### ステータスサマリ

| 状態 | 件数 |
|------|------|
| 一致(OK) | 3 |
| 不一致(NG) | 1 |
| 実環境未存在 (期待値のみ) | 0 |
| 対象外 (無効行) | 0 |
| **合計** | **4** |

---

### 一致(OK)リソース詳細
#### リソース識別子: XXXSMON0001S
**出典**: EC2.xlsx / EC2 / データ部の第 1 行目

| プロパティ | 期待値 | 実績値 | 判定 |
|------------|--------|--------|------|
| InstanceName | XXXSMON0001S | XXXSMON0001S | ✅ |
| AvailabilityZone | ap-northeast-1a | ap-northeast-1a | ✅ |
| AMI-ID | ami-01b394144003a8283 | ami-01b394144003a8283 | ✅ |
| InstanceType | m7i.large | m7i.large | ✅ |
| KeyName | xxx-stg-ec2-keypair-common | xxx-stg-ec2-keypair-common | ✅ |
| VPCID | vpc-012dda1f0340ffc45 | vpc-012dda1f0340ffc45 | ✅ |
| SubnetID | subnet-067dfb85f74c94f6b | subnet-067dfb85f74c94f6b | ✅ |
| EbsOptimized | True | True | ✅ |
| IamInstanceProfile | `{"Arn":"xxx-stg-iam-profile-mon-ec2-ZabbixServer","Id":"AIPAQDHGKHMKS7BHEA7GL"}` | {'Arn': 'xxx-stg-iam-profile-mon-ec2-ZabbixServer', 'Id': 'AIPAQDHGKHMKS7BHEA7GL'} | ✅ |
| Monitoring | `{"State":"disabled"}` | {'State': 'disabled'} | ✅ |
| PrivateDnsNameOptions | `{"EnableResourceNameDnsAAAARecord":"False","EnableResourceNameDnsARecord":"True","HostnameType":"ip-name"}` | {'HostnameType': 'ip-name', 'EnableResourceNameDnsARecord': True, 'EnableResourceNameDnsAAAARecord': False} | ✅ |
| SourceDestCheck | True | True | ✅ |
| Tags | `[{"Key":"Name","Value":"XXXSMON0001S"},{"Key":"SystemName","Value":"xxx"}]` | `[{"Key":"Name","Value":"XXXSMON0001S"},{"Key":"SystemName","Value":"xxx"}]` | ✅ |

#### リソース識別子: XXXSMON0002S
**出典**: EC2.xlsx / EC2 / データ部の第 2 行目

| プロパティ | 期待値 | 実績値 | 判定 |
|------------|--------|--------|------|
| InstanceName | XXXSMON0002S | XXXSMON0002S | ✅ |
| AvailabilityZone | ap-northeast-1c | ap-northeast-1c | ✅ |
| AMI-ID | ami-01b394144003a8283 | ami-01b394144003a8283 | ✅ |
| InstanceType | m7i.large | m7i.large | ✅ |
| KeyName | xxx-stg-ec2-keypair-common | xxx-stg-ec2-keypair-common | ✅ |
| VPCID | vpc-012dda1f0340ffc45 | vpc-012dda1f0340ffc45 | ✅ |
| SubnetID | subnet-06f2e7a2fd4a848d6 | subnet-06f2e7a2fd4a848d6 | ✅ |
| EbsOptimized | True | True | ✅ |
| IamInstanceProfile | `{"Arn":"xxx-stg-iam-profile-mon-ec2-ZabbixServer","Id":"AIPAQDHGKHMKS7BHEA7GL"}` | {'Arn': 'xxx-stg-iam-profile-mon-ec2-ZabbixServer', 'Id': 'AIPAQDHGKHMKS7BHEA7GL'} | ✅ |
| Monitoring | `{"State":"disabled"}` | {'State': 'disabled'} | ✅ |
| PrivateDnsNameOptions | `{"EnableResourceNameDnsAAAARecord":"False","EnableResourceNameDnsARecord":"True","HostnameType":"ip-name"}` | {'HostnameType': 'ip-name', 'EnableResourceNameDnsARecord': True, 'EnableResourceNameDnsAAAARecord': False} | ✅ |
| SourceDestCheck | True | True | ✅ |
| Tags | `[{"Key":"Name","Value":"XXXSMON0002S"},{"Key":"SystemName","Value":"xxx"}]` | `[{"Key":"Name","Value":"XXXSMON0002S"},{"Key":"SystemName","Value":"xxx"}]` | ✅ |

#### リソース識別子: XXXSLOG0002S
**出典**: EC2.xlsx / EC2 / データ部の第 4 行目

| プロパティ | 期待値 | 実績値 | 判定 |
|------------|--------|--------|------|
| InstanceName | XXXSLOG0002S | XXXSLOG0002S | ✅ |
| AvailabilityZone | ap-northeast-1c | ap-northeast-1c | ✅ |
| AMI-ID | ami-01b394144003a8283 | ami-01b394144003a8283 | ✅ |
| InstanceType | m7i.large | m7i.large | ✅ |
| KeyName | xxx-stg-ec2-keypair-common | xxx-stg-ec2-keypair-common | ✅ |
| VPCID | vpc-012dda1f0340ffc45 | vpc-012dda1f0340ffc45 | ✅ |
| SubnetID | subnet-06f2e7a2fd4a848d6 | subnet-06f2e7a2fd4a848d6 | ✅ |
| EbsOptimized | True | True | ✅ |
| IamInstanceProfile | `{"Arn":"xxx-stg-iam-profile-mon-ec2-SyslogServer","Id":"AIPAQDHGKHMKVMRYKJW4Q"}` | {'Arn': 'xxx-stg-iam-profile-mon-ec2-SyslogServer', 'Id': 'AIPAQDHGKHMKVMRYKJW4Q'} | ✅ |
| Monitoring | `{"State":"disabled"}` | {'State': 'disabled'} | ✅ |
| PrivateDnsNameOptions | `{"EnableResourceNameDnsAAAARecord":"False","EnableResourceNameDnsARecord":"True","HostnameType":"ip-name"}` | {'HostnameType': 'ip-name', 'EnableResourceNameDnsARecord': True, 'EnableResourceNameDnsAAAARecord': False} | ✅ |
| SourceDestCheck | True | True | ✅ |
| Tags | `[{"Key":"Name","Value":"XXXSLOG0002S"},{"Key":"SystemName","Value":"xxx"}]` | `[{"Key":"Name","Value":"XXXSLOG0002S"},{"Key":"SystemName","Value":"xxx"}]` | ✅ |


---

### 不一致(NG)リソース詳細
#### リソース識別子: XXXSLOG0001S
**出典**: EC2.xlsx / EC2 / データ部の第 3 行目

| プロパティ | 期待値 | 実績値 | 判定 |
|------------|--------|--------|------|
| InstanceName | XXXSLOG0001S | XXXSLOG0001S | ✅ |
| AvailabilityZone | ap-northeast-1a | ap-northeast-1a | ✅ |
| AMI-ID | ami-01b394144003a8283 | ami-01b394144003a8283 | ✅ |
| InstanceType | m6i.8xlarge | m7i.large | ❌ |
| KeyName | xxx-stg-ec2-keypair-common | xxx-stg-ec2-keypair-common | ✅ |
| VPCID | vpc-012dda1f0340ffc45 | vpc-012dda1f0340ffc45 | ✅ |
| SubnetID | subnet-067dfb85f74c94f6b | subnet-067dfb85f74c94f6b | ✅ |
| EbsOptimized | True | True | ✅ |
| IamInstanceProfile | `{"Arn":"xxx-stg-iam-profile-mon-ec2-SyslogServer","Id":"AIPAQDHGKHMKVMRYKJW4Q"}` | {'Arn': 'xxx-stg-iam-profile-mon-ec2-SyslogServer', 'Id': 'AIPAQDHGKHMKVMRYKJW4Q'} | ✅ |
| Monitoring | `{"State":"disabled"}` | {'State': 'disabled'} | ✅ |
| PrivateDnsNameOptions | `{"EnableResourceNameDnsAAAARecord":"False","EnableResourceNameDnsARecord":"True","HostnameType":"ip-name"}` | {'HostnameType': 'ip-name', 'EnableResourceNameDnsARecord': True, 'EnableResourceNameDnsAAAARecord': False} | ✅ |
| SourceDestCheck | True | True | ✅ |
| Tags | `[{"Key":"Name","Value":"XXXSLOG0001S"},{"Key":"SystemName","Value":"xxx"}]` | `[{"Key":"Name","Value":"XXXSLOG0001S"},{"Key":"SystemName","Value":"xxx"}]` | ✅ |


---

### 実環境未存在リソース一覧
*実環境未存在リソースはありませんでした*

---

### 対象外リソース（無効行）一覧
*対象外（無効行）リソースはありませんでした*

---

*レポート生成日時: 2026-07-06 13:54:00 JST*
