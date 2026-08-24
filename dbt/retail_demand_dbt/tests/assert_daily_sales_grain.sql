SELECT
    id,
    date,
    COUNT(*) AS record_count
FROM {{ ref('fct_daily_sales') }}
GROUP BY
    id,
    date
HAVING COUNT(*) > 1