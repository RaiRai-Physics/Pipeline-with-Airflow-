# COVID Analytics Medallion Pipeline

This repository is a GitHub-ready starter project for an end-to-end ETL / ELT pipeline using:

- **AWS** for source ingestion and storage
- **Databricks** for Bronze / Silver / Gold medallion processing
- **Snowflake** for serving curated analytics-ready data

## What this pipeline does

1. Pulls weekly COVID state-level data from an external public source.
2. Lands raw files in **Amazon S3**.
3. Ingests those files into **Databricks Bronze** using **Auto Loader**.
4. Cleans and standardizes data in **Silver**.
5. Builds dimensions, facts, and KPIs in **Gold**.
6. Publishes Gold outputs back to **S3** for **Snowflake** loading.
7. Loads curated tables into **Snowflake** with `COPY INTO`.

## Repository layout

```text
covid-analytics-medallion/
├── configs/
├── docs/
├── infra/
├── notebooks/
├── orchestration/
├── sql/
├── src/
└── tests/
```

## Runtime architecture

```text
External public source
    -> AWS Lambda
    -> S3 raw
    -> Databricks Bronze
    -> Databricks Silver
    -> Databricks Gold
    -> S3 publish
    -> Snowflake stage
    -> Snowflake analytics schema
```

## Source dataset

The default config assumes a CDC / Socrata-style CSV export URL. If you prefer a Kaggle or another source, update `source.url` in `configs/dev.yaml` and adjust the candidate column mapping in `src/silver/silver_state_weekly.py`.

## Prerequisites

- AWS account with:
  - S3
  - IAM
  - Lambda
  - EventBridge Scheduler
- Databricks workspace on AWS
- Snowflake account
- Python 3.10+
- Terraform 1.5+ if you want infra-as-code deployment

## 1) Update environment config

Edit `configs/dev.yaml`:

- `aws.bucket_name`
- `databricks.catalog`
- `snowflake.database`
- `source.url`

## 2) Deploy AWS ingestion infra

### Option A: Terraform

```bash
cd infra/terraform/aws
terraform init
terraform plan \
  -var="project_name=covid-analytics" \
  -var="environment=dev" \
  -var="aws_region=us-east-1" \
  -var="bucket_name=YOUR_BUCKET_NAME" \
  -var="source_url=https://data.cdc.gov/api/views/pwn4-m3yp/rows.csv?accessType=DOWNLOAD"
terraform apply
```

### Option B: Manual
Create:
- S3 bucket
- Lambda function from `src/ingestion/lambda_handler.py`
- EventBridge Scheduler weekly trigger
- IAM role with:
  - write access to your S3 bucket
  - CloudWatch Logs permissions

## 3) Create Databricks objects

Run:

```sql
-- sql/databricks/001_create_catalog_and_schemas.sql
-- sql/databricks/002_create_external_locations_template.sql
```

Then import or sync this repo into Databricks Repos.

## 4) Run Databricks notebooks in order

1. `notebooks/01_bronze_ingestion.py`
2. `notebooks/02_silver_transform.py`
3. `notebooks/03_gold_dimensions.py`
4. `notebooks/04_gold_fact_and_kpi.py`
5. `notebooks/05_publish_to_s3.py`

You can also create a Databricks Workflow using `orchestration/databricks_job_spec.json`.

## 5) Set up Snowflake

Run in order:

```sql
sql/snowflake/001_create_database.sql
sql/snowflake/002_create_storage_integration.sql
sql/snowflake/003_create_stage.sql
sql/snowflake/004_create_tables.sql
sql/snowflake/005_copy_into_tables.sql
sql/snowflake/006_create_views.sql
sql/snowflake/007_validation_queries.sql
```

## 6) What you need to replace

Search the repo for these placeholders:

- `YOUR_BUCKET_NAME`
- `YOUR_AWS_REGION`
- `YOUR_DATABRICKS_CATALOG`
- `YOUR_STORAGE_AWS_ROLE_ARN`
- `YOUR_SNOWFLAKE_AWS_IAM_USER_ARN`
- `YOUR_SNOWFLAKE_EXTERNAL_ID`
- `YOUR_REPO_NOTEBOOK_BASE_PATH`

## 7) Medallion layer outputs

### Bronze
- `bronze.cdc_state_weekly_raw`

### Silver
- `silver.state_weekly_metrics`
- `silver.state_weekly_metrics_quarantine`

### Gold
- `gold.dim_state`
- `gold.dim_date`
- `gold.fact_covid_state_weekly`
- `gold.kpi_latest_national_snapshot`
- `gold.top10_states_latest_cases`

## 8) Local helper commands

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Package Lambda zip locally
make package-lambda

# Run basic unit tests
pytest -q
```

## 9) Notes

- Bronze is intentionally permissive and captures metadata.
- Silver is the contract layer with standard names and types.
- Gold is modeled for analytics and Snowflake serving.
- This starter is designed to be small, readable, and easy to demo. Add more quality checks, dbt, or CI/CD later as needed.
