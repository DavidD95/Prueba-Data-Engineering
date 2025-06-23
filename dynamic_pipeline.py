import subprocess
from pathlib import Path
from prefect import flow, task
from google.cloud import storage
from google.cloud import bigquery
from datetime import datetime

# ====================================================================
# Task: Find new files to process in GCS
# ====================================================================
@task(log_prints=True)
def get_new_files(bucket_name: str):
    """Looks for any files in the bucket that are not in the 'archive' folder."""
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name)
    new_files = [blob.name for blob in blobs if not blob.name.startswith("archive/")]
    if not new_files:
        print("No new files found to process.")
    else:
        print(f"Found {len(new_files)} new files to process: {new_files}")
    return new_files

# ====================================================================
# Task: Run the EL process for a single file
# ====================================================================
@task(retries=3, log_prints=True)
def extract_and_load_file(bucket_name: str, file_name: str):
    """Reads a file from GCS and loads its raw content into a BQ staging table."""
    print(f"--- Processing file: {file_name} ---")
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    raw_content = blob.download_as_text()
    
    bq_client = bigquery.Client()
    table_id = f"{bq_client.project}.todos_pipeline.raw_sales"
    schema = [
        bigquery.SchemaField("file_name", "STRING"),
        bigquery.SchemaField("raw_content", "STRING"),
        bigquery.SchemaField("loaded_at", "TIMESTAMP"),
    ]
    table = bigquery.Table(table_id, schema=schema)
    bq_client.create_table(table, exists_ok=True)
    rows_to_insert = [
        {"file_name": file_name, "raw_content": raw_content, "loaded_at": datetime.utcnow().isoformat()}
    ]
    errors = bq_client.insert_rows_json(table_id, rows_to_insert)
    if not errors:
        print(f"Successfully staged data from {file_name}")
    else:
        raise Exception(f"Error loading data to BigQuery: {errors}")
    return True

# ====================================================================
# Task: Run dbt commands using subprocess
# ====================================================================
@task(log_prints=True)
def run_dbt_command(command: str):
    """Runs any dbt command using subprocess from the correct directory."""
    dbt_project_dir = Path(__file__).parent / "dbt_pipeline"
    print(f"Running command: {command}")
    # Use 'dbt' directly since we fixed the PATH. If it fails, revert to 'python -m dbt.main'
    result = subprocess.run(command.split(), cwd=dbt_project_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print("dbt command failed!")
        print(result.stderr)
        raise Exception("dbt command failed.")
    print("dbt command succeeded!")
    print(result.stdout)
    return True

# ====================================================================
# Task: Archive a successfully processed file
# ====================================================================
@task(log_prints=True)
def archive_file(bucket_name: str, file_name: str):
    """Moves a file to the 'archive' folder in the same GCS bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    source_blob = bucket.blob(file_name)
    destination_blob_name = f"archive/{file_name}"
    bucket.copy_blob(source_blob, bucket, new_name=destination_blob_name)
    source_blob.delete()
    print(f"Successfully archived {file_name}")
    return True

# ====================================================================
# FLOW: The complete, final, dynamic pipeline
# ====================================================================
@flow(name="Dynamic File Processing Pipeline")
def dynamic_elt_flow():
    YOUR_BUCKET_NAME = "prueba-sales-data-1234" #<-- Make sure this is your bucket name
    print("--- Starting Dynamic File Processing Flow ---")
    
    files_to_process = get_new_files(bucket_name=YOUR_BUCKET_NAME)
    
    if not files_to_process:
        print("--- Flow finished: No new files to process. ---")
        return

    # Process each file one by one
    for file_name in files_to_process:
        load_result = extract_and_load_file(bucket_name=YOUR_BUCKET_NAME, file_name=file_name)

    # After ALL files are loaded, run dbt ONCE
    print("--- All files loaded. Now running dbt transformations. ---")
    dbt_run_result = run_dbt_command(command="dbt run --select clean_sales", wait_for=[load_result])
    dbt_test_result = run_dbt_command(command="dbt test --select clean_sales", wait_for=[dbt_run_result])

    # After dbt is done, archive ALL the files we processed
    for file_name in files_to_process:
        archive_file(bucket_name=YOUR_BUCKET_NAME, file_name=file_name, wait_for=[dbt_test_result])

    print("--- Dynamic File Processing Flow finished successfully. ---")

# --- Main execution block ---
if __name__ == "__main__":
    dynamic_elt_flow()