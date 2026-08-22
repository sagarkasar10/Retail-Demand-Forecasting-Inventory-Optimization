SELECT
    item_id,
    COUNT(*) AS record_count
FROM {{ ref('dim_product') }}
GROUP BY item_id
HAVING COUNT(*) > 1