{{ config(
    materialized='table' 
) }}

WITH source_data AS (
    -- 1. Mengambil data dari source yang kita definisikan di sources.yml
    SELECT 
        month,
        target_amount
    FROM {{ source('raw_django', 'raw_user_targets') }}
),

cleaned_data AS (
    SELECT
        -- Logic 1: Date Truncation (Memastikan data per bulan)
        -- Mengubah '2017-10-04' menjadi '2017-10-01'
        DATE_TRUNC('month', month)::date as report_month,

        -- Logic 2: Data Cleaning (Case When)
        -- Jika ada error data minus, kita nol-kan
        CASE 
            WHEN target_amount < 0 THEN 0
            ELSE target_amount 
        END as clean_target_amount,

        -- Logic 3: Menambahkan Metadata
        CURRENT_TIMESTAMP as dbt_processed_at

    FROM source_data
    WHERE month IS NOT NULL -- Filter data kosong
)

SELECT * FROM cleaned_data