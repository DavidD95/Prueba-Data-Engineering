-- This config block tells dbt to build this model as a table
{{ config(materialized='table') }}

-- This SQL statement performs the transformation
WITH raw_data AS (
    -- Select the most recent raw data record from our staging table
    SELECT raw_data
    FROM {{ source('todos_pipeline', 'raw_todos') }}
    ORDER BY loaded_at DESC
    LIMIT 1
)

-- BigQuery's JSON functions are used to parse the data.
-- We use CROSS JOIN and UNNEST to turn the JSON array into individual rows.
SELECT
    CAST(JSON_VALUE(todo_item, '$.id') AS INT64) AS id,
    CAST(JSON_VALUE(todo_item, '$.userId') AS INT64) AS user_id,
    JSON_VALUE(todo_item, '$.title') AS title,
    CAST(JSON_VALUE(todo_item, '$.completed') AS BOOL) AS completed
FROM
    raw_data,
    UNNEST(JSON_QUERY_ARRAY(raw_data.raw_data)) AS todo_item