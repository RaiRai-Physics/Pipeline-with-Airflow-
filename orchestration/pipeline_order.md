# Pipeline order

## AWS
1. Deploy Terraform in `infra/terraform/aws`.
2. Confirm Lambda can write into `s3://YOUR_BUCKET_NAME/raw/cdc_state_weekly/`.
3. Trigger Lambda once manually from AWS console or CLI.

## Databricks
1. Run `sql/databricks/001_create_catalog_and_schemas.sql`
2. Set up external locations or storage credentials if needed.
3. Import repo to Databricks Repos.
4. Run notebooks:
   - `01_bronze_ingestion.py`
   - `02_silver_transform.py`
   - `03_gold_dimensions.py`
   - `04_gold_fact_and_kpi.py`
   - `05_publish_to_s3.py`

## Snowflake
1. Run `sql/snowflake/001_create_database.sql`
2. Run `sql/snowflake/002_create_storage_integration.sql`
3. Update AWS IAM trust with returned Snowflake values.
4. Run `sql/snowflake/003_create_stage.sql`
5. Run `sql/snowflake/004_create_tables.sql`
6. Run `sql/snowflake/005_copy_into_tables.sql`
7. Run `sql/snowflake/006_create_views.sql`
8. Run `sql/snowflake/007_validation_queries.sql`
