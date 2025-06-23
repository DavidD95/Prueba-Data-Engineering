{{ config(
    materialized='incremental',
    unique_key='order_id'
) }}

-- This SQL statement performs the transformation
WITH source_data AS (
    -- Select all raw sales records from the staging table
    SELECT * FROM {{ source('todos_pipeline', 'raw_sales') }}
    
    {% if is_incremental() %}
    -- If this is an incremental run, only select records that are newer
    -- than the most recent record already in the clean_sales table.
    WHERE loaded_at > (SELECT MAX(loaded_at) FROM {{ this }})
    {% endif %}
),
split_rows AS (
    -- Next, split the raw CSV content into individual lines (rows)
    SELECT row_str, loaded_at
    FROM source_data,
    UNNEST(SPLIT(raw_content, '\n')) AS row_str
    WHERE row_str NOT LIKE 'order_id,product_name%' AND row_str != ''
)
-- Finally, split each row, trim, and cast, now including the loaded_at timestamp
SELECT
    CAST(TRIM(SPLIT(row_str, ',')[OFFSET(0)]) AS INT64) AS order_id,
    TRIM(SPLIT(row_str, ',')[OFFSET(1)]) AS product_name,
    CAST(TRIM(SPLIT(row_str, ',')[OFFSET(2)]) AS INT64) AS quantity,
    CAST(TRIM(SPLIT(row_str, ',')[OFFSET(3)]) AS FLOAT64) AS price,
    CAST(TRIM(SPLIT(row_str, ',')[OFFSET(4)]) AS DATE) AS sale_date,
    loaded_at  -- Pass through the timestamp for the incremental logic
FROM split_rows