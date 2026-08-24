SELECT
    item_id,
    store_id,
    total_sales,
    avg_daily_sales
FROM {{ ref('fct_item_store_sales') }}
WHERE total_sales < 0
   OR avg_daily_sales < 0