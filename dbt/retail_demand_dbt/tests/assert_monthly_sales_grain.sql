SELECT
    item_id,
    store_id,
    year,
    month,
    COUNT(*) AS record_count
FROM {{ ref('fct_monthly_sales') }}
GROUP BY
    item_id,
    store_id,
    year,
    month
HAVING COUNT(*) > 1