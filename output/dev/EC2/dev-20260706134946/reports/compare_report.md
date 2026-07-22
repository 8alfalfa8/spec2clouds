# 検証結果比較レポート: EC2.xlsx

## 1. 実行情報

- **実行開始日時**: 2026-07-06 13:49:46 JST
- **実行終了日時**: 2026-07-06 13:49:50 JST
- **実行時間**: 0:00:04.122161
- **環境**: dev
- **AWS リージョン**: ap-northeast-1
- **AWS アカウントID**: 178875779790
- **期待値ソース**: [Excel file] EC2.xlsx
---
## 2. 全体サマリ

| シート | AWSサービス | 一致(OK) | 不一致(NG) | 実環境未存在 | 対象外 | 合計 |
|--------|---------------|------|--------|--------------|--------|------|
| EC2 | ec2 | 1 | 1 | 0 | 2 |  4 |
| **合計** | **-** | **1** | **1** | **0** | **2** | **4** |

---

## ◆ シート: EC2
### AWSサービス: ec2

### ステータスサマリ

| 状態 | 件数 |
|------|------|
| 一致(OK) | 1 |
| 不一致(NG) | 1 |
| 実環境未存在 (期待値のみ) | 0 |
| 対象外 (無効行) | 2 |
| **合計** | **4** |

---

### 一致(OK)リソース詳細
#### リソース識別子: XXXSMON0001D
**出典**: EC2.xlsx / EC2 / データ部の第 1 行目

| プロパティ | 期待値 | 実績値 | 判定 |
|------------|--------|--------|------|
| InstanceName | XXXSMON0001D | XXXSMON0001D | ✅ |
| AvailabilityZone | ap-northeast-1a | ap-northeast-1a | ✅ |
| AMI-ID | ami-01b394144003a8283 | ami-01b394144003a8283 | ✅ |
| InstanceType | m7i.large | m7i.large | ✅ |
| KeyName | xxx-dev-ec2-keypair-common | xxx-dev-ec2-keypair-common | ✅ |
| VPCID | vpc-0ff05646be472c04a | vpc-0ff05646be472c04a | ✅ |
| SubnetID | subnet-036514ef60896f53c | subnet-036514ef60896f53c | ✅ |
| EbsOptimized | True | True | ✅ |
| IamInstanceProfile | `{"Arn":"xxx-dev-iam-profile-mon-ec2-ZabbixServer","Id":"AIPASTJOTZLHIELUPDZ65"}` | {'Arn': 'xxx-dev-iam-profile-mon-ec2-ZabbixServer', 'Id': 'AIPASTJOTZLHIELUPDZ65'} | ✅ |
| Monitoring | `{"State":"disabled"}` | {'State': 'disabled'} | ✅ |
| PrivateDnsNameOptions | `{"EnableResourceNameDnsAAAARecord":"False","EnableResourceNameDnsARecord":"True","HostnameType":"ip-name"}` | {'HostnameType': 'ip-name', 'EnableResourceNameDnsARecord': True, 'EnableResourceNameDnsAAAARecord': False} | ✅ |
| SourceDestCheck | True | True | ✅ |
| Tags | `[{"Key":"Name","Value":"XXXSMON0001D"},{"Key":"SystemName","Value":"xxx"}]` | `[{"Key":"Name","Value":"XXXSMON0001D"},{"Key":"SystemName","Value":"xxx"}]` | ✅ |


---

### 不一致(NG)リソース詳細
#### リソース識別子: XXXSLOG0001D
**出典**: EC2.xlsx / EC2 / データ部の第 3 行目

| プロパティ | 期待値 | 実績値 | 判定 |
|------------|--------|--------|------|
| InstanceName | XXXSLOG0001D | XXXSLOG0001D | ✅ |
| AvailabilityZone | ap-northeast-1a | ap-northeast-1a | ✅ |
| AMI-ID | ami-01b394144003a8283 | ami-01b394144003a8283 | ✅ |
| InstanceType | m6i.8xlarge | m7i.large | ❌ |
| KeyName | xxx-dev-ec2-keypair-common | xxx-dev-ec2-keypair-common | ✅ |
| VPCID | vpc-0ff05646be472c04a | vpc-0ff05646be472c04a | ✅ |
| SubnetID | subnet-036514ef60896f53c | subnet-036514ef60896f53c | ✅ |
| EbsOptimized | True | True | ✅ |
| IamInstanceProfile | `{"Arn":"xxx-dev-iam-profile-mon-ec2-SyslogServer","Id":"AIPASTJOTZLHKUTSJOQVZ"}` | {'Arn': 'xxx-dev-iam-profile-mon-ec2-SyslogServer', 'Id': 'AIPASTJOTZLHKUTSJOQVZ'} | ✅ |
| Monitoring | `{"State":"disabled"}` | {'State': 'disabled'} | ✅ |
| PrivateDnsNameOptions | `{"EnableResourceNameDnsAAAARecord":"False","EnableResourceNameDnsARecord":"True","HostnameType":"ip-name"}` | {'HostnameType': 'ip-name', 'EnableResourceNameDnsARecord': True, 'EnableResourceNameDnsAAAARecord': False} | ✅ |
| SourceDestCheck | True | True | ✅ |
| Tags | `[{"Key":"Name","Value":"XXXSLOG0001D"},{"Key":"SystemName","Value":"xxx"}]` | `[{"Key":"Name","Value":"XXXSLOG0001D"},{"Key":"SystemName","Value":"xxx"}]` | ✅ |


---

### 実環境未存在リソース一覧
*実環境未存在リソースはありませんでした*

---

### 対象外リソース（無効行）一覧
| 識別子 | 出典 |
|--------|------|
| XXXSMON0002D | EC2.xlsx / EC2 / データ部の第 2 行目 |
| XXXSLOG0002D | EC2.xlsx / EC2 / データ部の第 4 行目 |

---

*レポート生成日時: 2026-07-06 13:49:50 JST*