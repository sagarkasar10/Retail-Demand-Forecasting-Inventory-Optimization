SELECT
    item_id,
    store_id,
    date,
    sales
FROM {{ ref('fct_daily_sales') }}
WHERE sales < 0