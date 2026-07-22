# 🛠️ spec2clouds

<!-- PROFILE_BADGE_START -->

[![GitHub](https://img.shields.io/badge/GitHub-Profile-181717?logo=github)](https://github.com/8alfalfa8)
[![Qiita](https://img.shields.io/badge/Qiita-Profile-55C500?logo=qiita&logoColor=white)](https://qiita.com/8alfalfa8)
[![Zenn](https://img.shields.io/badge/Zenn-Profile-3EA8FF?logo=zenn&logoColor=white)](https://zenn.dev/8alfalfa8)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/8alfalfa8)

<!-- PROFILE_BADGE_END -->

Excel パラメータシートから AWS リソースのテストデータ (JSON) を生成し、さらに AWS 実環境のリソースと比較するツールです。
テンプレート駆動で柔軟なデータ変換が可能で、比較結果は Markdown / HTML レポートとして出力できます。

---

## ✅ 主な機能

## 機能

- **Excel → JSON 変換**
  - ヘッダー多階層の自動解析
  - 列制御 (有効列の指定) とデータ行の有効(対象)/無効（対象外）判定
  - 環境トークン `{prd|reh|stg|dev}` / `{P|R|S|D}` の自動置換
  - テンプレート自動生成と手動カスタマイズの両対応
- **期待値 vs AWS 実績の比較**
  - AWSサービス（EC2、CloudWatch、EventBridgeなど）の比較に対応 (無料版EC2のみ)
  - 一致／不一致／不足／過剰リソースの検出
  - 比較レポートを Markdown と HTML（商用版） で同時出力
- **カスタム文字列置換**
  - 外部の置換ルールファイル (テンプレート別) による柔軟な置換
  - 置換条件 (完全一致 / 部分一致) を指定可能
  - 置換後の文字列に動的変数 (`{aws_account_id}` など) を埋め込み可能（商用版）
- **レポート出力**
  - JSON プロパティを 1 行圧縮＆インラインコード化し、テーブル崩れを防止
  - 国際化サポートに準拠したレポート言語の指定機能（商用版）
- **バッチ処理サポート（商用版）**
  - バッチ処理からの実行をサポートするため、終了コードを返却する。
  - 「不一致（NG）」件数および「実環境未存在」件数がともに0件の場合、終了コード0（正常終了）を返却する。
  - 上記以外の場合、終了コード1（異常終了）を返却する。

---
## プロジェクト構成
<!-- START_TREE -->
├── [LICENSE](LICENSE)  
├── [README.ja.md](README.ja.md)  
├── [README.md](README.md)  
├── config/  
│&nbsp;&nbsp;&nbsp;├── [replace.yaml](config/replace.yaml)  
│&nbsp;&nbsp;&nbsp;├── [settings.yaml](config/settings.yaml)  
│&nbsp;&nbsp;&nbsp;└── stg/  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── [replace_ec2.yaml](config/stg/replace_ec2.yaml)  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── [settings-ec2.yaml](config/stg/settings-ec2.yaml)  
├── input/  
│&nbsp;&nbsp;&nbsp;└── ec2/  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── [EC2.xlsx](input/ec2/EC2.xlsx)  
├── output/  
│&nbsp;&nbsp;&nbsp;├── dev/  
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└── EC2/  
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── dev-20260706134946/  
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── json/  
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [result_EC2.json](output/dev/EC2/dev-20260706134946/json/result_EC2.json)  
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└── [result_all.json](output/dev/EC2/dev-20260706134946/json/result_all.json)  
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── reports/  
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── [compare_report.md](output/dev/EC2/dev-20260706134946/reports/compare_report.md)  
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── [compare_summary.json](output/dev/EC2/dev-20260706134946/reports/compare_summary.json)  
│&nbsp;&nbsp;&nbsp;└── stg/  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── EC2/  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── stg-20260706135355/  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── json/  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [result_EC2.json](output/stg/EC2/stg-20260706135355/json/result_EC2.json)  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└── [result_all.json](output/stg/EC2/stg-20260706135355/json/result_all.json)  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── reports/  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── [compare_report.md](output/stg/EC2/stg-20260706135355/reports/compare_report.md)  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── [compare_summary.json](output/stg/EC2/stg-20260706135355/reports/compare_summary.json)  
├── [requirements.txt](requirements.txt)  
└── src/  
&nbsp;&nbsp;&nbsp;&nbsp;├── [cli.py](src/cli.py)  
&nbsp;&nbsp;&nbsp;&nbsp;├── collector/  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [__init__.py](src/collector/__init__.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└── [aws_collector.py](src/collector/aws_collector.py)  
&nbsp;&nbsp;&nbsp;&nbsp;├── comparator/  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [__init__.py](src/comparator/__init__.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [comparator.py](src/comparator/comparator.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└── [report_generator.py](src/comparator/report_generator.py)  
&nbsp;&nbsp;&nbsp;&nbsp;├── core/  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [__init__.py](src/core/__init__.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [config_validator.py](src/core/config_validator.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [data_processor.py](src/core/data_processor.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [excel_reader.py](src/core/excel_reader.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└── [header_processor.py](src/core/header_processor.py)  
&nbsp;&nbsp;&nbsp;&nbsp;├── [init.py](src/init.py)  
&nbsp;&nbsp;&nbsp;&nbsp;├── [main.py](src/main.py)  
&nbsp;&nbsp;&nbsp;&nbsp;├── models/  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [resource.py](src/models/resource.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└── [sheet_context.py](src/models/sheet_context.py)  
&nbsp;&nbsp;&nbsp;&nbsp;├── normalizer/  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [__init__.py](src/normalizer/__init__.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [aws_normalizer.py](src/normalizer/aws_normalizer.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└── [expected_normalizer.py](src/normalizer/expected_normalizer.py)  
&nbsp;&nbsp;&nbsp;&nbsp;├── output/  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [__init__.py](src/output/__init__.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [json_generator.py](src/output/json_generator.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [template_builder.py](src/output/template_builder.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└── [template_engine.py](src/output/template_engine.py)  
&nbsp;&nbsp;&nbsp;&nbsp;└── utils/  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── [__init__.py](src/utils/__init__.py)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── [excel_utils.py](src/utils/excel_utils.py)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── [string_utils.py](src/utils/string_utils.py)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── [validation.py](src/utils/validation.py)  

23 directories, 43 files  
<!-- END_TREE -->

---

## 動作要件

- Python 3.9+
- 推奨: Python 3.11 以上

依存ライブラリ:

- pandas
- pyyaml
- boto3

## インストール

```bash
# 1. リポジトリをクローン
git clone <repository-url>
cd spec2clouds

# 2. 依存パッケージをインストール
pip install -r requirements.txt

```

---

## 📙 使用方法

### 1. 設定ファイルの準備

`config/stg/settings-ec2.yaml` を編集して、Excelファイルのパスや解析条件を設定します。

```yaml
# config\stg\settings-ec2.yaml
# ============================================================
# spec2clouds stg設定ファイル
# ============================================================

# --- 環境指定 ---
env: "stg"                         # {prd|reh|stg|dev} または、{P|R|S|D}対応

# --- 入出力設定 ---
input:
  directory: "input/ec2"           # 入力Excelファイルのフォルダ
  file_pattern: "*.xlsx"           # 処理対象ファイルパターン

output:
  directory: "output/stg/ec2"      # 出力フォルダ
  file_prefix: "result"            # 出力ファイル接頭辞
  combine_all: true                # 全ファイル統合JSONを出力するか

# --- テンプレート設定 ---
template:
  auto_generate: true              # テンプレート自動生成を有効にするか
  auto_generate_only: false        # 自動生成のみ行い、通常処理はスキップするか
  id_cell: "C5"                    # テンプレートIDが記載されたセル
  directory: "templates/ec2"       # テンプレートファイルのフォルダ
  mapping:                         # AWSサービスID → テンプレートファイル名
    "EC2": "EC2.json"

# --- 正規化設定 ---
normalize:
  unicode_form: ""                 # デフォルト NFKC (NFC/NFKC/NFD/NFKD)
  regex_escape: false              # デフォルト true

# --- 検証対象シート設定 ---
target_sheets:
  - "EC2"

# --- ヘッダー設定 ---
header:
  start_row: 7                     # ヘッダー開始行（1始まり）
  max_levels: 3                    # ヘッダーの最大階層数
  start_string: ""                 # 開始列の文字列（空=非空セル）
  end_string: "Remarks"            # 終了列の文字列（空=空セル）
  fill_empty_cells: true           # 空セルを上位/前方から補完

# --- データ設定 ---
data:
  data_start_row: 11               # データ開始行（1始まり、空=ヘッダー終了行+1）
  end_row_string: "Remarks"        # データ終了の先頭セル文字列（空=空セル）
  termination:
    empty_row_threshold: 2         # データ終了とみなす連続空行数

  # --- 列制御設定 ---
  column_control:
    row: 6                         # 制御行（1始まり、0=無効）
    exclude_value: "0"             # 除外を示す値

  # --- データ行制御設定 ---
  invalid_row_control:
    column: "DO"                   # 判定列
    invalid_value: "0"             # この値なら無効
    output_field: "enabled"        # 無効行の判定結果を出力するフィールド名
    valid_output: true             # 有効行の判定値
    invalid_output: false          # 無効行の判定値
    skip_invalid_rows: false       # 無効行を出力からスキップするか

# --- 比較設定 ---
compare:
  enabled: true                    # 比較を実行するか
  show_extra_resources: false      # true なら第6章表示、false なら非表示
  timezone: "Asia/Tokyo"           # デフォルト：東京
  aws:
    region: "ap-northeast-1"
    profile: XXX-Stg               # AWSプロファイル名（nullならデフォルト）
  resources:                       # 比較対象のAWSサービスIDリスト
    - "EC2"

# --- 置換ルール設定 ---
replace_rules:
  mapping:
    "EC2": "replace_ec2.yaml"

# --- json：Key-Value マッピング設定 ---
json:
  key_value_mappings:
    Dimensions:
      key_field: Name
      value_field: Value
    Metrics:
      key_field: Name
      value_field: Value
    Tags:
      key_field: Key
      value_field: Value
    "*":
      key_field: Key
      value_field: Value

  # 数字データは文字列として処理する項目のパスを指定
  preserve_string_paths:
    - Metrics.AccountId

```
### 2. Excelファイル配置

`input/ec2/` フォルダに処理したい.xlsxファイルを配置します。

#### Excelフォーマット要件

##### サービス識別

- 各シートの `C5`（設定変更可`template:id_cell`）に サービスID を記載

例:

```text
C5 = EC2
```

##### 列制御行

- `data:column_control:row` で指定した行に以下を記載

| 値 | 意味 |
|----|------|
| 1  | 出力対象 |
| 0  | 除外 |

##### 無効行制御

- `data:invalid_row_control:column`指定列の値で行を有効/無効判定可能

---

### 3. テンプレートのカスタマイズ

- 初回実行時、`auto_generate: true` により `templates/` にテンプレートが自動生成されます。
- 生成されたテンプレートは手動で編集可能です。
  例 (`EC2.json`):
  ```json
  {
    "source": {
      "file": "{{$file}}",
      "sheet": "{{$sheet}}",
      "row_index": "{{$index}}",
      "env": "{{$env}}"
    },
    "data": {
      "InstanceId": "{{InstanceId}}",
      "Name": "{{Name}}",
      "InstanceType": "{{InstanceType}}"
    }
  }
  ```
- 変数は `{{列名}}` で参照し、Excel の該当列の値が埋め込まれます。
- 特殊変数: `{{$index}}` (行番号), `{{$file}}` (ファイル名), `{{$sheet}}` (シート名), `{{$env}}` (環境)

### 4. 置換ルール

テンプレート毎に YAML ファイルで置換ルールを定義できます。
ファイルは `config/` に配置し、`settings.yaml` の `replace_rules.mapping` で関連付けます。

**書式 (`config/stg/replace_ec2.yaml` の例)**:
```yaml
# config\stg\replace-ec2.yaml
# EC2用の置換ルール
# 置換ルールと処理の関連付け設定：
#    config\settings-ec2.yaml
#      replace_rules:
#            mapping:
# 設定説明：
#   - source:置換前の文字列
#     condition: partial         (partial: 部分置換 / exact: 一致置換)
#     replacement: 置換後の文字列
#

# 不要な「ブランク」文字列を削除
- source: "ブランク"
  condition: exact
  replacement: ""

# ハイフンだけの項目を削除
- source: "-"
  condition: exact
  replacement: ""

# []だけの項目を削除
- source: "[]"
  condition: exact
  replacement: ""

# (なし)だけの項目を削除
- source: "(なし)"
  condition: exact
  replacement: ""

# {prd|reh|stg}を実際の値に置換
- source: "{prd|reh|stg}"
  condition: partial
  replacement: "{env_long}"

# {P|R|S}を実際の値に置換
- source: "{P|R|S}"
  condition: partial
  replacement: "{env_short}"

- source: "｛共通基盤VPC ID｝"
  condition: partial
  replacement: "vpc-012dda1f0340ffc45"

- source: "｛共通基盤Subnet ID｝"
  condition: partial
  replacement: "subnet-067dfb85f74c94f6b"

- source: "｛共通基盤Subnet ID2｝"
  condition: partial
  replacement: "subnet-06f2e7a2fd4a848d6"

- source: "{Zabbix Security Group ID}"
  condition: partial
  replacement: "sg-012218c9d5780c52c\n"

- source: "{VolumeId}"
  condition: partial
  replacement: "vol-0a1e3d5082b3272cc"

- source: "{VolumeId2}"
  condition: partial
  replacement: "vol-023f66071637724c7"

- source: "{InstanceId}"
  condition: partial
  replacement: "i-0295f55268c6389b3"

- source: "{InstanceId2}"
  condition: partial
  replacement: "i-030cd49242e6c82a0"

- source: "TBD1"
  condition: partial
  replacement: "10.41.1.13"

- source: "TBD2"
  condition: partial
  replacement: "10.41.2.13"

- source: "arn:aws:iam::006925466389:instance-profile/xxx-stg-iam-profile-mon-ec2-ZabbixServer"
  condition: partial
  replacement: "xxx-stg-iam-profile-mon-ec2-ZabbixServer"

```

- `condition`: `exact` (完全一致) または `partial` (部分一致)
- `replacement` には動的変数 `{aws_account_id}`, `{aws_region}`, `{env_long}`, `{env_short}` などが使用可能です(商用版)。

### 4. 実行

#### AWS 認証情報の設定
   - `~/.aws/credentials` または環境変数で有効な認証情報を設定してください。
   - 比較機能を使用しない場合でも、アカウントID 置換が必要な場合は認証が必要です。
   - 共通基盤開発環境（XXX-Stg）認証例：
   　　$env:HTTP_PROXY = "http://Proxy-apj.xxxxxx.net:8080"​
   　　$env:HTTPS_PROXY = "http://Proxy-apj.xxxxxx.net:8080"
       aws sso login --profile XXX-Stg
   - config/settings-xxx.yamlに下記情報を正しく設定してください。
  ```
        compare:
          aws:
            region: "ap-northeast-1"
            profile: XXX-Stg
  ```

#### デフォルト設定（config/settings.yamlを利用する場合）で実行

```bash
python -m src.cli
```

#### 設定ファイル指定で実行

```bash
python -m src.cli config/stg/settings-ec2.yaml
```

#### 環境変数指定で実行（商用版EventBridgeのeventbusを指定する場合）

```bash
#Power Shellの場合
$env:AWS_EVENT_BUS_NAME="xxx-stg-events-bus-mon-alarmrules-dat"
python -m src.cli config/stg/settings-eventbridge.yaml
```

#### デバッグモード（CLI実装時）

```bash
python -m src.cli --debug
```

#### 設定ファイル検証

```bash
python -m src.cli --validate-only
```

#### 比較機能の実行方法
1. settings.yaml で `compare:enabled` を true に設定。
2. AWSクレデンシャルを環境変数または ~/.aws/credentials で設定。
3. 通常通り python -m src.cli を実行。
4. 出力フォルダに比較レポート JSON とログが出力されます。

## 出力

- **JSON ファイル** (`output/result_<ファイル名>_<シート名>.json`)
  Excel 各行を変換したオブジェクトの配列
- **統合 JSON** (`result_combined_all.json`) : 全ファイル結合 (設定による)
- **比較レポート** (`output/stg/入力ファイル名/stg-yyyymmddhhmiss/compare_report.md` / `.html`)
  一致/不一致/不足/対象外リソースの詳細

### 比較レポートの構成例
1. 実行情報
2. ステータスサマリ
3. 一致リソース詳細 (全プロパティの期待値と実績値。✅で可視化)
4. 不一致リソース詳細 (差分を ✅/❌ で可視化)
5. 実環境に存在しないリソース
6. 期待値に定義されていないリソース (デフォルト：非表示)
7. 対象外リソース

## ⚡ 性能目安 (Performance Reference)

大規模なインフラ環境でも実用的な速度で動作するよう、軽量かつ高速な設計（openpyxl非依存の高速XML解析など）を行っています。一般的な業務リポジトリ（ノートPC環境）でも、ストレスなく検証が可能です。

### 📊 処理時間の目安
* **検証リソース数**: 約 1,000 件
* **処理時間**: **約 10 分** （データの変換から、AWS実環境との比較・レポート同時出力まで完了）

### 💻 検証実施環境（ベンチマークスペック）
本ツールは、一般的なビジネス向けノートPCにて上記のパフォーマンスを発揮することを確認しています。

| 項目 | スペック |
| :--- | :--- |
| **OS** | Windows 11 Enterprise (23H2) |
| **CPU** | Intel(R) Core(TM) i5-10210U @ 1.60GHz (最大 2.11 GHz) |
| **メモリ** | 16.0 GB (15.8 GB 使用可能) |

### 🧑‍💻 手作業（人的操作）との効率比較
人間がAWSマネジメントコンソール（画面）とExcel仕様書を目視で比較し、レポートを手動で作成する場合と比較して、**圧倒的な業務効率化**を実現します。

| 評価項目 | 手作業（目視チェック） | spec2clouds | 効率化の効果 |
| :--- | :--- | :--- | :--- |
| **1,000件の確認時間** | **約 80.4 時間** (1件5分換算) | **約 10 分** | **約 500 倍の高速化** |
| **必要な人員・コスト** | 1〜2名のエンジニアが丸1週～2週拘束 | コマンドを1回実行するだけ | 人件費の大幅な削減 |
| **確認の正確性** | 見落としやヒューマンエラーが発生 | プログラムによる100%正確な差分検出 | チェック品質の担保 |

> 💡 **経営・現場マネージャー視点でのメリット**
> 定期的なインフラ監査やリリース後の整合性チェックを手作業で行うと、膨大な工数と「見落としリスク」が発生します。本ツールを導入することで、これまで数日かかっていた確認作業を「コーヒーを飲んでいる10分の間」に完全自動で終わらせることができます。
>
> *(※商用版のPro版では、マルチスレッド/非同期処理による並行リクエストの最適化を行い、この10分をさらに**1〜2分程度まで短縮**することが可能です)*



## 注意事項

- `.xlsx` ファイルのみ対応 (`.xls` 不可)。ZIP/XML 解析のため openpyxl 非依存。
- パスワード保護されたファイルは読み込めません
- 数式の計算結果ではなく、キャッシュされた値を読み取ります
- 比較機能利用には AWS 認証情報と適切な IAM 権限が必要です。
- プレースホルダー `{aws_account_id}` の解決には AWS 認証が必須です。失敗時は置換されません。
- 大量のリソースを比較する場合は AWS API のレート制限に注意してください。
- 入力ファイル（Excel）を開いたまま実行すると、下記のエラーが発生します。
```
ERROR - Failed to process input/cw_alarm\~$XXXXXX.xlsx: [Errno 13] Permission denied: 'input/cw_alarm\\~$XXXXXX.xlsx'
```

---

## 🤝 有償サポート・製品版のご案内 (Commercial Support & Pro Edition)

`spec2clouds` をご検討いただきありがとうございます。
本リポジトリは無料のコミュニティ版（EC2リソースの検証のみ対応）ですが、開発者個人による柔軟かつ迅速な有償サポート、および機能拡張された製品版（Pro Edition）を提供しています。

以下のような課題がございましたら、お気軽にお問い合わせください。

### 💡 このような場合にご相談ください
* **企業の商用プロジェクトへ導入したい**
  * 社内環境への導入支援、初期セットアップのレクチャー
  * 自社の運用ルールに合わせたExcelパラメータシート（テンプレート）のカスタマイズ代行
* **対応リソース・機能を拡張したい（Proエディションのご提供）**
  * `EventBridge`、`CloudWatch`、`S3` などの主要なAWSリソースの自動比較・検証
  * GitHub ActionsなどのCI/CDパイプラインに組み込むための終了コード制御（バッチ処理最適化）
* **マルチクラウドやインフラ作成への早期対応**
  * 将来ロードマップにある「GCP対応」や「定義シートからのインフラ自動構築（プロビジョニング）」機能の優先的な共同開発・個別開発

---

### 📝 お問い合わせ・ご相談窓口

個人開発ならではのフットワークの軽さで、NDA（秘密保持契約）の締結から、個別のお見積書・請求書の発行まで柔軟に対応いたします。
まずは「こういった使い方はできるか？」というカジュアルなご相談から大歓迎です。

* **担当者（開発者）:**  Y.Fukumori (💼 [LinkedIn](https://www.linkedin.com/in/8alfalfa8))

* **対応可能時間:**  平日夜間、土日祝日（メールは24時間受付、2営業日以内にご返信いたします）

> **💡 安心・安全への取り組み**
> 本ツール（無料版・有料版ともに）は、インフラの「読み取り（検証）」を主目的として設計されています。AWS環境のデータを書き換えたり破壊したりするリスクが極めて低いため、企業のセキュリティ・コンプライアンス基準もクリアしやすい仕様です。

---
