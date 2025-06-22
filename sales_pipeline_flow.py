import subprocess
from pathlib import Path
from prefect import flow, task
from google.cloud import storage
from google.cloud import bigquery
from datetime import datetime

# ====================================================================
# TASK 1: EXTRACT & LOAD (No changes here)
# ====================================================================
@task(retries=3, log_prints=True)
def extract_and_load_sales_data(bucket_name: str, file_name: str):
    """
    Reads a file from GCS and loads its raw content into a new 'raw_sales' BQ table.
    """
    print(f"Starting EL task for file: {file_name} in bucket: {bucket_name}")
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    if not blob.exists():
        print(f"File {file_name} not found in bucket {bucket_name}. Skipping.")
        return False # Return False if file not found
    raw_content = blob.download_as_text()
    print(f"Successfully extracted content from {file_name}")
    bq_client = bigquery.Client()
    table_id = f"{bq_client.project}.todos_pipeline.raw_sales"
    schema = [
        bigquery.SchemaField("file_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("raw_content", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("loaded_at", "TIMESTAMP", mode="REQUIRED"),
    ]
    table = bigquery.Table(table_id, schema=schema)
    bq_client.create_table(table, exists_ok=True)
    rows_to_insert = [
        {"file_name": file_name, "raw_content": raw_content, "loaded_at": datetime.utcnow().isoformat()}
    ]
    errors = bq_client.insert_rows_json(table_id, rows_to_insert)
    if not errors:
        print(f"Successfully loaded raw data from {file_name} into {table_id}")
    else:
        raise Exception(f"Error loading data to BigQuery: {errors}")
    return True

# ====================================================================
# TASK 2: DBT Runner Task (Copied from our previous project)
# ====================================================================
@task(log_prints=True)
def run_dbt_command(command: str):
    """
    Runs any dbt command using subprocess, ensuring it runs from the correct directory.
    """
    dbt_project_dir = Path.cwd() / "dbt_pipeline"
    print(f"Running command: {command}")
    result = subprocess.run(command.split(), cwd=dbt_project_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print("dbt command failed!")
        print(result.stderr)
        raise Exception("dbt command failed. See logs for details.")
    print("dbt command succeeded!")
    print(result.stdout)
    return True

# ====================================================================
# FLOW: The complete, end-to-end sales pipeline
# ====================================================================
@flow(name="Fully Orchestrated Sales Pipeline")
def sales_elt_flow_final():
    YOUR_BUCKET_NAME = "prueba-sales-data-1234"
    THE_FILE_TO_PROCESS = "sales_data_2025-06-22.csv"
    
    print("--- Starting Sales ELT Flow ---")
    
    # Run the Extract and Load task
    load_result = extract_and_load_sales_data(YOUR_BUCKET_NAME, THE_FILE_TO_PROCESS)
    
    if load_result:
        # After EL succeeds, run the dbt transformation for the sales model
        run_result = run_dbt_command(
            command="dbt run --select clean_sales",
            wait_for=[load_result]
        )
        
        # After the transformation succeeds, run the dbt tests for the sales model
        run_dbt_command(
            command="dbt test --select clean_sales",
            wait_for=[run_result]
        )
        print("--- Sales ELT Flow finished successfully. ---")
    else:
        print("--- Sales ELT Flow finished: No new file to process. ---")


# --- Main execution block ---
if __name__ == "__main__":
    sales_elt_flow_final()