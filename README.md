# Data Engineering Pipeline Project

## Project Goal
Automate extraction, loading, and transformation of data to create clean and usable datasets for analysis.

## How It Works
The pipeline consists of two scripts: `extract_load.py` connects to a live API and loads raw data into a staging table, while `transform.py` cleans and parses the raw data into a structured final table. The transformation script is idempotent, so it can safely be rerun without data duplication or error.

## How to Run
1. Run `extract_load.py` to fetch and load raw data from the API into the staging database.
2. After completion, run `transform.py` to process and clean the staging data into the final table.
3. Verify the cleaned data in the final table before use.

## Skills Demonstrated

### Extraction & Loading (EL)
- Fetch data from a live API.
- Store raw data in a staging table as a robust pipeline best practice.
- Separate loading and transforming steps, following the “digital dump truck” principle.

### Transformation (T)
- Parse complex JSON from staging data.
- Load cleaned data into a structured, final table.
- Implement idempotency to ensure safe script reruns without side effects.

### Orchestration & Documentation
- Design an automated schedule that respects script dependencies.
- Write clear, concise documentation enabling others to understand the pipeline quickly.

---

*Prepared as a portfolio project to demonstrate core data engineering skills.*