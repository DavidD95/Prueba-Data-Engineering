import subprocess
import sys
from pathlib import Path
from prefect import flow, task
import requests
from google.cloud import bigquery
from datetime import datetime

# ====================================================================
# TASK 1: EXTRACT & LOAD (This remains the same)
# ====================================================================
@task(retries=3, log_prints=True)
def extract_and_load_to_staging():
    """
    Fetches data from the API and loads the raw text into a BigQuery staging table.
    """
    print("Starting: Extract & Load Task")
    client = bigquery.Client()
    table_id = f"{client.project}.todos_pipeline.raw_todos"
    
    url = "https://jsonplaceholder.typicode.com/todos"
    response = requests.get(url)
    response.raise_for_status()
    raw_json = response.text
    loaded_at = datetime.utcnow().isoformat()
    
    rows_to_insert = [{"raw_data": raw_json, "loaded_at": loaded_at}]
    errors = client.insert_rows_json(table_id, rows_to_insert)
    
    if not errors:
        print(f"Success: Loaded raw data into {table_id}")
    else:
        raise Exception(f"Error loading data: {errors}")
    return True

# ====================================================================
# NEW TASK: A generic task to run any dbt command using subprocess
# ====================================================================
@task(log_prints=True)
def run_dbt_command(command: str):
    """
    Runs any dbt command using subprocess, ensuring it runs from the correct directory.
    """
    # Get the path to the dbt project directory
    dbt_project_dir = Path.cwd() / "dbt_pipeline"
    
    print(f"Running command: {command}")
    
    # Run the command
    result = subprocess.run(
        command.split(),
        cwd=dbt_project_dir,  # Run the command from the dbt project directory
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("dbt command failed!")
        print(result.stderr)
        raise Exception("dbt command failed. See logs for details.")
    
    print("dbt command succeeded!")
    print(result.stdout)
    return True

# ====================================================================
# FLOW: The final pipeline using the subprocess task
# ====================================================================
@flow(name="Fully Orchestrated Cloud ELT Pipeline v2")
def main_elt_flow():
    """
    The main pipeline flow that orchestrates the Python EL script and dbt operations.
    """
    print("Flow started: Running ELT pipeline...")
    
    load_result = extract_and_load_to_staging()
    
    # This task now calls 'dbt run'
    run_result = run_dbt_command(
        command="dbt run",
        wait_for=[load_result]
    )
    
    # This task now calls 'dbt test'
    run_dbt_command(
        command="dbt test",
        wait_for=[run_result]
    )

    print("Flow finished successfully.")

# --- Main execution block ---
if __name__ == "__main__":
    main_elt_flow()