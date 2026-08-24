SELECT
    item_id,
    store_id,
    date
FROM {{ ref('fct_daily_sales') }}
WHERE item_id IS NULL
   OR store_id IS NULL
   OR date IS NULL
   OR sales IS NULL