SELECT
    store_id,
    item_id,
    wm_yr_wk,
    sell_price
FROM {{ ref('stg_prices') }}
WHERE sell_price < 0