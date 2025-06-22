import json
from google.cloud import bigquery
import os

def transform_in_bq():
    # Setup the BigQuery client
    client = bigquery.Client()
    project_id = client.project

    # Define our source (staging) and destination (clean) tables
    source_table_id = f"{project_id}.todos_pipeline.raw_todos"
    dest_table_id = f"{project_id}.todos_pipeline.clean_todos"

    # --- Part 1: Define the schema for the clean destination table ---
    dest_schema = [
        bigquery.SchemaField("id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "INTEGER"),
        bigquery.SchemaField("title", "STRING"),
        bigquery.SchemaField("completed", "BOOLEAN"),
    ]
    
    # Create the destination table if it doesn't exist
    dest_table = bigquery.Table(dest_table_id, schema=dest_schema)
    client.create_table(dest_table, exists_ok=True)
    print(f"Destination table {dest_table_id} is ready.")

    # --- Part 2: Read, Transform, and Load ---
    # Query the raw data from our staging table
    query = f"SELECT raw_data FROM `{source_table_id}`"
    query_job = client.query(query)  # Make an API request.

    rows_to_insert = []
    print("Reading raw data and transforming...")
    for row in query_job:
        # The raw data is a single JSON string, parse it
        raw_json_text = row["raw_data"]
        todos = json.loads(raw_json_text)
        
        # Transform each item in the JSON list into a clean dictionary
        for todo_item in todos:
            clean_row = {
                "id": todo_item.get("id"),
                "user_id": todo_item.get("userId"),
                "title": todo_item.get("title"),
                "completed": todo_item.get("completed")
            }
            rows_to_insert.append(clean_row)

    # --- Part 3: Insert clean data into the destination table ---
    if rows_to_insert:
        # Note: For production, you'd likely use a MERGE statement to handle idempotency.
        # For our learning purpose, we'll clear the table before inserting to keep it simple.
        client.query(f"TRUNCATE TABLE `{dest_table_id}`").result() 
        
        errors = client.insert_rows_json(dest_table_id, rows_to_insert)
        if not errors:
            print(f"Successfully inserted {len(rows_to_insert)} rows into clean_todos.")
        else:
            print(f"Encountered errors: {errors}")
    else:
        print("No rows to insert.")

if __name__ == "__main__":
    transform_in_bq()