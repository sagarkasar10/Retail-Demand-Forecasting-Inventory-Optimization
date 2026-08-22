SELECT
    store_id,
    COUNT(*) AS record_count
FROM {{ ref('dim_store') }}
GROUP BY store_id
HAVING COUNT(*) > 1