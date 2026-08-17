WITH source_prices AS (

    SELECT
        CAST(store_id AS STRING) AS store_id,
        CAST(item_id AS STRING) AS item_id,
        SAFE_CAST(wm_yr_wk AS INT64) AS wm_yr_wk,
        SAFE_CAST(sell_price AS FLOAT64) AS sell_price
    FROM {{ source('retail_demand', 'raw_prices') }}

)

SELECT *
FROM source_prices