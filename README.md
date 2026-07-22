# 🛠️ spec2clouds
* 🇯🇵 日本語ドキュメント (Japanese Documentation)は **[README.ja.md](./README.ja.md)** をご覧ください。

---


<!-- PROFILE_BADGE_START -->

[![GitHub](https://img.shields.io/badge/GitHub-Profile-181717?logo=github)](https://github.com/8alfalfa8)
[![Qiita](https://img.shields.io/badge/Qiita-Profile-55C500?logo=qiita&logoColor=white)](https://qiita.com/8alfalfa8)
[![Zenn](https://img.shields.io/badge/Zenn-Profile-3EA8FF?logo=zenn&logoColor=white)](https://zenn.dev/8alfalfa8)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/8alfalfa8)

<!-- PROFILE_BADGE_END -->

This tool generates test data (JSON) for AWS resources from an Excel parameter sheet and compares it with resources in the actual AWS environment.
It enables flexible data transformation through a template-driven approach, and comparison results can be output as Markdown or HTML reports.

---

## ✅ Key Features

## Features

- **Excel → JSON Conversion**
  - Automatic parsing of multi-level headers
  - Column control (specifying valid columns) and determination of whether data rows are valid (included) or invalid (excluded)
  - Automatic replacement of environment tokens `{prd|reh|stg|dev}` / `{P|R|S|D}`
  - Supports both automatic template generation and manual customization
- **Comparison of Expected Values vs. AWS Actuals**
  - Supports comparisons of AWS services (EC2, CloudWatch, EventBridge, etc.) (Free Tier EC2 only)
  - Detection of matching, mismatched, insufficient, and excess resources
  - Simultaneous output of comparison reports in Markdown and HTML (Commercial Edition)
- **Custom String Replacement**
  - Flexible replacement using external replacement rule files (per template)
  - Specify replacement conditions (exact match / partial match)
  - Ability to embed dynamic variables (such as `{aws_account_id}`) in the replaced string (Commercial Edition)
- **Report Output**
  - Compresses JSON properties into a single line and inlines code to prevent table layout issues
  - Function to specify the report language in accordance with internationalization standards (Commercial Edition)
- **Batch Processing Support (Commercial Edition)**
  - Returns an exit code to support execution via batch processing.
  - If both the number of “mismatches (NG)” and the number of “records not found in production” are 0, returns exit code 0 (successful completion).
  - In all other cases, returns exit code 1 (abnormal termination).

---
## Project Structure
<!-- START_TREE -->
├── [LICENSE](LICENSE)  
├── [README.ja.md](README.ja.md)  
├── [README.md](README.md)  
├── config/  
│&nbsp;&nbsp;&nbsp; ├── [replace.yaml](config/replace.yaml)  
│&nbsp;&nbsp;&nbsp;├── [settings.yaml](config/settings.yaml)  
│&nbsp;&nbsp;&nbsp;└── stg/  
│ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── [replace_ec2.yaml](config/stg/replace_ec2.yaml)  
│&nbsp;&nbsp;& nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── [settings-ec2.yaml](config/stg/settings-ec2.yaml)  
├── input/  
│&nbsp;&nbsp;&nbsp;└── ec2/  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; └── [EC2.xlsx](input/ec2/EC2.xlsx)  
├── [requirements.txt](requirements.txt)  
└── src/  
&nbsp;&nbsp;&nbsp;&nbsp;├── [cli.py](src/cli.py)  
&nbsp;&nbsp;&nbsp;&nbsp;├── collector/  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp; ├── [__init__.py](src/collector/__init__.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└ ── [aws_collector.py](src/collector/aws_collector.py)  
&nbsp;&nbsp;&nbsp;&nbsp;├── comparator/  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [__init__.py](src/comparator/__init__.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp; &nbsp;&nbsp;├── [comparator.py](src/comparator/comparator.py)  
&nbsp; &nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└── [report_generator.py](src/comparator/report_generator.py)  
&nbsp;&nbsp;&nbsp;&nbsp;├── core/  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [__init__.py](src/core/__init__.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [config_validator.py](src/core/config_validator.py)  
&nbsp;&nbsp;&nbsp;&nbsp; │&nbsp;&nbsp;&nbsp;├── [data_processor.py](src/core/data_processor.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp; ├── [excel_reader.py](src/core/excel_reader.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp; └── [header_processor.py](src/core/header_processor.py)  
&nbsp;&nbsp;&nbsp;&nbsp;├── [init.py](src/init.py)  
&nbsp;&nbsp;&nbsp;&nbsp;├── [main.py](src/main.py)  
&nbsp;&nbsp;&nbsp;&nbsp;├── models/  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [resource.py](src/models/resource.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└ ── [sheet_context.py](src/models/sheet_context.py)  
&nbsp;&nbsp;&nbsp;&nbsp;├── normalizer/  
&nbsp;&nbsp; &nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [__init__.py](src/normalizer/__init__.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp; &nbsp;&nbsp;├── [aws_normalizer.py](src/normalizer/aws_normalizer.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp; &nbsp;└── [expected_normalizer.py](src/normalizer/expected_normalizer.py)  
&nbsp;&nbsp;&nbsp;&nbsp;├── output/  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├─ ─ [__init__.py](src/output/__init__.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [json_generator.py](src/output/json_generator.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── [template_builder.py](src/output/template_builder.py)  
&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└── [template_engine.py](src/output/template_engine.py)  
&nbsp;&nbsp;&nbsp;&nbsp;└── utils/  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ├── [__init__.py](src/utils/__init__.py)  
├── [excel_utils.py](src/utils/excel_utils.py)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ├── [string_utils.py](src/utils/string_utils.py)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── [validation.py](src/utils/validation.py)  

12 directories, 35 files  
<!-- END_TREE -->

---

## System Requirements

- Python 3.9+
- Recommended: Python 3.11 or later

Dependencies:

- pandas
- pyyaml
- boto3

## Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd spec2clouds

# 2. Install dependency packages
pip install -r requirements.txt

```

---

## 📙 How to Use

### 1. Prepare the Configuration File

Edit `config/stg/settings-ec2.yaml` to set the path to the Excel file and the analysis conditions.

```yaml
# config\stg\settings-ec2.yaml
# ============================================================
# spec2clouds stg configuration file
# ============================================================

# --- Environment Specification ---
env: "stg" # {prd|reh|stg|dev} or {P|R|S|D}

# --- Input/Output Settings ---
input:
  directory: "input/ec2" # Folder for input Excel files
  file_pattern: "*.xlsx" # Pattern for files to be processed

output:
  directory: "output/stg/ec2" # Output folder
  file_prefix: "result" # Output file prefix
  combine_all: true # Whether to output a consolidated JSON file for all files

# --- Template Settings ---
template:
  auto_generate: true # Enable automatic template generation
  auto_generate_only: false # Perform only automatic generation and skip normal processing
  id_cell: "C5" # Cell containing the template ID
  directory: "templates/ec2" # Folder for template files
  mapping: # AWS service ID → Template filename
    "EC2": "EC2.json"

# --- Normalization Settings ---
normalize:
  unicode_form: "" # Default: NFKC (NFC/NFKC/NFD/NFKD)
  regex_escape: false # Default: true

# --- Sheets to Validate ---
target_sheets:
  - "EC2"

# --- Header Settings ---
header:
  start_row: 7 # Header start row (starting from row 1)
  max_levels: 3 # Maximum number of header levels
  start_string: "" # Start column string (empty = non-empty cell)
  end_string: "Remarks" # End column string (empty = empty cell)
  fill_empty_cells: true # Fill empty cells from the top/front

# --- Data Settings ---
data:
  data_start_row: 11 # Data start row (starting at 1; empty = header end row + 1)
  end_row_string: "Remarks" # String in the first cell marking the end of data (empty = empty cell)
  termination:
    empty_row_threshold: 2 # Number of consecutive empty rows to consider as data end

  # --- Column Control Settings ---
  column_control:
    row: 6 # Control row (starting at 1; 0 = disabled)
    exclude_value: "0" # Value indicating exclusion

  # --- Data Row Control Settings ---
  invalid_row_control:
    column: "DO" # Evaluation column
    invalid_value: "0" # A row is invalid if this value is present
    output_field: "enabled" # Field name to output the validation result for invalid rows
    valid_output: true # Validation value for valid rows
    invalid_output: false # Validation value for invalid rows
    skip_invalid_rows: false # Whether to skip invalid rows from the output

# --- Comparison Settings ---
compare:
  enabled: true # Whether to perform the comparison
  show_extra_resources: false # Set to true to display Chapter 6; set to false to hide it
  timezone: "Asia/Tokyo" # Default: Tokyo
  aws:
    region: "ap-northeast-1"
    profile: XXX-Stg # AWS profile name (default if null)
  resources: # List of AWS service IDs to compare
    - "EC2"

# --- Replacement Rule Settings ---
replace_rules:
  mapping:
    "EC2": "replace_ec2.yaml"

# --- JSON: Key-Value Mapping Settings -- -
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

  # Specify the paths of items where numeric data should be treated as strings
  preserve_string_paths:
    - Metrics.AccountId

```
### 2. Placing Excel Files

Place the .xlsx files you want to process in the `input/ec2/` folder.

#### Excel Format Requirements

##### Service Identification

- Enter the service ID in cell `C5` of each sheet (configurable via `template:id_cell`)

Example:

```text
C5 = EC2
```

##### Column Control Row

- Enter the following in the row specified by `data:column_control:row`:

| Value | Meaning |
|----|------|
| 1  | To be output |
| 0  | Excluded |

##### Invalid Row Control

- You can enable or disable rows based on the value in the column specified by `data:invalid_row_control:column`

---

### 3. Customizing Templates

- Upon first execution, templates are automatically generated in the `templates/` directory via `auto_generate: true`.
- The generated templates can be edited manually.
  Example (`EC2.json`):
  ```json
  {
    "source": {
 "file": "{{$file}}",
 "sheet": "{{$sheet}}",
 "row_index": "{{$index}}",
 "env": "{{$env}}"
    } ,
    "data": {
 "InstanceId": "{{InstanceId}}",
 "Name": "{{Name}}",
 "InstanceType": "{{InstanceType}}"
    }
  }
  ```
- Variables are referenced as `{{column_name}}`, and the value from the corresponding column in Excel is embedded.
- Special variables: `{{$index}}` (row number), `{{$file}}` (file name), `{{$sheet}}` (sheet name), `{{$env}}` (environment)

### 4. Replacement Rules

You can define replacement rules in a YAML file for each template.
Place the files in the `config/` directory and associate them via `replace_rules.mapping` in `settings.yaml`.

**Format (example from `config/stg/replace_ec2.yaml`)**:
```yaml
# config\stg\replace-ec2.yaml
# Replacement rules for EC2
# Configuration for associating replacement rules with processing:
#    config\settings-ec2.yaml
# replace_rules:
# mapping:
# Configuration description:
#   - source: String before replacement
#     condition: partial (partial: partial replacement / exact: exact match)
#     replacement: String after replacement
#

# Remove unnecessary "blank" strings
- source: "blank"
  condition: exact
  replacement: ""

# Remove items consisting only of hyphens
- source: "-"
  condition: exact
  replacement: ""

# Remove entries consisting only of []
- source: "[]"
  condition: exact
  replacement: ""

# Remove entries consisting only of "(None)"
- source: "(None)"
  condition: exact
  replacement: ""

# Replace {prd|reh|stg} with the actual value
- source: "{prd|reh|stg}"
  condition: partial
  replacement: "{env_long}"

# Replace {P|R|S} with the actual value
- source: "{P|R|S}"
  condition: partial
  replacement: "{env_short}"

- source: "{Common Infrastructure VPC ID}"
  condition: partial
  replacement: "vpc-012dda1f0340ffc45"

- source: "{Common Infrastructure Subnet ID}"
  condition: partial
  replacement: "subnet-067dfb85f74c94f6b"

- source: "{Common Infrastructure Subnet ID2}"
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

- source: "arn:aws: iam::006925466389:instance-profile/xxx-stg-iam-profile-mon-ec2-ZabbixServer"
  condition: partial
  replacement: "xxx-stg-iam-profile-mon-ec2-ZabbixServer"

```

- `condition`: `exact` (exact match) or `partial` (partial match)
- `replacement` can use dynamic variables such as `{aws_account_id}`, `{aws_region}`, `{env_long}`, `{env_short}`, and others (Commercial Edition).

### 4. Execution

#### Configuring AWS Credentials
   - Set valid credentials in `~/.aws/credentials` or via environment variables.
   - Authentication is required even if you do not use the comparison feature, provided that account ID substitution is necessary.
   - Example of credentials for the Shared Infrastructure Development Environment (XXX-Stg):
   　　$env:HTTP_PROXY = "http://Proxy-apj.xxxxxx.net:8080"​
 $env:HTTPS_PROXY = "http://Proxy-apj.xxxxxx.net:8080"
       aws sso login --profile XXX-Stg
   - Please configure the following information correctly in `config/settings-xxx.yaml`.
  ```
 compare:
 aws:
 region: "ap-northeast-1"
 profile: XXX-Stg
  ```

#### Run with default settings (when using config/settings.yaml)

```bash
python -m src.cli
```

#### Run by specifying a configuration file

```bash
python -m src.cli config/stg/settings-ec2.yaml
```

#### Run using environment variables (when specifying the commercial EventBridge event bus)

```bash
# For PowerShell
$env:AWS_EVENT_BUS_NAME="xxx-stg-events-bus-mon-alarmrules-dat"
python -m src.cli config/stg/settings-eventbridge.yaml
```

#### Debug mode (when implementing the CLI)

```bash
python -m src.cli --debug
```

#### Validating the Configuration File

```bash
python -m src.cli --validate-only
```

#### How to Run the Comparison Feature
1. Set `compare:enabled` to true in `settings.yaml`.
2. Set AWS credentials via environment variables or in ~/.aws/credentials.
3. Run `python -m src.cli` as usual.
4. The comparison report JSON and logs will be output to the output folder.

## Output

- **JSON Files** (`output/result_<filename>_<sheet_name>.json`)
  An array of objects representing each Excel row
- **Combined JSON** (`result_combined_all.json`): All files combined (depending on settings)
- **Comparison Report** (`output/stg/input_filename/stg-yyyymmddhhmiss/compare_report.md` / `.html`)
  Details of matching, mismatched, missing, and excluded resources

### Example Comparison Report Structure
1. Execution Information
2. Status Summary
3. Matching Resource Details (Expected and actual values for all properties; visualized with ✅)
4. Mismatched Resource Details (Differences visualized with ✅/❌)
5. Resources Not Present in the Production Environment
6. Resources Not Defined in the Expected Values (Default: Hidden)
7. Excluded Resources

## ⚡ Performance Reference

We’ve implemented a lightweight and high-speed design (such as high-speed XML parsing independent of openpyxl) to ensure the tool runs at a practical speed even in large-scale infrastructure environments. You can perform verification without any issues even on a typical work laptop.

### 📊 Estimated Processing Time
* **Number of Resources Verified**: Approximately 1,000
* **Processing Time**: **Approximately 10 minutes** (from data conversion to comparison with the actual AWS environment and simultaneous report generation)

### 💻 Testing Environment (Benchmark Specifications)
We have confirmed that this tool delivers the above performance on a typical business laptop.

| Item | Specifications |
| :--- | :--- |
| **OS** | Windows 11 Enterprise (23H2) |
| **CPU** | Intel® Core™ i5-10210U @ 1.60 GHz (up to 2.11 GHz) |
| **Memory** | 16.0 GB (15.8 GB available) |

### 🧑‍💻 Efficiency Comparison with Manual (Human) Operations
Compared to a scenario where a human visually compares the AWS Management Console (screen) with an Excel specification sheet and manually creates a report, this solution achieves **overwhelming operational efficiency improvements**.

| Evaluation Item | Manual Work (Visual Check) | spec2clouds | Efficiency Gain |
| :--- | :--- | :--- | :--- |
| **Time to Verify 1,000 Records** | **Approx. 80.4 hours** (based on 5 minutes per record) | **Approx. 10 minutes** | **Approx. 500 times faster** |
| **Personnel and Costs Required** | 1–2 engineers tied up for 1–2 full weeks | Simply run a single command | Significant reduction in labor costs |
| **Verification Accuracy** | Oversights and human errors occur | 100% accurate difference detection via program | Guaranteed check quality |

> 💡 **Benefits from the Perspective of Executives and On-Site Managers**
> Performing regular infrastructure audits and post-release consistency checks manually results in enormous man-hours and the “risk of oversights.” By implementing this tool, verification tasks that previously took several days can be completed fully automatically in “the 10 minutes it takes to drink a cup of coffee.”
>
> *(※In the commercial Pro version, parallel requests are optimized using multithreading and asynchronous processing, making it possible to **further reduce** this 10-minute process to **about 1–2 minutes**)*



## Notes

- Supports only `.xlsx` files (`.xls` not supported). Does not depend on openpyxl for ZIP/XML parsing.
- Cannot read password-protected files
- Reads cached values rather than the results of formula calculations
- AWS credentials and appropriate IAM permissions are required to use the comparison feature.
- AWS authentication is required to resolve the placeholder `{aws_account_id}`. If authentication fails, the placeholder will not be replaced.
- Be mindful of AWS API rate limits when comparing large numbers of resources.
- If you run this script while the input file (Excel ) open while running the script, the following error will occur:
```
ERROR - Failed to process input/cw_alarm\~$XXXXXX.xlsx: [Errno 13] Permission denied: 'input/cw_alarm\\~$XXXXXX.xlsx'
```

---

## 🤝 Information on Paid Support and the Pro Edition

Thank you for considering `spec2clouds`.
While this repository offers a free Community Edition (which supports only EC2 resource verification), we also provide flexible and prompt paid support from the developer, as well as a feature-enhanced Pro Edition.

Please feel free to contact us if you encounter any of the following issues.

### 💡 Please Contact Us in the Following Situations
* **You want to implement it in a corporate commercial project**
  * Assistance with deployment in your internal environment and guidance on initial setup
  * Customization of Excel parameter sheets (templates) to align with your company’s operational rules
* **You want to expand supported resources and features (Pro Edition available)**
  * Automated comparison and validation of major AWS resources such as `EventBridge`, `CloudWatch`, and `S3`
  * Exit code control for integration into CI/CD pipelines such as GitHub Actions (Batch processing optimization)
* **Early support for multi-cloud and infrastructure creation**
  * Priority joint development or custom development of features on our future roadmap, such as “GCP support” and “automatic infrastructure provisioning from definition sheets”

---

### 📝 Contact & Consultation

Leveraging the agility unique to independent development, we offer flexible support—from signing NDAs (Non-Disclosure Agreements) to issuing customized quotes and invoices.
We welcome casual inquiries, such as “Can this be used in this way?”

* **Contact (Developer):**  Y. Fukumori (💼 [LinkedIn](https://www.linkedin.com/in/8alfalfa8))

* **Availability:**  Weekday evenings, weekends, and holidays (Emails are accepted 24 hours a day; we will reply within 2 business days)

> **💡 Commitment to Safety and Security**
> This tool (both the free and paid versions) is designed primarily for “reading (verifying)” infrastructure. Since the risk of overwriting or destroying data in AWS environments is extremely low, the tool’s design makes it easy to meet corporate security and compliance standards.

---
