WITH source_calendar AS (

    SELECT
        SAFE_CAST(date AS DATE) AS date,
        SAFE_CAST(wm_yr_wk AS INT64) AS wm_yr_wk,
        CAST(weekday AS STRING) AS weekday,
        SAFE_CAST(wday AS INT64) AS wday,
        SAFE_CAST(month AS INT64) AS month,
        SAFE_CAST(year AS INT64) AS year,
        CAST(event_name_1 AS STRING) AS event_name_1,
        CAST(event_type_1 AS STRING) AS event_type_1,
        CAST(event_name_2 AS STRING) AS event_name_2,
        CAST(event_type_2 AS STRING) AS event_type_2,
        SAFE_CAST(snap_CA AS INT64) AS snap_CA,
        SAFE_CAST(snap_TX AS INT64) AS snap_TX,
        SAFE_CAST(snap_WI AS INT64) AS snap_WI
    FROM {{ source('retail_demand', 'raw_calendar') }}

)

SELECT *
FROM source_calendar