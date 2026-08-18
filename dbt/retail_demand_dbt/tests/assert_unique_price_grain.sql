SELECT
    store_id,
    item_id,
    wm_yr_wk,
    COUNT(*) AS record_count
FROM {{ ref('stg_prices') }}
GROUP BY
    store_id,
    item_id,
    wm_yr_wk
HAVING COUNT(*) > 1