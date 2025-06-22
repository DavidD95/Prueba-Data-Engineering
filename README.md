
# Data Engineering Pipeline Project

## Project Goal
Automate extraction, loading, and transformation of data to create clean and usable datasets for analysis.

---

## Architecture

```
API (https://jsonplaceholder.typicode.com/todos)
        ↓
Python Script: extract_load.py
        ↓
BigQuery Staging Table: todos_pipeline.raw_todos
        ↓
Python Script: transform.py
        ↓
BigQuery Clean Table: todos_pipeline.clean_todos
```

**Explanation:**  
The pipeline fetches raw data from a live API, stores it in a raw, staging table in BigQuery, and then processes it with a transformation script into a clean, structured table ready for analysis or reporting.

---

## How It Works

The pipeline consists of two scripts:

- `extract_load.py`: Fetches data from the API and loads the raw JSON into the BigQuery staging table.
- `transform.py`: Reads raw JSON data from BigQuery, parses and cleans it, then writes the results into a clean, structured BigQuery table.

Both scripts use Google Cloud credentials to authenticate and interact with BigQuery.

---

## Setup

Before running the scripts, follow these steps to configure your environment:

### 1. Create a Google Cloud Project
- Sign up or log in to [Google Cloud Console](https://console.cloud.google.com).
- Create a new project (e.g., `de-portfolio-project`).

### 2. Enable BigQuery API
- In your project, search for “BigQuery API” and enable it.

### 3. Create a BigQuery Dataset
- Navigate to BigQuery in the console.
- Create a dataset named `todos_pipeline`.

### 4. Create a Service Account
- Go to “IAM & Admin” → “Service Accounts”.
- Click “Create Service Account”.
- Name it `pipeline-runner`.
- Assign the role “BigQuery Data Editor”.

### 5. Download the JSON Key
- From your service account, go to the “Keys” tab.
- Click “Add Key” → “Create new key” → select JSON → click “Create”.
- Save the downloaded JSON file into your project directory.

### 6. Set the Environment Variable

Tell your scripts where to find the JSON key by setting the `GOOGLE_APPLICATION_CREDENTIALS` environment variable **in the terminal session where you'll run the scripts**.

Replace `/path/to/your/key.json` with the actual path to your downloaded JSON key:

- **Mac/Linux:**

  ```bash
  export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/key.json"
  ```

- **Windows (Command Prompt):**

  ```cmd
  set GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\key.json"
  ```

- **Windows (PowerShell):**

  ```powershell
  $env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\key.json"
  ```

---

## How to Run

1. Set up the environment variable as explained above.
2. Run the extraction and loading script:

    ```
    python extract_load.py
    ```

3. Run the transformation script:

    ```
    python transform.py
    ```

Check your BigQuery console to verify the data populated in the staging and clean tables.

---

## Skills Demonstrated

### Extraction & Loading (EL)
- Fetch data from a live API.
- Store raw data in a staging table as a robust pipeline best practice.
- Separate loading and transformation using the “digital dump truck” principle.

### Transformation (T)
- Parse complex JSON from staging data.
- Load cleaned data into a structured, final table.
- Implement idempotency to ensure safe script reruns.

### Orchestration & Documentation
- Designed an automated schedule respecting script dependencies.
- Wrote clear, concise documentation enabling others to quickly understand the pipeline.

---

*Prepared as a portfolio project to demonstrate core data engineering skills.*
