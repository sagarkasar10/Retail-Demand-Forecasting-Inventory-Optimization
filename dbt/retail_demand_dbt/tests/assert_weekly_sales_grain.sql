SELECT
    item_id,
    store_id,
    wm_yr_wk,
    COUNT(*) AS record_count
FROM {{ ref('fct_weekly_sales') }}
GROUP BY
    item_id,
    store_id,
    wm_yr_wk
HAVING COUNT(*) > 1