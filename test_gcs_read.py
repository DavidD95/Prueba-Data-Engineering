from google.cloud import storage
import os

def read_gcs_bucket(bucket_name: str, file_name: str):
    """Connects to GCS, lists files, and reads a specific file."""
    
    # The client will use the same GOOGLE_APPLICATION_CREDENTIALS environment variable
    # that you set up for BigQuery. No new configuration is needed.
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        print(f"Successfully connected to bucket: {bucket_name}")
        print("-" * 30)
        
        # --- List files in the bucket ---
        print("Files found in bucket:")
        blobs = storage_client.list_blobs(bucket_name)
        for blob in blobs:
            print(f"- {blob.name}")
        
        print("-" * 30)

        # --- Read a specific file ---
        print(f"Reading content of file: {file_name}")
        blob = bucket.blob(file_name)
        content = blob.download_as_text()
        
        print("File content:")
        print(content)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure your bucket name is correct and the service account has the 'Storage Object Viewer' role.")

# --- Main execution block ---
if __name__ == "__main__":
    
    YOUR_BUCKET_NAME = "prueba-sales-data-1234"
    THE_FILE_TO_READ = "sales_data_2025-06-22.csv"
    
    read_gcs_bucket(YOUR_BUCKET_NAME, THE_FILE_TO_READ)