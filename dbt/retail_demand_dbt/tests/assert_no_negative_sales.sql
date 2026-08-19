SELECT
    id,
    item_id,
    store_id,
    date,
    sales
FROM {{ ref('int_daily_sales') }}
WHERE sales < 0