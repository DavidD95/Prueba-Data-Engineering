{{ config(materialized='table') }}

WITH latest_raw_sales AS (
    -- First, find the most recently loaded batch of raw sales data
    SELECT raw_content
    FROM {{ source('todos_pipeline', 'raw_sales') }}
    ORDER BY loaded_at DESC
    LIMIT 1
),
split_rows AS (
    -- Next, split the raw CSV content into individual lines (rows)
    -- We also filter out the header row
    SELECT row_str
    FROM latest_raw_sales,
    UNNEST(SPLIT(raw_content, '\n')) AS row_str
    WHERE row_str NOT LIKE 'order_id,product_name%'
)
-- Finally, split each row by the comma, TRIM any invisible characters,
-- and then cast them to the correct data types.
SELECT
    CAST(TRIM(SPLIT(row_str, ',')[OFFSET(0)]) AS INT64) AS order_id,
    TRIM(SPLIT(row_str, ',')[OFFSET(1)]) AS product_name,
    CAST(TRIM(SPLIT(row_str, ',')[OFFSET(2)]) AS INT64) AS quantity,
    CAST(TRIM(SPLIT(row_str, ',')[OFFSET(3)]) AS FLOAT64) AS price,
    CAST(TRIM(SPLIT(row_str, ',')[OFFSET(4)]) AS DATE) AS sale_date
FROM split_rows
WHERE row_str != '' -- Filter out any potential empty lines