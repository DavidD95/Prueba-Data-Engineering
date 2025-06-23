# Modern Data Engineering Portfolio Projects

This repository showcases a series of end-to-end data engineering projects, demonstrating a mastery of modern data stack tools and best practices. The projects cover API data ingestion, file-based batch processing, cloud integration, data transformation, orchestration, and automated data quality testing.

## Core Technologies & Concepts Demonstrated

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Prefect](https://img.shields.io/badge/Prefect-0052FF?style=for-the-badge&logo=prefect&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-FF694B?style=for-the-badge&logo=dbt&logoColor=white)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![BigQuery](https://img.shields.io/badge/BigQuery-669DF6?style=for-the-badge&logo=google-bigquery&logoColor=white)
![Cloud Storage](https://img.shields.io/badge/Cloud_Storage-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-000000?style=for-the-badge&logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

---

## Project 1: API-Driven ELT Pipeline

This project builds an automated pipeline that pulls data from a public REST API, stages it in a cloud data warehouse, and uses dbt to transform and test the data.

### Architecture
`REST API` -> `Python Script` -> `Google BigQuery (Staging)` -> `dbt` -> `Google BigQuery (Clean)` -> `Data Quality Tests`

### Key Features
- **Orchestration:** Fully automated and scheduled using **Prefect**.
- **Extraction & Loading:** Python script extracts data from a live API and loads raw JSON into a BigQuery staging table.
- **Transformation:** dbt models transform the raw JSON into a clean, structured, and analytics-ready table.
- **Data Quality:** Includes automated data quality tests (e.g., `unique`, `not_null`) managed by dbt to ensure data integrity.

---

## Project 2: Automated File-Based Batch Processing Pipeline

This project simulates a common enterprise scenario where data arrives daily as files in a cloud storage bucket. The pipeline automatically detects, processes, validates, and archives these files.

### Architecture
`New File in GCS` -> `Prefect (Scheduled)` -> `Python Script (EL)` -> `BigQuery (Staging)` -> `dbt (T+Tests)` -> `BigQuery (Clean)` -> `Archive File in GCS`

### Key Features
- **Dynamic File Detection:** The pipeline automatically discovers new files in a Google Cloud Storage (GCS) bucket.
- **Incremental Models:** The dbt transformation is configured as an `incremental` model, ensuring that historical data is preserved and only new data is appended.
- **"List, Process, Archive" Pattern:** Implements a robust pattern where files are moved to an `archive` folder after successful processing to prevent duplicate work.
- **End-to-End Automation:** The entire workflow is orchestrated by a single, scheduled Prefect flow.

---

## Setup & Local Execution

### Prerequisites
- Python 3.11+
- A Google Cloud Platform (GCP) project with BigQuery and Cloud Storage APIs enabled.
- A GCP Service Account with `BigQuery Data Editor`, `BigQuery User`, and `Storage Object Admin` roles.

### Configuration

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/DavidD95/Prueba-Data-Engineering.git](https://github.com/DavidD95/Prueba-Data-Engineering.git)
    cd Prueba-Data-Engineering
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure dbt:** Set up your `~/.dbt/profiles.yml` file to connect to your BigQuery project using your service account keyfile, as detailed in the dbt documentation.

4.  **Set Environment Variables:** For the orchestration system to work, you must set permanent environment variables for your operating system that point to your GCP credentials and local Prefect server.
    - `GOOGLE_APPLICATION_CREDENTIALS`: The absolute path to your GCP keyfile.
    - `PREFECT_API_URL`: The address of your local Prefect server (e.g., `http://127.0.0.1:4200/api`).

### Running the System
This project is designed as a client-server orchestration system. To run it locally, you need two terminals running continuously:

1.  **Terminal 1 (Start the Server):**
    ```bash
    prefect server start
    ```

2.  **Terminal 2 (Start the Worker):**
    ```bash
    # Ensure environment variables are set if not done permanently
    prefect worker start --pool "dynamic-workpool"
    ```

You will need a third terminal to deploy the flow initially:

3.  **Terminal 3 (Deploy the Flow):**
    ```bash
    # This only needs to be run once, or when you update the code
    prefect deploy dynamic_pipeline.py:dynamic_elt_flow --name "Sales Pipeline Deployment" --cron "*/5 * * * *"
    ```

Once these components are running, the system is fully autonomous and will execute the file-based pipeline according to the schedule.

---

*Prepared as a portfolio project to demonstrate core data engineering skills.*
