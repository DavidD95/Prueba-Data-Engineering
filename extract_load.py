import requests
from google.cloud import bigquery
from datetime import datetime
import os

def fetch_and_load_to_bq():
    # --- Part 1: Fetch data from API (Same as before) ---
    url = "https://jsonplaceholder.typicode.com/todos"
    try:
        response = requests.get(url)
        response.raise_for_status()
        raw_json = response.text
        loaded_at = datetime.utcnow().isoformat()
        
        # --- Part 2: Load data into BigQuery ---
        # The client will automatically use the credentials from your environment variable.
        client = bigquery.Client()
        
        # Define your table ID (project.dataset.table)
        table_id = f"{client.project}.todos_pipeline.raw_todos"
        
        # Define the schema for our staging table
        schema = [
            bigquery.SchemaField("raw_data", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("loaded_at", "TIMESTAMP", mode="REQUIRED"),
        ]
        
        # Create the table if it doesn't exist
        table = bigquery.Table(table_id, schema=schema)
        client.create_table(table, exists_ok=True)
        
        # Prepare the row(s) to insert
        rows_to_insert = [
            {"raw_data": raw_json, "loaded_at": loaded_at}
        ]
        
        # Insert the data
        errors = client.insert_rows_json(table_id, rows_to_insert)
        if not errors:
            print("Raw data loaded to BigQuery successfully.")
        else:
            print(f"Encountered errors while inserting rows: {errors}")
            
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    fetch_and_load_to_bq()